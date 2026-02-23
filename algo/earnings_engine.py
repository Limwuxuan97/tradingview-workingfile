"""
EARNINGS ENGINE — Earnings data pull & catalyst scoring
========================================================
Pulls earnings data from yfinance to make informed EP (Episodic Pivot) trades.
When an EP triggers near an earnings event, we score the earnings quality
and add a BONUS to the scan score (never penalize — keep pure technical).

Earnings Catalyst Score (0-100):
  - EPS surprise magnitude (0-30)
  - Revenue surprise (0-25)
  - Revenue acceleration QoQ (0-25)
  - Earnings beat streak (0-20)
"""

import os
import json
import time
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta


# ============================================================================
# CACHE
# ============================================================================

def _earnings_cache_dir() -> str:
    cache_dir = os.path.join(os.path.dirname(__file__), "..", ".cache", "earnings")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _cache_path(ticker: str) -> str:
    return os.path.join(_earnings_cache_dir(), f"{ticker}_earnings.json")


def _cache_is_fresh(path: str, max_age_hours: int = 168) -> bool:
    """Earnings data cached for 7 days (168 hours) — rarely changes retroactively."""
    if not os.path.exists(path):
        return False
    age = time.time() - os.path.getmtime(path)
    return age < max_age_hours * 3600


# ============================================================================
# DATA FETCHING
# ============================================================================

def fetch_earnings_for_ticker(ticker: str) -> List[dict]:
    """
    Fetch earnings history for a single ticker from yfinance.
    Returns list of earnings records sorted by date (oldest first).
    Each record: {date, eps_actual, eps_estimate, revenue_actual, revenue_estimate}
    """
    cache_file = _cache_path(ticker)

    if _cache_is_fresh(cache_file):
        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except Exception:
            pass

    try:
        import yfinance as yf
        tk = yf.Ticker(ticker)

        records = []

        # Try earnings_history (has EPS actual vs estimate)
        try:
            eh = tk.earnings_history
            if eh is not None and not eh.empty:
                for _, row in eh.iterrows():
                    record = {
                        "date": str(row.name.date()) if hasattr(row.name, 'date') else str(row.name),
                        "eps_actual": float(row.get("epsActual", 0)) if pd.notna(row.get("epsActual")) else None,
                        "eps_estimate": float(row.get("epsEstimate", 0)) if pd.notna(row.get("epsEstimate")) else None,
                    }
                    records.append(record)
        except Exception:
            pass

        # Try quarterly financials for revenue data
        try:
            qf = tk.quarterly_financials
            if qf is not None and not qf.empty:
                for col_date in qf.columns:
                    rev = None
                    for key in ["Total Revenue", "Revenue", "totalRevenue"]:
                        if key in qf.index:
                            val = qf.loc[key, col_date]
                            if pd.notna(val):
                                rev = float(val)
                                break

                    date_str = str(col_date.date()) if hasattr(col_date, 'date') else str(col_date)

                    # Match to existing record or create new one
                    matched = False
                    for r in records:
                        # Match within 30 days
                        try:
                            r_date = datetime.strptime(r["date"], "%Y-%m-%d").date()
                            q_date = col_date.date() if hasattr(col_date, 'date') else col_date
                            if abs((r_date - q_date).days) <= 30:
                                r["revenue_actual"] = rev
                                matched = True
                                break
                        except Exception:
                            pass

                    if not matched and rev is not None:
                        records.append({
                            "date": date_str,
                            "eps_actual": None,
                            "eps_estimate": None,
                            "revenue_actual": rev,
                        })
        except Exception:
            pass

        # Sort by date
        records.sort(key=lambda x: x.get("date", ""))

        # Cache
        try:
            with open(cache_file, "w") as f:
                json.dump(records, f, indent=2)
        except Exception:
            pass

        return records

    except Exception:
        return []


def bulk_fetch_earnings(
    tickers: List[str],
    max_per_batch: int = 20,
    delay: float = 1.0,
) -> Dict[str, List[dict]]:
    """
    Fetch earnings data for multiple tickers.
    Returns: {ticker: [earnings_records]}
    """
    result = {}
    total = len(tickers)

    for i, ticker in enumerate(tickers):
        if i > 0 and i % max_per_batch == 0:
            if i % 100 == 0:
                print(f"  Earnings fetch: {i}/{total} tickers...")
            time.sleep(delay)

        records = fetch_earnings_for_ticker(ticker)
        if records:
            result[ticker] = records

    print(f"  Fetched earnings for {len(result)}/{total} tickers")
    return result


