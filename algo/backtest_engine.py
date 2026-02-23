"""
BACKTESTING ENGINE — Walk-forward simulation
=============================================
Event-driven backtester that:
  1. Steps through each trading day
  2. Runs the scanner for new setups
  3. Opens positions based on ranking + risk budget
  4. Updates existing positions (stops, partials, trails)
  5. Applies regime filter + Kitchin cycle overlay
  6. Tracks full equity curve + trade log
"""

import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple
import math

from algo.config import (
    INITIAL_CAPITAL, MAX_POSITIONS, KITCHIN, QMAG, MACRO, UNIVERSE,
    BACKTEST_START, BACKTEST_END, BENCHMARK_TICKER,
    FULL_UNIVERSE, SECTOR_ETF_UNIVERSE, CHINA_ADR_UNIVERSE,
)
from algo.config import MACRO_ENGINE
from algo.universe_builder import daily_scan_prefilter
from algo.indicators import (
    sma, ema, market_regime, kitchin_cycle_position,
    kitchin_sine_wave, composite_technical_score,
    is_cme_t35_window, sector_strength,
)
from algo.scanner import run_full_scan, ScanResult
from algo.position_manager import PositionManager, TradeRecord
from algo.macro_engine import (
    fetch_macro_data, macro_regime_score, macro_sizing_multiplier,
    kitchin_rotation_signal, describe_macro_regime,
)
from algo.earnings_engine import bulk_fetch_earnings


