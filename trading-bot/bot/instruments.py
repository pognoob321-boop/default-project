"""Per-instrument cost defaults.

The cost model is:  cost_dollars = commission_per_rt + slippage_points * point_value
A single hard-coded model silently gives every symbol the economics of ES, so
costs are looked up per instrument instead.

Verified figures (round-turn, retail):
  ES   $4.20 commission, 1 tick (0.25 pt) slippage, $50/point
  MES  $2.10 commission, 1 tick slippage, $5/point
  NQ   $4.20 commission, 1 tick slippage, $20/point
  MNQ  $1.40 commission, 1 tick slippage, $2/point
  Equities (Alpaca/most brokers): $0 commission, 1 cent slippage, $1/point
"""

from __future__ import annotations

FUTURES = {
    "ES=F": dict(commission_per_rt=4.20, slippage_points=0.25, point_value=50.0),
    "MES=F": dict(commission_per_rt=2.10, slippage_points=0.25, point_value=5.0),
    "NQ=F": dict(commission_per_rt=4.20, slippage_points=0.25, point_value=20.0),
    "MNQ=F": dict(commission_per_rt=1.40, slippage_points=0.25, point_value=2.0),
    "YM=F": dict(commission_per_rt=4.20, slippage_points=0.25, point_value=5.0),
}

EQUITIES = dict(commission_per_rt=0.0, slippage_points=0.01, point_value=1.0)

# Crypto: percent-based costs. Binance spot taker 0.10% per side, ~0.05%
# slippage per side on a 1-minute market order.
CRYPTO = dict(
    commission_per_rt=0.0,
    slippage_points=0.0,
    point_value=1.0,
    fee_pct=0.001,
    slippage_pct=0.0005,
)


def costs_for(symbol: str) -> dict:
    """Cost defaults for a symbol; equities default for anything unknown."""
    if symbol.upper().endswith(("USDT", "USDC", "BUSD")):
        return dict(CRYPTO)
    return dict(FUTURES.get(symbol, EQUITIES))
