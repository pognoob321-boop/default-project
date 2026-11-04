"""Trend-following (time-series momentum) on free crypto data.

Why this family: it is the only rule-based strategy family with strong
cross-market academic evidence (Moskowitz, Ooi & Pedersen 2012; Hurst, Ooi &
Pedersen 2017, "A Century of Evidence on Trend-Following Investing"). It also
trades far less often than an intraday breakout, so retail fees do not
dominate the result.

Rules (classic Donchian / turtle, made causal):
  * entry  : close breaks the prior N-bar high (long) or prior N-bar low (short)
  * exit   : close breaks the prior M-bar opposite channel, or an ATR stop
  * fill   : at the NEXT bar's open, never at the signal bar's close
  * costs  : taker fee on both sides + slippage on both sides
  * sizing : fixed notional fraction of equity (no leverage by default)

Everything here is measured against buy-and-hold on the same bars. A strategy
that returns less than holding, with more drawdown, is not a strategy.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class TrendConfig:
    entry_len: int = 20
    exit_len: int = 10
    atr_len: int = 14
    atr_stop_mult: float = 0.0   # 0 = no ATR stop (channel exit only)
    side: str = "both"           # "long" | "both"
    fee_pct: float = 0.001       # per side
    slippage_pct: float = 0.0005 # per side
    notional: float = 1.0        # fraction of equity per position
    # --- enhancements (each one must earn its place walk-forward) ---
    regime_len: int = 0          # only trade long above this SMA
    regime_slope: bool = False   # ...and only if the SMA is rising
    vol_target: float = 0.0      # risk per trade as a fraction of equity (0=off)
    max_leverage: float = 1.0   # hard cap on notional/equity (keep it comparable to holding)
    trailing_atr: float = 0.0    # Chandelier trail (0=off)
    time_stop_bars: int = 0      # force an exit after N bars (0=off)
    cost_filter_mult: float = 0.0  # skip trades whose ATR move < mult * round-trip cost
    dd_cut: float = 0.0          # cut notional when equity drawdown exceeds this


@dataclass
class TrendResult:
    equity: pd.Series
    trades: pd.DataFrame
    bars: int
    exposure: float
    fees_paid: float
    avg_leverage: float = 0.0


def _true_range(high, low, close):
    prev_close = np.concatenate([[close[0]], close[:-1]])
    return np.maximum(high - low, np.maximum(np.abs(high - prev_close), np.abs(low - prev_close)))


def or_channel(entry_high, entry_low, side: int) -> float:
    """The channel level the position is measured against (for sizing)."""
    if side == 1:
        return float(entry_high) if not np.isnan(entry_high) else float("nan")
    return float(entry_low) if not np.isnan(entry_low) else float("nan")


def run_trend(df: pd.DataFrame, cfg: TrendConfig) -> TrendResult:
    """Simulate the strategy on a OHLCV frame.

    Causal order, per bar i:
      A. fill a pending exit at THIS bar's open
      B. fill a pending entry at THIS bar's open
      C. check the resting ATR stop against this bar's range
      D. mark equity at this bar's close
      E. generate the signal for bar i+1 (channel exits and entries)
    """
    o = df["open"].to_numpy()
    h = df["high"].to_numpy()
    low = df["low"].to_numpy()
    c = df["close"].to_numpy()
    n = len(df)
    if n < cfg.entry_len + 5:
        raise ValueError("not enough bars")

    # channels EXCLUDE the current bar (shift(1)) -> no lookahead
    entry_high = pd.Series(h).rolling(cfg.entry_len).max().shift(1).to_numpy()
    entry_low = pd.Series(low).rolling(cfg.entry_len).min().shift(1).to_numpy()
    exit_high = pd.Series(h).rolling(cfg.exit_len).max().shift(1).to_numpy()
    exit_low = pd.Series(low).rolling(cfg.exit_len).min().shift(1).to_numpy()
    atr = pd.Series(_true_range(h, low, c)).rolling(cfg.atr_len).mean().shift(1).to_numpy()
    sma = (
        pd.Series(c).rolling(cfg.regime_len).mean().shift(1).to_numpy()
        if cfg.regime_len > 0
        else None
    )
    sma_slope = (
        pd.Series(c).rolling(cfg.regime_len).mean().diff(5).shift(1).to_numpy()
        if (cfg.regime_len > 0 and cfg.regime_slope)
        else None
    )
    round_trip_cost = 2 * (cfg.fee_pct + cfg.slippage_pct)

    cash = 1.0
    units = 0.0
    side = 0
    stop = np.nan
    entry_price = np.nan
    entry_i = 0
    pending_exit: str | None = None
    pending_entry = 0
    run_high = -np.inf
    run_low = np.inf
    peak_equity = 1.0
    equity = np.empty(n)
    trades: list[dict] = []
    fees_paid = 0.0
    in_market = 0
    leverage_sum = 0.0
    leverage_n = 0

    def close_position(px: float, when: int, reason: str) -> None:
        nonlocal cash, units, side, stop, fees_paid
        slip = cfg.slippage_pct
        fill = px * (1 - slip) if side == 1 else px * (1 + slip)
        # fee is a fraction of the POSITION notional, not of the price
        fee = abs(units) * fill * cfg.fee_pct
        cash += units * fill - fee
        fees_paid += fee
        pnl = (fill - entry_price) * units - fee
        trades.append(
            {
                "entry_time": df.index[entry_i],
                "exit_time": df.index[when],
                "side": "long" if side == 1 else "short",
                "entry": entry_price,
                "exit": fill,
                "bars_held": when - entry_i,
                "return": pnl / max(abs(entry_price * units), 1e-12),
                "reason": reason,
            }
        )
        units = 0.0
        side = 0
        stop = np.nan

    for i in range(n):
        # A. pending exit fills at this bar's open
        if pending_exit is not None and side != 0:
            close_position(o[i], i, pending_exit)
            pending_exit = None

        # B. pending entry fills at this bar's open
        if pending_entry != 0 and side == 0 and i > 0:
            ns = pending_entry
            pending_entry = 0
            slip = cfg.slippage_pct
            fill = o[i] * (1 + slip) if ns == 1 else o[i] * (1 - slip)
            # size off EQUITY, never off cash (cash goes negative when long)
            equity_now = cash + units * c[i]
            notional = equity_now * cfg.notional
            if cfg.vol_target > 0 and not np.isnan(atr[i]) and atr[i] > 0:
                # risk-based sizing: stop distance = ATR stop, or the channel distance
                stop_dist = (
                    cfg.atr_stop_mult * atr[i]
                    if cfg.atr_stop_mult > 0
                    else abs(fill - (or_channel(entry_high[i], entry_low[i], side=ns)))
                )
                stop_pct = stop_dist / fill
                if stop_pct > 0:
                    notional = equity_now * (cfg.vol_target / stop_pct)
            # hard leverage cap: without it, vol-target sizing quietly turns a
            # 1x strategy into a 10-50x one and the comparison to holding is rigged
            if cfg.max_leverage > 0:
                notional = min(notional, equity_now * cfg.max_leverage)
            if cfg.dd_cut > 0:
                peak = max(peak_equity, equity_now)
                peak_equity = peak
                dd = 1.0 - equity_now / peak if peak > 0 else 0.0
                if dd >= cfg.dd_cut:
                    notional *= 0.5
            fee = notional * cfg.fee_pct
            units = notional / fill * ns
            cash -= units * fill + fee
            fees_paid += fee
            if equity_now > 0:
                leverage_sum += notional / equity_now
                leverage_n += 1
            side = ns
            entry_price = fill
            entry_i = i
            run_high = h[i]
            run_low = low[i]
            if cfg.atr_stop_mult > 0 and not np.isnan(atr[i]):
                stop = fill - ns * cfg.atr_stop_mult * atr[i]

        # C. resting ATR stop, live from the entry fill (+ trailing update)
        if side != 0:
            run_high = max(run_high, h[i])
            run_low = min(run_low, low[i])
            if cfg.trailing_atr > 0 and not np.isnan(atr[i]):
                trail = run_high - cfg.trailing_atr * atr[i] if side == 1 else run_low + cfg.trailing_atr * atr[i]
                stop = trail if np.isnan(stop) else (
                    max(stop, trail) if side == 1 else min(stop, trail)
                )
            if not np.isnan(stop):
                hit = low[i] <= stop if side == 1 else high[i] >= stop
                if hit:
                    px = min(stop, o[i]) if side == 1 else max(stop, o[i])
                    close_position(px, i, "atr_stop")

        # D. equity at this bar's close
        if side != 0:
            in_market += 1
        equity[i] = cash + units * c[i]

        # E. signals for the next bar
        if side != 0 and pending_exit is None:
            if cfg.time_stop_bars > 0 and (i - entry_i) >= cfg.time_stop_bars:
                pending_exit = "time"
            elif side == 1 and not np.isnan(exit_low[i]) and c[i] < exit_low[i]:
                pending_exit = "channel"
            elif side == -1 and not np.isnan(exit_high[i]) and c[i] > exit_high[i]:
                pending_exit = "channel"
        if side == 0 and pending_entry == 0 and i + 1 < n:
            want_long = not np.isnan(entry_high[i]) and c[i] > entry_high[i]
            want_short = not np.isnan(entry_low[i]) and c[i] < entry_low[i]
            # higher-timeframe regime filter: only trade with the trend
            if cfg.regime_len > 0 and not np.isnan(sma[i]):
                if c[i] < sma[i]:
                    want_long = False
                if cfg.regime_slope and not np.isnan(sma_slope[i]) and sma_slope[i] <= 0:
                    want_long = False
                    want_short = False
            # cost-aware filter: never take a trade whose expected move is
            # smaller than a multiple of the round-trip cost
            if cfg.cost_filter_mult > 0 and not np.isnan(atr[i]) and c[i] > 0:
                if (atr[i] / c[i]) < cfg.cost_filter_mult * round_trip_cost:
                    want_long = want_short = False
            if want_long and cfg.side in ("long", "both"):
                pending_entry = 1
            elif want_short and cfg.side == "both":
                pending_entry = -1

    eq = pd.Series(equity, index=df.index, name="equity")
    tdf = pd.DataFrame(trades)
    return TrendResult(
        equity=eq,
        trades=tdf,
        bars=n,
        exposure=in_market / n if n else 0.0,
        fees_paid=fees_paid,
        avg_leverage=leverage_sum / leverage_n if leverage_n else 0.0,
    )


def buy_and_hold(df: pd.DataFrame, fee_pct: float = 0.001, slippage_pct: float = 0.0005) -> pd.Series:
    """The benchmark: buy at the first open, hold to the last close, pay costs.

    The fee is a fraction of the account, not of the price: a 1.0 account
    paying 0.1% loses 0.001, not 4.29.
    """
    o = df["open"].to_numpy()
    c = df["close"].to_numpy()
    entry = o[0] * (1 + slippage_pct)
    units = (1.0 - fee_pct) / entry
    return pd.Series(units * c, index=df.index, name="buy_and_hold")
