#!/usr/bin/env python3
"""Did the video model ANIMATE the approved still, or INVENT something?

    python3 pipeline/check_invention.py /tmp/final-clips
    python3 pipeline/check_invention.py /tmp/final-clips --beats 11,14

WHY FRAME-DIFFERENCE CANNOT ANSWER THIS. Every motion figure this pipeline has
ever reported measures how much the pixels move. A sprout undergoing mitosis moves
pixels beautifully:

    beat 11 — one sprout splitting into two, extra leaves appearing —
    scored 2.36 median, 0% frozen: the HIGHEST of all fifteen beats,
    and the steward called it the best beat in the episode.

The founder called it in one viewing: *"the sapling doing mitosis"*, and *"the big
rock randomly morphing because the ai cant figure out what else to do."* The metric
rewarded exactly the defect, because a metric that asks "is it moving?" cannot ask
"is it still the same thing?"

THE SIGNAL THIS USES INSTEAD. In image-to-video the first frame IS the approved
still, so it is ground truth for what the shot is supposed to contain. Then:

  - **Legitimate animation is RECURRENT.** A leaf sways out and back; grass lashes
    and settles; light pulses. Structural distance from frame 0 rises, then falls
    again. The composition keeps returning to itself.
  - **Invention is ONE-WAY.** A rock morphing into a different rock, or a second
    sprout growing where there was one, never returns. Distance from frame 0 climbs
    and stays climbing, and the final frame is the furthest thing from the still the
    founder actually approved.

So the tell is not the amount of change but its SHAPE over time:

    return_ratio  = d(last) / max(d)     ~1.0 means it walked away and never came back
    monotonic     = share of steps where d increases    high means one-way
    area_ratio    = foreground area last/first          >1 means new stuff exists
    spread_ratio  = spatial spread of foreground        >1 means a second object

Distances are computed on CONTRAST-NORMALISED frames, so a legitimate lighting
change (the glow surges, the sun arcs) does not read as a structural one — the
episode is full of deliberate light pulses and they must not trip this.

HONEST LIMITS, stated because the last metric was trusted too far. This measures
composition stability, not correctness. It cannot tell a *good* invention from a
bad one, it cannot see that a leaf is drawn wrong, and a beat that is SUPPOSED to
transform (beat 11's leaf genuinely unfurls; beat 01's fig genuinely grows) will
score like an invention because structurally that is what it is. It is a
FLAGGING tool: it says "look at this one", never "this one is bad". The founder's
eye remains the verdict — this exists so his eye is spent on the shots that need
it instead of on all fifteen.

MEASURED RECALL: 1 OF 5. THIS TOOL IS UNVALIDATED AND THE NUMBER IS NOT AN
ESTIMATE. On 2026-08-09 the beat-16 drift experiment produced the first clips
whose labels are known by construction — same plate, same recipe, four seeds, two
prompts 38 bytes apart — and three of them contain a full anime human who is not
in the conditioning frame. This gate passed all three and printed "nothing
flagged". Three more control-arm seeds were rendered the same night to take the
set to twelve (task `ep2-b16-expand-0810`); two of them drew a person, and the
gate catches exactly one — `control-s20260812`, the clip where a head and a bank
of rocks rise together, so the composition finally climbs the way the drift rule
expects. Four of five still walk through. The set, the harness and every number
below are `pipeline/invention-labelled-set.yaml` and `pipeline/eval_invention.py`;
run it before believing anything here.

  - `monotonic > 0.70` RUNS BACKWARDS. Measured AUC 0.34 on the twelve — still
    the wrong side of 0.5 — because the leaf keeps swaying while the man
    arrives, so the distance curve oscillates instead of climbing. All four
    misses fail on this conjunct alone.
  - DELETING IT DOES NOT PRODUCE A DETECTOR, it produces an alarm bell. With the
    conjunct struck out the rule scores 5/5 recall and 7/7 FALSE ALARMS: on
    six-second LTX output `return_ratio > 0.88 AND peak > 0.18` is true of every
    clip, invented or not. The conjunct that runs backwards is the only thing
    keeping the gate quiet, which means the gate carries no information on this
    engine in either configuration.
  - `peak > 0.18` DOES NO WORK ON LTX. Every labelled clip reads 0.57-0.95. The
    threshold was calibrated against AnimateDiff clips that read 0.12-0.50, and
    nobody rescaled it when the engine changed.
  - `area_ratio` and `spread_ratio` miss because `fg()` masks pixels DARKER than
    typical and an anime human in mid-tone linework is not darker than a peach
    sky. Masking on linework density instead gets closer (AUC 0.89 on area, 0.94
    on spread) and still does not separate the set.

WHAT WAS TRIED AND FAILED, recorded so it is not tried twice. The obvious repair
— compute the drift shape PER BLOCK so a man arriving in one corner is not
averaged away by a swaying leaf — is CONTRADICTED, not merely unsupported:
`local_mono_max` scores AUC 0.37 and `local_oneway_max` 0.41, both pointing the
wrong way. So does `shift_blob_frac` (0.36), the "an invention is a connected
blob" idea. Ledger record 38's pre-registered lead, the fraction of consecutive
frame pairs moving more than 1.0, separated the first nine perfectly and then
FLAGGED BEAT 11 AND BEAT 01 of the shipped episode-1 cut — the mitosis beat the
founder called the best in the episode reads 1.00 — which is the circularity that
record warned about, confirmed. The three expansion clips finished it off from
the other side: it no longer separates even in sample (AUC 0.80), because both
new invented clips are quiet ones.

THE ONE METRIC THAT CLEARED THE CORRECTION, AND WHY IT IS STILL NOT A THRESHOLD.
`peak` separates all twelve perfectly, AUC 1.00, exact two-sided p 0.0025, and
0.0025 x 15 candidates = 0.038 — the first and only time anything here has come
in under alpha 0.05. That was a PRE-REGISTERED test and not a lucky slice: the
n = 12 with 5 invented was computed in advance by `sample_size_needed`, three
arm-A seeds were rendered to reach exactly it, and the metric held. Leave-one-out
is 12/12 and it remains the only leader that does not flag the episode-1 cut
(those clips read 0.12-0.50).

AND IN THE SAME RUN IT FAILED THE ONLY HONEST TEST IT HAS EVER HAD. The three new
clips postdate both the candidate list and the leaderboard, so they are the first
points nobody chose. Draw the boundary on the eight original drift clips — 0.7674,
the number that existed BEFORE these clips were rendered — and it calls both new
invented clips clean: they read 0.7477 and 0.7458. The separation at twelve is
perfect only because the threshold is allowed to slide down to 0.7393 after
seeing them, and the usable margin fell from 0.21 to 0.03 as the two new
positives landed in the gap the first nine had left empty. THE RANKING SURVIVED;
THE BOUNDARY DID NOT, and a gate ships a boundary.

So nothing is retuned here, again, and now for a better reason than "the sample
is too small". The sample is no longer too small, and what it says is that this
metric's threshold does not transfer between two batches of the SAME beat on the
SAME plate, one seed apart. `peak` is still the best thing on the board and is
still not a number anyone can ship. This file prints how little it knows.
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# numpy and PIL are imported INSIDE the measuring functions, not here. The
# decision this file makes lives in verdict(), which is arithmetic on a dict, and
# a module-level numpy import made that function unreachable from CI — where the
# install list is pyyaml, pillow, markdown and nothing else. The consequence was
# that the gate's rule was the one part of the pipeline no test could execute,
# and it stayed 0-for-3 on the labelled set with every test green. Now
# `import check_invention` costs nothing and test_pipeline.py runs verdict() on
# the committed measurements.

sys.path.insert(0, str(Path(__file__).resolve().parent))
import licence_gate as lg  # noqa: E402 — the tolerant sidecar reader

# PRINTED AFTER EVERY RUN, PASS OR FAIL. A quiet detector reads as an all-clear,
# and this one's silence has been measured against ground truth exactly once — it
# was silent on three clips with a man in them. Whoever reads the table next
# should read that in the same breath, not find it in a docstring. The wording is
# blunt on purpose: "0 of 3" is a fact about this tool, not a caveat about tools
# in general.
UNVALIDATED = """
  ── INSUFFICIENT VALIDATION ─────────────────────────────────────────────────
  An `ok` here is WEAK EVIDENCE and a silent run is not an all-clear. Measured
  recall on the only labelled set this tool has (12 clips, 5 containing a human
  the plate never had) is 1 OF 5: four walk straight through. No threshold in it
  has been validated against ground truth, and the `monotonic` conjunct is
  measured running BACKWARDS (AUC 0.34) on those same clips.
  `peak` is the one candidate that clears the family-wise correction (p 0.038),
  and its boundary still MISSED both invented clips it had not already seen.
    labels   pipeline/invention-labelled-set.yaml
    harness  python3 pipeline/eval_invention.py
  Clearing a clip still needs eyes on frames. This tool cannot do it.
  ────────────────────────────────────────────────────────────────────────────"""

# Coarse on purpose. We are asking about composition, not texture: at 96x171 a
# second sprout is unmissable and a leaf's serration is invisible, which is the
# right trade for this question and makes fifteen clips take seconds.
W, H = 96, 171
SAMPLE_FPS = 8          # enough to see the shape of the curve, cheap to extract


def frames(clip: Path):
    """(n, H, W) float32 grayscale, contrast-normalised per frame."""
    import numpy as np
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(clip),
             "-vf", f"fps={SAMPLE_FPS},scale={W}:{H},format=gray",
             f"{td}/f%04d.png"],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg failed on {clip.name}: {r.stderr[:200]}")
        fs = sorted(Path(td).glob("f*.png"))
        if len(fs) < 3:
            raise RuntimeError(f"{clip.name}: only {len(fs)} frames sampled")
        out = []
        for p in fs:
            a = np.asarray(Image.open(p), dtype=np.float32)
            # normalise contrast, NOT just brightness: the episode deliberately
            # pulses light in beats 3, 5, 10 and 15, and those must not register
            # as the composition changing.
            s = a.std()
            out.append((a - a.mean()) / (s if s > 1e-6 else 1.0))
        return np.stack(out)


def edges(f):
    """Gradient-magnitude map, contrast-normalised.

    MEASURE SHAPE, NOT BRIGHTNESS. The first version of this compared normalised
    intensity and flagged beats 05, 10 and 15 — whose motion directions are "the
    dying screen glow **drains away**", "the glow **pulses hard**" and "the warm
    glow **slamming brighter**". Those are deliberate one-way LIGHTING ramps, and
    intensity distance cannot tell one from a rock changing silhouette. Edges can:
    a glow ramp leaves the edges where they are, while an invention moves them.
    """
    import numpy as np
    gx = np.zeros_like(f); gy = np.zeros_like(f)
    gx[:, 1:-1] = f[:, 2:] - f[:, :-2]
    gy[1:-1, :] = f[2:, :] - f[:-2, :]
    m = np.hypot(gx, gy)
    s = m.std()
    return (m - m.mean()) / (s if s > 1e-6 else 1.0)


def measure(fr) -> dict:
    import numpy as np
    em = np.stack([edges(f) for f in fr])
    e0 = em[0]
    d = np.array([np.abs(e - e0).mean() for e in em])
    dmax = float(d.max()) if d.max() > 1e-9 else 1e-9

    # foreground = the darker-than-typical mass. The episode's subjects (leaf,
    # sprout, soil, hand) are all darker than their skies/backgrounds, and after
    # normalisation a fixed threshold is meaningful across beats.
    def fg(f):
        m = f < -0.35
        return m

    m0, mL = fg(fr[0]), fg(fr[-1])
    a0, aL = int(m0.sum()), int(mL.sum())

    def spread(m):
        ys, xs = np.nonzero(m)
        if len(xs) < 8:
            return 0.0
        return float(np.hypot(xs.std(), ys.std()))

    rises = int(np.sum(np.diff(d) > 0))

    # SHAPE CHURN. return_ratio asks "did it come back?", which beat 11 passes:
    # its sprout ends where it started. But its leaves change SILHOUETTE between
    # every frame — the upper leaf is a different shape in all four samples. That
    # is morphing without travelling, and the return test is blind to it.
    #
    # A leaf swaying smoothly has consecutive frames that barely differ while the
    # total excursion is large -> low ratio. A leaf whose shape churns has large
    # consecutive differences and goes nowhere -> high ratio.
    step = np.array([np.abs(em[i] - em[i - 1]).mean() for i in range(1, len(em))])
    churn = float(step.mean() / dmax)

    return {
        "return_ratio": float(d[-1] / dmax),
        "monotonic": rises / max(1, len(d) - 1),
        "peak": dmax,
        "churn": churn,
        "area_ratio": (aL / a0) if a0 > 40 else 1.0,
        "spread_ratio": (spread(mL) / spread(m0)) if spread(m0) > 1e-6 else 1.0,
    }


def verdict(m: dict) -> tuple:
    """(flag, why). Thresholds are deliberately loose — this points a human at a
    clip, so a false alarm costs one look and a miss costs a shipped defect.

    AND ON THE ONE LABELLED SET THEY ARE ALSO WRONG: 1 of 5 recall, the
    `monotonic` conjunct measured pointing backwards (AUC 0.34), and `peak > 0.18`
    true of every LTX clip ever measured. They are left exactly as they were
    because the one candidate that cleared the correction on twelve clips
    (`peak`, p 0.038) then missed both positives it had not been fitted on, so
    the replacement on offer is a threshold that is already measured not to
    transfer. `pipeline/eval_invention.py` is where one has to earn its way in.
    """
    why = []
    # one-way drift: ends at its furthest point AND mostly climbed to get there.
    # MEASURED 2026-08-09 on invention-labelled-set.yaml — four of the five
    # invented clips read monotonic 0.55-0.62 against a clean mean above them, so
    # this conjunct is what stops them flagging, and striking it out flags all
    # twelve. The fifth (control-s20260812) clears it at 0.72 and is the tool's
    # only true positive on record; a head and a bank of rocks rise together
    # there, which is a one-way composition change of the kind this rule was
    # actually built for.
    if m["return_ratio"] > 0.88 and m["monotonic"] > 0.70 and m["peak"] > 0.18:
        why.append(f"one-way drift (ends at {m['return_ratio']:.2f} of peak, "
                   f"{m['monotonic']:.0%} of steps climbing) — the composition "
                   f"walks away from the approved still and never returns")
    if m["area_ratio"] > 1.30:
        why.append(f"foreground grew {m['area_ratio']:.2f}x — something exists at "
                   f"the end that was not there at the start")
    # CHURN IS REPORTED, NOT TRIGGERED ON, and that is a finding rather than a
    # TODO. It was built to catch beat 11, whose leaves change silhouette between
    # every frame while the composition returns — invisible to the drift test.
    # Measured: beat 11 churns 0.46; beat 01, whose hands are legitimately hammering
    # a keyboard, churns 0.53. Fast honest motion and morphing produce the SAME
    # number, so any threshold that catches beat 11 also condemns beat 01.
    # Lowering it until the one known case trips would be fitting a threshold to a
    # single label — which is how a mean got trusted over a median all of 2026-08-03.
    # The column stays visible because a human reading it alongside the others
    # learns something; the gate does not act on it.
    if m["spread_ratio"] > 1.25:
        why.append(f"subject spread grew {m['spread_ratio']:.2f}x — mass appearing "
                   f"away from the original subject (the mitosis signature)")
    return (bool(why), why)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips_dir")
    ap.add_argument("--beats", default="", help="comma list, default all")
    a = ap.parse_args()

    d = Path(a.clips_dir)
    want = {int(x) for x in a.beats.split(",") if x.strip()}
    clips = sorted(p for p in d.glob("*.mp4")
                   if re.match(r"^\d\d-", p.name)
                   and (not want or int(p.name[:2]) in want))
    if not clips:
        sys.exit(f"no NN-*.mp4 clips in {d}")

    # SKIP HELD STILLS. hold_still.py drives a deterministic ease-out push-in, so
    # its distance-from-frame-0 climbs monotonically to its maximum BY
    # CONSTRUCTION — the exact signature this tool calls one-way drift. On the
    # first run that produced four confident false positives (beats 04 and 14 were
    # held; the report would have claimed six beats contained invented content).
    # A held still cannot invent anything: no model ran. The sidecar says so.
    held = []
    for p in list(clips):
        # either naming shape (lg.sidecar_for): this located
        # `<full name>.mp4.meta.yaml` only, so a held clip filed under the stem
        # shape comes back as four confident false positives instead of a skip.
        meta = lg.sidecar_for(p, lg.META_EXT)
        if meta and "model: none" in meta.read_text(encoding="utf-8"):
            clips.remove(p)
            held.append(p.name)
    if held:
        print(f"  skipping {len(held)} held still(s) — no model ran, nothing to "
              f"invent: {', '.join(n[:2] for n in held)}\n")

    print(f"  {'beat':<5} {'ret':>5} {'mono':>5} {'peak':>5} {'chrn':>5} "
          f"{'area':>5} {'sprd':>5}  clip")
    flagged = []
    for c in clips:
        try:
            m = measure(frames(c))
        except RuntimeError as e:
            print(f"  {c.name[:2]:<5} {'--':>5}  {e}")
            continue
        flag, why = verdict(m)
        mark = "FLAG" if flag else "ok  "
        print(f"  {c.name[:2]:<5} {m['return_ratio']:>5.2f} {m['monotonic']:>5.2f} "
              f"{m['peak']:>5.2f} {m['churn']:>5.2f} {m['area_ratio']:>5.2f} "
              f"{m['spread_ratio']:>5.2f}  {mark} {c.name}")
        if flag:
            flagged.append((c.name, why))

    if flagged:
        print(f"\n  {len(flagged)} beat(s) to LOOK AT — this flags, it does not judge:")
        for name, why in flagged:
            print(f"    {name}")
            for w in why:
                print(f"      - {w}")
    else:
        print("\n  nothing flagged: every clip returns toward its opening frame")
    print(UNVALIDATED)
    return 0


if __name__ == "__main__":
    sys.exit(main())
