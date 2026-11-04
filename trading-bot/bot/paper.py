"""Free paper-trading engine.

Runs a strategy forward on live free data with simulated fills, so the bot can
be tested for weeks before any real money exists. No broker, no account, no
KYC, no cost.

Data source : Binance public REST klines (no key). 24/7, 1-minute candles.
Fills       : signal on a CLOSED candle -> market fill at the NEXT candle's
              open, plus slippage, plus fees on BOTH sides. Stops can be
              gapped through (exit at the open, loss can exceed 1R).
State       : data/paper_state.json (position, session levels)
Journal     : data/paper_journal.csv (one row per closed trade)

Run:
    python scripts/run_paper.py --symbol BTCUSDT --session-start 00:00
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import requests

from . import data

STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "paper_state.json"
JOURNAL_PATH = Path(__file__).resolve().parent.parent / "data" / "paper_journal.csv"
DATA_DIR = STATE_PATH.parent


@dataclass
class PaperConfig:
    symbol: str = "BTCUSDT"
    interval: str = "1m"          # kline interval
    session_start: str = "00:00"  # UTC session boundary (crypto = 00:00 UTC)
    or_minutes: int = 15          # opening-range window
    stop_mode: str = "midpoint"
    target_r: float = 2.0
    target_mode: str = "r"          # "r" | "measured"
    vwap_filter: bool = True
    flat_by: str = "23:50"        # time stop, UTC
    taker_fee: float = 0.001      # Binance spot taker fee, per side
    slippage_pct: float = 0.0005  # slippage on each fill
    max_trades_per_day: int = 1
    poll_seconds: int = 15


def fetch_recent(symbol: str, interval: str, limit: int = 1000) -> pd.DataFrame:
    """Closed candles only - the last kline from Binance is still forming.

    Paginates backwards so the returned window can cover a full session
    (needed for a session-anchored VWAP). Binance caps a page at 1000.
    """
    url = "https://api.binance.com/api/v3/klines"
    frames = []
    end_time = None
    remaining = limit + 1  # +1 because the last kline is still forming
    while remaining > 0:
        params = {"symbol": symbol, "interval": interval, "limit": min(1000, remaining)}
        if end_time is not None:
            params["endTime"] = end_time
        rows = data._binance_get("/api/v3/klines", params)
        if not rows:
            break
        frames.append(rows)
        remaining -= len(rows)
        end_time = rows[0][0] - 1
        if len(rows) < 1000:
            break
        time.sleep(0.1)

    rows = [row for page in frames for row in page]
    df = pd.DataFrame(
        rows,
        columns=["open_time", "open", "high", "low", "close", "volume",
                 "close_time", "qvol", "trades", "tb", "tq", "ignore"],
    )
    df.index = pd.to_datetime(pd.to_numeric(df["open_time"]), unit="ms", utc=True)
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df = df.iloc[:-1]  # drop the still-forming candle
    return df


class PaperEngine:
    def __init__(self, cfg: PaperConfig):
        self.cfg = cfg
        self.state = {
            "session": None,
            "or_high": None,
            "or_low": None,
            "or_closed": False,
            "trades_today": 0,
            "position": None,
        }
        if STATE_PATH.exists():
            try:
                self.state.update(json.loads(STATE_PATH.read_text()))
            except Exception:
                pass

    def save(self) -> None:
        STATE_PATH.write_text(json.dumps(self.state, indent=2, default=str))

    def log_trade(self, row: dict) -> None:
        exists = JOURNAL_PATH.exists()
        pd.DataFrame([row]).to_csv(JOURNAL_PATH, mode="a", header=not exists, index=False)

    # ------------------------------------------------------------------
    def on_bar(self, bar: pd.Series, bar_time: pd.Timestamp) -> None:
        cfg = self.cfg
        st = self.state
        session = bar_time.date()

        if st["session"] != session:
            # a position open across the session boundary is closed out, not dropped
            pos = st.get("position")
            if pos and pos.get("filled"):
                self.close_position(pos, bar["open"], bar_time, "session")
            st.update(session=session, or_high=None, or_low=None,
                      or_closed=False, trades_today=0, position=None)

        start = pd.Timestamp(cfg.session_start).time()
        end = (pd.Timestamp(cfg.session_start) + pd.Timedelta(minutes=cfg.or_minutes)).time()
        t = bar_time.time()
        flat_t = pd.Timestamp(cfg.flat_by).time()

        # --- manage an open position FIRST (also during the OR window) ---
        pos = st["position"]
        if pos and not pos.get("filled"):
            # fill at this bar's open (the bar after the signal candle)
            slip = cfg.slippage_pct
            entry = bar["open"] * (1 - slip) if pos["side"] == "long" else bar["open"] * (1 + slip)
            if pos["side"] == "long":
                risk = entry - pos["stop"]
            else:
                risk = pos["stop"] - entry
            pos["entry"] = entry
            pos["fill_fee"] = abs(entry) * cfg.taker_fee
            if risk <= 0:
                # gapped through the stop: fill anyway, exit immediately at the open
                pos["risk"] = abs(risk) or 1e-9
                pos["filled"] = True
                pos["fill_time"] = str(bar_time)
                self.close_position(pos, entry, bar_time, "gap_stop")
                return
            pos["risk"] = risk
            pos["filled"] = True
            pos["fill_time"] = str(bar_time)
            if cfg.target_mode == "r":
                pos["target"] = (
                    entry + cfg.target_r * risk if pos["side"] == "long"
                    else entry - cfg.target_r * risk
                )
            self.save()
            return

        if pos:
            if t >= flat_t:
                self.close_position(pos, bar["open"], bar_time, "time")
                return
            if pos["side"] == "long":
                if bar["low"] <= pos["stop"]:
                    exit_price = min(pos["stop"], bar["open"])
                    self.close_position(pos, exit_price, bar_time, "stop")
                    return
                if bar["high"] >= pos["target"]:
                    self.close_position(pos, pos["target"], bar_time, "target")
                    return
            else:
                if bar["high"] >= pos["stop"]:
                    exit_price = max(pos["stop"], bar["open"])
                    self.close_position(pos, exit_price, bar_time, "stop")
                    return
                if bar["low"] <= pos["target"]:
                    self.close_position(pos, pos["target"], bar_time, "target")
                    return
            return

        # --- opening range accumulation ---
        if start <= t < end:
            st["or_high"] = bar["high"] if st["or_high"] is None else max(st["or_high"], bar["high"])
            st["or_low"] = bar["low"] if st["or_low"] is None else min(st["or_low"], bar["low"])
            return

        if not st["or_closed"]:
            st["or_closed"] = True
            self.save()

        if t >= flat_t:
            return
        if st["trades_today"] >= cfg.max_trades_per_day:
            return
        if st["or_high"] is None or st["or_low"] is None:
            return

        # --- entry signal (on a closed candle) ---
        close = bar["close"]
        above_vwap = close > bar["_vwap"]
        side = None
        if close > st["or_high"] and (not cfg.vwap_filter or above_vwap):
            side = "long"
        elif close < st["or_low"] and (not cfg.vwap_filter or not above_vwap):
            side = "short"
        if side is None:
            return

        mid = (st["or_high"] + st["or_low"]) / 2
        if side == "long":
            stop = st["or_low"] if cfg.stop_mode == "opposite" else mid
        else:
            stop = st["or_high"] if cfg.stop_mode == "opposite" else mid

        st["position"] = {
            "side": side,
            "signal_price": close,
            "stop": stop,
            "target": close,          # re-based on the actual fill
            "risk": abs(close - stop) or 1e-9,
            "signal_time": str(bar_time),
            "filled": False,
        }
        st["trades_today"] += 1
        self.save()

    def close_position(self, pos: dict, price: float, when: pd.Timestamp, reason: str) -> None:
        cfg = self.cfg
        entry = pos["entry"]
        slip = cfg.slippage_pct
        fill = price * (1 - slip) if pos["side"] == "long" else price * (1 + slip)
        gross = (fill - entry) if pos["side"] == "long" else (entry - fill)
        # fees on BOTH sides
        fee = abs(entry) * cfg.taker_fee + abs(fill) * cfg.taker_fee
        net = gross - fee          # in price units
        r = net / pos["risk"]      # R = net P&L / risk per unit
        self.log_trade(
            {
                "symbol": cfg.symbol,
                "session": str(self.state["session"]),
                "side": pos["side"],
                "signal_time": pos["signal_time"],
                "fill_time": pos.get("fill_time", ""),
                "exit_time": str(when),
                "entry": entry,
                "exit_price": fill,
                "stop": pos["stop"],
                "target": pos["target"],
                "reason": reason,
                "net_pct": round((net / entry) * 100, 4),
                "r": round(r, 4),
            }
        )
        self.state["position"] = None
        self.save()


def run_forever(cfg: PaperConfig, max_bars: int | None = None, bars: int = 1000) -> None:
    engine = PaperEngine(cfg)
    seen: set[pd.Timestamp] = set()
    processed = 0
    print(f"paper bot started | {cfg.symbol} {cfg.interval} | OR={cfg.or_minutes}m "
          f"target={cfg.target_r}R stop={cfg.stop_mode} fee={cfg.taker_fee*100:.2f}%/side")
    while True:
        df = fetch_recent(cfg.symbol, cfg.interval, limit=bars)
        # session-anchored VWAP: cumulative from the session open, per day
        pv = df["close"] * df["volume"]
        df["_vwap"] = (
            pv.groupby(df.index.date).cumsum() / df["volume"].groupby(df.index.date).cumsum()
        )
        for ts, bar in df.iterrows():
            if ts in seen:
                continue
            seen.add(ts)
            engine.on_bar(bar, ts)
            processed += 1
        pos = engine.state["position"]
        print(f"[{pd.Timestamp.now('UTC'):%H:%M:%S}] bars={processed} "
              f"session={engine.state['session']} "
              f"OR=[{engine.state['or_low']}, {engine.state['or_high']}] "
              f"pos={pos['side'] if pos else 'flat'}")
        if max_bars and processed >= max_bars:
            break
        time.sleep(cfg.poll_seconds)
