#!/usr/bin/env python3
r"""BEAT 12's NATURALIZE, RE-FIRED ON A SKY THAT WAS REDRAWN INSTEAD OF SMEARED.

    python3 pipeline/derive_ep2_b12_sapnat3_0822.py [--write]

THE FAULT THIS ANSWERS was pre-registered by its own parent and then fired.
`ep2-b12-sapnat2-0822` passed P1, P2, P3 and P5 and failed on the one thing its
spec said to watch:

    "ALSO EXPECTED AND NOT A FAULT: b12's erase left a horizontal smear across
     the cloud bank where two 250 px discs were filled from their boundary ...
     If the smear survives, THAT is the finding: 0.30 finishes a drawn
     structure and a boundary-fill smear is a structure, so the fix would be a
     wider erase and a redrawn sky rather than a higher strength."

It survived. And 121 frames of LTX did not repaint it either.

WHERE THE SMEAR COMES FROM, and it is not the strength and not the mask area.
`fill_from_boundary` says its premise out loud in its own docstring: *"this
plate is a horizontally banded field -- so the fill is a per-row linear
interpolation between the nearest surviving pixels on that row, which
reproduces the banding exactly."* That is TRUE of the b15 grass plate it was
ported from and of b19's field, and it is FALSE OF A CUMULUS BANK. Beat 12
erased two 250 px discs out of the sky, so ~670 rows were each interpolated
between whatever survived at their two ends, and the result is a fan of
horizontal bars where the clouds were.

> **A FILL DIRECTION IS A CLAIM ABOUT THE PLATE.** Being wrong about it does
> not leave a soft patch, it INVENTS STRUCTURE -- and structure is precisely
> what a 0.30 pass is built to preserve. That is why the smear came through a
> naturalize and a whole i2v render untouched: at every stage it was doing its
> job on a thing that should never have been in the picture.

THE FIX IS IN THE COMPOSITOR, NOT IN THE SAMPLER. `--fill-mode harmonic`
(beat16_sapling_composite.py) reads the same boundary in two axes instead of
one: normalized convolution at a decreasing scale, within class, nothing
copied from elsewhere in the frame. Both of the row fill's load-bearing
properties survive -- decal tell #4 stays impossible by construction and a hole
in the sky is never averaged with grass -- and the streaks do not.

THE A/B WAS CUT LOCALLY AND COSTS NOTHING, WHICH IS WHY IT IS EXACT. The
parent's own command line was never recorded anywhere (not in its geometry
json, not in its spec, not in the ladder), so four numbers had to be
reverse-engineered off the geometry and two -- erase-lum and body-box -- could
not be recovered at all. Rather than pretend a rung against the shipped parent
is one variable, BOTH ARMS WERE RE-CUT HERE from one command line differing in
one flag:

    --fill-mode row        farm-out/ep2-b12-sapnat3-0822/b12-fill-row-control-0822.png
    --fill-mode harmonic   farm-out/ep2-b12-sapnat3-0822/b12-sapnat3-in-0822.png

At 1:1 the row arm reproduces the shipped smear exactly, which is the control
that says the reverse-engineered parameters are the right ones; the harmonic
arm has no bars in it. The tool now writes its own argv into the geometry json
so the next lane does not repeat the reverse-engineering.

AND ONE SIDE EFFECT WORTH THE SENTENCE, because it was not predicted: the fill
is not only backdrop. `light_direction` is measured on the FILLED array, so
changing the fill moved the measured light from dx -0.105 to dx +0.549 and the
drawn leaves are lit from the other side. The row arm's answer was being taken
off manufactured horizontal bars.

WHAT IS HELD: seed 20260820, strength 0.30, 40 steps, cfg 7.5, pad-crop 64,
blur 8, the prompt, the negative, the mask geometry (23.3% of frame; the
parent's was 19.8% and the difference is in the un-recoverable erase
parameters, which is stated rather than hidden) and every other byte of
ep2-b12-sapnat2-0822. THE ONE VARIABLE IS THE INIT, and inside the init it is
the fill of the erased region.

$0 to derive. ~4 GPU minutes.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_fetch_guard                                     # noqa: E402
import derive_spec                                            # noqa: E402

PARENT = "pipeline/jobs/ep2-b12-sapnat2-0822.yaml"
NEW_ID = "ep2-b12-sapnat3-0822"
PUBDIR = "farm-out/ep2-b12-sapnat3-0822"
INIT = "b12-sapnat3-in-0822.png"
MASK = "b12-sapnat3-in-mask-0822.png"

FETCH = '''#!/usr/bin/env python3
"""Fetch beat 12's HARMONIC-FILL composite and its mask, refusing on any sha
mismatch. Both files are on origin/main, so these sha256s are verifiable
against the repo by anyone who clones it. They were made on a Mac, so they are
NOT on the box's courier worktree -- the courier only ever contains what the
box produced."""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\b12sapnat3-0822"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "farm-out/ep2-b12-sapnat3-0822/")
UA = {{"User-Agent": "banyan-city-b12-sapnat/1.0 (albert.numbro@gmail.com)"}}
WANT = {{
    "{init}":
        "{init_sha}",
    "{mask}":
        "{mask_sha}",
}}

os.makedirs(OUT, exist_ok=True)
for name, want in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(RAW + name, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %s -- refusing.\\n   want %s\\n   have %s"
                 % (name, want, have))
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %s %d bytes sha %s OK" % (name, len(raw), have), flush=True)
'''

BAR_ADD = """
THE PARENT'S BAR IS UNCHANGED AND IS STILL THE BAR (P1-P6 + P4'). ONE CLAUSE
IS ADDED, and it is the clause this rung exists for:

  P7  THE CLOUD BANK HAS NO HORIZONTAL BARS IN IT. Read the band between the
      grass line and the top of the leaves at 1:1. The shipped parent has a fan
      of hard horizontal streaks there; `b12-fill-row-control-0822.png` in the
      same directory is the matched control that reproduces them from this
      lane's own command line, so the comparison is exact and does not depend
      on recovering the parent's argv.

      A PASS is: no bars, and whatever the pass drew there reads as cumulus or
      as soft sky. A soft, low-detail wash in the bank's own colours IS A PASS
      -- a harmonic fill is smooth by construction and the trade was taken
      deliberately, because a wash is a plausible piece of cloud and a bar is
      not a piece of anything.

      A NEW FAIL MODE, named so it cannot be discovered afterwards: the wash
      reads as an OUT-OF-FOCUS PATCH against sharp cel clouds -- the same
      dialect break that made beat 16's bokeh plate unusable, arriving here
      from the compositor instead of from the checkpoint. If that is what comes
      back, the next lever is a smaller erase (leave more real cloud standing)
      and NOT a higher strength.

  P8  THE LEAVES ARE STILL LIT FROM A DIRECTION THE PLATE SUPPORTS. The fill
      changed the measured light (dx -0.105 -> +0.549) because
      light_direction reads the FILLED array. The row arm was reading
      manufactured bars, so the new answer is the better-founded one -- but it
      is a change to the drawing and it is scored, not assumed.
