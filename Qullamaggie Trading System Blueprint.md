# Qullamaggie Trading System Blueprint

> Converted from `.docx` to Markdown (best-effort automated conversion).

# Systematic Replication of the Qullamaggie Momentum Methodology: A Quantitative Framework

The translation of discretionary breakout momentum trading into a fully automated, programmatic system requires a rigorous deconstruction of both market microstructure and behavioral price action. The methodology engineered by Kristjan Kullamägi—commonly referred to as Qullamaggie—capitalizes on severe structural imbalances in supply and demand, specifically targeting equities exhibiting extreme relative strength, explosive volatility, and institutional accumulation.1 This methodology eschews mean-reversion in favor of trend-following and momentum bursts, capturing the specific statistical anomalies in market distribution where outsized, multi-bagger returns reside.2

This report provides an exhaustive, mathematically defined blueprint for algorithmically replicating the Qullamaggie strategy. By translating visual chart patterns and discretionary heuristics into strict quantitative logic, this framework establishes the exact parameters for setup identification, universe screening, execution triggers, risk containment, and regime filtering. The objective is to provide a programmatic architecture suitable for API integration, transforming behavioral market observation into systematic execution.

## 1. The Core Setups (The "What")

The foundation of this quantitative framework rests on three highly specific market anomalies: High Tight Flags (HTFs), Episodic Pivots (EPs), and Parabolic Shorts. These setups are not merely visual chart patterns; they are statistical representations of psychological extremes, institutional capital flows, and sudden fundamental repricing events. The algorithmic detection of these setups requires precise mathematical conditions to filter out market noise and isolate genuine accumulation or distribution.

### High Tight Flags (HTFs)

The High Tight Flag (HTF) is the primary continuation setup within the methodology, designed to capture secondary and tertiary momentum bursts in assets that have already demonstrated extreme accumulation.5 The underlying market mechanics dictate that when an asset experiences a massive price surge, the natural expectation is a mean-reverting sell-off as early buyers take profits. An HTF forms when this expected sell-off does not occur.5 Instead, the asset consolidates near its absolute highs, indicating that institutional demand is aggressively absorbing all available secondary supply, setting the stage for a subsequent explosive advance.5

To programmatically identify an HTF, the algorithm must first detect the "pole"—the initial phase of extreme momentum. The asset must exhibit a rapid price appreciation of at least 30% to 100% within a compressed timeframe, typically between four to eight weeks, or spanning a rolling one-month (1M), three-month (3M), and six-month (6M) lookback period.6 In systematic terms, the system must scan for equities ranking in the top 1% to 2.5% of relative performance across the broader market during these specific temporal windows.3

Following this surge, the algorithm must evaluate the consolidation phase, or the "flag." This phase is characterized by a Volatility Contraction Pattern (VCP), wherein the asset's trading range systematically narrows, and intraday volatility compresses.12 The maximum allowable drawdown from the peak of the pole to the trough of the base is strictly capped at 25%, though optimal, highly algorithmic setups retrace between 10% and 20%.5 A retracement exceeding 25% invalidates the HTF thesis, as it signals a structural shift from institutional accumulation to broader market distribution.5 The duration of this consolidation must span a minimum of five trading days up to a maximum of eight weeks.5 Furthermore, the algorithm must detect a severe volume contraction during the base formation, verifying that selling pressure has completely evaporated.6

| **HTF Parameter** | **Mathematical Condition / Programmatic Filter** |
| --- | --- |
| **Prior Trend (The Pole)** | Price current >= Price past (20-40 days) * 1.30 to 2.00 |
| **Momentum Percentile** | Stock ranks in the top 1% - 2.5% of market returns over 1M, 3M, 6M |
| **Consolidation Duration** | 5 <= Days Since High <= 40 (approximately 2 to 8 weeks) |
| **Base Depth (Retracement)** | (High pole - Low base) / High pole <= 0.25 |
| **Volatility Contraction (VCP)** | Current 5-day Average True Range (ATR) < 50% of 20-day ATR |
| **Volume Dry-Up** | Volume over last 3-5 days <= 70% of 20-day Simple Moving Average (SMA) Volume |

