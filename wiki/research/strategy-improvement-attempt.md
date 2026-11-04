# Strategy Improvement Attempt — What Actually Improved

> **Status:** Research page | **Date:** 2026-10-22 | **Data:** SPY 30y daily (7,546 bars, Yahoo, free) + BTCUSDT 9y (4.79M 1m bars, Binance archive, free)
> **Code:** `trading-bot/bot/trend.py` (enhanced engine), `bot/walkforward.py` (protocol), `bot/metrics.py`, `scripts/walkforward.py`, `scripts/compare_fixed.py`

## The Brief

Improve the trading strategy as much as possible. The trap: "improving" on the same data you test on is how bots lie. So the protocol was fixed in advance:

- **Add real ingredients, not parameter tweaks:** volatility-target sizing, a higher-timeframe regime filter (200-day SMA + slope), ATR stops, Chandelier trailing stops, time stops, a cost-aware entry filter (skip trades whose ATR move is smaller than a multiple of round-trip cost), and drawdown de-risking.
- **Measure with walk-forward:** pick parameters on 5 years, trade the *next* untouched year, roll forward. 25 folds on SPY, 4 on BTC. Report the stitched out-of-sample curve against buy-and-hold.
- **Cap leverage at 1x** so the comparison with holding is honest.
- **Require the gain on both venues.**

## What Was Built

| Ingredient | Purpose | Verdict |
|---|---|---|
| Vol-target sizing (risk-based position size) | equalize risk per trade | **FAKE WIN — see below** |
| Regime filter (SMA 100/200 + slope) | only trade with the long-term trend | real on equities, **destructive on crypto** |
| ATR stop (2-3x) | exit on volatility, not a fixed level | **real improvement on equities** |
| Chandelier trailing stop | let winners run, cut losers | neutral-to-harmful |
| Time stop (250 bars) | free capital | neutral |
| Cost-aware entry filter | never take a trade smaller than the fee | logically sound, rarely binding |
| Drawdown de-risking (halve size past -15%) | survive your own drawdowns | neutral |
| Walk-forward framework | measure the *procedure*, not the luck | the most valuable piece |

## The Three Fake Wins

**1. A 316× out-of-sample return that was pure leverage.** Vol-target sizing with a tight stop implies 10-50× notional. The first walk-forward printed **+31,629%** over 30 years, beating holding's +491%. Capping notional at 1× (the same as holding) collapsed it to **+1.1×**. A hard `max_leverage` cap now sits in the engine, because a leverage-driven result is not a strategy result.

**2. "9 of 32 configs beat holding" is a post-hoc number.** It counts the best-looking configs *after* seeing the test data. The disciplined version — pick by in-sample, then evaluate out-of-sample — produced: best in-sample config (entry 100 / exit 20 long, in-sample Sharpe 1.16) → out-of-sample Sharpe 1.11 vs holding's 1.60. It lost.

**3. Per-fold re-optimization was worse than not optimizing at all.** On SPY, fixed parameters returned 1.685× out-of-sample; the same strategy with per-fold parameter search returned **1.105×** (and 0.553× with a smaller grid). The optimizer thrashes: `exit_len=50` was chosen in only 12 of 26 folds. Every fold it picked something different, and the average fold return was +3.8%/yr against holding's +8.1%/yr. **More knobs made it worse.** The negative fold returns cluster exactly where the filter was supposed to protect: -13.2% (2007-08) and -11.0% (2021-22).

## What Actually Improved (SPY, 30 years, 1x leverage, $0 fees)

| Curve | Total | CAGR | Max DD | Sharpe | Calmar |
|---|---|---|---|---|---|
| buy & hold | 9.89x | 8.3% | -56.5% | 0.509 | 0.147 |
| A plain Donchian 20/10 | 1.68x | 3.3% | -45.4% | 0.392 | 0.074 |
| **B improved: 20/50 + 2x ATR stop** | **4.76x** | **6.0%** | **-36.4%** | **0.536** | **0.165** |
| C + 200-day regime filter | 2.95x | 4.7% | **-20.8%** | 0.495 | **0.225** |
| D + vol target | 0.63x | 1.6% | **-7.6%** | 0.455 | 0.217 |
| E + trailing stop | 0.33x | 1.0% | -23.9% | 0.192 | 0.040 |

