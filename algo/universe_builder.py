"""
UNIVERSE BUILDER — Dynamic ticker discovery & pre-filtering
============================================================
Implements Qullamaggie's approach: scan 5000+ stocks nightly,
filter down to the top 1-2% that meet strict momentum criteria.

Three-stage funnel:
  1. Discover: Get all US-listed tickers (~7000-8000)
  2. Pre-filter: Metadata-based (market cap, volume, price) → ~2000-3000
  3. Daily scan filter: OHLCV-based (above 200 SMA, ADR > 2%) → ~200-500/day
"""

import os
import time
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

from algo.config import CHINA_ADR_UNIVERSE


# ============================================================================
# STAGE 1: TICKER DISCOVERY
# ============================================================================

def _get_cache_dir() -> str:
    """Cache directory for ticker lists."""
    cache_dir = os.path.join(os.path.dirname(__file__), "..", ".cache", "ticker_lists")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _cache_is_fresh(path: str, max_age_days: int = 7) -> bool:
    """Check if cache file exists and is recent enough."""
    if not os.path.exists(path):
        return False
    age = time.time() - os.path.getmtime(path)
    return age < max_age_days * 86400


def discover_nasdaq_screener() -> pd.DataFrame:
    """
    Fetch all US-listed stocks from NASDAQ Stock Screener.
    Returns DataFrame with: symbol, name, market_cap, sector, volume, last_sale.
    """
    cache_path = os.path.join(_get_cache_dir(), "nasdaq_screener.csv")

    if _cache_is_fresh(cache_path, max_age_days=7):
        print("  Using cached NASDAQ screener data...")
        return pd.read_csv(cache_path)

    print("  Fetching ticker list from NASDAQ screener...")
    try:
        # NASDAQ provides a CSV download endpoint
        url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=10000&offset=0"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        import urllib.request
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        rows = data.get("data", {}).get("table", {}).get("rows", [])
        if not rows:
            # Try alternative: data.data.rows
            rows = data.get("data", {}).get("rows", [])

        if rows:
            df = pd.DataFrame(rows)
            # Standardize columns
            col_map = {
                "symbol": "symbol",
                "name": "name",
                "lastsale": "last_sale",
                "netchange": "net_change",
                "pctchange": "pct_change",
                "marketCap": "market_cap",
                "volume": "volume",
                "sector": "sector",
                "industry": "industry",
                "country": "country",
            }
            df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

            # Clean numeric fields
            for col in ["last_sale", "market_cap", "volume"]:
                if col in df.columns:
                    df[col] = (
                        df[col].astype(str)
                        .str.replace("$", "", regex=False)
                        .str.replace(",", "", regex=False)
                        .str.replace("%", "", regex=False)
                    )
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            df.to_csv(cache_path, index=False)
            print(f"  Discovered {len(df)} tickers from NASDAQ screener")
            return df

    except Exception as e:
        print(f"  [WARN] NASDAQ screener failed: {e}")

    # Fallback: return empty (will use Wikipedia fallback)
    return pd.DataFrame()


def discover_wikipedia_sp500() -> List[str]:
    """Fetch S&P 500 tickers from Wikipedia."""
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        df = tables[0]
        tickers = df["Symbol"].str.replace(".", "-", regex=False).tolist()
        print(f"  Discovered {len(tickers)} S&P 500 tickers from Wikipedia")
        return tickers
    except Exception as e:
        print(f"  [WARN] Wikipedia S&P 500 fetch failed: {e}")
        return []


def discover_wikipedia_russell1000() -> List[str]:
    """Fetch Russell 1000 tickers from Wikipedia for broader coverage."""
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/Russell_1000_Index")
        # Usually the first or second table has the constituents
        for table in tables:
            if "Ticker" in table.columns or "Symbol" in table.columns:
                col = "Ticker" if "Ticker" in table.columns else "Symbol"
                tickers = table[col].str.replace(".", "-", regex=False).dropna().tolist()
                if len(tickers) > 500:
                    print(f"  Discovered {len(tickers)} Russell 1000 tickers from Wikipedia")
                    return tickers
    except Exception:
        pass
    return []


def discover_all_tickers(refresh: bool = False) -> pd.DataFrame:
    """
    Master discovery function. Tries multiple sources.
    Returns DataFrame with at minimum: symbol, market_cap, volume columns.
    """
    cache_path = os.path.join(_get_cache_dir(), "all_tickers.csv")

    if not refresh and _cache_is_fresh(cache_path, max_age_days=7):
        df = pd.read_csv(cache_path)
        print(f"  Loaded {len(df)} cached tickers")
        return df

    print("Discovering US-listed tickers...")

    # Try NASDAQ screener first (best: has market cap, volume, sector)
    df = discover_nasdaq_screener()

    if df.empty or len(df) < 1000:
        # Fallback: combine Wikipedia sources
        print("  Falling back to Wikipedia sources...")
        sp500 = discover_wikipedia_sp500()
        russell = discover_wikipedia_russell1000()

        all_tickers = list(set(sp500 + russell + CHINA_ADR_UNIVERSE))
        df = pd.DataFrame({"symbol": all_tickers})
        df["market_cap"] = np.nan
        df["volume"] = np.nan
        df["sector"] = ""
        df["last_sale"] = np.nan

    # Always include China ADRs
    china_df = pd.DataFrame({"symbol": CHINA_ADR_UNIVERSE})
    for col in df.columns:
        if col not in china_df.columns:
            china_df[col] = np.nan
    df = pd.concat([df, china_df], ignore_index=True).drop_duplicates(subset=["symbol"])

    # Cache
    df.to_csv(cache_path, index=False)
    print(f"  Total discovered: {len(df)} tickers")
    return df


