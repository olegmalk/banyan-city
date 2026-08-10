#!/usr/bin/env python3
"""002b beat 01 — ROUND 9, the DEPTH-CONTROLNET round: the geometry stays, the
colour goes.

WHY THIS IS NOT r8 AGAIN. r8 answered its question and the answer was half a
yes. Seven rounds of wording could not produce one grounded whole-plant frame;
the b15 init produced eight of eight, at both strengths, with the stem inside or
near the founder's ceiling. And all eight wear the plate's amber dusk, its shaft
of light and its macro bokeh, where the beat asks for `peach and gold sunrise
sky, wide shot`. r8's own t2i control draws that sky correctly on all four
seeds, so the prompt is fine and the init is overriding it.

r8's closing sentence is the thing this round has to answer:

    In this particular plate the palette IS the composition — the light shaft is
    what makes it a macro, and the macro is what makes the sapling read small —
    so strength cannot buy one without spending the other.

That sentence is true about STRENGTH and does not generalise to DEPTH. An
img2img init is an RGB array in which geometry and colour are the same numbers,
and `strength` is one scalar over that array, so there is no setting at which it
keeps one and drops the other — r8's ladder is conclusive on that. A depth map
performs the separation BEFORE diffusion starts: one channel of geometry with
the colour thrown away, so there is no colour left to leak. The question r9 asks
is not "can we tune the leak down" but "is the geometry still sufficient once
the colour is gone".

THE HONEST RISK, STATED UP FRONT. If what made the sapling read small to the
founder was the macro LOOK rather than the size relationship, then a
sunrise-wide-shot version of the same geometry may not read small to him. That
is a taste question (R4) that no measurement here can settle. This script exists
to produce exactly the frame that asks him that question.

THE SINGLE VARIABLE. Everything not named here is r8's, byte for byte: the base
checkpoint, bf16 on cuda, 832x1216, 40 steps, cfg 7.5, the seed rule, the
positive (65 CLIP tokens on the box) and the negative (72, r7's string
unchanged). The one change is that the plate arrives as
`image=<committed depth map>` through a ControlNet instead of as an init through
img2img. `control_guidance_start/end` are pinned at 0.0/1.0 deliberately: ending
control early is the standard trick for letting the prompt own late-stage
colour, but a depth map carries no colour, so here it would be a second variable
bought against a problem the architecture already solves. If geometry and
palette fight late in the denoise, that is r10's axis.

ONE SET OF WEIGHTS. The base pipeline is loaded once and
`AutoPipelineForText2Image.from_pipe(pipe, controlnet=cn)` swaps the class while
reusing the already-loaded modules — same discipline as r8's
`StableDiffusionXLImg2ImgPipeline.from_pipe(pipe)`. One dtype, one device, one
tokenizer, no reload between arms.

THE MAP IS COMMITTED, NOT DERIVED HERE. `Intel/dpt-hybrid-midas` never loads in
this script. Stage 0 derived the map, a human looked at it against three gates
(polarity: near is bright; the sprout survives the downsample; the shaft is
gone), and the map was committed as a file with its own sidecar. Regenerating it
at render time would make the round depend on an estimator's weights staying
byte-stable, which is the weaker design. This script asserts its sha256, and the
sha256 of the approved plate it was derived from — the G1 chain is
plate -> pinned estimator -> committed map -> pipeline, and neither end of it can
be swapped without the round refusing to start.

SHOTS.MD IS NOT EDITED, exactly as r8. The height predicate is stripped
script-side after asserting the fence on disk is byte-for-byte r7's, so a stale
checkout cannot start and the founder's approved shot list keeps ONE authored
version of this beat instead of nine.

THE ONE-SAMPLE RULE IS CODE HERE, NOT ETIQUETTE. `--frames` defaults to 1 and
the script REFUSES more than one frame without an explicit `--stage2`. Stage 1
is `d60`, seed 20260720, one frame, ~10 seconds; Stage 2 is the remaining twelve
and only runs if Stage 1 holds geometry AND draws this beat's own sky. The K
recipe cost an hour by skipping straight to fifteen on a defect one sample would
have shown in three minutes. `pipeline/budget.yaml` makes the spend guard code;
this makes the sample gate code.

TOKEN COUNTS ARE A BOX MEASUREMENT. `sd_prompt._token_estimate` over-counts a
positive of this shape by ~3 near the 77 boundary, and the whole comparability
claim of this round is that the positive is byte-identical to r8's 65 tokens and
the negative to r7's 72. A Mac-side count would not merely be imprecise, it
would invalidate the round — so `if _clip_tokenizer() is None: return 8` is
kept exactly as r8 has it. It sits AFTER the file/hash assertions rather than
before them, which is the one structural difference from r8: that ordering lets
`--dry` prove every hash and every dimension off-box, and it gates nothing,
because no prompt is built, nothing is measured and no weight is loaded until
after it.

    C:\\banyan-farm\\venv\\Scripts\\python.exe render_b01r9.py --root ... --measure
    C:\\banyan-farm\\venv\\Scripts\\python.exe render_b01r9.py --root ... --dry
    C:\\banyan-farm\\venv\\Scripts\\python.exe render_b01r9.py --root ... --arm d60

PRE-REGISTERED RUBRIC, fixed before any pixel exists. Two axes, because r9
claims two things. (A) GEOMETRY, unchanged from r8 so the numbers are
comparable: stem height fraction, apex to groundline over frame height, against
the 32% ceiling he revoked, with r8's ~30% (i35) as the standing best; plus
grounded-whole-plant, person and pale-slab counts, n of 4 per arm, person-binding
observed and never assumed. (B) PALETTE, the new axis, measured rather than
eyeballed: mean sky RGB over the top 25% against three references — the b15
plate, r8-i35-s0 (the leak) and r8-t2i-s0 (the correct sky) — plus the
column-luminance profile across the top 25%, where the plate peaks at x=333 of
832. r9 SUCCEEDS only if both hold; either alone is a failure, and the two
failures mean different things. Geometry holds and palette still leaks retires
structure-control for this beat and leaves the checkpoint swap and inpaint as
the named levers. Palette free and geometry gone is a scale question and argues
for a higher-scale r10, not a new architecture. THE FIG STAYS OBSERVED AND
UNGATED: 0 of 12 in r8, size adjectives make it larger, and a depth map of a
fruitless plate carries no fruit, so r9 says nothing new there.

NOTHING HERE IS A PICK. Steward-rendered candidates, sidecars written at render
time, `approved: false`, and nothing opened on the founder's screen.

THE SIDECAR NAMES THE FILE THAT WAS OPENED (fixed after auditing Stage 1's).
Stage 1 ran on the box with `--control C:\\banyan-farm\\b01-r9-depth-b15.png`,
because that clone sat at 11e5ab1 — one commit behind aef79ac, which is where
the map actually landed in the repo. The old code caught the `relative_to`
ValueError and quietly kept `CONTROL_REL`, so the sidecar recorded a
repo-relative path next to `repo_commit: 11e5ab1` at which that path does not
exist. The rendered bytes were never in doubt (CONTROL_SHA is asserted before a
weight loads, and it matched the committed map), but the pair as written was not
reproducible. So the recorded path is now always the path read; `control_map_in_repo`
says which kind of path it is; `control_map_at_repo_commit` is checked with
`git cat-file -e` and reports present/absent/unknown, never guessing; and
anything unresolvable is spelled out in `provenance_warning` and shouted on
stdout. None of it refuses — the defect was in the record, not the render.

Plan of record: B01-R9-PLAN.md. Direct ancestor: pipeline/render_b01r8.py.
"""
import argparse
import datetime
import hashlib
import importlib
import os
import re
import subprocess
import sys
import time
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# ---------------------------------------------------------------- the recipe
# Held constant from r8 so the arms differ by the control and nothing else.
NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, "
       "low quality, blurry, extra limbs, deformed, jpeg artifacts, "
       "realistic skin texture")
