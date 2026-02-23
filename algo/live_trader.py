"""
LONGBRIDGE LIVE TRADING — Order Execution & Portfolio Tracking
================================================================
Connects to Longbridge broker API for:
  1. Real-time market data
  2. Order placement (limit/market)
  3. Position tracking
  4. Portfolio monitoring
  5. Auto-execution from scanner signals

Requirements:
  pip install longbridge
  Environment variables: LB_APP_KEY, LB_APP_SECRET, LB_ACCESS_TOKEN
"""

import os
import json
import time
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# Try importing longbridge SDK
try:
    from longbridge.openapi import Config, TradeContext, QuoteContext
    from longbridge.openapi import OrderSide, OrderType, TimeInForceType
    HAS_LONGBRIDGE = True
except ImportError:
    HAS_LONGBRIDGE = False


@dataclass
class LivePosition:
    """Tracks a live position with stop/target management."""
    ticker: str
    shares: int
    entry_price: float
    entry_date: str
    stop_price: float
    setup_type: str
    score: float
    trail_ma: int = 20
    highest_close: float = 0.0
    partial_sold: bool = False
    order_id: str = ""


@dataclass
class LiveConfig:
    """Configuration for live trading."""
    app_key: str = ""
    app_secret: str = ""
    access_token: str = ""
    max_positions: int = 10
    max_risk_per_trade_pct: float = 0.01
    max_total_risk_pct: float = 0.06
    paper_trade: bool = True  # Safety: paper trade by default
    market: str = "US"  # US or HK


