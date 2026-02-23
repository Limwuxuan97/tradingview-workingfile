"""
TECHNICAL INDICATORS — Complete library
=======================================
All indicators needed for:
  - Qullamaggie scanning (ADR, RS, VCP, volume analysis)
  - Kitchin cycle overlay
  - Macro/liquidity scoring
  - Regime detection
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict
from datetime import date, datetime
import math


# ============================================================================
# MOVING AVERAGES
# ============================================================================

def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period, min_periods=period).mean()

def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


# ============================================================================
# ADR — Average Daily Range (Qullamaggie volatility filter)
# ============================================================================

def adr_pct(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Average Daily Range as percentage of close. ADR(20) >= 4% is the filter."""
    daily_range_pct = (df["high"] - df["low"]) / df["close"] * 100.0
    return daily_range_pct.rolling(window=period, min_periods=period).mean()


# ============================================================================
# ATR — Average True Range
# ============================================================================

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range."""
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=period).mean()


# ============================================================================
# RSI — Relative Strength Index
# ============================================================================

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100.0 - (100.0 / (1.0 + rs))


# ============================================================================
# MACD
# ============================================================================

def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
         ) -> Tuple[pd.Series, pd.Series, pd.Series]:
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


# ============================================================================
# BOLLINGER BANDS
# ============================================================================

def bollinger_bands(series: pd.Series, period: int = 20, mult: float = 2.0
                    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
    middle = sma(series, period)
    std = series.rolling(window=period, min_periods=period).std()
    upper = middle + mult * std
    lower = middle - mult * std
    return upper, middle, lower

def bollinger_pct_b(series: pd.Series, period: int = 20, mult: float = 2.0) -> pd.Series:
    upper, middle, lower = bollinger_bands(series, period, mult)
    return (series - lower) / (upper - lower)

def bollinger_width(series: pd.Series, period: int = 20, mult: float = 2.0) -> pd.Series:
    upper, middle, lower = bollinger_bands(series, period, mult)
    return (upper - lower) / middle * 100.0

def bollinger_squeeze(series: pd.Series, period: int = 20, mult: float = 2.0) -> pd.Series:
    """True when BB width < 75% of its own SMA — coiling pattern."""
    width = bollinger_width(series, period, mult)
    width_sma = sma(width, period)
    return width < width_sma * 0.75


# ============================================================================
# RELATIVE STRENGTH (Mansfield-style)
# ============================================================================

def relative_strength(stock: pd.Series, benchmark: pd.Series, period: int = 63) -> pd.Series:
    """Mansfield RS: stock performance vs benchmark over lookback period."""
    stock_ret = stock.pct_change(period)
    bench_ret = benchmark.pct_change(period)
    return stock_ret - bench_ret

def rs_rank(returns_dict: dict, period: int = 63) -> pd.DataFrame:
    """Rank all stocks by RS. Returns DataFrame with rank percentile (0-100)."""
    rs_scores = {}
    for ticker, series in returns_dict.items():
        if len(series) > period:
            rs_scores[ticker] = series.pct_change(period).iloc[-1]

    if not rs_scores:
        return pd.DataFrame()

    rs_df = pd.Series(rs_scores).to_frame("rs_score")
    rs_df["rs_rank"] = rs_df["rs_score"].rank(pct=True) * 100.0
    return rs_df.sort_values("rs_rank", ascending=False)


# ============================================================================
# VOLUME ANALYSIS
# ============================================================================

def relative_volume(volume: pd.Series, period: int = 50) -> pd.Series:
    """Relative volume: current volume / SMA(volume, period)."""
    vol_sma = sma(volume, period)
    return volume / vol_sma.replace(0, np.nan)

def volume_contraction(volume: pd.Series, period: int = 20) -> pd.Series:
    """Measures volume drying up. Lower = more contraction (bullish for breakout)."""
    recent = volume.rolling(5).mean()
    avg = sma(volume, period)
    return recent / avg.replace(0, np.nan)

def volume_dry_up(volume: pd.Series, period: int = 20, threshold: float = 0.70) -> pd.Series:
    """True when last 5-day avg volume <= 70% of 20-day SMA."""
    return volume_contraction(volume, period) <= threshold


# ============================================================================
# VCP — Volatility Contraction Pattern
# ============================================================================

def vcp_score(df: pd.DataFrame) -> pd.Series:
    """
    VCP detection: 5d ATR contracting below 50% of 20d ATR.
    Returns 0-100 score (higher = tighter contraction).
    """
    atr5 = atr(df, 5)
    atr20 = atr(df, 20)
    ratio = atr5 / atr20.replace(0, np.nan)
    # Normalize: ratio < 0.50 = good VCP (score 80+), ratio > 1.0 = no VCP (score 0)
    score = np.clip((1.0 - ratio) * 100.0, 0, 100)
    return score


# ============================================================================
# TREND ANALYSIS
# ============================================================================

def ma_alignment(df: pd.DataFrame, periods: list = [10, 20, 50]) -> pd.Series:
    """
    Returns True when MAs are properly stacked:
    Price > shortest MA > medium MA > longest MA, all rising.
    """
    mas = {p: sma(df["close"], p) for p in sorted(periods)}
    sorted_periods = sorted(periods)

    # Check stacking: price > MA(10) > MA(20) > MA(50)
    stacked = df["close"] > mas[sorted_periods[0]]
    for i in range(len(sorted_periods) - 1):
        stacked = stacked & (mas[sorted_periods[i]] > mas[sorted_periods[i + 1]])

    # Check all rising (slope positive over last 5 days)
    rising = pd.Series(True, index=df.index)
    for p in sorted_periods:
        slope = mas[p] - mas[p].shift(5)
        rising = rising & (slope > 0)

    return stacked & rising

def above_long_ma(df: pd.DataFrame, period: int = 200) -> pd.Series:
    """Price above long-term MA (200 SMA)."""
    return df["close"] > sma(df["close"], period)


# ============================================================================
# PRIOR TREND DETECTION (for HTF)
# ============================================================================

def prior_run_pct(df: pd.DataFrame, lookback_weeks: int = 8) -> pd.Series:
    """
    Calculate the percentage gain from the lowest low to the highest high
    in the lookback window. For HTF: need +30-100% in 4-8 weeks.
    """
    lookback_days = lookback_weeks * 5
    rolling_low = df["low"].rolling(window=lookback_days, min_periods=20).min()
    rolling_high = df["high"].rolling(window=lookback_days, min_periods=20).max()
    return (rolling_high - rolling_low) / rolling_low.replace(0, np.nan) * 100.0


# ============================================================================
# CONSOLIDATION DETECTION
# ============================================================================

def consolidation_depth(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Measures retracement from recent high.
    For HTF: max 25% retracement during consolidation.
    """
    rolling_high = df["high"].rolling(window=period * 3, min_periods=period).max()
    return (rolling_high - df["close"]) / rolling_high.replace(0, np.nan) * 100.0