The programmatic identification of "tightness" requires analyzing sequential daily ranges. The system should calculate the daily high-minus-low range and ensure that over the final 3 to 5 days of the consolidation, this range is significantly smaller than the stock's Average Daily Range (ADR).17 Furthermore, the presence of "inside days"—where the daily high and low are completely contained within the previous day's high and low—on dead volume serves as the ultimate algorithmic confirmation of tightness before the breakout sequence triggers.7

### Episodic Pivots (EPs)

While High Tight Flags exploit existing momentum, Episodic Pivots (EPs) capitalize on the sudden, violent inception of a new trend driven by an unexpected fundamental catalyst. An EP occurs when a paradigm-shifting event—such as a massive earnings surprise, FDA approval, a significant contract acquisition, or a macro-level sector shift—forces market participants to instantly re-evaluate the asset's intrinsic value.2 This rapid repricing traps short sellers and forces under-allocated institutional funds to aggressively accumulate shares at market open, generating a liquidity vacuum to the upside.2

The programmatic identification of an EP relies on three primary vectors: the overnight price gap, the intraday volume surge, and the pre-existing base structure. The asset must gap up by a minimum of 10% (though the methodology permits high-quality setups to trigger at 7% to 9% under exceptional market conditions) from the previous day's close.10 This gap must violently disrupt a prolonged period of relative stagnation, commonly referred to as a multi-month consolidation base or a state of market neglect.10

Volume is the definitive validation mechanism for an EP. Without overwhelming volume, a price gap is highly susceptible to fading as early holders sell into the opening strength. The algorithm must verify that the asset is trading at a massive multiple of its standard liquidity. Specifically, the relative volume (RVol) must exceed 2.0 (200% of average daily volume), and ideally scale toward 3.0 to 5.0 for the highest probability setups.4 A critical intraday metric is that the asset's entire average daily volume should be transacted within the first 15 to 30 minutes of the trading session.4

To optimize the algorithm's capability to detect genuine EPs, it should incorporate the "MAGNA 53+ CAP 10x10" framework developed by Pradeep Bonde (Stockbee), which heavily influenced this methodology.2 This requires parsing fundamental API data alongside price action.

| **EP Parameter** | **Mathematical Condition / Programmatic Filter** |
| --- | --- |
| Price Gap | Open(today) >= Close(yesterday) * 1.10 |
| Liquidity Baseline | 50-day Average Daily Volume >= 300,000 to 500,000 shares |
| Intraday Volume Surge | Volume (first 15-30 mins) >= Average Daily Volume (20-day) |
| Relative Volume (RVol) | Volume(current) / SMA(Volume, 20) >= 2.0 |
| Prior Structure | 3-6 month preceding price action is relatively flat or range-bound |
| Fundamental Catalyst | Earnings beat, +39% sales growth (MAGNA rule), or sector news |

Furthermore, the algorithm must monitor the intraday price action to ensure the asset maintains its gap. The daily close must finish in the upper quartile of the intraday range, confirming sustained institutional demand rather than a retail-driven morning spike that subsequently collapses.1 EPs driven by verifiable earnings beats are categorized by the system as the highest quality signals.22

### Parabolic Shorts

The Parabolic Short is a contrarian, mean-reversion setup deployed strictly during periods of localized market euphoria. It targets highly volatile assets—frequently low-float, micro-cap, or small-cap stocks—that have completely decoupled from their underlying fundamentals and entered a terminal "blow-off top" phase.26 The market mechanics here involve a severe short squeeze compounded by retail "fear of missing out" (FOMO), driving the price vertically until the final marginal buyer is exhausted. Once incoming liquidity dries up, the price collapses violently under the weight of profit-taking and renewed, institutional short-selling.28

For the algorithmic system to safely engage in this inherently dangerous strategy, the setup criteria must be ruthlessly restrictive. The asset must exhibit undeniable vertical price acceleration: a gain of 50% to 100%+ within days for large-cap equities, or an explosive 300% to 1000%+ return for small-cap equities.27 This price verticality must occur over 3 to 5 consecutive positive trading sessions, leading to a massive spatial extension from the foundational moving averages.14