# ============================================================================
# STAGE 2: PRE-FILTER (metadata-based, no OHLCV needed)
# ============================================================================

def pre_filter_universe(
    all_tickers: pd.DataFrame,
    min_market_cap: float = 300_000_000,
    min_volume: int = 100_000,
    min_price: float = 5.0,
    max_tickers: int = 3000,
) -> List[str]:
    """
    Filter tickers by metadata (market cap, volume, price).
    Returns list of ticker symbols that pass basic criteria.
    """
    df = all_tickers.copy()
    initial_count = len(df)

    # Remove blanks
    df = df[df["symbol"].notna() & (df["symbol"].str.len() > 0)]

    # Remove tickers with special characters (warrants, units, etc.)
    df = df[~df["symbol"].str.contains(r"[^A-Z\-\.]", na=False, regex=True)]

    # Filter by length (most stocks are 1-5 chars, exclude long symbols)
    df = df[df["symbol"].str.len() <= 5]

    # If we have market cap data, filter
    if "market_cap" in df.columns and df["market_cap"].notna().any():
        df = df[(df["market_cap"] >= min_market_cap) | df["market_cap"].isna()]

    # If we have volume data, filter
    if "volume" in df.columns and df["volume"].notna().any():
        df = df[(df["volume"] >= min_volume) | df["volume"].isna()]

    # If we have price data, filter
    if "last_sale" in df.columns and df["last_sale"].notna().any():
        df = df[(df["last_sale"] >= min_price) | df["last_sale"].isna()]

    # Cap at max_tickers (sort by market cap if available)
    if "market_cap" in df.columns and df["market_cap"].notna().any():
        df = df.sort_values("market_cap", ascending=False, na_position="last")

    tickers = df["symbol"].head(max_tickers).tolist()

    print(f"  Pre-filter: {initial_count} -> {len(tickers)} tickers "
          f"(cap>=${min_market_cap/1e6:.0f}M, vol>={min_volume/1000:.0f}K, price>=${min_price})")
    return tickers


# ============================================================================
# STAGE 3: DAILY SCAN PRE-FILTER (fast vectorized OHLCV filter)
# ============================================================================

def daily_scan_prefilter(
    universe_data: Dict[str, pd.DataFrame],
    as_of_date: pd.Timestamp,
    min_adr_pct: float = 2.0,
    above_sma: int = 200,
) -> List[str]:
    """
    Fast vectorized pre-filter on OHLCV data.
    Returns tickers that:
      1. Have price above their 200 SMA (uptrend)
      2. Have ADR(20) > 2% (volatile enough for momentum)

    This narrows ~3000 tickers to ~200-500 candidates per day.
    Only these go to the full HTF/EP/Breakout scanner.
    """
    candidates = []

    for ticker, df in universe_data.items():
        if df.empty or len(df) < above_sma + 20:
            continue

        # Get data up to as_of_date
        mask = df.index <= as_of_date
        if not mask.any():
            continue

        idx = mask.sum() - 1
        if idx < above_sma:
            continue

        close = df["close"].values
        high = df["high"].values
        low = df["low"].values

        current_close = close[idx]

        # 1. Above 200 SMA
        sma_val = np.mean(close[idx - above_sma + 1:idx + 1])
        if current_close < sma_val:
            continue

        # 2. ADR(20) > min_adr_pct
        if idx >= 20:
            daily_range = (high[idx - 19:idx + 1] - low[idx - 19:idx + 1]) / close[idx - 19:idx + 1] * 100
            adr = np.mean(daily_range)
            if adr < min_adr_pct:
                continue

        # 3. Minimum volume (last 20 days avg > 50K)
        vol = df["volume"].values
        if idx >= 20:
            avg_vol = np.mean(vol[idx - 19:idx + 1])
            if avg_vol < 50000:
                continue

        candidates.append(ticker)

    return candidates


# ============================================================================
# CONVENIENCE: Build full filtered universe for backtest
# ============================================================================

def build_backtest_universe(
    min_market_cap: float = 300_000_000,
    min_volume: int = 100_000,
    min_price: float = 5.0,
    max_tickers: int = 3000,
    include_china: bool = True,
    refresh: bool = False,
) -> List[str]:
    """
    Full pipeline: discover → pre-filter → return ticker list.
    Use this to get the universe for backtesting.
    """
    all_tickers = discover_all_tickers(refresh=refresh)
    filtered = pre_filter_universe(
        all_tickers,
        min_market_cap=min_market_cap,
        min_volume=min_volume,
        min_price=min_price,
        max_tickers=max_tickers,
    )

    # Always include China ADRs
    if include_china:
        for ticker in CHINA_ADR_UNIVERSE:
            if ticker not in filtered:
                filtered.append(ticker)

    return filtered
