# Timeblocking Plan (Obsidian journal)

Built 2026-10-19. The user's Obsidian vault is **not** the `Default Project` repo — it is a separate vault whose path is recorded in `%APPDATA%\obsidian\obsidian.json`.

## Vault

| | |
|---|---|
| Vault name | `journal` |
| Path | `C:\Users\ZBook\.openhuman\users\6a744f5e93802f5472ebc834\workspace\memory_tree\content\.obsidian\journal` |
| Look up any vault path | `Get-Content "$env:APPDATA\obsidian\obsidian.json" -Raw` |
| Core plugins already on | `daily-notes`, `templates`, `canvas`, `bases`, `sync`, `properties`. **Templater is NOT installed.** |

The vault was near-empty before this: only `Home.md`, `Untitled.canvas`, and pasted images. It contains none of `wiki/` — `Home.md` links `../features/...`, so the vault sits *inside* the openhuman `memory_tree/content` tree but the research wiki lives in the `Default Project` repo instead.

## School timetable — the hard data

Source: two aSc Timetables printouts pasted into `timeblocking.md`.

**SS2 HS Timetable 26-27, 9 Adonis** — CIA FIRST International School, 107 St 2004, Phnom Penh. Generated 8/10/2026.

| Period | Time | Mon | Tue | Wed | Thu | Fri |
|---|---|---|---|---|---|---|
| P1 | 07:30–08:40 | Social Studies 202 | Mathematics 137 | English Lang Arts 105 | Social Studies 202 | Life Science 302 + Chemistry 303 |
| — | 08:40–08:55 | snack | snack | snack | snack | snack |
| P2 | 08:55–10:05 | Mathematics 137 | Health & Hygiene 2023 | Comp Sci Principles 106 | English Lang Arts 105 | English Lang Arts 105 |
| — | 10:05–10:10 | transition | transition | transition | transition | transition |
| P3 | 10:10–11:20 | English Lang Arts 105 | Social Studies 202 | Mathematics 137 | Comp Sci Principles 111 | rotation |
| Advisory | 11:20–11:35 | room 111 · Kris, every day | | | | |
| — | 11:35–12:15 | lunch | lunch | lunch | lunch | lunch |
| P4 | 12:15–13:25 | Life Science 302 + Chemistry 303 | same | same | Mathematics 137 | Social Studies 202 |
| — | 13:25–13:30 | transition | transition | transition | transition | transition |
| P5/P6 | 13:30–15:30 | "Afternoon Elective" all five days | | | | |

Teachers: Daniel SS · Natun · Arna · R-Jay · Rurrel · Aric · Kris (advisory, Thu P3, Fri rotation).

## Elective block — Grade 9 Phnom Penh. Generated 12/8/2026. Different grid, has a Saturday column, ends 16:45.

**Read the printout structure before transcribing it.** Each weekday column is **one merged cell spanning 13:35–15:05** (a 10-minute break sits inside it at 14:15–14:25) and **one merged cell spanning 15:16–16:45** (break inside at 15:55–16:05). The tell is that the teacher name is printed **once per merged cell**. Splitting those into 13:35–14:15 + 14:25–15:05 is wrong — that is just the row-label column, not two periods.

