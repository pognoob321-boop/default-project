"""Opening Range Breakout (ORB) strategy — causal, honest fills.

Rules come from the repo's own research page (wiki/research/orb-trading-strategy.md).

Correctness rules enforced here (each one was a real bug in v1):

  * No lookahead. A decision on bar N may only use bars up to N.
  * A signal is generated when a bar CLOSES beyond the range, but the fill
    happens at the NEXT bar's OPEN - you cannot trade a price you only learn
    at the close of that bar.
  * Stops can be gapped through. If the next open is already past the stop,
    the exit is the open, so a loss CAN exceed 1R. v1 filled every stop
    exactly at the stop, which hid all tail risk.
  * VWAP is measured from the session open, not from midnight, so overnight
    futures volume cannot drag the baseline.
  * The "confirmation candle" is a real filter: entries are only evaluated on
    bars aligned to `confirm_minutes` from the session open.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class ORBConfig:
    session_start: str = "09:30"       # exchange local time
    or_minutes: int = 30               # opening-range window length
    confirm_minutes: int = 5           # confirmation candle size
    stop_mode: str = "midpoint"        # "midpoint" | "opposite" | "range"
    stop_mult: float = 2.0             # for stop_mode="range": stop = entry -/+ mult*width
    target_r: float = 2.0              # target in R
    target_mode: str = "r"             # "r" | "measured"
    vwap_filter: bool = True
    index_confirm: bool = False
    flat_by: str = "11:30"             # time stop: flat at this bar's open
    max_trades_per_day: int = 1
    min_or_width: float | None = None  # skip sessions whose range is too tight
    max_or_width: float | None = None  # ...or too wide
    min_or_width_pct: float | None = None   # width as a fraction of price
    max_or_width_pct: float | None = None
    gap_filter_pct: float | None = None
    # execution costs, used by the backtest summary (not by the signal logic)
    commission_per_rt: float = 0.0   # round-turn commission in dollars
    slippage_points: float = 0.0     # slippage in price points, round trip
    point_value: float = 1.0         # dollars per point
    # percent-based costs (crypto): fee and slippage as a fraction of price
    fee_pct: float = 0.0             # taker fee per side
    slippage_pct: float = 0.0        # slippage per side
    extra: dict = field(default_factory=dict)


@dataclass
class Trade:
    session: object
    side: str
    signal_time: pd.Timestamp
    entry_time: pd.Timestamp
    entry: float
    stop: float
    target: float
    exit_time: pd.Timestamp
    exit: float
    r: float
    reason: str
    or_high: float
    or_low: float


def session_vwap(bars: pd.DataFrame, start_time: pd.Timestamp | None = None) -> pd.Series:
    """Cumulative VWAP, measured from the session open (not from midnight)."""
    if start_time is not None:
        bars = bars[bars.index.time >= start_time]
    pv = bars["close"] * bars["volume"]
    return pv.cumsum() / bars["volume"].cumsum()


def split_sessions(df: pd.DataFrame) -> dict:
    """Group bars by calendar date in the frame's own timezone."""
    return {day: grp.sort_index() for day, grp in df.groupby(df.index.date)}


def _levels(bars: pd.DataFrame, cfg: ORBConfig):
    start = pd.Timestamp(cfg.session_start).time()
    end = (pd.Timestamp(cfg.session_start) + pd.Timedelta(minutes=cfg.or_minutes)).time()
    opening = bars[(bars.index.time >= start) & (bars.index.time < end)]
    if opening.empty:
        return None
    return float(opening["high"].max()), float(opening["low"].min())


def _minutes_from_open(t: pd.Timestamp, cfg: ORBConfig) -> float:
    open_ts = pd.Timestamp(t.normalize() + pd.Timedelta(
        hours=pd.Timestamp(cfg.session_start).hour,
        minutes=pd.Timestamp(cfg.session_start).minute,
        seconds=pd.Timestamp(cfg.session_start).second,
    ))
    return (t - open_ts).total_seconds() / 60.0


def _index_trend_up(idx_bars: pd.DataFrame, t: pd.Timestamp, cfg: ORBConfig) -> bool | None:
    """Index direction known AT the decision time (never the day's last bar)."""
    start = pd.Timestamp(cfg.session_start).time()
    upto = idx_bars[(idx_bars.index.time >= start) & (idx_bars.index <= t)]
    if upto.empty:
        return None
    vwap = session_vwap(upto)
    last_close = float(upto["close"].iloc[-1])
    last_vwap = float(vwap.iloc[-1])
    return last_close > last_vwap