class LiveTrader:
    """
    Live trading engine that connects scanner output to Longbridge execution.
    
    Usage:
        trader = LiveTrader(config)
        trader.connect()
        signals = trader.run_daily_scan()
        trader.execute_signals(signals)
    """

    def __init__(self, config: LiveConfig = None):
        self.config = config or LiveConfig()
        self.positions: Dict[str, LivePosition] = {}
        self.trade_log: List[dict] = []
        self.trade_ctx = None
        self.quote_ctx = None
        self._connected = False

        # Load config from env if not provided
        if not self.config.app_key:
            self.config.app_key = os.environ.get("LB_APP_KEY", "")
        if not self.config.app_secret:
            self.config.app_secret = os.environ.get("LB_APP_SECRET", "")
        if not self.config.access_token:
            self.config.access_token = os.environ.get("LB_ACCESS_TOKEN", "")

        # Load saved positions
        self._positions_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "live_state", "positions.json"
        )
        self._load_positions()

    def connect(self) -> bool:
        """Connect to Longbridge API."""
        if not HAS_LONGBRIDGE:
            print("WARNING: longbridge package not installed. Running in simulation mode.")
            print("Install with: pip install longbridge")
            return False

        if not all([self.config.app_key, self.config.app_secret, self.config.access_token]):
            print("WARNING: Longbridge credentials not configured.")
            print("Set environment variables: LB_APP_KEY, LB_APP_SECRET, LB_ACCESS_TOKEN")
            print("Or pass them in LiveConfig. Running in simulation mode.")
            return False

        try:
            lb_config = Config(
                app_key=self.config.app_key,
                app_secret=self.config.app_secret,
                access_token=self.config.access_token,
            )
            self.trade_ctx = TradeContext(lb_config)
            self.quote_ctx = QuoteContext(lb_config)
            self._connected = True
            print("Connected to Longbridge API successfully!")
            return True
        except Exception as e:
            print(f"Failed to connect to Longbridge: {e}")
            print("Running in simulation mode.")
            return False

    def get_account_balance(self) -> dict:
        """Get current account balance."""
        if not self._connected:
            return {"cash": 0, "total_equity": 0, "error": "Not connected"}
        
        try:
            balances = self.trade_ctx.account_balance()
            if balances:
                b = balances[0]
                return {
                    "cash": float(b.cash_infos[0].available_cash) if b.cash_infos else 0,
                    "total_equity": float(b.total_cash),
                    "currency": "USD",
                }
        except Exception as e:
            return {"error": str(e)}
        return {"cash": 0, "total_equity": 0}

    def get_positions(self) -> List[dict]:
        """Get current broker positions."""
        if not self._connected:
            return [{"ticker": p.ticker, "shares": p.shares, "entry": p.entry_price} 
                    for p in self.positions.values()]
        
        try:
            positions = self.trade_ctx.stock_positions()
            result = []
            for channel in positions.channels:
                for pos in channel.positions:
                    result.append({
                        "ticker": pos.symbol,
                        "shares": int(pos.quantity),
                        "available": int(pos.available_quantity),
                        "cost": float(pos.cost_price),
                        "market_value": float(pos.market_value) if pos.market_value else 0,
                    })
            return result
        except Exception as e:
            print(f"Error getting positions: {e}")
            return []

    def place_order(
        self,
        ticker: str,
        side: str,  # "BUY" or "SELL"
        shares: int,
        price: float = None,  # None = market order
        order_type: str = "LIMIT",
    ) -> Optional[str]:
        """Place an order through Longbridge."""
        
        # Map ticker to Longbridge symbol format
        symbol = f"US.{ticker}" if self.config.market == "US" else f"HK.{ticker}"
        
        if self.config.paper_trade:
            order_id = f"PAPER_{datetime.now().strftime('%Y%m%d%H%M%S')}_{ticker}"
            print(f"[PAPER] {side} {shares} {ticker} @ ${price or 'MKT'} -> {order_id}")
            self._log_trade(ticker, side, shares, price or 0, order_id, "PAPER")
            return order_id

        if not self._connected:
            print(f"[SIM] {side} {shares} {ticker} @ ${price or 'MKT'}")
            return None

        try:
            lb_side = OrderSide.Buy if side == "BUY" else OrderSide.Sell
            
            if order_type == "MARKET" or price is None:
                lb_type = OrderType.Market
                submitted_price = 0
            else:
                lb_type = OrderType.LO  # Limit order
                submitted_price = price

            resp = self.trade_ctx.submit_order(
                symbol=symbol,
                order_type=lb_type,
                side=lb_side,
                submitted_quantity=shares,
                submitted_price=submitted_price,
                time_in_force=TimeInForceType.Day,
                remark=f"AlgoSystem_{datetime.now().strftime('%Y%m%d')}",
            )
            
            order_id = resp.order_id
            print(f"[LIVE] {side} {shares} {ticker} @ ${price or 'MKT'} -> Order ID: {order_id}")
            self._log_trade(ticker, side, shares, price or 0, order_id, "LIVE")
            return order_id
            
        except Exception as e:
            print(f"Order failed for {ticker}: {e}")
            return None

    def execute_signals(self, signals: list, available_cash: float = None):
        """Execute trading signals from the scanner."""
        from algo.config import KITCHIN, QMAG, MAX_POSITIONS
        from algo.indicators import kitchin_cycle_position
        
        today = date.today()
        cycle_pos = kitchin_cycle_position(today, KITCHIN.c3_trough, KITCHIN.period_months)
        cycle_mult = KITCHIN.get_cycle_sizing_multiplier(cycle_pos)
        cycle_phase = KITCHIN.get_phase_label(cycle_pos)
        
        print(f"\nKitchin Phase: {cycle_phase} (pos={cycle_pos:.2f}, sizing mult={cycle_mult:.1f}x)")
        
        if available_cash is None:
            balance = self.get_account_balance()
            available_cash = balance.get("cash", 0)
            if available_cash == 0 and not self._connected:
                available_cash = 8000  # Default for simulation
                
        current_positions = len(self.positions)
        max_new = MAX_POSITIONS - current_positions
        
        if max_new <= 0:
            print(f"At max positions ({current_positions}/{MAX_POSITIONS}). No new entries.")
            return
        
        print(f"Available slots: {max_new} | Cash: ${available_cash:,.0f}")
        
        for signal in signals[:max_new]:
            ticker = signal.ticker
            if ticker in self.positions:
                continue
            
            # Calculate position size
            risk_per_trade = available_cash * QMAG.risk_per_trade_pct * cycle_mult
            risk_per_share = signal.entry_price - signal.stop_price
            
            if risk_per_share <= 0:
                continue
            
            shares = int(risk_per_trade / risk_per_share)
            if shares <= 0:
                continue
            
            cost = shares * signal.entry_price
            if cost > available_cash * 0.95:  # Keep 5% buffer
                shares = int(available_cash * 0.95 / signal.entry_price)
            
            if shares <= 0:
                continue
            
            # Place order
            order_id = self.place_order(
                ticker=ticker,
                side="BUY",
                shares=shares,
                price=round(signal.entry_price, 2),
                order_type="LIMIT",
            )
            
            if order_id:
                self.positions[ticker] = LivePosition(
                    ticker=ticker,
                    shares=shares,
                    entry_price=signal.entry_price,
                    entry_date=str(today),
                    stop_price=signal.stop_price,
                    setup_type=signal.setup_type,
                    score=signal.score,
                    order_id=order_id,
                )
                available_cash -= cost
                self._save_positions()
                
        print(f"\nActive positions: {len(self.positions)}")

    def check_stops(self, current_prices: Dict[str, float]):
        """Check all positions against stop losses."""
        to_close = []
        
        for ticker, pos in self.positions.items():
            price = current_prices.get(ticker)
            if price is None:
                continue
            
            # Update highest
            if price > pos.highest_close:
                pos.highest_close = price
            
            # Check stop
            if price <= pos.stop_price:
                print(f"STOP HIT: {ticker} at ${price:.2f} (stop=${pos.stop_price:.2f})")
                order_id = self.place_order(ticker, "SELL", pos.shares, order_type="MARKET")
                if order_id:
                    to_close.append(ticker)
        
        for ticker in to_close:
            del self.positions[ticker]
        
        if to_close:
            self._save_positions()

    def portfolio_summary(self) -> dict:
        """Get current portfolio status."""
        from algo.config import KITCHIN
        from algo.indicators import kitchin_cycle_position
        
        today = date.today()
        cycle_pos = kitchin_cycle_position(today, KITCHIN.c3_trough, KITCHIN.period_months)
        
        return {
            "date": str(today),
            "num_positions": len(self.positions),
            "positions": {
                ticker: {
                    "shares": p.shares,
                    "entry": p.entry_price,
                    "stop": p.stop_price,
                    "setup": p.setup_type,
                    "entry_date": p.entry_date,
                }
                for ticker, p in self.positions.items()
            },
            "kitchin_phase": KITCHIN.get_phase_label(cycle_pos),
            "kitchin_position": round(cycle_pos, 3),
            "cycle_sizing_mult": KITCHIN.get_cycle_sizing_multiplier(cycle_pos),
        }

    def _log_trade(self, ticker, side, shares, price, order_id, mode):
        """Log a trade."""
        self.trade_log.append({
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker,
            "side": side,
            "shares": shares,
            "price": price,
            "order_id": order_id,
            "mode": mode,
        })

    def _save_positions(self):
        """Save positions to disk."""
        os.makedirs(os.path.dirname(self._positions_file), exist_ok=True)
        data = {
            ticker: {
                "ticker": p.ticker,
                "shares": p.shares,
                "entry_price": p.entry_price,
                "entry_date": p.entry_date,
                "stop_price": p.stop_price,
                "setup_type": p.setup_type,
                "score": p.score,
                "highest_close": p.highest_close,
                "partial_sold": p.partial_sold,
                "order_id": p.order_id,
            }
            for ticker, p in self.positions.items()
        }
        with open(self._positions_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load_positions(self):
        """Load saved positions from disk."""
        if os.path.exists(self._positions_file):
            try:
                with open(self._positions_file, "r") as f:
                    data = json.load(f)
                for ticker, pdata in data.items():
                    self.positions[ticker] = LivePosition(**pdata)
                print(f"Loaded {len(self.positions)} saved positions.")
            except Exception as e:
                print(f"Could not load positions: {e}")


def run_live_cycle():
    """Run one cycle of the live trading system."""
    from algo.config import KITCHIN
    from algo.indicators import kitchin_cycle_position
    from algo.main import run_scan
    
    print(f"\n{'#'*70}")
    print(f"# LIVE TRADING SYSTEM")
    print(f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    cycle_pos = kitchin_cycle_position(date.today(), KITCHIN.c3_trough, KITCHIN.period_months)
    phase = KITCHIN.get_phase_label(cycle_pos)
    mult = KITCHIN.get_cycle_sizing_multiplier(cycle_pos)
    
    print(f"# Kitchin: {phase} | Pos: {cycle_pos:.3f} | Size Mult: {mult:.1f}x")
    print(f"{'#'*70}\n")
    
    # Initialize trader
    trader = LiveTrader()
    connected = trader.connect()
    
    # Show current portfolio
    summary = trader.portfolio_summary()
    print(f"Current positions: {summary['num_positions']}")
    for ticker, info in summary["positions"].items():
        print(f"  {ticker}: {info['shares']} shares @ ${info['entry']:.2f} "
              f"(stop=${info['stop']:.2f}, setup={info['setup']})")
    
    # Run scanner
    print("\nRunning scanner...")
    signals = run_scan()
    
    if signals:
        print(f"\nFound {len(signals)} signals. Execute? (y/n)")
        # In automated mode, execute automatically
        # trader.execute_signals(signals)
    else:
        print("\nNo signals found today.")
    
    return trader, signals


if __name__ == "__main__":
    run_live_cycle()
