#!/usr/bin/env python3
"""QUEUE HISTORY — every render job the box ran, with its full recipe, in one
committed JSON the /queue page can bake without seeing a farm branch.

The founder, 2026-08-14: "i cant keep blindly saying these videos are low
quality, lets improve the queue so i actually understand exactly how these
beats are being generated. we need to see a history of the queue, what has
been generated, what image reference did it use, what was the prompt, etc.
and also we need to see future things in the queue."

WHY A COMMITTED FILE AND NOT A LIVE FETCH. The provenance of a finished job is
scattered across two branches: the box sidecar (`farm-out/box/<id>.json` on
origin/farm-results-rtx5090) has the run record but no prompts; the prompts
live in the per-artifact `.yaml` sidecars beside the images (same branch) or —
for motion jobs since the encode/render split — ONLY in the committed spec's
`payload:` on main. A deploy checkout has no farm branches (same reason
`pipeline/measured/box-work-daily.yaml` exists), and a reader's browser cannot
join yaml across branches. So this script does the join on a laptop that CAN
see origin/farm-results-rtx5090 and writes ONE file:

    pipeline/measured/queue-history.json

Re-run it (then commit the file) when you want /queue's history to move —
nothing else refreshes it. `--refresh` keeps rows for sidecars already
extracted and appends only new ones; the default is a full rebuild.

HONESTY RULES, inherited from the pulse and status pages:
 * no guessed fields — a prompt this script cannot read is `null` with
   `prompt_source` saying WHY ("spec deleted", "pre-payload era"), never a
   recomputed approximation (the 77-token fit happened on the box tokenizer
   and recomputation can differ exactly where it matters);
 * filenames lie, fields don't — beat/task/node come from sidecar fields,
   never from the `b13-…` template vestiges in file names;
 * founder verdicts are never invented — the only "passed his look" this file
   will ever carry is a beat state copied from
   pipeline/measured/episode-progress.yaml, which itself only records his
   recorded words.

Usage:
    python3 pipeline/queue_history.py            # full rebuild
    python3 pipeline/queue_history.py --refresh  # append new jobs only
    python3 pipeline/queue_history.py --fetch    # git fetch the branch first
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))

BRANCH = "farm-results-rtx5090"
REMOTE_REF = f"origin/{BRANCH}"
OUT_FILE = REPO / "pipeline" / "measured" / "queue-history.json"
JOBS_DIR = REPO / "pipeline" / "jobs"
CANCELLED_DIR = JOBS_DIR / "cancelled-by-founder"

# What script ran → what kind of job it was. Classified from the sidecar's own
# steps[].argv (the runtime record), never from the file names it wrote.
KIND_BY_SCRIPT = {
    "ltx_i2v.py": "motion",
    "render_wave_sample.py": "still",
    "goblin_ipa_beat.py": "still-ipa",
    "goblin_ipa_sample.py": "still-ipa",
    "inpaint_fruit.py": "inpaint",
    "runpod_render.py": "still",
}

# A spec that says this, in text, is authored-but-deliberately-not-enqueued.
# There is no machine hold key for these (the `gate:` key exists but is a
# different, older mechanism), so the page states the hold from the words the
# author left, and only when no run record exists for the id.
HELD_RE = re.compile(r"PRE-AUTHORED|DO NOT ENQUEUE", re.I)

# How much planning prose rides along per job. The full text stays in the spec
# on main (linked from the page); the JSON carries enough to read the card.
PROSE_CAP = 500
# A line that has been superseded carries its replacement inline (see
# carry_correction), so it needs more room than an ordinary one — otherwise the
# correction is what gets clipped off the end and the stale half is all that
# ships. Only corrected lines ever use this.
CORRECTED_CAP = 2200

MEDIA_EXT = {".png": "image", ".jpg": "image", ".jpeg": "image",
             ".webp": "image", ".gif": "image", ".mp4": "video",
             ".webm": "video"}


# ---------------------------------------------------------------- pure logic
def classify_kind(steps) -> str:
    """Job kind from the scripts its steps ran. First recognised script wins;
    helper scripts (cover_crop.py, inline -c publishes) never classify."""
    for step in steps or []:
        for arg in step.get("argv") or []:
            base = str(arg).replace("\\", "/").rsplit("/", 1)[-1].lower()
            if base in KIND_BY_SCRIPT:
                return KIND_BY_SCRIPT[base]
    return "other"


def box_to_repo_path(p: str):
    """Map a box-absolute courier path to its repo-relative twin, or None.
    C:\\banyan-farm\\courier-box\\farm-out\\x\\y.png -> farm-out/x/y.png"""
    if not p:
        return None
    q = str(p).replace("\\", "/")
    marker = "courier-box/farm-out/"
    i = q.find(marker)
    if i >= 0:
        return "farm-out/" + q[i + len(marker):]
    return None


def safe_repo_path(p: str) -> bool:
    """Same law as the status page's safePath: only paths shaped like
    farm-out/... with no traversal ever reach a URL."""
    return bool(re.match(r"^farm-out/[\w.\-/]+$", p or "")) and ".." not in (p or "")


def first_sentence(text, cap=240) -> str:
    t = " ".join(str(text or "").split())
    if not t:
        return ""
    m = re.match(r"(.+?[.!?])(?:\s|$)", t)
    s = m.group(1) if m else t
    return s if len(s) <= cap else s[: cap - 1].rstrip() + "…"


def clip(text, cap=PROSE_CAP):
    t = " ".join(str(text).split()) if text is not None else None
    if not t:
        return None
    return t if len(t) <= cap else t[: cap - 1].rstrip() + "…"


def parse_duration_s(started_at, finished_at):
    try:
        a = datetime.datetime.fromisoformat(str(started_at).replace("Z", "+00:00"))
        b = datetime.datetime.fromisoformat(str(finished_at).replace("Z", "+00:00"))
        return max(0, int((b - a).total_seconds()))
    except (ValueError, TypeError):
        return None


def pubdir_map(branch_paths):
    """task id -> farm-out publish dir, recovered from the one mechanical link:
    every publish step writes `farm-out/<dir>/<task>.sha256`. The manifest's
    FILENAME carries the full task id even when the dir name is shortened."""
    out = {}
    for p in branch_paths:
        parts = p.split("/")
        if len(parts) == 3 and parts[0] == "farm-out" and parts[2].endswith(".sha256"):
            task = parts[2][: -len(".sha256")]
            out[task] = f"farm-out/{parts[1]}"
    return out


def sha_map_from_manifests(manifest_texts):
    """sha256 -> repo path, over every published manifest. Resolves 'which
    file has these bytes' questions (e.g. an IP-Adapter reference sha)."""
    out = {}
    for mpath, text in manifest_texts.items():
        d = mpath.rsplit("/", 1)[0]
        for line in (text or "").splitlines():
            bits = line.split()
            if len(bits) >= 2 and re.fullmatch(r"[0-9a-f]{64}", bits[0]):
                out.setdefault(bits[0], f"{d}/{bits[-1]}")
    return out


