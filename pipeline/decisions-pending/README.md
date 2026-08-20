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

| card | dir | options |
|---|---|---|
| `/review/ep2-guards-0818` | `ep2-guards-0818/` | pass → the beat-09 cut swap, written and runnable · recast → a casting rung · stage → nothing to file |
| `/review/ep2-b13-shade-0820` | `ep2-b13-shade-0820/` | A "ship it" → file nothing · B "draw it taller" → the motion spec, written |
| `/review/ep2-b16-leaf-0820` | `ep2-b16-leaf-0820/` | restage → file nothing (R4 writes it) · licence → the motion spec, written |

Beat 04's card (`/review/ep2-b04-action-0820`) deliberately has **no** directory
here: it asks the author to pick among three action lines, and the pick *is* the
spec. Pre-staging three of them would be pre-staging three different episodes.
