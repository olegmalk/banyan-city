#!/usr/bin/env python3
r"""BEAT 06 RE-PLATE ON THE RATIFIED GUARD, one sample.

    python3 pipeline/derive_b06_guard1_0822.py --selftest   # assert, write nothing
    python3 pipeline/derive_b06_guard1_0822.py --write

WHY THIS BEAT AND WHY NOW. Beat 06 THE CLIPBOARD carries two standing faults on
`/review/ep2-beats-0821` and has never had a single candidate under it:

  1. "The bark board is the wrong size. Three of four clauses pass and that one
     fails."
  2. "1.9 s of picture in a 6.5 s slot -- 4.5 s of this beat is one frozen
     frame. It is the biggest ratio in the episode."

Fault 2 is a MOTION fault and it cannot be attacked first: an i2v pass needs an
init, and the init this beat has is a pre-canon guard. On 2026-08-22 the founder
ratified guard 1 by posting one of our own frames back at us
(`taste/refs/guard1-canon-founder-0822.png`, canon entry
`ep2-guard1-canon-founder-0822`), which retires every b06 draft above this one:
they draw a ROUND BALD BUREAUCRAT IN MISMATCHED ARMOUR, and he is not the
character any more. So the plate comes first and the motion is the next rung.

THE STACK IS THE CINEMATIC ONE AND THAT IS THE WHOLE POINT. The 08-22 ladder
entry rules the flat goblin-era tag stack OFF for human subjects and names the
replacement by file: `goblin_ipa_beat.py --character guard --arm window4`,
IP-Adapter at scale 0.6 off after the first 15% of the denoise, over a
box-resident refs dir, with a PROSE prompt closing on the ratified 14-token
style tail. That is the recipe that drew the frame he called canon
(`pipeline/jobs/ep2-b09-cast-0817.yaml`), and the immediate parent for the
staging and publish shape is `pipeline/jobs/ep2-guardcast2-a-0822.yaml`, which
ran this exact route against this exact reference on this exact beat number
eleven hours ago.

WHY THE ADAPTER IS RIGHT HERE AND WAS WRONG ELEVEN HOURS AGO. `derive_
guardcast2b_0822` took the adapter OUT, and its reasoning is not reversed here,
it is inverted by the question. A CASTING sheet exists to VARY the face, so
conditioning it on one man's portrait pins the only axis it wanted to move --
and cell A came back as a copy of guard 1 with his own hand on his cheek. THIS
job wants exactly that outcome: it is not casting anybody, it is drawing the man
who is already cast. The failure mode of round 2 is this round's success
criterion.

AND THE COMPOSITION LOCK DOES NOT APPLY. 2b measured WHY the adapter cloned the
pose: the reference is a face close-up and the request was a face close-up, so
at the steps where the sampler fixes coarse structure the adapter had a matching
composition to hand over. Beat 06 asks for a MEDIUM SHOT of a standing man
holding a board at chest height -- the b09 geometry, where the same reference
set at the same scale in the same window gave up its colour and kept quiet about
layout. Pre-registered as a fail mode below anyway, because "measured once" is
not "cannot happen".

WHAT IS DELIBERATELY *NOT* IN THIS JOB, AND IT IS A DEPARTURE FROM THE FILED
NIGHT ORDER. The order says "guard-1 ref + 5-head skeleton". The skeleton is not
here, and the reason is mechanical rather than a preference: `goblin_ipa_beat.py`
-> `goblin_ipa_sample.py` exposes no ControlNet flag at all, so a skeleton means
switching to `controlnet_plate.py` -- which is a DIFFERENT DRIVER, and the one
whose openpose+no-reference configuration the founder rejected on 08-22. Doing
both at once would change the driver, the conditioning class and the prompt
family in one fire, and the sample would answer none of them. So: reference
first, on the proven driver, one sample. IF the man comes back child-proportioned
-- the specific thing a 5-head skeleton buys -- that is the next rung and it is
named in `next_rung` on the spec rather than guessed at now. The 08-22 evidence
says the words carry the age (`A grown guard man` drew a grown man at 10 of 10
in guardcast2d), so the skeleton is the fallback, not the opener.

THE BOARD SIZE IS ANSWERED POSITIVELY. `a large flat slab of rough brown bark
... as wide as his shoulders` is in the POSITIVE; `no small board` is in the
negative as containment only. This tree has five recorded firings of the law
that a negative does not place a thing -- beats 05, 10, 19, the b19 `glossy`
case and the b07 wardrobe re-run tonight, where banning the goblin's collar by
name moved nothing. Asserting the size is the lever; banning the other size is
not.

77 positive / 70 negative CLIP tokens, counted offline with assert_under_clip77
before the draft was written, because the box's clip77 guard is the backstop and
not the check.

$0 -- local card, no provider, no spend. ~3 minutes of GPU. Nothing here is a
pick: R4 is the founder's and this job stages a candidate, at most.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                                  # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77           # noqa: E402

BEAT = 6
SLUG = "the-clipboard"
NODE = "002b-first-citizen"
SPEC_ID = "ep2-b06-guard1-0822"
DRAFT_KEY = "authored_b06_guard1canon_0822"
REF_REPO_PATH = "taste/refs/guard1-canon-founder-0822-sq.png"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       + REF_REPO_PATH)
REF_PREFIX = "guard1sq"
# The sampler prepends this before encoding -- see assert_compiled_positive_fits.
COUNT_TAG = "1boy"
WORK = r"C:\banyan-farm\ep2-b06-guard1-0822"
REFS = WORK + r"\refs"
OUT = WORK + r"\out"
# The sampler's own arithmetic: wg.SEED (20260719) + BEAT + seed_start * 1000.
SEED = 20260719 + BEAT

BAR = (
    "ONE 832x1216 png, judged AT 1:1 against taste/refs/guard1-canon-founder-0822.png "
    "on a MATCHED-SCALE face sheet -- the r11a lesson from the goblin lane, where a "
    "pick was declared off two full frames at different head sizes and flipped the "
    "moment the crops were the same height. PRE-REGISTERED, BEFORE THE PIXELS EXIST: "
    "(1) HE IS GUARD 1 -- dark cropped hair, round wire-rim glasses, the same face. "
    "Unlike the casting sheet, a clone of the reference is a PASS here. (2) A GROWN "
    "MAN. A child, teenager or female read is a DROP. (3) THE BOARD IS LARGE -- a "
    "slab of bark at least as wide as his shoulders, held in BOTH hands at chest "
    "height, with him looking down at it. This is the beat's standing fault and a "
    "small board is a FAIL however good the man is. (4) IT IS BARK, not a clipboard: "
    "no metal clip, no spring clip, no white or lined paper. (5) DETAILED CINEMATIC "
    "ANIME, the look of the reference. Flat, muted or tag-sheet is a fail. (6) The "
    "costume family reads: cream shirt collar and WHITE SHOULDER SASH. (7) A real "
    "grass-and-hedgerow field behind him, not a plain ground. (8) NOTHING GOBLIN: no "
    "green skin, no pointed ears -- tonight's b07 re-run put a pointed ear on this "
    "same guard, so this is a live defect and not a formality. "
    "PRE-REGISTERED FAIL MODES, recorded whether or not they fire: the adapter "
    "handing over the reference's COMPOSITION (a face close-up instead of a medium "
    "shot, and/or the hand-on-cheek) -- measured to happen when reference and request "
    "geometries agree, which here they do not; the board arriving small anyway, which "
    "would mean scale is not reachable by words on this stack and the next rung is an "
    "object composite; child proportions, whose named answer is a 5-head skeleton on "
    "controlnet_plate.py."
)


# ---------------------------------------------------------------------------
# THE COUNT TAG IS PART OF THE POSITIVE AND assert_under_clip77 DOES NOT SEE IT.
# Learned at 23:23 on 2026-08-22, twice in one minute, for zero GPU seconds
# because the `dry` step caught it: both this job and its beat-05 sibling were
# authored at 77 bare tokens, which is exactly the ceiling -- and then
# goblin_ipa_sample PREPENDS the beat's count tag (`1boy, ` / `2boys, `) before
# encoding. The compiled positive came to 80, the compressor dropped from the
# TAIL, and the tail is the ratified style anchor. Result: `STYLE ANCHOR
# MISSING (`very aesthetic` not in positive)` and `POSITIVE DROPPED: quality |
# very aesthetic.`, rc=1, nothing drawn.
#
# assert_under_clip77 was doing its job correctly and the job was the wrong one:
# it measures the string in the yaml, and the string the sampler encodes is a
# different, longer string. Counting the wrong string is the same class of
# error as judging a face at the wrong scale, which is the other thing this
# night has been about.
def assert_compiled_positive_fits(label, positive, count_tag):
    """Count what the SAMPLER will encode, not what the drafts file holds."""
    import clip_token_count
    clip = clip_token_count.Clip()
    compiled = "%s, %s%s" % (count_tag, positive[:1].lower(), positive[1:])
    n = clip.count(compiled)[0] + clip_token_count.SPECIALS
    if not positive.rstrip().endswith("very aesthetic"):
        raise SystemExit("!! %s does not end on the ratified style anchor "
                         "`very aesthetic`" % label)
    if n > clip_token_count.CEILING - 1:
        raise SystemExit(
            "!! %s compiles to %d tokens once the `%s` count tag is prepended, "
            "against CLIP's %d with one token of headroom reserved. The "
            "compressor drops from the TAIL, and the tail is the style anchor, "
            "so this does not render badly -- it refuses at the dry step with "
            "STYLE ANCHOR MISSING. Shorten the positive."
            % (label, n, count_tag, clip_token_count.CEILING))
    return n


def refs_sha():
    with open(os.path.join(REPO, REF_REPO_PATH), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def drafts_sha():
    with open(os.path.join(REPO, "pipeline", "wave-drafts.yaml"), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def draft_text():
    import yaml
    with open(os.path.join(REPO, "pipeline", "wave-drafts.yaml"),
              encoding="utf-8") as fh:
        return yaml.safe_load(fh)["beats"][BEAT][DRAFT_KEY]


def frame_name():
    """The exact file the sampler writes. NOT A GLOB -- see the parent's note."""
    return "%02d-%s-ipa-r0-w015-s0.png" % (BEAT, SLUG)