BASE = "cagliostrolab/animagine-xl-3.1"
LICENCE = "CreativeML Open RAIL++-M (use restrictions travel; D15)"
SEED = 20260719
W, H, STEPS, CFG = 832, 1216, 40, 7.5
DROP_NEG = "tall tree"
CANDIDATE_SET = "r9"
QUEUE_ENTRY = "ep2-b01-r7-coldopen-1786292601"   # the beat's open entry
TASK = "ep2-b01-r9-depth-controlnet"
BEAT = 1
EXPECT_DROP = 1          # `tiny`, `40cm`, `seedling` all fire _SMALL
EXTRA_NEG = ""           # r6, r7 and r8 carried none on this beat and r9 adds none

# ------------------------------------------------------------- the new arm
CONTROLNET = "diffusers/controlnet-depth-sdxl-1.0"
CONTROLNET_LICENCE = "openrail++ (D15 SAFE — same family as the base)"
# `variant="fp16"` selects which FILE is downloaded (the repo ships both fp16
# and fp32); `torch_dtype` sets the in-memory dtype and MUST match the UNet's,
# so bf16. A ControlNet left in fp16 against a bf16 UNet fails at the first
# forward pass on a scalar-type mismatch. Note this call is NOT portable to the
# xinsir repos, which ship no `*.fp16.safetensors` and raise if `variant` is
# passed at all — see B01-R9-PLAN.md §9.
CONTROLNET_VARIANT = "fp16"
CTRL_START, CTRL_END = 0.0, 1.0

# The estimator is NOT loaded here. It is recorded because the committed map is
# its output, and the sidecar has to carry the whole chain.
DEPTH_ESTIMATOR = "Intel/dpt-hybrid-midas"
DEPTH_ESTIMATOR_REV = "11eaf7a1cf4bd70740697dbc216f98980c0aeb03"
DEPTH_ESTIMATOR_LICENCE = "apache-2.0 (D15 SAFE — permissive, adds nothing)"

# arm id -> controlnet_conditioning_scale. Three points bracketing the diffusers
# card's own published `0.5  # recommended for good generalization`.
ARMS = {"d40": 0.40, "d60": 0.60, "d80": 0.80}
STAGE1_ARM = "d60"

# ------------------------------------------------------------- the assertions
# The control map: committed artifact, Stage 0 output, three gates passed.
CONTROL_REL = "genomes/sapling/nodes/002b-first-citizen/control/b01-r9-depth-b15.png"
CONTROL_SHA = "fda4bf6c8838c2da770ce79dd36c885f3c1699755fbb7ce4b0581fd1c32adc28"

# The plate the map was derived from: b15-r3-s1, the ONE sapling-in-grass frame
# the founder has passed, canon since d4488de. It is read here for its hash and
# for nothing else — it is NEVER passed to the pipeline. r8 conditioned on its
# pixels; r9 conditions on its geometry, and mixing the two would silently make
# this an img2img round wearing a ControlNet's name.
PLATE_REL = "genomes/sapling/nodes/001-capability-inventory/stills/15-something-s-coming.png"
PLATE_SHA = "f60c1404f88d45720ca295dfc753e9eaabb815446710bcfffb3c7a07b7277f54"

# shots.md as the plan was written against (commit 11e5ab1).
SHOTS_SHA = "445b8c682a5f94954d98a2a0be5209876c0c558c666c085ba126b35614e491c9"

# THE ONE EDIT, made script-side so shots.md keeps one authored fence.
STRIP_CLAUSE = " no taller than the grass around it"
EXPECT_PREFIX = "a tiny 40cm seedling standing in short grass"
FORBID_CLAUSE = "rising well above the grass"          # r6's; a stale checkout
AFTER_STRIP = "its sturdy curved stem, two oversized cotyledon leaves"

ANCHOR = ("cinematic lighting, detailed, newest, masterpiece, best quality, "
          "very aesthetic")

# r7's authored fence exactly as shots.md must still carry it.
R7_AUTHORED = (
    "A tiny 40cm seedling standing in short grass, its sturdy curved stem no "
    "taller than the grass around it, two oversized cotyledon leaves, one small "
    "round green fruit hanging from the stem, whole plant in frame, wide shot, "
    "peach and gold sunrise sky, no girl, no boy, no child, no person, no "
    "chibi, no mascot, no creature, no face, no branches, no night sky, "
    "cinematic lighting, detailed, newest, masterpiece, best quality, very "
    "aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.")

# The SENT positive r8's twelve frames were drawn with, read off their sidecars.
# r9's must come out byte-identical or the round is not comparable to r8's.
R8_POS_SENT = (
    "A tiny 40cm seedling standing in short grass, its sturdy curved stem, two "
    "oversized cotyledon leaves, one small round green fruit hanging from the "
    "stem, whole plant in frame, wide shot, peach and gold sunrise sky, "
    "cinematic lighting, detailed, newest, masterpiece, best quality, very "
    "aesthetic")

# The negative r6, r7 and r8 were all drawn with. Changing the conditioning must
# not move the negative by one byte, and if it does, the round has quietly
# become a two-variable round.
R7_NEG_SENT = (
    "photorealistic, 3d render, abstract, text, watermark, signature, "
    "low quality, blurry, extra limbs, deformed, mature tree, large tree, "
    "thick trunk, full canopy, forest, bush, shrubbery, girl, boy, child, "
    "person, chibi, mascot, creature, face, branches, night sky, photorealism")

# Measured on the box's own CLIP tokenizer for r8. Byte-identical strings should
# reproduce these exactly; a divergence is reported loudly rather than gated,
# because byte-identity is the assertion that actually carries the claim.
EXPECT_POS_TOKENS = 65
EXPECT_NEG_TOKENS = 72

PERSON_NEG = ("girl", "boy", "child", "person")