def motion_provenance(spec):
    """Prompt bytes for a motion job, from the spec's payload — the ONLY
    record in the encode/render-split era (the .mp4.meta.yaml stamps '')."""
    got = {"prompt": None, "negative": None, "seed": None,
           "init_src": None, "init_sha256": None,
           "prompt_source": "not recorded — spec missing or carries no payload"}
    if not spec:
        return got
    payload = spec.get("payload") or {}
    for key, val in payload.items():
        k = str(key).replace("\\", "/").lower()
        if k.endswith("-motion-prompt.txt"):
            got["prompt"] = str(val).strip()
        elif k.endswith("-negative.txt"):
            got["negative"] = str(val).strip()
        elif k.endswith("-render.json") or k.endswith("jobs-render.json"):
            try:
                jobs = json.loads(val)
                if jobs and isinstance(jobs, list):
                    got["seed"] = jobs[0].get("seed")
            except (ValueError, TypeError):
                pass
    for step in spec.get("steps") or []:
        argv = [str(a) for a in (step.get("argv") or [])]
        if step.get("name") == "crop" or any(a.endswith("cover_crop.py") for a in argv):
            if "--src" in argv:
                got["init_src"] = box_to_repo_path(argv[argv.index("--src") + 1])
            if "--sha256" in argv:
                got["init_sha256"] = argv[argv.index("--sha256") + 1]
    if got["prompt"] is not None:
        got["prompt_source"] = "spec payload (the exact bytes the encode step read)"
    return got


def still_provenance(art_yamls):
    """Prompt/recipe for a still job from its per-artifact render-time
    sidecars. Field VALUES are mechanical; sidecar prose is boilerplate and
    is deliberately not copied. One prompt per job (seeds vary, words don't)."""
    got = {"prompt": None, "negative": None, "seeds": [], "recipe": {},
           "reference": None,
           "prompt_source": "not recorded — no artifact sidecar on the branch"}
    ref = None
    for _name, y in sorted(art_yamls.items()):
        if not isinstance(y, dict):
            continue
        if got["prompt"] is None and y.get("prompt"):
            got["prompt"] = str(y["prompt"]).strip()
            got["negative"] = str(y.get("negative_prompt") or "").strip() or None
            got["prompt_source"] = "artifact sidecar (written at render time on the box)"
            r = got["recipe"]
            for k in ("model", "size", "steps", "guidance", "draft_variant",
                      "extra_negative_tier", "count_tag",
                      "negative_terms_removed", "render_seconds"):
                if y.get(k) is not None:
                    r[k] = y[k]
            if y.get("ip_adapter_reference"):
                ref = {"name": y["ip_adapter_reference"],
                       "sha256": y.get("ip_adapter_reference_sha256"),
                       "scale": y.get("ip_adapter_scale"),
                       "step_window": clip(y.get("ip_adapter_step_window"), 200)}
        if y.get("seed") is not None and y["seed"] not in got["seeds"]:
            got["seeds"].append(y["seed"])
    got["reference"] = ref
    return got


# ------------------------------------------------- the prompt fallback chain
#
# THE GAP THIS CLOSES, 2026-08-21 (founder: many Finished cards say "PROMPT NOT
# RECORDED" while the prompt is sitting in the committed spec). The two readers
# above each know exactly ONE place to look — `motion_provenance` reads payload
# keys ending `-motion-prompt.txt`, `still_provenance` reads the branch artifact
# sidecar's `prompt:` — and a job that keeps its prompt anywhere else fell
# through both. Measured over 1,187 rows: 440 showed no prompt, and 287 of those
# had the bytes in their own `pipeline/jobs/<id>.yaml` the whole time, under the
# plain `prompt.txt` payload key that 188 specs use. Every `inpaint_fruit.py`
# job and every `controlnet_plate.py` tilefix/tileread job is in that set.
#
# This is a JOIN, not a recomputation: the payload value IS the byte string the
# box wrote to disk and the render step read. The 77-token-fit warning in this
# file's header is about re-deriving what the box computed — reading back the
# exact bytes it was handed is the opposite of that.


def payload_base(key) -> str:
    """Basename of a payload key, which is a box-absolute Windows path."""
    return str(key).replace("\\", "/").rsplit("/", 1)[-1].lower()


def spec_prompt_bytes(spec):
    """(prompt, negative, key) — the prompt bytes a spec ships to the box.

    Preference order is the order a job's own recipe would read them: a motion
    prompt first (a motion spec that carries both is an encode/render pair and
    the motion file is the one the render step opens), then the plain
    `prompt.txt` that most still and inpaint specs use, then any other
    `*-prompt.txt`, then a top-level `prompt:` field. `key` names which one
    answered so the page can say where the words came from.
    """
    if not isinstance(spec, dict):
        return None, None, None
    payload = spec.get("payload") or {}
    prompt, key = None, None

    def take(pred):
        for k, v in payload.items():
            b = payload_base(k)
            if pred(b):
                text = str(v).strip()
                if text:
                    return text, b
        return None, None

    for pred in (lambda b: b.endswith("-motion-prompt.txt"),
                 lambda b: b == "prompt.txt",
                 lambda b: b.endswith("prompt.txt") and "negative" not in b):
        prompt, key = take(pred)
        if prompt:
            break
    if not prompt:
        for field in ("prompt", "positive_prompt"):
            if spec.get(field):
                prompt, key = str(spec[field]).strip(), field + ":"
                break

    negative, _ = take(lambda b: b == "negative.txt" or b.endswith("-negative.txt"))
    return prompt or None, negative or None, key


def sidecar_prompt_bytes(parsed_arts):
    """(prompt, negative, filename) from any published artifact sidecar.

    `still_provenance` already reads these for still-shaped jobs; this is the
    same read made available to the other kinds, and it is the last link in the
    chain rather than the first because a spec is committed and a branch file
    is not.
    """
    for path, y in sorted((parsed_arts or {}).items()):
        if not isinstance(y, dict):
            continue
        for field in ("prompt", "positive_prompt"):
            if y.get(field):
                neg = str(y.get("negative_prompt") or y.get("negative") or "").strip()
                return str(y[field]).strip(), neg or None, path.rsplit("/", 1)[-1]
    return None, None, None


def task_id_variants(task, job_id):
    """Ids to try against the spec index, most exact first.

    `task` is normally already the clean spec id and `id` is the same thing
    stamped `-<epoch>` by the runner, but not every era wrote both, and a few
    re-runs carry an `-again` token the spec file never had. Normalising costs
    nothing and a spec found is a prompt shown.
    """
    out = []
    for raw in (task, job_id):
        base = str(raw or "").strip()
        if not base:
            continue
        for cand in (base,
                     re.sub(r"-\d{10,13}$", "", base)):
            for final in (cand,
                          re.sub(r"-(?:again|retry|rerun)\d*(?=$|-)", "", cand)):
                if final and final not in out:
                    out.append(final)
    return out


# Scripts that assemble their prompt ON THE BOX from a selector key — a
# `--variant` / `--draft-key` / `--arm` index into a table living inside the
# harness copy that ran. There are no prompt bytes in the spec or on the branch
# to join to, so the page names the mechanism instead of implying a lost record.
HARNESS_SCRIPTS = {
    "render_wave_sample.py", "goblin_ipa_beat.py", "goblin_ipa_sample.py",
    "render_b06r6.py", "render_b06r7.py", "render_b06r8.py",
    "controlnet_probe.py",
}