"""


def sha256_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build(force=False, write=False):
    init_abs = os.path.join(REPO, PUBDIR, INIT)
    mask_abs = os.path.join(REPO, PUBDIR, MASK)
    for f in (init_abs, mask_abs):
        if not os.path.isfile(f):
            raise SystemExit("!! missing composite input %s" % f)
    init_sha, mask_sha = sha256_of(init_abs), sha256_of(mask_abs)

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "early-morning lane, 2026-08-22",
            "consumer": (
                "THE INIT FOR BEAT 12's MOTION RE-RUN, and nothing else until "
                "a human has opened it. Beat 12's current candidate is "
                "`12-related-LTX-stillmotion-r2-0822`'s parent r1, which "
                "measured 0 px of apex climb and FIXES the beat's recorded "
                "shipping fault -- so the cut is not waiting on this. What is "
                "waiting on this is the SMEAR, which r1 carries because r1's "
                "plate carries it."),
            "success": (
                "ONE 704x1280 png that passes the parent's whole bar AND P7: "
                "no horizontal bars in the cloud bank. Judged by eye at 1:1 "
                "against b12-fill-row-control-0822.png in the same directory."),
            "why": (
                "ONE VARIABLE OFF ep2-b12-sapnat2-0822: THE FILL OF THE ERASED "
                "REGION. The parent's own spec pre-registered the smear and "
                "named what its survival would mean; it survived, and it "
                "survived 121 frames of LTX on top. The cause is that "
                "fill_from_boundary interpolates PER ROW because it was "
                "written for a horizontally banded grass plate, and beat 12's "
                "backdrop is a cumulus bank. beat16_sapling_composite.py gained "
                "`--fill-mode harmonic` for this; the default stays `row` so "
                "every plate already cut reproduces byte for byte.\n\n"
                "BOTH ARMS WERE CUT LOCALLY FROM ONE COMMAND LINE differing in "
                "that one flag, because the parent's argv was never recorded "
                "anywhere and a rung against an unrecoverable parent is not "
                "one variable. The row arm is committed beside the init as the "
                "control. The tool now writes its own argv into the geometry "
                "json."),
        },
        overrides={
            "argv:--init-sha256": init_sha,
            "payload:fetch_init.py": FETCH.format(
                init=INIT, mask=MASK, init_sha=init_sha, mask_sha=mask_sha),
            "key:priority": 18,
        },
        retoken=[
            ("b12sapnat2-0822", "b12sapnat3-0822"),
            ("farm-out/ep2-b12-sapnat-0822/", PUBDIR + "/"),
            ("b12-sapnat-in-mask-0822.png", MASK),
            ("b12-sapnat-in-0822.png", INIT),
            ("b12-sapnat2-s", "b12-sapnat3-s"),
        ],
        extra={
            "bar_addendum": BAR_ADD,
            "the_one_variable": (
                "THE FILL MODE OF THE ERASED REGION IN THE INIT -- `row` -> "
                "`harmonic` in pipeline/beat16_sapling_composite.py. Seed, "
                "strength, steps, cfg, pad-crop, blur, prompt, negative and "
                "every payload byte are the parent's."),
            "the_rung_this_is_one_variable_from": (
                "farm-out/ep2-b12-sapnat3-0822/b12-fill-row-control-0822.png, "
                "cut by this lane from the same command line with "
                "`--fill-mode row`. NOT the shipped parent: its argv was never "
                "written down and two of its erase parameters cannot be "
                "recovered from what it did record."),
            "init_provenance": (
                "%s/%s, 704x1280, sha256 %s, with its mask %s sha256 %s. Cut "
                "by pipeline/beat16_sapling_composite.py --fill-mode harmonic "
                "from farm-out/ep2-b12-sapnat3-0822/b12-plate-src-0822.png "
                "(sha256 554db53257fde35ffa8a2f750c3fa9edef14aa9ffb3e2e30f75d67"
                "43cac537e8), which is f000 of the SHIPPED TAKE and not this "
                "beat's render plate -- b12's take abandons the 12-related-r4-s2 "
                "macro by f006, so the picture to correct is the one the model "
                "settled on. The full argv is in the geometry json beside the "
                "png."
                % (PUBDIR, INIT, init_sha, MASK, mask_sha)),
            "failure_predicted_in_advance": (
                "FIRST, AND IT IS THE ONE WITH THE MOST RIDING ON IT: the "
                "harmonic wash reads as OUT OF FOCUS against sharp cel clouds. "
                "That is beat 16's bokeh failure arriving from the compositor "
                "side, and if it fires the lever is a SMALLER ERASE -- leave "
                "more real cloud standing -- and not a higher strength.\n"
                "SECOND: the mask is 23.3% of the frame against the parent's "
                "19.8%, because the erase parameters could not be recovered "
                "exactly and this cut uses the tool's documented defaults. The "
                "mask-area law says 0.30 does less as the mask grows, so if P1 "
                "comes back weaker than the parent's, area is the reason and "
                "the fix is the erase, not the number.\n"
                "THIRD, AND UNPREDICTED UNTIL THE A/B WAS CUT: the light "
                "direction moved because it is measured on the filled array. "
                "The leaves are lit from the other side now. P8 scores it."),
            "not_done_on_purpose": (
                "NO MOTION IS FILED BY THIS JOB. Beat 12's motion question is "
                "separately settled -- r1 measures 0 px of apex climb against "
                "the take-in-the-cut's 140 px and reproduces at a second "
                "wording (r3) -- so the motion re-run off this plate is a "
                "cheap follow-on and NOT a re-opening of the still/grow "
                "question. It waits on this plate being looked at."),
        },
        by="pipeline/derive_ep2_b12_sapnat3_0822.py")

    out = "pipeline/jobs/%s.yaml" % NEW_ID
    if write:
        derive_spec.write(child, os.path.join(REPO, out), force=force)
        derive_fetch_guard.assert_fetch_urls_resolve(
            os.path.join(REPO, out), must_hold=(INIT, MASK))
        print("wrote %s" % out)
    else:
        print("DRY RUN -- pass --write. id=%s init=%s sha=%s"
              % (NEW_ID, INIT, init_sha[:16]))
    return child


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    build(force=a.force, write=a.write)
    return 0


if __name__ == "__main__":
    sys.exit(main())
