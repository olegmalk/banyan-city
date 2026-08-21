#!/usr/bin/env python3
r"""GUARD-2 CASTING, ROUND 2 — the sheet re-cut on the recipe the founder ratified.

    python3 pipeline/derive_guardcast2_0822.py --selftest   # assert, write nothing
    python3 pipeline/derive_guardcast2_0822.py --write      # emit the ten specs

WHY THERE IS A ROUND 2. On 2026-08-22 the founder answered
`/review/ep2-guardcast-0822` — twelve cells, ten shown — with one sentence:

    "none of them are right, the style is wrong"

and posted THE BEAT-09 GUARD CLOSE-UP back at us as the contrast. Two rulings
came out of it and both are in pipeline/canon.yaml:

  * `ep2-guard1-canon-founder-0822` — that frame IS guard 1. A generation of
    ours that HE SELECTED, which is the goblin's provenance pattern exactly
    (`ep2-goblin-design-adult`: "i didnt draw the goblin.. i just used an old
    generation") and carries the same authority. It is committed at
    taste/refs/guard1-canon-founder-0822.png.
  * `ep2-human-style-cinematic-anime` — humans are DETAILED CINEMATIC ANIME,
    which is the July ruling re-applied. The round-1 sheet was drawn on the flat
    goblin-era tag stack and that is what he was looking at when he said the
    style was wrong.

So round 2 is not round 1 with better words. It is a DIFFERENT STACK, and the
stack is not a guess: it is the one that drew the frame he just called canon.

THE TRACE, END TO END, BECAUSE THE WHOLE POINT IS THAT THIS RECIPE IS NOT NEW.

    taste/refs/guard1-canon-founder-0822.png      sha 420fc2c0...
      = farm-out/ep2-b09-platecrop-0820/09-the-pause-platecrop-r2s2.png
      <- farm-out/ep2-b09-cast-0817/09-the-pause-ipa-r2-w015-s2.png
      <- pipeline/jobs/ep2-b09-cast-0817.yaml       <- THE RECIPE

and that spec runs `goblin_ipa_beat.py --character guard --arm window4` over
animagine-xl-3.1 with a PROSE prompt out of wave-drafts.yaml closing on the
14-token style tail `cinematic lighting, masterpiece, best quality, very
aesthetic`. Everything structural below is carried from it unchanged.

WHAT `window4` ACTUALLY IS, spelled out because the filename misleads and it
misled this lane for an hour today. `w015` in `09-the-pause-ipa-r2-w015-s2.png`
is NOT an adapter weight of 0.15. goblin_ipa_sample.CELLS_WINDOW4 is
`[(r, WINDOW_SCALE, 0.15) for r in 0..3]` with `WINDOW_SCALE = 0.6`: the
IP-Adapter runs at SCALE 0.6 and is switched off by `callback_on_step_end`
after the first 15% of the denoise — 6 steps of 40. A strong EARLY-STRUCTURE
hold, then the text prompt owns everything after step 6. That is why it can
carry a style and a costume family off one reference without cloning the face
in it, and it is the property this sheet depends on.

THE FOUR THINGS THIS SHEET CHANGES FROM ep2-b09-cast-0817, each with its reason:

  1. THE REFERENCE. b09 conditioned on `refs-guards-twoinfield-nos2-0815`, three
     distinct images of the OLD cast — the same references the founder called
     "not the best... some have girls, and theyre just improper". This sheet
     conditions on guard 1 as he ruled him, and on nothing else.
  2. THE REFERENCE IS PRE-SQUARED. The sampler centre-crops its reference to
     square, and a centre crop of the 832x1216 canon frame starts at y=192 and
     CUTS THE CROWN OFF HIS HEAD — the hair would never reach the adapter. So a
     TOP-ANCHORED 832x832 crop is authored into the repo as
     `taste/refs/guard1-canon-founder-0822-sq.png` and the sampler's own crop
     becomes a no-op on it. Looked at at 1:1 against the centre crop before it
     was chosen; $0, pure geometry, no model.
  3. FOUR SLOTS, ONE IMAGE. `window4` reads `<prefix>-s0..s3.png` and there is
     one reference, so the stage step writes four byte-identical copies and
     `dedup_cells` collapses them to ONE cell — the same mechanism that made
     b09's true frame count 12 and not 16. Reported here in advance rather than
     discovered in the artifact check, which is what retired a b09 job rc 92.
  4. THE BEAT IS 06, `the-clipboard`. Guard 2's beat: `1boy`, `kind: guard`, and
     the bark board is his prop. Beat 09 is guard 1's face and is not re-asked.

WHAT VARIES ACROSS THE TEN CELLS AND WHAT DOES NOT. Held: the opening clause
(which is also what derives the `1boy` count tag), head-and-shoulders framing,
the costume family, the background, the style tail, the negative, and the
reference. Varied: HAIR and FACE/BUILD. Two axes at once, deliberately — this
is a casting sheet whose job is to hand him ten different men, not a
measurement rung that isolates one variable. Round 1's own honest miss was that
its build axis barely moved because a single openpose skeleton fixed every
silhouette; there is no skeleton here, so build is carried by face words that
actually reach CLIP.

ONE SAMPLE BEFORE THE BATCH, AND IT IS NOT NEGOTIABLE HERE OF ALL PLACES.
CLAUDE.md: one sample per RECIPE CHANGE. This is a new reference, a new prompt
family and a new beat, and the named risk is specific — the reference has WIRE
RIMS and A HAND ON THE CHEEK, and a 6-step structure hold is exactly when a
composition gets set. `no glasses` and `no hands` are in the negative for that
reason and the sample is what says whether they hold. Cell A fires alone, gets
looked at at 1:1, and the other nine fire only after. Round 1's spec said "THE
BATCH IS THE SAMPLE" and round 1 was rejected whole.

$0 — local card, no provider, no spend. Nothing here casts anybody: the pick is
R4 and it is the founder's.
"""
from __future__ import annotations

