# `decisions-pending/` — work that is finished except for one word

**Created 2026-08-20, on the founder's directive: _"we need more automation unless
there is something strictly blocked by human action."_**

Some work is blocked by a human and cannot be automated away — a taste call is the
whole example, and R4 says taste belongs to the author. But *only the call itself*
is blocked. Everything downstream of it is ordinary machine work that has been
sitting unwritten, so that when the answer arrives someone has to sit down and
figure out the steps again, and the founder gets asked a second question ("ok, and
now what do you want me to do about X?") that his first answer already settled.

**This directory is where that downstream work is written BEFORE the answer.** One
subdirectory per open review card. Inside each: a `README.md` naming every option
the card offers and exactly what fires for each, plus the runnable artifact for
every option that has one — a job spec, a script, a checklist.

## The rules this directory runs under

1. **NOTHING HERE IS ENQUEUED, RUN OR MERGED.** A spec in here is written, not
   filed. `box_autofill` reads `backlog/`, never this; `box_enqueue` takes an
   explicit path and nothing globs this tree. Being here is the *opposite* of
   being queued.
2. **One option, one artifact, no bundling.** If the author says "B", exactly the
   things under B fire, and nothing under A does.
3. **An option whose next step is authored work gets NOTHING here, and says so.**
   Writing a spec for a staging the author has not written yet would be inventing
   his answer. "File nothing; R4 writes the new staging" is a complete and correct
   entry.
4. **These expire the moment the card is answered.** When a card resolves, its
   directory is either fired or deleted in the same commit that records the
   verdict. A stale pre-staged chain is worse than none, because the next lane
   will trust it.
5. **The card must say the chain exists**, in the founder's own reading path —
   otherwise this is a filing cabinet nobody opens.

## Open right now

**NOTHING.** The table is empty for the first time since this directory was
made, and an empty table is the correct state — a pre-staged chain is only ever
justified while a card is genuinely waiting on one word.

| card | dir | options |
|---|---|---|
| *(none)* | | |

`/review/ep2-b04-action-0820` deliberately had **no** directory here: it asked the
author to pick among three action lines, and the pick *was* the spec. Pre-staging
three of them would have been pre-staging three different episodes. He answered
**A** (the peek) on 2026-08-20 and the line is now in `node.md`,
`done-definitions.yaml`, the approved leaf and `shots.md`.

## Fired and deleted — 2026-08-20/21

Rule 4 in practice, recorded because the deletions are the only evidence it was
followed:

| card | answer | what happened to the dir |
|---|---|---|
| `/review/ep2-guards-0818` | **pass** ("they should look like grown men. yes. dumb grown men.") | deleted 2026-08-21. `swap-b09-into-cut.sh` had been overtaken twice — beat 09 entered `review/ep2-ship-0821` on 08-20 under a steward override, and its live successor is `pipeline/swap_b09_r2s2_into_ship.sh`, which takes the take id as an argument and asserts the traps the old script only listed |
| `/review/ep2-b13-shade-0820` | **A** ("this does satisfy it…") | deleted 2026-08-21. A's chain was "file nothing, enqueue nothing, record the verdict, delete this directory", and the four records it named are written. `derive-b13-tallmotion.py`, the emitter for **B**, went with it — the ruling kills B |
| `/review/ep2-b16-leaf-0820` | **NEITHER — CLOSED-MOOT by the steward** | deleted 2026-08-21. The only one of the three closed without an answer, and the distinction matters: its premise expired rather than being decided. It asked how to unblock a SLATE; beat 16 got footage at 01:05 (`1dce7e70`, 7/7 on its bar) and the slate stopped existing. Neither branch fires — *restage* was always "nothing to file" and *licence* pointed at a canon exception plus a `derive-b16-leafmotion.py` nobody wrote. The macro is **not refused**; reopening costs one word |

Both sat armed for a day after their cards were answered, which is exactly the
failure rule 4 names. **Rule 3 is doing real work here too**: "nothing fires, and
here is why" was the right entry for A, and it is what stopped a lane inventing a
rung after the answer arrived.

## The failure this directory is designed to make impossible

On 2026-08-20 three taste cards were open and every one of them would, on being
answered, have started a fresh round of *"right — so what do I do now?"* Two of
the three also had an option the author could not see, only read about. Both are
the same defect: **the machine stopping at the question instead of at the human.**
A card is finished when the only thing missing is a word.