NOTE = (
    'round 9, the DEPTH-CONTROLNET round: the plate is taken as GEOMETRY ONLY, '
    'its colour discarded before the first denoise step. r8 settled half of '
    'this beat — seven rounds of wording produced no grounded whole-plant '
    'frame and the b15 init produced 8 of 8, at ~30% (i35) and ~25-34% (i55) '
    'stem height — and left the other half open: all eight wear the plate\'s '
    'amber dusk, its light shaft and its macro bokeh where the beat asks for '
    '`peach and gold sunrise sky, wide shot`, while r8\'s own t2i control drew '
    'that sky correctly on all four seeds. So the prompt is fine and the init '
    'is overriding it. r8\'s closing sentence — "in this particular plate the '
    'palette IS the composition, so strength cannot buy one without spending '
    'the other" — is true about STRENGTH and does not generalise to DEPTH: an '
    'RGB init makes geometry and colour the same numbers and `strength` is one '
    'scalar over both, whereas a depth map separates them BEFORE diffusion '
    'starts, one channel of geometry with no colour left to leak. THE SINGLE '
    'VARIABLE is the conditioning: base checkpoint, bf16/cuda, 832x1216, 40 '
    'steps, cfg 7.5, the seed rule, the sent positive (65 tokens) and the sent '
    'negative (72, r7\'s string) are all r8\'s byte for byte, and the plate '
    'arrives as image=<depth map> through diffusers/controlnet-depth-sdxl-1.0 '
    'instead of as an init. control_guidance_start/end are pinned at 0.0/1.0 '
    'deliberately: ending control early is the standard trick for letting the '
    'prompt own late-stage colour, but a depth map carries no colour, so here '
    'it would be a second variable bought against a problem the architecture '
    'already solves — if geometry and palette fight late in the denoise, that '
    'is r10\'s axis. ONE SET OF WEIGHTS: the base pipeline loads once and '
    'AutoPipelineForText2Image.from_pipe(pipe, controlnet=cn) swaps the class '
    'while reusing the loaded modules, the same discipline as r8\'s from_pipe. '
    'THE MAP IS COMMITTED, NOT DERIVED HERE — Intel/dpt-hybrid-midas never '
    'loads in this script; Stage 0 derived the map, a human passed it against '
    'three gates (polarity: near is bright, per MiDaS inverse depth; the '
    'sprout survives the estimator\'s downsample; b15\'s light shaft is gone '
    'from the sky band), and it was committed with its own sidecar so the '
    'round stays reproducible even if the estimator\'s weights or defaults '
    'move. G1 CHAIN, both ends asserted: approved plate b15-r3-s1 (canon since '
    'd4488de, sha f60c1404…) -> pinned estimator -> committed map (sha '
    'fda4bf6c…) -> pipeline. The map carries strictly LESS than the approved '
    'still, so it can subtract from approved content but cannot introduce '
    'unapproved content, and the plate itself is read for its hash only and is '
    'never passed to the pipeline. b15 is the only admissible geometry source '
    'and that is structural rather than a taste choice: every beat-01 frame '
    'carrying the right palette — r2-s3, r3-s3, r6-s3 — is unapproved or '
    'revoked and would fail G1 before the founder saw it, which is exactly why '
    'the fix has to be to discard the init\'s colour rather than to find a '
    'better-coloured init. SHOTS.MD WAS NOT EDITED; the height predicate is '
    'stripped script-side after asserting the fence on disk is byte-for-byte '
    'r7\'s, so a stale checkout cannot start. ONE SAMPLE IS ENFORCED IN CODE: '
    '--frames defaults to 1 and more than one frame refuses without an '
    'explicit --stage2, so Stage 1 (d60, seed 20260720, one frame) cannot be '
    'skipped past. THE TOKEN COUNTS ARE A BOX MEASUREMENT — the script refuses '
    'to run without a real CLIP tokenizer, because the estimator over-counts a '
    'positive of this shape by ~3 near the 77 boundary and the comparability '
    'claim rests on 65 and 72 exactly. PRE-REGISTERED RUBRIC, two axes: (A) '
    'geometry unchanged from r8 so the numbers compare — stem height fraction '
    'against the 32% ceiling he revoked, with r8\'s ~30% standing, plus '
    'grounded/person/pale-slab counts n of 4, person-binding observed not '
    'assumed; (B) palette, measured not eyeballed — mean sky RGB over the top '
    '25% against the plate, r8-i35-s0 (the leak) and r8-t2i-s0 (the correct '
    'sky), plus the column-luminance profile whose plate peak sits at x=333 of '
    '832. Both must hold: geometry-holds-palette-leaks retires '
    'structure-control for this beat and leaves the checkpoint swap and '
    'inpaint; palette-free-geometry-gone is a scale question and argues for a '
    'higher-scale r10. THE HONEST RISK, named before the pixels: if what made '
    'the sapling read small was the macro LOOK rather than the size '
    'relationship, a sunrise wide shot on the same geometry may not read small '
    'to him — that is R4 and no measurement here settles it; this frame exists '
    'to ask him. THE FIG STAYS OBSERVED AND UNGATED: 0 of 12 in r8, size '
    'adjectives make it larger, and a depth map of a fruitless plate carries '
    'no fruit. PROVISIONAL: steward-rendered candidate, not a pick and not '
    'canon, and nothing is opened on the founder\'s screen.')


# ------------------------------------------------------------------ helpers
def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(root: Path) -> str:
    """The commit the repo is on, read off .git with no subprocess."""
    try:
        head = (root / ".git" / "HEAD").read_text(encoding="utf-8").strip()
        if not head.startswith("ref:"):
            return head
        ref = head.split(":", 1)[1].strip()
        loose = root / ".git" / ref
        if loose.exists():
            return loose.read_text(encoding="utf-8").strip()
        packed = root / ".git" / "packed-refs"
        if packed.exists():
            for line in packed.read_text(encoding="utf-8").splitlines():
                if line.endswith(" " + ref):
                    return line.split(" ", 1)[0].strip()
    except Exception:
        pass
    return "unresolved"


# A plain YAML scalar where that is unambiguous, single-quoted where it is not.
# The in-repo relative path matches this and is therefore written exactly as it
# always was; a Windows absolute path (`C:\banyan-farm\b01-r9-depth-b15.png`)
# does not, and gets quoted. Single quotes rather than double, because YAML's
# double-quoted form reads `\b` as an escape and would silently mangle the path.
_PLAIN_SCALAR = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._/@=+()~,-]*$")


def yaml_scalar(value) -> str:
    s = str(value)
    if s and s == s.strip() and _PLAIN_SCALAR.match(s):
        return s
    return "'" + s.replace("'", "''") + "'"


