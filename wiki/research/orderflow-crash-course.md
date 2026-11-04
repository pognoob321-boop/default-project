# Order Flow Trading — Free Crash Course

> **Status:** Feature/guide | **Date:** 2026-08-07 | **Purpose:** Free alternative to paid "frameworks" (e.g. Orochi by @44emirr) — same concepts, no paywall

## What Order Flow Is

Price action and indicators are **lagging** — they describe what already happened. Order flow is the **live record of actual buying and selling**: aggressive market orders consuming resting limit orders. It answers *why* price moved and hints at *what's next* ([Pearl of Trades](https://pearloftrades.com/learn/trading-strategies/order-flow/)).

- Candles show the result. Order flow shows the cause.
- Works best in **futures** (ES, NQ, MES, MNQ, CL, GC) because they trade on centralized exchanges with real bid/ask data.

## The Tools

| Tool | What it shows | Free option |
|---|---|---|
| **DOM (Depth of Market / ladder)** | Resting buy/sell orders at each price level | NinjaTrader free demo, Tradovate, Sierra Chart (paid) |
| **Time & Sales (the tape)** | Every executed trade: time, price, size, at bid or ask | Built into most platforms |
| **Footprint charts** | Bid vs ask volume inside each candle | Sierra Chart + MarketDelta (paid), Bookmap |
| **Bookmap heatmap** | Visual order book: resting liquidity + executions over time | Bookmap (paid, has free tier/trial) |
| **Volume profile** | Where volume concentrated (HVN = chop, LVN = movement) | TradingView (free with bars/volume profile limited) |

## Core Vocabulary (The 8 Words You Need)

1. **Bid** — highest price buyers will pay. **Ask/Offer** — lowest price sellers will sell at.
2. **Market order** — aggressive; hits the bid or lifts the offer instantly.
3. **Limit order** — passive; rests on the book until someone trades into it.
4. **Absorption** — big passive size keeps eating aggressive flow without price moving = someone defending a level. **The #1 signal.**
5. **Stacking** — limit orders piling onto a level as price approaches = intent forming.
6. **Pulling / Spoofing** — large order vanishes before price reaches it = fake liquidity, manipulation tell.
7. **Delta** — (volume traded at ask) − (volume traded at bid) per bar. Positive = buying aggression, negative = selling. **Cumulative delta** = running total over the session.
8. **Iceberg** — a huge order hidden in small displayed pieces; seen as repeated identical prints at one price.

## The Signals — What to Look For

- **Bid absorption (long setup):** sellers hammer the bid at a key level, price refuses to drop → a large buyer is absorbing everything. Institutional support.
- **Offer absorption (short setup):** buyers keep lifting the offer at resistance, price stalls → institutions are distributing into strength.
- **Delta divergence:** price makes a new high but cumulative delta makes a lower high → buying energy is fake; reversal likely. (Mirror for shorts.)
- **Stacked offers at a level + price approaching:** potential short zone — but only enter once you see the absorption *happen*, never preemptively.
- **Three-print rule:** one big print is data, not a signal. Three consecutive aggressive fills at the same level while price refuses to move = A+ setup.

## A Simple Beginner Framework (5 Steps)

1. **Pre-market (before 9:30 ET):** mark the levels that matter — prior session high/low, overnight high/low, VWAP anchor. Order flow confirms levels; it doesn't create them. No map, no trade.
2. **Wait out the noise (9:30–9:33+):** the first ~3 minutes of the open are algo chaos. Let it wash. Clean setups usually print 9:45–10:30 ET.
3. **Watch the DOM at your levels:** look for absorption — size getting eaten without price advancing (threshold idea: 800–1,000+ contracts absorbed in ~90 seconds on NQ; anything less is noise).
4. **Confirm with the tape:** prints must be predominantly one-sided (all at the ask for longs, all at the bid for shorts). Alternating prints = two-sided fighting = no trade.
5. **Execute:** enter on the first pullback tick, **limit orders only** (market orders cost 1–2 ticks slippage). Stop goes a few ticks *behind* the absorption zone (e.g. 4–6 ticks on NQ). Target at the next structural level or VWAP. Risk max ~1% of account per trade.