**Config B is the first thing in this entire project to beat the benchmark on risk-adjusted terms** (Sharpe 0.536 vs 0.509, Calmar 0.165 vs 0.147, over 30 years). The ingredients that did it: a **longer exit (50 vs 10 days)** and a **2× ATR stop**. No filters, no leverage, no re-optimization.

Out-of-sample (2010-2026, never used to pick anything):

| Curve | Total | CAGR | Max DD | Sharpe | Calmar |
|---|---|---|---|---|---|
| buy & hold | 5.79x | 12.1% | -34.1% | 0.754 | 0.354 |
| A plain Donchian 20/10 | 1.94x | 6.6% | **-9.0%** | **0.758** | **0.735** |
| B improved 20/50 + ATR stop | 2.86x | 8.4% | -16.3% | 0.740 | 0.515 |
| C + regime filter | 1.65x | 6.0% | -14.0% | 0.623 | 0.426 |

**Out-of-sample the plain 20/10 filter matches holding's risk-adjusted return (Sharpe 0.758 vs 0.754) with a quarter of the drawdown (-9.0% vs -34.1%) and double the Calmar (0.735 vs 0.354) — for one third of the return.** That is the whole trade, measured honestly.

## The Same "Improvements" On Crypto (BTCUSDT, 9y, 0.30% round-trip cost)

| Curve | Full-period Sharpe | OOS 2023-2026 Sharpe | OOS Max DD |
|---|---|---|---|
| buy & hold | 0.826 | **1.160** | -53.0% |
| A plain Donchian 20/10 | **1.103** | 0.876 | -38.4% |
| B improved 20/50 + ATR stop | 0.929 | 0.748 | -42.2% |
| C + regime filter | 0.612 | 0.386 | -38.9% |
| E + trailing stop | -0.157 | -0.104 | -22.2% |

**Every enhancement that helped on equities hurt on crypto**, and the plain Donchian was the best of the family (OOS 1.321x vs holding 4.032x). The 200-day regime filter is the clearest example: it exits during a crypto drawdown and stays out through the recovery — on a 24/7 asset with no gaps to re-enter on, it produced 0.309x out-of-sample.

## The Procedure-Level Result (the honest headline)

| Venue | Enhanced walk-forward OOS Sharpe | Fixed baseline OOS Sharpe | Buy & hold OOS Sharpe |
|---|---|---|---|
| SPY, 25 folds | 0.404 | 0.474 | 0.506 |
| BTC, 4 folds | 0.591 | 0.507 | 0.761 |

**The improvement procedure never beat buy-and-hold on Sharpe or CAGR on either venue.** On SPY it was worse than simply fixing the parameters once.

## Final Verdict

1. **The best version of this strategy is boring:** long-only, 1x leverage, 20-day entry channel, 50-day exit channel, 2× ATR stop, no leverage, no re-optimization, on a broad index. It earned holding's risk-adjusted return with a quarter of the drawdown on equities out-of-sample.
2. **It still does not beat holding on return, on any venue, in any window.** The upside of "trading" is not money; it is a smaller worst loss.
3. **The enhancements are venue-specific.** The regime filter and trailing stop are equity-appropriate and crypto-destructive.
4. **Most of what looked like an improvement was an artifact:** leverage, post-hoc config counts, and per-fold re-optimization. All three produced results that a spreadsheet would have called "excellent".
5. **The most valuable output is still the machinery** — the walk-forward protocol, the cost model, the benchmark discipline, and the five-plus bugs that each produced a plausible-looking fake.

## Bugs Found In This Round (all produced plausible-looking nonsense)

1. **Uncapped leverage** in vol-target sizing → a fake +31,629% out-of-sample return.
2. **Annualization at 365 days/year for equities** (252 trading days) → every Sharpe understated by ~20% and every CAGR wrong. Now measured from the data's own span (`bars_per_year_from_data`).
3. `l[i]` vs `low[i]` in the trailing-stop update → NameError.

## Sources

- https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1m/ — 9 years of 1m bars
- https://query1.finance.yahoo.com/v8/finance/chart/SPY — 30 years of daily bars, no key
- Moskowitz, Ooi & Pedersen (2012), "Time Series Momentum" — the only rule family with strong evidence
- Wilder (1978), "New Concepts in Technical Trading Systems" — ATR
- Lo (2004), "The Adaptive Markets Hypothesis" — why published edges decay
