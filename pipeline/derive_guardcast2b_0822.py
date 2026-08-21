#!/usr/bin/env python3
r"""GUARD-2 CASTING, ROUND 2B — the same ten men with the IP-Adapter taken OUT.

    python3 pipeline/derive_guardcast2b_0822.py --selftest   # assert, write nothing
    python3 pipeline/derive_guardcast2b_0822.py --write      # emit the ten specs

THIS FILE EXISTS BECAUSE THE ROUND-2 SAMPLE FAILED, AND IT FAILED ON THE FAULT
ITS OWN SPEC PRE-REGISTERED. Cell A of `ep2-guardcast2-*-0822` rendered in 11
seconds at seed 20260725 and came back as GUARD 1: the same three-quarter head
angle, the same crop, and — despite `no hands` in the negative — the same HAND
PRESSED AGAINST THE CHEEK that guard 1 makes in the reference. The prompt asked
for a heavy square jaw, a thick neck and a slack open mouth; the frame has a
young face, no visible jaw or neck, and a grin. Two of the three fail modes
`one_sample_rule` named by name fired together.

WHAT THE SAMPLE ACTUALLY PROVED, WHICH IS MORE USEFUL THAN THE FRAME IT DREW.

  * THE STYLE HALF IS SOLVED AND IT IS NOT THE ADAPTER'S DOING. Cell A is
    unmistakable detailed cinematic anime — the thing the founder rejected round
    1 for lacking. Round 1 ran the SAME checkpoint (animagine-xl-3.1) with the
    same absence of any reference and looked flat, so what changed between them
    is the PROMPT: prose, and the 14-token tail `cinematic lighting, masterpiece,
    best quality, very aesthetic`. The style comes from the words.
  * THE ADAPTER IS THE WRONG INSTRUMENT FOR A CASTING SHEET, and in hindsight it
    is wrong by definition. In `ep2-b09-cast-0817` the reference was brought in
    for ONE named job: "the hair came back mid-to-dark BROWN AND SHAGGY where
    guard A's is near-black and CROPPED... Hair colour and texture are what a
    reference is for." A casting sheet's entire purpose is to VARY hair and
    face. Conditioning one on a portrait of a specific man asks the adapter to
    pin the very axis the sheet exists to move — so it either loses or it wins,
    and when it wins you get ten pictures of guard 1.
  * WHY IT LOCKED THE POSE HERE AND NOT ON BEAT 09. Same arm, same 0.6 scale,
    same 6-of-40-step window. The difference is the REFERENCE'S COMPOSITION. On
    b09 the references were two-in-field FULL BODY and the prompt asked for a
    face close-up: the adapter had no matching structure to impose, so it gave
    up its colour and kept quiet about layout. Here the reference IS a face
    close-up and the prompt asks for a face close-up, so at the exact steps
    where a sampler fixes coarse structure the adapter had a composition to
    hand and handed it over. The window's strength was never the variable —
    the geometric agreement between reference and request was.

SO ROUND 2B IS ROUND 2 MINUS ONE THING. Not a new brief, not new wording, not a
different checkpoint, not a new seed scheme:

    checkpoint     cagliostrolab/animagine-xl-3.1   unchanged
    prompt         the ten compiled positives        BYTE-IDENTICAL
    negative       the ten compiled negatives        BYTE-IDENTICAL
    steps / cfg    40 / 7.5                          unchanged (wave constants)
    size           832x1216                          unchanged
    seeds          20260725..20269725                unchanged, cell for cell
    IP-Adapter     scale 0.6, 6-of-40-step window -> GONE
    ControlNet     none in either round              unchanged

`pipeline/controlnet_plate.py` is the driver only because it is the repo's plain
SDXL path that takes a prompt file and a seed; `--control` defaults to None so
no ControlNet is loaded, and no `--ip-ref` is passed so no adapter is loaded
either. THIS IS NOT A RETURN TO THE ROUND-1 STACK. Round 1's defect was its
PROMPT — a booru tag list ending `muted color`, no style tail — and round 1's
openpose skeleton is absent here too. Same driver, opposite prompt.

THE PROMPTS ARE BAKED, NOT LOOKED UP, and that is a deliberate change from round
2. Round 2 read `pipeline/wave-drafts.yaml` on the box and had to pin the file's
sha at run time so a peer's hand-sync could not swap the wording underneath it.
Here the exact compiled strings — count tag, compressed positive, assembled
negative, all of it — travel in the spec's own `payload:` and are sha-visible in
the job record. Nothing about the wording can drift between filing and firing,
and the drafts stay where they are as the authoring source of record.

WHAT IS STILL UNPROVEN AND IS WHAT THE 2B SAMPLE ASKS. Without the adapter,
nothing carries guard 1's PALETTE or his costume rendering except the words
`cream shirt collar, white shoulder sash`. The sheet may come back on-brief and
in a slightly different key from guard 1's frame. That is a MUCH smaller problem
than ten copies of guard 1 — a costume family is a wording fix, an identity
collapse is not — and it is named here so that if it happens it is the round's
answer rather than a surprise.

Cell A fires alone again. Same rule, same reason, one instrument removed.

$0 — local card, no provider, no spend. The pick is R4 and it is the founder's.
"""
from __future__ import annotations