import hashlib
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                                  # noqa: E402

BEAT = 6
SLUG = "the-clipboard"
NODE = "002b-first-citizen"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "taste/refs/guard1-canon-founder-0822-sq.png")
REF_REPO_PATH = "taste/refs/guard1-canon-founder-0822-sq.png"
REF_PREFIX = "guard1sq"
# The seed a cell draws is the sampler's own arithmetic, not ours:
#   wg.SEED (20260719) + BEAT (6) + seed_start * 1000
# so cell i is `--seeds 1 --seed-start i` and its seed is pinned by construction.
SEED_BASE = 20260719 + BEAT

# (letter, the one clause that differs)
CELLS = [
    ("a", "thick dark brown hair, heavy square jaw, thick neck, slack open mouth"),
    ("b", "light sandy hair, long thin face, drooping eyelids, blank stare"),
    ("c", "cropped ginger hair, round heavy face, full cheeks, small eyes"),
    ("d", "shaved head, dark stubble, broad flat face, wide-set eyes, slack mouth"),
    ("e", "shaggy black hair, gaunt narrow face, big ears, eyebrows raised"),
    ("f", "grey-streaked brown hair, thick moustache, jowly face, half-closed eyes"),
    ("g", "receding sandy hair, high forehead, narrow face, puzzled frown"),
    ("h", "curly black hair, wide square face, thick neck, gormless grin"),
    ("i", "straight light brown hair, big nose, doughy face, mouth slightly open"),
    ("j", "short red hair, freckles, heavy brow, blunt chin, blank stare"),
]

