#!/usr/bin/env python3
r"""EP2 FINISH LANE: the 0.30 naturalize, pointed at the GRADED composites.

    python3 pipeline/file_finishnat_0822.py                  # dry
    python3 pipeline/file_finishnat_0822.py --write --beats 2,3

WHAT THIS IS. Step three of the finish chain, and the only step in it that
costs a GPU second:

    pick crop  ->  composite the prop  ->  grade  ->  NATURALIZE  ->  motion
                   (beat16_sapling_       (ep2_finish_   (here)
                    composite.py)          grade.py)

WHY THE COMPOSITE HAPPENS BEFORE THE GRADE AND NOT AFTER, WHICH IS THE ORDER
THE SHAPE WAS HANDED DOWN IN. Measured, on the first try: run
`beat16_sapling_composite.py` against a GRADED b03 plate and its own C5 check
refuses -- "the plant's FILL luma 175.6 is 74.6 away from the field's 101.1
(tolerance 46) -- it will read as pasted before the pass ever runs". The
compositor derives its palette from the plate's own greens, and on a graded
plate the brightest-green sample and the field mean have pulled apart far
enough that the drawing it makes no longer belongs to the field it is drawn
into. Compositing on the RAW plate and grading afterwards fixes it for free and
costs nothing in correctness, because the grade is a GLOBAL per-pixel function:
the pasted object and the plate it sits in get bit-identical treatment, so the
grade cannot introduce a seam. Both b02 and b03 then pass every gate at t=1.00.

WHAT THE 0.30 PASS IS FOR. The composite is a flat vector fill with a hard cut
edge; the pass returns it as cel line work in the plate's own ink weight
without moving it. 12 of 40 steps run from a latent that still holds the drawn
structure, so the layout steps never run. Nothing here is a new number --
every sampler value is carried from the parent, which is the rung beats 03, 13,
15, 16 and 19 already shipped plants on.

THE BAR IS THE PARENT'S AND IS NOT RE-WRITTEN: P1 drawn not pasted, P2 it has
not moved, P3 exactly two leaves on one stem, P4 HE survives unchanged, P5 it
sits in the grass. A FAIL on P2 or P4 kills the plate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import yaml as _yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                    # noqa: E402

PARENT = "pipeline/jobs/ep2-b03-sapnat-0821.yaml"
RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
COMP_DIR = "farm-out/ep2-finish-comp-0822"

# beat -> (init stem, what the prop is, why this beat needs it in the PLATE).
ROWS = {
    2: ("b02-comp-h520",
        "the thin sapling trunk he dives behind",
        "The canon-motion wave measured it four times: a prompt naming an "
        "object ABSENT from the init makes the model build the object and pull "
        "the camera back hunting for it. b02's own 0821 verdict is the type "
        "case -- 'by f104 he is a speck at bottom right of a wide shot "
        "dominated by a large bare tree that is in no plate'. The trunk is in "
        "this plate so the motion prompt is allowed to name it."),
    3: ("b03-comp-h480",
        "the trunk that hides roughly one-sixth of him",
        "Same root cause as b02 and the b03 verdict says so: 'the camera pulls "
        "back from ~f072 and his height roughly halves by f104. No trunk is "
        "ever drawn, so the beat's cover does not exist.' The stem runs up the "
        "centre across his waist, which IS the joke -- a trunk wide enough to "
        "actually hide him would be the wrong picture."),
}

# Two composites were rejected by eye before either of these was kept, which is
# the point of doing the structure with image processing -- a rejection costs
# seconds. Recorded so the next lane does not re-walk it:
#   b03 h620 -- the leaves landed at his CHIN and read as growing out of his
#               neck, which is the 2026-08-09 'sapling growing out of his head'
#               verdict in a new place. Lowered to h480, leaves at his waist.
#   b02 h580 -- the tool's own C3 refused it: the plant touched the frame edge.
#               h520 is the largest that stays whole in frame.
REJECTED = 2


def sha_of(rel: str) -> str:
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


FETCH_PY = '''#!/usr/bin/env python3
"""Fetch beat {beat:02d}'s graded composite and its mask, each pinned by sha256.

Both were made on a Mac, so they are NOT on the box's courier worktree -- the
courier only ever contains what the box produced. A wrong byte here is a pass
run over somebody else's picture, so this refuses rather than warns."""
import hashlib, os, sys, urllib.request