def path_at_commit(root: Path, commit: str, rel: str) -> str:
    """'present' | 'absent' | 'unknown' — does `rel` exist in the tree at `commit`?

    `unknown` is returned for every case where the question could not be ASKED
    (git not on PATH, HEAD unresolved, a commit this clone does not have), so
    that a failed check can never be read as a clean answer. `git cat-file -e`
    alone cannot make that distinction — it exits nonzero both for a missing
    path and for a missing commit — so the commit is probed first.
    """
    if not commit or commit == "unresolved" or not rel:
        return "unknown"

    def _run(args):
        return subprocess.run(["git", "-C", str(root)] + args,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, timeout=30)

    try:
        if _run(["cat-file", "-e", commit + "^{commit}"]).returncode != 0:
            return "unknown"
        ok = _run(["cat-file", "-e", f"{commit}:{rel}"]).returncode == 0
    except Exception:
        return "unknown"
    return "present" if ok else "absent"


def control_provenance(control_path: Path, root: Path, commit: str) -> tuple:
    """What may HONESTLY be written down about the map that was ACTUALLY opened.

    Returns `(recorded_path, in_repo, at_commit, warning)`.

    The Stage 1 sidecar recorded `control_map: <the in-repo default>` next to
    `repo_commit: 11e5ab1` for a render whose map was read from a loose copy at
    `C:\\banyan-farm\\...`, because the old code caught the `relative_to`
    ValueError and kept the hard-coded default. The pair it wrote does not
    resolve: the map landed in the repo one commit later, at aef79ac. The bytes
    were right — CONTROL_SHA is asserted before any weight loads — but the
    provenance was not reproducible as written. So: the path recorded is always
    the path opened, `in_repo` says at a glance which kind of path it is, and
    anything that makes the (path, commit) pair unresolvable is stated in the
    sidecar instead of being dropped on the floor. This never refuses — the
    render is legitimate and sha-asserted; only the record was wrong.
    """
    try:
        rel = str(control_path.relative_to(root)).replace("\\", "/")
    except ValueError:
        rel = None

    if rel is None:
        return (str(control_path), False, "n/a", (
            "control_map is OUTSIDE this checkout (" + str(root) + "). The "
            "path recorded in control_map is the ABSOLUTE path of the file "
            "this render actually opened; it is not repo-relative and it does "
            "not resolve at repo_commit " + commit + " or at any other "
            "commit. The bytes are still the approved Stage 0 map — sha256 "
            + CONTROL_SHA + " is asserted before any weight loads and the run "
            "refuses without it — so to REPRODUCE this render you must supply "
            "that file (it is committed at " + CONTROL_REL + "), not check it "
            "out of this commit."))

    at = path_at_commit(root, commit, rel)
    if at == "present":
        return (rel, True, at, None)
    if at == "absent":
        return (rel, True, at, (
            "control_map is inside the checkout but does NOT exist at "
            "repo_commit " + commit + ": `git cat-file -e " + commit + ":"
            + rel + "` fails. This clone is on a commit that does not carry "
            "the map, so the (control_map, repo_commit) pair recorded here is "
            "NOT reproducible as written — resolve the path against a commit "
            "that contains it. The bytes are sha-asserted (" + CONTROL_SHA
            + "), so what is wrong is the record, not the render."))
    return (rel, True, at, (
        "control_map's presence at repo_commit " + commit + " could NOT be "
        "verified here (git unusable: not on PATH, HEAD unresolved, or the "
        "commit is not in this clone). Treat control_map_at_repo_commit: "
        "unknown as unverified, never as confirmed. The bytes are sha-asserted "
        "(" + CONTROL_SHA + ")."))


def module_version(name: str) -> str:
    """Runtime version of an installed module, or a self-describing miss.

    Every path is caught: this is provenance, and provenance must never be the
    thing that kills a render that is otherwise fine.
    """
    try:
        mod = importlib.import_module(name)
    except Exception:
        return "unresolved (not importable here)"
    try:
        v = getattr(mod, "__version__", None)
        if v:
            return str(v)
        from importlib.metadata import version as _v
        return str(_v(name))
    except Exception:
        return "unresolved (imported, no version string)"


def runtime_versions() -> dict:
    return {"python": sys.version.split()[0],
            "torch": module_version("torch"),
            "diffusers": module_version("diffusers"),
            "transformers": module_version("transformers")}


def utc_now() -> str:
    return datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hub_revision(repo_id: str) -> str:
    """Best-effort: the snapshot commit(s) cached for a repo. No network."""
    try:
        try:
            from huggingface_hub.constants import HF_HUB_CACHE as cache
        except Exception:
            cache = os.environ.get("HF_HUB_CACHE") or os.path.join(
                os.environ.get("HF_HOME", str(Path.home() / ".cache" / "huggingface")),
                "hub")
        snaps = Path(cache) / ("models--" + repo_id.replace("/", "--")) / "snapshots"
        names = sorted(p.name for p in snaps.iterdir() if p.is_dir())
        if names:
            return ", ".join(names)
    except Exception:
        pass
    return "unresolved (hub default `main` at load time; not pinned, as r5-r8)"


def strip_height_clause(authored: str) -> str:
    """Delete the height predicate, keep the stem. Exactly one occurrence."""
    if authored.count(STRIP_CLAUSE) != 1:
        raise ValueError(
            f"expected exactly 1 occurrence of {STRIP_CLAUSE!r}, "
            f"found {authored.count(STRIP_CLAUSE)}")
    return authored.replace(STRIP_CLAUSE, "", 1)


def strip_term(neg: str, term: str) -> tuple:
    parts = [p.strip() for p in neg.split(",")]
    kept = [p for p in parts if p.lower() != term.lower()]
    return ", ".join(kept), len(parts) - len(kept)


def build(authored, compress, beat_negative):
    """(positive, sent negative, recipe negative, dropped sentences, warnings)."""
    warns = []
    pos, dropped = compress(authored)
    neg_full = beat_negative(NEG, authored, EXTRA_NEG, warn=warns.append)
    neg, removed = strip_term(neg_full, DROP_NEG)
    return pos, neg, neg_full, dropped, warns, removed