The quantitative trigger for exhaustion often correlates with a climactic volume signature. Intraday volume must go parabolic, reaching levels completely unseen during the prior days of the prevailing rally, indicating that a massive transfer of shares is occurring from smart money to late retail buyers.28 The algorithm must track moving average extension; as the stock goes vertical, the short-term and long-term moving averages will begin to splay apart rapidly.28

| **Parabolic Short Parameter** | **Mathematical Condition / Programmatic Filter** |
| --- | --- |
| Vertical Acceleration | Gain >= 50% – 100% (Large Cap) or >= 300% – 1000% (Small Cap) |
| Consecutive Advances | >= 3 to 5+ consecutive up days |
| Oscillator Extreme | RSI(14) >= 75 to 85 |
| Moving Average Extension | Price is severely extended above 10-day and 20-day EMAs; MAs are splaying |
| Volume Climax | Intraday volume goes parabolic, exceeding all prior days in the rally sequence |

## 2. The Screening Parameters (The "How")

The effectiveness of this quantitative system relies on ruthlessly filtering the broader market to isolate a highly concentrated universe of hyper-growth candidates. The algorithm must dynamically scan thousands of equities using exact volatility, trend, and comparative strength measurements to build a master stock list.31

### Average Daily Range (ADR) Percentage

The Average Daily Range (ADR) is the paramount volatility metric in this framework. It measures the average percentage distance between a stock's intraday high and low over a specific lookback period. The methodology mandates targeting stocks with a high ADR because an asset must inherently possess the capacity for wide intraday expansion to achieve the outsized swing-trading returns required to make the mathematics of the strategy viable.3 A low ADR indicates a sluggish, low-beta asset incapable of generating the requisite momentum for a rapid breakout.32

The algorithm must calculate the ADR over a 14-day or 20-day period. The absolute minimum threshold for inclusion in the screening universe is an ADR of 4.0%, though an ADR exceeding 5.0% or 6.0% is vastly preferred for optimal capital compounding, particularly for smaller trading accounts.10

*(Equation defining the standard 20-day ADR calculation utilized in the screener)*

Furthermore, the ADR acts as a vital exhaustion filter intraday. The algorithm utilizes an "ADR Checker" logic: if a stock has already moved an amount equal to or greater than its 20-day ADR percentage on the day of the breakout, the system must not execute a new entry.34 Buying an asset that has already consumed 100% of its average daily energy drastically increases the statistical probability of buying a localized top, exposing the system to immediate reversion.34

### Moving Averages (SMAs/EMAs)

Moving averages operate as dynamic support vectors and stringent trend regime filters. The system utilizes specific simple and exponential moving averages to confirm that the asset is in a valid, bullish alignment prior to authorizing a breakout execution. The algorithm must map the 10-day (EMA/SMA), 20-day (EMA/SMA), and 50-day SMA.14

For an HTF setup to be valid, the stock must be actively "surfing" the shorter-term averages. The price must be consolidating at, or slightly above, the 10-day or 20-day moving average, utilizing these levels as kinetic support.10 A critical algorithmic filter requires strict bullish stacking: the 10-day MA must be numerically greater than the 20-day MA, and both must possess a positive mathematical slope (trending upward).34

The system institutes a hard baseline rule: no long positions are permitted if the asset's price is trading below its 50-day Simple Moving Average.14 In the screening visualizer, this MA alignment is traditionally color-coded. The algorithm will flag a setup as pristine (Dark Green) only when the 10-day MA is greater than the 20-day MA, and both variables are trending upward compared to their values 5 days prior.34

### Relative Strength (RS) Calculation

Relative Strength (RS), in the context of this methodology, is not the standard Relative Strength Index (RSI) momentum oscillator; rather, it is a direct measurement of an asset's absolute momentum or its performance relative to a broader market index (typically the S&P 500 or NASDAQ). The objective is to ruthlessly filter out laggards and identify the apex market leaders.14

The programmatic screening process achieves this by calculating the percentage change of the asset's price over a 6-month (126 trading days) window. A common formulaic approach utilized in the methodology via platforms like TC2000 is tracking the current price relative to the 6-month low, expressed algorithmically as Current Close / 126-Day Minimum Low or .38 Another accepted variation compares the current price to the 6-month average, Current Close / 126-Day Average Close.39

