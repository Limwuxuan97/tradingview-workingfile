"""
POSITION MANAGER — Trade lifecycle management (Qullamaggie-style)
=================================================================
Handles:
  - Position sizing: 10-20% of equity per position (concentrated)
  - Dynamic max positions: 20 in bull, 12 neutral, 3 in bear
  - Two-stage partial profit taking (1/3 at 2R, 1/3 at 5R, trail rest)
  - Trailing stops from day 5 (don't wait for partial)
  - Portfolio-level risk limits (30% total open risk)
  - Regime-aware exposure scaling
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from algo.config import (
    INITIAL_CAPITAL, MAX_POSITIONS, MAX_POSITIONS_BULL,
    MAX_POSITIONS_NEUTRAL, MAX_POSITIONS_BEAR,
    MAX_RISK_PER_TRADE_PCT, MAX_TOTAL_RISK_PCT,
    MAX_POSITION_PCT_OF_EQUITY, TARGET_POSITION_PCT,
    COMMISSION_PCT, SLIPPAGE_PCT, QMAG, KITCHIN,
)
from algo.indicators import sma, ema, atr, TICKER_SECTOR_MAP


@dataclass
class Position:
    """Active position tracking."""
    ticker: str
    entry_date: pd.Timestamp
    entry_price: float
    shares: int
    initial_shares: int
    stop_price: float
    initial_stop: float
    setup_type: str            # HTF, EP, BREAKOUT
    score: float               # Scan score at entry
    highest_close: float = 0.0 # For trailing stop
    partial_1_sold: bool = False  # First 1/3 trim done
    partial_2_sold: bool = False  # Second 1/3 trim done
    trail_ma: int = 10         # Trailing MA period
    r_multiple: float = 0.0    # Current R-multiple
    pnl: float = 0.0          # Unrealized P&L
    status: str = "OPEN"       # OPEN, PARTIAL, CLOSED
    exit_date: Optional[pd.Timestamp] = None
    exit_price: float = 0.0
    exit_reason: str = ""
    days_held: int = 0         # Track days in trade for early trailing
    pyramid_count: int = 0     # Number of times we've added to this position

    @property
    def risk_per_share(self) -> float:
        return self.entry_price - self.initial_stop

    @property
    def initial_risk(self) -> float:
        return self.risk_per_share * self.initial_shares

    @property
    def current_value(self) -> float:
        return self.shares * self.entry_price


@dataclass
class TradeRecord:
    """Completed trade for analytics."""
    ticker: str
    setup_type: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_price: float
    exit_price: float
    shares: int
    pnl: float
    r_multiple: float
    holding_days: int
    exit_reason: str
    score: float


class PositionManager:
    """Manages portfolio with Qullamaggie aggressive sizing and risk rules."""

    def __init__(self, initial_capital: float = INITIAL_CAPITAL):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.equity = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[TradeRecord] = []
        self.consecutive_stops: int = 0
        self.halted: bool = False
        self.halt_date: Optional[pd.Timestamp] = None
        self.equity_curve: List[Tuple[pd.Timestamp, float]] = []
        self._current_regime: int = 0  # Set by backtest engine
        # Portfolio-level drawdown protection
        self.peak_equity: float = initial_capital
        self.drawdown_pct: float = 0.0

    @property
    def num_positions(self) -> int:
        return len(self.positions)

    @property
    def total_risk(self) -> float:
        """Total $ at risk across all positions."""
        return sum(
            p.risk_per_share * p.shares
            for p in self.positions.values()
        )

    @property
    def total_risk_pct(self) -> float:
        return self.total_risk / self.equity if self.equity > 0 else 0

    @property
    def total_exposure_pct(self) -> float:
        """Total position value as % of equity (can exceed 100% with margin)."""
        total_val = sum(
            p.entry_price * p.shares for p in self.positions.values()
        )
        return total_val / self.equity if self.equity > 0 else 0

    def get_max_positions(self) -> int:
        """Dynamic max positions based on market regime (Qullamaggie style)."""
        if self._current_regime >= 2:
            return MAX_POSITIONS_BULL     # 20 in strong bull
        elif self._current_regime >= 1:
            return MAX_POSITIONS_NEUTRAL  # 12 in bull
        elif self._current_regime <= -1:
            return MAX_POSITIONS_BEAR     # 3 in bear
        else:
            return MAX_POSITIONS_NEUTRAL  # 12 neutral

    @property
    def drawdown_sizing_mult(self) -> float:
        """
        Qullamaggie does NOT reduce size in drawdowns. He maintains full sizing
        and recovers with the next big winner. The trailing stop + regime filter
        already protect the downside. Cutting sizing in DDs kills compounding.
        Only reduce at catastrophic levels to prevent account death.
        """
        if self.drawdown_pct < 60:
            return 1.0       # Full sizing — 40-60% DDs are expected and normal
        else:
            return 0.5       # Only at catastrophic 60%+ DD: half size to survive

    MAX_PER_SECTOR = 999  # No sector limit — Qullamaggie concentrates in the leading sector

    def sector_count(self, ticker: str) -> int:
        """Count how many positions we hold in the same sector as ticker."""
        sector = TICKER_SECTOR_MAP.get(ticker, None)
        if sector is None:
            return 0
        count = 0
        for t in self.positions:
            if TICKER_SECTOR_MAP.get(t, None) == sector:
                count += 1
        return count

    def can_open_position(self, ticker: str = "") -> bool:
        """Check if we can open new positions."""
        if self.halted:
            return False
        if self.num_positions >= self.get_max_positions():
            return False
        if self.total_risk_pct >= MAX_TOTAL_RISK_PCT:
            return False
        # Sector concentration limit
        if ticker and self.sector_count(ticker) >= self.MAX_PER_SECTOR:
            return False
        return True

    def calculate_position_size(
        self,
        entry_price: float,
        stop_price: float,
        cycle_position: float = 0.5,
        score: float = 50.0,
        macro_multiplier: float = 1.0,
    ) -> int:
        """
        Qullamaggie-style position sizing:
          1. Target 10-20% of equity per position
          2. Risk-based: max 3% of account risk per trade
          3. Kitchin cycle multiplier (more aggressive near trough/expansion)
          4. Conviction multiplier (higher score = larger)
          5. Macro regime multiplier (±15% based on forward-looking signals)
          6. Use the SMALLER of risk-based and %-of-equity sizing
        """
        risk_per_share = entry_price - stop_price
        if risk_per_share <= 0:
            return 0

        # --- Method 1: Risk-based sizing (3% of equity) ---
        base_risk = self.equity * MAX_RISK_PER_TRADE_PCT

        # Kitchin cycle multiplier (up to 2.5x at trough/expansion)
        cycle_mult = KITCHIN.get_cycle_sizing_multiplier(cycle_position)

        # Conviction multiplier (0.7x for score=30, 1.3x for score=80+)
        conviction_mult = 0.7 + (min(score, 80) - 30) / 50.0 * 0.6

        # Drawdown protection: reduce sizing as portfolio drops from peak
        dd_mult = self.drawdown_sizing_mult

        # Macro regime multiplier (0.85-1.15x from forward-looking signals)
        macro_mult = max(0.85, min(1.15, macro_multiplier))

        adjusted_risk = base_risk * cycle_mult * conviction_mult * dd_mult * macro_mult
        shares_by_risk = int(adjusted_risk / risk_per_share)

        # Use risk-based sizing, but cap position value at 20% of equity
        shares = shares_by_risk
        max_value = self.equity * MAX_POSITION_PCT_OF_EQUITY
        max_shares_by_value = int(max_value / entry_price)
        shares = min(shares, max_shares_by_value)

        # Cap total risk budget
        remaining_risk_budget = (MAX_TOTAL_RISK_PCT * self.equity) - self.total_risk
        if remaining_risk_budget <= 0:
            return 0
        max_shares_by_budget = int(remaining_risk_budget / risk_per_share)
        shares = min(shares, max_shares_by_budget)

        # Margin-based buying power: use equity * leverage, not cash
        # Qullamaggie uses full margin (2x) and often 150-300% invested
        max_buying_power = self.equity * 2.5  # 2.5x margin (Qullamaggie uses heavy margin)
        current_exposure = sum(
            p.entry_price * p.shares for p in self.positions.values()
        )
        remaining_buying_power = max_buying_power - current_exposure
        if remaining_buying_power <= 0:
            return 0

        cost = shares * entry_price * (1 + COMMISSION_PCT + SLIPPAGE_PCT)
        if cost > remaining_buying_power:
            shares = int(remaining_buying_power / (entry_price * (1 + COMMISSION_PCT + SLIPPAGE_PCT)))

        return max(0, shares)

    def open_position(
        self,
        ticker: str,
        entry_date: pd.Timestamp,
        entry_price: float,
        stop_price: float,
        setup_type: str,
        score: float,
        cycle_position: float = 0.5,
        macro_multiplier: float = 1.0,
    ) -> Optional[Position]:
        """Open a new position."""
        if not self.can_open_position(ticker):
            return None

        if ticker in self.positions:
            return None  # Already holding

        # Apply slippage to entry
        fill_price = entry_price * (1 + SLIPPAGE_PCT)

        shares = self.calculate_position_size(fill_price, stop_price, cycle_position, score, macro_multiplier)
        if shares <= 0:
            return None

        # Commission
        commission = fill_price * shares * COMMISSION_PCT
        total_cost = fill_price * shares + commission

        # Margin check: total exposure should not exceed 2x equity
        current_exposure = sum(p.entry_price * p.shares for p in self.positions.values())
        if current_exposure + total_cost > self.equity * 2.5:
            return None

        pos = Position(
            ticker=ticker,
            entry_date=entry_date,
            entry_price=fill_price,
            shares=shares,
            initial_shares=shares,
            stop_price=stop_price,
            initial_stop=stop_price,
            setup_type=setup_type,
            score=score,
            highest_close=fill_price,
            trail_ma=QMAG.trail_ma_alt if setup_type == "EP" else QMAG.trail_ma,
        )

        self.cash -= total_cost
        self.positions[ticker] = pos
        self.consecutive_stops = 0  # New position breaks losing streak
        return pos

    def update_positions(self, current_prices: Dict[str, pd.DataFrame],
                         current_date: pd.Timestamp) -> List[TradeRecord]:
        """
        Update all positions with current prices.
        Qullamaggie trade management:
          1. Stop loss hits → exit full position
          2. Day 5+: Start trailing on 10/20 SMA (don't wait for partial)
          3. At 2R: Trim 1/3, move stop to breakeven
          4. At 5R: Trim another 1/3, trail rest aggressively
          5. Trail final 1/3 on 10/20 SMA until MA break
        """
        closed_trades = []
        tickers_to_close = []

        for ticker, pos in self.positions.items():
            if ticker not in current_prices or current_prices[ticker].empty:
                continue

            df = current_prices[ticker]
            # Find the row for current_date (or closest)
            if current_date in df.index:
                row = df.loc[current_date]
            else:
                mask = df.index <= current_date
                if not mask.any():
                    continue
                row = df.loc[df.index[mask][-1]]

            current_close = row["close"]
            current_low = row["low"]
            current_high = row["high"]

            # Update days held
            pos.days_held = (current_date - pos.entry_date).days

            # Update highest close
            pos.highest_close = max(pos.highest_close, current_close)

            # Calculate R-multiple
            risk = pos.risk_per_share
            if risk > 0:
                pos.r_multiple = (current_close - pos.entry_price) / risk

            # Unrealized P&L
            pos.pnl = (current_close - pos.entry_price) * pos.shares

            # === STOP LOSS CHECK ===
            if current_low <= pos.stop_price:
                fill_price = pos.stop_price * (1 - SLIPPAGE_PCT)
                commission = fill_price * pos.shares * COMMISSION_PCT
                proceeds = fill_price * pos.shares - commission
                self.cash += proceeds

                r_mult = (fill_price - pos.entry_price) / risk if risk > 0 else 0
                holding_days = (current_date - pos.entry_date).days

                trade = TradeRecord(
                    ticker=ticker,
                    setup_type=pos.setup_type,
                    entry_date=pos.entry_date,
                    exit_date=current_date,
                    entry_price=pos.entry_price,
                    exit_price=fill_price,
                    shares=pos.shares,
                    pnl=proceeds - pos.entry_price * pos.shares,
                    r_multiple=r_mult,
                    holding_days=holding_days,
                    exit_reason="STOP_LOSS" if r_mult < 0 else "TRAILING_STOP",
                    score=pos.score,
                )
                closed_trades.append(trade)
                tickers_to_close.append(ticker)

                if r_mult < 0:
                    self.consecutive_stops += 1
                    if self.consecutive_stops >= QMAG.max_consecutive_stops:
                        self.halted = True
                        self.halt_date = current_date
                continue

            # NOTE: No breakeven stop before partials. Qullamaggie waits for the
            # 2R partial to move stop to breakeven. A 1.5R breakeven stop kills
            # trades that pull back to 0.5R then run to 5-10R (common pattern).
            # The 20 SMA trail after day 10 provides gradual protection instead.

            # === FIRST PARTIAL: 1/3 at 2R or after 3-5 day burst ===
            # Time-based burst: if held 3 to 5 days and in good profit (> 1.5R), take partial
            burst_condition = (3 <= pos.days_held <= 5) and (pos.r_multiple >= 1.5)
            if not pos.partial_1_sold and (pos.r_multiple >= QMAG.first_target_r_multiple or burst_condition):
                sell_shares = max(1, int(pos.initial_shares * QMAG.initial_sell_pct))
                if sell_shares > 0 and sell_shares < pos.shares:
                    fill_price = current_close * (1 - SLIPPAGE_PCT)
                    commission = fill_price * sell_shares * COMMISSION_PCT
                    proceeds = fill_price * sell_shares - commission
                    self.cash += proceeds
                    pos.shares -= sell_shares
                    pos.partial_1_sold = True
                    pos.status = "PARTIAL_1"

                    # Move stop to breakeven (risk-free trade now)
                    pos.stop_price = pos.entry_price

                    trade = TradeRecord(
                        ticker=ticker,
                        setup_type=pos.setup_type,
                        entry_date=pos.entry_date,
                        exit_date=current_date,
                        entry_price=pos.entry_price,
                        exit_price=fill_price,
                        shares=sell_shares,
                        pnl=(fill_price - pos.entry_price) * sell_shares,
                        r_multiple=pos.r_multiple,
                        holding_days=(current_date - pos.entry_date).days,
                        exit_reason=f"PARTIAL_33%_AT_{QMAG.first_target_r_multiple}R",
                        score=pos.score,
                    )
                    closed_trades.append(trade)

            # === SECOND PARTIAL: 1/3 at 5R ===
            if (pos.partial_1_sold and not pos.partial_2_sold and
                    pos.r_multiple >= QMAG.second_target_r_multiple):
                sell_shares = max(1, int(pos.initial_shares * QMAG.second_sell_pct))
                sell_shares = min(sell_shares, pos.shares - 1)  # Keep at least 1 share
                if sell_shares > 0:
                    fill_price = current_close * (1 - SLIPPAGE_PCT)
                    commission = fill_price * sell_shares * COMMISSION_PCT
                    proceeds = fill_price * sell_shares - commission
                    self.cash += proceeds
                    pos.shares -= sell_shares
                    pos.partial_2_sold = True
                    pos.status = "PARTIAL_2"

                    trade = TradeRecord(
                        ticker=ticker,
                        setup_type=pos.setup_type,
                        entry_date=pos.entry_date,
                        exit_date=current_date,
                        entry_price=pos.entry_price,
                        exit_price=fill_price,
                        shares=sell_shares,
                        pnl=(fill_price - pos.entry_price) * sell_shares,
                        r_multiple=pos.r_multiple,
                        holding_days=(current_date - pos.entry_date).days,
                        exit_reason=f"PARTIAL_33%_AT_{QMAG.second_target_r_multiple}R",
                        score=pos.score,
                    )
                    closed_trades.append(trade)

            # === PYRAMIDING (add to winners) ===
            # Qullamaggie adds to positions that are working
            if (QMAG.pyramid_enabled and
                    pos.r_multiple >= QMAG.pyramid_threshold_r and
                    pos.pyramid_count < QMAG.pyramid_max_adds and
                    not pos.partial_1_sold):
                add_shares = max(1, int(pos.initial_shares * QMAG.pyramid_size_pct))
                add_cost = current_close * add_shares * (1 + COMMISSION_PCT + SLIPPAGE_PCT)
                current_exposure = sum(
                    p.entry_price * p.shares for p in self.positions.values()
                )
                if current_exposure + add_cost <= self.equity * 2.5:
                    self.cash -= add_cost
                    pos.shares += add_shares
                    pos.pyramid_count += 1
                    # Move stop up to protect profits (1R below current)
                    new_stop = current_close - pos.risk_per_share
                    pos.stop_price = max(pos.stop_price, new_stop)

            # === TRAILING STOP UPDATE ===
            # Qullamaggie: Trail on 20/50 SMA. Start trailing after 10 days or after partial.
            should_trail = (pos.days_held >= QMAG.trail_from_day) or pos.partial_1_sold
            if should_trail and len(df) > pos.trail_ma:
                trail_val = sma(df["close"], pos.trail_ma)
                if current_date in trail_val.index:
                    trail_price = trail_val.loc[current_date]
                elif len(trail_val) > 0:
                    trail_price = trail_val.iloc[-1]
                else:
                    trail_price = pos.stop_price

                if not pd.isna(trail_price):
                    # Only raise stop, never lower
                    new_stop = max(pos.stop_price, trail_price * 0.99)
                    pos.stop_price = new_stop

        # Remove closed positions
        for ticker in tickers_to_close:
            del self.positions[ticker]

        # Update equity
        self._update_equity(current_prices, current_date)

        # Check halt condition — unhalt after 7 days cooldown (faster recovery)
        if self.halted and self.halt_date is not None:
            days_halted = (current_date - self.halt_date).days
            if days_halted >= 7:  # ~5 trading days — faster recovery
                self.halted = False
                self.consecutive_stops = 0
                self.halt_date = None

        return closed_trades

    def _update_equity(self, current_prices: Dict[str, pd.DataFrame],
                       current_date: pd.Timestamp):
        """Update total equity (cash + positions marked-to-market)."""
        position_value = 0.0
        for ticker, pos in self.positions.items():
            if ticker in current_prices and not current_prices[ticker].empty:
                df = current_prices[ticker]
                mask = df.index <= current_date
                if mask.any():
                    price = df.loc[df.index[mask][-1], "close"]
                    position_value += price * pos.shares
                else:
                    position_value += pos.entry_price * pos.shares
            else:
                position_value += pos.entry_price * pos.shares

        self.equity = self.cash + position_value
        # Track peak equity and current drawdown for portfolio protection
        if self.equity > self.peak_equity:
            self.peak_equity = self.equity
        self.drawdown_pct = (self.peak_equity - self.equity) / self.peak_equity * 100 if self.peak_equity > 0 else 0
        self.equity_curve.append((current_date, self.equity))

    def force_close_all(self, current_prices: Dict[str, pd.DataFrame],
                        current_date: pd.Timestamp, reason: str = "END_OF_BACKTEST"
                        ) -> List[TradeRecord]:
        """Close all positions (e.g., end of backtest or regime change)."""
        closed = []
        for ticker in list(self.positions.keys()):
            pos = self.positions[ticker]
            if ticker in current_prices and not current_prices[ticker].empty:
                df = current_prices[ticker]
                mask = df.index <= current_date
                if mask.any():
                    price = df.loc[df.index[mask][-1], "close"]
                else:
                    price = pos.entry_price
            else:
                price = pos.entry_price

            fill_price = price * (1 - SLIPPAGE_PCT)
            commission = fill_price * pos.shares * COMMISSION_PCT
            proceeds = fill_price * pos.shares - commission
            self.cash += proceeds

            risk = pos.risk_per_share
            r_mult = (fill_price - pos.entry_price) / risk if risk > 0 else 0

            trade = TradeRecord(
                ticker=ticker,
                setup_type=pos.setup_type,
                entry_date=pos.entry_date,
                exit_date=current_date,
                entry_price=pos.entry_price,
                exit_price=fill_price,
                shares=pos.shares,
                pnl=(fill_price - pos.entry_price) * pos.shares,
                r_multiple=r_mult,
                holding_days=(current_date - pos.entry_date).days,
                exit_reason=reason,
                score=pos.score,
            )
            closed.append(trade)

        self.positions.clear()
        self._update_equity(current_prices, current_date)
        return closed

    def get_portfolio_summary(self) -> dict:
        """Current portfolio snapshot."""
        return {
            "equity": round(self.equity, 2),
            "cash": round(self.cash, 2),
            "num_positions": self.num_positions,
            "max_positions": self.get_max_positions(),
            "total_risk_pct": round(self.total_risk_pct * 100, 2),
            "total_exposure_pct": round(self.total_exposure_pct * 100, 2),
            "halted": self.halted,
            "consecutive_stops": self.consecutive_stops,
            "positions": {
                t: {
                    "shares": p.shares,
                    "entry": p.entry_price,
                    "stop": p.stop_price,
                    "r_mult": round(p.r_multiple, 2),
                    "pnl": round(p.pnl, 2),
                    "setup": p.setup_type,
                    "days_held": p.days_held,
                }
                for t, p in self.positions.items()
            },
        }
