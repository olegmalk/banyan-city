#!/usr/bin/env python3
r"""BEAT 05 RE-PLATE: BOTH GUARDS, THE SASH, AND A PROVISIONAL GUARD 2.

    python3 pipeline/derive_b05_guards_0822.py --selftest
    python3 pipeline/derive_b05_guards_0822.py --write

THE FAULT THIS ANSWERS, in the beats page's own words: "Neither guard wears the
sash you froze for the cast -- the clip contradicts a ruling that is already
final." Beat 05 THE PATROL has that fault, three others, and ZERO candidates.
What it also has is the one thing four rounds of rewording never bought: "Two
figures in the field from the first frame to the 117th -- never one, never
three." That win is not put at risk here -- both men are PLACED, left and right,
which is the wording shape that finally got a second figure into beat 07.

THE ROUTE IS b06's, FILED AN HOUR AGO, AND THAT IS DELIBERATE. Same driver
(`goblin_ipa_beat.py --character guard --arm window4`), same box-resident refs
dir holding `taste/refs/guard1-canon-founder-0822-sq.png`, same IP-Adapter scale
and window, same style tail, same seed arithmetic. Only the beat and the draft
move. Filing the two together means that if b06 comes back right and b05 comes
back wrong, the difference is the SECOND FIGURE and not the stack -- which is
the question this beat has never had a clean read on.

GUARD 2 IS NOT CAST AND NOTHING HERE CASTS HIM. The casting sheet is at
/review/ep2-guardcast2-0822 and the pick is R4. This draft takes CELL F --
grey-streaked hair, thick moustache, jowly face -- and everything downstream of
it is PROVISIONAL, marked as such on the page, and replaced in one edit when his
letter arrives. F rather than B or J on tonight's own b07 finding: the guard's
white sash landed and his collar did not, and the difference between them is
that the sash has NO COMPETITOR in the sentence while a collar has the goblin's
three clauses upstream. Of the three strong reads, F's thick grey moustache is
the only feature the other man in this frame cannot also have. B (light sandy
hair, long thin face) and J (short red hair, freckles) are written as the next
rung and are NOT fired, because the recipe running two identities through one
adapter window has never been sampled and one cell answers that.

THE ADAPTER CARRIES GUARD 1 AND MUST NOT CARRY GUARD 2, and that is the specific
risk this sample exists to measure. The reference is one man's face. Round 2b
measured that a face-close-up reference hands over its composition when the
request is also a face close-up; here the request is a two-figure medium shot,
so the geometry disagrees -- but nothing in this tree has ever measured what a
single-identity reference does to the SECOND figure in a two-figure frame. The
pre-registered fail mode is TWO GUARD ONES, and it is the most likely one.

$0, local card, ~3 GPU minutes, one cell, one seed.
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

BEAT = 5
SLUG = "the-patrol"
NODE = "002b-first-citizen"
SPEC_ID = "ep2-b05-guards-f-0822"
DRAFT_KEY = "authored_b05_guards_f_0822"
REF_REPO_PATH = "taste/refs/guard1-canon-founder-0822-sq.png"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       + REF_REPO_PATH)
REF_PREFIX = "guard1sq"
WORK = r"C:\banyan-farm\ep2-b05-guards-f-0822"
REFS = WORK + r"\refs"
OUT = WORK + r"\out"
# The sampler's own arithmetic: wg.SEED (20260719) + BEAT + seed_start * 1000.
SEED = 20260719 + BEAT

BAR = (
    "ONE 832x1216 png, judged AT 1:1 and on a MATCHED-SCALE two-face sheet beside "
    "taste/refs/guard1-canon-founder-0822.png -- the r11a lesson, where a pick was "
    "declared off full frames at different head sizes and flipped the moment the "
    "crops were the same height. PRE-REGISTERED, BEFORE THE PIXELS EXIST: "
    "(1) TWO MEN, side by side, both whole and both facing out -- one is a DROP and "
    "three is a DROP. This beat's one existing win is two figures for 117 frames and "
    "the plate may not lose it. (2) THEY ARE DIFFERENT MEN. The left is guard 1 as "
    "ratified (dark cropped hair, round wire-rim glasses); the right has a THICK GREY "
    "MOUSTACHE and a jowly face and has neither the cropped hair nor the glasses. Two "
    "copies of guard 1 is the headline failure of this job and it is not a note, it "
    "is a FAIL. (3) BOTH WEAR A WHITE SHOULDER SASH -- the beat's own standing fault, "
    "'neither guard wears the sash you froze for the cast', and the reason this plate "
    "exists. A sash on one man only is a HALF PASS and is reported as one. (4) BOTH "
    "ARE GROWN MEN; a child, teenager or female read on either is a DROP. (5) DETAILED "
    "CINEMATIC ANIME, the look of the reference. Flat, muted or tag-sheet fails "
    "however good the casting is. (6) A real tall-grass-and-hedgerow field, not a "
    "plain ground. (7) NOTHING GOBLIN on either man: no green skin, no pointed ears -- "
    "tonight's b07 re-run put a pointed ear on this same guard, so this is a live "
    "defect and not a formality. "
    "PRE-REGISTERED FAIL MODES, recorded whether or not they fire, MOST LIKELY FIRST: "
    "TWO GUARD ONES -- the adapter holds one man's face and nothing in this tree has "
    "ever measured what that does to the SECOND figure in a two-figure frame, which is "
    "the whole reason this is one cell and not three; the moustache landing on the "
    "wrong man, which is the b07 attribute-binding failure with the figures swapped; "
    "the adapter handing over the reference's face-close-up COMPOSITION, measured to "
    "happen when reference and request geometries agree, which here they do not; a "
    "third figure, which four rounds of rewording on this beat did eventually beat "
    "and which `no third man, no crowd` is carrying."
)


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
        "owner": ("night iteration lane, 2026-08-22 -- beat 05's first plate with "
                  "both guards and both sashes"),
        "consumer": (
            "BEAT 05's SLOT IN /review/ep2-beats-0821, which has carried four failing "
            "clauses and ZERO candidates since the page was built. If the frame passes "
            "the bar it is staged as this beat's first candidate -- marked PROVISIONAL "
            "on guard 2, whose casting is R4 and open at /review/ep2-guardcast2-0822 -- "
            "and it becomes the init for the beat's motion rung. If it fails, it "
            "answers the question nothing in this tree has asked: what one man's "
            "reference does to the second figure in a two-figure frame. Three GPU "
            "minutes either way."),
        "success": BAR,
        "why": (
            "BEAT 05 CONTRADICTS A FINAL RULING IN ITS OWN PICTURE: 'neither guard "
            "wears the sash you froze for the cast'. Both sashes are asserted here, "
            "positively, in one clause covering both men, and both men are PLACED left "
            "and right -- the wording shape that finally got a second figure into beat "
            "07 after two empty attempts. Guard 1 is the ratified man; guard 2 is NOT "
            "cast and this draft takes casting cell F provisionally, chosen because a "
            "thick grey moustache is the only feature in the sentence the other man "
            "cannot also have -- tonight's b07 finding, where the sash bound and the "
            "collar did not. Route: the cinematic stack the 08-22 ladder names by file "
            "-- goblin_ipa_beat.py --character guard --arm window4, IP-Adapter 0.6 off "
            "after the first 15%% of the denoise, over a box-resident refs dir holding "
            "the ratified frame. Identical to pipeline/jobs/ep2-b06-guard1-0822.yaml "
            "filed an hour ago, so a b06 pass beside a b05 fail isolates THE SECOND "
            "FIGURE as the cause. $0, minutes of local GPU. Full trace: "
            "pipeline/derive_b05_guards_0822.py."),
        "script_authority": (
            "Node 002b-first-citizen, live script `002b-t0-c`, `approved_by: founder`, "
            "`approved_on: 2026-08-03`. A STILL PLATE on an approved node: no voice, "
            "no motion, no episode assembly, no publication. review/ep2-ship-0821 is "
            "not touched by this job."),
        "script_line": ("Beat 05 THE PATROL: two guards halt and scan an empty "
                        "morning field. Drawn here standing side by side and looking "
                        "out, because the beat's fault is the costume and the cast, "
                        "not the movement."),
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
            "beat, same reference, same arm, ran 2026-08-22); the recipe's own "
            "parent is pipeline/jobs/ep2-b09-cast-0817.yaml, which drew the frame the "
            "founder ratified. Reference %s sha %s, a top-anchored 832x832 crop of "
            "taste/refs/guard1-canon-founder-0822.png. Prompt "
            "pipeline/wave-drafts.yaml beats.5.%s, file sha %s, enforced at RUN time "
            "by --expect-drafts-sha256 so a hand-sync between filing and firing "
            "cannot swap the wording underneath it."
            % (REF_REPO_PATH, refs_sha()[:16], DRAFT_KEY, drafts_sha()[:16])),
        "one_sample_rule": (
            "ONE CELL, ONE SEED, AND THE OTHER TWO CASTING READS ARE HELD. The night "
            "order names cells B, F and J as the sheet's strongest reads; only F is "
            "fired. The reason is not thrift: running TWO identities through a "
            "single-identity adapter window has never been sampled in this tree, and "
            "if it collapses into two guard ones then B and J would have produced two "
            "more pictures of guard 1 and taught nothing. One cell answers that, and B "
            "and J are a wave the moment it comes back clean. Everything else -- "
            "driver, reference bytes, arm, scale, window, size, seed arithmetic -- is "
            "the b06 job's, unchanged."),
        "next_rung": (
            "NAMED, NOT FIRED, so every outcome has somewhere to go: (a) clean two-man "
            "frame -> cells B and J as siblings, same everything, so the founder picks "
            "guard 2 off three plates of the actual beat rather than three casting "
            "heads; (b) TWO GUARD ONES -> the adapter cannot serve two identities from "
            "one reference and the answer is per-figure conditioning (--ip-ref twice "
            "with --ip-mask-capsules on controlnet_plate.py, which the b08 lane already "
            "wired), not another wording; (c) moustache on the wrong man -> the b07 "
            "attribute-binding problem, and the lever is the same one: give guard 1 a "
            "feature guard 2 cannot have, rather than banning the crossover; (d) clean "
            "-> i2v motion off THIS plate, the halt-and-scan."),
        "seed_note": (
            "Seed is the sampler's arithmetic, pinned by construction: wg.SEED "
            "(20260719) + beat (5) + seed_start (0) * 1000 = %d. It differs from the "
            "b06 job's by exactly one, which is the beat number, and that is the "
            "sampler's arithmetic rather than a choice -- the two jobs are otherwise "
            "seed-identical and neither can collide with any casting cell." % SEED),
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
    npos = assert_under_clip77("b05 guards-f positive", text[:i].strip())
    nneg = assert_under_clip77("b05 guards-f negative", text[i:].strip())
    assert npos <= 77 and nneg <= 77, (npos, nneg)

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
    # BOTH figures must be PLACED. Beat 07 came back empty twice for naming a
    # figure without saying where he goes, and this beat's one existing win is
    # two figures held for 117 frames.
    assert "The left man" in text and "The right man" in text
    assert "Two grown guard men" in text
    # THE SASH IS THE BEAT'S STANDING FAULT and it is asserted for BOTH men in
    # one clause, positively. A negative cannot place a garment -- six firings.
    assert "Both wear white shoulder sashes" in text
    # The two men must be DISTINGUISHABLE, and the distinguishing feature must
    # be one the other man cannot also have (tonight's b07 finding).
    assert "dark cropped hair and round wire-rim glasses" in text
    assert "thick grey moustache" in text
    # Figure COUNT containment: this beat has fought a third figure for four
    # rounds and won; the negative carries the win forward.
    assert "no third man" in text and "no crowd" in text
    # The species negatives the b07 re-run earned tonight.
    for term in ("no goblin", "no green skin", "no pointed ears"):
        assert term in text, term
    # NOTHING HERE CASTS GUARD 2. If a future edit ever drops the word
    # PROVISIONAL out of the consumer, this selftest fails rather than letting a
    # taste call be made by a deriver.
    assert "PROVISIONAL" in spec["consumer"]
    # The ratified style tail, verbatim.
    assert text.rstrip().split("aesthetic")[0].endswith(
        "cinematic lighting, masterpiece, best quality, very ")
    assert spec["artifacts"] == [OUT + "\\" + frame_name()]
    print("SELFTEST OK  %s  pos=%d neg=%d  seed=%d  drafts=%s"
          % (SPEC_ID, npos, nneg, SEED, drafts_sha()[:12]))
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