The algorithm then ranks the entire market universe based on these output values, exclusively isolating stocks that reside in the top 1.0% to 2.5% percentile of performance.3 Additionally, the script can track a dedicated RS line relative to the SPY; a valid pre-breakout signal occurs when the RS line establishes a new 50-day high before the actual underlying price breaks out, confirming hidden institutional accumulation is underway.14

| **Screening Metric** | **Programmatic Filter / Algorithmic Code Logic** |
| --- | --- |
| Volatility (ADR Threshold) | ADR(20) >= 4.0% (ideal target >= 5.0%) |
| Trend Alignment (Stacking) | Price > 10MA > 20MA > 50SMA |
| Moving Average Trajectory | 10MA(current) > 10MA(past 5 days) (Positive slope) |
| Relative Strength Formula | RS_Score = Close(current) / Min(Low, 126) |
| Relative Strength Ranking | Asset must rank in the top 1% – 2.5% of RS_Score across all equities |

## 3. Execution & Risk Management (The "Trigger")

Identifying a mathematically pristine setup is entirely subordinate to the precision of the execution and the rigidity of the risk parameters. The algorithmic execution engine relies on intraday microstructure to validate the breakout in real-time, instantly aborting the trade if specific volume or price thresholds fail to materialize.

### Entry Mechanics

The system never anticipates a breakout; it strictly reacts to upward range expansion confirmed by institutional volume. The primary execution protocol is the Opening Range Breakout (ORB) or the High of Day (HOD) trigger.10

For High Tight Flags, the algorithm maps the high of the established consolidation range. Once the market opens, the system establishes an intraday opening range—typically utilizing the 1-minute, 5-minute, or 15-minute timeframe depending on the asset's innate volatility profile.40 A long order is executed the moment the price definitively breaches the high of this intraday range or the overarching high of the prior consolidation base.10 For Episodic Pivots, the entry often utilizes the Opening Price Guarantee (OPG) at the immediate market open for high-conviction catalysts, or it waits for the 5-minute to 10-minute ORB to confirm that the gap is holding.2

Crucially, this price breach is heavily gated by a Relative Volume (RVol) check. A price breakout occurring on stagnant volume is a statistical trap indicative of retail participation rather than institutional sponsorship. At the exact moment of the breakout, the intraday RVol must register greater than 2.0 (meaning the stock is trading at more than twice its normal volume for that specific time of day).15 Without this volume surge, the execution algorithm will bypass the signal entirely.

For Parabolic Shorts, the entry logic is inverted and delayed. Shorting the absolute top is statistically improbable. Instead, the algorithm waits for structural failure. It executes a short position when the asset breaks down below the intraday opening range lows (utilizing 1-minute or 5-minute candles) after an initial morning spike.27 Alternatively, the system waits for the asset to fail at the Volume Weighted Average Price (VWAP) line intraday. The trigger is the completion of the first definitive red 1-minute or 5-minute candle pushing down into, and failing to hold, the VWAP.27

### Risk Management and Hard Stops

Capital preservation is mathematically codified to ensure systematic longevity despite the methodology's inherently low win rate (which historically hovers between 30% and 40%, relying on massive outliers to generate positive expectancy). The methodology dictates that the maximum account risk must never exceed 1.0% to 2.0% per trade, with an optimal sizing algorithm risking only 0.25% to 0.50% of total equity per setup.10

The placement of the hard stop-loss is absolute, structural, and non-negotiable. For a standard HTF breakout, the algorithm places the stop just below the low of the breakout day itself, or alternatively, 1% to 3% below the absolute low of the localized consolidation base.10 For an Episodic Pivot, the stop is placed strictly at the low of the gap day or the low of the specific opening range candle used for entry.4 Moving or widening a stop-loss is algorithmically prohibited; if a stop is triggered, the system exits immediately, as "stops are sacred".4

The most critical algorithmic constraint regarding stop placement is the ADR rule: the percentage distance from the entry price to the hard stop-loss must never exceed the asset's Average Daily Range (1x ADR).10 If the technical structure requires a stop wider than the stock's typical daily movement, the algorithm must reject the trade, as the risk bandwidth is too broad and nullifies the mathematical edge.

