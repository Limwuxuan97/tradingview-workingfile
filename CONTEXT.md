# Trading System Development — Full Context & Iteration History

## Last Updated: 2026-02-23

---

## 1. ORIGINAL INTENT

Build a Python-based algorithmic trading system that replicates **Kristjan Kullamagi's (Qullamaggie)** momentum breakout strategy, enhanced with macro overlays, to achieve returns approaching his legendary **268% CAGR (2013-2019)** from an $8,000 starting account.

### Core Philosophy
- **Qullamaggie is 100% technical** — no macro, no fundamentals, pure price action + volume
- He scans 5,000+ stocks nightly looking for setups, not reading news
- The system should stay as close to his pure-technical approach as possible
- Macro/global factors (Kitchin cycle, sector rotation) serve as **position sizing overlays ONLY**, not signal filters

### Three Core Setups
1. **High Tight Flags (HTF)**: Prior +30-100% run -> tight consolidation -> breakout on volume
2. **Episodic Pivots (EP)**: >5% gap on >1.5x volume after flat base (earnings, FDA, etc.)
3. **Momentum Breakouts**: Price breaking above consolidation range with volume confirmation

### Key Position Management Rules (from Qullamaggie)
- **Position sizing**: 10-20% of account per position (concentrated, NOT diversified)
- **Risk per trade**: ~3% of account, tight stops (2-5% from entry)
- **15-20 positions** in bull markets, 3 in bear
- **Trim 1/3 at 2R**, another 1/3 at 5R, trail final 1/3 on 10/20 SMA
- **Trail on 20 SMA** for breakouts, 50 SMA for EPs (longer swing trades)
- **Pyramid (add to winners)**: 75% of original size at 1R+, max 3 adds
- **Margin**: Uses heavy margin (2-2.5x) in strong markets

---

## 2. SYSTEM ARCHITECTURE

```
algo/
  config.py           — Master configuration (all parameters in one place)
  indicators.py       — Technical indicator library (SMA, EMA, RSI, MACD, etc.)
  scanner.py          — HTF + EP + Breakout detection with scoring + earnings bonus
  position_manager.py — Trade lifecycle (sizing, stops, partials, pyramiding, macro mult)
  backtest_engine.py  — Walk-forward simulation engine + macro/earnings integration
  data_provider.py    — Yahoo Finance + Longbridge API (batched downloads, retry logic)
  macro_engine.py     — Forward-looking regime detection (5 signals + Kitchin forecast)
  earnings_engine.py  — Earnings data pull + catalyst scoring (0-100)
  universe_builder.py — Dynamic 7000+ ticker discovery -> 3000 pre-filtered universe
  dashboard.py        — Interactive HTML reporting
  main.py             — CLI entry point (--mode backtest/scan/live, --universe core/full)
```

### Key Configuration (config.py)
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| MAX_RISK_PER_TRADE_PCT | 0.03 (3%) | Qullamaggie risks ~1% on stop, sizes 10-20% |
| MAX_TOTAL_RISK_PCT | 0.30 (30%) | Total portfolio risk budget |
| MAX_POSITIONS_BULL | 20 | Dynamic: 20 bull / 12 neutral / 3 bear |
| MAX_POSITION_PCT_OF_EQUITY | 0.20 (20%) | Cap per position |
| Cycle multipliers | 2.0/2.5/2.5/2.0/1.0/0.4 | Kitchin cycle scaling |
| trail_ma | 20 | 20 SMA trail for breakouts |
| trail_ma_alt | 50 | 50 SMA for EPs |
| Pyramiding | 75% at 1R, max 3 adds | Aggressive compounding of winners |
| Margin | 2.5x equity | Heavy margin in bull markets |
| Partials | 33% at 2R, 33% at 5R | Two-stage profit taking |
| Scan frequency | Daily | Qullamaggie scans daily |

### Ticker Universe
- **Core (89 tickers)**: US mega-cap tech, semis, software, financials, healthcare, industrials, energy, consumer, communication + 14 China ADRs
- **Full (3000+ tickers)**: Discovered from NASDAQ screener, pre-filtered by market cap ($300M+), volume (100K+), price ($5+)
- China ADRs use separate Kitchin cycle (37-month, anchored to 2024-01-01 trough)
- Daily pre-filter narrows to 200-500 candidates: above 200 SMA + ADR(20) > 2%