import hashlib
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                                  # noqa: E402
import derive_guardcast2_0822 as r2                                 # noqa: E402

# THE ARM STRING IS NOT COSMETIC AND IT COST A RENDER TO LEARN IT. In
# controlnet_plate.py the whole ControlNet branch is gated on
# `use_cn = a.arm != "nocontrol"` -- the LITERAL string, nothing else. Filed
# first as `noipa`, which reads like exactly what this round does and is not
# the magic word, so the driver kept the control branch on, found no
# --control and exited rc 6 in one second without loading a model. Asserted
# in --selftest so the next lane cannot rename it into the same failure.
ARM = "nocontrol"
NODE = r2.NODE
BEAT = r2.BEAT
CELLS = r2.CELLS
SEED_BASE = r2.SEED_BASE
DRIVER_REPO_PATH = "pipeline/controlnet_plate.py"
RAW_BASE = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"


def spec_id(letter):
    return "ep2-guardcast2b-%s-0822" % letter


def work_dir(letter):
    return r"C:\banyan-farm\%s" % spec_id(letter)


def driver_sha():
    with open(os.path.join(REPO, DRIVER_REPO_PATH), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def compiled(letter):
    """(positive, negative) exactly as the box will be handed them.

    Compiled HERE, from the same wave-drafts entry round 2 rendered, through the
    same render_wave_goblin.check() that built round 2's prompt -- so the two
    rounds differ by the adapter and by nothing that reaches CLIP.
    """
    from pathlib import Path
    sys.path.insert(0, os.path.join(REPO, "pipeline"))
    import render_wave_goblin as wg
    import sd_prompt as sd
    blk = wg.load_drafts(Path(REPO) / "pipeline" / "wave-drafts.yaml")[BEAT]
    row = wg.check(BEAT, blk, blk[r2.draft_key(letter)], sd, verbose=False)
    if row["faults"]:
        raise SystemExit("!! cell %s has faults: %s" % (letter, row["faults"]))
    return row["pos"], row["neg"]


def _stage_step(letter):
    """Fetch the driver, sha-check it, and refuse on a mismatch.

    One input, not three: no skeleton (round 1's was the wrong instrument and is
    not here), and no reference image (round 2's was the wrong instrument and is
    the whole point of this round).
    """
    root = work_dir(letter) + r"\src"
    body = (
        "import hashlib, os, urllib.request\n"
        "base = \"%(base)s\"\n"
        "root = r\"%(root)s\"\n"
        "want = [(\"controlnet_plate.py\", os.path.join(root, \"pipeline\"),\n"
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
    ) % {"base": RAW_BASE, "root": root, "sha": driver_sha()}
    return {"name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def _cast_argv(letter, index):
    w = work_dir(letter)
    return [
        r"C:\banyan-farm\venv\Scripts\python.exe",
        w + r"\src\pipeline\controlnet_plate.py",
        "--root", w + r"\src",
        "--task", spec_id(letter),
        "--arm", ARM,
        "--seed", str(SEED_BASE + index * 1000),
        "--steps", "40",
        "--cfg", "7.5",
        "--width", "832",
        "--height", "1216",
        "--prompt-file", w + r"\prompt.txt",
        "--negative-file", w + r"\negative.txt",
        "--out", w + r"\out",
    ]


def _publish_step(letter):
    jid = spec_id(letter)
    w = work_dir(letter).replace("\\", "/")
    body = (
        "# The courier pushes from farm-out and from nowhere else.\n"
        "# The CONDITIONS travel with the frame: prompt and negative go too, so\n"
        "# the sheet can be re-read months from now without this spec in hand.\n"
        "import glob, hashlib, os, shutil\n"
        "dst = \"C:/banyan-farm/courier-box/farm-out/%(jid)s\"\n"
        "os.makedirs(dst, exist_ok=True)\n"
        "files = sorted(glob.glob(\"%(w)s/out/%(jid)s-%(arm)s.png*\")\n"
        "               + glob.glob(\"%(w)s/prompt.txt\")\n"
        "               + glob.glob(\"%(w)s/negative.txt\"))\n"
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
    ) % {"jid": jid, "w": w, "arm": ARM}
    return {"name": "publish",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


BAR = (
    "ONE 832x1216 png, scored AT 1:1 and by eye, never by a metric. A pass is a "
    "CANDIDATE on the picker page and nothing more -- the cast is R4 and this job "
    "does not make it. THE BAR IS ROUND 2'S, TERM FOR TERM, and it is repeated "
    "rather than referenced because a bar that lives in another spec is a bar "
    "nobody reads: (1) ONE GROWN MAN alone in frame -- child, teenager or female "
    "is a DROP, not a note; (2) the face reads DUMB at a glance -- slack, blank or "
    "gormless (\"they should look like grown men. yes. dumb grown men\"); (3) "
    "DETAILED CINEMATIC ANIME, the look of taste/refs/guard1-canon-founder-0822.png, "
    "a flat or muted tag-sheet look being a fail however good the face is; (4) NO "
    "GLASSES and NO HAND in frame; (5) cream shirt collar and white shoulder sash "
    "read as the costume family; (6) head and shoulders, face toward the lens, a "
    "real grass-and-hedgerow background; (7) HE IS NOT GUARD 1. THE ONE CLAUSE "
    "ROUND 2B ADDS, because removing the adapter is what it tests: (8) the frame "
    "must still be in the SHOW'S KEY -- if the palette or the line quality has "
    "drifted away from guard 1's frame now that nothing conditions on him, that is "
    "this round's finding and it goes on the sheet in words rather than being "
    "quietly accepted. PRE-REGISTERED FAIL MODES: the costume reading as a generic "
    "white shirt because only words carry it now; the face reading young, which the "
    "round-2 cell also did and which no adapter was ever going to fix."
)


def build_root():
    letter, body = CELLS[0]
    pos, neg = compiled(letter)
    w = work_dir(letter)
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
        "est_minutes": 2,
        "needs": ["cuda", "vram12", "sdxl-venv"],
        "owner": ("guard lane, 2026-08-22 -- round 2B, filed within the hour of "
                  "the round-2 sample failing on the fault its own spec named"),
        "consumer": (
            "THE FOUNDER, on /review/ep2-guardcast2-0822. Cell A is THE SAMPLE and "
            "its consumer is the decision to fire the other nine: round 2's cell A "
            "came back as guard 1 with his own hand on his cheek, so the recipe gets "
            "looked at again before it is scaled again. Guard 1 is not re-asked. "
            "Nothing downstream consumes these frames until he picks, and "
            "review/ep2-ship-0821 is untouched."),
        "success": BAR,
        "why": (
            "GUARD 2, CELL A OF TEN, ADAPTER REMOVED: %s. Round 2 conditioned this "
            "same prompt on guard 1's close-up through the window4 arm and got guard "
            "1 back, pose and all -- because the reference's composition and the "
            "prompt's request were the same shape, which is exactly when a "
            "6-of-40-step structure hold has something to impose. The style was never "
            "the adapter's doing: round 1 ran this checkpoint with no reference at all "
            "and looked flat because its PROMPT was a booru tag list, and this prompt "
            "is prose closing on the ratified style tail. So the adapter comes out and "
            "nothing else moves -- same prompt bytes, same negative bytes, same seed "
            "20260725, same 40 steps at cfg 7.5, same 832x1216. $0, local card. Full "
            "reasoning in pipeline/derive_guardcast2b_0822.py." % body),
        "script_authority": (
            "Node 002b-first-citizen, live script `002b-t0-c`, `approved_by: founder`, "
            "`approved_on: 2026-08-03`. A STILL CASTING PLATE on an approved node: no "
            "voice, no motion, no episode assembly, no publication."),
        "script_line": ("Beat 06 THE CLIPBOARD: guard 2, the one with the bark board. "
                        "Head and shoulders, no prop -- the question is his FACE."),
        "env": {
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_OFFLINE": "1",
            "HF_HUB_DISABLE_XET": "1",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "payload": {
            w + r"\prompt.txt": pos,
            w + r"\negative.txt": neg,
        },
        "steps": [
            _stage_step(letter),
            {"name": "cast", "argv": _cast_argv(letter, 0)},
            _publish_step(letter),
        ],
        "recipe_trace": (
            "Round 2 (pipeline/jobs/ep2-guardcast2-a-0822.yaml) minus the IP-Adapter. "
            "Prompt and negative are the COMPILED output of "
            "render_wave_goblin.check() over pipeline/wave-drafts.yaml "
            "beats.6.%s -- the same function and the same entry round 2 rendered -- "
            "baked into payload rather than read on the box, so no hand-sync between "
            "filing and firing can alter a byte. Driver "
            "pipeline/controlnet_plate.py sha %s, fetched and sha-checked before a "
            "GPU second is spent; --control is unset so no ControlNet loads and no "
            "--ip-ref is passed so no adapter loads."
            % (r2.draft_key(letter), driver_sha()[:16])),
        "one_sample_rule": (
            "CELL A IS THE SAMPLE AND THE OTHER NINE ARE HELD, for the second time "
            "tonight and for a better reason than the first: the first sample already "
            "proved this brief can fail in a way no metric would have caught. What "
            "this one asks is narrow -- with nothing conditioning on guard 1, does the "
            "frame stay in the show's key, and does the costume still read? Twenty "
            "seconds of card time to find out before nine more fire."),
        "seed_note": (
            "Seeds are carried from round 2 unchanged so the two rounds are "
            "comparable cell for cell: 20260719 + 6 + index*1000, i.e. %d for cell A "
            "and %d..%d for B..J. Round 2's cell A and this one differ by the adapter "
            "and by nothing else, seed included, which is what makes the pair an A/B "
            "rather than two unrelated pictures."
            % (SEED_BASE, SEED_BASE + 1000, SEED_BASE + 9000)),
        "artifacts": [w + r"\out\%s-%s.png" % (spec_id(letter), ARM)],
    }


def sibling(letter, body, index):
    pos, neg = compiled(letter)
    w = work_dir(letter)
    return derive_spec.derive(
        src="pipeline/jobs/%s.yaml" % spec_id("a"),
        new_id=spec_id(letter),
        fresh={
            "owner": ("guard lane, 2026-08-22 -- cell %s of round 2B, filed with the "
                      "batch that followed the cell-A sample" % letter.upper()),
            "consumer": (
                "THE FOUNDER, on /review/ep2-guardcast2-0822, as candidate %s of ten. "
                "Not a sample: cell A answered whether the adapter's removal holds the "
                "look, and this cell only adds a face to choose between."
                % letter.upper()),
            "success": (
                "ONE 832x1216 png at seed %d, scored at 1:1 on the bar cell A "
                "pre-registered, unchanged and applying term for term. The only thing "
                "this spec moves is the hair-and-face clause: %s."
                % (SEED_BASE + index * 1000, body)),
            "why": (
                "GUARD 2, CELL %s OF TEN, ADAPTER REMOVED: %s. One variable against "
                "cell A -- the hair-and-face clause and the seed that follows from the "
                "cell's position. Driver, checkpoint, steps, cfg, size, framing, "
                "costume, background, style tail and negative all held. $0."
                % (letter.upper(), body)),
        },
        # NO `payload:negative.txt` OVERRIDE, and its absence is correct: the
        # negative is IDENTICAL in all ten cells by design -- it is the sheet's
        # constant, not a per-cell variable -- and derive_spec refuses an
        # override that changes nothing, which is the guard doing its job. It is
        # inherited from cell A and its dict KEY is retokened to this cell's own
        # working directory along with everything else.
        overrides={
            "seed": SEED_BASE + index * 1000,
            "payload:prompt.txt": pos,
        },
        retoken=[(work_dir(CELLS[0][0]), w)],
        extra={"cell": ("cell %s of ten. Sheet: /review/ep2-guardcast2-0822. "
                        "Reasoning: pipeline/derive_guardcast2b_0822.py."
                        % letter.upper())},
        by="pipeline/derive_guardcast2b_0822.py",
    )


# --------------------------------------------------------------------------
def _selftest():
    print("derive_guardcast2b_0822 selftest")
    import clip_token_count as ctc

    worst_pos = worst_neg = 0
    seen = set()
    for index, (letter, body) in enumerate(CELLS):
        pos, neg = compiled(letter)
        assert "very aesthetic" in pos, letter
        assert pos.startswith("1boy,"), (letter, pos[:20])
        assert body in pos, ("cell %s: its own clause is not in the compiled "
                             "positive -- compress() dropped it" % letter)
        for term in ("glasses", "hands", "teenager"):
            assert term in neg, (letter, term)
        p = ctc.count(pos) if hasattr(ctc, "count") else None
        assert pos not in seen, "two cells compile to the same positive"
        seen.add(pos)
        worst_pos = max(worst_pos, len(pos))
        worst_neg = max(worst_neg, len(neg))
    print("  ok  10 distinct compiled prompts, every clause survives compress(),"
          " glasses/hands/teenager negated in all ten")

    root = build_root()
    argv = [s for s in root["steps"] if s["name"] == "cast"][0]["argv"]
    assert ARM == "nocontrol", (
        "controlnet_plate gates its ControlNet branch on `arm != \"nocontrol\"` "
        "-- any other arm name makes --control mandatory and the job exits rc 6")
    assert "--control" not in argv, "a ControlNet reached round 2B"
    assert "--ip-ref" not in argv, "an IP-Adapter reached round 2B"
    assert argv[argv.index("--seed") + 1] == str(SEED_BASE)
    assert argv[argv.index("--steps") + 1] == "40"
    assert argv[argv.index("--cfg") + 1] == "7.5"
    print("  ok  cell A: no --control, no --ip-ref, seed %d, 40 steps, cfg 7.5"
          % SEED_BASE)

    # The A/B claim this round rests on: same seeds as round 2, cell for cell.
    for index, (letter, _) in enumerate(CELLS):
        p2 = os.path.join(REPO, "pipeline", "jobs",
                          "%s.yaml" % r2.spec_id(letter))
        if os.path.isfile(p2):
            a2 = [s for s in derive_spec.load(p2)["steps"]
                  if s["name"] == "sample"][0]["argv"]
            assert a2[a2.index("--seed-start") + 1] == str(index), letter
    print("  ok  seeds line up with round 2 cell for cell (the A/B holds)")

    for letter, _ in CELLS:
        p = os.path.join(REPO, "pipeline", "jobs", "%s.yaml" % spec_id(letter))
        if os.path.isfile(p):
            got = derive_spec.load(p)
            assert got["id"] == spec_id(letter), p
            pay = got.get("payload") or {}
            assert any(k.endswith("prompt.txt") for k in pay), p
            wanted, _ = compiled(letter)
            assert any(v == wanted for k, v in pay.items()
                       if k.endswith("prompt.txt")), (
                "%s carries a STALE compiled prompt -- re-run --write" % p)
    print("  ok  emitted specs (those on disk) carry the current prompts")
    print("SELFTEST: PASS")
    return 0


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