def generate_trades(
    df: pd.DataFrame,
    cfg: ORBConfig,
    index_by_session: dict | None = None,
) -> list[Trade]:
    """Walk each session bar-by-bar and simulate the ORB honestly.

    Uses numpy arrays per session (the pure-pandas version was ~30x slower and
    could not handle multi-million-bar crypto archives).
    """
    trades: list[Trade] = []
    sessions = split_sessions(df)

    start_time = pd.Timestamp(cfg.session_start).time()
    or_end = (pd.Timestamp(cfg.session_start) + pd.Timedelta(minutes=cfg.or_minutes)).time()
    flat_t = pd.Timestamp(cfg.flat_by).time()

    for day, bars in sessions.items():
        levels = _levels(bars, cfg)
        if levels is None:
            continue
        or_high, or_low = levels
        or_width = or_high - or_low
        if or_width <= 0:
            continue
        if cfg.min_or_width is not None and or_width < cfg.min_or_width:
            continue
        if cfg.max_or_width is not None and or_width > cfg.max_or_width:
            continue

        idx = bars.index
        n = len(bars)
        if n < 3:
            continue
        o = bars["open"].to_numpy()
        h = bars["high"].to_numpy()
        low = bars["low"].to_numpy()
        c = bars["close"].to_numpy()
        v = bars["volume"].to_numpy()
        times = idx.time

        # session-anchored VWAP (from the session open, not midnight)
        vwap = np.full(n, np.nan)
        rth = np.array([t >= start_time for t in times])
        if rth.any():
            idx_rth = np.flatnonzero(rth)
            pv = c[idx_rth] * v[idx_rth]
            cum_pv = np.cumsum(pv)
            cum_v = np.cumsum(v[idx_rth])
            with np.errstate(invalid="ignore", divide="ignore"):
                vwap[idx_rth] = cum_pv / cum_v

        # opening-range bars
        in_or = np.array([start_time <= t < or_end for t in times])
        if not in_or.any():
            continue
        or_high = float(h[in_or].max())
        or_low = float(low[in_or].min())
        or_width = or_high - or_low
        if or_width <= 0:
            continue
        if cfg.min_or_width is not None and or_width < cfg.min_or_width:
            continue
        if cfg.max_or_width is not None and or_width > cfg.max_or_width:
            continue
        ref_price = float(c[in_or][0])
        if cfg.min_or_width_pct is not None and or_width < cfg.min_or_width_pct * ref_price:
            continue
        if cfg.max_or_width_pct is not None and or_width > cfg.max_or_width_pct * ref_price:
            continue

        mid = (or_high + or_low) / 2
        stop_level = or_low if cfg.stop_mode == "opposite" else mid
        stop_short = or_high if cfg.stop_mode == "opposite" else mid

        taken = 0
        for i in range(n):
            t = times[i]
            if t < or_end:
                continue
            if t >= flat_t:
                break
            if taken >= cfg.max_trades_per_day:
                break
            if cfg.confirm_minutes > 0:
                mins = _minutes_from_open(idx[i], cfg)
                if abs(mins % cfg.confirm_minutes) > 1e-6:
                    continue

            close = float(c[i])
            vw = vwap[i]
            above_vwap = (not np.isnan(vw)) and close > float(vw)

            side = None
            if close > or_high and (not cfg.vwap_filter or above_vwap):
                side = "long"
            elif close < or_low and (not cfg.vwap_filter or not above_vwap):
                side = "short"
            if side is None:
                continue

            if cfg.index_confirm and index_by_session is not None:
                idx_bars = index_by_session.get(day)
                if idx_bars is None or idx_bars.empty:
                    continue
                trend = _index_trend_up(idx_bars, idx[i], cfg)
                if trend is None:
                    continue
                if side == "long" and not trend:
                    continue
                if side == "short" and trend:
                    continue

            # fill at the NEXT bar's open
            if i + 1 >= n:
                break
            entry = float(o[i + 1])

            if side == "long":
                if cfg.stop_mode == "range":
                    stop = entry - cfg.stop_mult * or_width
                else:
                    stop = stop_level
                risk = entry - stop
                if risk <= 0:
                    continue
                target = entry + or_width if cfg.target_mode == "measured" else entry + cfg.target_r * risk
            else:
                if cfg.stop_mode == "range":
                    stop = entry + cfg.stop_mult * or_width
                else:
                    stop = stop_short
                risk = stop - entry
                if risk <= 0:
                    continue
                target = entry - or_width if cfg.target_mode == "measured" else entry - cfg.target_r * risk

            exit_price, exit_time, reason = None, None, None
            for j in range(i + 1, n):
                tj = times[j]
                if tj >= flat_t:
                    exit_price, exit_time, reason = float(o[j]), idx[j], "time"
                    break
                if side == "long":
                    if low[j] <= stop:
                        exit_price = min(stop, float(o[j]))
                        exit_time, reason = idx[j], "stop"
                        break
                    if h[j] >= target:
                        exit_price = target
                        exit_time, reason = idx[j], "target"
                        break
                else:
                    if h[j] >= stop:
                        exit_price = max(stop, float(o[j]))
                        exit_time, reason = idx[j], "stop"
                        break
                    if low[j] <= target:
                        exit_price = target
                        exit_time, reason = idx[j], "target"
                        break
            if exit_price is None:
                exit_price, exit_time, reason = float(c[-1]), idx[-1], "time"

            r = (exit_price - entry) / risk if side == "long" else (entry - exit_price) / risk

            trades.append(
                Trade(
                    session=day,
                    side=side,
                    signal_time=idx[i],
                    entry_time=idx[i + 1],
                    entry=entry,
                    stop=stop,
                    target=target,
                    exit_time=exit_time,
                    exit=exit_price,
                    r=float(r),
                    reason=reason,
                    or_high=or_high,
                    or_low=or_low,
                )
            )
            taken += 1
    return trades