# Scripts that only move, crop or stamp bytes. A job built entirely from these
# generated no pixels and never had a prompt — "NOT RECORDED" is not merely
# unhelpful there, it is wrong.
TRANSFER_SCRIPTS = {
    "fetch_init.py", "fetch_plate.py", "fetch_plates.py", "copy_plate.py",
    "cover_crop.py", "stamp_sidecar.py", "verify_embeds.py",
    "identity_agreement.py", "green_share.py",
}

SELECTOR_FLAGS = ("--draft-key", "--variant", "--arm")


def job_scripts(sc):
    """Basenames of every .py a run's steps invoked, from the runtime record."""
    out = set()
    for step in (sc or {}).get("steps") or []:
        for arg in step.get("argv") or []:
            b = str(arg).replace("\\", "/").rsplit("/", 1)[-1].lower()
            if b.endswith(".py"):
                out.add(b)
    return out


def job_selector(sc):
    """`--variant foo` / `--draft-key foo` / `--arm foo` as a printable phrase."""
    for step in (sc or {}).get("steps") or []:
        argv = [str(a) for a in (step.get("argv") or [])]
        for flag in SELECTOR_FLAGS:
            if flag in argv:
                i = argv.index(flag)
                if i + 1 < len(argv):
                    return f"{flag} {argv[i + 1]}"
    return None


def absent_prompt_label(sc, spec, had_spec):
    """An honest sentence for a job whose prompt is absent BY NATURE.

    Returns None when the absence is a genuine gap in the record — those keep
    saying so. The point is only to stop printing "PROMPT NOT RECORDED" over a
    file-transfer job, which never had one to record: a marker that cries wolf
    on 153 rows is a marker nobody reads on the rows that matter.
    """
    scripts = job_scripts(sc)
    harness = sorted(scripts & HARNESS_SCRIPTS)
    if harness:
        sel = job_selector(sc)
        return ("prompt built on the box by `%s`%s — it is assembled from that "
                "selector at render time, so no prompt text exists in the spec "
                "or on the results branch to quote here"
                % (harness[0], f" from `{sel}`" if sel else ""))
    if scripts and not (scripts - TRANSFER_SCRIPTS):
        return ("file-transfer job — no prompt: its steps only fetch, crop or "
                "stamp bytes (%s) and generate no pixels"
                % ", ".join(f"`{s}`" for s in sorted(scripts)))
    if not scripts:
        return ("file-transfer job — no prompt: this run generated nothing, its "
                "steps are inline publish/probe commands only")
    if had_spec:
        return None
    return None


def resolve_prompt(row, sc, spec, spec_rel, parsed_arts):
    """Fill `row`'s prompt from the first source that has it, and say which.

    Chain: whatever the per-kind reader already found (the render-time record)
    -> the committed job spec's payload -> a published artifact sidecar. Then,
    if all three are empty, an honest by-kind label for jobs that never had a
    prompt at all. `prompt_from` is the machine-readable answer to "which link
    filled this", so a later audit can count the joins without parsing prose.
    """
    if row.get("prompt"):
        row["prompt_from"] = "record"
        return

    prompt, negative, key = spec_prompt_bytes(spec)
    if prompt:
        row["prompt"] = prompt
        row["negative"] = row.get("negative") or negative
        row["prompt_from"] = "spec"
        row["prompt_source"] = (
            "job spec `%s`%s — the exact bytes the box was handed"
            % (spec_rel or "pipeline/jobs/…",
               f", payload `{key}`" if key else ""))
        return

    prompt, negative, name = sidecar_prompt_bytes(parsed_arts)
    if prompt:
        row["prompt"] = prompt
        row["negative"] = row.get("negative") or negative
        row["prompt_from"] = "sidecar"
        row["prompt_source"] = (
            "published artifact sidecar `%s` (written at render time on the box)"
            % name)
        return

    row["prompt_from"] = None
    label = absent_prompt_label(sc, spec, bool(spec))
    if label:
        row["prompt_absent"] = label
        row["prompt_source"] = label


def spec_state(raw_text, in_cancelled_dir):
    if in_cancelled_dir:
        return "cancelled-by-founder"
    if raw_text and (HELD_RE.search(raw_text) or
                     re.search(r"^gate:", raw_text, re.M)):
        return "held"
    return "authored"


def held_reason(spec):
    for field in ("why", "success"):
        t = str((spec or {}).get(field) or "")
        m = HELD_RE.search(t)
        if m:
            return first_sentence(t[m.start():], 300)
    return None


# ------------------------------------------------------------------ git I/O
def _git(*args, binary=False):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                       **({} if binary else
                          {"text": True, "encoding": "utf-8", "errors": "replace"}))
    if r.returncode != 0:
        err = r.stderr if not binary else r.stderr.decode("utf-8", "replace")
        raise SystemExit(f"!! git {' '.join(args)} failed:\n{err}")
    return r.stdout


def _no_lazy_fetch_works():
    """True if GIT_NO_LAZY_FETCH will actually be honoured by this git.

    It landed in git 2.42. On anything older the variable is IGNORED, and an
    ignored no-lazy-fetch in a partial clone is not a small regression — it
    turns one `cat-file --batch-check` over 11,784 oids into a 4.5 GB download,
    one blob at a time. So this is checked rather than assumed, and a partial
    clone under an old git simply declines to measure sizes.
    """
    try:
        parts = _git("version").split()[2].split(".")
        return (int(parts[0]), int(parts[1])) >= (2, 42)
    except (IndexError, ValueError, SystemExit):
        return False


