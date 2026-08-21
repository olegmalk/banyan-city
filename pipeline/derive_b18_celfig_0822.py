#!/usr/bin/env python3
r"""BEAT 18: ONE STYLIZED-ANIME FIG, BESIDE THE ONE THAT IS ALREADY PASSING.

    python3 pipeline/derive_b18_celfig_0822.py --selftest
    python3 pipeline/derive_b18_celfig_0822.py --write

WHAT THIS IS NOT. It is not a fix. Beat 18 PASSES on its own bar -- motion in
all four quarters, no light pumping, the named pick of three seeds -- and its
one recorded fault is a hold, not the picture: 5.0 s of footage in an 11.0 s
slot. Nothing here touches the cut and nothing here is a swap.

WHAT IT IS. A second option in a different DIALECT, so the author has a choice
on a beat where the only open question filed against him is a material one --
`Open and yours: matte or gloss on the fig` -- and he has never been shown the
fig drawn any other way. Every b18 plate this tree has ever made asks for `held
macro, extreme close-up ... warm amber afternoon light` and gets back a
rendered, lit, near-photographic fruit. The house dialect for HUMANS was
re-ratified on 2026-08-22 -- detailed cinematic anime, and the finding that
came with it was that THE STYLE COMES FROM THE WORDS, measured on the guard
casting sheet: same checkpoint, same absence of any reference, and round 2's
prose-plus-style-tail was unmistakable cinematic anime where round 1's booru tag
list was flat. That finding has never been pointed at the fig.

SO THE ONE VARIABLE IS THE DIALECT, and it is spelled out rather than implied:
`cel shaded anime illustration, clean black ink outlines, flat colour, one hard
shadow edge`. The fig's own canon is carried verbatim from
`authored_b18_canon_0816` -- deep purple-violet, green at its neck, matte -- and
the count clause is carried too, because `the only fruit in frame` is the clause
that made this beat's third round the one that worked.

`glossy` and `specular highlight` are in the negative and this is the ONE place
that is not merely hopeful. Beat 19's sapgloss sample measured a specular as a
MID-SIGMA effect reachable by denoise strength, and measured `glossy` in the
negative arriving anyway -- the positive-placement law's fifth firing. So the
negative here is containment, and the thing actually doing the work is `matte
and dusty` plus `flat colour` in the POSITIVE. Recorded so that if a gloss
arrives, nobody reads it as a surprise.

THE STACK IS THE NO-ADAPTER, NO-CONTROLNET ONE, deliberately. The fig has a
licence-clean reference set on the box, and it is not used: conditioning a
STYLE question on a photographic reference would fight the only variable this
job has. Parent is `pipeline/jobs/ep2-guardcast2b-a-0822.yaml` -- prose prompt
and negative baked into the spec's own payload, driver fetched by sha at run
time, `--arm nocontrol`, 40 steps, cfg 7.5, 832x1216.

THE ARM STRING IS `nocontrol` AND IT IS LOAD-BEARING. controlnet_plate.py gates
its whole ControlNet branch on the literal string; a plausible synonym costs a
run at rc 6 in one second. Asserted in --selftest.

TOKENS ARE COUNTED ON THE STRING THE SAMPLER SEES, which on this route is the
payload file byte-for-byte -- there is no count tag prepended here, unlike the
goblin_ipa route that refused two guard jobs an hour ago. 75 positive, 68
negative, both under 77, both ending where they are meant to.

$0, ~2 minutes of local GPU, one seed, one frame. The pick is R4's.
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

BEAT = 18
NODE = "002b-first-citizen"
SPEC_ID = "ep2-b18-celfig-0822"
WORK = r"C:\banyan-farm\ep2-b18-celfig-0822"
DRIVER = "controlnet_plate.py"
ARM = "nocontrol"
SEED = 20260818
RAW_BASE = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"

POSITIVE = (
    "One small deep purple-violet fig, green at its neck, matte and dusty, "
    "hanging from the thin bending stem of a tiny sapling against a soft pale "
    "sky, the only fruit in frame, cel shaded anime illustration, clean black "
    "ink outlines, flat colour, one hard shadow edge, extreme close-up, "
    "cinematic lighting, masterpiece, best quality, very aesthetic")

NEGATIVE = (
    "photorealistic, 3d render, abstract, text, watermark, signature, low "
    "quality, blurry, deformed, jpeg artifacts, glossy, specular highlight, "
    "second fruit, apple, red fruit, grapes, berry cluster, face, eyes, "
    "person, chibi, mascot, white background, dark, night, photorealism")

BAR = (
    "ONE 832x1216 png, judged by eye BESIDE the frame already in the cut, at the "
    "same size on one sheet. PRE-REGISTERED: (1) A STRANGER WOULD CALL IT A FIG -- "
    "the beat's own done_when, and the clause three rounds were spent on. (2) "
    "EXACTLY ONE fruit in frame. Two is a DROP, not a note. (3) PURPLE-VIOLET with "
    "a green neck, and MATTE -- no specular lobe. (4) IT LOOKS DRAWN: clean ink "
    "outline, flat colour fields, ONE hard shadow terminator. A soft airbrushed or "
    "photographic fruit means the dialect did not carry to an object and that is "
    "the finding, negative but real. (5) It is a CHOICE beside the current frame, "
    "not a replacement -- a pass here changes nothing in the cut by itself. "
    "PRE-REGISTERED FAIL MODES: a gloss arriving despite the negative, which is "
    "measured behaviour on this tree and would confirm rather than surprise; the "
    "cel words flattening the fig into a sticker with no form at all, which is the "
    "opposite failure and the reason `one hard shadow edge` is in the positive "
    "instead of `no shading`; a second fruit, which every wording round on this "
    "beat has had to fight.")


def driver_sha():
    with open(os.path.join(REPO, "pipeline", DRIVER), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def out_png():
    return "%s-%s.png" % (SPEC_ID, ARM)


def _stage_step():
    body = (
        "import hashlib, os, urllib.request\n"
        "base = \"%(base)s\"\n"
        "root = r\"%(work)s\\src\"\n"
        "want = [(\"%(drv)s\", os.path.join(root, \"pipeline\"),\n"
        "         \"%(sha)s\")]\n"
        "for name, dst, sha in want:\n"
        "    os.makedirs(dst, exist_ok=True)\n"
        "    with urllib.request.urlopen(base + \"pipeline/\" + name, timeout=120) as r:\n"
        "        blob = r.read()\n"
        "    got = hashlib.sha256(blob).hexdigest()\n"
        "    if got != sha:\n"
        "        raise SystemExit(\"!! %%s sha %%s, wanted %%s\" %% (name, got, sha))\n"
        "    with open(os.path.join(dst, name), \"wb\") as fh:\n"
        "        fh.write(blob)\n"
        "    print(\"staged\", name, got[:12])\n"
    ) % {"base": RAW_BASE, "work": WORK, "drv": DRIVER, "sha": driver_sha()}
    return {"name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def _plate_argv():
    return [
        r"C:\banyan-farm\venv\Scripts\python.exe",
        WORK + "\\src\\pipeline\\" + DRIVER,
        "--root", WORK + r"\src",
        "--task", SPEC_ID,
        "--arm", ARM,
        "--seed", str(SEED),
        "--steps", "40",
        "--cfg", "7.5",
        "--width", "832",
        "--height", "1216",
        "--prompt-file", WORK + r"\prompt.txt",
        "--negative-file", WORK + r"\negative.txt",
        "--out", WORK + r"\out",
    ]


def _publish_step():
    body = (
        "# The courier pushes from farm-out and from nowhere else.\n"
        "# The CONDITIONS travel with the frame: prompt and negative go too, so\n"
        "# this can be re-read months from now without the spec in hand.\n"
        "import glob, hashlib, os, shutil\n"
        "dst = \"C:/banyan-farm/courier-box/farm-out/%(jid)s\"\n"
        "os.makedirs(dst, exist_ok=True)\n"
        "files = sorted(glob.glob(\"%(work)s/out/%(png)s*\")\n"
        "               + glob.glob(\"%(work)s/prompt.txt\")\n"
        "               + glob.glob(\"%(work)s/negative.txt\"))\n"
        "lines = []\n"
        "for f in files:\n"
        "    shutil.copy2(f, dst)\n"
        "    c = os.path.join(dst, os.path.basename(f))\n"
        "    with open(c, \"rb\") as fh:\n"
        "        lines.append(hashlib.sha256(fh.read()).hexdigest() + \"  \"\n"
        "                     + os.path.basename(f))\n"
        "with open(os.path.join(dst, \"%(jid)s.sha256\"), \"w\", newline=\"\\n\") as fh:\n"
        "    fh.write(\"\\n\".join(sorted(lines)) + \"\\n\")\n"
        "print(\"published\", len(files), \"file(s) + manifest ->\", dst)\n"
        "raise SystemExit(0 if len(files) >= 3 else 1)\n"
    ) % {"jid": SPEC_ID, "work": WORK.replace("\\", "/"), "png": out_png()}
    return {"name": "publish",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def build():
    return {
        "id": SPEC_ID,
        "task": SPEC_ID,
        "node": NODE,
        "beat": BEAT,
        "runner": "box",
        "priority": 7,
        "needs_gpu": True,
        "max_attempts": 1,
        "sample": True,
        "est_minutes": 2,
        "needs": ["cuda", "vram12", "sdxl-venv"],
        "owner": ("night iteration lane, 2026-08-22 -- one stylized-anime fig beside "
                  "the passing one"),
        "consumer": (
            "THE FOUNDER, on /review/ep2-beats-0821 beat 18, as a SECOND OPTION beside "
            "the frame already in the cut. The only question filed against him on this "
            "beat is a material one -- matte or gloss -- and he has never been shown "
            "the fig drawn in any dialect but the rendered one. A pass here changes "
            "nothing in the cut by itself; it gives an open taste question a second "
            "set of pixels, which is the standing directive for open cards."),
        "success": BAR,
        "why": (
            "BEAT 18 PASSES AND IS NOT BEING FIXED. Every fig plate this tree has made "
            "asks for a held macro in warm amber light and gets back a rendered, lit, "
            "near-photographic fruit. On 2026-08-22 the house dialect for humans was "
            "re-ratified as detailed cinematic anime, and the finding that came with "
            "it -- measured on the guard casting sheet, same checkpoint, no reference "
            "either round -- is that THE STYLE COMES FROM THE WORDS. That finding has "
            "never been pointed at the fig. One variable: the dialect clause. The "
            "fig's canon and its count clause are carried verbatim. No adapter and no "
            "ControlNet, because conditioning a STYLE question on a photographic "
            "reference would fight the only variable there is. $0, ~2 GPU minutes. "
            "Full trace: pipeline/derive_b18_celfig_0822.py."),
        "script_authority": (
            "Node 002b-first-citizen, live script `002b-t0-c`, `approved_by: founder`, "
            "`approved_on: 2026-08-03`. A STILL PLATE on an approved node: no voice, no "
            "motion, no episode assembly, no publication, and review/ep2-ship-0821 is "
            "not touched."),
        "script_line": ("Beat 18 THE DECISION: one fig on a trembling stem. Drawn here "
                        "still, because the question is the fruit's LOOK and not its "
                        "movement."),
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
        "payload": {
            WORK + r"\prompt.txt": POSITIVE,
            WORK + r"\negative.txt": NEGATIVE,
        },
        "steps": [
            _stage_step(),
            {"name": "plate", "argv": _plate_argv()},
            _publish_step(),
        ],
        "recipe_trace": (
            "parent pipeline/jobs/ep2-guardcast2b-a-0822.yaml -- same driver "
            "(pipeline/%s sha %s, fetched and sha-checked at run time), same "
            "--arm %s, same 40 steps / cfg 7.5 / 832x1216, same payload-baked prompt "
            "so no drafts file can drift between filing and firing. The fig's canon "
            "wording is pipeline/wave-drafts.yaml beats.18.authored_b18_canon_0816, "
            "carried by hand into the payload rather than by draft key, because this "
            "route reads no drafts file at all."
            % (DRIVER, driver_sha()[:16], ARM)),
        "one_sample_rule": (
            "ONE FRAME, ONE SEED, AND NOTHING SCALES OFF IT. The dialect clause has "
            "never been tried on an object in this tree. If it lands, the same four "
            "words are a candidate rung for the other fig beats (1, 19, 20) and for "
            "the sapling plates -- and each of those is its own sample, not a wave."),
        "seed_note": (
            "Seed %d, fixed and stated. It is NOT the cut frame's 20260871: a different "
            "seed and a different prompt means this frame cannot be read as a "
            "controlled A/B of the dialect alone, and saying so here is cheaper than "
            "someone inferring it later. What it IS is a second option on a taste "
            "question. If the author wants the dialect isolated, the controlled "
            "version is one job at 20260871 with only the four cel words changed."
            % SEED),
        "artifacts": [WORK + r"\out" + "\\" + out_png()],
    }


def _selftest():
    spec = build()
    npos = assert_under_clip77("b18 celfig positive", POSITIVE)
    nneg = assert_under_clip77("b18 celfig negative", NEGATIVE)
    argv = spec["steps"][1]["argv"]
    assert argv[argv.index("--arm") + 1] == ARM == "nocontrol", "arm string"
    assert argv[1].endswith(DRIVER), argv[1]
    assert "--control" not in argv, "nocontrol means no --control is passed"
    assert "--ip-ref" not in argv, "no adapter -- the dialect is the variable"
    assert argv[argv.index("--seed") + 1] == str(SEED)
    # The payload is what the sampler reads, so the payload is what was counted.
    assert spec["payload"][WORK + r"\prompt.txt"] == POSITIVE
    assert spec["payload"][WORK + r"\negative.txt"] == NEGATIVE
    # The ratified style tail, verbatim, and the fig canon it must not lose.
    assert POSITIVE.endswith("masterpiece, best quality, very aesthetic")
    for term in ("deep purple-violet", "green at its neck", "matte",
                 "the only fruit in frame"):
        assert term in POSITIVE, term
    # The dialect clause, which is the entire point of the job.
    for term in ("cel shaded anime illustration", "clean black ink outlines",
                 "flat colour", "one hard shadow edge"):
        assert term in POSITIVE, term
    # Gloss containment is a NEGATIVE and the positive carries the real lever.
    assert "glossy" in NEGATIVE and "specular highlight" in NEGATIVE
    assert "matte and dusty" in POSITIVE
    assert spec["artifacts"] == [WORK + r"\out" + "\\" + out_png()]
    print("SELFTEST OK  %s  pos=%d neg=%d  seed=%d  driver=%s"
          % (SPEC_ID, npos, nneg, SEED, driver_sha()[:12]))
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
    print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