# ============================================================================
# GAP DETECTION (for EPs)
# ============================================================================

def gap_pct(df: pd.DataFrame) -> pd.Series:
    """Gap percentage: (today's open - yesterday's close) / yesterday's close."""
    return (df["open"] - df["close"].shift(1)) / df["close"].shift(1).replace(0, np.nan) * 100.0


# ============================================================================
# KITCHIN CYCLE CALCULATIONS
# ============================================================================

def kitchin_cycle_position(as_of_date: date, anchor_date: date,
                           period_months: float = 41.0) -> float:
    """
    Get current position within the Kitchin cycle.
    Returns 0.0 (trough) to 1.0 (next trough).
    """
    days_since = (as_of_date - anchor_date).days
    cycle_days = period_months * 30.44
    position = (days_since % cycle_days) / cycle_days
    return position

def kitchin_sine_wave(dates: pd.DatetimeIndex, anchor_date: date,
                      period_months: float = 41.0) -> pd.Series:
    """
    Generate Kitchin cycle sine wave for a date range.
    Returns normalized 0-100 (0 = trough, 100 = peak).
    """
    cycle_days = period_months * 30.44
    values = []
    for d in dates:
        as_of = d.date() if hasattr(d, 'date') else d
        days_since = (as_of - anchor_date).days
        phase = (days_since % cycle_days) / cycle_days * 2 * math.pi
        sine = math.sin(phase - math.pi / 2)  # -1 at trough, +1 at peak
        norm = (sine + 1) / 2 * 100  # 0-100
        values.append(norm)
    return pd.Series(values, index=dates)