def _is_partial_clone():
    r = subprocess.run(["git", "config", "--get", "remote.origin.promisor"],
                       cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return (r.stdout or "").strip() == "true"


def _blob_sizes(oids, lazy):
    """oid -> byte size, for the oids this repo can answer without guessing.

    `lazy=False` sets GIT_NO_LAZY_FETCH, which in a partial clone makes a blob
    the clone does not hold answer `missing` instead of silently downloading it.
    `lazy=True` lets git fetch it — one network round trip per object, ~1.9 s
    measured against GitHub, so the caller decides how many it is willing to pay
    for. An oid with no answer is absent from the map: never 0.
    """
    if not oids:
        return {}
    if not lazy and _is_partial_clone() and not _no_lazy_fetch_works():
        print("!! git < 2.42 in a partial clone: sizes cannot be read without "
              "risking a full blob download, so none are read")
        return {}
    env = dict(os.environ)
    if lazy:
        env.pop("GIT_NO_LAZY_FETCH", None)
    else:
        env["GIT_NO_LAZY_FETCH"] = "1"
    r = subprocess.run(["git", "cat-file", "--batch-check"], cwd=REPO, env=env,
                       input="\n".join(oids).encode() + b"\n", capture_output=True)
    sizes = {}
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == "blob":
            try:
                sizes[parts[0]] = int(parts[2])
            except ValueError:
                pass
    return sizes


# How many artifact sizes this is willing to pull over the network in one run.
# Nothing needs the bytes THEMSELVES — only the size — but git has no way to ask
# for a size alone, so an unknown size costs a whole blob (~1.9 s each, measured
# against GitHub). One box-hour is ~40 renders, so 400 covers a run that has
# fallen most of a day behind and still refuses to drag the 4.5 GB branch down.
SIZE_FETCH_CAP = 400

# path -> oid for the last branch listing, so the size top-up at the end of a run
# can look an artifact up without walking the tree a second time. Module state
# because this file is a script with one pass over one commit; branch_listing
# refills it, and nothing else writes it.
_OID_BY_PATH: dict[str, str] = {}


def branch_listing(commit, known=None):
    """[(path, size_bytes)] for everything under farm-out/ at the commit.

    Names and oids come from the tree; SIZES are a separate question, because
    this has to be correct in a PARTIAL clone as well as a full one. The hourly
    refresh workflow fetches the results branch with `--filter=blob:limit=128k`
    — every text sidecar, none of the 4.5 GB of PNGs and MP4s — and in that
    clone the obvious `ls-tree -l` does one of two wrong things: with lazy
    fetching on it downloads all 4.5 GB to print sizes, and with it off it
    reports every absent blob as `0`, which would put "0 KB" on 4,113 cards.
    Measured both, 2026-08-21.

    So: the tree gives paths and oids with no object lookup at all, then sizes
    come from what is local, then from `known` — the sizes the previous ledger
    already measured. Carrying those forward is sound because farm-out artifacts
    are write-once: a publish step stamps its directory with the task id, so a
    re-run writes a NEW directory rather than replacing a file, and a path that
    did change would change oid and be caught as absent rather than trusted.

    Anything still unsized after that is left as None here and topped up by
    `fill_missing_sizes` once the job rows exist — because only then is it known
    which artifacts a card will actually show. 704 blobs on this branch belong
    to no job at all (measured 2026-08-21), and paying a network round trip for
    each of those to publish nothing is how a cheap job becomes a slow one.
    """
    known = known or {}
    out = _git("ls-tree", "-r", "-z", "--full-tree",
               "--format=%(objectname) %(objecttype) %(path)", commit, "farm-out")
    entries = []
    for rec in out.split("\0"):
        if not rec:
            continue
        try:
            oid, otype, path = rec.split(" ", 2)
        except ValueError:
            continue
        if otype == "blob":
            entries.append((path, oid))

    _OID_BY_PATH.clear()
    _OID_BY_PATH.update(entries)
    sizes = _blob_sizes([o for _, o in entries], lazy=False)
    return [(p, sizes.get(o, known.get(p))) for p, o in entries]


def fill_missing_sizes(jobs, cap=SIZE_FETCH_CAP):
    """Measure the artifacts a card will show and whose size nothing knew yet.

    Runs after the rows are built, over the artifacts they actually reference,
    so the network cost is exactly the run's NEW output and not the whole
    branch. Returns how many it filled. In a full clone there is nothing to fill.
    """
    slots = []
    for job in jobs:
        for art in list(job.get("outputs") or []) + [job.get("init"),
                                                     job.get("reference")]:
            # `"bytes" in art` and not `.get("bytes") is None`: an init frame
            # carries a path and a sha256 and no size field at all, and adding
            # one here would change the shape of the record rather than fill it.
            if isinstance(art, dict) and art.get("path") \
                    and "bytes" in art and art["bytes"] is None:
                slots.append(art)
    paths = sorted({a["path"] for a in slots})
    if not paths:
        return 0
    if len(paths) > cap:
        print(f"!! {len(paths)} artifact sizes are not in this clone and "
              f"measuring them would exceed the {cap}-blob cap — those cards "
              f"show no KB rather than a wrong one")
        return 0
    oids = {p: _OID_BY_PATH[p] for p in paths if p in _OID_BY_PATH}
    sizes = _blob_sizes(sorted(set(oids.values())), lazy=True)
    filled = 0
    for art in slots:
        got = sizes.get(oids.get(art["path"], ""))
        if got is not None:
            art["bytes"] = got
            filled += 1
    if filled:
        print(f"   measured {filled} artifact size(s) this clone did not hold")
    return filled


def known_sizes(path):
    """path -> bytes, read back off a ledger this run is about to replace.

    Only the sizes. Everything else in that file is re-derived from the branch,
    and carrying more of it forward is how a rebuild starts preserving its own
    mistakes.
    """
    out = {}
    try:
        old = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return out
    for job in old.get("jobs") or []:
        if not isinstance(job, dict):
            continue
        for art in list(job.get("outputs") or []) + [job.get("init"),
                                                     job.get("reference")]:
            if isinstance(art, dict) and art.get("path") \
                    and isinstance(art.get("bytes"), int):
                out[str(art["path"])] = art["bytes"]
    return out


def read_blobs(commit, paths):
    """path -> decoded text, one `git cat-file --batch` round trip."""
    if not paths:
        return {}
    inp = "".join(f"{commit}:{p}\n" for p in paths).encode("utf-8")
    r = subprocess.run(["git", "cat-file", "--batch"], cwd=REPO,
                       input=inp, capture_output=True)
    if r.returncode != 0:
        raise SystemExit("!! git cat-file --batch failed:\n"
                         + r.stderr.decode("utf-8", "replace"))
    out, i, blobs = r.stdout, 0, {}
    order = list(paths)
    for path in order:
        nl = out.index(b"\n", i)
        header = out[i:nl].decode("utf-8", "replace")
        i = nl + 1
        if header.endswith((" missing", " ambiguous")):
            blobs[path] = None
            continue
        size = int(header.rsplit(" ", 1)[1])
        blobs[path] = out[i:i + size].decode("utf-8", "replace")
        i += size + 1  # trailing newline
    return blobs


# ----------------------------------------------------------------- assembly
def load_specs():
    """id -> (spec dict, repo-relative path, raw text, cancelled?). Indexed by
    the `id:` INSIDE each yaml — 15 of ~600 specs have id != filename stem, so
    the stem is not the key; on a duplicate id the exact-stem file wins."""
    import yaml
    index, skipped = {}, []
    for d, cancelled in ((JOBS_DIR, False), (CANCELLED_DIR, True)):
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.yaml")):
            raw = f.read_text(encoding="utf-8", errors="replace")
            try:
                spec = yaml.safe_load(raw)
            except yaml.YAMLError as e:
                skipped.append(f"{f.name}: {e.__class__.__name__}")
                continue
            if not isinstance(spec, dict):
                continue
            sid = str(spec.get("id") or spec.get("task") or f.stem)
            rel = str(f.relative_to(REPO))
            entry = (spec, rel, raw, cancelled)
            if sid in index and f.stem != sid:
                continue  # duplicate id: the exact-stem spec already won / will win
            index[sid] = entry
            index.setdefault(f.stem, entry)
    return index, skipped


_GATE_CORRECTION = re.compile(r"^gate_[A-Z][A-Z_0-9]*_\d{4}$")


def correction_keys(entry, field):
    """Dated `<field>[_SUBJECT]_MMDD` correction siblings of `field`, sorted.

    House style across gate-evidence.yaml, done-definitions.yaml,
    episode-progress.yaml and the job specs is one shape: a superseded line is
    NEVER erased, it is left standing and a dated sibling key is written beside
    it. The sibling is always `<field>_` + SHOUTING + `_MMDD`, so one matcher
    finds them for any field — `gate_CORRECTION_0816`, `state_CORRECTION_0816`,
    `success_CORRECTION_0816`, `guards_CORRECTION_0816`. Returns [] when the
    line has not been superseded, which is the common case.
    """
    if not isinstance(entry, dict):
        return []
    pat = re.compile(r"^%s_[A-Z][A-Z_0-9]*_\d{4}$" % re.escape(field))
    return sorted(k for k in entry if isinstance(k, str) and pat.match(k))


def carry_correction(entry, field, where, include_text=False):
    """`entry[field]`, marked SUPERSEDED and pointed at its dated sibling.

    `include_text=True` inlines the sibling's own words instead of only naming
    it. Use it where the reader needs the REPLACEMENT and not merely a warning
    — a success criterion is the bar someone judges against, so a pointer to
    another file is not enough; a gate is a yes/no and a pointer suffices.

    THE FAILURE THIS CLOSES, AND IT HAS NOW HAPPENED THREE TIMES IN ONE FILE.
    This reader copies authored yaml into queue-history.json, which /queue
    publishes. When the yaml is corrected in house style — old line left
    standing, dated sibling beside it — a reader that reads only the old key
    republishes the retracted text forever. Hand-editing the JSON is NOT the
    fix: `_meta.writer` says do not, and the next run puts the stale text
    straight back. The reader carries the correction instead.

    1. `gate` (2026-08-16): six rows saying "GATED - guard cast unapproved (his
       call)" outlived the founder lifting it ("the cast stands as drawn").
    2. `state` (2026-08-16, this audit): episode-progress.yaml was measured at
       2026-08-14 09:40Z and holds twelve goblin beats at `blocked-decision --
       goblin beat, character gate`. He opened that gate ninety minutes later,
       at 2026-08-14T11:09:07Z — "seed s0 is the goblin" — and all twelve have
       animated since. 248 job rows carried the dead block into the ledger, and
       beat 20's printed it beside `gate: "rendering now (2 jobs)"`, one record
       contradicting itself on one line.
    3. `consumer`/`why`/`success` (2026-08-16, same audit): the ALL-21 WAVE was
       authored by copying one spec, so 28 of its 32 specs carried BEAT 02's
       purpose prose verbatim — the recorded success bar for the beat-20 clip
       read "a goblin sprints in, skids and dives behind a sapling", which is
       beat 02's action, not beat 20's fig-and-look-up. Anyone judging those 28
       clips from the ledger was reading the wrong beat's bar.

    Nothing in the yaml is rewritten; the marker points at the key to read.
    """
    val = entry.get(field) if isinstance(entry, dict) else None
    if not val:
        return val
    corr = correction_keys(entry, field)
    if not corr:
        return val
    out = ("%s -- SUPERSEDED, do not act on it: see `%s` in %s"
           % (val, "`, `".join(corr), where))
    if include_text:
        out += " -- " + " ".join(str(entry[k]).strip() for k in corr)
    return out


def gate_text(beat_entry):
    """A beat's `gate:` string, carrying its dated correction if one exists.

    THE FAILURE THIS CLOSES, 2026-08-16. gate-evidence.yaml's house style — the
    same one done-definitions.yaml and steward-picks-0815.yaml use — is that a
    superseded line is NEVER erased: it is left standing and a dated
    `<key>_CORRECTION_MMDD` sibling is written beside it. This function used to
    read `gate` alone, so six rows saying "GATED - guard cast unapproved (his
    call)" were copied verbatim into queue-history.json and rendered on /queue
    (build_queue.py reads `det.verdict.gate`) — a block the founder lifted on
    2026-08-16 ("the cast stands as drawn"), still being published by the site.
    Hand-editing the JSON is not the fix: its own `_meta.writer` says do not,
    and the next run would put the stale text straight back. So the reader
    carries the correction forward instead, for any subject, not just guards.
    Nothing in the yaml is rewritten; the marker points at the key to read.
    """
    gate = beat_entry.get("gate")
    if not gate:
        return gate
    corr = sorted(k for k in beat_entry
                  if isinstance(k, str) and _GATE_CORRECTION.match(k))
    if not corr:
        return gate
    return ("%s -- SUPERSEDED, do not act on it: see `%s` in "
            "review/ep2-picks/gate-evidence.yaml"
            % (gate, "`, `".join(corr)))


def load_verdicts():
    """(node,beat) -> beat state/note; beat -> gate; beat -> pick. Missing
    files are stated, not guessed."""
    import yaml
    notes = []
    beat_state, gates, picks = {}, {}, {}
    ep = REPO / "pipeline" / "measured" / "episode-progress.yaml"
    try:
        d = yaml.safe_load(ep.read_text(encoding="utf-8"))
        for e in d.get("episodes") or []:
            for b in e.get("beats") or []:
                beat_state[(e.get("node"), int(b["n"]))] = {
                    "state": carry_correction(
                        b, "state",
                        "pipeline/measured/episode-progress.yaml"),
                    "note": clip(b.get("note"), 300)}
    except (OSError, yaml.YAMLError, KeyError, TypeError, ValueError) as e:
        notes.append(f"episode-progress unreadable: {e.__class__.__name__}")
    ge = REPO / "review" / "ep2-picks" / "gate-evidence.yaml"
    try:
        d = yaml.safe_load(ge.read_text(encoding="utf-8"))
        for b in d.get("beats") or []:
            gates[int(b["beat"])] = gate_text(b)
    except (OSError, yaml.YAMLError, KeyError, TypeError, ValueError) as e:
        notes.append(f"gate-evidence unreadable: {e.__class__.__name__}")
    dd = REPO / "review" / "ep2-picks" / "done-definitions.yaml"
    try:
        d = yaml.safe_load(dd.read_text(encoding="utf-8"))
        for k, v in (d.get("beats") or {}).items():
            if isinstance(v, dict) and v.get("pick"):
                picks[int(k)] = str(v["pick"])
    except (OSError, yaml.YAMLError, KeyError, TypeError, ValueError) as e:
        notes.append(f"done-definitions unreadable: {e.__class__.__name__}")
    return beat_state, gates, picks, notes


# ------------------------------------------------- what the clip is FOR
# The founder's ask, 2026-08-21, verbatim: "in the queue history it should also
# show what the clip is supposed to express, like what part of the story it is,
# it helps alot." A card that says `beat 13` names a slot in a list; it does not
# say that a goblin whose legs have gone sits down in a tree's shade and thanks
# it. Everything below is READ from the tree — the beat's own stage direction and
# spoken line out of node.md, the bar out of done-definitions.yaml — and nothing
# is composed. A job shape this cannot place gets NO story key at all, because a
# guessed story on a render page is worse than a blank one.

NODES_DIR = REPO / "genomes" / "sapling" / "nodes"
LINEAGE_FILE = REPO / "genomes" / "sapling" / "lineage.yaml"
# Per-episode "what has to be visible" bars, where a shipping lane wrote them.
DONE_DEFS = {2: REPO / "review" / "ep2-picks" / "done-definitions.yaml"}

# **THE SHADE — 1:00–1:04**  → a beat header. The em dash and the timecode are
# both required: `**Format:**` and the restage notes are bold too.
_BEAT_HEAD = re.compile(r"^\*\*\s*([^*]+?)\s+—\s+\d+:\d\d–\d+:\d\d\s*\*\*\s*$")
# > **SCAVENGER:** …Thanks for the shade.
_SPEECH = re.compile(r"^>\s*\*\*([^*:]+?)\s*:?\*\*:?\s*(.*)$")

_STORY_CACHE: dict = {}

# Card-sized. The detail pane gets the whole thing.
STORY_CARD_CAP = 150
# Below this a lone first sentence is not a story moment — beat 06 of episode 1
# opens "Blinding green blur." and beat 01 of episode 3 opens "Dawn." Keep
# taking sentences until the line actually says something.
STORY_MIN_USEFUL = 60


def story_short(text, cap=STORY_CARD_CAP):
    """One card line: whole sentences up to `cap`, never a bare fragment."""
    t = " ".join(str(text or "").split())
    if not t:
        return None
    if len(t) <= cap:
        return t
    out = ""
    for part in re.findall(r".+?(?:[.!?](?:\s|$)|$)", t):
        if out and len(out) + len(part) > cap:
            break
        out += part
        if len(out.strip()) >= STORY_MIN_USEFUL:
            break
    out = out.strip()
    if not out or len(out) > cap:
        # One long sentence and no clause boundary inside the cap. Cut on a WORD
        # boundary — "hand-sized pat…" is a typo the reader has to decode.
        head = t[: cap - 1]
        out = (head.rsplit(" ", 1)[0] or head).rstrip(" ,;—-") + "…"
    return out


def _strip_md(text) -> str:
    """Markdown out, words in. Struck text (`~~old~~`) is REMOVED rather than
    unwrapped — a retired stage direction lives on beside its replacement in
    these files and must not read as what the clip shows."""
    t = re.sub(r"~~.*?~~", "", str(text or ""), flags=re.S)
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"\*(.+?)\*", r"\1", t, flags=re.S)
    t = t.replace("`", "")
    return " ".join(t.split())