def _stage_step():
    body = (
        "import hashlib, os, shutil, urllib.request\n"
        "dst = r\"%(refs)s\"\n"
        "os.makedirs(dst, exist_ok=True)\n"
        "want = \"%(sha)s\"\n"
        "with urllib.request.urlopen(\"%(url)s\", timeout=120) as r:\n"
        "    blob = r.read()\n"
        "got = hashlib.sha256(blob).hexdigest()\n"
        "if got != want:\n"
        "    raise SystemExit(\"!! guard-1 reference sha %%s, wanted %%s -- \"\n"
        "                     \"refusing to condition on unknown bytes\"\n"
        "                     %% (got, want))\n"
        "first = os.path.join(dst, \"%(pfx)s-s0.png\")\n"
        "with open(first, \"wb\") as fh:\n"
        "    fh.write(blob)\n"
        "for i in (1, 2, 3):\n"
        "    shutil.copy2(first, os.path.join(dst, \"%(pfx)s-s%%d.png\" %% i))\n"
        "print(\"reference verified\", got[:12], \"-> 4 slots (3 are byte-copies; \"\n"
        "      \"dedup_cells drops them and one cell is drawn)\")\n"
    ) % {"refs": REFS, "sha": refs_sha(), "url": RAW, "pfx": REF_PREFIX}
    return {"name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def _sample_argv():
    return [
        r"C:\banyan-farm\venv\Scripts\python.exe",
        r"C:\banyan-farm\wave-goblin-prep\goblin_ipa_beat.py",
        "--beat", str(BEAT),
        "--character", "guard",
        "--harness", r"C:\banyan-farm\wave-goblin-prep",
        "--root", r"C:\banyan-farm\wave-goblin-prep\repo",
        "--refs", REFS,
        "--ref-prefix", REF_PREFIX,
        "--out", OUT,
        "--draft-key", DRAFT_KEY,
        "--arm", "window4",
        "--seeds", "1",
        "--seed-start", "0",
        "--expect-drafts-sha256", drafts_sha(),
        "--task", SPEC_ID,
    ]


def _publish_step():
    body = (
        "import glob, hashlib, os, shutil\n"
        "srcdir = r\"%(out)s\"\n"
        "dst = r\"C:\\banyan-farm\\courier-box\\farm-out\\%(jid)s\"\n"
        "os.makedirs(dst, exist_ok=True)\n"
        "want = \"%(frame)s\"\n"
        "png = os.path.join(srcdir, want)\n"
        "if not os.path.isfile(png):\n"
        "    have = sorted(os.path.basename(f) for f in glob.glob(srcdir + \"/*.png\"))\n"
        "    raise SystemExit(\"!! %%s was not written; the dir holds %%s\" %% (want, have))\n"
        "src = [png] + sorted(glob.glob(png + \".*\"))\n"
        "lines = []\n"
        "for f in src:\n"
        "    shutil.copy2(f, dst)\n"
        "    c = os.path.join(dst, os.path.basename(f))\n"
        "    with open(c, \"rb\") as fh:\n"
        "        lines.append(hashlib.sha256(fh.read()).hexdigest() + \"  \"\n"
        "                     + os.path.basename(f))\n"
        "with open(os.path.join(dst, \"%(jid)s.sha256\"), \"w\", newline=\"\\n\") as fh:\n"
        "    fh.write(\"\\n\".join(lines) + \"\\n\")\n"
        "print(\"published\", len(src), \"file(s) ->\", dst)\n"
    ) % {"out": OUT, "jid": SPEC_ID, "frame": frame_name()}
    return {"name": "publish",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def build():
    return {
        "id": SPEC_ID,
        "task": SPEC_ID,
        "node": NODE,
        "beat": BEAT,
        "runner": "box",
        "priority": 6,
        "needs_gpu": True,
        "max_attempts": 1,
        "sample": True,
        "est_minutes": 3,
        "needs": ["cuda", "vram20", "farm-venv"],
        "owner": ("night iteration lane, 2026-08-22 -- beat 06's first plate on the "
                  "ratified guard"),
        "consumer": (
            "BEAT 06's SLOT IN /review/ep2-beats-0821, which has carried two named "
            "faults and ZERO candidates since the page was built. If the frame passes "
            "the bar it is staged as this beat's first candidate and becomes the init "
            "for the motion rung that answers the beat's second fault -- 4.5 s of a "
            "6.5 s slot is one frozen frame, the worst ratio in the episode. If it "
            "fails, the failure names the next rung and costs three GPU minutes."),
        "success": BAR,
        "why": (
            "BEAT 06's INIT IS A CHARACTER WHO NO LONGER EXISTS. Every b06 draft "
            "before this one draws a round bald bureaucrat in mismatched armour; on "
            "2026-08-22 the founder ratified guard 1 as a specific man -- dark cropped "
            "hair, round wire-rim glasses, cream shirt, white shoulder sash -- by "
            "posting one of our own frames back at us. A motion pass cannot fix a "
            "wrong man, so the plate is first. Same job also answers the beat's "
            "board-size fault, positively, in the words. Route: the cinematic stack "
            "the 08-22 ladder entry names by file -- goblin_ipa_beat.py --character "
            "guard --arm window4, IP-Adapter 0.6 off after the first 15%% of the "
            "denoise, over a box-resident refs dir holding the ratified frame, prose "
            "prompt out of wave-drafts.yaml closing on the ratified style tail. "
            "Minutes of local GPU, $0. Full trace: pipeline/derive_b06_guard1_0822.py."),
        "script_authority": (
            "Node 002b-first-citizen, live script `002b-t0-c`, `approved_by: founder`, "
            "`approved_on: 2026-08-03`. A STILL PLATE on an approved node: no voice, "
            "no motion, no episode assembly, no publication. review/ep2-ship-0821 is "
            "not touched by this job."),
        "script_line": ("Beat 06 THE CLIPBOARD: the guard turns the bark board over "
                        "and reads it. Drawn here WITH the prop, at chest height, "
                        "because the prop's size is the beat's standing fault."),
        "env": {
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1",
            "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "steps": [
            _stage_step(),
            {"name": "dry", "argv": _sample_argv() + ["--dry"]},
            {"name": "sample", "argv": _sample_argv()},
            _publish_step(),
        ],
        "recipe_trace": (
            "driver + conditioning: pipeline/jobs/ep2-guardcast2-a-0822.yaml (same "
            "beat number, same reference, same arm, ran 2026-08-22); the recipe's own "
            "parent is pipeline/jobs/ep2-b09-cast-0817.yaml, which drew the frame the "
            "founder ratified. Reference %s sha %s, a top-anchored 832x832 crop of "
            "taste/refs/guard1-canon-founder-0822.png. Prompt "
            "pipeline/wave-drafts.yaml beats.6.%s, file sha %s, enforced at RUN time "
            "by --expect-drafts-sha256 so a hand-sync between filing and firing "
            "cannot swap the wording underneath it."
            % (REF_REPO_PATH, refs_sha()[:16], DRAFT_KEY, drafts_sha()[:16])),
        "one_sample_rule": (
            "ONE CELL, ONE SEED. Two things change against the guardcast2-a parent -- "
            "the draft (a casting head with `no hands, no clipboard` becomes a medium "
            "shot with a prop in both hands) and the beat's own consumer. The driver, "
            "the reference bytes, the arm, the scale, the window, the size and the "
            "seed arithmetic are all untouched. Nothing scales off this frame until "
            "it has been looked at at 1:1."),
        "next_rung": (
            "NAMED, NOT FIRED, so the failure has somewhere to go: (a) if the man is "
            "right and the BOARD is small, scale is not reachable by words on this "
            "stack and the next rung is an object composite drawn into the plate, the "
            "sapcomp route, not a fourth wording; (b) if the man reads CHILD, the next "
            "rung is a 5-head openpose skeleton, which means moving to "
            "controlnet_plate.py with --ip-ref and is a driver change, deliberately "
            "not bundled here; (c) if he is right, the next rung is i2v motion off "
            "THIS plate -- the board turning over -- which is what fault 2 needs and "
            "what makes 4.5 s of frozen frame into picture."),
        "seed_note": (
            "Seed is the sampler's arithmetic, pinned by construction: wg.SEED "
            "(20260719) + beat (6) + seed_start (0) * 1000 = %d. Same seed as "
            "guardcast2 cell A, deliberately: the prompt is the variable and holding "
            "the seed is what makes the two frames comparable." % SEED),
        "frame_count": (
            "ONE png. window4 enumerates four reference slots and the stage step "
            "writes four byte-identical copies of the single reference, so dedup_cells "
            "drops three and one cell is drawn at one seed. Stated rather than "
            "discovered by the artifact check."),
        "artifacts": [OUT + "\\" + frame_name()],
    }


def _selftest():
    spec = build()
    text = draft_text()
    i = text.index("No girl")
    npos = assert_under_clip77("b06 guard1 positive", text[:i].strip())
    nneg = assert_under_clip77("b06 guard1 negative", text[i:].strip())
    assert npos <= 77 and nneg <= 77, (npos, nneg)
    ncomp = assert_compiled_positive_fits("b06 guard1 compiled positive",
                                          text[:i].strip(), COUNT_TAG)

    argv = spec["steps"][2]["argv"]
    assert "--arm" in argv and argv[argv.index("--arm") + 1] == "window4"
    assert argv[argv.index("--draft-key") + 1] == DRAFT_KEY
    assert argv[argv.index("--character") + 1] == "guard"
    assert argv[argv.index("--refs") + 1] == REFS
    assert argv[argv.index("--expect-drafts-sha256") + 1] == drafts_sha()
    # THE ARM STRING IS LOAD-BEARING (cost a render in derive_guardcast2b_0822):
    # nothing here may rename it, and nothing here may switch drivers.
    assert argv[1].endswith("goblin_ipa_beat.py"), argv[1]
    assert "--control" not in argv, "no ControlNet on this driver -- see the docstring"
    assert "--dry" in spec["steps"][1]["argv"]
    assert "--dry" not in argv
    # The board size must be ASSERTED, not merely banned.
    assert "as wide as his shoulders" in text
    assert "large flat slab of rough brown bark" in text
    assert "no small board" in text
    # The species negatives the b07 re-run earned tonight.
    for term in ("no goblin", "no green skin", "no pointed ears"):
        assert term in text, term
    # The ratified man, by his two identifying features.
    assert "dark cropped hair" in text and "round wire-rim glasses" in text
    # The ratified style tail, verbatim.
    assert text.rstrip().split("aesthetic")[0].endswith(
        "cinematic lighting, masterpiece, best quality, very ")
    assert spec["artifacts"] == [OUT + "\\" + frame_name()]
    print("SELFTEST OK  %s  pos=%d (compiled %d with `%s`) neg=%d  seed=%d  drafts=%s"
          % (SPEC_ID, npos, ncomp, COUNT_TAG, nneg, SEED, drafts_sha()[:12]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    _selftest()
    if not a.write:
        print("dry run -- nothing written. Pass --write.")
        return 0
    p = derive_spec.write(build(), "pipeline/jobs/%s.yaml" % SPEC_ID,
                          force=a.force)
    # derive_fetch_guard.assert_fetch_urls_resolve() only knows farm-out URLs
    # and REFUSES a spec with none, which is right for a child fetching a
    # parent's output and wrong here: this job's only fetch is a committed
    # taste/refs file, which retoken cannot rename because no job id appears in
    # its path. The guard's actual concern -- "the address is invented" -- is
    # answered directly, by re-reading the EMITTED yaml and resolving the URL
    # against this working tree, which is exactly what that module does for the
    # farm-out case.
    emitted = open(p, encoding="utf-8").read()
    if RAW not in emitted:
        raise SystemExit("!! the reference URL did not survive into %s" % p)
    if not os.path.isfile(os.path.join(REPO, REF_REPO_PATH)):
        raise SystemExit("!! %s is not in this working tree, so it is not on "
                         "main either and the box's fetch will 404" % REF_REPO_PATH)
    print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