**Wednesday is the exception in structure only**: three separate cells — M 13:35–14:15, K 14:25–15:05, C 15:16–**16:45**. The last cell is still 90 minutes; only the first two are shortened. **Every day ends at 16:45** (the earlier "finishes at 15:55" reading was wrong — corrected 2026-10-19 at the user's request).

**Subject legend — supplied by the user 2026-10-19.** The aSc sheets print no key; these mappings came from the user, not the printout:

| Code | Subject | Code | Subject |
|---|---|---|---|
| K | Khmer | C | Chemistry |
| H | History | Mo | Civic Ethics |
| B | Biology | G | Geography |
| M | Mathematics | Ea | Earth Study |
| P | Physics | | |

| Day | 13:35–15:05 | 15:16–16:45 |
|---|---|---|
| Mon | Khmer · San Sreynich | History · Phorn Seyha |
| Tue | Biology · Him Sarith | Mathematics · Eang Samathphary |
| Wed | *Mathematics 13:35–14:15 · Khmer 14:25–15:05* | *Chemistry 15:16–16:45* · Son Chanthirit |
| Thu | Civic Ethics · Chheang Bunthour | Khmer · San Sreynich |
| Fri | Mathematics · Eang Samathphary | Physics · Chhan Kimchhorn |
| Sat | Geography · Bun Yithro | Earth Study · Pich Khunnarady |

**Timetable AT 26-2027** — third printout, same period times as the SS2 table. Two things it adds: Wednesday is **Eagle Day, 1 hr periods**, with an Eagle Period 10:50–11:45 in place of P3; and the P5 afternoon block is labelled **FTI** on all five weekdays.

## Resolved conflicts

1. ~~**End of school day.** SS2 table says 15:30, Grade 9 PP says 16:45.~~ **RESOLVED 2026-10-19: school ends 16:45.** The 15:30 figure came from the SS2 printout's "Afternoon Elective" placeholder row, which does not reflect the real merged cells. The Grade 9 PP table is the authoritative afternoon. This also means the evening plan genuinely runs off a 16:45 finish.
2. ~~**Wednesday ends at 15:55.**~~ **CORRECTED 2026-10-19 at the user's request:** C runs 15:16–16:45. Wednesday is three *cells*, not a shorter day.
3. ~~**Elective subject codes unknown.**~~ **RESOLVED 2026-10-19 by the user** — legend table above. Event titles now spell subjects out; the codes live only in the generator script header.

## Still unresolved

1. **Saturday school.** Grade 9 PP has a Sa column; SS2 and AT have none. The plan treats Saturday as a school day (G 13:35–15:05, Ea 15:16–16:45).
2. **Wednesday structure.** Eagle Day 1-hr periods vs the standard P3. Ask Kris.

## Plan structure

`timeblocking.md` in the vault holds the master grid. Design decisions worth keeping:

- **Three knobs, not a re-plannable grid.** Wake 05:30 / bed 22:00 (9.5 h), 45 min travel each way, gym Mon/Wed/Fri. These are the only numbers the user is meant to edit; everything else follows.
- **One 90-minute evening block only — Block 1 19:45–21:15, after the weekday tutor 18:30–19:30.** The original two-block structure (Block 1 18:30–20:00 + Block 2 20:15–21:15) was cut when the tutor became Mon–Fri: one uninterrupted 90-min block beats two truncated ones, and it preserves 21:15 screens-down / 22:00 bed. Matches [Focus study work ethic](research/focus-study-work-ethic.md) on 90-min cycles and 4–5 h deep-work ceilings.
- **Block 1 splits 60/30** (added 2026-10-19 with the subject legend): 60 min main subject + 30 min that day's first elective, or Khmer in a test week. Weekly plan: Tue ELA+Bio, Wed CS+Khmer, Thu CS+Maths elective, Fri 90 min science, Sat catch-up + Geo/Earth Study retrieval.
- **Do the day's work the night it is set**, hardest subject in Block 1. Keeps math/CSP out of a Friday-night brain.
- **Restart rule copied into every daily note**, from [Study quit loop](research/study-quit-loop-and-beginner-method.md): missed Block 1 → 20 minutes, not 90; missed day → skip to the next Block 1, never double up.
- Skincare/football/nap anchors came from [Weekly protocol](features/weekly-protocol.md) so the two systems do not contradict each other.

Seven daily notes `2026-10-19.md` … `2026-10-25.md` were written pre-filled, plus `Templates/Timeblocked Day.md` and `.obsidian/{templates,daily-notes}.json`. **Caveat: core Templates has no conditionals**, so a future daily note gets the skeleton but not the right weekday's subjects — new weeks need the subjects typed in, or Templater installed.

## Related

- [Weekly protocol](weekly-protocol.md) — skincare, football, nap, sleep anchors
- [Focus study work ethic](../research/focus-study-work-ethic.md) — where the 90-min block and the 4–5 h ceiling come from
- [Study quit loop](../research/study-quit-loop-and-beginner-method.md) — the restart rule