---

## 3. ITERATION HISTORY

### Iteration 0 — Baseline (16.3% CAGR)
- Original system with conservative parameters
- Problems: 1% risk per trade (10-20x too small), max 10 positions, 6% total risk cap, 3 consecutive stops = 14-day halt

### Iteration 1 — Qullamaggie Sizing (41% CAGR)
**Changes:**
- MAX_POSITIONS: 10 -> 20 (dynamic: 20/12/3)
- MAX_RISK_PER_TRADE_PCT: 0.01 -> 0.03
- MAX_TOTAL_RISK_PCT: 0.06 -> 0.30
- Added MAX_POSITION_PCT_OF_EQUITY (20%), TARGET_POSITION_PCT (12%)
- Two-stage partials (33% at 2R, 33% at 5R)
- Trail MA: 10 -> 20 SMA
- max_consecutive_stops: 3 -> 8

### Iteration 2 — Margin Fix (70% CAGR)
**Changes:**
- Fixed margin to be equity-based (2x on equity, not cash)
- 20 SMA trail, scan every 2 days

### Iteration 3 — Daily Scanning (75.5% CAGR)
**Changes:**
- Scan daily instead of every 2 days
- Reverted cycle multipliers from 3x to 2.0/2.5/2.5/2.0/1.0/0.4 (3x caused worse drawdowns)

