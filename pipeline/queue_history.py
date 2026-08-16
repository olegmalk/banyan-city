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


def branch_listing(commit):
    """[(path, size_bytes)] for everything under farm-out/ at the commit."""
    out = _git("ls-tree", "-r", "-l", "--full-tree", commit, "farm-out")
    files = []
    for line in out.splitlines():
        try:
            meta, path = line.split("\t", 1)
            size = meta.split()[3]
            files.append((path, None if size == "-" else int(size)))
        except (ValueError, IndexError):
            continue
    return files


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


def build_job_row(sidecar_path, sc, specs, pubdirs, files_by_dir, blobs, shamap,
                  beat_state, gates, picks):
    task = sc.get("task") or sc.get("id")
    kind = classify_kind(sc.get("steps"))
    spec, spec_rel = None, None
    hit = specs.get(str(task))
    if hit:
        spec, spec_rel = hit[0], hit[1]

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

    files = branch_listing(commit)
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

    # A spec is 'upcoming' only if NOTHING has run under its id: no box
    # sidecar, no published farm-out dir, no heartbeat STARTED/DONE line
    # (the last two are the only traces of the pre-sidecar era).
    done_tasks = {str(j["task"]) for j in jobs}
    done_tasks |= set(pubdirs.keys())
    hb = read_blobs(commit, ["farm-out/heartbeat.txt"]).get("farm-out/heartbeat.txt")
    done_tasks |= heartbeat_tasks(hb)
    upcoming = build_upcoming(specs, done_tasks, spec_commit_dates())

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