BAR = (
    "ONE 832x1216 png, scored AT 1:1 and by eye, never by a metric. A pass is a "
    "CANDIDATE on the picker page and nothing more -- the cast is R4 and this job "
    "does not make it. THE BAR, PRE-REGISTERED BEFORE THE PIXELS EXIST: (1) ONE "
    "GROWN MAN, alone in frame -- a read of child, teenager or female is a DROP, "
    "not a note, and the round-1 sheet cut two cells on exactly this; (2) the face "
    "reads DUMB and readable at a glance -- slack, blank or gormless, which is the "
    "founder's own brief (\"they should look like grown men. yes. dumb grown men\"); "
    "(3) DETAILED CINEMATIC ANIME, the style of taste/refs/guard1-canon-founder-0822.png "
    "and the whole reason this round exists -- a flat, muted or tag-sheet look is a "
    "fail however good the face is; (4) NO GLASSES and NO HAND in frame, both being "
    "attributes of the REFERENCE that must not travel; (5) the costume family reads: "
    "cream shirt collar and white shoulder sash; (6) head and shoulders, face toward "
    "the lens, a real grass-and-hedgerow background rather than a plain ground; (7) "
    "he is NOT guard 1 -- if the adapter has cloned the reference's face this cell is "
    "a duplicate, not a candidate, and the sheet says so. PRE-REGISTERED FAIL MODES, "
    "recorded by name whether or not they fire: wire rims arriving off the reference "
    "despite the negative; the hand-on-cheek composition arriving with them; the "
    "6-step structure hold being too short to carry the style at all, which would "
    "show as a cell that is on-brief and off-look."
)


def spec_id(letter):
    return "ep2-guardcast2-%s-0822" % letter


def draft_key(letter):
    return "authored_b06_guard2cast_%s_0822" % letter


def out_dir(letter):
    return r"C:\banyan-farm\guardcast2-0822\out-%s" % letter


def refs_dir():
    return r"C:\banyan-farm\guardcast2-0822\refs"