# ============================================================================
# REGIME DETECTION (Market Health)
# ============================================================================

def market_regime(spy_df: pd.DataFrame) -> pd.Series:
    """
    Market regime filter (Qullamaggie rules):
    +2 = Strong bull (SPY > 50SMA, 10EMA > 20EMA, breadth strong)
    +1 = Bull (SPY > 50SMA)
     0 = Neutral
    -1 = Bear (SPY < 50SMA)
    -2 = Strong bear (all bearish)
    """
    spy_50sma = sma(spy_df["close"], 50)
    spy_10ema = ema(spy_df["close"], 10)
    spy_20ema = ema(spy_df["close"], 20)

    above_50 = spy_df["close"] > spy_50sma
    ema_bull = spy_10ema > spy_20ema

    regime = pd.Series(0, index=spy_df.index)
    regime[above_50 & ema_bull] = 2
    regime[above_50 & ~ema_bull] = 1
    regime[~above_50 & ema_bull] = 0
    regime[~above_50 & ~ema_bull] = -1

    # Smooth: require 3 consecutive days to confirm regime change
    regime = regime.rolling(3).median().ffill()
    return regime


# ============================================================================
# COMPOSITE TECHNICAL SCORE (0-100)
# ============================================================================

def composite_technical_score(df: pd.DataFrame) -> pd.Series:
    """
    Weighted composite of technicals (from Pine Script logic).
    EMA alignment: 30%, RSI: 25%, MACD: 25%, Bollinger: 20%
    """
    close = df["close"]

    # EMA component
    ema21 = ema(close, 21)
    ema55 = ema(close, 55)
    ema200 = ema(close, 200)
    ema_bull = (ema21 > ema55).astype(float) * 30.0
    trend_up = (close > ema200).astype(float) * 30.0
    ema_score = np.clip(ema_bull + trend_up + 20.0, 0, 100)

    # RSI component (contrarian: oversold = high score)
    rsi_val = rsi(close, 14)
    rsi_score = pd.Series(50.0, index=df.index)
    rsi_score[rsi_val < 30] = 70.0 + (30.0 - rsi_val[rsi_val < 30]) * 2.0
    rsi_score[rsi_val > 70] = 30.0 - (rsi_val[rsi_val > 70] - 70.0) * 2.0
    rsi_score = np.clip(rsi_score, 0, 100)

    # MACD component
    macd_line, signal_line, hist = macd(close)
    macd_bull = (macd_line > signal_line).astype(float)
    hist_rising = (hist > hist.shift(1)).astype(float)
    macd_score = macd_bull * 65.0 + hist_rising * 15.0 + (1 - macd_bull) * 20.0
    macd_score = np.clip(macd_score, 0, 100)

    # Bollinger component
    pct_b = bollinger_pct_b(close)
    bb_score = 50.0 - (pct_b - 0.5) * 70.0  # Near lower band = high score
    bb_score = np.clip(bb_score, 0, 100)

    composite = ema_score * 0.30 + rsi_score * 0.25 + macd_score * 0.25 + bb_score * 0.20
    return np.clip(composite, 0, 100)


# ============================================================================
# CME T+35 / T+42 FORCED SELLING WINDOW
# ============================================================================

