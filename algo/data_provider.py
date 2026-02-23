"""
DATA PROVIDER — Fetches OHLCV + fundamental data
================================================
Primary: yfinance for backtesting
Secondary: Longbridge API for live trading
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import time
import json


class DataProvider:
    """Abstract data provider interface."""

    def get_ohlcv(self, ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
        raise NotImplementedError

    def get_bulk_ohlcv(self, tickers: List[str], start: str, end: str, interval: str = "1d") -> Dict[str, pd.DataFrame]:
        raise NotImplementedError


class YFinanceProvider(DataProvider):
    """Yahoo Finance data provider for backtesting."""

    def __init__(self, cache_dir: str = None):
        try:
            import yfinance as yf
            self.yf = yf
        except ImportError:
            raise ImportError("Install yfinance: pip install yfinance")
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), "..", ".cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self._cache: Dict[str, pd.DataFrame] = {}

    def _cache_key(self, ticker: str, start: str, end: str, interval: str) -> str:
        return f"{ticker}_{start}_{end}_{interval}"

    def _cache_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.parquet")

    def get_ohlcv(self, ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
        """Fetch OHLCV data with disk caching."""
        key = self._cache_key(ticker, start, end, interval)

        # Memory cache
        if key in self._cache:
            return self._cache[key]

        # Disk cache
        cache_file = self._cache_path(key)
        if os.path.exists(cache_file):
            mod_time = os.path.getmtime(cache_file)
            if time.time() - mod_time < 86400:  # 24h cache
                try:
                    df = pd.read_parquet(cache_file)
                    self._cache[key] = df
                    return df
                except Exception:
                    pass

        # Fetch from yfinance
        try:
            tk = self.yf.Ticker(ticker)
            df = tk.history(start=start, end=end, interval=interval, auto_adjust=True)
            if df.empty:
                return pd.DataFrame()

            # Standardize columns
            df.columns = [c.lower().replace(" ", "_") for c in df.columns]
            for col in ["open", "high", "low", "close", "volume"]:
                if col not in df.columns:
                    df[col] = np.nan

            df = df[["open", "high", "low", "close", "volume"]].copy()
            df.index = pd.to_datetime(df.index)
            df.index = df.index.tz_localize(None)  # Remove timezone
            df = df.dropna(subset=["close"])

            # Cache
            try:
                df.to_parquet(cache_file)
            except Exception:
                pass
            self._cache[key] = df
            return df

        except Exception as e:
            print(f"  [WARN] Failed to fetch {ticker}: {e}")
            return pd.DataFrame()

    def get_bulk_ohlcv(self, tickers: List[str], start: str, end: str,
                       interval: str = "1d",
                       batch_size: int = 100,
                       batch_delay: float = 2.0) -> Dict[str, pd.DataFrame]:
        """
        Fetch multiple tickers with batching and retry logic.
        For large universes (1000+), downloads in batches to avoid rate limits.
        """
        result = {}

        # Split into batches for large universes
        if len(tickers) <= batch_size:
            batches = [tickers]
        else:
            batches = [tickers[i:i + batch_size] for i in range(0, len(tickers), batch_size)]
            print(f"  Downloading {len(tickers)} tickers in {len(batches)} batches...")

        for batch_idx, batch in enumerate(batches):
            if len(batches) > 1:
                print(f"  Batch {batch_idx + 1}/{len(batches)}: {len(batch)} tickers "
                      f"({len(result)} loaded so far)...")

            batch_result = self._download_batch(batch, start, end, interval)
            result.update(batch_result)

            # Delay between batches to avoid rate limits
            if batch_idx < len(batches) - 1 and batch_delay > 0:
                time.sleep(batch_delay)

        # Fetch missing tickers individually (with retry)
        missing = [t for t in tickers if t not in result]
        if missing and len(missing) <= 50:
            for ticker in missing:
                df = self.get_ohlcv(ticker, start, end, interval)
                if not df.empty:
                    result[ticker] = df

        return result

    def _download_batch(self, tickers: List[str], start: str, end: str,
                        interval: str, max_retries: int = 3) -> Dict[str, pd.DataFrame]:
        """Download a batch of tickers with retry logic."""
        result = {}

        for attempt in range(max_retries):
            try:
                raw = self.yf.download(tickers, start=start, end=end,
                                       interval=interval, auto_adjust=True,
                                       group_by="ticker", threads=True,
                                       progress=False)

                if isinstance(raw.columns, pd.MultiIndex):
                    for ticker in tickers:
                        try:
                            df = raw[ticker].copy()
                            df.columns = [c.lower().replace(" ", "_") for c in df.columns]
                            df = df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
                            df.index = pd.to_datetime(df.index).tz_localize(None)
                            if not df.empty:
                                result[ticker] = df
                        except Exception:
                            pass
                elif len(tickers) == 1:
                    df = raw.copy()
                    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
                    df = df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
                    df.index = pd.to_datetime(df.index).tz_localize(None)
                    if not df.empty:
                        result[tickers[0]] = df

                return result

            except Exception as e:
                delay = 5 * (3 ** attempt)  # 5s, 15s, 45s
                if attempt < max_retries - 1:
                    print(f"  [RETRY] Batch download failed (attempt {attempt + 1}): {e}. "
                          f"Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    print(f"  [WARN] Batch download failed after {max_retries} attempts: {e}")

        return result

    def get_market_cap(self, ticker: str) -> Optional[float]:
        """Get current market cap."""
        try:
            info = self.yf.Ticker(ticker).info
            return info.get("marketCap", None)
        except Exception:
            return None


def get_sp500_tickers() -> List[str]:
    """Fetch current S&P 500 constituents from Wikipedia."""
    try:
        table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        df = table[0]
        tickers = df["Symbol"].str.replace(".", "-", regex=False).tolist()
        return tickers
    except Exception as e:
        print(f"  [WARN] Could not fetch S&P 500 list: {e}")
        return []


def get_dynamic_universe(include_china: bool = True) -> List[str]:
    """Build dynamic universe: S&P 500 + China ADRs."""
    from algo.config import CHINA_ADR_UNIVERSE
    tickers = get_sp500_tickers()
    if include_china:
        tickers = list(set(tickers + CHINA_ADR_UNIVERSE))
    print(f"  Dynamic universe: {len(tickers)} tickers")
    return tickers


class LongbridgeProvider(DataProvider):
    """Longbridge API data provider for live trading."""

    def __init__(self, app_key: str, app_secret: str, access_token: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from longbridge.openapi import QuoteContext, Config
                config = Config(
                    app_key=self.app_key,
                    app_secret=self.app_secret,
                    access_token=self.access_token,
                )
                self._client = QuoteContext(config)
            except ImportError:
                raise ImportError("Install longbridge SDK: pip install longbridge")
        return self._client

    def get_ohlcv(self, ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
        """Fetch from Longbridge. Ticker format: 'US.BABA' for US stocks."""
        try:
            from longbridge.openapi import Period, AdjustType
            ctx = self._get_client()

            # Map interval
            period_map = {
                "1d": Period.Day,
                "1wk": Period.Week,
                "1mo": Period.Month,
            }
            period = period_map.get(interval, Period.Day)

            # Longbridge uses 'US.TICKER' format
            lb_ticker = f"US.{ticker}" if "." not in ticker else ticker

            candles = ctx.candlesticks(
                lb_ticker,
                period,
                500,  # max count
                AdjustType.ForwardAdjust,
            )

            rows = []
            for c in candles:
                rows.append({
                    "date": c.timestamp,
                    "open": float(c.open),
                    "high": float(c.high),
                    "low": float(c.low),
                    "close": float(c.close),
                    "volume": int(c.volume),
                })

            df = pd.DataFrame(rows)
            if df.empty:
                return df
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index()

            # Filter date range
            df = df.loc[start:end]
            return df

        except Exception as e:
            print(f"  [WARN] Longbridge fetch failed for {ticker}: {e}")
            return pd.DataFrame()

    def get_bulk_ohlcv(self, tickers: List[str], start: str, end: str,
                       interval: str = "1d") -> Dict[str, pd.DataFrame]:
        result = {}
        for ticker in tickers:
            df = self.get_ohlcv(ticker, start, end, interval)
            if not df.empty:
                result[ticker] = df
        return result
