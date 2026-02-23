"""
MACRO ENGINE — Forward-looking regime detection & Kitchin cycle forecasting
===========================================================================
The market is FORWARD-LOOKING. This engine detects regime shifts BEFORE they
fully play out, using leading indicators from Yahoo Finance (all free).

Five forward-looking signals:
  1. Yield Curve Slope (^TNX - ^IRX) — recession predictor 12-18 months ahead
  2. Rate Direction (^IRX trend) — Fed policy direction, leads 6-9 months
  3. Copper/Gold Ratio (HG=F / GC=F) — growth expectations
  4. Dollar Regime (DXY) — liquidity proxy, EM/commodity impact
  5. VIX Regime (^VIX) — sentiment and fear/greed

Plus: Kitchin cycle forecasting with separate US and China cycles.
China leads US by 12-18 months — when US peaks, China is sloping up.

ALL outputs map to position SIZING only, never signal filtering.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import date, datetime

from algo.config import KITCHIN


# ============================================================================
# MACRO TICKERS (all free from Yahoo Finance)
# ============================================================================

MACRO_TICKERS = {
    "tnx": "^TNX",       # 10-Year Treasury yield
    "irx": "^IRX",       # 13-week T-bill (Fed funds proxy)
    "fvx": "^FVX",       # 5-Year Treasury yield
    "dxy": "DX-Y.NYB",   # US Dollar Index
    "vix": "^VIX",       # Volatility Index
    "gold": "GC=F",      # Gold futures
    "copper": "HG=F",    # Copper futures
    "tlt": "TLT",        # 20+ Year Treasury ETF
}


def fetch_macro_data(start: str, end: str) -> Dict[str, pd.DataFrame]:
    """
    Fetch all macro indicator data from Yahoo Finance.
    Returns dict of {name: DataFrame with 'close' column}.
    """
    from algo.data_provider import YFinanceProvider

    provider = YFinanceProvider()
    tickers = list(MACRO_TICKERS.values())
    data = provider.get_bulk_ohlcv(tickers, start, end)

    # Map back to friendly names
    result = {}
    for name, ticker in MACRO_TICKERS.items():
        if ticker in data and not data[ticker].empty:
            result[name] = data[ticker]

    print(f"  Loaded {len(result)}/{len(MACRO_TICKERS)} macro indicators")
    return result


# ============================================================================
# FORWARD-LOOKING SIGNALS (each returns -1, 0, or +1)
# ============================================================================

def yield_curve_signal(macro_data: Dict[str, pd.DataFrame], as_of_date) -> int:
    """
    Yield curve slope: ^TNX (10Y) - ^IRX (3M T-bill).
    > 0 and rising: Economy expanding -> BULLISH (+1)
    < 0 (inverted): Recession 12-18 months ahead -> BEARISH (-1)
    Un-inverting after inversion: Recession imminent -> VERY BEARISH (-1)
    """
    if "tnx" not in macro_data or "irx" not in macro_data:
        return 0

    tnx = macro_data["tnx"]["close"]
    irx = macro_data["irx"]["close"]

    # Align dates
    mask_tnx = tnx.index <= as_of_date
    mask_irx = irx.index <= as_of_date
    if not mask_tnx.any() or not mask_irx.any():
        return 0

    tnx_val = tnx[mask_tnx].iloc[-1]
    irx_val = irx[mask_irx].iloc[-1]
    spread = tnx_val - irx_val

    # Check if was inverted recently (last 6 months)
    lookback = 126  # ~6 months
    if mask_tnx.sum() > lookback and mask_irx.sum() > lookback:
        recent_tnx = tnx[mask_tnx].iloc[-lookback:]
        recent_irx = irx[mask_irx].iloc[-lookback:]
        # Simple check: was spread < 0 at any point in last 6 months?
        min_idx = min(len(recent_tnx), len(recent_irx))
        if min_idx > 0:
            recent_spreads = recent_tnx.values[-min_idx:] - recent_irx.values[-min_idx:]
            was_inverted = np.any(recent_spreads < 0)
            if was_inverted and spread > 0:
                # Un-inverting — recession typically imminent
                return -1

    if spread < -0.5:
        return -1  # Deeply inverted
    elif spread < 0:
        return -1  # Inverted
    elif spread > 1.0:
        return 1   # Healthy positive slope
    else:
        return 0   # Neutral/flat


def rate_direction_signal(macro_data: Dict[str, pd.DataFrame], as_of_date) -> int:
    """
    Fed rate direction proxy: ^IRX (13-week T-bill) trend.
    ^IRX falling (below 50 SMA): Fed easing or expected to ease -> BULLISH (+1)
    ^IRX rising (above 50 SMA): Fed tightening -> BEARISH (-1)
    Detects: 2022 hiking cycle, 2024 easing cycle automatically.
    """
    if "irx" not in macro_data:
        return 0

    irx = macro_data["irx"]["close"]
    mask = irx.index <= as_of_date
    if mask.sum() < 50:
        return 0

    irx_recent = irx[mask]
    current = irx_recent.iloc[-1]
    sma50 = irx_recent.iloc[-50:].mean()

    # Also check direction (compare to 3 months ago)
    if len(irx_recent) >= 63:
        three_months_ago = irx_recent.iloc[-63]
        if current < sma50 and current < three_months_ago:
            return 1   # Falling below SMA — easing
        elif current > sma50 and current > three_months_ago:
            return -1  # Rising above SMA — tightening

    if current < sma50 * 0.95:
        return 1
    elif current > sma50 * 1.05:
        return -1

    return 0


def copper_gold_signal(macro_data: Dict[str, pd.DataFrame], as_of_date) -> int:
    """
    Copper/Gold ratio — one of the best forward-looking growth indicators.
    Rising: Growth expectations improving -> BULLISH (+1)
    Falling: Growth fears, recession risk -> BEARISH (-1)
    """
    if "copper" not in macro_data or "gold" not in macro_data:
        return 0

    copper = macro_data["copper"]["close"]
    gold = macro_data["gold"]["close"]

    mask_cu = copper.index <= as_of_date
    mask_au = gold.index <= as_of_date
    if mask_cu.sum() < 63 or mask_au.sum() < 63:
        return 0

    cu_recent = copper[mask_cu]
    au_recent = gold[mask_au]

    # Compute ratio at current and 3 months ago
    cu_now = cu_recent.iloc[-1]
    au_now = au_recent.iloc[-1]
    ratio_now = cu_now / au_now if au_now > 0 else 0

    cu_3m = cu_recent.iloc[-63]
    au_3m = au_recent.iloc[-63]
    ratio_3m = cu_3m / au_3m if au_3m > 0 else 0

    if ratio_3m > 0:
        change_pct = (ratio_now / ratio_3m - 1) * 100
        if change_pct > 5:
            return 1   # Rising — growth expectations up
        elif change_pct < -5:
            return -1  # Falling — growth fears
    return 0


def dollar_signal(macro_data: Dict[str, pd.DataFrame], as_of_date) -> int:
    """
    US Dollar Index (DXY) regime.
    DXY < 50 SMA and falling: Weak dollar = liquidity expanding -> BULLISH (+1)
    DXY > 50 SMA and rising: Strong dollar = headwind -> BEARISH (-1)
    Critical for EM/China ADRs.
    """
    if "dxy" not in macro_data:
        return 0

    dxy = macro_data["dxy"]["close"]
    mask = dxy.index <= as_of_date
    if mask.sum() < 50:
        return 0

    dxy_recent = dxy[mask]
    current = dxy_recent.iloc[-1]
    sma50 = dxy_recent.iloc[-50:].mean()

    if current < sma50 * 0.98:
        return 1   # Weak dollar — bullish
    elif current > sma50 * 1.02:
        return -1  # Strong dollar — bearish
    return 0


def vix_signal(macro_data: Dict[str, pd.DataFrame], as_of_date) -> int:
    """
    VIX regime and mean reversion.
    VIX < 20 and falling: Risk-on -> NEUTRAL/BULLISH (+0 or +1)
    VIX 20-30: Elevated fear -> NEUTRAL (0)
    VIX > 30: Panic -> BEARISH (-1)
    VIX spike then mean revert (fell 30%+ from recent peak): Bottom signal (+1)
    """
    if "vix" not in macro_data:
        return 0

    vix = macro_data["vix"]["close"]
    mask = vix.index <= as_of_date
    if mask.sum() < 20:
        return 0

    vix_recent = vix[mask]
    current = vix_recent.iloc[-1]

    # Check for mean reversion (spike then drop)
    if len(vix_recent) >= 20:
        recent_peak = vix_recent.iloc[-20:].max()
        if recent_peak > 30 and current < recent_peak * 0.7:
            return 1  # VIX spiked and is reverting — classic bottom signal

    if current > 35:
        return -1  # Panic
    elif current > 25:
        return 0   # Elevated but not panic
    elif current < 15:
        return 1   # Low vol, risk-on
    return 0


# ============================================================================
# COMPOSITE MACRO REGIME SCORE
# ============================================================================

def macro_regime_score(
    macro_data: Dict[str, pd.DataFrame],
    as_of_date,
    weights: Dict[str, float] = None,
) -> float:
    """
    Composite macro regime score from -1.0 to +1.0.
    Weighted average of all forward-looking signals.
    """
    if weights is None:
        weights = {
            "yield_curve": 0.30,    # Strongest forward predictor
            "rate_direction": 0.25, # Fed policy direction
            "copper_gold": 0.20,    # Growth expectations
            "dollar": 0.15,         # Liquidity proxy
            "vix": 0.10,           # Sentiment
        }

    signals = {
        "yield_curve": yield_curve_signal(macro_data, as_of_date),
        "rate_direction": rate_direction_signal(macro_data, as_of_date),
        "copper_gold": copper_gold_signal(macro_data, as_of_date),
        "dollar": dollar_signal(macro_data, as_of_date),
        "vix": vix_signal(macro_data, as_of_date),
    }

    score = sum(signals[k] * weights.get(k, 0) for k in signals)
    return max(-1.0, min(1.0, score))


def macro_sizing_multiplier(
    score: float,
    max_boost: float = 1.15,
    max_penalty: float = 0.85,
) -> float:
    """
    Convert macro score to position sizing multiplier.
    GENTLE: +-15% max. Never crush positions.

    Score > 0.5: RISK-ON -> up to 1.15x
    Score -0.25 to 0.5: NEUTRAL -> 1.0x
    Score < -0.25: RISK-OFF -> down to 0.85x
    """
    if score > 0.5:
        # Linear scale from 1.0 to max_boost
        t = min(1.0, (score - 0.5) / 0.5)
        return 1.0 + t * (max_boost - 1.0)
    elif score < -0.25:
        # Linear scale from 1.0 to max_penalty
        t = min(1.0, (-0.25 - score) / 0.75)
        return 1.0 - t * (1.0 - max_penalty)
    else:
        return 1.0


# ============================================================================
# KITCHIN CYCLE FORECASTING
# ============================================================================

def kitchin_forecast(as_of_date, is_china: bool = False) -> Dict[str, any]:
    """
    Kitchin cycle forecast with separate US and China tracking.

    Key insight: China leads US by 12-18 months.
    When US is peaking/contracting, China is already in early expansion.
    This creates rotation opportunities: shift from US to China ADRs
    when US cycle peaks and vice versa.

    Returns dict with:
      - phase: Current cycle phase label
      - position: 0.0-1.0 (position in cycle)
      - sizing_mult: Kitchin-based sizing multiplier
      - months_to_trough: Estimated months until next trough
      - months_to_peak: Estimated months until next peak
      - cycle_direction: "expanding" or "contracting"
      - divergence: US-China divergence score (-1 to +1)
    """
    from algo.indicators import kitchin_cycle_position

    if hasattr(as_of_date, 'date'):
        d = as_of_date.date()
    elif isinstance(as_of_date, str):
        d = datetime.strptime(as_of_date, "%Y-%m-%d").date()
    else:
        d = as_of_date

    # Compute both cycles
    us_pos = kitchin_cycle_position(d, KITCHIN.c3_trough, KITCHIN.period_months)
    china_pos = kitchin_cycle_position(d, KITCHIN.china_trough, KITCHIN.china_period_months)

    # Use the appropriate cycle
    if is_china:
        pos = china_pos
        period = KITCHIN.china_period_months
    else:
        pos = us_pos
        period = KITCHIN.period_months

    phase = KITCHIN.get_phase_label(pos)
    sizing_mult = KITCHIN.get_cycle_sizing_multiplier(pos)

    # Forecast: months to next trough and peak
    months_in_cycle = pos * period
    months_to_trough = period - months_in_cycle
    # Peak is roughly at 40-55% of cycle
    peak_pos = 0.47  # Midpoint of mid-expansion
    if pos < peak_pos:
        months_to_peak = (peak_pos - pos) * period
    else:
        months_to_peak = (1.0 - pos + peak_pos) * period  # Next cycle's peak

    # Direction
    if pos < 0.55:
        cycle_direction = "expanding"
    else:
        cycle_direction = "contracting"

    # US-China divergence score
    # Positive = China stronger than US (rotate to China)
    # Negative = US stronger than China (rotate to US)
    us_phase_score = _phase_to_score(KITCHIN.get_phase_label(us_pos))
    china_phase_score = _phase_to_score(KITCHIN.get_phase_label(china_pos))
    divergence = (china_phase_score - us_phase_score) / 100.0  # Normalize to -1 to +1

    return {
        "phase": phase,
        "position": round(pos, 3),
        "sizing_mult": round(sizing_mult, 2),
        "months_to_trough": round(months_to_trough, 1),
        "months_to_peak": round(months_to_peak, 1),
        "cycle_direction": cycle_direction,
        "us_position": round(us_pos, 3),
        "china_position": round(china_pos, 3),
        "us_phase": KITCHIN.get_phase_label(us_pos),
        "china_phase": KITCHIN.get_phase_label(china_pos),
        "divergence": round(divergence, 2),
    }


def _phase_to_score(phase: str) -> float:
    """Convert phase label to a bullishness score (0-100)."""
    scores = {
        "TROUGH_ACCUMULATE": 90,
        "EARLY_EXPANSION": 80,
        "MID_EXPANSION": 65,
        "LATE_EXPANSION_PEAK": 40,
        "EARLY_CONTRACTION": 20,
        "LATE_CONTRACTION": 60,  # Accumulation zone
    }
    return scores.get(phase, 50)


def kitchin_rotation_signal(as_of_date) -> Tuple[float, str]:
    """
    Returns (rotation_mult, description) for US vs China allocation.

    When China cycle is in expansion and US is contracting:
      -> Favor China ADRs (rotation_mult > 1.0 for China tickers)

    When US is expanding and China is contracting:
      -> Favor US stocks (rotation_mult < 1.0 for China tickers)

    This mult applies to China ADR sizing only.
    """
    forecast = kitchin_forecast(as_of_date, is_china=False)
    divergence = forecast["divergence"]
    us_phase = forecast["us_phase"]
    china_phase = forecast["china_phase"]

    if divergence > 0.3:
        # China significantly ahead — favor China ADRs
        return 1.2, f"China {china_phase} > US {us_phase}: favor China ADRs"
    elif divergence < -0.3:
        # US significantly ahead — favor US stocks
        return 0.8, f"US {us_phase} > China {china_phase}: favor US stocks"
    else:
        return 1.0, f"US {us_phase} ~ China {china_phase}: neutral"


def describe_macro_regime(
    macro_data: Dict[str, pd.DataFrame],
    as_of_date,
) -> str:
    """Human-readable description of current macro regime."""
    score = macro_regime_score(macro_data, as_of_date)
    mult = macro_sizing_multiplier(score)
    forecast = kitchin_forecast(as_of_date)

    signals = {
        "yield_curve": yield_curve_signal(macro_data, as_of_date),
        "rate_direction": rate_direction_signal(macro_data, as_of_date),
        "copper_gold": copper_gold_signal(macro_data, as_of_date),
        "dollar": dollar_signal(macro_data, as_of_date),
        "vix": vix_signal(macro_data, as_of_date),
    }

    signal_names = {1: "BULLISH", 0: "NEUTRAL", -1: "BEARISH"}
    parts = [f"{k}: {signal_names.get(v, '?')}" for k, v in signals.items()]

    regime = "RISK-ON" if score > 0.5 else "RISK-OFF" if score < -0.25 else "NEUTRAL"

    return (
        f"Macro: {regime} (score={score:+.2f}, mult={mult:.2f}x) | "
        f"Kitchin US={forecast['us_phase']} China={forecast['china_phase']} "
        f"(divergence={forecast['divergence']:+.2f}) | "
        + " | ".join(parts)
    )