def cme_quarterly_expiry(year: int, month: int) -> date:
    """Find the 3rd Friday of a given month (CME quarterly expiry)."""
    from datetime import timedelta
    first_day = date(year, month, 1)
    weekday = first_day.weekday()  # 0=Monday, 4=Friday
    first_friday = first_day + timedelta(days=(4 - weekday) % 7)
    third_friday = first_friday + timedelta(days=14)
    return third_friday


def is_cme_t35_window(as_of_date, buffer_start: int = 33, buffer_end: int = 44) -> bool:
    """
    Check if current date falls in the T+35 forced selling window.
    After each CME quarterly expiry (3rd Friday of Mar/Jun/Sep/Dec),
    there's forced delivery pressure at T+35 and T+42 days.
    Avoid entering new positions during this window.
    """
    from datetime import timedelta
    d = as_of_date.date() if hasattr(as_of_date, 'date') else as_of_date

    for year in range(d.year - 1, d.year + 1):
        for month in [3, 6, 9, 12]:
            try:
                expiry = cme_quarterly_expiry(year, month)
                window_start = expiry + timedelta(days=buffer_start)
                window_end = expiry + timedelta(days=buffer_end)
                if window_start <= d <= window_end:
                    return True
            except ValueError:
                continue
    return False


def cme_t35_score_adjustment(as_of_date) -> float:
    """
    Returns a multiplier for scan scores based on CME timing.
    1.0 = normal, 0.5 = T+35 window (reduce conviction), 1.2 = post-flush (buy opportunity)
    """
    from datetime import timedelta
    d = as_of_date.date() if hasattr(as_of_date, 'date') else as_of_date

    for year in range(d.year - 1, d.year + 1):
        for month in [3, 6, 9, 12]:
            try:
                expiry = cme_quarterly_expiry(year, month)
                days_since = (d - expiry).days
                # T+33 to T+44: forced selling window — reduce conviction
                if 33 <= days_since <= 44:
                    return 0.5
                # T+45 to T+55: post-flush recovery — good buying opportunity
                if 45 <= days_since <= 55:
                    return 1.2
            except ValueError:
                continue
    return 1.0


# ============================================================================
# MONTHLY OPEX T+1 / T+2 SETTLEMENT WINDOW (The Post-OpEx Pump)
# ============================================================================

def monthly_opex_expiry(year: int, month: int) -> date:
    """Find the 3rd Friday of a given month (Standard Options Expiration - OpEx)."""
    from datetime import timedelta
    first_day = date(year, month, 1)
    weekday = first_day.weekday()  # 0=Monday, 4=Friday
    first_friday = first_day + timedelta(days=(4 - weekday) % 7)
    third_friday = first_friday + timedelta(days=14)
    return third_friday

def is_opex_settlement_window(as_of_date) -> bool:
    """
    Check if the current date is the Monday or Tuesday following a monthly OpEx.
    With T+1 settlement for options exercise delivery, Market Makers are forced
    to buy/deliver shares on T+1 (Monday) and T+2 (Tuesday), causing artificial pumps.
    Returns True if the date is on T+1 or T+2.
    """
    from datetime import timedelta
    d = as_of_date.date() if hasattr(as_of_date, 'date') else as_of_date
    
    try:
        expiry = monthly_opex_expiry(d.year, d.month)
        t1_monday = expiry + timedelta(days=3)
        t2_tuesday = expiry + timedelta(days=4)
        
        return d == t1_monday or d == t2_tuesday
    except ValueError:
        return False

# ============================================================================
# SECTOR RELATIVE STRENGTH
# ============================================================================

