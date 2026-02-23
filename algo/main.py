"""
MAIN — Unified Trading System Entry Point
==========================================
Modes:
  1. BACKTEST: Walk-forward simulation over historical data
  2. SCAN: Run current scanner on latest data
  3. LIVE: Connect to Longbridge for live signals (future)

Usage:
  python -m algo.main --mode backtest
  python -m algo.main --mode scan
  python -m algo.main --mode live
"""

import sys
import os
import json
import argparse
from datetime import datetime, date, timedelta

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algo.config import (
    FULL_UNIVERSE, SECTOR_ETF_UNIVERSE, BENCHMARK_TICKER,
    BACKTEST_START, BACKTEST_END, INITIAL_CAPITAL, KITCHIN, UNIVERSE,
)
from algo.data_provider import YFinanceProvider
from algo.backtest_engine import BacktestEngine
from algo.scanner import run_full_scan
from algo.indicators import kitchin_cycle_position


def run_backtest(
    universe: list = None,
    start: str = BACKTEST_START,
    end: str = BACKTEST_END,
    capital: float = INITIAL_CAPITAL,
    scan_freq: int = 3,
    universe_mode: str = "core",
):
    """Run full backtest."""
    if universe is None:
        if universe_mode == "full":
            # Dynamic universe: discover and pre-filter 3000+ tickers
            from algo.universe_builder import build_backtest_universe
            universe = build_backtest_universe(
                min_market_cap=UNIVERSE.min_market_cap,
                min_volume=UNIVERSE.min_avg_volume,
                min_price=UNIVERSE.min_price,
                max_tickers=UNIVERSE.max_tickers,
            )
        else:
            # Core universe: hardcoded 89 tickers from config
            from algo.config import FULL_UNIVERSE
            universe = FULL_UNIVERSE

    print(f"\n{'#'*70}")
    print(f"# UNIFIED TRADING SYSTEM — BACKTEST MODE")
    print(f"# Universe: {len(universe)} tickers")
    print(f"# Period: {start} to {end}")
    print(f"# Capital: ${capital:,.0f}")
    print(f"# Kitchin C3 Trough: {KITCHIN.c3_trough}")
    print(f"# Kitchin C4 Projected Trough: {KITCHIN.c4_trough_projected}")
    print(f"{'#'*70}\n")

    # Fetch data
    print("Fetching historical data...")
    provider = YFinanceProvider()

    # Add SPY to universe if not present
    all_tickers = list(set(universe + [BENCHMARK_TICKER]))

    data = provider.get_bulk_ohlcv(all_tickers, start, end)

    # Separate SPY
    spy_data = data.pop(BENCHMARK_TICKER, None)
    if spy_data is None or spy_data.empty:
        print("ERROR: Could not fetch SPY data. Aborting.")
        return None

    universe_data = {t: df for t, df in data.items() if not df.empty}
    print(f"Loaded {len(universe_data)} tickers with data (out of {len(universe)} requested)")

    if len(universe_data) < 5:
        print("WARNING: Very few tickers loaded. Results may be unreliable.")

    # Fetch sector ETF data for sector rotation scoring
    sector_etfs = ["XLK", "XLF", "XLE", "XLI", "XLV", "XLY", "XLP", "XLC", "KWEB"]
    print(f"Fetching {len(sector_etfs)} sector ETFs for rotation scoring...")
    sector_etf_data = provider.get_bulk_ohlcv(sector_etfs, start, end)
    sector_etf_data = {t: df for t, df in sector_etf_data.items() if not df.empty}
    print(f"Loaded {len(sector_etf_data)} sector ETFs")

    # Run backtest
    engine = BacktestEngine(
        universe_data=universe_data,
        spy_data=spy_data,
        initial_capital=capital,
        scan_frequency=scan_freq,
        start_date=start,
        end_date=end,
        verbose=True,
        sector_etf_data=sector_etf_data,
    )

    results = engine.run()

    # Save results
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backtest_results")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"backtest_{timestamp}.json")

    # Convert non-serializable types
    serializable = json.loads(json.dumps(results, default=str))
    with open(output_file, "w") as f:
        json.dump(serializable, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    # Generate interactive dashboard
    from algo.dashboard import generate_dashboard
    dashboard_path = os.path.join(output_dir, f"dashboard_{timestamp}.html")
    generate_dashboard(serializable, dashboard_path)
    print(f"Dashboard saved to: {dashboard_path}")

    return results


def run_scan():
    """Run current scanner on latest data."""
    print(f"\n{'#'*70}")
    print(f"# UNIFIED TRADING SYSTEM — DAILY SCAN")
    print(f"# Date: {date.today()}")
    print(f"{'#'*70}\n")

    # Current Kitchin cycle position
    cycle_pos = kitchin_cycle_position(date.today(), KITCHIN.c3_trough, KITCHIN.period_months)
    cycle_phase = KITCHIN.get_phase_label(cycle_pos)
    cycle_score = KITCHIN.get_cycle_score(cycle_pos)

    print(f"Kitchin Cycle Position: {cycle_pos:.3f} ({cycle_phase})")
    print(f"Cycle Score: {cycle_score:.1f}/100")
    print(f"Cycle Sizing Multiplier: {KITCHIN.get_cycle_sizing_multiplier(cycle_pos):.2f}x\n")

    # Fetch latest data (6 months back)
    provider = YFinanceProvider()
    start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")

    # Dynamic universe: pull S&P 500 + China ADRs (any ticker can qualify)
    from algo.data_provider import get_dynamic_universe
    scan_universe = get_dynamic_universe(include_china=True)
    all_tickers = list(set(scan_universe + [BENCHMARK_TICKER]))
    print(f"Fetching data for {len(all_tickers)} tickers...")
    data = provider.get_bulk_ohlcv(all_tickers, start, end)

    spy_data = data.pop(BENCHMARK_TICKER, None)
    if spy_data is None or spy_data.empty:
        print("ERROR: Could not fetch SPY data.")
        return

    universe_data = {t: df for t, df in data.items() if not df.empty and len(df) > 50}
    print(f"Scanning {len(universe_data)} tickers...\n")

    results = run_full_scan(universe_data, spy_data, min_score=40.0)

    if not results:
        print("No setups found today.")
        return

    print(f"Found {len(results)} setups (sorted by score):\n")
    print(f"{'Ticker':8s} {'Setup':10s} {'Score':6s} {'ADR%':6s} {'RS':6s} "
          f"{'RVol':6s} {'Entry':8s} {'Stop':8s} {'Risk%':6s} {'Prior%':7s}")
    print("-" * 82)

    for r in results[:20]:  # Top 20
        print(f"{r.ticker:8s} {r.setup_type:10s} {r.score:6.1f} {r.adr:6.1f} "
              f"{r.rs_rank:6.1f} {r.rvol:6.1f} ${r.entry_price:<7.2f} "
              f"${r.stop_price:<7.2f} {r.risk_pct:6.1f} {r.prior_run:7.1f}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Unified Trading System")
    parser.add_argument("--mode", choices=["backtest", "scan", "live"],
                        default="backtest", help="Operating mode")
    parser.add_argument("--start", default=BACKTEST_START, help="Backtest start date")
    parser.add_argument("--end", default=BACKTEST_END, help="Backtest end date")
    parser.add_argument("--capital", type=float, default=INITIAL_CAPITAL, help="Starting capital")
    parser.add_argument("--scan-freq", type=int, default=5, help="Scan frequency in trading days")
    parser.add_argument("--universe", choices=["core", "full"], default="core",
                        help="Universe: 'core' (89 tickers) or 'full' (3000+ discovered)")

    args = parser.parse_args()

    if args.mode == "backtest":
        run_backtest(start=args.start, end=args.end, capital=args.capital,
                     scan_freq=args.scan_freq, universe_mode=args.universe)
    elif args.mode == "scan":
        run_scan()
    elif args.mode == "live":
        print("Live mode not yet implemented. Use --mode scan for daily signals.")


if __name__ == "__main__":
    main()
