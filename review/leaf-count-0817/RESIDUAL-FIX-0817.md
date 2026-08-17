# THE COMPOSITOR'S RESIDUAL-LAMINA FAULT — fixed and proven on ALL FOUR variants

**2026-08-17, leaf-count lane (rung 3 preparation).** The mechanism that bound leaf
count (`ep2-b01-leafcomp-inpaint-0817`, 4 of 4 exactly two blades) was fired off ONE
composite, `comp-s1`. Its own verdict handed a defect forward: `comp-s0` and `comp-s2`
keep **a dark residual lamina below the junction** that the bar's own counting rules
("any partly occluded blade whose outline is identifiable is a blade") would score as
a THIRD BLADE. `comp-s1` and `comp-s3` do not. **A 50% defect rate in the compositor**,
and it had to be fixed before either beat took a canon plate off it.

## What the fault actually was — measured, not guessed

One hand-fitted `--remove` geometry was reused across four seeds whose blades differ.
On seed s0, of the dark pixels that survived the patch below the junction, **only 9%
lay inside the declared hard ellipse** (mask alpha median **5 of 255** on those
pixels): the declared region never covered the object it claimed to remove, and
**nothing in the tool measured that**. This is the house pattern's own rule broken —
*"FITTED TO THE OBJECT, NOT TO THE MASK"*, `pipeline/composite-init-pattern.md` §3.

## The fix — two additions to `pipeline/leaf_count_composite.py`, both opt-in

1. **`--check` measures what survived** inside the removal footprint (or a declared
   `--check-region`), against a declared per-plate OBJECT RULE (`--object-dark`,
   `--object-bright`, `--object-gmr-min/max`), groups it into 4-connected components
   and prints each one ≥ `--residual-min-area` with area and bbox.
   **`--assert-clear` refuses to write** while any such component survives — so this
   defect cannot silently reach a canon plate again. Guards live in code.
2. **`--sweep` patches the survivor fitted to its OWN silhouette** (dilated by
   `--sweep-grow`, feathered), not to a second guessed ellipse, from
   `--sweep-offset` (default: the first `--source-offset`). `--protect` boxes are
   excluded from both stages.

**THE SOURCE LAW, discovered while proving the fix and now enforced in code.** The
first sweep DIVERGED: on s2 the residual went **741 → 867 → 957 px** across three
passes, and on s0 **615 → 160 → 284**. Cause: at the original `--source-offset
-300,0` the background being copied in *itself satisfies the object rule* (a dark
blurred grass blob 300px to the right), so the sweep was patching a blade with pixels
that read as a blade — the residual moved rather than shrank. The tool now checks the
sweep source under the same rule **before** touching a pixel and refuses with
`!! THE SOURCE LAW` if the source is dirty. `--sweep-offset -220,-70` is clean on all
four seeds (0 rule hits) and converges in **one pass**.

This is the sibling of the vacancy law already in the pattern doc: *never leave an
unpainted gap* has a twin, *never paint with something that reads as the thing you
removed.*

## Proof, on all four variants and not only the two that were already clean

Object rule measured on THIS plate (no colour rule in this repo has ever transferred
between plates): `--object-dark 160 --object-gmr-min -45`, check region
`315,688,462,780`, `--residual-min-area 150`, `--sweep-offset -220,-70`,
`--sweep-grow 4`, `--sweep-passes 3`, `--assert-clear`.

| seed | residual before | passes | residual after | out sha256 | eye at 6x/9x |
|---|---|---|---|---|---|
| s0 | **660 px**, bbox (400,728)-(441,780) | 1 | **0** | `c1102490f75e54a4…` | dark green lamina GONE; both stem strands continuous through the swept band, softened not broken |
| s1 | 0 (already clean) | 0 | 0 | `0e84d2304c6884e1…` **unchanged** | untouched — byte-identical to the proven init |
| s2 | **922 px** in 2 comps, (323,696)-(354,746) + (402,732)-(418,766) | 1 | **0** | `2737b72f87c64cde…` | grey-green wedge below the junction GONE; stem intact |
| s3 | 0 (already clean) | 0 | 0 | `5faab465681e726d…` **unchanged** | untouched |

Independent agreement worth stating: the numeric detector, given a rule measured on
the plate and no knowledge of the prior read, fires on **exactly s0 and s2** and is
clear on s1 and s3 — the same split the previous lane found by eye at 4x. A filter
agreeing with the eye, never a verdict (§7 of the pattern doc).

**Regression, run first and passed:** with the new flags ABSENT, all four composites
reproduce the committed `cccbc85f` bytes exactly — `532b8542…`, `0e84d230…`,
`f6691a04…`, `5faab465…`. **The proven rung's pinned init chain (plate `ac754458`,
composite `0e84d230`) still reproduces**, so nothing already scored moved.
**Determinism:** re-running the swept invocation reproduces `c1102490…` and
`2737b72f…` byte for byte.

Cost: **$0** — PIL only, no model, no GPU, no network.

## What this does NOT fix, named so it is not assumed

- The blades on this plate are narrow **lance** shapes. Subtraction cannot make an
  "average leaf" out of a lance blade; that is a separate, additive job and a
  founder-facing shape question.
- The sweep softens whatever it crosses. On s0 it crosses the stem, which comes out
  continuous but lower-contrast in a ~50px band; the following 0.30 inpaint mask
  covers that band (the swept region is unioned into `--mask-out`), which is how the
  previous rung's own residual "resolved into stem and shadow rather than into a leaf".
  A stem that came out BROKEN would be a vacancy and would have to be re-swept with a
  `--protect` box instead — it did not happen here, and it is checked by eye, not
  assumed.