# Map tickers to sector ETFs
TICKER_SECTOR_MAP = {
    # Technology / Software / Cloud
    "AAPL": "XLK", "MSFT": "XLK", "NVDA": "XLK", "AVGO": "XLK",
    "CRM": "XLK", "ADBE": "XLK", "NOW": "XLK", "PANW": "XLK",
    "CRWD": "XLK", "SNOW": "XLK", "PLTR": "XLK", "DDOG": "XLK",
    "NET": "XLK", "ORCL": "XLK", "HUBS": "XLK", "VEEV": "XLK",
    "WDAY": "XLK", "BILL": "XLK", "MDB": "XLK", "TEAM": "XLK",
    "CFLT": "XLK", "ESTC": "XLK", "SHOP": "XLK", "ZS": "XLK", "FTNT": "XLK",
    # Semiconductors
    "AMD": "XLK", "INTC": "XLK", "QCOM": "XLK", "MU": "XLK",
    "MRVL": "XLK", "AMAT": "XLK", "LRCX": "XLK", "KLAC": "XLK",
    "SMCI": "XLK", "ARM": "XLK", "ON": "XLK", "MPWR": "XLK",
    "SWKS": "XLK", "TXN": "XLK",
    # Communication / Media
    "GOOGL": "XLC", "META": "XLC", "NFLX": "XLC", "DIS": "XLC",
    "CMCSA": "XLC", "TMUS": "XLC", "SE": "XLC", "SPOT": "XLC",
    "RBLX": "XLC", "TTD": "XLC",
    # Consumer Discretionary
    "AMZN": "XLY", "TSLA": "XLY", "HD": "XLY", "NKE": "XLY",
    "SBUX": "XLY", "MCD": "XLY", "COST": "XLY", "ABNB": "XLY",
    "DASH": "XLY", "CMG": "XLY", "LULU": "XLY", "DECK": "XLY",
    "ROST": "XLY", "TJX": "XLY", "ORLY": "XLY", "AZO": "XLY",
    "MELI": "XLY",
    # Financials
    "JPM": "XLF", "BAC": "XLF", "GS": "XLF", "MS": "XLF",
    "V": "XLF", "MA": "XLF", "AXP": "XLF", "BLK": "XLF",
    "SCHW": "XLF", "CME": "XLF", "ICE": "XLF", "MSCI": "XLF",
    "SPGI": "XLF", "SQ": "XLF", "COIN": "XLF",
    # Healthcare / Biotech
    "UNH": "XLV", "LLY": "XLV", "JNJ": "XLV", "PFE": "XLV",
    "ABBV": "XLV", "MRK": "XLV", "TMO": "XLV", "ISRG": "XLV",
    "DXCM": "XLV", "PODD": "XLV", "VRTX": "XLV", "REGN": "XLV",
    "GILD": "XLV", "AMGN": "XLV", "BSX": "XLV", "EW": "XLV",
    "MRNA": "XLV", "BIIB": "XLV",
    # Industrials
    "CAT": "XLI", "DE": "XLI", "GE": "XLI", "HON": "XLI",
    "RTX": "XLI", "LMT": "XLI", "BA": "XLI", "UNP": "XLI", "URI": "XLI",
    "GWW": "XLI", "FTV": "XLI", "WM": "XLI", "RSG": "XLI",
    "ODFL": "XLI", "TT": "XLI", "EMR": "XLI", "ROK": "XLI",
    # Energy
    "XOM": "XLE", "CVX": "XLE", "COP": "XLE", "SLB": "XLE",
    "EOG": "XLE", "MPC": "XLE", "OXY": "XLE", "DVN": "XLE",
    "FANG": "XLE", "HAL": "XLE", "PSX": "XLE",
    # Consumer Staples
    "WMT": "XLP", "PG": "XLP", "KO": "XLP", "PEP": "XLP",
    "PM": "XLP", "MO": "XLP", "CL": "XLP", "EL": "XLP",
    # REITs
    "AMT": "XLRE", "EQIX": "XLRE", "PLD": "XLRE", "DLR": "XLRE",
    # Utilities
    "NEE": "XLU", "SO": "XLU", "DUK": "XLU", "AEP": "XLU",
    # Materials
    "FCX": "XLB", "NEM": "XLB", "APD": "XLB", "LIN": "XLB", "SHW": "XLB",
    # China ADRs
    "BABA": "KWEB", "JD": "KWEB", "PDD": "KWEB", "BIDU": "KWEB",
    "NIO": "KWEB", "XPEV": "KWEB", "LI": "KWEB", "BEKE": "KWEB",
    "TME": "KWEB", "BILI": "KWEB", "ZTO": "KWEB", "VNET": "KWEB",
    "FUTU": "KWEB", "MNSO": "KWEB",
}