class BacktestEngine:
    """
    Walk-forward backtesting engine (Qullamaggie-style aggressive).

    Architecture:
      - Scans universe every 3 days (more frequent to catch setups)
      - Checks for entries/exits daily
      - Dynamic position limits: 20 bull / 12 neutral / 3 bear
      - Aggressive sizing: 10-20% of equity per position
      - Kitchin cycle multiplier for conviction-based scaling
      - Regime-aware exposure: max exposure in strong bull, near zero in bear
    """

    def __init__(
        self,
        universe_data: Dict[str, pd.DataFrame],
        spy_data: pd.DataFrame,
        initial_capital: float = INITIAL_CAPITAL,
        scan_frequency: int = 1,  # Scan daily (Qullamaggie scans daily for all setups)
        start_date: str = BACKTEST_START,
        end_date: str = BACKTEST_END,
        verbose: bool = True,
        sector_etf_data: Optional[Dict[str, pd.DataFrame]] = None,
    ):
        self.universe_data = universe_data
        self.spy_data = spy_data
        self.sector_etf_data = sector_etf_data or {}
        self.pm = PositionManager(initial_capital)
        self.scan_frequency = scan_frequency
        self.start_date = pd.Timestamp(start_date)
        self.end_date = pd.Timestamp(end_date)
        self.verbose = verbose

        # Build trading calendar from SPY
        self.trading_days = spy_data.index[
            (spy_data.index >= self.start_date) &
            (spy_data.index <= self.end_date)
        ]

        # Pre-compute regime
        self.regime = market_regime(spy_data)

        # Pre-compute Kitchin cycle for all dates (US cycle)
        self.kitchin_positions = {}
        for d in self.trading_days:
            self.kitchin_positions[d] = kitchin_cycle_position(
                d.date(), KITCHIN.c3_trough, KITCHIN.period_months
            )

        # Pre-compute China/EM Kitchin cycle (leads US by 12-18 months)
        self.china_kitchin_positions = {}
        for d in self.trading_days:
            self.china_kitchin_positions[d] = kitchin_cycle_position(
                d.date(), KITCHIN.china_trough, KITCHIN.china_period_months
            )

        # China ADR set for quick lookup
        self.china_adrs = set(CHINA_ADR_UNIVERSE)

        # === MACRO ENGINE: Fetch forward-looking indicators ===
        self.macro_data = {}
        if MACRO_ENGINE.enabled:
            try:
                print("  Loading macro indicators (8 Yahoo Finance tickers)...")
                self.macro_data = fetch_macro_data(start_date, end_date)
            except Exception as e:
                print(f"  [WARN] Macro data fetch failed: {e}")

        # === EARNINGS ENGINE: Pre-fetch earnings data ===
        self.earnings_data = {}
        if MACRO_ENGINE.earnings_enabled:
            try:
                tickers_list = list(universe_data.keys())
                # Only fetch earnings for manageable universe sizes
                if len(tickers_list) <= 500:
                    print(f"  Loading earnings data for {len(tickers_list)} tickers...")
                    self.earnings_data = bulk_fetch_earnings(
                        tickers_list,
                        delay=MACRO_ENGINE.earnings_fetch_delay,
                    )
                else:
                    print(f"  Skipping earnings fetch ({len(tickers_list)} tickers > 500 limit)")
            except Exception as e:
                print(f"  [WARN] Earnings data fetch failed: {e}")

        # Tracking
        self.scan_results_log: List[Tuple[pd.Timestamp, List[ScanResult]]] = []
        self.daily_log: List[dict] = []

    def run(self) -> dict:
        """Execute the full backtest. Returns performance summary."""
        if self.verbose:
            print(f"{'='*70}")
            print(f"BACKTEST: {self.start_date.date()} to {self.end_date.date()}")
            print(f"Universe: {len(self.universe_data)} tickers | Capital: ${self.pm.initial_capital:,.0f}")
            macro_status = f"Macro: {len(self.macro_data)} indicators" if self.macro_data else "Macro: disabled"
            earnings_status = f"Earnings: {len(self.earnings_data)} tickers" if self.earnings_data else "Earnings: disabled"
            print(f"{macro_status} | {earnings_status}")
            print(f"{'='*70}")

        day_count = 0
        last_scan_results: List[ScanResult] = []
        pending_entries: Dict[str, ScanResult] = {}  # Waiting for entry trigger

        for i, current_date in enumerate(self.trading_days):
            day_count += 1

            # === 1. REGIME CHECK ===
            regime_val = 0
            if current_date in self.regime.index:
                regime_val = self.regime.loc[current_date]
            elif len(self.regime) > 0:
                mask = self.regime.index <= current_date
                if mask.any():
                    regime_val = self.regime.loc[self.regime.index[mask][-1]]

            is_bullish_regime = regime_val >= 1

            # Kitchin cycle position (US default — China override per-ticker at entry)
            cycle_pos = self.kitchin_positions.get(current_date, 0.5)
            china_cycle_pos = self.china_kitchin_positions.get(current_date, 0.5)
            cycle_phase = KITCHIN.get_phase_label(cycle_pos)
            cycle_score = KITCHIN.get_cycle_score(cycle_pos)

            # === MACRO REGIME SIZING ===
            macro_mult = 1.0
            china_rotation_mult = 1.0
            if self.macro_data and MACRO_ENGINE.enabled:
                try:
                    m_score = macro_regime_score(self.macro_data, current_date)
                    macro_mult = macro_sizing_multiplier(
                        m_score,
                        max_boost=MACRO_ENGINE.max_boost,
                        max_penalty=MACRO_ENGINE.max_penalty,
                    )
                    rot_mult, _ = kitchin_rotation_signal(current_date)
                    china_rotation_mult = rot_mult
                except Exception:
                    pass

            # === SET REGIME ON POSITION MANAGER (for dynamic max positions) ===
            self.pm._current_regime = regime_val

            # === 2. UPDATE EXISTING POSITIONS ===
            closed_trades = self.pm.update_positions(self.universe_data, current_date)
            for trade in closed_trades:
                self.pm.trade_history.append(trade)

            # === 3. REGIME-BASED EXITS ===
            # Reduce excess positions if regime drops and we're over limit
            max_pos_now = self.pm.get_max_positions()
            if self.pm.num_positions > max_pos_now and regime_val <= -1:
                # Close weakest positions (lowest R-multiple) to get under limit
                sorted_positions = sorted(
                    self.pm.positions.items(),
                    key=lambda x: x[1].r_multiple,
                )
                while self.pm.num_positions > max_pos_now and sorted_positions:
                    weak_ticker, weak_pos = sorted_positions.pop(0)
                    if weak_ticker in self.universe_data:
                        df = self.universe_data[weak_ticker]
                        mask = df.index <= current_date
                        if mask.any():
                            price = df.loc[df.index[mask][-1], "close"]
                            fill_price = price * (1 - 0.001)
                            commission = fill_price * weak_pos.shares * 0.001
                            proceeds = fill_price * weak_pos.shares - commission
                            self.pm.cash += proceeds
                            risk = weak_pos.risk_per_share
                            r_mult = (fill_price - weak_pos.entry_price) / risk if risk > 0 else 0
                            from algo.position_manager import TradeRecord
                            trade = TradeRecord(
                                ticker=weak_ticker,
                                setup_type=weak_pos.setup_type,
                                entry_date=weak_pos.entry_date,
                                exit_date=current_date,
                                entry_price=weak_pos.entry_price,
                                exit_price=fill_price,
                                shares=weak_pos.shares,
                                pnl=(fill_price - weak_pos.entry_price) * weak_pos.shares,
                                r_multiple=r_mult,
                                holding_days=(current_date - weak_pos.entry_date).days,
                                exit_reason="REGIME_REDUCTION",
                                score=weak_pos.score,
                            )
                            self.pm.trade_history.append(trade)
                            del self.pm.positions[weak_ticker]

            # === 4. SCAN FOR NEW SETUPS ===
            # Scan every 3 days for full scan, daily for EPs
            do_full_scan = (day_count % self.scan_frequency == 0)
            do_ep_scan = True  # Always check for EPs daily

            # Qullamaggie: Trade aggressively in bull, selective in bear
            can_scan = (is_bullish_regime or regime_val >= 0 or
                       cycle_phase in ["TROUGH_ACCUMULATE", "EARLY_EXPANSION", "LATE_CONTRACTION"])

            if can_scan and (do_full_scan or do_ep_scan):
                # PRE-FILTER: Fast vectorized check before full scan
                # Narrows 3000 tickers → 200-500 candidates per day
                if len(self.universe_data) > 200:
                    prefiltered = daily_scan_prefilter(
                        self.universe_data, current_date,
                        min_adr_pct=UNIVERSE.pre_filter_min_adr,
                        above_sma=UNIVERSE.pre_filter_above_sma,
                    )
                    scan_source = {t: self.universe_data[t] for t in prefiltered
                                   if t in self.universe_data}
                else:
                    scan_source = self.universe_data

                # Build subset of data up to current date
                scan_data = {}
                for ticker, df in scan_source.items():
                    mask = df.index <= current_date
                    if mask.any():
                        subset = df.loc[mask]
                        if len(subset) >= 100:
                            scan_data[ticker] = subset

                spy_subset = self.spy_data[self.spy_data.index <= current_date]

                # Compute sector relative strength for this date
                sector_rs = {}
                if hasattr(self, 'sector_etf_data') and self.sector_etf_data:
                    sector_scan = {}
                    for etf, edf in self.sector_etf_data.items():
                        mask = edf.index <= current_date
                        if mask.any():
                            subset = edf.loc[mask]
                            if len(subset) >= 63:
                                sector_scan[etf] = subset
                    spy_close_sub = spy_subset["close"] if not spy_subset.empty else pd.Series()
                    if sector_scan and len(spy_close_sub) >= 63:
                        sector_rs = sector_strength(sector_scan, spy_close_sub, 63)

                if do_full_scan:
                    last_scan_results = run_full_scan(
                        scan_data, spy_subset, as_of_idx=-1, min_score=20.0,
                        sector_rs=sector_rs, current_date=current_date,
                        cycle_phase=cycle_phase,
                        earnings_data=self.earnings_data if self.earnings_data else None,
                    )
                    # Refresh pending entries — keep highest score per ticker
                    pending_entries = {}
                    for r in last_scan_results:
                        if r.ticker not in self.pm.positions:
                            if r.ticker not in pending_entries or r.score > pending_entries[r.ticker].score:
                                pending_entries[r.ticker] = r
                else:
                    # Daily EP-only scan
                    from algo.scanner import scan_ep
                    for ticker, df_sub in scan_data.items():
                        if ticker in self.pm.positions or ticker in pending_entries:
                            continue
                        try:
                            ticker_earnings = self.earnings_data.get(ticker) if self.earnings_data else None
                            ep = scan_ep(df_sub, ticker, spy_subset["close"] if not spy_subset.empty else pd.Series(), -1,
                                         earnings_data=ticker_earnings)
                            if ep and ep.score >= 20.0:
                                pending_entries[ticker] = ep
                        except Exception:
                            continue

                self.scan_results_log.append((current_date, list(pending_entries.values())))

            # === 5. EXECUTE ENTRIES ===
            if self.pm.can_open_position() and pending_entries:
                # Sort candidates by score
                candidates = sorted(
                    pending_entries.values(),
                    key=lambda x: x.score,
                    reverse=True,
                )

                for result in candidates:
                    ticker = result.ticker
                    if not self.pm.can_open_position(ticker):
                        if self.pm.num_positions >= self.pm.get_max_positions():
                            break  # At max positions, stop entirely
                        continue  # Sector limit hit, try next ticker

                    if ticker in self.pm.positions:
                        continue

                    if ticker not in self.universe_data:
                        continue

                    df = self.universe_data[ticker]
                    mask = df.index <= current_date
                    if not mask.any():
                        continue

                    current_row = df.loc[df.index[mask][-1]]
                    current_close = current_row["close"]

                    # CME T+35 window: already penalized via score multiplier in scanner
                    # No hard block — let score-based ranking handle it

                    # Entry fill price
                    entry_fill = current_close

                    # Use China Kitchin cycle for China ADRs, US cycle for others
                    is_china_adr = ticker in self.china_adrs
                    ticker_cycle = china_cycle_pos if is_china_adr else cycle_pos

                    # Macro multiplier: apply China rotation for China ADRs
                    ticker_macro_mult = macro_mult
                    if is_china_adr:
                        ticker_macro_mult *= china_rotation_mult

                    # Open position
                    pos = self.pm.open_position(
                        ticker=ticker,
                        entry_date=current_date,
                        entry_price=entry_fill,
                        stop_price=result.stop_price,
                        setup_type=result.setup_type,
                        score=result.score,
                        cycle_position=ticker_cycle,
                        macro_multiplier=ticker_macro_mult,
                    )

                    if pos and self.verbose and day_count % 20 == 0:
                        pass  # Reduce noise

                    # Remove from pending
                    if ticker in pending_entries:
                        del pending_entries[ticker]

            # === 6. DAILY LOG ===
            self.daily_log.append({
                "date": current_date,
                "equity": self.pm.equity,
                "cash": self.pm.cash,
                "num_positions": self.pm.num_positions,
                "regime": regime_val,
                "cycle_pos": cycle_pos,
                "cycle_phase": cycle_phase,
                "cycle_score": cycle_score,
                "macro_mult": macro_mult,
                "halted": self.pm.halted,
            })

            # Progress reporting
            if self.verbose and day_count % 252 == 0:
                yr = day_count // 252
                print(f"  Year {yr}: Equity ${self.pm.equity:,.0f} | "
                      f"Trades: {len(self.pm.trade_history)} | "
                      f"Positions: {self.pm.num_positions} | "
                      f"Cycle: {cycle_phase} | "
                      f"MacroMult: {macro_mult:.2f}")

        # === END: Close all remaining positions ===
        final_closes = self.pm.force_close_all(
            self.universe_data, self.trading_days[-1], "END_OF_BACKTEST"
        )
        for trade in final_closes:
            self.pm.trade_history.append(trade)

        # Build results
        return self._compute_results()

    def _compute_results(self) -> dict:
        """Compute comprehensive backtest analytics."""
        daily_df = pd.DataFrame(self.daily_log)
        if daily_df.empty:
            return {"error": "No trading days processed"}

        daily_df = daily_df.set_index("date")
        equity = daily_df["equity"]

        # Total return
        total_return = (equity.iloc[-1] / equity.iloc[0] - 1) * 100

        # CAGR
        years = (equity.index[-1] - equity.index[0]).days / 365.25
        cagr = ((equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1) * 100 if years > 0 else 0

        # Max drawdown
        peak = equity.cummax()
        drawdown = (equity - peak) / peak * 100
        max_dd = drawdown.min()
        max_dd_date = drawdown.idxmin()

        # Sharpe ratio (assuming risk-free = 0)
        daily_returns = equity.pct_change().dropna()
        sharpe = (daily_returns.mean() / daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0

        # Sortino ratio
        downside = daily_returns[daily_returns < 0]
        sortino = (daily_returns.mean() / downside.std() * np.sqrt(252)) if len(downside) > 0 and downside.std() > 0 else 0

        # Calmar ratio
        calmar = cagr / abs(max_dd) if max_dd != 0 else 0

        # Trade statistics
        trades = self.pm.trade_history
        num_trades = len(trades)

        if num_trades > 0:
            winners = [t for t in trades if t.pnl > 0]
            losers = [t for t in trades if t.pnl <= 0]
            win_rate = len(winners) / num_trades * 100

            avg_win = np.mean([t.pnl for t in winners]) if winners else 0
            avg_loss = np.mean([t.pnl for t in losers]) if losers else 0
            profit_factor = abs(sum(t.pnl for t in winners) / sum(t.pnl for t in losers)) if losers and sum(t.pnl for t in losers) != 0 else float('inf')

            avg_r = np.mean([t.r_multiple for t in trades])
            avg_hold = np.mean([t.holding_days for t in trades])

            # By setup type
            setup_stats = {}
            for stype in set(t.setup_type for t in trades):
                s_trades = [t for t in trades if t.setup_type == stype]
                s_winners = [t for t in s_trades if t.pnl > 0]
                setup_stats[stype] = {
                    "count": len(s_trades),
                    "win_rate": len(s_winners) / len(s_trades) * 100 if s_trades else 0,
                    "avg_r": np.mean([t.r_multiple for t in s_trades]),
                    "total_pnl": sum(t.pnl for t in s_trades),
                }
        else:
            win_rate = 0
            avg_win = avg_loss = profit_factor = avg_r = avg_hold = 0
            setup_stats = {}

        # Benchmark comparison (SPY buy-and-hold)
        spy_start = self.spy_data["close"].iloc[0]
        spy_end_mask = self.spy_data.index <= self.end_date
        spy_end = self.spy_data.loc[spy_end_mask, "close"].iloc[-1] if spy_end_mask.any() else spy_start
        spy_return = (spy_end / spy_start - 1) * 100

        results = {
            "performance": {
                "total_return_pct": round(total_return, 2),
                "cagr_pct": round(cagr, 2),
                "max_drawdown_pct": round(max_dd, 2),
                "max_dd_date": str(max_dd_date.date()) if hasattr(max_dd_date, 'date') else str(max_dd_date),
                "sharpe_ratio": round(sharpe, 3),
                "sortino_ratio": round(sortino, 3),
                "calmar_ratio": round(calmar, 3),
                "final_equity": round(equity.iloc[-1], 2),
                "peak_equity": round(peak.max(), 2),
            },
            "trades": {
                "total": num_trades,
                "win_rate_pct": round(win_rate, 1),
                "avg_win": round(avg_win, 2),
                "avg_loss": round(avg_loss, 2),
                "profit_factor": round(profit_factor, 3),
                "avg_r_multiple": round(avg_r, 3),
                "avg_holding_days": round(avg_hold, 1),
                "by_setup": setup_stats,
            },
            "benchmark": {
                "spy_return_pct": round(spy_return, 2),
                "alpha_pct": round(total_return - spy_return, 2),
            },
            "cycle": {
                "phases_traded": {str(k): int(v) for k, v in daily_df["cycle_phase"].value_counts().items()},
            },
            "equity_curve": {str(k): v for k, v in daily_df["equity"].to_dict().items()},
            "trade_log": [
                {
                    "ticker": t.ticker,
                    "setup": t.setup_type,
                    "entry_date": str(t.entry_date.date()) if hasattr(t.entry_date, 'date') else str(t.entry_date),
                    "exit_date": str(t.exit_date.date()) if hasattr(t.exit_date, 'date') else str(t.exit_date),
                    "entry_price": round(t.entry_price, 2),
                    "exit_price": round(t.exit_price, 2),
                    "shares": t.shares,
                    "pnl": round(t.pnl, 2),
                    "r_multiple": round(t.r_multiple, 2),
                    "days": t.holding_days,
                    "exit_reason": t.exit_reason,
                }
                for t in trades
            ],
        }

        if self.verbose:
            self._print_results(results)

        return results

    def _print_results(self, results: dict):
        """Pretty print backtest results."""
        p = results["performance"]
        t = results["trades"]
        b = results["benchmark"]

        print(f"\n{'='*70}")
        print(f"BACKTEST RESULTS")
        print(f"{'='*70}")
        print(f"  Total Return:    {p['total_return_pct']:>8.1f}%")
        print(f"  CAGR:            {p['cagr_pct']:>8.1f}%")
        print(f"  Max Drawdown:    {p['max_drawdown_pct']:>8.1f}%  ({p['max_dd_date']})")
        print(f"  Sharpe Ratio:    {p['sharpe_ratio']:>8.3f}")
        print(f"  Sortino Ratio:   {p['sortino_ratio']:>8.3f}")
        print(f"  Calmar Ratio:    {p['calmar_ratio']:>8.3f}")
        print(f"  Final Equity:    ${p['final_equity']:>10,.2f}")
        print(f"  Peak Equity:     ${p['peak_equity']:>10,.2f}")
        print(f"\n  SPY B&H Return:  {b['spy_return_pct']:>8.1f}%")
        print(f"  Alpha:           {b['alpha_pct']:>8.1f}%")
        print(f"\n{'='*70}")
        print(f"TRADE STATISTICS")
        print(f"{'-'*70}")
        print(f"  Total Trades:    {t['total']:>8d}")
        print(f"  Win Rate:        {t['win_rate_pct']:>8.1f}%")
        print(f"  Avg Win:         ${t['avg_win']:>10,.2f}")
        print(f"  Avg Loss:        ${t['avg_loss']:>10,.2f}")
        print(f"  Profit Factor:   {t['profit_factor']:>8.3f}")
        print(f"  Avg R-Multiple:  {t['avg_r_multiple']:>8.3f}")
        print(f"  Avg Hold (days): {t['avg_holding_days']:>8.1f}")

        if t["by_setup"]:
            print(f"\n  BY SETUP TYPE:")
            for stype, stats in t["by_setup"].items():
                print(f"    {stype:12s}: {stats['count']:3d} trades, "
                      f"WR={stats['win_rate']:.0f}%, "
                      f"Avg R={stats['avg_r']:.2f}, "
                      f"PnL=${stats['total_pnl']:,.0f}")

        print(f"{'='*70}\n")
