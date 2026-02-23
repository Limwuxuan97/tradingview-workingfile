"""
QULLAMAGGIE SCANNER — HTF + EP + Setup Detection
=================================================
Scans universe for:
  1. High Tight Flags (HTF): Prior +30-100% run → tight consolidation → breakout
  2. Episodic Pivots (EP): >10% gap on >2x volume after flat base
  3. VCP setups: Volatility contraction with volume dry-up near breakout
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from algo.indicators import (
    sma, ema, adr_pct, atr, rsi, relative_volume, volume_dry_up,
    vcp_score, ma_alignment, above_long_ma, prior_run_pct,
    consolidation_depth, gap_pct, relative_strength, bollinger_squeeze,
    composite_technical_score, get_sector_score_bonus,
    cme_t35_score_adjustment,
)
from algo.config import QMAG


@dataclass
class ScanResult:
    """Result from scanning a single ticker."""
    ticker: str
    setup_type: str          # "HTF", "EP", "VCP", "BREAKOUT"
    score: float             # 0-100 composite quality score
    adr: float               # ADR% (volatility)
    rs_rank: float           # Relative strength percentile
    rvol: float              # Relative volume at signal
    consolidation_days: int  # Days in consolidation (HTF/VCP)
    retracement_pct: float   # Max pullback from high
    prior_run: float         # Prior trend magnitude
    stop_price: float        # Suggested stop loss
    entry_price: float       # Suggested entry price
    risk_pct: float          # Risk per share as % of entry
    date: pd.Timestamp       # Signal date


def scan_htf(df: pd.DataFrame, ticker: str, spy_close: pd.Series,
             as_of_idx: int = -1) -> Optional[ScanResult]:
    """
    High Tight Flag Scanner.
    Criteria (from Qullamaggie Blueprint):
      1. Prior trend: +30-100% in 4-8 weeks
      2. Top 2.5% RS rank
      3. Consolidation: 5-40 days, max 25% retracement
      4. VCP: 5d ATR < 50% of 20d ATR
      5. Volume dry-up: last 3-5d vol <= 70% of 20d SMA
      6. Price above 200 SMA
      7. MA alignment: 10 > 20 > 50, all rising
    """
    if len(df) < 250:
        return None

    row_idx = as_of_idx if as_of_idx != -1 else len(df) - 1
    if row_idx < 200:
        return None

    close = df["close"]
    high = df["high"]
    low = df["low"]
    vol = df["volume"]

    current_close = close.iloc[row_idx]
    current_date = df.index[row_idx]

    # 1. ADR filter
    _adr = adr_pct(df, 20).iloc[row_idx]
    if pd.isna(_adr) or _adr < QMAG.min_adr_pct or _adr > QMAG.max_adr_pct:
        return None

    # 2. Above 200 SMA (relaxed: allow within 5% below for emerging setups)
    sma200 = sma(close, 200).iloc[row_idx]
    if pd.isna(sma200) or current_close < sma200 * 0.95:
        return None

    # 3. Prior run: find the most recent significant rise ending in consolidation
    # Look back further (up to 60 days) and find the best run/consolidation combo
    # Relaxed: accept 15%+ runs (not just 30%+) to catch more emerging breakouts
    best_result = None
    best_score = 0

    for consol_len in range(5, min(41, row_idx - 40)):
        run_end = row_idx - consol_len
        run_start = max(0, run_end - 56)  # Look back 56 days (~8 weeks) for prior run

        if run_end <= run_start + 10:
            continue

        window = df.iloc[run_start:run_end + 1]
        if len(window) < 10:
            continue

        run_low = window["low"].min()
        run_high = window["high"].max()
        run_pct = (run_high - run_low) / run_low * 100.0 if run_low > 0 else 0

        if run_pct < QMAG.htf_prior_run_pct or run_pct > 200.0:  # Strict 30%+ prior run
            continue
            
        # Check consolidation quality
        consol_window = df.iloc[run_end:row_idx + 1]
        consol_high = consol_window["high"].max()
        consol_low = consol_window["low"].min()
        retracement = (consol_high - consol_low) / consol_high * 100.0 if consol_high > 0 else 100
        
        if retracement > QMAG.htf_max_retracement_pct:  # Strict max retracement (25%)
            continue
            
        # Score this combination
        combo_score = run_pct * 0.3 + (25 - retracement) * 2 + (20 - consol_len) * 0.5
        if combo_score > best_score:
            best_score = combo_score
            best_result = (run_pct, consol_len, retracement, consol_high, consol_low)
    
    if best_result is None:
        return None
    
    run_pct, consol_days, retracement, consol_high, consol_low = best_result

    # 6. VCP: ATR contraction
    _vcp = vcp_score(df).iloc[row_idx]
    # VCP and volume are scored, not gated hard
    vol_dry = volume_dry_up(vol, 20, QMAG.htf_volume_dry_ratio).iloc[row_idx]  # Strict threshold

    # 8. MA alignment
    aligned = ma_alignment(df, QMAG.trend_mas).iloc[row_idx]
    if not aligned:
        return None

    # 9. RS vs SPY
    if len(spy_close) > 63 and len(close) > 63:
        _rs = relative_strength(close, spy_close, 63).iloc[row_idx]
        rs_pct = _rs * 100 if not pd.isna(_rs) else 0
    else:
        rs_pct = 50.0

    # Calculate score
    score = 0.0
    score += min(25, run_pct / 100.0 * 25)          # Prior run strength
    score += min(25, _vcp / 100.0 * 25)             # VCP tightness
    score += 15 if aligned else 0                     # MA alignment
    score += 10 if retracement < 15 else 5            # Tight retracement
    score += min(10, rs_pct * 10) if rs_pct > 0 else 0  # RS bonus
    score += 15 if vol_dry else 5                     # Volume confirmation (partial credit)

    # Entry / Stop
    entry_price = consol_high  # Breakout above consolidation high
    stop_price = consol_low * 0.99  # Below consolidation low - 1%
    risk_pct = (entry_price - stop_price) / entry_price * 100 if entry_price > 0 else 100

    # Check risk is within ADR
    _atr_val = atr(df, 14).iloc[row_idx]
    if not pd.isna(_atr_val) and (entry_price - stop_price) > _atr_val * QMAG.max_stop_adr_multiple:
        return None

    return ScanResult(
        ticker=ticker,
        setup_type="HTF",
        score=min(100, score),
        adr=_adr,
        rs_rank=rs_pct,
        rvol=relative_volume(vol, 50).iloc[row_idx] if not pd.isna(relative_volume(vol, 50).iloc[row_idx]) else 0,
        consolidation_days=consol_days,
        retracement_pct=retracement,
        prior_run=run_pct,
        stop_price=round(stop_price, 2),
        entry_price=round(entry_price, 2),
        risk_pct=round(risk_pct, 2),
        date=current_date,
    )


def scan_ep(df: pd.DataFrame, ticker: str, spy_close: pd.Series,
            as_of_idx: int = -1,
            earnings_data: Optional[list] = None) -> Optional[ScanResult]:
    """
    Episodic Pivot Scanner.
    Criteria (from Qullamaggie Blueprint):
      1. Gap >= 10% on open
      2. RVol >= 2.0
      3. 50d avg volume >= 300K-500K
      4. 3-6 month flat prior base
      5. Fundamental catalyst (earnings, FDA, etc.)
    """
    if len(df) < 150:
        return None

    row_idx = as_of_idx if as_of_idx != -1 else len(df) - 1
    if row_idx < 130:
        return None

    close = df["close"]
    vol = df["volume"]

    current_close = close.iloc[row_idx]
    current_date = df.index[row_idx]
    prev_close = close.iloc[row_idx - 1]

    # 1. Gap detection (and OpEx deferral logic)
    from algo.indicators import is_opex_settlement_window
    
    gap_idx = row_idx
    gap_open = df["open"].iloc[gap_idx]
    prev_close = close.iloc[gap_idx - 1]
    _gap = (gap_open - prev_close) / prev_close * 100.0 if prev_close > 0 else 0
    
    if abs(_gap) >= QMAG.ep_min_gap_pct:
        # Gap is today. Check if today is a forced MM settlement window (T+1/T+2 post OpEx)
        if is_opex_settlement_window(current_date):
            return None  # Defer entry. Do not buy into the forced settlement pump.
    else:
        # No gap today. Check if there was a gap 1-2 days ago during the OpEx window, and we are now on T+3/T+4
        found_deferred_gap = False
        for offset in [1, 2]:
            temp_idx = row_idx - offset
            if temp_idx < 1: continue
            temp_date = df.index[temp_idx]
            
            if is_opex_settlement_window(temp_date):
                t_open = df["open"].iloc[temp_idx]
                t_prev = close.iloc[temp_idx - 1]
                t_gap = (t_open - t_prev) / t_prev * 100.0 if t_prev > 0 else 0
                
                if abs(t_gap) >= QMAG.ep_min_gap_pct:
                    # Found a valid deferred gap. Check if price held the gap.
                    if current_close >= t_open * 0.98:  # Price must basically hold the gap
                        gap_idx = temp_idx
                        _gap = t_gap
                        found_deferred_gap = True
                        break
        
        if not found_deferred_gap:
            return None

    # 2. Relative volume (measured on the gap day)
    _rvol = relative_volume(vol, 50).iloc[gap_idx]
    if pd.isna(_rvol) or _rvol < QMAG.ep_min_rvol:  # Strict 2x relative volume requirement
        return None

    # 3. Average volume
    avg_vol = sma(vol, 50).iloc[gap_idx]
    if pd.isna(avg_vol) or avg_vol < QMAG.ep_min_avg_volume:
        return None

    # 4. Flat prior base (3-6 months before the gap)
    base_start = max(0, gap_idx - 130)  # ~6 months
    base_end = gap_idx - 1
    base_data = df.iloc[base_start:base_end]

    if len(base_data) < 60:
        return None

    base_high = base_data["high"].max()
    base_low = base_data["low"].min()
    base_range_pct = (base_high - base_low) / base_low * 100.0 if base_low > 0 else 100

    # For EP: base should be relatively flat (< 40% range)
    is_flat_base = base_range_pct < 40.0

    # 5. ADR
    _adr = adr_pct(df, 20).iloc[row_idx]
    if pd.isna(_adr):
        _adr = 5.0

    # RS
    if len(spy_close) > 63 and len(close) > 63:
        _rs = relative_strength(close, spy_close, 63).iloc[row_idx]
        rs_pct = _rs * 100 if not pd.isna(_rs) else 0
    else:
        rs_pct = 50.0

    # Score
    score = 0.0
    score += min(25, abs(_gap) / 20.0 * 25)        # Gap magnitude
    score += min(25, _rvol / 5.0 * 25)              # Volume confirmation
    score += 20 if is_flat_base else 5               # Base quality
    score += 15 if _gap > 0 else 5                   # Bullish gap preferred
    score += min(15, rs_pct * 15) if rs_pct > 0 else 0

    # Entry: high of day (HOD breakout)
    entry_price = df["high"].iloc[gap_idx]
    # Stop: low of gap day
    stop_price = df["low"].iloc[gap_idx] * 0.99
    risk_pct = (entry_price - stop_price) / entry_price * 100 if entry_price > 0 else 100

    # === EARNINGS CATALYST BONUS (additive only, never subtractive) ===
    # If this gap is near an earnings event, check if the earnings were strong
    # Strong earnings (score > 60) get a +15 bonus — confirmed catalyst EP
    if earnings_data:
        try:
            from algo.earnings_engine import is_near_earnings, earnings_catalyst_score
            if is_near_earnings(earnings_data, current_date, window_days=3):
                e_score = earnings_catalyst_score(earnings_data, current_date)
                if e_score > 60:
                    score += 15  # Confirmed strong catalyst
                elif e_score > 40:
                    score += 8   # Decent catalyst
                # Below 40: no bonus (but no penalty either)
        except Exception:
            pass

    return ScanResult(
        ticker=ticker,
        setup_type="EP",
        score=min(100, score),
        adr=_adr,
        rs_rank=rs_pct,
        rvol=_rvol,
        consolidation_days=len(base_data),
        retracement_pct=base_range_pct,
        prior_run=abs(_gap),
        stop_price=round(stop_price, 2),
        entry_price=round(entry_price, 2),
        risk_pct=round(risk_pct, 2),
        date=current_date,
    )


def scan_breakout(df: pd.DataFrame, ticker: str, spy_close: pd.Series,
                  as_of_idx: int = -1) -> Optional[ScanResult]:
    """
    General breakout scanner (lighter criteria than HTF).
    Looks for: price breaking above consolidation range with volume.
    """
    if len(df) < 100:
        return None

    row_idx = as_of_idx if as_of_idx != -1 else len(df) - 1
    if row_idx < 60:
        return None

    close = df["close"]
    high = df["high"]
    vol = df["volume"]

    current_close = close.iloc[row_idx]
    current_date = df.index[row_idx]

    # ADR filter
    _adr = adr_pct(df, 20).iloc[row_idx]
    if pd.isna(_adr) or _adr < 2.0:
        return None

    # Find recent consolidation range (last 20 days)
    recent = df.iloc[max(0, row_idx - 20):row_idx]
    if len(recent) < 10:
        return None

    range_high = recent["high"].max()
    range_low = recent["low"].min()

    # Breakout: close above range high
    is_breakout = current_close > range_high

    if not is_breakout:
        return None

    # Volume confirmation
    _rvol = relative_volume(vol, 50).iloc[row_idx]
    if pd.isna(_rvol) or _rvol < 1.0:  # Very relaxed for range breakouts
        return None

    # VCP bonus
    _vcp = vcp_score(df).iloc[row_idx]

    # Bollinger squeeze bonus
    _squeeze = bollinger_squeeze(close).iloc[row_idx]

    # MA check
    aligned = ma_alignment(df, [10, 20, 50]).iloc[row_idx]
    above200 = above_long_ma(df, 200).iloc[row_idx]

    # RS
    if len(spy_close) > 63 and len(close) > 63:
        _rs = relative_strength(close, spy_close, 63).iloc[row_idx]
        rs_pct = _rs * 100 if not pd.isna(_rs) else 0
    else:
        rs_pct = 50.0

    # Score
    score = 0.0
    score += 20  # Base: it's a breakout
    score += min(15, _rvol / 3.0 * 15)    # Volume
    score += min(15, _vcp / 100.0 * 15) if not pd.isna(_vcp) else 0  # VCP
    score += 10 if _squeeze else 0          # Squeeze breakout bonus
    score += 15 if aligned else 5           # MA alignment
    score += 10 if above200 else 0          # Above 200 SMA
    score += min(15, rs_pct * 15) if rs_pct > 0 else 0

    entry_price = current_close
    stop_price = range_low * 0.99
    risk_pct = (entry_price - stop_price) / entry_price * 100 if entry_price > 0 else 100

    # Risk too wide? Skip (but use a generous multiplier)
    if risk_pct > _adr * 2.5:
        return None

    return ScanResult(
        ticker=ticker,
        setup_type="BREAKOUT",
        score=min(100, score),
        adr=_adr,
        rs_rank=rs_pct,
        rvol=_rvol,
        consolidation_days=len(recent),
        retracement_pct=(range_high - range_low) / range_high * 100 if range_high > 0 else 0,
        prior_run=0,
        stop_price=round(stop_price, 2),
        entry_price=round(entry_price, 2),
        risk_pct=round(risk_pct, 2),
        date=current_date,
    )


def run_full_scan(
    universe_data: Dict[str, pd.DataFrame],
    spy_df: pd.DataFrame,
    as_of_idx: int = -1,
    min_score: float = 20.0,
    sector_rs: Optional[Dict[str, float]] = None,
    current_date=None,
    cycle_phase: str = "",
    earnings_data: Optional[Dict[str, list]] = None,
) -> List[ScanResult]:
    """
    Run all scanners across the universe.
    Applies sector rotation bonus (with Newton cycle rotation), CME T+35 adjustment,
    composite score filter, and RSI guard.
    Returns sorted list of setups (best first).
    """
    results = []
    spy_close = spy_df["close"] if not spy_df.empty else pd.Series()

    for ticker, df in universe_data.items():
        if df.empty or len(df) < 100:
            continue

        # Determine the row index to scan
        idx = as_of_idx if as_of_idx != -1 else len(df) - 1

        # Get earnings data for this ticker (if available)
        ticker_earnings = earnings_data.get(ticker) if earnings_data else None

        # Run all scanners
        for scanner in [scan_htf, scan_ep, scan_breakout]:
            try:
                if scanner == scan_ep and ticker_earnings:
                    result = scanner(df, ticker, spy_close, idx,
                                     earnings_data=ticker_earnings)
                else:
                    result = scanner(df, ticker, spy_close, idx)
                if result is None:
                    continue

                # NOTE: All score overlays DISABLED.
                # Qullamaggie uses PURE price action + volume. No sector RS, no
                # tech score overlays, no CME timing on signals. These overlays
                # were stacking to create 15-20% score penalties that crushed
                # performance from ~90% CAGR to 12%. Macro factors are already
                # handled via Kitchin cycle position sizing + regime filter.

                if result.score >= min_score:
                    results.append(result)
            except Exception:
                continue

    # Sort by score descending
    results.sort(key=lambda x: x.score, reverse=True)
    return results
