"""Mean reversion strategies — the opposite of trend following.

If trend following failed to beat holding on return, mean reversion is the
natural counter-test: buy when price is cheap relative to recent history, sell
when it reverts. Two flavors:

1. Z-score mean reversion: buy when price is `z_entry` stddevs below the N-bar
   mean, sell when it crosses back through the mean.
2. RSI mean reversion: buy when RSI < `rsi_low`, sell when RSI > `rsi_high`.

Both are causal, flat-only, long-only, 1x leverage. Nothing exotic.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class MeanRevConfig:
    window: int = 20           # lookback for mean/std
    z_entry: float = 2.0       # entry: price is z_entry stddevs below mean
    z_exit: float = 0.0        # exit: price crosses back through mean (0.0)
    rsi_low: float | None = None   # RSI entry threshold (if used instead of z)
    rsi_high: float | None = None  # RSI exit threshold
    stop_pct: float = 0.05     # hard stop, fraction of entry price
    fee_pct: float = 0.001       # per side
    slippage_pct: float = 0.0005 # per side
    side: str = "long"         # long only
    max_leverage: float = 1.0  # hard cap
    notional: float = 1.0      # fraction of equity per position


def _rsi(close: np.ndarray, period: int = 14) -> np.ndarray:
    delta = np.diff(close, prepend=close[0])
    up = np.where(delta > 0, delta, 0.0)
    down = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(up).ewm(alpha=1 / period, adjust=False).mean().to_numpy()
    roll_down = pd.Series(down).ewm(alpha=1 / period, adjust=False).mean().to_numpy()
    rs = roll_up / np.where(roll_down == 0, np.inf, roll_down)
    return 100 - (100 / (1 + rs))


def run_mean_reversion(df: pd.DataFrame, cfg: MeanRevConfig):
    o = df["open"].to_numpy()
    h = df["high"].to_numpy()
    l = df["low"].to_numpy()
    c = df["close"].to_numpy()
    n = len(c)
    if n < cfg.window + 5:
        raise ValueError("not enough bars")

    roll_mean = pd.Series(c).rolling(cfg.window).mean().shift(1).to_numpy()
    roll_std = pd.Series(c).rolling(cfg.window).std().shift(1).to_numpy()
    rsi = _rsi(c, 14)

    cash = 1.0
    units = 0.0
    side_pos = 0
    entry_price = np.nan
    entry_i = 0
    equity = np.empty(n)
    trades = []
    fees_paid = 0.0

    for i in range(n):
        if side_pos != 0:
            px = c[i]
            exit_px = None
            reason = None
            if side_pos == 1:
                if not np.isnan(roll_mean[i]) and px >= roll_mean[i]:
                    exit_px = px
                    reason = "mean_revert"
                elif cfg.stop_pct > 0 and px <= entry_price * (1 - cfg.stop_pct):
                    exit_px = entry_price * (1 - cfg.stop_pct)
                    reason = "stop"
                elif cfg.rsi_high is not None and rsi[i] >= cfg.rsi_high:
                    exit_px = px
                    reason = "rsi_high"
            if exit_px is not None:
                slip = cfg.slippage_pct
                fill = exit_px * (1 - slip) if side_pos == 1 else exit_px * (1 + slip)
                fee = abs(units) * fill * cfg.fee_pct
                cash += units * fill - fee
                fees_paid += fee
                trades.append(
                    {
                        "entry_time": df.index[entry_i],
                        "exit_time": df.index[i],
                        "entry": entry_price,
                        "exit": fill,
                        "bars_held": i - entry_i,
                        "return": (fill - entry_price) * units / max(abs(entry_price * units), 1e-12),
                        "reason": reason,
                    }
                )
                units = 0.0
                side_pos = 0

        if side_pos == 0 and i + 1 < n:
            take = False
            if cfg.rsi_low is not None and not np.isnan(rsi[i]) and rsi[i] <= cfg.rsi_low:
                take = True
            elif cfg.z_entry > 0 and not np.isnan(roll_std[i]) and roll_std[i] > 0:
                z = (c[i] - roll_mean[i]) / roll_std[i]
                if z <= -cfg.z_entry:
                    take = True

            if take:
                slip = cfg.slippage_pct
                fill = o[i + 1] * (1 + slip) if side_pos == 1 else o[i + 1] * (1 - slip)
                fee = abs(fill) * cfg.fee_pct * 1.0  # fee on entry notional fraction
                equity_now = cash + units * c[i]
                notional = min(equity_now * cfg.notional if hasattr(cfg, 'notional') else equity_now, equity_now * cfg.max_leverage)
                units = notional / fill
                cash -= units * fill + fee
                fees_paid += fee
                side_pos = 1
                entry_price = fill
                entry_i = i + 1

        equity[i] = cash + units * c[i]

    eq = pd.Series(equity, index=df.index, name="equity")
    tdf = pd.DataFrame(trades)
    return eq, tdf