Position sizing is dynamically and mathematically derived from this structural stop distance:

| **Execution & Risk Metric** | **Algorithmic Rule / Implementation** |
| --- | --- |
| Long Entry Trigger | Price(current) > Max(High ORB, High Consolidation) |
| Volume Confirmation | Intraday RVol(current) >= 2.0 at the exact moment of breakout |
| Short Entry Trigger | Price breaks below 5-min ORB Low OR fails at Intraday VWAP |
| Stop Loss Placement | Price(stop) = Low(Breakout Day) OR Low(Base) - 1% |
| Max ADR Risk Limit | (Entry - Stop) / Entry <= ADR(20) |
| Max Account Risk | 0.25% to 1.00% (max 2%) of total account equity per trade |

## 4. Trade Management & Selling Rules (The "Exit")

Exiting a trade is partitioned into two distinct procedural phases: securing baseline probability through initial partial profit-taking, and capturing outsized variance by algorithmically trailing the remaining position. This bifurcated approach smooths the overall equity curve, funds the inevitable string of small losses, and preserves structural exposure to multi-bagger momentum runs.

### Partial Profit Realization

Breakout momentum in modern equity markets typically occurs in immediate, violent bursts lasting a few days before the asset naturally exhausts its initial thrust and requires a secondary period of consolidation. To systematically capitalize on this behavior, the algorithm is programmed to sell a partial position—typically one-third (1/3) to one-half (1/2) of the total accumulated shares—directly into strength after 3 to 5 trading days.10 Alternatively, this partial exit sequence can be coded to trigger automatically when the trade achieves a calculated risk-to-reward multiple of 2R to 3R.10

Upon the execution of this initial profit-taking sequence, the algorithm must immediately amend the stop-loss order for the remaining shares, moving it up to the exact breakeven (entry) price.10 This mathematical adjustment effectively eliminates downside risk on the balance of the trade, creating a "free roll" scenario where the system can hold the asset without exposing principal capital to reversion.

### Trailing Stop Parameters

The residual position is held specifically to ride the prevailing long-term trend, governed entirely by a mechanical trailing stop tied to moving averages. Human discretion is removed; the algorithm utilizes the 10-day SMA/EMA or the 20-day SMA/EMA as the definitive trailing threshold.10

The exit trigger is not activated by a momentary, intraday dip below the moving average. The system requires a definitive daily close below the selected moving average to execute the final sell order.47 For assets exhibiting extreme velocity—where price has gone parabolic and is accelerating vertically away from the daily moving averages—the algorithm shifts to a faster intraday metric. In these high-velocity scenarios, the system triggers a full exit if an hourly candle closes below the 20-hour EMA.47 This dynamic, multi-timeframe adjustment protects against the devastating, instantaneous mean-reversions inherent to climax runs.

| **Exit Phase** | **Algorithmic Rule** |
| --- | --- |
| First Partial Exit (Time) | Sell 33% – 50% of position at T + 3 to T + 5 trading days |
| First Partial Exit (Price) | Sell 33% – 50% of position when Unrealized PnL >= 2R to 3R |
| Risk Adjustment | Following partial exit, adjust remaining Stop Loss = Entry Price (Breakeven) |
| Final Trailing Stop | Sell remaining position if Close(daily) < 10MA or 20MA |
| Parabolic Trailing Stop | Sell remaining position if Close(hourly) < 20EMA(hourly) |

## 5. Market Environment & Mindset

The most sophisticated execution algorithms will degrade capital rapidly if deployed during bearish or choppy market regimes. The Qullamaggie methodology places supreme importance on situational awareness, dictating that systems must aggressively limit exposure or transition entirely to cash when the broader market environment is uncooperative. The system requires strict, overarching programmatic regime filters to pause automated trading during hostile conditions.

### Hostile Market Determination

A hostile market is mathematically characterized by broken index trendlines, elevated broad-market volatility, and a high failure rate of individual stock breakouts. The algorithm establishes the market regime by continually analyzing the primary indices—specifically tracking the S&P 500 (SPY) and the NASDAQ (QQQ).

