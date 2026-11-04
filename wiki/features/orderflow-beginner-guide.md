# Order Flow Trading — Beginner's Start Guide (From Zero to Live)

> **Status:** Feature/guide | **Date:** 2026-08-07 | **Goal:** Exact steps a beginner follows to learn order flow trading safely — setup → paper → small live

## Phase 0: What You Need (1 Day)

**Minimum setup (free/cheap):**
- **NinjaTrader** (free demo account) or **Tradovate** (free trial) — platform with DOM + tape + market replay built in
- **Under 18?** NinjaTrader/Tradovate/IBKR all require 18+. Use **TradingView Paper Trading** instead — free signup (email only, no ID/KYC), works in Cambodia, supports MNQ/NQ futures with $100k virtual money (CME data is 10-min delayed on the free plan). Verified 2026-08-07.
- A computer and internet — that's it. No $5k of monitors needed. No paid data feed yet.
- Notebook or spreadsheet for a **trading journal** (Google Sheets is fine)

**Skip for now (money traps):**
- Paid courses, paid "frameworks" (Orochi, etc.), paid Discord groups, signal services
- Bookmap/Sierra Chart subscriptions ($150–200/mo) — upgrade only after you prove you can profit on demo
- Prop firm challenges (Topstep, Apex, FTMO) — they expire in days/weeks; a beginner burning through them is burning money

**Expectations to set now:**
- Budget **at least 1–2 months** of paper trading before real money
- Most people lose money their first 6 months live. Your goal in month 1 is NOT profit — it's *process*.

## Phase 1: Setup Day (Day 1)

1. Download NinjaTrader (free), open Tradovate demo, **or (under 18) TradingView → chart MNQ → Trading Panel → Paper Trading**
2. Open an **MNQ** (Micro Nasdaq futures) chart — $2/point, small risk per contract. NOT NQ ($20/pt). NOT ES.
3. Turn on: DOM (SuperDOM), Time & Sales, 5-minute chart
4. Find the **market replay** feature — practice on yesterday's session
5. Write your journal template:
   - Date, time, setup type, level, what you saw (absorption/stacking/delta)
   - Entry/exit prices, R:R, screen/photo of chart
   - 1 sentence: "what was my thesis?" and "what would I do differently?"

## Phase 2: Learn the Vocabulary in Action (Week 1)

**Goal: pattern recognition, zero trades that matter.**

- Days 1–2: Watch 1–2 hours/day of replay from the previous session. Don't trade. Just mark on the chart where big absorption happened (price grinding at a level without breaking).
- Days 3–4: Watch 2 live sessions (9:30–11:00 AM ET) with the DOM open. Say the words out loud: "that's stacking at the offer" / "that bid got pulled — spoofing" / "delta diverged there." Naming what you see is the skill-building step.
- Day 5: Review your week. Did you see at least 3 absorption events? If no, replay more. If yes, move on.

**Watch list for the week:** 1 liquid streamer who explains order flow (Flow Zone Trader's NQ streams, Tim Warren's blog). Educational only — never copy their trades blindly.

## Phase 3: Paper Trade the 5-Step Framework (Weeks 2–4)

Trade ONLY this checklist, ONLY on MNQ demo:

1. **Pre-market (10 min):** mark prior day high/low, overnight high/low, VWAP. No map → no trade.
2. **9:30–9:33:** hands off. Algo noise.
3. **9:45–11:00:** watch the DOM at your levels for absorption (size eaten at a level, price not moving).
4. **Confirm:** tape shows one-sided prints (all at bid for shorts / all at ask for longs). Alternating = no trade.
5. **Execute:** limit order on the first pullback tick. Stop 6–8 points behind the absorption zone (MNQ). Target: next level or VWAP. Max 2 trades/day.

**Rules for the whole phase:**
- Log EVERY trade in the journal — wins AND skipped setups
- Track your win rate, average R, and drawdown weekly
- If you hit 2 stop-outs, you're done for the day. No revenge trading. Go do something else.
- After 3 weeks, look at your numbers: is your win rate ≥ 40% with average winner ≥ 1.5× average loser? That's the minimum bar to keep going.

**Week 3–4 additions (one at a time):**
- Add delta divergence as a second setup type
- Start classifying days: TREND day (breakouts follow through) vs CHOP day (everything fails) — you'll learn to sit out chop days

## Phase 4: Go Live Small (Weeks 5–6, only if paper is profitable)

**If your paper results after 4 weeks are a net loss — do NOT go live yet.** Repeat Phase 3 or take a step back and reconsider whether day trading fits you at all.

**If profitable:**
- Fund with an amount you can afford to LOSE 100% of. $500–$1,000 is plenty for MNQ micros.
- Trade **1 MNQ contract** only. No scaling up until 50+ live trades are logged.
- Same checklist, same journal, same 2-trade max. Nothing changes except it's real money.
- Risk per trade: 0.5–1% of account. With $1,000 that's $5–10 risk per trade. If that feels tiny — good. It's supposed to.

## Phase 5: Scale (Month 3+, only after consistency)

- 100+ live trades logged with positive expectancy → consider 2 contracts
- Only then think about: prop firm challenges (with a tested edge), better data feed, Bookmap
- Review monthly: win rate, expectancy, max drawdown, which setups made money vs lost

## The 5 Rules That Keep Beginners Alive

1. **Paper trade until profitable.** Not until "comfortable" — until the numbers are positive over 30+ trades.
2. **1 contract. 1 setup. 1 market.** MNQ, absorption only, nothing else for 2 months.
3. **2 losses = done for the day.** This one rule saves more accounts than any strategy.
4. **Journal everything.** You can't fix what you can't see. Charts + screenshots + 1-line lessons.
5. **Never pay for what you can learn free.** Paid frameworks, signals, and Discord "mentors" sell hope. The skill is free to learn; the cost is your time and discipline.

## Red Flags to Quit Immediately

- You're trading with money you need for bills/rent
- You're gambling (no stop, oversized size, revenge trades)
- You've blown 2 accounts and are planning the 3rd "this time with discipline"
- Someone is promising guaranteed returns or showing Lambo screenshots

## Realistic Timeline

| Month | Milestone | Success metric |
|---|---|---|
| 1 | Setup + vocabulary + paper | Can name 3 signals on a live chart |
| 2 | Paper trading checklist | Positive expectancy over 30+ paper trades |
| 3 | Live, 1 contract | Follow checklist 100% of the time |
| 4–6 | Consistency phase | Green month on demo OR live, journal complete |
| 7+ | Scale or reconsider | Only scale if data says so |

## Related Wiki Pages

- [Order Flow Crash Course](orderflow-crash-course.md) — the concepts this plan practices
- [ORB Trading Strategy](orb-trading-strategy.md) — the simpler morning strategy, good alternative for beginners

## Sources

- https://pearloftrades.com/learn/trading-strategies/order-flow/ — free order flow concepts
- https://timwarrentrading.com/blog/2026-06-10-nq-futures-order-flow — absorption examples and risk math
- https://www.youtube.com/watch?v=T44U-0rdIWI — Flow Zone Trader live NQ order flow streams (free watching)