def drafts_sha():
    with open(os.path.join(REPO, "pipeline", "wave-drafts.yaml"), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def ref_sha():
    with open(os.path.join(REPO, REF_REPO_PATH), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _stage_step():
    """Fetch the ONE reference, sha-check it, write it into four slots.

    THE SHA CHECK IS THE POINT. Every input this sheet is conditioned on is
    verified before a GPU second is spent, because a reference that silently
    changed is a sheet that answers a question nobody asked. Four slots because
    window4 enumerates s0..s3; dedup_cells collapses them back to one cell and
    SAYS SO in its own report.
    """
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
    ) % {"refs": refs_dir(), "sha": ref_sha(), "url": RAW, "pfx": REF_PREFIX}
    return {"name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def _sample_argv(letter, index):
    return [
        r"C:\banyan-farm\venv\Scripts\python.exe",
        r"C:\banyan-farm\wave-goblin-prep\goblin_ipa_beat.py",
        "--beat", str(BEAT),
        "--character", "guard",
        "--harness", r"C:\banyan-farm\wave-goblin-prep",
        "--root", r"C:\banyan-farm\wave-goblin-prep\repo",
        "--refs", refs_dir(),
        "--ref-prefix", REF_PREFIX,
        "--out", out_dir(letter),
        "--draft-key", draft_key(letter),
        "--arm", "window4",
        "--seeds", "1",
        "--seed-start", str(index),
        "--expect-drafts-sha256", drafts_sha(),
        "--task", spec_id(letter),
    ]


def frame_name(index):
    """The exact file the sampler writes for this cell.

    NOT A GUESS. goblin_ipa_sample writes `f"{BEAT:02d}-{slug}-ipa-{tag}-s{i}"`
    with `tag = f"r{ref_i}-w{end_frac*100:03d}"` for the window arms, and this
    sheet's four reference slots are byte-identical so dedup_cells leaves only
    ref slot 0 -- hence `r0-w015` on every cell. `i` is the SEED INDEX, which is
    `--seed-start`, which is the cell's position. Naming it literally (rather
    than globbing for it) is what makes the runner's missing-artifact check mean
    something: a glob that matches nothing publishes nothing and still returns a
    code that reads like a render failure, which is what made six rendered
    plates read as six failures on 2026-08-14.
    """
    return "%02d-%s-ipa-r0-w015-s%d.png" % (BEAT, SLUG, index)


def _publish_step(letter, index):
    """Copy the ONE named frame and its sidecar into farm-out with a manifest."""
    jid = spec_id(letter)
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
    ) % {"out": out_dir(letter), "jid": jid, "frame": frame_name(index)}
    return {"name": "publish",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def build_root():
    """Cell A, authored in full. The other nine are derived from this file."""
    letter, body = CELLS[0]
    return {
        "id": spec_id(letter),
        "task": spec_id(letter),
        "node": NODE,
        "beat": BEAT,
        "runner": "box",
        "priority": 6,
        "needs_gpu": True,
        "max_attempts": 1,
        "sample": True,
        "est_minutes": 3,
        "needs": ["cuda", "vram20", "farm-venv"],
        "owner": ("guard lane, 2026-08-22 -- the round-2 casting sheet, filed the "
                  "night the founder rejected round 1 on style"),
        "consumer": (
            "THE FOUNDER, on /review/ep2-guardcast2-0822. Cell A is THE SAMPLE and "
            "its consumer is the decision to fire the other nine at all: it is one "
            "cell of a ten-cell sheet and it exists so the recipe is looked at "
            "before it is scaled. Guard 1 is NOT re-asked -- he is cast, and "
            "taste/refs/guard1-canon-founder-0822.png is him. Nothing downstream "
            "consumes any of these frames until he picks: no beat plate, no motion "
            "spec, and review/ep2-ship-0821 is not touched."),
        "success": BAR,
        "why": (
            "GUARD 2, CELL A OF TEN: %s. Round 1's twelve cells were drawn on the "
            "flat goblin-era tag stack and the founder rejected all of them in one "
            "sentence -- \"none of them are right, the style is wrong\" -- posting "
            "the beat-09 guard close-up as the contrast. This is the same casting "
            "question re-asked through the recipe THAT frame was drawn with: "
            "goblin_ipa_beat.py --character guard --arm window4 (IP-Adapter at "
            "scale 0.6, off after the first 15%% of the denoise) over the new "
            "guard-1 reference, with a prose prompt out of wave-drafts.yaml closing "
            "on the ratified 14-token style tail. Minutes of local GPU, $0, no "
            "provider. See pipeline/derive_guardcast2_0822.py for the full trace." % body),
        "script_authority": (
            "Node 002b-first-citizen, live script `002b-t0-c`, `approved_by: founder`, "
            "`approved_on: 2026-08-03`. A STILL CASTING PLATE on an approved node: no "
            "voice, no motion, no episode assembly, no publication. It draws nobody "
            "who is cast -- guard 2 is the open question and this sheet is how it is "
            "put to the founder."),
        "script_line": ("Beat 06 THE CLIPBOARD: guard 2, the one with the bark board. "
                        "Drawn here head-and-shoulders, without the prop, because the "
                        "question is his FACE."),
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
            {"name": "dry", "argv": _sample_argv(letter, 0) + ["--dry"]},
            {"name": "sample", "argv": _sample_argv(letter, 0)},
            _publish_step(letter, 0),
        ],
        "recipe_trace": (
            "parent recipe pipeline/jobs/ep2-b09-cast-0817.yaml; reference "
            "%s sha %s, a top-anchored 832x832 crop of "
            "taste/refs/guard1-canon-founder-0822.png (sha 420fc2c0...); prompt "
            "pipeline/wave-drafts.yaml beats.6.%s, file sha %s, enforced at RUN "
            "time by --expect-drafts-sha256 so a hand-sync between filing and "
            "firing cannot swap the wording underneath it."
            % (REF_REPO_PATH, ref_sha()[:16], draft_key(letter), drafts_sha()[:16])),
        "one_sample_rule": (
            "CELL A IS THE SAMPLE AND THE OTHER NINE ARE HELD. CLAUDE.md requires one "
            "sample per RECIPE CHANGE, and this is three at once: a new reference, a "
            "new prompt family and a new beat. The specific risk the sample answers: "
            "the reference wears WIRE RIMS and has A HAND ON THE CHEEK, and a 6-step "
            "structure hold is precisely when a composition is set, so `no glasses` "
            "and `no hands` are load-bearing negatives that have never been tested "
            "against THIS reference. Round 1's spec argued \"THE BATCH IS THE SAMPLE\" "
            "and round 1 was rejected entire."),
        "seed_note": (
            "Seeds are the sampler's own arithmetic and are pinned by construction: "
            "wg.SEED (20260719) + beat (6) + seed_start * 1000. Cell A is "
            "--seed-start 0 -> %d; cells B..J take seed_start 1..9 -> %d..%d. No two "
            "cells can collide and every cell's seed is derivable from its letter "
            "without opening the artifact."
            % (SEED_BASE, SEED_BASE + 1000, SEED_BASE + 9000)),
        "frame_count": (
            "ONE png per cell. window4 enumerates four reference slots and the stage "
            "step writes four byte-identical copies of the single guard-1 reference, "
            "so dedup_cells drops three and one cell is drawn, at one seed. Stated "
            "here rather than discovered by the artifact check -- an artifact list "
            "naming frames the run never writes is what retired a b09 job at rc 92."),
        "artifacts": [out_dir(letter) + "\\" + frame_name(0)],
    }


def sibling(letter, body, index):
    """One of B..J: cell A with the draft key, the seed index and the paths moved."""
    jid = spec_id(letter)
    child = derive_spec.derive(
        src="pipeline/jobs/%s.yaml" % spec_id("a"),
        new_id=jid,
        fresh={
            "owner": ("guard lane, 2026-08-22 -- cell %s of the round-2 casting "
                      "sheet, filed with the batch that followed the cell-A sample"
                      % letter.upper()),
            "consumer": (
                "THE FOUNDER, on /review/ep2-guardcast2-0822, as candidate %s of ten. "
                "This cell is NOT a sample and does not carry the sample's job: cell A "
                "answered whether the recipe holds and this one only adds a face to "
                "choose between. Nothing downstream consumes it until he picks."
                % letter.upper()),
            "success": (
                "ONE 832x1216 png at seed %d, scored at 1:1 on the bar cell A "
                "pre-registered, which is unchanged and applies to this cell term for "
                "term. The only thing this spec moves is the hair-and-face clause: %s."
                % (SEED_BASE + index * 1000, body)),
            "why": (
                "GUARD 2, CELL %s OF TEN: %s. One variable against cell A -- the "
                "hair-and-face clause and the seed index that follows from the cell's "
                "position. Driver, checkpoint, reference, adapter arm, framing, "
                "costume, background, style tail and negative are all held. $0."
                % (letter.upper(), body)),
        },
        overrides={
            "argv:--draft-key": draft_key(letter),
            "argv:--seed-start": str(index),
            "argv:--out": out_dir(letter),
        },
        retoken=[("out-%s" % CELLS[0][0], "out-%s" % letter),
                 (frame_name(0), frame_name(index))],
        extra={
            "cell": ("cell %s of ten. Sheet: /review/ep2-guardcast2-0822. "
                     "Recipe and full trace: pipeline/derive_guardcast2_0822.py."
                     % letter.upper()),
        },
        by="pipeline/derive_guardcast2_0822.py",
    )
    return child


# --------------------------------------------------------------------------
def _tokens(text):
    """Real CLIP BPE count against animagine's own vocab, or None if absent."""
    try:
        sys.path.insert(0, os.path.join(REPO, "pipeline"))
        import clip_token_count as ctc
        return ctc.count(text) if hasattr(ctc, "count") else None
    except SystemExit:
        return None
    except Exception:
        return None


def _selftest():
    """Asserts, not prints. A selftest that only prints is a demo."""
    print("derive_guardcast2_0822 selftest")
    ok = True

    # 1. Ten cells, ten distinct letters, ten distinct seeds.
    letters = [c[0] for c in CELLS]
    assert len(letters) == 10, letters
    assert len(set(letters)) == 10, letters
    seeds = [SEED_BASE + i * 1000 for i in range(10)]
    assert len(set(seeds)) == 10, seeds
    print("  ok  10 cells, 10 distinct seeds %d..%d" % (seeds[0], seeds[-1]))

    # 2. The reference exists, is square, and is the top of the canon frame.
    ref = os.path.join(REPO, REF_REPO_PATH)
    assert os.path.isfile(ref), ref
    try:
        from PIL import Image
        w, h = Image.open(ref).size
        assert w == h == 832, (w, h)
        canon = os.path.join(REPO, "taste/refs/guard1-canon-founder-0822.png")
        assert Image.open(canon).crop((0, 0, 832, 832)).tobytes() == \
            Image.open(ref).tobytes(), "square ref is not the TOP crop of the canon frame"
        print("  ok  reference 832x832, top-anchored crop of the canon frame")
    except ImportError:
        print("  --  PIL absent, geometry unchecked")

    # 3. Every draft key exists, derives 1boy, and fits CLIP's 77.
    try:
        sys.path.insert(0, os.path.join(REPO, "pipeline"))
        from pathlib import Path
        import render_wave_goblin as wg
        import sd_prompt as sd
        blk = wg.load_drafts(Path(REPO) / "pipeline" / "wave-drafts.yaml")[BEAT]
        worst_pos = worst_neg = 0
        for letter, body in CELLS:
            key = draft_key(letter)
            assert key in blk, "draft key %r missing from beat %d" % (key, BEAT)
            row = wg.check(BEAT, blk, blk[key], sd, verbose=False)
            assert not row["faults"], (key, row["faults"])
            assert body in blk[key], "cell %s body not in its own draft" % letter
            assert "very aesthetic" in row["pos"], key
            for term in ("glasses", "hands", "teenager"):
                assert term in row["neg"], (key, term)
            worst_pos = max(worst_pos, row["pos_tok"])
            worst_neg = max(worst_neg, row["neg_tok"])
        assert worst_pos <= 77, worst_pos
        assert worst_neg <= 77, worst_neg
        print("  ok  10 drafts, 0 faults, longest positive %d/77, negative %d/77"
              % (worst_pos, worst_neg))
    except ImportError as exc:
        ok = False
        print("  !!  could not check the drafts: %s" % exc)

    # 4. The emitted specs, if written, still match what this file would emit.
    root = build_root()
    assert root["id"] == "ep2-guardcast2-a-0822", root["id"]
    argv = [s for s in root["steps"] if s["name"] == "sample"][0]["argv"]
    assert "--arm" in argv and argv[argv.index("--arm") + 1] == "window4"
    assert argv[argv.index("--character") + 1] == "guard"
    assert argv[argv.index("--beat") + 1] == str(BEAT)
    assert argv[argv.index("--expect-drafts-sha256") + 1] == drafts_sha()
    assert "--ref-prefix" in argv
    print("  ok  cell A argv: window4, --character guard, beat %d, drafts pinned"
          % BEAT)

    for letter, _ in CELLS:
        p = os.path.join(REPO, "pipeline", "jobs", "%s.yaml" % spec_id(letter))
        if os.path.isfile(p):
            got = derive_spec.load(p)
            assert got["id"] == spec_id(letter), p
            sargv = [s for s in got["steps"] if s["name"] == "sample"][0]["argv"]
            assert sargv[sargv.index("--draft-key") + 1] == draft_key(letter), p
            assert sargv[sargv.index("--expect-drafts-sha256") + 1] == drafts_sha(), (
                "%s pins a STALE wave-drafts.yaml -- re-run --write" % p)
    print("  ok  emitted specs (those on disk) agree with this file")

    print("SELFTEST: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def write_all(force=False):
    paths = [derive_spec.write(build_root(),
                               "pipeline/jobs/%s.yaml" % spec_id("a"), force=force)]
    for index, (letter, body) in enumerate(CELLS):
        if index == 0:
            continue
        paths.append(derive_spec.write(sibling(letter, body, index),
                                       "pipeline/jobs/%s.yaml" % spec_id(letter),
                                       force=force))
    for p in paths:
        print("wrote", os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    if "--write" in sys.argv:
        sys.exit(write_all(force="--force" in sys.argv))
    sys.exit(_selftest())