The primary binary filter is the 50-day Simple Moving Average. If the daily close price of the SPY or QQQ drops below their respective 50-day SMAs, the market regime is officially flagged by the algorithm as "Hostile".11 Furthermore, the algorithm assesses the short-term trajectory of the indices; if the 10-day EMA crosses below the 20-day EMA on the major indices, and both lines are sloping downward, the environment is classified as a confirmed downtrend.45 Under these conditions, the statistical probability of a stock breakout succeeding collapses drastically, as individual equities are heavily tethered to broad market beta.

### Rules for Halting Trading (Going to Cash)

In addition to index moving averages, the system must monitor internal market breadth to gauge absolute health. Integrating principles from the Stockbee Market Monitor, the algorithm tracks the ratio of advancing issues to declining issues, as well as the aggregate number of stocks making 5-day or 20-day highs versus lows.51 When the Net Highs/Lows indicator flips below 1.0 (indicating more new lows than new highs across the market breadth), it signals severe underlying market distribution.51

The final fail-safe mechanism relies on empirical feedback from the strategy's own execution log. If the algorithm detects that recently executed breakouts are consistently reversing, hitting stop-losses, or closing red, it confirms the absence of a momentum edge in the current environment.15 Specifically, a hard-coded kill switch is implemented: if the system encounters 2 to 3 consecutive stopped-out trades in a single session, the algorithm suspends all further long entries for the day.15

When index health is broken (price below 50 SMA), breadth is negative, and execution feedback is poor, the algorithmic protocol mandates overriding all individual stock setups, halting new long executions, and transitioning the portfolio to 100% cash.11 The system remains in cash until the indices reclaim their 10-day, 20-day, and 50-day moving averages and establish a distinct, verifiable uptrend.

| **Regime Filter** | **Algorithmic Rule (If True = Halt New Longs & Go to Cash)** |
| --- | --- |
| Index Trend | SPY Close < 50SMA OR QQQ Close < 50SMA (Halt New Longs) |
| Index Momentum | SPY/QQQ Weekly Price < 10SMA AND 10SMA < 20SMA (declining) |
| Market Breadth | Net 5-Day Highs / Lows Ratio < 1.0 (More lows than highs) |
| System Drawdown | Intraday Consecutive Stop-Losses >= 2 to 3 |

#### Works cited