def sidecar(png: Path, *, seed: int, arm: str, scale: float, pos: str, neg: str,
            neg_full: str, secs: float, warns: list, task: str, shots_sha: str,
            pos_tokens: int, neg_tokens: int, control_rel: str,
            control_sha: str, frames: int, commit: str, base_rev: str,
            cn_rev: str, control_in_repo: bool, control_at_commit: str,
            control_abs: str, prov_warning, rendered_at: str, versions: dict,
            scheduler: str, device: str, dtype: str) -> None:
    """`control_rel` is the path that was ACTUALLY read — repo-relative when the
    file resolved inside --root, absolute otherwise. It is never the constant.
    Every argument here is required on purpose: a default would be exactly the
    silent substitution this function was fixed to stop making."""
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())
    lines = ["# Still provenance (7.2), written AT RENDER TIME by render_b01r9.py",
             "# on the rtx5090 (C:\\banyan-farm\\sample-b01-r9).",
             "# The negative below is what the model actually saw. The recipe's own",
             "# negative, before this script's one deliberate removal, was:",
             f"#   {neg_full}"]
    lines += [f"#   NEGWARN: {w}" for w in warns]
    body = ["platform: local-gpu (rtx5090)",
            f"model: {BASE}",
            f"model_revision: {base_rev}",
            f"model_licence: {LICENCE}",
            f"controlnet: {CONTROLNET}",
            f"controlnet_revision: {cn_rev}",
            f"controlnet_variant: {CONTROLNET_VARIANT} (file selector; dtype is bfloat16)",
            f"controlnet_licence: {CONTROLNET_LICENCE}",
            f"controlnet_conditioning_scale: {scale}",
            f"control_guidance_start: {CTRL_START}",
            f"control_guidance_end: {CTRL_END}",
            f"control_map: {yaml_scalar(control_rel)}",
            # true  -> control_map is repo-relative, resolve it at repo_commit.
            # false -> control_map is an absolute path outside this checkout;
            #          repo_commit says nothing about it. See provenance_warning.
            f"control_map_in_repo: {str(bool(control_in_repo)).lower()}",
            f"control_map_at_repo_commit: {control_at_commit}",
            f"control_map_abs: {yaml_scalar(control_abs)}",
            f"control_map_sha256: {control_sha}",
            f"control_map_derived_from: {PLATE_REL}",
            f"control_map_source_sha256: {PLATE_SHA}",
            f"depth_estimator: {DEPTH_ESTIMATOR}",
            f"depth_estimator_revision: {DEPTH_ESTIMATOR_REV}",
            f"depth_estimator_licence: {DEPTH_ESTIMATOR_LICENCE}",
            "depth_estimator_loaded_at_render_time: false",
            f"shot_beat: {BEAT}",
            f"size: {W}x{H}",
            f"steps: {STEPS}",
            f"guidance: {CFG}",
            f"seed: {seed}",
            f"seed_rule: SEED({SEED}) + BEAT({BEAT}) + i*1000",
            f"seeds_in_batch: {frames}",
            f"arm: {arm}",
            "pipeline: StableDiffusionXLControlNetPipeline (text2img + depth control)",
            "init_image: none (r9 conditions on geometry, not pixels)",
            "strength: n/a",
            f"task: {task}",
            f"queue_entry: {QUEUE_ENTRY}",
            f"render_round: {CANDIDATE_SET}",
            f"candidate_set: {CANDIDATE_SET}-{arm}",
            f"negative_terms_removed: {DROP_NEG}",
            f"prompt_source_sha256: {shots_sha}",
            f"positive_clip_tokens: {pos_tokens}",
            f"negative_clip_tokens: {neg_tokens}",
            "tokenizer: openai/clip-vit-large-patch14 (transformers, on the box)",
            "positive_identical_to_r8: true",
            "negative_identical_to_r7: true",
            "shots_md_edited: false",
            f"repo_commit: {commit}",
            "provenance_warning: >-" if prov_warning else
            "provenance_warning: none",
            block(prov_warning) if prov_warning else
            "  # control_map is repo-relative and present at repo_commit.",
            # Quoted so YAML keeps it a string: unquoted, `safe_load` resolves
            # an ISO8601 stamp to a datetime and readers comparing scalars to
            # every other field here get a different type back for this one.
            f"rendered_at_utc: {yaml_scalar(rendered_at)}",
            f"device: {yaml_scalar(device)}",
            f"dtype: {yaml_scalar(dtype)}",
            f"scheduler: {yaml_scalar(scheduler)}",
            f"python_version: {yaml_scalar(versions.get('python', 'unresolved'))}",
            f"torch_version: {yaml_scalar(versions.get('torch', 'unresolved'))}",
            f"diffusers_version: {yaml_scalar(versions.get('diffusers', 'unresolved'))}",
            f"transformers_version: "
            f"{yaml_scalar(versions.get('transformers', 'unresolved'))}",
            "single_variable: >-",
            block("The conditioning, and only the conditioning. Base, dtype, "
                  "device, size, steps, cfg, seed rule, sent positive and sent "
                  "negative are r8's byte for byte; the b15 plate arrives as a "
                  "committed depth map through "
                  "diffusers/controlnet-depth-sdxl-1.0 instead of as an "
                  "img2img init. control_guidance_start/end are pinned at "
                  "0.0/1.0 so no second axis is opened."),
            "g1_chain: >-",
            block("b15-r3-s1 (APPROVED, canon since d4488de, sha256 "
                  f"{PLATE_SHA}) -> {DEPTH_ESTIMATOR} @ {DEPTH_ESTIMATOR_REV}, "
                  "fixed parameters, no sampling -> committed map (sha256 "
                  f"{control_sha}) -> ControlNet. Both hashes are asserted at "
                  "render time. The map carries strictly less than the "
                  "approved still — one channel of geometry, colour discarded "
                  "— so it can subtract from approved content but cannot "
                  "introduce unapproved content. The plate itself was read for "
                  "its hash only and was never passed to the pipeline."),
            "provisional: >-",
            block("PROVISIONAL. A steward-rendered CANDIDATE, not a pick and not "
                  "canon. Scored against taste/steward-model.v1 and logged in "
                  "taste/steward-model.ledger.yaml BEFORE the founder saw it. "
                  "Ground truth is the founder (R4); he has ratified nothing "
                  "here. Never takes a canon filename, is not published, not "
                  "posted, and not assembled into an episode."),
            "approved: false",
            "recipe_inherited_from: >-",
            block("round 8, takes/stills/01-cold-open-r8-*.png — model, size, "
                  "steps, cfg, seed rule, the one-term negative removal, the "
                  "script-side strip of the height predicate and both sent "
                  "prompts are r8's unchanged. What is new is the depth "
                  "ControlNet in place of the img2img init, per "
                  "B01-R9-PLAN.md."),
            f"wall_seconds: {secs:.0f}",
            "cost_usd: 0",
            "note: |-", block(NOTE),
            "prompt: |-", block(pos),
            "negative: |-", block(neg)]
    png.with_suffix(".png.meta.yaml").write_text("\n".join(lines + body) + "\n",
                                                 encoding="utf-8")