OUT = r"{work}"
UA = {{"User-Agent": "banyan-city-finishnat/1.0 (albert.numbro@gmail.com)"}}
WANT = {{
{want}
}}

os.makedirs(OUT, exist_ok=True)
for name, (url, want) in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %s -- refusing." % name + chr(10) +
                 "   want %s" % want + chr(10) + "   have %s" % have)
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %s %d bytes sha %s OK" % (name, len(raw), have), flush=True)
'''


def build(beat: int):
    stem, obj, cause = ROWS[beat]
    init_rel = "%s/%s-graded.png" % (COMP_DIR, stem)
    mask_rel = "%s/%s-mask.png" % (COMP_DIR, stem)
    geom_rel = "%s/%s.png.geometry.json" % (COMP_DIR, stem)
    grade_rel = init_rel + ".grade.json"
    for r in (init_rel, mask_rel, geom_rel, grade_rel):
        if not os.path.isfile(os.path.join(REPO, r)):
            raise SystemExit("!! %s is not on disk" % r)
    init_sha, mask_sha = sha_of(init_rel), sha_of(mask_rel)
    g = json.load(open(os.path.join(REPO, grade_rel), encoding="utf-8"))
    geo = json.load(open(os.path.join(REPO, geom_rel), encoding="utf-8"))
    if g["out_sha256"] != init_sha:
        raise SystemExit("!! %s changed since it was graded" % init_rel)

    new_id = "ep2-b%02d-finishnat-0822" % beat
    work = r"C:\banyan-farm\%s" % new_id
    init_name = "%s-graded.png" % stem
    mask_name = "%s-mask.png" % stem

    parent = _yaml.safe_load(open(os.path.join(REPO, PARENT), encoding="utf-8"))
    child = derive_spec.derive(
        PARENT, new_id,
        fresh={
            "owner": "the episode-finish compositor lane, 2026-08-22",
            "consumer":
                "THE INIT FOR BEAT %02d'S MOTION SPEC, and nothing else until "
                "then. review/ep2-ship-0821 is not touched and no cut moves "
                "because this landed." % beat,
            "success":
                "ONE 832x1216 png in which %s IS DRAWN INTO THE PLATE AND HAS "
                "NOT MOVED, judged by eye at 1:1. P1 stem and both leaves "
                "carry cel shading and the plate's ink line weight, not the "
                "compositor's flat fill; P2 root, height and leaf tips within "
                "a few px of where they were composited (root %s, height %.0f, "
                "apex %s); P3 exactly two leaves on one stem; P4 the goblin is "
                "untouched -- the mask is local and must not reach him; P5 the "
                "stem meets the grass with no floating base and no halo. The "
                "named degenerate outcome is a RELOCATED or REGROWN plant."
                % (obj, geo["root"], geo["height_px"], geo["apex"]),
            "why":
                "BEAT %02d'S MOTION FAILS PLATE-SIDE, AND THIS DRAWS THE "
                "MISSING OBJECT INTO THE PLATE INSTEAD OF REWORDING THE PROMPT "
                "AT IT.\n\n%s\n\nWHAT IS NEW HERE AND WHAT IS NOT. Not one "
                "sampler number: strength, steps, cfg, pad-crop, blur and the "
                "whole inpaint payload are the parent's, and the parent is the "
                "rung beats 03, 13, 15, 16 and 19 already shipped plants on. "
                "What is new is the INIT, and it is new in two ways. It is "
                "built on the pass-two finish plate (a 0.30 identity pass off "
                "the founder's own canon ref, so the face is his pixels), and "
                "it is COLOUR GRADED -- station %s, converge t=%.2f, lum %.1f "
                "-> %.1f -- because the prompt provably could not buy light: "
                "across all 19 pass-two plates the 0.30 pass moved 33-48%% of "
                "pixels while the mean RGB moved about one level.\n\nORDER "
                "NOTE: the prop is composited on the RAW plate and the grade "
                "is applied after. Compositing onto a graded plate trips the "
                "compositor's own C5 luma-agreement check, and the grade is a "
                "global per-pixel function so it cannot introduce a seam "
                "between the prop and the plate."
                % (beat, cause, g["station"], g["converge_t"],
                   g["before"]["lum"], g["after"]["lum"]),
        },
        overrides={
            "argv:--init": r"%s\%s" % (work, init_name),
            "argv:--init-sha256": init_sha,
            "argv:--mask-png": r"%s\%s" % (work, mask_name),
            "key:beat": beat,
            "key:priority": 9,
            "seed": 20260880 + beat,
        },
        extra={
            "the_one_variable":
                "THE INIT. Every sampler number is the parent's; what changed "
                "is which picture the pass finishes.",
            "plate_provenance":
                "%s, sha256 %s (mask %s, sha256 %s).\nLINEAGE, every hop "
                "hashed: taste/refs/goblin-canon-founder-0821.png (the "
                "founder's own image) -> farm-out/ep2-finish-plates-0822/"
                "b%02d.png (0.30 all-white-mask identity pass) -> "
                "beat16_sapling_composite.py draws %s at root %s, height %.0f, "
                "tilt %.1f, light direction MEASURED from the plate at dx "
                "%+.3f dy %+.3f and the palette sampled from the field's own "
                "greens -> ep2_finish_grade.py station %s at t=%.2f.\nTHE "
                "COMPOSITE WAS OPENED BEFORE THIS SPEC EXISTED and %d earlier "
                "ones were rejected by eye at zero GPU cost."
                % (init_rel, init_sha, mask_rel, mask_sha, beat, obj,
                   geo["root"], geo["height_px"], geo["tilt_deg"],
                   geo["light_dx"], geo["light_dy"], g["station"],
                   g["converge_t"], REJECTED),
        },
        retoken=[("ep2-b03-sapnat-0821", new_id),
                 ("b03sapnat-0821", "b%02dfinishnat-0822" % beat),
                 ("b03-sapnat-in-0821.png", init_name),
                 ("b03-sapnat-in-mask-0821.png", mask_name),
                 ("b03-sapnat", "b%02d-finishnat" % beat)],
        by="pipeline/file_finishnat_0822.py",
    )

    # SET AFTER derive() ON PURPOSE. derive_spec refuses a plate_ack passed in
    # `extra` -- it is findings-shaped, and a spec earns findings after its
    # pixels exist. That guard is right and is not being worked around: a
    # plate_ack is not a finding about THIS job's output, it is a statement
    # about its INPUT, which already exists on disk and is hashed below.
    child["plate_ack"] = [
        "unfetchable: %s is a Mac-side CPU composite-plus-grade, not a "
        "farm-out render, so it is not on origin/farm-results-rtx5090. It is "
        "on origin/main at sha256 %s and this job's fetch step refuses any "
        "other bytes. Opened at 1:1 before the spec was written; %d earlier "
        "composites were rejected by eye at zero GPU cost."
        % (init_rel, init_sha, REJECTED),
        "unresolved: no farm-out job produced it and none should -- "
        "beat16_sapling_composite.py and ep2_finish_grade.py are both "
        "deterministic, $0 and CPU-only. Their geometry and grade sidecars "
        "are committed beside the plate.",
    ]

    # The parent fetches from its own farm-out dir; ours come from two files in
    # a different one, so the fetch payload is replaced wholesale rather than
    # retokened -- a half-retokened URL that still resolves is the worst case.
    want = ",\n".join(
        '    "%s": ("%s", "%s")' % (n, RAW + r, s)
        for n, r, s in ((init_name, init_rel, init_sha),
                        (mask_name, mask_rel, mask_sha)))
    for k in [k for k in child["payload"] if k.endswith("fetch_inits.py")
              or k.endswith("fetch.py")]:
        del child["payload"][k]
    child["payload"][r"%s\fetch_inits.py" % work] = FETCH_PY.format(
        beat=beat, work=work, want=want)
    for st in child["steps"]:
        if st.get("name") == "fetch":
            st["argv"] = [r"C:\banyan-farm\venv\Scripts\python.exe",
                          r"%s\fetch_inits.py" % work]
    return child


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--beats", default=",".join(str(b) for b in sorted(ROWS)))
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    for beat in [int(b) for b in a.beats.split(",")]:
        if beat not in ROWS:
            raise SystemExit("!! beat %d has no row here" % beat)
        child = build(beat)
        out = "pipeline/jobs/%s.yaml" % child["id"]
        av = [t for st in child["steps"] for t in st.get("argv", [])]
        print("%-30s beat %02d  init %s"
              % (child["id"], beat,
                 av[av.index("--init") + 1].split("\\")[-1]))
        if a.write:
            derive_spec.write(child, out, force=a.force)
            print("   wrote %s" % out)
    if not a.write:
        print("\nDRY RUN -- pass --write to emit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
