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
| `/review/ep2-guards-0818` | `ep2-guards-0818/` | **pass** → `swap-b09-into-cut.sh`, written and runnable · **recast** → nothing to file, and why · **stage** → fires the same swap |
| `/review/ep2-b13-shade-0820` | `ep2-b13-shade-0820/` | **A** → nothing to file, and why · **B** → canon exception first, then `derive-b13-tallmotion.py`, written |
| `/review/ep2-b16-leaf-0820` | `ep2-b16-leaf-0820/` | **restage** → nothing to file (R4 writes the staging) · **licence** → canon exception first; the motion spec is *not yet written* and the README says why |

`/review/ep2-b04-action-0820` deliberately has **no** directory here: it asks the
author to pick among three action lines, and the pick *is* the spec. Pre-staging
three of them would be pre-staging three different episodes.

**Rule 3 is doing real work in two of these four**, and that is the point rather
than a shortfall. "Nothing fires, and here is why" took as long to write as a
spec would have, and it is the entry that stops the next lane inventing one.

## The failure this directory is designed to make impossible

On 2026-08-20 three taste cards were open and every one of them would, on being
answered, have started a fresh round of *"right — so what do I do now?"* Two of
the three also had an option the author could not see, only read about. Both are
the same defect: **the machine stopping at the question instead of at the human.**
A card is finished when the only thing missing is a word.