# --------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(
        description="beat 01 round 9 — depth-ControlNet over the approved b15 "
                    "plate's geometry. Stage 1 is one frame; more than one "
                    "frame refuses without --stage2.")
    ap.add_argument("--root", default=None,
                    help="repo root (default: the parent of pipeline/)")
    ap.add_argument("--shots", default=None,
                    help="path to shots.md (default: 002b-first-citizen/shots.md "
                         "under --root)")
    ap.add_argument("--control", default=None,
                    help=f"path to the committed depth map (default: "
                         f"{CONTROL_REL} under --root)")
    ap.add_argument("--arm", default=STAGE1_ARM, choices=sorted(ARMS),
                    help=f"conditioning arm (default {STAGE1_ARM}, Stage 1's)")
    ap.add_argument("--scale", type=float, default=None,
                    help="controlnet_conditioning_scale; must equal the arm's "
                         "own value or the run refuses, because the arm id is "
                         "what the filename and the sidecar claim")
    ap.add_argument("--seed", type=int, default=SEED,
                    help=f"base seed (default {SEED}); frame i uses "
                         f"seed + BEAT({BEAT}) + i*1000")
    ap.add_argument("--out", default=None,
                    help="output directory (default: ./out beside this script)")
    ap.add_argument("--frames", type=int, default=1,
                    help="frames to render (default 1 = Stage 1). >1 requires "
                         "--stage2")
    ap.add_argument("--stage2", action="store_true",
                    help="acknowledge that Stage 1 was rendered AND LOOKED AT, "
                         "unlocking --frames > 1")
    ap.add_argument("--dry", action="store_true",
                    help="resolve everything, assert every hash and dimension, "
                         "print the plan; load no weights and touch no GPU")
    ap.add_argument("--measure", action="store_true",
                    help="print r9's and r8's CLIP token counts side by side on "
                         "this box's tokenizer, then exit; draw nothing")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "pipeline"))
    from generate_shots import parse_shots                          # noqa: E402
    from sd_prompt import (beat_negative, compress,                 # noqa: E402
                           negative_tokens, _clip_tokenizer)

    node = root / "genomes/sapling/nodes/002b-first-citizen"
    shots_path = Path(a.shots).resolve() if a.shots else node / "shots.md"
    control_path = Path(a.control).resolve() if a.control else root / CONTROL_REL
    plate_path = root / PLATE_REL
    out = Path(a.out).resolve() if a.out else Path(__file__).resolve().parent / "out"

    scale = ARMS[a.arm] if a.scale is None else a.scale
    commit = git_commit(root)

    print(f"\n== beat {BEAT:02d} cold-open [{CANDIDATE_SET}] arm {a.arm} "
          f"scale {scale} — depth ControlNet", flush=True)
    print(f"   root:     {root}  (commit {commit})", flush=True)
    print(f"   out:      {out}", flush=True)

    # ================================================================ SECTION A
    # Files, hashes and dimensions. Pure stdlib + PIL: no transformers, no
    # torch, no CUDA, nothing downloaded. Deliberately FIRST so `--dry` proves
    # every one of these off-box, where the CLIP gate below would otherwise
    # stop the run before a single hash had been checked.

    # A1 — the arm id must mean what it says. Rendering 0.80 into a file called
    # d60 would corrupt the round's provenance more quietly than any crash.
    if a.arm in ARMS and abs(scale - ARMS[a.arm]) > 1e-9:
        print(f"   !! ARM/SCALE MISMATCH: arm {a.arm} is "
              f"controlnet_conditioning_scale {ARMS[a.arm]}, but --scale "
              f"{scale} was given. The arm id is what the filename and the "
              f"sidecar claim. Use the matching arm, or add a new arm id for a "
              f"new scale; stopping.", flush=True)
        return 18

    # A2 — the one-sample rule, as code rather than as etiquette (CLAUDE.md,
    # 2026-08-03; B01-R9-PLAN.md §7). Stage 1 is ONE frame, looked at by a
    # human, before the other twelve exist.
    if a.frames < 1:
        print(f"   !! --frames {a.frames} is not a number of frames; stopping.",
              flush=True)
        return 17
    if a.frames > 1 and not a.stage2:
        print(f"   !! --frames {a.frames} without --stage2. The house rule is "
              f"ONE SAMPLE per recipe change, and r9 changes the recipe: "
              f"render Stage 1 ({STAGE1_ARM}, seed {SEED + BEAT}, one frame), "
              f"have a human LOOK at it, and only then pass --stage2. The K "
              f"recipe cost an hour by skipping straight to fifteen on a "
              f"defect one sample would have shown in three minutes; "
              f"stopping.", flush=True)
        return 17

    # A3 — shots.md is the prompt source and its hash is the plan's pin.
    if not shots_path.exists():
        print(f"   !! SHOTS MISSING: {shots_path}; stopping.", flush=True)
        return 13
    raw = shots_path.read_bytes()
    shots_sha = hashlib.sha256(raw).hexdigest()
    print(f"   shots.md: {shots_path}\n   shots sha256: {shots_sha}", flush=True)
    if shots_sha != SHOTS_SHA:
        print(f"   !! SHOTS.MD SHA MISMATCH — expected {SHOTS_SHA} (the pin "
              f"B01-R9-PLAN.md was written against, commit 11e5ab1). This "
              f"round strips one clause out of that exact file; against any "
              f"other text the strip means something else; stopping.",
              flush=True)
        return 13

    shots = {s["num"]: s for s in parse_shots(raw.decode("utf-8"))}
    s = shots[BEAT]
    slug = s["slug"]
    authored_r7 = s["prompt"]

    # A4 — the fence on disk must be r7's, exactly. Byte assertion, no
    # tokenizer needed, so `--dry` can prove it anywhere.
    if authored_r7 != R7_AUTHORED:
        print("   !! shots.md's beat 01 fence is NOT r7's. This round strips one "
              "clause out of that exact string; against any other text the "
              "strip means something else.\n"
              f"      on disk: {authored_r7}\n      expected: {R7_AUTHORED}\n"
              "   stopping.", flush=True)
        return 4
    if FORBID_CLAUSE in authored_r7.lower():
        print(f"   !! r6 clause `{FORBID_CLAUSE}` is on disk — stale checkout; "
              f"stopping.", flush=True)
        return 6
    print("   fence: byte-identical to r7's authored text", flush=True)

    # A5 — the control map. Committed Stage 0 artifact; its hash and its size
    # are the round. No resize: a map that is not 832x1216 is the wrong file,
    # not a file to be fixed up.
    if not control_path.exists():
        print(f"   !! CONTROL MAP MISSING: {control_path}\n"
              f"      Stage 0 derives it (committed at {CONTROL_REL}); "
              f"stopping.", flush=True)
        return 14
    control_sha = sha256_of(control_path)
    print(f"   control:  {control_path}\n   control sha256: {control_sha}",
          flush=True)
    if control_sha != CONTROL_SHA:
        print(f"   !! CONTROL MAP SHA MISMATCH — expected {CONTROL_SHA}. The "
              f"map is the Stage 0 artifact a human passed against the "
              f"polarity / sprout / shaft gates; a different file has not been "
              f"through those gates; stopping.", flush=True)
        return 15
    from PIL import Image                                            # noqa: E402
    control_img = Image.open(control_path).convert("RGB")
    print(f"   control size: {control_img.size[0]}x{control_img.size[1]}",
          flush=True)
    if control_img.size != (W, H):
        print(f"   !! CONTROL MAP IS {control_img.size}, not {(W, H)}. The map "
              f"is derived at the render size on purpose — no resize, no crop; "
              f"stopping.", flush=True)
        return 16

    # A6 — the plate. Read for its hash and for nothing else: it is the G1
    # source of the map and it is NEVER passed to the pipeline. r8 conditioned
    # on these pixels; r9 conditions on their geometry.
    if not plate_path.exists():
        print(f"   !! PLATE MISSING: {plate_path}\n      The approved plate is "
              f"the head of this round's G1 chain and its hash is recorded in "
              f"every sidecar; stopping.", flush=True)
        return 11
    plate_sha = sha256_of(plate_path)
    print(f"   plate:    {PLATE_REL}\n   plate sha256: {plate_sha}  "
          f"(provenance only — NOT passed to the pipeline)", flush=True)
    if plate_sha != PLATE_SHA:
        print(f"   !! PLATE SHA MISMATCH — expected {PLATE_SHA}. b15-r3-s1 is "
              f"the only G1-admissible geometry source for this beat and the "
              f"committed map claims to be derived from it; stopping.",
              flush=True)
        return 12

    # A7 — WHAT GETS WRITTEN DOWN about the map just read. Not an assertion and
    # not a refusal: the bytes passed A5 and the render is legitimate. This is
    # the record, and the record has to name the file that was actually opened.
    # Resolved here, inside Section A, so `--dry` proves it off-box alongside
    # every hash — the CLIP gate below stops a Mac before Section C.
    control_rel, control_in_repo, control_at_commit, prov_warning = \
        control_provenance(control_path, root, commit)
    print(f"   control_map (recorded): {control_rel}", flush=True)
    print(f"   control_map_in_repo: {str(control_in_repo).lower()}   "
          f"at repo_commit {commit}: {control_at_commit}", flush=True)
    if prov_warning:
        loud = ("!! PROVENANCE WARNING — the render is fine, the RECORD is not "
                "clean:")
        print("\n   " + loud, flush=True)
        for ln in prov_warning.split(". "):
            if ln.strip():
                print(f"      {ln.strip().rstrip('.')}.", flush=True)
        print(f"      recorded control_map: {control_rel}\n"
              f"      recorded repo_commit: {commit}\n"
              f"      This is written into every sidecar this run produces as "
              f"`provenance_warning:`, so no reader is misled.\n", flush=True)

    seeds = [a.seed + BEAT + i * 1000 for i in range(a.frames)]
    print(f"   arms available: "
          f"{', '.join(f'{k}={v}' for k, v in sorted(ARMS.items()))}", flush=True)
    print(f"   control_guidance: {CTRL_START} -> {CTRL_END} (pinned; r10's axis, "
          f"not r9's)", flush=True)
    print(f"   frames: {a.frames}  seeds: {seeds}"
          f"{'  [stage2]' if a.stage2 else '  [stage 1, one sample]'}",
          flush=True)

    # ================================================================ SECTION B
    # The tokenizer gate, unchanged from r7 and r8. Nothing has been measured
    # and nothing has been loaded above this line, so moving it below the file
    # assertions costs the gate nothing and buys `--dry` its whole value
    # off-box.
    if _clip_tokenizer() is None:
        print("!! NO CLIP TOKENIZER — transformers is not importable, so every "
              "token count here would be the estimator that over-counts this "
              "prompt by ~3 near the 77 boundary. The negative is fitted to a "
              "77-token budget, so a wrong count silently produces a DIFFERENT "
              "sent negative and the round stops being comparable to r7/r8. "
              "Run this on the box's venv; stopping.", flush=True)
        return 8

    # ================================================================ SECTION C
    # The prompts, and the traps that guard them.
    authored = strip_height_clause(authored_r7)
    pos, neg, neg_full, dropped, warns, removed = build(
        authored, compress, beat_negative)

    print(f"\n   AUTHORED(r7, on disk): {authored_r7}", flush=True)
    print(f"   AUTHORED(r9, stripped): {authored}", flush=True)
    print(f"   POS: {pos}", flush=True)
    print(f"   NEG(recipe): {neg_full}", flush=True)
    print(f"   NEG(sent):   {neg}", flush=True)
    pos_tokens = negative_tokens(pos)
    neg_tokens = negative_tokens(neg)
    print(f"   positive tokens: {pos_tokens} (budget 77, r8 measured "
          f"{EXPECT_POS_TOKENS})", flush=True)
    print(f"   negative tokens: recipe {negative_tokens(neg_full)} -> "
          f"sent {neg_tokens} (budget 77, r7 measured {EXPECT_NEG_TOKENS})",
          flush=True)
    for w in warns:
        print(f"   NEGWARN: {w}", flush=True)
    if pos_tokens != EXPECT_POS_TOKENS or neg_tokens != EXPECT_NEG_TOKENS:
        print(f"   ** TOKEN COUNTS MOVED: {pos_tokens}/{neg_tokens} against "
              f"r8's {EXPECT_POS_TOKENS}/{EXPECT_NEG_TOKENS} on byte-identical "
              f"strings — the tokenizer itself has changed. Not gated here "
              f"because byte-identity is the assertion that carries the claim, "
              f"but say so in the report.", flush=True)

    if a.measure:
        print("\n-- r8 CONTROL, recorded on this box's tokenizer --", flush=True)
        print(f"   POS: {R8_POS_SENT}", flush=True)
        print(f"   positive tokens: {negative_tokens(R8_POS_SENT)}  "
              f"(recorded {EXPECT_POS_TOKENS})", flush=True)
        print(f"   NEG: {R7_NEG_SENT}", flush=True)
        print(f"   negative tokens: {negative_tokens(R7_NEG_SENT)}  "
              f"(recorded {EXPECT_NEG_TOKENS})", flush=True)
        print(f"\n-- r9 --\n   positive tokens: {pos_tokens}  "
              f"anchor {'INTACT' if pos.rstrip().endswith(ANCHOR) else 'DROPPED'}"
              f"  dropped={dropped}", flush=True)
        print(f"   negative tokens: {neg_tokens}", flush=True)
        print(f"   positive byte-identical to r8: {pos == R8_POS_SENT}",
              flush=True)
        print(f"   negative byte-identical to r7: {neg == R7_NEG_SENT}",
              flush=True)
        print(f"   delta r9-r8: {pos_tokens - negative_tokens(R8_POS_SENT)} "
              f"tokens on the positive, "
              f"{neg_tokens - negative_tokens(R7_NEG_SENT)} on the negative",
              flush=True)
        return 0

    # C1 — the strip landed where it was aimed, and the height predicate is
    # gone from the SENT positive rather than merely from the fence.
    low = pos.lower()
    if not low.startswith(EXPECT_PREFIX):
        print(f"   !! POSITIVE does not open `{EXPECT_PREFIX}` — opens "
              f"`{pos[:60]}`; stopping.", flush=True)
        return 4
    if AFTER_STRIP not in low:
        print(f"   !! the strip did not join up: `{AFTER_STRIP}` is not in the "
              f"positive; stopping.", flush=True)
        return 5
    if "taller than" in low:
        print("   !! `taller than` is still in the SENT positive — the height "
              "instruction left the text in r8 and must stay out; stopping.",
              flush=True)
        return 5
    # C2 — the positive must be r8's, byte for byte. This is the comparability
    # claim of the whole round: r9 differs from r8 by the conditioning alone.
    if pos != R8_POS_SENT:
        print("   !! SENT POSITIVE DIFFERS FROM r8's. r9's only claim is that "
              "the conditioning changed and nothing else did.\n"
              f"      r8: {R8_POS_SENT}\n      r9: {pos}\n   stopping.",
              flush=True)
        return 5
    # C3 — and the negative must not have moved either.
    if neg != R7_NEG_SENT:
        print("   !! SENT NEGATIVE DIFFERS FROM r6/r7/r8's. Changing the "
              "conditioning must not move the negative by one byte.\n"
              f"      r7: {R7_NEG_SENT}\n      r9: {neg}\n   stopping.",
              flush=True)
        return 7
    missing = [t for t in PERSON_NEG
               if t not in [p.strip().lower() for p in neg.split(",")]]
    if missing:
        print(f"   !! PERSON TERMS DROPPED by the 77-token budget: "
              f"{', '.join(missing)}; stopping.", flush=True)
        return 9
    if not pos.rstrip().endswith(ANCHOR):
        print(f"   !! STYLE ANCHOR DROPPED — the positive does not end with "
              f"`{ANCHOR}`; stopping.", flush=True)
        return 10
    if removed != EXPECT_DROP:
        print(f"   !! EXPECTED to remove {EXPECT_DROP} x '{DROP_NEG}', removed "
              f"{removed} — stopping so a human decides.", flush=True)
        return 2
    if dropped:
        print(f"   !! POSITIVE DROPPED: {' | '.join(dropped)} — stopping.",
              flush=True)
        return 3

    if a.dry:
        print(f"\nDRY OK — arm {a.arm} scale {scale}, control_guidance "
              f"{CTRL_START}->{CTRL_END}, {a.frames} frame(s) at seeds "
              f"{seeds}, {W}x{H} / {STEPS} steps / cfg {CFG}\n"
              f"   base:       {BASE} (bf16, cuda, use_safetensors)\n"
              f"   controlnet: {CONTROLNET} (variant fp16 file, bf16 in memory)\n"
              f"   sidecar would record: control_map: {control_rel} | "
              f"control_map_in_repo: {str(control_in_repo).lower()} | "
              f"control_map_at_repo_commit: {control_at_commit} | "
              f"provenance_warning: {'yes' if prov_warning else 'none'}\n"
              f"   would write: "
              f"{out / f'{BEAT:02d}-{slug}-{CANDIDATE_SET}-{a.arm}-s0.png'}\n"
              f"   nothing drawn, no weights loaded, GPU untouched", flush=True)
        return 0

    out.mkdir(parents=True, exist_ok=True)

    import torch                                                     # noqa: E402
    from diffusers import (AutoPipelineForText2Image,                # noqa: E402
                           ControlNetModel, StableDiffusionXLPipeline)
    t_load = time.time()
    # ONE set of base weights. from_pipe swaps the pipeline class while reusing
    # the already-loaded modules rather than copying them — r8's discipline,
    # one derivation further along.
    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE, torch_dtype=torch.bfloat16, use_safetensors=True)
    pipe.to("cuda")
    # `variant` picks the fp16 FILE; `torch_dtype` sets the in-memory dtype and
    # must match the UNet's bf16, or the first forward pass dies on a
    # scalar-type mismatch.
    cn = ControlNetModel.from_pretrained(
        CONTROLNET, variant=CONTROLNET_VARIANT, torch_dtype=torch.bfloat16,
        use_safetensors=True)
    cn.to("cuda")
    cnet = AutoPipelineForText2Image.from_pipe(pipe, controlnet=cn)
    print(f"MODEL_LOADED cuda/bfloat16 in {time.time() - t_load:.0f}s "
          f"({type(cnet).__name__})", flush=True)

    base_rev = hub_revision(BASE)
    cn_rev = hub_revision(CONTROLNET)

    # Runtime facts, read off the objects that were actually built rather than
    # asserted from the constants. Every read is caught: a missing attribute on
    # some future diffusers must degrade one provenance field, never kill a
    # render that has already loaded its weights.
    versions = runtime_versions()
    try:
        device = str(cnet.device)
    except Exception:
        device = "unresolved"
    try:
        dtype = str(cnet.dtype).replace("torch.", "")
    except Exception:
        dtype = "unresolved"
    try:
        scheduler = type(cnet.scheduler).__name__
    except Exception:
        scheduler = "unresolved"
    print(f"RUNTIME device={device} dtype={dtype} scheduler={scheduler} "
          f"python={versions['python']} torch={versions['torch']} "
          f"diffusers={versions['diffusers']} "
          f"transformers={versions['transformers']}", flush=True)

    n = 0
    for i, seed in enumerate(seeds):
        g = torch.Generator(device="cpu").manual_seed(seed)
        t0 = time.time()
        img = cnet(prompt=pos, negative_prompt=neg, image=control_img,
                   controlnet_conditioning_scale=scale,
                   control_guidance_start=CTRL_START,
                   control_guidance_end=CTRL_END,
                   num_inference_steps=STEPS, guidance_scale=CFG,
                   generator=g, width=W, height=H).images[0]
        f = out / f"{BEAT:02d}-{slug}-{CANDIDATE_SET}-{a.arm}-s{i}.png"
        img.save(f)
        secs = time.time() - t0
        sidecar(f, seed=seed, arm=a.arm, scale=scale, pos=pos, neg=neg,
                neg_full=neg_full, secs=secs, warns=warns, task=TASK,
                shots_sha=shots_sha, pos_tokens=pos_tokens,
                neg_tokens=neg_tokens, control_rel=control_rel,
                control_sha=control_sha, frames=a.frames, commit=commit,
                base_rev=base_rev, cn_rev=cn_rev,
                control_in_repo=control_in_repo,
                control_at_commit=control_at_commit,
                control_abs=str(control_path), prov_warning=prov_warning,
                rendered_at=utc_now(), versions=versions,
                scheduler=scheduler, device=device, dtype=dtype)
        n += 1
        print(f"   {f.name} seed={seed} {secs:.0f}s  ({n}/{len(seeds)})",
              flush=True)

    print(f"\nDONE {n} still(s) in {out}", flush=True)
    if not a.stage2:
        print("STAGE 1 COMPLETE — a human looks at this frame before --stage2 "
              "unlocks the remaining twelve.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
