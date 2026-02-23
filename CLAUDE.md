# Qullamaggie Algo Trading System

## Quick Start
```bash
python -m algo.main --mode backtest    # Run backtest ($8K, 2014-2026)
python -m algo.main --mode scan        # Scan for live setups
python -m algo.main --mode live        # Live trading mode
```

## What This Is
A Python algorithmic trading system replicating **Kristjan Kullamagi's (Qullamaggie)** momentum breakout strategy with Kitchin cycle position sizing. The user's goal is to grow $8,000 to millions using aggressive concentrated momentum trading.

**Read [CONTEXT.md](CONTEXT.md) for the FULL iteration history, all lessons learned, and architectural decisions.**

## Current State (2026-02-23)
- **CAGR: 58.9%** | $8K -> $2.2M over 12 years | Sharpe 1.184 | PF 2.349
- **Best achieved: ~90% CAGR** ($8K -> $15-25M) — gap is from expanded universe + data changes
- Max Drawdown: -53.1% | Win Rate: 50.9% | 3,547 trades
- **Macro engine + earnings engine integrated** (forward-looking regime detection)
- **Universe builder ready** (`--universe full` for 3000+ tickers)

## Architecture
```
algo/config.py           — All parameters (sizing, cycle, scanning, macro, universe)
algo/scanner.py          — HTF + EP + Breakout signal detection + earnings catalyst bonus
algo/position_manager.py — Trade lifecycle (sizing, stops, partials, pyramiding, macro mult)
algo/backtest_engine.py  — Walk-forward simulation + macro/earnings integration
algo/indicators.py       — Technical indicators + sector mapping
algo/data_provider.py    — Yahoo Finance + Longbridge API (batched downloads)
algo/macro_engine.py     — Forward-looking regime detection (yield curve, rates, Cu/Au, DXY, VIX)
algo/earnings_engine.py  — Earnings data pull + catalyst scoring (0-100)
algo/universe_builder.py — Dynamic 7000+ ticker discovery -> 3000 pre-filtered
algo/dashboard.py        — HTML reporting
algo/main.py             — CLI entry point (--universe core/full)
```

## Critical Rules (DO NOT VIOLATE)

### 1. No multiplicative score penalties in scanner
The scanner scores signals 0-100. NEVER apply multiplicative penalty chains (e.g., score * 0.9 * 0.8 * 0.75). This crashed CAGR from 90% to 13.9%. Macro factors belong in **position sizing**, not signal scoring.

### 2. No breakeven stop before 2R partial
Momentum stocks pull back after initial moves. A breakeven stop at 1.5R kills future 5-10R winners. The stop moves to breakeven ONLY when the 2R partial triggers (which also trims 1/3).

### 3. Qullamaggie is 100% technical
He does NOT use macro, fundamentals, sector rotation, or RSI guards for entry decisions. The system's macro overlays (Kitchin cycle, macro engine, sector RS) are applied via **position sizing multiplier only**, not signal filtering. Earnings data is ADDITIVE only (+15 bonus for strong catalyst EPs, never penalizes).

### 4. Keep position sizing aggressive
3% risk per trade, 20% max position, 2.5x margin, pyramid 75% at 1R. Reducing sizing in drawdowns kills compounding. Only reduce at catastrophic 60%+ drawdown.

### 5. Trail on 20 SMA, not 50
50 SMA gives back too much profit. 20 SMA is the default for breakouts. EPs use 50 SMA (longer-term trades).

## What Was Tried and Failed
See CONTEXT.md Section 3 "TRIED AND REVERTED" for full details:
- Forced cash-out in bear+contraction -> 56.7% (cycle phases misalign with reality)
- 3R/8R partial targets -> 86.4% (winners give back gains before reaching)
- 4% risk / 40% total risk -> Worse drawdowns
- Breakeven stop at 1.5R -> Killed big winners
- Heavy sector/macro score overlays -> Crashed to 13.9%

## Next Opportunities to Explore
1. Run full universe backtest (`--universe full`, 3000+ tickers) — find more setups
2. Investigate why BREAKOUT scanner produces 0 trades (all trades are HTF/EP)
3. Test 10 SMA trail vs 20 SMA for faster profit locking
4. Re-enable sector RS as VERY light overlay (+/-3% max, A/B tested)
5. Add "monster move" scoring for highest-conviction trade sizing
6. Optimize partial targets (test 1.5R/3R instead of 2R/5R)
7. Fine-tune macro engine weights (currently yield curve 30%, rates 25%, Cu/Au 20%, DXY 15%, VIX 10%)
8. Test more aggressive macro sizing range (currently +-15% max)

## Key Reference Files
- [Qullamaggie Trading System Blueprint.docx](Qullamaggie%20Trading%20System%20Blueprint.docx) — Full methodology
- [Strategic Book allocation.xlsx](Strategic%20Book%20allocation.xlsx) — Kitchin cycle timing
- [CONVERSATION_CONTEXT.md](CONVERSATION_CONTEXT.md) — Original session context (BABA analysis, CME mechanics)
- [CONTEXT.md](CONTEXT.md) — **Full iteration history and lessons learned**