def parse_node_script(path):
    """node.md → [{n, title, action, speaker, line}], one entry per beat, in
    script order. `n` is 1-based because that is how the whole tree — job ids,
    done-definitions, the founder — counts beats."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return []
    beats, cur = [], None
    for raw in text.splitlines():
        head = _BEAT_HEAD.match(raw.strip())
        if head:
            cur = {"n": len(beats) + 1, "title": _strip_md(head.group(1)).title(),
                   "action": "", "speaker": None, "line": None}
            beats.append(cur)
            continue
        if cur is None:
            continue
        line = raw.strip()
        if not line:
            continue
        sp = _SPEECH.match(line)
        if sp:
            if cur["line"] is None:
                who = _strip_md(sp.group(1))
                said = _strip_md(sp.group(2))
                if said:
                    cur["speaker"], cur["line"] = who, said
            continue
        if line.startswith((">", "#", "```", "|", "---")):
            continue
        if not cur["action"]:
            # The first prose paragraph after the header IS the stage
            # direction. Later italic paragraphs are restage provenance notes,
            # which belong in the record and not on a card.
            body = _strip_md(line)
            if body:
                cur["action"] = body
    return beats


def trunk_episodes():
    """episode number → node slug, from lineage.yaml's trunk in file order.
    Hardcoding {2: '002b-first-citizen'} would be a second place to update the
    day the trunk moves; the tree already states its own spine."""
    import yaml
    try:
        d = yaml.safe_load(LINEAGE_FILE.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}
    out, n = {}, 0
    for node in d.get("nodes") or []:
        if node.get("trunk") and node.get("slug"):
            n += 1
            out[n] = str(node["slug"])
    return out


def _node_slug(node_id):
    """'002b' → '002b-first-citizen'. Exact directory prefix only."""
    if not node_id:
        return None
    for p in sorted(NODES_DIR.glob(f"{node_id}-*")):
        if p.is_dir():
            return p.name
    return None


def _episode_of(slug):
    for ep, s in trunk_episodes().items():
        if s == slug:
            return ep
    return None


def _script(slug):
    if slug not in _STORY_CACHE:
        _STORY_CACHE[slug] = parse_node_script(NODES_DIR / slug / "node.md")
    return _STORY_CACHE[slug]


_DONE_CACHE: dict = {}


def _done_when(ep, beat):
    """The shipping lane's bar for this beat, if one was written. This is the
    most literal answer to 'what is the clip supposed to show' we own, because
    somebody wrote it to judge clips against."""
    if ep not in DONE_DEFS:
        return None
    if ep not in _DONE_CACHE:
        import yaml
        try:
            d = yaml.safe_load(DONE_DEFS[ep].read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            d = {}
        _DONE_CACHE[ep] = {int(k): v for k, v in (d.get("beats") or {}).items()
                           if str(k).isdigit() and isinstance(v, dict)}
    entry = _DONE_CACHE[ep].get(int(beat))
    return clip(entry.get("done_when"), 400) if entry else None


# Jobs that are not a beat and never were. Each entry is (pattern, what, why) and
# the label says both — "not a story beat" is the load-bearing half, because a
# goblin face sheet sitting in a grid of beats reads as a beat unless the card
# says otherwise. First match wins, so the specific rows come first.
SUPPORT_JOBS = [
    (r"jerry|goblin",
     "Character design work — the goblin",
     "Not a story beat. These build the reference pictures of him that the "
     "real shots are drawn from, so he looks like the same creature twice."),
    (r"charref-guards?|guards?-(?:[a-z0-9]+-)?(?:sheet|derived)",
     "Character design work — the two patrol guards",
     "Not a story beat. Reference pictures of the guards, so the pair look "
     "like the same two men in every shot they appear in."),
    (r"charref-assessor",
     "Character design work — the assessor",
     "Not a story beat. Reference pictures of a character from a later "
     "episode, drawn ahead of the shots that need him."),
    (r"charref-farmer",
     "Character design work — the farmer",
     "Not a story beat. Reference pictures of a character from a later "
     "episode, drawn ahead of the shots that need him."),
    (r"charref-magistrate",
     "Character design work — the magistrate",
     "Not a story beat. Reference pictures of a character from a later "
     "episode, drawn ahead of the shots that need him."),
    (r"sapfield|sapfld|saplora|sapling-(reference|dataset|lora)",
     "Sapling dataset — episode 3 prep",
     "Not a story beat. Pictures of the sapling in many places, sizes and "
     "lights, collected to teach the model to draw it the same way every time."),
    (r"bark-plates?",
     "Prop work — the guards' bark clipboard",
     "Not a story beat. A picture of the prop itself, so the shots that use "
     "it start from something that already looks right."),
    (r"ipa-\w*-fetch|preflight|autofill|heartbeat|probe|poscontrol|"
     r"nohumans|clip-measure",
     "Pipeline test — no story in it",
     "Not a story beat. A check on the machinery itself: does the box pick "
     "the job up, does the model load, how fast does it run."),
]
SUPPORT_JOBS = [(re.compile(p, re.I), what, why) for p, what, why in SUPPORT_JOBS]

# ep2-b13-…, 001-b06-…, ep3-003b-b01-…, ep2-b0708-twofig-… (one job, two beats).
_BEAT_IN_TASK = re.compile(r"(?:^|[-_])(?:(\d{3}[a-z]?)-)?b(\d{2})(\d{2})?(?![0-9])",
                           re.I)
_EP_IN_TASK = re.compile(r"(?:^|[-_])ep(\d+)(?![0-9])", re.I)


def story_context(task, node=None):
    """What part of the story this job is, in plain words — or None.

    Reads the BEAT OUT OF THE JOB ID, never out of the sidecar's `beat` field:
    the box stamps non-beat work with whatever beat the spec was copied from
    (`ep3-sapfld2-r04-0821`, a LoRA dataset cell, is filed under beat 16), and a
    dataset tile captioned "Beat 16 — WHY" is a lie told confidently.
    """
    task = str(task or "")
    if not task:
        return None

    m = _BEAT_IN_TASK.search(task)
    if m:
        slug = _node_slug(m.group(1)) if m.group(1) else None
        ep = _episode_of(slug) if slug else None
        if slug is None:
            epm = _EP_IN_TASK.search(task)
            if epm:
                ep = int(epm.group(1))
                slug = trunk_episodes().get(ep)
        if slug is None and node:
            slug, ep = str(node), _episode_of(str(node))
        beats = [int(m.group(2))] + ([int(m.group(3))] if m.group(3) else [])
        script = _script(slug) if slug else []
        found = [b for b in script if b["n"] in beats]
        if found:
            first = found[0]
            nums = " and ".join(f"{b['n']:02d}" for b in found)
            titles = " / ".join(b["title"] for b in found)
            expresses = _done_when(ep, first["n"])
            out = {
                "kind": "beat",
                "episode": ep,
                "beat": first["n"],
                "beats": beats if len(beats) > 1 else None,
                "label": f"Beat{'s' if len(found) > 1 else ''} {nums} — {titles}",
                "moment": first["action"] or None,
                "moment_short": story_short(first["action"]),
                "line": first["line"],
                "speaker": first["speaker"],
                "expresses": expresses,
                "expresses_short": story_short(expresses),
            }
            return {k: v for k, v in out.items() if v not in (None, "", [])}
        # The id names a beat this episode's script does not have. Say the
        # number and stop — no invented moment.
        if beats:
            return {"kind": "beat", "beat": beats[0], "episode": ep,
                    "label": f"Beat {beats[0]:02d}",
                    "moment": None,
                    "why": "the script on main has no beat by this number"}

    for pat, what, why in SUPPORT_JOBS:
        if pat.search(task):
            return {"kind": "support", "label": what, "moment": why}
    return None


def attach_story(rows):
    """Stamp every row — refreshed and freshly read alike, which is why this is
    a pass over the finished list and not a line inside build_job_row."""
    for row in rows:
        st = story_context(row.get("task") or row.get("id"), row.get("node"))
        if st:
            row["story"] = st
        else:
            row.pop("story", None)
    return rows


def build_job_row(sidecar_path, sc, specs, pubdirs, files_by_dir, blobs, shamap,
                  beat_state, gates, picks):
    task = sc.get("task") or sc.get("id")
    kind = classify_kind(sc.get("steps"))
    spec, spec_rel = None, None
    # Most exact id first. The runner stamps `id` as `<task>-<epoch>` and a few
    # eras wrote only one of the two, so a plain `specs[task]` lost the spec —
    # and with it the prompt — for 68 motion rows whose file was on main all
    # along (measured 2026-08-21).
    for cand in task_id_variants(task, sc.get("id")):
        hit = specs.get(cand)
        if hit:
            spec, spec_rel = hit[0], hit[1]
            break

    row = {
        "id": sc.get("id"), "task": task, "node": sc.get("node"),
        "beat": sc.get("beat"), "kind": kind,
        "rc": sc.get("rc"), "failed_step": sc.get("failed_step"),
        "attempts": sc.get("attempts"), "runner_host": sc.get("runner_host"),
        "started_at": sc.get("started_at"), "finished_at": sc.get("finished_at"),
        "duration_s": parse_duration_s(sc.get("started_at"), sc.get("finished_at")),
        "sidecar": sidecar_path, "spec_file": spec_rel,
    }
    if spec:
        # `include_text=True`: a success line is the bar a clip gets judged
        # against, so the replacement has to travel WITH the row. See
        # carry_correction() failure 3 — 28 wave rows published beat 02's bar.
        # PROSE_CAP still governs an uncorrected line; a corrected one gets the
        # room its replacement needs, because a bar clipped mid-sentence is the
        # same defect in a politer form.
        row["purpose"] = {}
        for k in ("consumer", "why", "success", "owner"):
            if not spec.get(k):
                continue
            corrected = carry_correction(spec, k, spec_rel, include_text=True)
            cap = PROSE_CAP if corrected == spec.get(k) else CORRECTED_CAP
            row["purpose"][k] = clip(corrected, cap)
        for k in ("est_minutes", "priority"):
            if spec.get(k) is not None:
                row["purpose"][k] = spec[k]
    else:
        row["purpose"] = None
        row["purpose_note"] = ("no spec on main for this task — deleted or "
                               "pre-box-queue; see git history of pipeline/jobs/")

    # outputs, from the publish dir the sha256 manifest names
    pubdir = pubdirs.get(str(task))
    row["artifacts_dir"] = pubdir
    outputs, art_yamls, meta_yaml = [], {}, None
    if pubdir:
        for path, size in files_by_dir.get(pubdir, []):
            name = path.rsplit("/", 1)[-1]
            ext = ("." + name.rsplit(".", 1)[-1].lower()) if "." in name else ""
            if ext in MEDIA_EXT and safe_repo_path(path):
                outputs.append({"path": path, "name": name, "bytes": size,
                                "kind": MEDIA_EXT[ext]})
            elif name.endswith(".meta.yaml"):
                meta_yaml = blobs.get(path)
            elif name.endswith(".yaml"):
                art_yamls[path] = blobs.get(path)
    row["outputs"] = outputs

    import yaml
    parsed_arts = {}
    for p, text in art_yamls.items():
        try:
            parsed_arts[p] = yaml.safe_load(text) if text else None
        except yaml.YAMLError:
            parsed_arts[p] = None

    if kind == "motion":
        mp = motion_provenance(spec)
        row["prompt"], row["negative"] = mp["prompt"], mp["negative"]
        row["prompt_source"] = mp["prompt_source"]
        recipe = {}
        for step in sc.get("steps") or []:
            argv = [str(a) for a in (step.get("argv") or [])]
            if any(a.endswith("ltx_i2v.py") for a in argv) and "--stage" in argv \
                    and argv[argv.index("--stage") + 1] == "render":
                for flag in ("--size", "--frames", "--fps", "--guidance", "--mode"):
                    if flag in argv:
                        recipe[flag.lstrip("-")] = argv[argv.index(flag) + 1]
        if meta_yaml:
            try:
                m = yaml.safe_load(meta_yaml) or {}
                for k in ("model", "steps", "seed", "seconds"):
                    if m.get(k) is not None:
                        recipe[k] = m[k]
            except yaml.YAMLError:
                pass
        if mp["seed"] is not None:
            recipe.setdefault("seed", mp["seed"])
        row["recipe"] = recipe or None
        if mp["init_src"]:
            row["init"] = {"path": mp["init_src"] if safe_repo_path(mp["init_src"]) else None,
                           "sha256": mp["init_sha256"]}
        row["reference"] = None
    else:
        sp = still_provenance(parsed_arts)
        row["prompt"], row["negative"] = sp["prompt"], sp["negative"]
        row["prompt_source"] = sp["prompt_source"]
        recipe = dict(sp["recipe"])
        if sp["seeds"]:
            recipe["seeds"] = sp["seeds"]
        row["recipe"] = recipe or None
        row["init"] = None
        ref = sp["reference"]
        if ref:
            ref["path"] = shamap.get(ref.get("sha256"))
            if not ref["path"]:
                ref["note"] = ("reference bytes live on the box only; the sha is "
                               "recorded here and the parent frame is ledgered in "
                               "taste/steward-model.ledger.yaml")
        row["reference"] = ref

    # Whatever the per-kind reader above could not find, the chain tries for:
    # the committed spec first, then a published sidecar, then an honest label.
    resolve_prompt(row, sc, spec, spec_rel, parsed_arts)

    v = {}
    bs = beat_state.get((row["node"], row["beat"]))
    if bs:
        v["beat_state"], v["beat_note"] = bs["state"], bs["note"]
    if row["node"] == "002b-first-citizen" and row["beat"] in gates:
        v["gate"] = gates[row["beat"]]
    if row["beat"] in picks and picks[row["beat"]] == str(task):
        v["picked"] = True
    row["verdict"] = v or None
    return row


def heartbeat_tasks(text):
    """Task ids the heartbeat has ever seen start or finish — the only run
    trace for pre-sidecar outputs. Ids come stamped `<task>-<epoch>`."""
    out = set()
    for jid in re.findall(r"task=([\w.\-]+)", text or ""):
        out.add(jid)
        out.add(re.sub(r"-\d{10}$", "", jid))
    return out


def spec_commit_dates():
    """spec repo-relative path -> unix time of its last commit, one git call.
    Lets the page separate a live hold from an old spec nobody deleted."""
    out, ct = {}, None
    log = _git("log", "--format=COMMIT:%ct", "--name-only", "--", "pipeline/jobs")
    for line in log.splitlines():
        if line.startswith("COMMIT:"):
            ct = int(line.split(":", 1)[1])
        elif line.strip():
            out.setdefault(line.strip(), ct)
    return out


def build_upcoming(specs, done_tasks, authored_at=None):
    """Specs with no run record anywhere (no sidecar, no published dir, no
    heartbeat line): authored / held / cancelled. Live 'queued on the box
    right now' is the page's telemetry overlay, not this file — ready ids are
    never published (pipeline/box_enqueue.py keeps planning fields repo-side
    on purpose)."""
    seen, rows = set(), []
    for sid, (spec, rel, raw, cancelled) in specs.items():
        if rel in seen:
            continue
        seen.add(rel)
        real_id = str(spec.get("id") or spec.get("task") or sid)
        if real_id in done_tasks or str(spec.get("task") or "") in done_tasks:
            continue
        state = spec_state(raw, cancelled)
        rows.append({
            "id": real_id, "node": spec.get("node"), "beat": spec.get("beat"),
            "kind": classify_kind(spec.get("steps")), "state": state,
            "priority": spec.get("priority"), "est_minutes": spec.get("est_minutes"),
            "consumer": clip(spec.get("consumer"), 300),
            "why_first": first_sentence(spec.get("why")),
            "hold_reason": held_reason(spec) if state == "held" else None,
            "spec_file": rel,
            "authored_at": (authored_at or {}).get(rel),
        })
    rows.sort(key=lambda r: (r["state"] != "held",
                             -(r["authored_at"] or 0),
                             r["priority"] if r["priority"] is not None else 999,
                             r["id"]))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--refresh", action="store_true",
                    help="keep rows already extracted; only read new sidecars")
    ap.add_argument("--fetch", action="store_true",
                    help=f"git fetch origin {BRANCH} first")
    ap.add_argument("--out", default=str(OUT_FILE))
    a = ap.parse_args(argv)

    if a.fetch:
        _git("fetch", "origin", BRANCH)
    commit = _git("rev-parse", REMOTE_REF).strip()

    # The ledger about to be overwritten is also the cheapest source of artifact
    # sizes this run already paid for — see branch_listing's docstring.
    files = branch_listing(commit, known_sizes(a.out))
    all_paths = [p for p, _ in files]
    files_by_dir = {}
    for p, size in files:
        files_by_dir.setdefault(p.rsplit("/", 1)[0], []).append((p, size))

    sidecar_paths = sorted(p for p in all_paths
                           if p.startswith("farm-out/box/") and p.endswith(".json"))
    pubdirs = pubdir_map(all_paths)

    prev_jobs = {}
    if a.refresh and Path(a.out).exists():
        old = json.loads(Path(a.out).read_text(encoding="utf-8"))
        prev_jobs = {j["sidecar"]: j for j in old.get("jobs", [])
                     if j.get("sidecar") in set(all_paths)}
    new_sidecars = [p for p in sidecar_paths if p not in prev_jobs]

    # one batched blob read: new sidecars + every published yaml/manifest
    want = list(new_sidecars)
    manifest_paths = [p for p in all_paths
                      if p.endswith(".sha256") and not p.startswith("farm-out/box/")]
    yaml_paths = [p for p in all_paths
                  if p.endswith(".yaml") and not p.startswith("farm-out/box/")]
    blobs = read_blobs(commit, want + manifest_paths + yaml_paths)
    shamap = sha_map_from_manifests({p: blobs.get(p) for p in manifest_paths})

    specs, spec_skipped = load_specs()
    beat_state, gates, picks, verdict_notes = load_verdicts()

    jobs, parse_skipped = list(prev_jobs.values()), []
    for p in new_sidecars:
        try:
            sc = json.loads(blobs.get(p) or "")
        except (ValueError, TypeError):
            parse_skipped.append(p)
            continue
        jobs.append(build_job_row(p, sc, specs, pubdirs, files_by_dir, blobs,
                                  shamap, beat_state, gates, picks))
    jobs.sort(key=lambda j: str(j.get("finished_at") or j.get("started_at") or ""),
              reverse=True)
    fill_missing_sizes(jobs)

    # A spec is 'upcoming' only if NOTHING has run under its id: no box
    # sidecar, no published farm-out dir, no heartbeat STARTED/DONE line
    # (the last two are the only traces of the pre-sidecar era).
    done_tasks = {str(j["task"]) for j in jobs}
    done_tasks |= set(pubdirs.keys())
    hb = read_blobs(commit, ["farm-out/heartbeat.txt"]).get("farm-out/heartbeat.txt")
    done_tasks |= heartbeat_tasks(hb)
    upcoming = build_upcoming(specs, done_tasks, spec_commit_dates())
    attach_story(jobs)
    attach_story(upcoming)

    ok = sum(1 for j in jobs if j.get("rc") == 0)
    doc = {
        "_meta": {
            "writer": "pipeline/queue_history.py — do not hand-edit; re-run it "
                      "(then commit) when you want /queue's history to move",
            "source_branch": BRANCH,
            "source_commit": commit,
            "measured_at": datetime.datetime.now(datetime.timezone.utc)
                           .strftime("%Y-%m-%dT%H:%M:%SZ"),
            "job_count": len(jobs), "ok": ok, "failed": len(jobs) - ok,
            "upcoming_count": len(upcoming),
            "skipped_sidecars": parse_skipped or None,
            "skipped_specs": spec_skipped or None,
            "verdict_notes": verdict_notes or None,
        },
        "jobs": jobs,
        "upcoming": upcoming,
    }
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    kb = out.stat().st_size // 1024
    print(f"✓ {out.relative_to(REPO) if out.is_relative_to(REPO) else out} — "
          f"{len(jobs)} jobs ({ok} ok, {len(jobs) - ok} failed), "
          f"{len(upcoming)} upcoming, {kb} KB, source {commit[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