- Episodic Pivot / Power Earnings Gap / Buyable Gap Up Explained - TradingSim, accessed February 20, 2026,
- Pradeep Bonde: 5 Swing Trading Strategies Using Episodic Pivots to Enter Explosive Stocks, accessed February 20, 2026,
- Find Stocks Like Qullamaggie: Kristjan Kullamägi Screens | Deepvue, accessed February 20, 2026,
- What is Episodic Pivot Trading? The Complete Guide to Catalyst-Based Momentum Trading, accessed February 20, 2026,
- High Tight Flag: 6 Signs To Identify Stocks About To Double | Deepvue, accessed February 20, 2026,
- High Tight Flag Pattern; How to Profit from this Explosive Breakout Setup? | ChartMill.com, accessed February 20, 2026,
- +222% Return in 27 Days - The High Tight Flag Trading Setup | Leif Soreide - YouTube, accessed February 20, 2026,
- 3 TIMELESS Setups That Have Made Me TENS OF MILLIONS! - Qullamaggie | PDF - Scribd, accessed February 20, 2026,
- What Is The High Tight Flag Chart Pattern? - TraderLion, accessed February 20, 2026,
- Free Qullamaggie Breakout Planner - Position Size & ADR Stop Calculator, accessed February 20, 2026,
- 3 momentum setups I'm watching - February 15, 2026 [Hostile Market so very cautious] : r/qullamaggie - Reddit, accessed February 20, 2026,
- Volatility Contraction Pattern (VCP): A Complete Guide - Defcofx, accessed February 20, 2026,
- Mastering the Volatility Contraction Pattern | TraderLion, accessed February 20, 2026,
- Qullamaggie Trading System Pro — vishnuv的指標 - TradingView, accessed February 20, 2026,
- Qullamaggie Trading Playbook | PDF - Scribd, accessed February 20, 2026,
- High Tight Flag Pattern | PDF - Scribd, accessed February 20, 2026,
- Qullamaggie High Tight Flag Table — Indicator by NNenov - TradingView, accessed February 20, 2026,
- Webinar-2-Slides | PDF | Stocks | Day Trading - Scribd, accessed February 20, 2026,
- QULLAMAGGIE Breakout Setups | Flags & Episodic Pivots EXPLAINED - YouTube, accessed February 20, 2026,
- How to Trade Episodic Pivots (EPs) - Reddit, accessed February 20, 2026,
- Episodic Pivot | PDF - Scribd, accessed February 20, 2026,
- Qullamaggie Trading System Pro — Indicator by vishnuv - TradingView, accessed February 20, 2026,
- Built a Qullamaggie-style scanner for swing traders: breakouts, EPs, RS, market monitor : r/swingtrading - Reddit, accessed February 20, 2026,
- Built a CANSLIM/Qullamaggie-style scanner: breakouts, EPs, RS, market monitor - Reddit, accessed February 20, 2026,
- Mastering the Qullamaggie Episodic Pivot Setup: A Flexible Stock Screening Approach, accessed February 20, 2026,
- Shorting Parabolic Stocks For Beginners - Warrior Trading, accessed February 20, 2026,
- 3 TIMELESS Setups That Have Made Me TENS of MILLIONS! - Qullamaggie | PDF - Scribd, accessed February 20, 2026,
- Climactic / Parabolic Reversal Setup - $FUBO Example : r/Daytrading - Reddit, accessed February 20, 2026,
- The Truth About Parabolic Moves: When to Buy, When to Short - YouTube, accessed February 20, 2026,
- 3 TIMELESS Setups That Have Made Me TENS of MILLIONS! - Qullamaggie | PDF - Scribd, accessed February 20, 2026,
- Deep Dive into Kristjan Kullamägi's Swing Trading Strategies: An In-Depth Guide - Medium, accessed February 20, 2026,
- Swing Dream - PAINT BARS | MA | EMA | DMA | VWAP | TABLE | ADR % — Indicator by TechFille006 — TradingView, accessed February 20, 2026,
- The Qullamaggie's Laws of Swing | PDF | Market (Economics) | Investing - Scribd, accessed February 20, 2026,
- Qullamaggie — Indicators and Strategies — TradingView — India, accessed February 20, 2026,
- Qullamaggie Setups Analysis | PDF | Moving Average - Scribd, accessed February 20, 2026,
- Qullamaggie Moving Averages - Deepvue, accessed February 20, 2026,
- Relative Strength | Indicators & Company Fundamentals - TC2000 Help Site, accessed February 20, 2026,
- Volume and top performers for my QM-style scan? : r/qullamaggie - Reddit, accessed February 20, 2026,
- Question about scan formula on TC2000 : r/qullamaggie - Reddit, accessed February 20, 2026,
- Opening Range Breakout (ORB) Trading Strategy: How it Works - LuxAlgo, accessed February 20, 2026,
- Opening Range Breakout (ORB) Trading Strategy Explained: How to Identify and Trade It, accessed February 20, 2026,
- Who is trading a ORB (Open Range Breakout) or PMRB (Pre-Market Range Breakout) strategy and what are the results? : r/Daytrading - Reddit, accessed February 20, 2026,
- How I Use Relative Volume (RVOL) to Find Intraday Movers! - TradingView, accessed February 20, 2026,
- Relative Volume (RVOL) - ChartSchool - StockCharts.com, accessed February 20, 2026,
- When do you go into a ALL cash position? : r/qullamaggie - Reddit, accessed February 20, 2026,
- Qullamaggie's Laws of Swing | PDF | Order (Exchange) | Day Trading, accessed February 20, 2026,
- Qullamaggie Examples | PDF - Scribd, accessed February 20, 2026,
- r/qullamaggie - Reddit, accessed February 20, 2026,
- r/qullamaggie - Reddit, accessed February 20, 2026,
- 99% of Indicators Are BS : r/qullamaggie - Reddit, accessed February 20, 2026,
- How can I be in sync with the market? : r/qullamaggie - Reddit, accessed February 20, 2026,
- Market Monitor on steroids : r/qullamaggie - Reddit, accessed February 20, 2026,
- Identifying Market Trends : r/qullamaggie - Reddit, accessed February 20, 2026,