def sector_strength(sector_etf_data: Dict[str, pd.DataFrame], spy_close: pd.Series,
                     lookback: int = 63) -> Dict[str, float]:
    """
    Calculate relative strength of each sector ETF vs SPY.
    Returns dict: sector_etf -> RS score (-1 to +1).
    Positive = outperforming SPY, negative = underperforming.
    """
    sector_rs = {}
    for etf, df in sector_etf_data.items():
        if df.empty or len(df) < lookback:
            continue
        close = df["close"]
        if len(close) >= lookback and len(spy_close) >= lookback:
            stock_ret = (close.iloc[-1] / close.iloc[-lookback] - 1)
            bench_ret = (spy_close.iloc[-1] / spy_close.iloc[-lookback] - 1)
            sector_rs[etf] = stock_ret - bench_ret
    return sector_rs


def get_sector_score_bonus(ticker: str, sector_rs: Dict[str, float],
                           cycle_phase: str = "") -> float:
    """
    Returns score multiplier based on sector strength + Newton's cycle rotation.

    Newton's insight: In late expansion/peak phases, Tech (XLK) underperforms
    while Industrials (XLI), Energy (XLE), Financials (XLF) outperform.
    The "Magnificent 7 drag" hits hardest in late summer/fall of cycle peaks.
    """
    sector_etf = TICKER_SECTOR_MAP.get(ticker, None)
    if sector_etf is None or sector_etf not in sector_rs:
        # Still apply cycle rotation even without RS data
        if cycle_phase and sector_etf:
            return _newton_cycle_sector_mult(sector_etf, cycle_phase)
        return 1.0

    # LIGHT RS multiplier (±10% max — don't crush good individual setups)
    rs = sector_rs[sector_etf]
    if rs > 0.05:
        rs_mult = 1.10
    elif rs > 0.0:
        rs_mult = 1.05
    elif rs > -0.05:
        rs_mult = 0.95
    else:
        rs_mult = 0.90

    # Newton's cycle-phase sector rotation overlay
    cycle_mult = _newton_cycle_sector_mult(sector_etf, cycle_phase) if cycle_phase else 1.0

    return rs_mult * cycle_mult


def _newton_cycle_sector_mult(sector_etf: str, cycle_phase: str) -> float:
    """
    Mark Newton's sector rotation by cycle phase.
    Late expansion/peak: Overweight XLI, XLE, XLF. Underweight XLK.
    Trough/early expansion: Overweight XLK, XLC (growth leads recovery).
    """
    # Sectors that lead in late cycle (defensive/value rotation)
    late_cycle_leaders = {"XLI", "XLE", "XLF", "XLV"}
    # Sectors that lead in early cycle (growth/risk-on)
    early_cycle_leaders = {"XLK", "XLC", "XLY", "KWEB"}

    if cycle_phase in ("LATE_EXPANSION_PEAK", "EARLY_CONTRACTION"):
        # Newton: mild preference for value over growth (±5%)
        if sector_etf in late_cycle_leaders:
            return 1.05
        elif sector_etf in early_cycle_leaders:
            return 0.95
        return 1.0
    elif cycle_phase in ("TROUGH_ACCUMULATE", "EARLY_EXPANSION"):
        # Growth leads out of troughs (±5%)
        if sector_etf in early_cycle_leaders:
            return 1.05
        elif sector_etf in late_cycle_leaders:
            return 0.95
        return 1.0
    else:
        return 1.0  # Neutral phases