## Hard Rules

- **Spoofing is rampant** on thin markets (NQ pre-market, 6–8:30 AM): a big bid looks like support until it vanishes at touch. Verify absorption with time & sales — real absorption *prints*.
- **Delta in isolation is noise.** Negative delta during an uptrend = normal pullback. The same delta at resistance after a run = distribution. **Location determines meaning.**
- **Don't chase DOM prints.** Iceberg flashes → retail chases → institutions reverse. Wait for the level to hold through 2–3 aggressive attempts.
- **Skip the first 90 seconds after CPI/NFP/FOMC** — the book is a slot machine. Wait 2–3 min for a range, then look for absorption at a defined level.
- **No checklist, no trade.** Trade without a process is how prop-firm challenges die.

## Where to Practice Free

1. **Paper trade** on NinjaTrader/Tradovate demo or TradingView paper — free.
2. **Market replay** (NinjaTrader/Tradovate replay of past sessions) — learn to read absorption without risking money. Free built-in.
3. **Watch live streamers** who trade order flow and explain it (e.g. Flow Zone Trader's live NQ streams) — free education, but never copy anyone's trades blindly.
4. **Read these free:** Pearl of Trades order-flow guide (pearloftrades.com/learn/trading-strategies/order-flow/), Tim Warren's NQ order flow blog series, Bookmap's YouTube channel.

## Common Beginner Mistakes

- Buying the framework, not the skill (the "Orochi" trap — paying for rebranded vocabulary)
- Trading the first 3 minutes of the open
- Entering on a single large print instead of 3 confirms
- Using market orders on scalps (slippage eats the edge)
- Trading delta without structural context
- Ignoring session context: 2 AM Globex flow ≠ 9:30 AM RTH flow. Clean setups print 9:30–11:00 ET.

## The Honest Truth

Order flow is a real skill that works for some traders — but it is **execution-heavy**: fast decisions, small margins, real stress. The concepts here are exactly what paid "frameworks" like Orochi repackage. Learn them free, paper trade 1–2 months, and only then consider whether you even want to trade this style — many people find slower styles (swing trading, ORB morning strategy) fit them better.

## Free Video Playlist (Watch in This Order)

1. **Full 1-hour course (start here):** "Master ORDER FLOW TRADING in Less than ONE HOUR!" — Fractal Flow — auction theory → footprint → CVD → volume profile → examples — https://www.youtube.com/watch?v=6Ac38LzXj3A
2. **What delta really means:** "What Delta REALLY Means in Orderflow" — Price Action Volume Trader — https://www.youtube.com/watch?v=3Jb-wf6Bexs
3. **Real ES/NQ examples:** "Order Flow | Absorption. Delta Trading." — DejaBrewTrading — https://www.youtube.com/watch?v=EtjJ0eiwGuM
4. **Absorption & sweeps on the DOM:** "How To Trade OrderFlow - Absorption and Sweeps On the DOM!!" — https://www.youtube.com/watch?v=F6EoBOI8BFs
5. **Simplified delta recap:** "Order Flow Made Simple" — TRADEPRO Academy — https://www.youtube.com/watch?v=VlVb30yQM_0
6. **Live practice (watch, don't copy):** Flow Zone Trader's live NQ order flow streams — https://www.youtube.com/@FlowZoneTrader

## Related Wiki Pages

- [ORB Trading Strategy](orb-trading-strategy.md) — the morning breakout strategy (simpler entry point)

## Sources

1. https://pearloftrades.com/learn/trading-strategies/order-flow/ — full free guide: DOM, tape, footprint, delta, absorption
2. https://timwarrentrading.com/blog/2026-06-10-nq-futures-order-flow — NQ absorption example walkthroughs
3. https://timwarrentrading.com/blog/2026-07-01-nq-order-flow-trading — stacking/pulling/spoofing mechanics
4. https://www.youtube.com/watch?v=T44U-0rdIWI — Flow Zone Trader live NQ order flow stream
5. https://www.youtube.com/shorts/H6ChbrIIDAk — the Orochi paid framework (what this course replaces, free)
