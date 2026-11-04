"""Binance historical data archives - free, no key, no signup.

data.binance.vision hosts monthly zips of klines. A 1-minute month is ~2 MB and
contains ~44,000 bars. This is the only source that gives 9+ years of intraday
history with zero account requirements.

    data/spot/monthly/klines/<SYMBOL>/<interval>/<SYMBOL>-<interval>-<YYYY-MM>.zip

The CSV inside has NO header row and 12 columns:
    open_time, open, high, low, close, volume, close_time, quote_volume,
    trades, taker_buy_volume, taker_buy_quote_volume, ignore

Per-month files are cached under data/archive/ so a re-run costs zero downloads.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

ARCHIVE_DIR = Path(__file__).resolve().parent.parent / "data" / "archive"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

BASE = "https://data.binance.vision/data/spot/monthly/klines"
COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "trades", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]


def _epoch_ms(index: pd.DatetimeIndex) -> pd.Series:
    """Epoch milliseconds for a DatetimeIndex.

    Do NOT hardcode a divisor: pandas 3.x keeps datetime64 at MILLISECOND
    resolution, so index.astype('int64') is already ms and dividing again
    silently shifts every timestamp by 1000x.
    """
    try:
        values = index.as_unit("ms").astype("int64")
    except Exception:  # older pandas: ns resolution
        values = index.astype("int64") // 10**6
    return pd.Series(values, index=index)


def _to_utc(epoch: pd.Series) -> pd.DatetimeIndex:
    """Epoch -> UTC timestamps, detecting the unit Binance shipped that month.

    Older monthly files use milliseconds; the newer ones (2026-04 onward)
    use microseconds. Assuming the wrong unit shifts the data by 1000x.
    """
    values = pd.to_numeric(epoch, errors="coerce")
    peak = float(values.max()) if len(values) else 0.0
    if peak > 1e15:
        unit = "us"
    elif peak > 1e12:
        unit = "ms"
    else:
        unit = "s"
    return pd.to_datetime(values, unit=unit, utc=True)


def _months(start: str, end: str) -> list[str]:
    """['2024-01', '2024-02', ...] inclusive of both endpoints (YYYY-MM)."""
    s = pd.Timestamp(start).to_period("M")
    e = pd.Timestamp(end).to_period("M")
    return [str(p) for p in pd.period_range(s, e, freq="M")]


def fetch_month(symbol: str, interval: str, month: str, refresh: bool = False) -> pd.DataFrame:
    """One month of klines. Cached on disk; returns an empty frame if 404."""
    symbol = symbol.upper()
    cache = ARCHIVE_DIR / f"{symbol}_{interval}_{month}.csv"
    if cache.exists() and not refresh:
        df = pd.read_csv(cache, index_col=0)
        df.index = _to_utc(df["open_time"])
        df = df.drop(columns="open_time")
        df.index.name = "timestamp"
        return df

    url = f"{BASE}/{symbol}/{interval}/{symbol}-{interval}-{month}.zip"
    resp = requests.get(url, timeout=120)
    if resp.status_code == 404:
        return pd.DataFrame()
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        name = zf.namelist()[0]
        with zf.open(name) as fh:
            raw = pd.read_csv(fh, header=None, names=COLUMNS)

    df = raw[["open_time", "open", "high", "low", "close", "volume", "trades"]].copy()
    df["open_time"] = pd.to_numeric(df["open_time"])
    df.index = _to_utc(df["open_time"])
    df.index.name = "timestamp"
    for col in ("open", "high", "low", "close", "volume", "trades"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close"])

    df.to_csv(cache)
    return df


def build_dataset(
    symbol: str = "BTCUSDT",
    interval: str = "1m",
    start: str = "2020-01",
    end: str = "2026-09",
    refresh: bool = False,
    verbose: bool = True,
    workers: int = 8,
) -> pd.DataFrame:
    """Concatenate months into one continuous frame (parallel download)."""
    from concurrent.futures import ThreadPoolExecutor

    months = _months(start, end)

    def get(month: str):
        try:
            return month, fetch_month(symbol, interval, month, refresh=refresh)
        except Exception as exc:
            print(f"  !! {month} failed: {exc}", flush=True)
            return month, pd.DataFrame()

    frames = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for i, (month, df) in enumerate(pool.map(get, months), 1):
            if not df.empty:
                frames.append(df)
            if verbose:
                print(f"  [{i}/{len(months)}] {month}: {len(df):>7} bars", flush=True)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames)
    out = out[~out.index.duplicated(keep="last")].sort_index()
    # keep the raw epoch so the CSV round-trip can rebuild the index exactly
    out["open_time"] = _epoch_ms(out.index)
    # the index may have been written as a data column by an older cache file
    out = out.drop(columns=[c for c in out.columns if c.startswith("timestamp")], errors="ignore")
    return out


def load_dataset(
    symbol: str = "BTCUSDT",
    interval: str = "1m",
    start: str = "2020-01",
    end: str = "2026-09",
    refresh: bool = False,
    verbose: bool = True,
) -> pd.DataFrame:
    """Load the combined archive frame, downloading missing months first."""
    symbol = symbol.upper()
    combined = ARCHIVE_DIR / f"{symbol}_{interval}_{start}_{end}.csv"
    if combined.exists() and not refresh:
        df = pd.read_csv(combined, index_col=0)
        df.index = _to_utc(df["open_time"])
        df = df.drop(columns="open_time")
        df.index.name = "timestamp"
        return df
    df = build_dataset(symbol, interval, start, end, refresh=refresh, verbose=verbose)
    if not df.empty:
        df.to_csv(combined)
    return df


def coverage(symbol: str = "BTCUSDT", interval: str = "1m") -> list[str]:
    """Months that exist on the archive (probe with a HEAD request)."""
    found = []
    for month in _months("2017-01", "2026-12"):
        url = f"{BASE}/{symbol.upper()}/{interval}/{symbol.upper()}-{interval}-{month}.zip"
        try:
            r = requests.head(url, timeout=20, allow_redirects=True)
            if r.status_code == 200:
                found.append(month)
        except Exception:
            continue
    return found