# ============================================================================
# EARNINGS CATALYST SCORING
# ============================================================================

def earnings_catalyst_score(
    earnings_records: List[dict],
    as_of_date,
) -> float:
    """
    Compute earnings catalyst score (0-100) based on the most recent
    earnings report on or before as_of_date.

    Components:
      EPS Surprise (0-30): How much did EPS beat estimates?
      Revenue Surprise (0-25): How much did revenue beat?
      Revenue Acceleration (0-25): Is revenue growth accelerating QoQ?
      Earnings Streak (0-20): How many consecutive beats?
    """
    if not earnings_records:
        return 0.0

    # Convert as_of_date
    if hasattr(as_of_date, 'date'):
        target = as_of_date.date()
    elif isinstance(as_of_date, str):
        target = datetime.strptime(as_of_date, "%Y-%m-%d").date()
    else:
        target = as_of_date

    # Find records on or before as_of_date
    past_records = []
    for r in earnings_records:
        try:
            r_date = datetime.strptime(r["date"], "%Y-%m-%d").date()
            if r_date <= target:
                past_records.append(r)
        except Exception:
            continue

    if not past_records:
        return 0.0

    # Most recent record
    latest = past_records[-1]
    score = 0.0

    # === EPS Surprise (0-30) ===
    eps_actual = latest.get("eps_actual")
    eps_estimate = latest.get("eps_estimate")
    if eps_actual is not None and eps_estimate is not None and eps_estimate != 0:
        surprise_pct = (eps_actual - eps_estimate) / abs(eps_estimate) * 100
        if surprise_pct >= 20:
            score += 30
        elif surprise_pct >= 10:
            score += 20
        elif surprise_pct >= 0:
            score += 10
        # Miss: 0 points (no penalty)

    # === Revenue Surprise (0-25) ===
    rev_actual = latest.get("revenue_actual")
    rev_estimate = latest.get("revenue_estimate")
    if rev_actual is not None and rev_estimate is not None and rev_estimate != 0:
        rev_surprise_pct = (rev_actual - rev_estimate) / abs(rev_estimate) * 100
        if rev_surprise_pct >= 5:
            score += 25
        elif rev_surprise_pct >= 2:
            score += 15
        elif rev_surprise_pct >= 0:
            score += 8

    # === Revenue Acceleration (0-25) ===
    # Compare last 2 quarters of revenue
    rev_values = []
    for r in past_records[-4:]:
        rev = r.get("revenue_actual")
        if rev is not None and rev > 0:
            rev_values.append(rev)

    if len(rev_values) >= 3:
        growth_recent = (rev_values[-1] / rev_values[-2] - 1) * 100
        growth_prior = (rev_values[-2] / rev_values[-3] - 1) * 100
        if growth_recent > growth_prior and growth_recent > 0:
            score += 25  # Accelerating
        elif growth_recent > 0:
            score += 15  # Steady growth
        else:
            score += 5   # Decelerating
    elif len(rev_values) >= 2:
        growth = (rev_values[-1] / rev_values[-2] - 1) * 100
        if growth > 5:
            score += 20
        elif growth > 0:
            score += 10

    # === Earnings Beat Streak (0-20) ===
    streak = 0
    for r in reversed(past_records):
        ea = r.get("eps_actual")
        ee = r.get("eps_estimate")
        if ea is not None and ee is not None:
            if ea >= ee:
                streak += 1
            else:
                break
        else:
            break

    if streak >= 3:
        score += 20
    elif streak >= 2:
        score += 10
    elif streak >= 1:
        score += 5

    return min(100.0, score)


def is_near_earnings(
    earnings_records: List[dict],
    as_of_date,
    window_days: int = 3,
) -> bool:
    """
    Check if there's an earnings event within window_days of as_of_date.
    Used to determine if an EP gap is earnings-driven.
    """
    if not earnings_records:
        return False

    if hasattr(as_of_date, 'date'):
        target = as_of_date.date()
    elif isinstance(as_of_date, str):
        target = datetime.strptime(as_of_date, "%Y-%m-%d").date()
    else:
        target = as_of_date

    for r in earnings_records:
        try:
            r_date = datetime.strptime(r["date"], "%Y-%m-%d").date()
            if abs((r_date - target).days) <= window_days:
                return True
        except Exception:
            continue

    return False
