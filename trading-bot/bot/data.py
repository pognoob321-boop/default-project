"""Free market data fetchers. No API keys, no signup, no paid tiers.

Sources used (both work from Cambodia / this machine, verified 2026-10-21):
  - Yahoo Finance chart API  : US equities + index futures. Free, no key.
        1m -> last 7 days | 5m -> last 60 days | 1d -> decades
  - Binance public klines API : crypto, 24/7. Free, no key, paginates to 2017.

Everything is cached to data/ as CSV so backtests are reproducible and reruns
cost zero API calls.
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Binance serves the same public market data from several hosts. api.binance.com
# rate-limits or resets connections under load, so every call tries a fallback.
# NOTE: testnet.binance.vision has its OWN simulated order book - use it for
# connectivity, never for real price history.
BINANCE_HOSTS = [
    "https://api.binance.com",
    "https://data-api.binance.vision",
    "https://api-gcp.binance.com",
]


def _binance_get(path: str, params: dict, tries: int | None = None) -> list:
    """GET a Binance path, rotating through hosts on connection failure."""
    last_exc = None
    for host in BINANCE_HOSTS[: tries or len(BINANCE_HOSTS)]:
        try:
            resp = requests.get(f"{host}{path}", params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # network-level failure -> try the next host
            last_exc = exc
            continue
    raise RuntimeError(f"Binance request failed on all hosts: {last_exc}")


def _cache_file(name: str) -> Path:
    return DATA_DIR / name


def load_cache(name: str) -> pd.DataFrame | None:
    path = _cache_file(name)
    if not path.exists():
        return None
    df = pd.read_csv(path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    return df


def save_cache(df: pd.DataFrame, name: str) -> Path:
    path = _cache_file(name)
    df.to_csv(path)
    return path


# --------------------------------------------------------------------------
# Yahoo Finance
# --------------------------------------------------------------------------

def fetch_yahoo(
    symbol: str,
    interval: str = "5m",
    range_: str = "60d",
    tz: str = "America/New_York",
    refresh: bool = False,
    cache_name: str | None = None,
) -> pd.DataFrame:
    """OHLCV bars from the Yahoo chart endpoint.

    Columns: open, high, low, close, volume. Index is tz-aware in `tz`.
    """
    cache_name = cache_name or f"{symbol.replace('=', '_').replace('^', '')}_{interval}_{range_}.csv"
    if not refresh:
        cached = load_cache(cache_name)
        if cached is not None:
            return cached.tz_convert(tz)

    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?interval={interval}&range={range_}&includePrePost=true"
    )
    resp = requests.get(url, headers=_UA, timeout=30)
    resp.raise_for_status()
    payload = resp.json()["chart"]["result"][0]

    quote = payload["indicators"]["quote"][0]
    df = pd.DataFrame(
        {
            "open": quote["open"],
            "high": quote["high"],
            "low": quote["low"],
            "close": quote["close"],
            "volume": quote.get("volume"),
        },
        index=pd.to_datetime(payload["timestamp"], unit="s", utc=True),
    )
    df = df.dropna(subset=["open", "high", "low", "close"])
    df.index.name = "timestamp"

    save_cache(df, cache_name)
    return df.tz_convert(tz)


# --------------------------------------------------------------------------
# Binance (crypto)
# --------------------------------------------------------------------------

def fetch_binance(
    symbol: str = "BTCUSDT",
    interval: str = "1m",
    start: str = "2021-01-01",
    end: str | None = None,
    refresh: bool = False,
    cache_name: str | None = None,
    sleep: float = 0.12,
) -> pd.DataFrame:
    """1m+ klines from the public Binance API (no key, no account).

    Paginates backwards from `end` in 1000-bar pages until `start`.
    """
    cache_name = cache_name or f"{symbol}_{interval}_{start}_{end or 'now'}.csv"
    if not refresh:
        cached = load_cache(cache_name)
        if cached is not None:
            return cached

    base = "https://api.binance.com/api/v3/klines"
    start_ms = int(pd.Timestamp(start, tz="UTC").timestamp() * 1000)
    end_ms = int(pd.Timestamp(end, tz="UTC").timestamp() * 1000) if end else int(time.time() * 1000)

    rows: list[list] = []
    cursor = end_ms
    while cursor > start_ms:
        page = _binance_get(
            "/api/v3/klines",
            {"symbol": symbol, "interval": interval, "limit": 1000, "endTime": cursor},
        )
        if not page:
            break
        rows.extend(page)
        oldest = page[0][0]
        cursor = oldest - 1
        if len(page) < 1000:
            break
        time.sleep(sleep)

    df = pd.DataFrame(
        rows,
        columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades",
            "taker_base", "taker_quote", "ignore",
        ],
    )
    df = df[["open", "high", "low", "close", "volume", "trades"]]
    df.index = pd.to_datetime(pd.to_numeric(df.index.get_level_values(0) if False else df["open_time"]), unit="ms", utc=True)
    df = df.drop(columns="open_time")
    df = df.drop_duplicates().sort_index()
    df.index.name = "timestamp"
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close"])

    save_cache(df, cache_name)
    return df
