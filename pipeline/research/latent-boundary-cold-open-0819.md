# Testing the latent-boundary lead against our own clips — one clean hit, one clean miss

2026-08-19, night supervisor (v2) · zero GPU, zero spend · measurement on clips
already rendered

`pipeline/research/video-samplers-steps-temporal-0818.md` calls one lead its
strongest "by a distance": that a 1–4 frame pop with a blended frame at the join is
not a sampler artifact at all but a **latent-chunk / I2V conditioning-boundary**
artifact. It ends with a falsifiable instruction — *check whether your pop starts at
frame 1 and settles at frame 4* (Wan's quantum; **LTX's is 8**).

We checked. **It is emphatically true on beat 17 and false on the cold open**, and
the difference is the useful part.

---

## The structural fact

LTX's VAE temporal quantum is 8 pixel frames. Pixel frame 0 **is** the conditioning
image and is its own latent slice; pixel frames 1–8 are latent 1. So a change that
begins at frame 1 and is finished by frame 8, with the rest of the clip comparatively
static, is exactly one latent frame wide and sits exactly on the I2V conditioning
boundary. `LTXVAddGuide` enforcing `frame_idx` divisible by 8 is the same number seen
from the tooling side.

## Hit: beat 17 abandons its plate inside latent 1

`ep2-b17-shake-0818`, mean absolute RGB distance from the f000 plate:

| f001 | f002 | f003 | f004 | f005 | f008 | f016 | f096 |
|---|---|---|---|---|---|---|---|
| 25.1 | 45.8 | 62.1 | 76.5 | 79.2 | **80.7** | 83.3 | 87.3 |

**92% of the entire drift is complete by frame 8; 95% by frame 16.** Then it plateaus
for the remaining 88 frames. In pictures: a blue sky over a green meadow with a
blue-violet cloak becomes an amber sky over a dry brown field with an orange cloak,
and then holds that new world perfectly steady.

That is the predicted signature, at the predicted width, on the predicted boundary.
The model does not drift away from the plate over five seconds — it leaves inside the
first latent step and never looks back. No seed changes that.

## Miss: the cold open front-loads too, but so does the seed that passes

The same measurement over all eight cold-open clips — share of total frame-to-frame
change falling inside pixel frames 1–8 (uniform expectation 6.7%):

| clip | f1–8 share | ratio vs rest | verdict on record |
|---|---|---|---|
| b | **32.7%** | 6.8× | **PASS — the pick** |
| b2 | 13.7% | 2.2× | FAIL G1, fig replaced |
| b3 | 26.9% | 5.1× | FAIL style only |
| b4 | 24.1% | 4.5× | FAIL G1, 15f then static |
| b5 | 3.6% | 0.5× | FAIL G1, two-frame pop |
| b6 | 14.6% | 2.4× | FAIL G1, four-frame pop |
| b7 | 13.1% | 2.1× | unjudged |
| b8 | 29.3% | 5.8× | unjudged |

Every clip front-loads into latent 1 — 2.1× to 6.8× above uniform — so front-loading
is real and is a property of **this recipe**. But **the pick front-loads hardest of
all (32.7%)**, and the seed with the *least* front-loading (b5 at 3.6%, actually
below uniform) is a G1 failure whose pop sits at frames 11 and 73–74, nowhere near a
conditioning boundary.

So on the cold open the boundary effect **does not separate pass from fail**. It
cannot be the explanation for G1.

A note on method, because the first cut of this was wrong: I initially tested
"biggest change lands at ≡1 mod 8". That statistic is worthless here — when nearly
all change is inside frames 1–7 anyway, the mod-8 residues just re-encode the raw
indices. The share-of-total-change measure above is the one that answers the
question.

## What this corrects, including something of mine

The correction appended to `pipeline/jobs/ep2-b01-growmotion-b-0818.yaml` earlier
tonight said the cold-open recipe's dominant fault is that it "does not distribute
change across the clip". **That is measured true of all eight clips including the
passing one**, so as stated it describes the recipe, not the defect that fails G1.
The part of that correction which stands is the arithmetic: four of five rejects fail
G1 by the same clause, so those failures are not three independent dice. The part
that needs narrowing is the mechanism — front-loading is the recipe's constant, not
G1's cause. Recorded here rather than quietly dropped.

## What this licenses

- **Beat 17: one sample**, one variable — the amber clause out of the positive prompt
  — with a plate-fidelity clause pre-registered in the bar. Filed as a follow-up on
  `ep2-b17-shake-0818`.
- **Cold open: nothing.** The lead that looked strongest is measured not to apply, and
  no replacement mechanism is named, so no sample is filed. Two more seeds (b7, b8)
  were run by another lane tonight and remain unjudged; they are seeds, not variables,
  and the sweep's stop conclusion is unaffected.
- **Not reachable:** the knob the research names for the beat-17 case is start-frame
  conditioning strength. `pipeline/ltx_i2v.py` exposes no `--init-strength`, so it is
  a code change and a daytime decision — the same answer as
  `guidance-schedule-feasibility-0818.md`.
