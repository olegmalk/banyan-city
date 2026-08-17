# PATCH, NOT APPLIED — `sapling-cotyledon-shape` against his 2026-08-17 ruling

**Status: written, unapplied, ready.** This file exists because the patch has now
been derived TWICE by two lanes and landed ZERO times, and a third derivation is
waste. Apply it verbatim when `pipeline/canon.yaml` goes clean.

**Target:** subject `sapling-cotyledon-shape` in `pipeline/canon.yaml`
(entry begins at line 246 as of commit `cda39571`).

## Why this is not applied

`pipeline/canon.yaml` and `pipeline/check_canon_drift.py` were both ` M` —
uncommitted in another lane's hands — at the time of writing (+130 and +301
lines, 408 insertions; that lane is unambiguously alive).

**The hazard is the COMMIT, not the edit.** The peer's diff does not touch this
entry, so there is no content conflict — an `Edit` would apply cleanly. But
`git commit -- pipeline/canon.yaml` sweeps the peer's 130 uncommitted lines into
this commit, and **there is no pathspec form of `git commit` that takes a
sub-file range.** Staging cannot help: a peer can stage in the gap between
`git add` and `git commit`. So the only safe move is to wait for the file.

The narrative lane declined this identically and recorded the same reasoning in
`genomes/sapling/THE-SAPLING.md` §2.2 ("Flagged, not touched"). Two lanes, same
verdict, same grounds. That is the guard working.

## The ruling being carried in

> *"the sapling 2 leaves are average leaves"*
>
> — the founder, 2026-08-17

Recorded in `genomes/sapling/THE-SAPLING.md` §2.2 (line 55 ff.), which supersedes
the steward's 2026-08-16 inference that the two leaves are round/oval cotyledons.
Both dates stay visible per house style §6.

What his words do NOT settle, and must not be stretched to cover: leaf SIZE in
frame, and whether the leaves are called *cotyledons*. "Average" rules on SHAPE.

## The four changes

### 1. `what:` — replace the inference with his words

The current text asserts ROUND/OVAL COTYLEDONS and labels itself "STEWARD
INFERENCE FROM HIS TWO-LEAF RULING AND NOT HIS WORDS". That self-label was
honest on 08-16 and is now simply obsolete: the claim is his. Replace with:

```yaml
  what: >-
    ORDINARY, AVERAGE LEAVES -- a plain unremarkable leaf, the shape anyone draws
    when you say "leaf", and nothing exotic on either side of it. HIS WORDS,
    2026-08-17: "the sapling 2 leaves are average leaves". This rules out the
    SPECIAL leaf in both directions: out are deeply lobed five-fingered palmate
    fig leaves (mature-tree foliage, a botanical specimen that reads as one), and
    out is any leaf drawn as a feature -- no lance shapes, no exaggerated
    silhouette, no leaf whose shape is the subject of the shot. SUPERSEDES the
    steward inference of 2026-08-16 (round/oval cotyledons, reasoned from the
    two-leaf ruling), which is kept struck-through beside it in THE-SAPLING.md
    section 2.2 with both dates so nobody applies the older rule. This entry no
    longer rests on an inference and is no longer vetoable in one line. NOT
    SETTLED by his words and not asserted here: leaf SIZE in frame (section 4
    still has `oversized` and `big` live and unruled) and whether the leaves are
    called cotyledons -- "average" is a ruling about shape, not about vocabulary
    or scale. The pre-ruling evidence survives intact: `wide oval cotyledon
    leaves with soft round tips, not narrow, not pointed, not lance-shaped` on
    beats 12/15/19/20 describes an average leaf and is compliant; `deeply lobed
    fig leaves with five fingers` on beat 01 does not and is not.
```

### 2. `since:` — `'2026-08-16'` → `'2026-08-17'`

The entry's authority changed hands on 08-17. The date must move with it.

### 3. `evidence.contains:` — repoint at live prose

```yaml
  evidence:
    file: genomes/sapling/THE-SAPLING.md
    contains: 'The canon is ORDINARY LEAVES'
```

Currently `'The working canon is ROUND/OVAL COTYLEDONS'`. **Read the next
section before touching this — the reason is not the one you would guess.**

### 4. `forbids:` — DELETE `no simple oval leaves`

```yaml
  forbids:
  - deeply lobed
  - \bfive fingers\b
  - \bpalmate\b
```

The first three survive his ruling: a palmate five-fingered fig leaf is the
opposite of average. **`no simple oval leaves` must go, and this is a real defect
in the guard rather than a bookkeeping tidy.** Against *"average leaves"*, an
ordinary leaf is closer to a simple oval than to anything else — so a rule that
forbids drafts for saying `no simple oval leaves` is **forbidding the canon it
exists to protect.** `THE-SAPLING.md` §2.2 and §6.3 both rule the negative
wrong, and as of 08-17 it is wrong against HIS words rather than against an
inference. It is live on beats 01 and 18; both need the negative dropped, which
is drafting work outside this patch.

Note the forbid-pattern sharp edge documented at `canon.yaml:201-205`: the
checker reads each draft as ONE string with the `No ...` negative tail
concatenated, so a bare-term forbid fires on the drafts that BAN the term.

## THE INSTRUCTION THAT TRAVELS WITH THIS PATCH

**Demonstrate that the rule still FIRES. A green suite is not evidence.**

A canon-honesty instrument that has quietly stopped checking is worse than no
instrument, because it reports safety it is not measuring. So whoever lands this
must show the rule goes RED when fed a violation — flip the evidence string to
something absent, or feed a lobed draft, confirm non-zero exit, then restore.
"`check_canon_drift.py` passed" is not the deliverable; "it passed AND I watched
it fail on purpose" is.

**And there is a specific reason to distrust this entry's evidence gate, which is
subtler than a stale string.** The old assertion
`'The working canon is ROUND/OVAL COTYLEDONS'` **is still present** in
`THE-SAPLING.md` — at line 81, *inside the struck-through superseded block*:

```
> ~~**The working canon is ROUND/OVAL COTYLEDONS.** He did not say this. He
```

So the gate is **passing right now, on text the file itself marks as dead.** It
was never going to fail, and it would have kept passing indefinitely.

That is a structural weakness in the register, not a one-off: **house style §6
keeps superseded text visible forever, so any `contains:` assertion pointed at
prose that later gets superseded keeps passing on the struck-through corpse of
its own claim.** The `contains:` mechanism cannot tell live canon from struck
canon. Every other entry using this pattern has the same latent hole —
`sapling-fig-not-green` and `ep2-fig-purple` are the ones to audit next.

Whoever fixes this properly should consider whether `contains:` needs to assert
against prose OUTSIDE `~~`-struck and `>`-quoted blocks, which is a
`check_canon_drift.py` change and belongs to that lane, not to this patch.

## Provenance

Written 2026-08-17 by the steward (Claude Opus 5), ControlNet-capability lane,
as a hand-off artifact. No render, no GPU, no spend, no canon file touched. The
`forbids:` defect and the struck-through-evidence finding are both this lane's;
the rest re-states an analysis the narrative lane reached independently.