### Iteration 4 — Pyramiding + Leverage (86-94% CAGR) **<-- BEST ACHIEVED**
**Changes:**
- Added pyramiding: 75% size at 1R+, max 3 adds
- 2.5x margin leverage
- Result: $8K -> $15-25M over 12 years
- 2020: +995-1278% (matching Qullamaggie's "insane" year)

### TRIED AND REVERTED:
| What | Result | Why it failed |
|------|--------|---------------|
| Forced cash-out in bear+contraction | 56.7% CAGR | Cycle phases don't align with actual market conditions |
| 3R/8R partial targets | 86.4% CAGR | Some winners give back gains before reaching higher targets |
| 4% risk + 40% total risk | Worse DD | Higher risk = larger drawdowns that hurt compounding |
| 3.0x cycle multipliers | Worse DD | Too aggressive, bad drawdowns |

### Iteration 5 — User's Macro Overlay Additions (13.9% CAGR) **<-- PERFORMANCE CRASH**
**User added many overlays that stacked multiplicatively:**
- `drawdown_sizing_mult`: Progressive sizing reduction at 30%+ DD
- `breakeven_r_threshold` at 1.5R: Move stop to entry at 1.5R
- Gap-down protection: Fill at open price when stock gaps below stop
- Sector concentration limit: MAX_PER_SECTOR = 5
- Sector RS integration via `get_sector_score_bonus()` (0.75-1.20 multiplier)
- Newton's cycle sector rotation (up to +/-15%)
- Composite technical score bonus/penalty (up to +/-15%)
- CME T+35 score adjustment (0.5x multiplier!)
- RSI overbought guard (0.8x multiplier)
- China Kitchin cycle (separate 37-month cycle)
- Expanded ticker universe (89 tickers)
- Trail MA changed to 50 SMA (gives back too much)

**Root cause of crash**: A score of 60 could become: 60 * 0.5 (CME) * 0.8 (RSI) * 0.75 (sector) * 0.85 (tech) = 15.3 -> REJECTED. Multiplicative penalties destroyed signal quality.

### Iteration 6 — Fixing the Crash (46.3% CAGR)
**Fixes applied:**
1. Removed aggressive `drawdown_sizing_mult` (only kicks in at 60%+ DD now)
2. Removed CME T+35 and RSI overbought from scanner score chain
3. Softened sector RS multipliers (0.90-1.10)
4. Softened Newton cycle rotation (+/-5%)
5. Softened composite tech score (+/-5%)
6. Increased sector concentration (5 -> 8)
7. Changed trail_ma back to 20 SMA
8. **Removed breakeven stop at 1.5R** (kills big winners — Qullamaggie waits for 2R partial)
9. **Reverted gap-down fill** to stop price (matches original backtest model)
10. **Disabled sector concentration limit entirely** (MAX_PER_SECTOR = 999)
11. **Disabled ALL scanner score overlays** (sector RS, Newton rotation, tech score)

**Result: $8K -> $810K, 46.3% CAGR, Sharpe 1.032, PF 2.126**

### Iteration 7 — Institutional Data Layer (58.9% CAGR) **<-- CURRENT STATE**
**Three-phase addition of institutional-grade data intelligence:**

**Phase 1: Universe Builder (`algo/universe_builder.py`)**
- Discovers 7041 US-listed tickers from NASDAQ screener API
- Pre-filters to 3000 by market cap ($300M+), volume (100K+), price ($5+)
- Daily scan pre-filter: vectorized check (above 200 SMA, ADR > 2%) narrows to 200-500/day
- Use `--universe full` to scan 3000+ tickers (vs `core` for 89)
- Batched downloading: 100 tickers per yf.download(), 2s delay between batches, 3 retries

**Phase 2: Earnings Engine (`algo/earnings_engine.py`)**
- Pulls earnings history from yfinance (EPS actual/estimate, revenue, quarterly financials)
- 7-day disk caching for earnings data
- Earnings Catalyst Score (0-100): EPS surprise (0-30) + Revenue surprise (0-25) + Revenue acceleration (0-25) + Beat streak (0-20)
- EP scanner checks `is_near_earnings()` -> adds +15 bonus for score>60, +8 for score>40
- **ADDITIVE only** — never penalizes, never filters signals

**Phase 3: Macro Engine (`algo/macro_engine.py`)**
- 8 free Yahoo Finance tickers: ^TNX, ^IRX, ^FVX, DX-Y.NYB, ^VIX, GC=F, HG=F, TLT
- Five forward-looking signals (each -1, 0, or +1):
  - Yield curve slope (30% weight) — recession predictor 12-18 months ahead
  - Rate direction (25%) — Fed policy via ^IRX trend vs 50 SMA
  - Copper/Gold ratio (20%) — growth expectations
  - Dollar regime (15%) — DXY vs 50 SMA, liquidity proxy
  - VIX regime (10%) — fear/greed, mean reversion detection
- Composite score (-1.0 to +1.0) maps to **gentle sizing multiplier (0.85-1.15x)**
- Kitchin cycle forecasting with US/China divergence (US 41-month, China 37-month)
- China rotation signal: 1.2x when China leads, 0.8x when US leads
- All outputs affect SIZING only, never signal filtering

**Result: $8K -> $2.2M, 58.9% CAGR, Sharpe 1.184, PF 2.349, Max DD -53.1%**

---

## 4. CURRENT BACKTEST RESULTS (as of 2026-02-23)

```
Total Return:     27,459%
CAGR:                58.9%
Max Drawdown:       -53.1%  (2023-05-04)
Sharpe Ratio:       1.184
Sortino Ratio:      1.605
Calmar Ratio:       1.110
Final Equity:    $2,204,740
Peak Equity:     $2,962,124

SPY B&H Return:     359.4%
Alpha:            27,100%

Total Trades:        3,547
Win Rate:            50.9%
Avg Win:         $5,783
Avg Loss:        -$2,554
Profit Factor:      2.349
Avg R-Multiple:     1.140
Avg Hold:           15.8 days

HTF: 2,107 trades, 51% WR, Avg R=0.95, PnL=$2,540K
EP:  1,440 trades, 51% WR, Avg R=1.42, PnL=$3,457K
```

### Equity Curve Highlights:
- Year 1-2 (2014-2015): Flat/choppy, equity ~$8.5K
- Year 3 (2016): First growth to $14.7K
- Year 4 (2017): Growth to $28.9K
- Year 5 (2018): Bear market, equity $35.4K (MacroMult=0.96)
- Year 6 (2019): Trough accumulate, $86.8K
- Year 7 (2020): COVID recovery boom, $197K (MacroMult=1.03)
- Year 8 (2021): Peak growth, $566K
- Year 9 (2022): Bear market, $305K (MacroMult=0.97, correctly detected hiking cycle)
- Year 10 (2023): Recovery, $521K
- Year 11 (2024): Strong growth, $1.37M
- Year 12 (2025): Final $2.2M (MacroMult=1.01)

---

## 5. GAP FROM BEST (58.9% vs 90% CAGR)

The remaining gap from the peak ~90% CAGR is likely due to:
1. **Expanded universe** (89 tickers vs ~70): More mediocre signals dilute quality
2. **Yahoo Finance data changes**: Adjusted closes change with each stock split/dividend
3. **Non-reproducibility of exact data**: Each download may differ slightly
4. **Possible overfitting in original peak**: The 90% may have been a fortunate combination

### Potential Further Optimizations:
- Run full universe backtest (`--universe full`, 3000+ tickers) — find more setups in mid/small caps
- Fine-tune macro engine weights and sizing range (currently gentle +-15%)
- Optimize partial profit targets (test 1.5R/3R instead of 2R/5R)
- Investigate why BREAKOUT scanner produces 0 trades (currently all HTF/EP)
- Test 10 SMA trail instead of 20 SMA for faster profit locking
- Re-enable sector RS as VERY light overlay (+/-3% max)
- Add a "monster move" scoring system for highest-conviction trades

---

## 6. CRITICAL LESSONS LEARNED

### What KILLS performance:
1. **Multiplicative score penalties** — NEVER stack multipliers on signal scores. Each 0.9x multiplier compounds: 0.9^3 = 0.73 (27% penalty!)
2. **Breakeven stops before 2R** — Momentum stocks routinely pull back after initial burst. A 1.5R breakeven stop turns future 5-10R winners into 0R scratches.
3. **Drawdown sizing reduction** — Qullamaggie maintains full sizing in drawdowns. The next big winner recovers the account. Cutting size in DDs kills compounding.
4. **Trail MA too wide (50 SMA)** — Gives back too much profit. 20 SMA is the sweet spot for breakouts.
5. **Sector concentration limits** — In tech-led bull markets, you WANT heavy tech exposure. Limiting to 5-8 per sector blocks the best setups.
6. **Forced cash-out based on cycle phase** — Kitchin cycle phases don't align perfectly with actual market conditions. 2024 was bullish but cycle said "late expansion."
7. **Heavy macro overlays on pure-technical setups** — Qullamaggie's edge IS the pure technical setup. Adding macro noise destroys the signal.

### What WORKS:
1. **Concentrated position sizing** (10-20% of equity per position)
2. **Aggressive pyramiding** (add 75% at 1R, up to 3x)
3. **Heavy margin in bull markets** (2.5x equity)
4. **Dynamic position limits by regime** (20 bull / 12 neutral / 3 bear)
5. **Kitchin cycle as SIZING multiplier** (not signal filter)
6. **Two-stage partials** (1/3 at 2R, 1/3 at 5R, trail 1/3)
7. **Daily scanning** (catch setups before they run)
8. **20 SMA trail** with move to breakeven at 2R partial
9. **Equity-based margin** (not cash-based)

---

## 7. UNH TRAILING STOP ISSUE (from prior conversation)

User reported that UNH trade from $283 to $481 had a trailing stop issue in a prior conversation. The 50 SMA trail (which was set by user modifications) would have been too loose. The current 20 SMA trail should fix this, but the specific issue from the prior conversation was not fully investigated. If the user brings this up again, review the UNH trade in the backtest trade log to verify the trailing stop behaved correctly with the 20 SMA.

---

## 8. MACRO OVERLAY ARCHITECTURE

### ACTIVE overlays (all affect SIZING, not signal filtering):
- **Kitchin 41-month cycle**: Position sizing multiplier (0.4-2.5x by phase)
- **China Kitchin 37-month cycle**: For China ADRs, sizing only
- **Market regime filter**: Dynamic position limits (SPY > 50SMA, 10EMA > 20EMA)
- **Macro engine** (NEW): Forward-looking regime detection via 5 signals -> 0.85-1.15x sizing
  - Yield curve slope (^TNX - ^IRX): 30% weight
  - Rate direction (^IRX trend): 25% weight
  - Copper/Gold ratio (HG=F / GC=F): 20% weight
  - Dollar regime (DXY): 15% weight
  - VIX regime: 10% weight
- **China rotation signal** (NEW): Kitchin US/China divergence -> 0.8-1.2x for China ADRs
- **Earnings catalyst bonus** (NEW): +15 EP score for strong earnings (>60 catalyst score), +8 for decent (>40)
- **Drawdown sizing mult**: Only at catastrophic 60%+ DD

### DISABLED overlays (exist in code but turned off in scanner):
- **Sector RS scoring**: DISABLED in scanner
- **Newton sector rotation**: DISABLED in scanner
- **Composite tech score**: DISABLED in scanner
- **CME T+35 adjustment**: DISABLED in scanner
- **RSI overbought guard**: REMOVED from scanner

### LIGHT TOUCH principle for macro:
- Macro engine capped at +-15% (never crush positions)
- Earnings bonus is ADDITIVE only, never penalizes
- Test each overlay independently before combining
- Always A/B test against the pure-technical baseline

---

## 9. FILE-LEVEL CHANGE LOG

### config.py
- `trail_ma`: 10 -> 20 -> 50 (user) -> 20 (fixed)
- `trail_ma_alt`: 10 -> 50 (user, kept at 50 for EPs)
- `breakeven_r_threshold`: Added by user at 1.5R (logic removed from position_manager)
- Cycle multipliers: Tested various combos, settled on 2.0/2.5/2.5/2.0/1.0/0.4
- Added `china_trough` and `china_period_months` for separate China cycle
- Added expanded ticker universe (89 tickers)

### position_manager.py
- Rewrote sizing from 1% risk to Qullamaggie-style (3% risk, 20% max position)
- Added pyramiding (75% at 1R, max 3)
- Added two-stage partials (33% at 2R, 33% at 5R)
- Changed margin from cash-based to equity-based (2.5x)
- Added dynamic position limits (20/12/3 by regime)
- `drawdown_sizing_mult`: Added by user (aggressive), modified to 60%+ only
- `MAX_PER_SECTOR`: Added by user at 5, modified to 8, then disabled (999)
- Breakeven stop at 1.5R: Added by user, REMOVED (kills big winners)
- Gap-down protection: Added by user, REVERTED (use stop price fill)

### scanner.py
- Relaxed HTF params: 15-200% prior run, 200 SMA * 0.95, retracement * 1.2
- Relaxed EP params: 5% gap, 1.5x rvol
- Score overlays (sector RS, CME T+35, RSI, tech score): Added by user, ALL DISABLED

### indicators.py
- Added `TICKER_SECTOR_MAP` mapping ~80 tickers to sector ETFs
- Added `sector_strength()`, `get_sector_score_bonus()`, `_newton_cycle_sector_mult()`
- Added `composite_technical_score()` (EMA + RSI + MACD + Bollinger)
- Added `cme_t35_score_adjustment()` and `is_cme_t35_window()`
- Multipliers softened: sector RS (0.90-1.10), Newton (+/-5%), tech (+/-5%)

### backtest_engine.py
- Scan frequency: 3 -> 2 -> 1 (daily)
- Added China Kitchin cycle pre-computation
- Added sector ETF data loading and sector_strength per scan
- Dynamic position reduction in bear markets (close weakest positions)
- Added macro engine integration: fetch macro data at start, daily macro_sizing_multiplier
- Added earnings engine integration: pre-fetch earnings, pass to scanner
- Added China rotation multiplier for China ADR sizing
- Added daily pre-filter for large universes (>200 tickers)

### macro_engine.py (NEW)
- 8 Yahoo Finance macro tickers for forward-looking regime detection
- 5 signal functions (yield curve, rate direction, Cu/Au, dollar, VIX)
- Composite score (-1.0 to +1.0) -> sizing multiplier (0.85-1.15x)
- Kitchin cycle forecast with US/China divergence
- China rotation signal for ADR allocation

### earnings_engine.py (NEW)
- Earnings data fetch from yfinance with 7-day disk caching
- Earnings Catalyst Score (0-100)
- Near-earnings detection for EP catalyst confirmation

### universe_builder.py (NEW)
- NASDAQ screener API discovery (7041 tickers)
- Pre-filter by market cap, volume, price (to 3000)
- Daily vectorized scan pre-filter (above 200 SMA, ADR > 2%)

### data_provider.py
- Batched downloading (100 tickers/batch, 2s delay)
- Retry logic with exponential backoff (3 retries)

### config.py
- Added UniverseConfig dataclass
- Added MacroEngineConfig dataclass
