#!/usr/bin/env python3
"""birdseye.py — read-only bird-eye view of the whole production.

Scans the repo (story tree, VO manifests, every *.meta.yaml render sidecar,
job specs, farm-out courier dirs, queue history, grades, spend ledger, plus
the farm-results branch listing) and emits ONE self-contained page:

    _birdseye/index.html          (untracked output dir; regenerate = rerun)

The heart is the CLIP VIEW: one card per render task / clip, expandable to a
full dossier — node+beat+script text, VO lines, prompt (labeled with which
era source supplied it), model/seed/settings, init plate + refs, files on
disk with sha256 where manifested, grade data, queue-history rows, cost rows.

Honesty is a feature: whatever could NOT be resolved (orphan clips, missing
sidecars, beat-number conflicts, compound task fields) is SHOWN in the data
health box, never hidden.

No server, no network, no writes outside _birdseye/. stdlib + pyyaml only.
"""

from __future__ import annotations

import csv
import html as html_mod
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

try:
    _Loader = yaml.CSafeLoader
except AttributeError:  # no libyaml build
    _Loader = yaml.SafeLoader

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "_birdseye"
FARM_BRANCH = "origin/farm-results-rtx5090"

MEDIA_EXTS = {".mp4", ".mov", ".webm", ".png", ".jpg", ".jpeg", ".gif",
              ".mp3", ".wav", ".m4a", ".aac", ".ogg"}
VIDEO_EXTS = {".mp4", ".mov", ".webm"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".ogg"}

SKIP_DIRS = {".git", "_birdseye", "_site", "node_modules", ".venv", "venv",
             "__pycache__", ".claude", ".github"}

EP_NODE_MAP = {"ep1": "001-capability-inventory", "ep2": "002b-first-citizen"}

health: dict[str, list] = {
    "unparsable_yaml": [],       # files pyyaml refused (fallback used)
    "orphan_sidecars": [],       # sidecar with no media file on disk
    "orphan_clips": [],          # mp4 with no sidecar anywhere
    "beat_conflicts": [],        # card ids where beat sources disagree
    "compound_tasks": [],        # sidecar task: fields holding 2+ task ids
    "tasks_missing_spec": [],    # task referenced, no pipeline/jobs/<task>.yaml
    "ship_pick_missing": [],     # ship-manifest take not on disk in sources/
    "node_unresolved": [],       # cards with no node
    "orphan_vo": [],             # NN-vo.json beyond the script's beat count
    "branch_only_tasks": [],     # farm-out task manifest only on the farm branch
    "retired_era_clips": [],     # slug-named clips made for a RETIRED script era
}


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def loose_yaml(path: Path):
    """yaml.safe_load with a line-based fallback for files pyyaml refuses.

    Fallback captures top-level `key: value` scalars and block scalars
    (| / |- / > / >-) — enough for every sidecar dialect's flat fields."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    try:
        d = yaml.load(text, Loader=_Loader)
        if isinstance(d, dict):
            return d
        # a scalar/None/other top level is useless — fall through to fallback
    except Exception:
        pass
    health["unparsable_yaml"].append(rel(path))
    out: dict = {}
    lines = text.splitlines()
    i = 0
    key_re = re.compile(r"^([A-Za-z_][\w .()/-]*):\s*(.*)$")
    while i < len(lines):
        m = key_re.match(lines[i])
        if m:
            k, v = m.group(1), m.group(2).strip()
            if v in ("|", "|-", ">", ">-", "|+", ">+"):
                block, i = [], i + 1
                while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                    block.append(lines[i].strip())
                    i += 1
                out[k] = " ".join(x for x in block if x)
                continue
            out[k] = v.strip("'\"")
        i += 1
    return out


# ---------------------------------------------------------------- story side

def load_lineage():
    d = loose_yaml(ROOT / "genomes/sapling/lineage.yaml") or {}
    nodes = {}
    for n in d.get("nodes", []):
        nodes[n["slug"]] = {
            "id": str(n.get("id")), "slug": n["slug"], "title": n.get("title", ""),
            "parent": (str(n["parent"]) if n.get("parent") else None),
            "trunk": bool(n.get("trunk")), "status": n.get("status", "?"),
            "released": str(n.get("released", "")),
        }
    return nodes


BEAT_RANGE = re.compile(r"\d+:\d+\s*[–—-]\s*\d+:\d+")


def parse_node_beats(md: str):
    """Port of render_t1.parse_frames' beat rule: inside '## Script', every
    full-bold line carrying a time range is a beat (bold WITHOUT a range is
    emphasis). Struck-through ~~lines~~ (retired staging) are excluded."""
    m = re.search(r"^## Script\s*\n(.*?)(?=^## |^---\s*$|\Z)", md, re.M | re.S)
    if not m:
        return []
    beats, current = [], None
    for line in m.group(1).splitlines():
        s = line.strip()
        head = re.match(r"^\*\*(.+?)\*\*\s*$", s)
        if head and BEAT_RANGE.search(head.group(1)):
            inner = head.group(1)
            tm = re.search(r"[—–-]\s*(\d+:\d+\s*[–—-]\s*\d+:\d+)\s*$", inner)
            rng = tm.group(1) if tm else ""
            title = inner[: tm.start()].strip() if tm else inner
            current = {"n": len(beats) + 1, "title": title, "range": rng, "text": []}
            beats.append(current)
        elif current is not None:
            if s.startswith("~~") and s.endswith("~~") and len(s) > 4:
                continue  # struck-through staging — retired, not current
            current["text"].append(line.rstrip())
    for b in beats:
        b["text"] = "\n".join(b["text"]).strip()
    return beats


def parse_shots(md: str):
    """shots.md '## Beat NN — TITLE (range) status' headings + first fenced
    block = the authored per-beat prompt registry."""
    out = {}
    blocks = re.split(r"^## Beat ", md, flags=re.M)[1:]
    for blk in blocks:
        head, _, body = blk.partition("\n")
        m = re.match(r"^(\d+)\s*[—–-]+\s*(.+?)\s*\(([^)]*)\)\s*(.*)$", head.strip())
        if not m:
            continue
        n = int(m.group(1))
        fence = re.search(r"```[^\n]*\n(.*?)```", body, re.S)
        out[n] = {"title": m.group(2), "status": m.group(4).strip(),
                  "prompt": fence.group(1).strip() if fence else ""}
    return out


def load_story(lineage):
    story = {}
    for slug, meta in lineage.items():
        nd = ROOT / "genomes/sapling/nodes" / slug
        entry = dict(meta)
        entry["beats"] = []
        entry["vo"] = {}
        entry["shots"] = {}
        node_md = nd / "node.md"
        if node_md.exists():
            entry["beats"] = parse_node_beats(node_md.read_text(encoding="utf-8", errors="replace"))
        shots_md = nd / "shots.md"
        if shots_md.exists():
            entry["shots"] = parse_shots(shots_md.read_text(encoding="utf-8", errors="replace"))
        clips = nd / "clips"
        if clips.is_dir():
            for f in sorted(clips.glob("[0-9][0-9]-vo.json")):
                try:
                    v = json.loads(f.read_text(encoding="utf-8", errors="replace"))
                except Exception:
                    health["unparsable_yaml"].append(rel(f))
                    continue
                n = int(f.name[:2])
                entry["vo"][n] = {
                    "engine": v.get("engine", "?"), "total_s": v.get("total_s"),
                    "lines": [[ln.get("who", "?"), ln.get("text", "")] for ln in v.get("lines", [])],
                    "path": rel(f),
                }
                if entry["beats"] and n > len(entry["beats"]):
                    health["orphan_vo"].append(f"{rel(f)} (beat {n} > script's {len(entry['beats'])} beats)")
        story[slug] = entry
    return story


# ---------------------------------------------------------------- disk scan

def walk_repo():
    sidecars, still_yamls, grades, manifests = [], [], [], []
    media = {}  # relpath -> bytes
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith("C:")]
        dp = Path(dirpath)
        in_farmout = "farm-out" in dp.relative_to(ROOT).parts[:1] if dp != ROOT else False
        for fn in filenames:
            p = dp / fn
            if fn.endswith(".meta.yaml"):
                sidecars.append(p)
            elif fn.endswith(".grade.json"):
                grades.append(p)
            elif fn.endswith(".sha256") and in_farmout:
                manifests.append(p)
            elif fn.endswith(".yaml") and in_farmout:
                still_yamls.append(p)
            else:
                ext = os.path.splitext(fn)[1].lower()
                if ext in MEDIA_EXTS:
                    try:
                        media[rel(p)] = p.stat().st_size
                    except OSError:
                        pass
    return sidecars, still_yamls, grades, manifests, media


TASK_TOKEN = re.compile(r"^[A-Za-z0-9][\w.-]*$")

# sidecar keys already consumed into dedicated card fields (or redundant with
# them) — everything else scalar flows into card["extras"] verbatim
CONSUMED_SIDECAR_KEYS = {
    "task", "model", "platform", "seed", "steps", "size", "guidance",
    "seconds", "duration_s", "prompt", "positive", "negative",
    "negative_prompt", "line", "shot_beat", "source_still", "node", "beat",
    "kind"}


def split_tasks(value):
    """A sidecar task: field is usually one id, but compound forms exist:
    'ep2-b12-tightB-0813 (source) + ep2-b12-b21-trim-0821 (this edit)'."""
    if not value or not isinstance(value, str):
        return []
    parts = [re.sub(r"\s*\([^)]*\)\s*$", "", p.strip()) for p in value.split(" + ")]
    return [p for p in parts if p and TASK_TOKEN.match(p)]


def sidecar_media(sc: Path):
    """Resolve a sidecar to its media file: '<file>.meta.yaml' (new) or
    '<stem>.meta.yaml' (old — try known media extensions)."""
    base = sc.with_name(sc.name[: -len(".meta.yaml")])
    if base.suffix.lower() in MEDIA_EXTS and base.exists():
        return base
    for ext in (".mp4", ".png", ".mp3", ".jpg", ".wav", ".webm", ".gif"):
        cand = base.with_name(base.name + ext)
        if cand.exists():
            return cand
    return None


def beat_from_task(task):
    m = re.search(r"-b(\d{1,2})(?:g\d)?(?=-|$)", task or "")
    return int(m.group(1)) if m else None


def beat_from_filename(name):
    m = re.match(r"^(\d{2})-", name or "")
    if m:
        return int(m.group(1))
    m = re.match(r"^beat-(\d{2})-", name or "")
    return int(m.group(1)) if m else None


def slug_key(s: str) -> str:
    """render_t3.slug_key — normalize a slug/title for the era cross-check."""
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


# NN-<story-slug>[-altK].<video ext> — the clip-naming grammar the slug guard
# covers. Take-named files (task ids, dates, UPPERCASE engine tags) are NOT
# story slugs and are excluded by the [a-z-] restriction.
RETIRED_SLUG = re.compile(r"^(\d{2})-([a-z][a-z-]*?)(?:-alt\d+)?\.(?:mp4|mov|webm)$")


def retired_era_slug(basename, beat, title):
    """Port of render_t3.footage_matches_beat's 10-char slug cross-check:
    footage is found by beat NUMBER, and a script rewrite renumbers beats —
    a clip whose filename slug does not match the CURRENT beat title was made
    for a retired script era. Returns the mismatching slug, or None."""
    m = RETIRED_SLUG.match(basename)
    if not m or int(m.group(1)) != beat:
        return None
    made_for = slug_key(m.group(2))
    now = slug_key(str(title).split("—")[0])
    if not made_for or not now:
        return None
    if made_for.startswith(now[:10]) or now.startswith(made_for[:10]):
        return None
    return m.group(2)


def classify_era(model, kind, platform):
    s = f"{model or ''} {platform or ''}".lower()
    if "ltx" in s:
        return "LTX motion"
    if "animagine" in s or "sdxl" in s or kind in ("still", "still-ipa", "inpaint"):
        return "SDXL still"
    if "wan2" in s or "alibaba" in s:
        return "wan (paid era)"
    if "chatterbox" in s or "kokoro" in s:
        return "VO"
    if model and str(model).startswith("none"):
        return "held-still"
    if kind == "motion":
        return "LTX motion"
    return "other"


def main():
    t0 = time.time()
    lineage = load_lineage()
    story = load_story(lineage)
    short2slug = {v["id"]: slug for slug, v in lineage.items()}

    sidecar_paths, still_yaml_paths, grade_paths, manifest_paths, media = walk_repo()

    # --- sha256 manifests: task -> farm-out dir; (dir, fname) -> sha
    task_dir, sha_of = {}, {}
    for mp in manifest_paths:
        task = mp.name[: -len(".sha256")]
        d = rel(mp.parent)
        task_dir[task] = d
        try:
            for line in mp.read_text(encoding="utf-8", errors="replace").splitlines():
                parts = line.split(None, 1)
                if len(parts) == 2:
                    sha_of[(d, parts[1].strip())] = parts[0]
        except OSError:
            pass

    # --- farm branch: dirs + files that exist only there
    branch_files_by_dir: dict[str, list[str]] = {}
    branch_task_dir = {}
    try:
        out = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", FARM_BRANCH, "farm-out/"],
            cwd=ROOT, capture_output=True, text=True, timeout=120)
        if out.returncode != 0:
            health.setdefault("notes", []).append(
                f"git ls-tree {FARM_BRANCH} failed (rc={out.returncode}): "
                f"{(out.stderr or '').strip()[:200]} — branch-only farm data unavailable")
        for line in out.stdout.splitlines():
            parts = line.split("/")
            if len(parts) < 3 or parts[1] == "box":
                continue  # farm-out/box/*.json = queue sidecars, summarized by queue-history
            d = "/".join(parts[:-1])
            branch_files_by_dir.setdefault(d, []).append(parts[-1])
            if parts[-1].endswith(".sha256"):
                branch_task_dir[parts[-1][: -len(".sha256")]] = d
    except Exception as e:
        health.setdefault("notes", []).append(f"git ls-tree {FARM_BRANCH} failed: {e}")

    # true DIRECTORY counts for the totals tile (manifest counts are a
    # different fact: some dirs carry no .sha256 manifest at all)
    farm_root = ROOT / "farm-out"
    local_farm_dirs = ({rel(p) for p in farm_root.iterdir() if p.is_dir()}
                       if farm_root.is_dir() else set())
    branch_only_dirs = {d for d in branch_files_by_dir if not (ROOT / d).is_dir()}
    for task, d in branch_task_dir.items():
        if not (ROOT / d).is_dir():
            health["branch_only_tasks"].append(task)

    # branch-only .sha256 manifests: fetch their contents in ONE git cat-file
    # --batch (no checkout) so branch-only file rows can show real hashes
    want = [f"{d}/{t}.sha256" for t, d in branch_task_dir.items()
            if not (ROOT / d / (t + ".sha256")).exists()]
    if want:
        try:
            out = subprocess.run(
                ["git", "cat-file", "--batch"], cwd=ROOT, timeout=120,
                input="".join(f"{FARM_BRANCH}:{p}\n" for p in want).encode(),
                capture_output=True)
            buf, i = out.stdout, 0
            for wp in want:
                nl = buf.find(b"\n", i)
                if nl < 0:
                    break
                header = buf[i:nl].decode(errors="replace")
                i = nl + 1
                if header.endswith(" missing") or len(header.split()) != 3:
                    continue
                size = int(header.rsplit(" ", 1)[1])
                content = buf[i:i + size].decode("utf-8", "replace")
                i += size + 1
                d = os.path.dirname(wp)
                for line in content.splitlines():
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        sha_of[(d, parts[1].strip())] = parts[0]
        except Exception as e:
            health.setdefault("notes", []).append(f"git cat-file --batch failed: {e}")

    # --- queue history (measured file preferred; _site copy is an older bake;
    # a corrupt file falls through to the next candidate, then to empty+note)
    queue_by_task: dict[str, list] = {}
    queue_meta, upcoming = {}, []
    qh = None
    for qh_path in (ROOT / "pipeline/measured/queue-history.json",
                    ROOT / "_site/queue-data.json"):
        if not qh_path.exists():
            continue
        try:
            qh = json.loads(qh_path.read_text(encoding="utf-8", errors="replace"))
            break
        except (json.JSONDecodeError, ValueError, OSError) as e:
            health.setdefault("notes", []).append(
                f"queue history {rel(qh_path)} unreadable ({e}) — trying next source")
            qh = None
    if isinstance(qh, dict):
        queue_meta = qh.get("_meta", {})
        queue_meta["_file"] = rel(qh_path)
        upcoming = qh.get("upcoming", [])
        for row in qh.get("jobs", []):
            task = row.get("task") or re.sub(r"-\d{10,13}$", "", row.get("id", ""))
            queue_by_task.setdefault(task, []).append(row)
    else:
        health.setdefault("notes", []).append(
            "queue history unavailable (no readable source) — queue data empty")

    # --- sidecars
    sidecar_recs = []
    for sc in sidecar_paths:
        d = loose_yaml(sc)
        if d is None:
            continue
        mediaf = sidecar_media(sc)
        if mediaf is None:
            health["orphan_sidecars"].append(rel(sc))
        tasks = split_tasks(d.get("task"))
        if len(tasks) > 1:
            health["compound_tasks"].append(f"{rel(sc)}: {d.get('task')}")
        sidecar_recs.append({"path": rel(sc), "media": rel(mediaf) if mediaf else None,
                             "tasks": tasks, "fields": d})

    # --- farm-out still .yaml sidecars (per-png prompt records)
    still_meta = {}  # media relpath -> fields
    for sy in still_yaml_paths:
        if sy.name.endswith(".sha256") or sy.name.endswith(".meta.yaml"):
            continue
        png = sy.with_suffix(".png")
        if not png.exists():
            continue
        d = loose_yaml(sy)
        if isinstance(d, dict) and ("prompt" in d or "positive" in d):
            still_meta[rel(png)] = {"path": rel(sy), "fields": d}

    # --- job specs (all of them: beat/node authority + never-ran count)
    specs = {}
    jobs_dir = ROOT / "pipeline/jobs"
    for jf in sorted(list(jobs_dir.glob("*.yaml"))
                     + list((jobs_dir / "cancelled-by-founder").glob("*.yaml"))):
        d = loose_yaml(jf)
        if not isinstance(d, dict):
            continue
        prompt = negative = seed = None
        payload = d.get("payload") if isinstance(d.get("payload"), dict) else {}
        for k, v in payload.items():
            if not isinstance(k, str) or not isinstance(v, str):
                continue
            if k.endswith("-motion-prompt.txt"):
                prompt = v.strip()
            elif k.endswith("-negative.txt"):
                negative = v.strip()
            elif k.endswith("-jobs-render.json"):
                m = re.search(r'"seed"\s*:\s*(\d+)', v)
                if m:
                    seed = int(m.group(1))
        init = None
        for st in (d.get("steps") or []):
            argv = st.get("argv") if isinstance(st, dict) else None
            if argv and "--src" in argv:
                try:
                    init = {"src": str(argv[argv.index("--src") + 1])}
                    if "--sha256" in argv:
                        init["sha256"] = str(argv[argv.index("--sha256") + 1])
                except Exception:
                    pass
        ip = d.get("init_provenance")
        plate = d.get("plate_provenance")
        deriv = d.get("derivation") or {}
        specs[jf.stem] = {
            "file": rel(jf), "node": d.get("node"),
            "cancelled": jf.parent.name == "cancelled-by-founder",
            "beat": d.get("beat") if isinstance(d.get("beat"), int) else None,
            "prompt": prompt, "negative": negative, "seed": seed,
            "sample": bool(d.get("sample")), "priority": d.get("priority"),
            "success": str(d.get("success") or d.get("bar") or "")[:500],
            "consumer": str(d.get("consumer") or "")[:300],
            "why": str(d.get("why") or "")[:300],
            "init": init,
            "init_provenance": (json.dumps(ip)[:400] if isinstance(ip, (dict, list)) else (str(ip)[:400] if ip else None)),
            "plate_provenance": (str(plate)[:400] if plate else None),
            "derived_from": (deriv.get("parent") if isinstance(deriv, dict) else None),
            "script_line": str(d.get("script_line") or "")[:300],
        }

    # --- grades (plate grades, ep2 finish pass)
    grades_by_beat: dict[int, list] = {}
    for gp in grade_paths:
        try:
            g = json.loads(gp.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            health["unparsable_yaml"].append(rel(gp))
            continue
        tag = gp.name.split("-graded")[0]
        m = re.match(r"^b(\d{1,2})", tag)
        beat = int(m.group(1)) if m else None
        png = gp.with_name(gp.name[: -len(".grade.json")]) if gp.name.endswith(".grade.json") else None
        rec = {"tag": tag, "file": rel(gp),
               "png": (rel(png) if png and png.exists() else None),
               "station": g.get("station"),
               "plate": g.get("plate"), "out_sha256": (g.get("out_sha256") or "")[:16],
               "hue_drift_deg": g.get("hue_drift_deg"), "ink_lift": g.get("ink_lift"),
               "before": g.get("before"), "after": g.get("after"),
               "knobs": g.get("knobs"), "tool": g.get("tool")}
        if beat is not None:
            grades_by_beat.setdefault(beat, []).append(rec)

    # --- ship manifest (final ep2 cut picks)
    ship = {}
    smp = ROOT / "review/ep2-ship-0821/sources/ship-manifest.yaml"
    if smp.exists():
        sm = loose_yaml(smp) or {}
        for row in sm.get("beats", []) or []:
            if not isinstance(row, dict):
                continue
            take = row.get("take") or row.get("clip")
            on_disk = bool(take) and (smp.parent / str(take)).exists()
            ship[row.get("beat")] = {
                "take": take, "sha256": (row.get("sha256") or "")[:16],
                "verdict": str(row.get("verdict") or ""), "on_disk": on_disk}
            if take and not on_disk:
                health["ship_pick_missing"].append(
                    f"beat {row.get('beat')}: {take} (named in ship-manifest, not in sources/)")

    # --- spend ledger (tolerant: unquoted commas in note produce >7 columns)
    ledger_rows, spend_total = [], 0.0
    lp = ROOT / "ledger/render-spend.csv"
    if lp.exists():
        with open(lp, newline="", encoding="utf-8", errors="replace") as fh:
            rdr = csv.reader(fh)
            hdr = next(rdr, None)
            for r in rdr:
                if len(r) < 6:
                    continue
                if len(r) > 7:
                    r = r[:6] + [",".join(r[6:])]
                date, node, beat, provider, model, est, note = (r + [""])[:7]
                try:
                    usd = float(est)
                except ValueError:
                    usd = 0.0
                spend_total += usd
                ledger_rows.append({"date": date, "node": node, "beat": beat,
                                    "provider": provider, "model": model,
                                    "usd": usd, "note": note})

    # ------------------------------------------------------------- cards
    cards = {}

    def get_card(key):
        return cards.setdefault(key, {
            "id": key, "task": None, "tasks": [], "node": None, "node_src": None,
            "beat": None, "beat_src": None, "beat_conflicts": [],
            "era": "other", "kind": None, "model": None, "platform": None,
            "seed": None, "steps": None, "size": None, "guidance": None,
            "seconds": None, "prompt": None, "prompt_src": None, "negative": None,
            "init": None, "refs": [], "files": [], "queue": [], "sidecars": [],
            "spec": None, "spec_info": None, "shipped": False, "support": None,
            "verdict": None, "problems": [], "cost": [], "extras": {},
            "retired_era": None})

    def add_file(card, path, where="local"):
        if any(f["p"] == path for f in card["files"]):
            return
        size = media.get(path)
        d, fn = os.path.split(path)
        ext = os.path.splitext(fn)[1].lower()
        kind = ("video" if ext in VIDEO_EXTS else "image" if ext in IMAGE_EXTS
                else "audio" if ext in AUDIO_EXTS else "file")
        card["files"].append({"p": path, "bytes": size, "sha": sha_of.get((d, fn)),
                              "where": where, "kind": kind})

    # 1) queue history — one card per task
    for task, rows in queue_by_task.items():
        c = get_card(task)
        c["task"] = task
        c["tasks"] = [task]
        rows.sort(key=lambda r: r.get("finished_at") or "")
        for r in rows:
            c["queue"].append({
                "id": r.get("id"), "rc": r.get("rc"), "step": r.get("failed_step"),
                "attempts": r.get("attempts"), "host": r.get("runner_host"),
                "start": r.get("started_at"), "dur": r.get("duration_s"),
                "kind": r.get("kind")})
        best = next((r for r in reversed(rows) if r.get("rc") == 0), rows[-1])
        c["kind"] = best.get("kind")
        c["node"], c["node_src"] = best.get("node"), "queue-history"
        if isinstance(best.get("beat"), int):
            c["beat"], c["beat_src"] = best["beat"], "queue-history row"
        rec = best.get("recipe") or {}
        c["model"] = rec.get("model")
        c["seed"] = rec.get("seed")
        c["steps"] = rec.get("steps")
        c["size"] = rec.get("size")
        c["guidance"] = rec.get("guidance")
        c["seconds"] = rec.get("seconds")
        if best.get("prompt"):
            c["prompt"] = best["prompt"]
            c["prompt_src"] = f"queue-history ({best.get('prompt_from') or best.get('prompt_source') or 'record'})"
        c["negative"] = best.get("negative")
        if best.get("init"):
            c["init"] = best["init"]
        if best.get("reference"):
            c["refs"].append(best["reference"])
        if best.get("verdict"):
            v = best["verdict"]
            # verdict notes render VERBATIM, never summarized (house rule)
            c["verdict"] = {"state": v.get("beat_state"), "note": str(v.get("beat_note") or ""),
                            "picked": v.get("picked")}
        st = best.get("story") or {}
        if st.get("kind") == "support":
            c["support"] = st.get("label") or "support work — not a story beat"
        c["_spec_files"] = [sf for sf in dict.fromkeys(
            r.get("spec_file") for r in reversed(rows)) if sf]
        for o in best.get("outputs") or []:
            p = o.get("path")
            if p:
                add_file(c, p, "local" if p in media else "on farm branch, not local")

    # 2) sidecars — enrich task cards, or standalone cards for taskless files
    for sr in sidecar_recs:
        f = sr["fields"]
        key = sr["tasks"][0] if sr["tasks"] else (("file:" + sr["media"]) if sr["media"] else ("sidecar:" + sr["path"]))
        c = get_card(key)
        if sr["tasks"]:
            c["task"] = c["task"] or sr["tasks"][0]
            for t in sr["tasks"]:
                if t not in c["tasks"]:
                    c["tasks"].append(t)
        c["sidecars"].append(sr["path"])
        if sr["media"]:
            add_file(c, sr["media"])
        c["model"] = c["model"] or f.get("model")
        c["platform"] = c["platform"] or f.get("platform")
        for k_src, k_dst in (("seed", "seed"), ("steps", "steps"), ("size", "size"),
                             ("guidance", "guidance"), ("seconds", "seconds"),
                             ("duration_s", "seconds")):
            if c[k_dst] is None and f.get(k_src) is not None:
                c[k_dst] = f.get(k_src)
        # prompt precedence: inline sidecar prompt (old eras) wins over queue copy
        p = f.get("prompt") or f.get("positive")
        if isinstance(p, str) and p.strip() and "none —" not in p[:30]:
            c["prompt"] = p.strip()
            c["prompt_src"] = "sidecar (inline — pre-farm era)" if not sr["tasks"] else "sidecar (inline)"
            neg = f.get("negative") or f.get("negative_prompt")
            if isinstance(neg, str) and neg.strip():
                c["negative"] = neg.strip()
        if f.get("line") and not c["prompt"]:
            c["prompt"] = None  # VO sidecars carry the script line, not a prompt
        if f.get("shot_beat") is not None:
            try:
                c.setdefault("_shot_beat", int(f.get("shot_beat")))
            except (TypeError, ValueError):
                pass
        if f.get("source_still"):
            c["init"] = c["init"] or {"path": str(f["source_still"]), "note": "held still source"}
        # every other scalar the sidecar records (zoom, line_note, recorded,
        # model_licence, cast, …) passes through to the settings table —
        # dropping fields silently is how the HELD-variant zoom went missing
        for k, v in f.items():
            if (k not in CONSUMED_SIDECAR_KEYS and k not in c["extras"]
                    and isinstance(v, (str, int, float, bool))):
                c["extras"][k] = (v.strip()[:600] if isinstance(v, str) else v)

    # 3) farm-out dirs: attach files (local via manifest map, branch-only listed)
    def resolve_task_card(task):
        """Find the card a dir/manifest name belongs to. A courier dir often
        lacks the task id's date suffix (ep1-b07-385f-cloudshigh vs …-0811) —
        merging on the '-' boundary prevents split-brain duplicate cards."""
        c = cards.get(task)
        if c is not None:
            return c
        hits = [cc for cc in cards.values() if cc["task"]
                and (task.startswith(cc["task"] + "-") or cc["task"].startswith(task + "-"))]
        if hits:
            hits.sort(key=lambda cc: (not cc["queue"], cc["id"]))
            return hits[0]
        return None

    for task, d in task_dir.items():
        c = resolve_task_card(task)
        if c is None:
            c = get_card(task)
            c["task"] = task
            c["tasks"] = [task]
        dd = ROOT / d
        if dd.is_dir():
            for f in sorted(dd.iterdir()):
                if f.suffix.lower() in MEDIA_EXTS:
                    add_file(c, rel(f))
    # local farm-out dirs WITHOUT a .sha256 manifest still hold real artifacts
    # (e.g. ep2-finish-graded-0822's graded pngs) — card their media too
    manifested_dirs = set(task_dir.values())
    if farm_root.is_dir():
        for dd in sorted(farm_root.iterdir()):
            if not dd.is_dir() or rel(dd) in manifested_dirs:
                continue
            mfiles = [f for f in sorted(dd.iterdir()) if f.suffix.lower() in MEDIA_EXTS]
            if not mfiles:
                continue
            c = resolve_task_card(dd.name)
            if c is None:
                c = get_card("dir:" + rel(dd))
            for f in mfiles:
                add_file(c, rel(f))
    for task in health["branch_only_tasks"]:
        c = resolve_task_card(task)
        if c is None:
            c = get_card(task)
            c["task"] = task
            c["tasks"] = [task]
        d = branch_task_dir[task]
        for fn in branch_files_by_dir.get(d, []):
            if os.path.splitext(fn)[1].lower() in MEDIA_EXTS:
                add_file(c, f"{d}/{fn}", "on farm branch, not local")

    # 4) still .yaml prompt records join by file already on a card. Runs
    #    AFTER the farm-out dir attach on purpose: pngs carded only via the
    #    manifest/dir walk (step 3) would otherwise miss their prompt records.
    file_card = {}
    for c in cards.values():
        for fl in c["files"]:
            file_card[fl["p"]] = c
    for png, srec in still_meta.items():
        c = file_card.get(png)
        if c is None:
            continue
        f = srec["fields"]
        if not c["prompt"]:
            p = f.get("prompt") or f.get("positive")
            if isinstance(p, str) and p.strip():
                c["prompt"] = p.strip()
                c["prompt_src"] = f"still sidecar ({srec['path'].split('/')[-1]})"
                neg = f.get("negative_prompt") or f.get("negative")
                if isinstance(neg, str):
                    c["negative"] = c["negative"] or neg.strip()
        if f.get("ip_adapter_reference"):
            c["refs"].append({"name": str(f.get("ip_adapter_reference")),
                              "scale": f.get("ip_adapter_scale") or f.get("ip_adapter_reference_scale")})

    # 5) spec join + node/beat resolution with the precedence rule
    specs_by_file = {sp["file"]: sp for sp in specs.values()}
    specs_by_base = {os.path.basename(sp["file"]): sp for sp in specs.values()}
    for c in cards.values():
        for t in c["tasks"]:
            sp = specs.get(t)
            if sp:
                c["spec"] = sp["file"]
                c["spec_info"] = sp
                break
        if c["spec_info"] is None:
            # queue-history names the spec VERBATIM in jobs[].spec_file —
            # the task id often carries a suffix the spec basename lacks
            for sf in c.pop("_spec_files", []):
                sp = specs_by_file.get(sf) or specs_by_base.get(os.path.basename(sf))
                if sp:
                    c["spec"] = sp["file"]
                    c["spec_info"] = sp
                    break
        if c["spec_info"] is None and c["tasks"]:
            health["tasks_missing_spec"].append(c["tasks"][0])
        sp = c["spec_info"]
        if sp and sp.get("cancelled"):
            c["problems"].append("spec lives in cancelled-by-founder/")
        # node: spec > queue > path containment > ep-prefix (inferred)
        if sp and sp.get("node"):
            c["node"], c["node_src"] = sp["node"], "job spec node:"
        if not c["node"]:
            for fl in c["files"] + [{"p": s} for s in c["sidecars"]]:
                m = re.match(r"genomes/sapling/nodes/([^/]+)/", fl["p"])
                if m:
                    c["node"], c["node_src"] = m.group(1), "path (genomes node dir)"
                    break
        if not c["node"] and c["task"]:
            ep = c["task"].split("-")[0]
            if ep in EP_NODE_MAP:
                c["node"], c["node_src"] = EP_NODE_MAP[ep], f"inferred from '{ep}' task prefix"
        if not c["node"]:
            for fl in c["files"]:
                p = fl["p"]
                m = re.search(r"(^|/)(ep[12])[-_]", p)
                if m:
                    c["node"], c["node_src"] = EP_NODE_MAP[m.group(2)], f"inferred from '{m.group(2)}' in path"
                    break
                if p.startswith("review/beat-"):  # old ep1 take grammar at review root
                    c["node"], c["node_src"] = EP_NODE_MAP["ep1"], "inferred from review/beat-NN grammar (ep1 era)"
                    break
        if not c["node"] and not c.get("support"):
            # a support job (charref/LoRA/probe) has no story node BY DESIGN;
            # anything else nodeless is a genuine unresolved link
            c["problems"].append("node unresolved")
        # beat precedence: spec beat: > queue row > bNN in task > NN- filename > shot_beat
        candidates = []
        if sp and sp.get("beat") is not None:
            candidates.append(("job spec beat:", sp["beat"]))
        if c["beat"] is not None:
            candidates.append((c["beat_src"] or "queue-history row", c["beat"]))
        for t in c["tasks"]:
            b = beat_from_task(t)
            if b is not None:
                candidates.append((f"bNN in task id ({t})", b))
                break
        for fl in c["files"]:
            b = beat_from_filename(os.path.basename(fl["p"]))
            if b is not None:
                candidates.append(("NN- filename prefix", b))
                break
        if "_shot_beat" in c:
            candidates.append(("sidecar shot_beat:", c.pop("_shot_beat")))
        if candidates:
            c["beat_src"], c["beat"] = candidates[0]
            distinct = sorted({v for _, v in candidates})
            if len(distinct) > 1:
                c["beat_conflicts"] = [f"{src} = {v}" for src, v in candidates]
                c["problems"].append("beat-number conflict (precedence applied: " + c["beat_src"] + ")")
                health["beat_conflicts"].append(f"{c['id']}: " + "; ".join(c["beat_conflicts"]))
        # prompt fallback: spec payload
        if not c["prompt"] and sp and sp.get("prompt"):
            c["prompt"] = sp["prompt"]
            c["prompt_src"] = "job spec payload (*-motion-prompt.txt)"
            c["negative"] = c["negative"] or sp.get("negative")
        if c["seed"] is None and sp and sp.get("seed") is not None:
            c["seed"] = sp["seed"]
        if not c["init"] and sp and sp.get("init"):
            c["init"] = sp["init"]

    # 6) orphan mp4s (no sidecar, not on any card) -> thin cards.
    #    Tier leaves (leaves/00X-tN-x.mp4) carry provenance in a sibling
    #    <stem>.yaml leaf file — those are NOT orphans.
    carded_files = set(file_card)
    for c in cards.values():
        carded_files.update(f["p"] for f in c["files"])
    for p in sorted(media):
        # repo-wide on purpose: scoping this to a dir allowlist silently hid
        # 59 orphan takes (pipeline/measured/judge-*, repo-root cuts/probes)
        if not p.endswith(".mp4") or p in carded_files:
            continue
        c = get_card("file:" + p)
        add_file(c, p)
        leaf_yaml = ROOT / (p[:-4] + ".yaml")
        if "/leaves/" in p and leaf_yaml.exists():
            lf = loose_yaml(leaf_yaml) or {}
            c["kind"] = f"tier leaf ({lf.get('tier', '?')})"
            c["model"] = lf.get("model")
            c["prompt"] = (str(lf.get("prompt")) if lf.get("prompt") not in (None, "none") else None)
            if c["prompt"]:
                c["prompt_src"] = f"leaf yaml ({os.path.basename(str(leaf_yaml))})"
            c["sidecars"].append(rel(leaf_yaml))
        else:
            health["orphan_clips"].append(p)
            c["problems"].append("no sidecar — provenance unrecorded")
        b = beat_from_filename(os.path.basename(p))
        if b is not None:
            c["beat"], c["beat_src"] = b, "NN- filename prefix (no sidecar!)"
        m = re.match(r"genomes/sapling/nodes/([^/]+)/", p)
        if m:
            c["node"], c["node_src"] = m.group(1), "path (genomes node dir)"
        elif re.search(r"(^|/)ep2[-_]", p):
            c["node"], c["node_src"] = EP_NODE_MAP["ep2"], "inferred from 'ep2' in path"
        elif re.search(r"(^|/)ep1[-_]", p) or p.startswith("review/beat-"):
            c["node"], c["node_src"] = EP_NODE_MAP["ep1"], "inferred from path"
        else:
            c["problems"].append("node unresolved")

    # 7) finishing touches per card
    take_index = {(v["take"], k) for k, v in ship.items() if v.get("take")}
    for c in cards.values():
        if not c["node"] and not c["support"]:
            health["node_unresolved"].append(c["id"])
        c["era"] = classify_era(c["model"], c["kind"], c["platform"])
        # render_t3's slug guard, ported: a slug-named clip whose filename slug
        # does not match the CURRENT beat title was made for a retired script —
        # attaching the current script's title/text/VO to it states a falsehood
        if c["node"] in story and c["beat"] is not None:
            beats = story[c["node"]]["beats"]
            if 1 <= c["beat"] <= len(beats):
                title = beats[c["beat"] - 1]["title"]
                for fl in c["files"]:
                    # only the tree render_t3 actually assembles from — farm-out
                    # and review take files carry EXPERIMENT names (03-negconf-mot),
                    # not story slugs, and must never be branded retired-era
                    if not re.match(r"genomes/[^/]+/nodes/[^/]+/clips/", fl["p"]):
                        continue
                    slug = retired_era_slug(os.path.basename(fl["p"]), c["beat"], title)
                    if slug:
                        c["retired_era"] = {"slug": slug, "current_title": title}
                        c["problems"].append(
                            f"retired script era — filename slug '{slug}' is not "
                            f"current beat {c['beat']} '{title}' (render_t3 slug guard)")
                        health["retired_era_clips"].append(
                            f"{c['id']}: slug '{slug}' vs current beat {c['beat']} '{title}'")
                        break
        if c["node"] == "002b-first-citizen" and c["beat"] is not None:
            for fl in c["files"]:
                if (os.path.basename(fl["p"]), c["beat"]) in take_index:
                    c["shipped"] = True
        for q in c["queue"]:
            if q["rc"] not in (0, None):
                c["problems"].append(f"queue run failed (rc={q['rc']}, step={q['step']})")
                break
        if any(f["where"] != "local" for f in c["files"]):
            c["problems"].append("files on farm branch, not local")
        if not c["prompt"] and c["era"] in ("LTX motion", "SDXL still"):
            c["problems"].append("prompt unrecorded")
        # cost rows: ledger joins by (short node id, beat)
        if c["node"] and c["beat"] is not None:
            short = lineage.get(c["node"], {}).get("id")
            for lr in ledger_rows:
                if lr["node"] == short and lr["beat"].lstrip("0") == str(c["beat"]):
                    c["cost"].append(lr)
        c.pop("spec_info", None)
        c.pop("_spec_files", None)

    # specs never run — a spec "ran" if a card carries its task id OR any
    # queue-history row names it verbatim in spec_file (task ids often carry
    # a suffix the spec basename lacks, so the task-id join alone lies)
    ran = set()
    for c in cards.values():
        ran.update(c["tasks"])
    ran_spec_files = {r["spec_file"] for rows in queue_by_task.values()
                      for r in rows if r.get("spec_file")}
    ran_spec_bases = {os.path.basename(p) for p in ran_spec_files}
    never_ran = sorted(t for t, sp in specs.items()
                       if t not in ran and sp["file"] not in ran_spec_files
                       and os.path.basename(sp["file"]) not in ran_spec_bases)
    # the actual overlap with the upcoming/held queue — NOT len(upcoming):
    # some never-ran specs are untracked and some upcoming ids have no spec
    never_ran_upcoming = len(set(never_ran) & {str(u.get("id")) for u in upcoming})

    # coverage per node/beat
    coverage = {}
    for slug, st in story.items():
        nb = len(st["beats"])
        if nb == 0:
            continue
        row = []
        for i in range(1, nb + 1):
            state = "none"
            if i in st["vo"]:
                state = "vo"
            row.append(state)
        coverage[slug] = row
    for c in cards.values():
        if c["retired_era"]:
            continue  # footage for a retired script must not light current-beat coverage
        slug, b = c["node"], c["beat"]
        if slug in coverage and b and 1 <= b <= len(coverage[slug]):
            cur = coverage[slug][b - 1]
            has_video = any(f["kind"] == "video" for f in c["files"])
            has_image = any(f["kind"] == "image" for f in c["files"])
            if c["shipped"]:
                coverage[slug][b - 1] = "ship"
            elif cur != "ship" and has_video:
                coverage[slug][b - 1] = "clip"
            elif cur in ("none", "vo") and has_image:
                coverage[slug][b - 1] = "still" if cur == "none" else "vo+still"

    card_list = sorted(cards.values(),
                       key=lambda c: (c["node"] or "~", c["beat"] or 99, c["id"]))

    # branch-only dirs are a marked FACT (they exist, just elsewhere),
    # fallback-parsed yamls were still read, and notes are build/infra
    # degradations, not data links — none is an unresolved link
    unresolved = sum(len(v) for k, v in health.items()
                     if isinstance(v, list)
                     and k not in ("branch_only_tasks", "unparsable_yaml", "notes"))

    totals = {
        "nodes": len(lineage),
        "beats": sum(len(s["beats"]) for s in story.values()),
        "vo_beats": sum(len(s["vo"]) for s in story.values()),
        "cards": len(card_list),
        "queue_runs": queue_meta.get("job_count", 0),
        "queue_ok": queue_meta.get("ok", 0),
        "queue_failed": queue_meta.get("failed", 0),
        "media_files": len(media),
        "farm_dirs_local": len(local_farm_dirs),
        "farm_dirs_branch_only": len(branch_only_dirs),
        "specs": len(specs),
        "specs_never_ran": len(never_ran),
        "spend_usd": round(spend_total, 2),
        "unresolved": unresolved,
    }

    data = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "root": str(ROOT),
        "queue_meta": queue_meta,
        "totals": totals,
        "nodes": {slug: {**st, "grades": (grades_by_beat if slug == "002b-first-citizen" else {}),
                         "ship": (ship if slug == "002b-first-citizen" else {})}
                  for slug, st in story.items()},
        "coverage": coverage,
        "cards": card_list,
        "health": {k: v for k, v in health.items()},
        "never_ran_sample": never_ran[:40],
        "never_ran_upcoming": never_ran_upcoming,
        "upcoming": [{"id": u.get("id"), "state": u.get("state"), "node": u.get("node"),
                      "beat": u.get("beat"), "kind": u.get("kind")} for u in upcoming],
        "ledger": ledger_rows,
    }

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(render_html(data, lineage), encoding="utf-8")

    dt = time.time() - t0
    print(f"BIRDSEYE: nodes={totals['nodes']} beats={totals['beats']} cards={totals['cards']} "
          f"queue_runs={totals['queue_runs']} media_files={totals['media_files']} "
          f"spend=${totals['spend_usd']} unresolved={unresolved} "
          f"out={rel(OUT_DIR / 'index.html')} ({dt:.1f}s)")
    return 0


# ------------------------------------------------------------------ HTML

def esc(s):
    return html_mod.escape(str(s if s is not None else ""))


def render_tree_html(lineage, data):
    children = {}
    for slug, n in lineage.items():
        children.setdefault(n["parent"], []).append(slug)
    id2slug = {n["id"]: s for s, n in lineage.items()}

    def branch(parent_id):
        out = []
        for slug in sorted(children.get(parent_id, [])):
            n = lineage[slug]
            beats = len(data["nodes"][slug]["beats"])
            ncards = sum(1 for c in data["cards"] if c["node"] == slug)
            trunk = ' <span class="trunk">trunk</span>' if n["trunk"] else ""
            cov = data["coverage"].get(slug)
            covh = ""
            if cov:
                cells = "".join(
                    f'<i class="cv cv-{st}" title="beat {i+1}: {st}" data-node="{esc(slug)}" data-beat="{i+1}"></i>'
                    for i, st in enumerate(cov))
                covh = f'<span class="covrow">{cells}</span>'
            out.append(
                f'<li><span class="tn" data-node="{esc(slug)}">'
                f'<b>{esc(n["id"])}</b> {esc(n["title"])}'
                f' <span class="st st-{esc(n["status"])}">{esc(n["status"])}</span>{trunk}'
                f' <span class="mut">{beats} beats · {ncards} cards</span></span>'
                f'{covh}')
            kids = branch(n["id"])
            if kids:
                out.append(f"<ul>{kids}</ul>")
            out.append("</li>")
        return "".join(out)

    return f'<ul class="tree">{branch(None)}</ul>'


def render_health_html(h, data):
    labels = {
        "unparsable_yaml": "YAML files the parser could not fully read (fallback used)",
        "orphan_sidecars": "sidecars whose media file is missing on disk",
        "orphan_clips": "mp4s with NO sidecar — provenance unrecorded",
        "beat_conflicts": "beat-number conflicts (precedence rule applied, all sources shown)",
        "compound_tasks": "compound task: fields (2+ task ids in one sidecar)",
        "tasks_missing_spec": "tasks with no job spec (by task id OR queue-history spec_file)",
        "ship_pick_missing": "ship-manifest picks NOT on disk in sources/",
        "node_unresolved": "cards whose story node could not be resolved",
        "orphan_vo": "VO manifests beyond the current script's beat count",
        "branch_only_tasks": "farm-out task manifests that exist only on the farm branch",
        "retired_era_clips": "clips made for a RETIRED script era (filename slug ≠ current beat title)",
        "notes": "build notes — infra degradations (git/queue-history unavailable), not data problems",
    }
    rows = []
    for k, label in labels.items():
        items = h.get(k, [])
        if not items:
            rows.append(f'<div class="hrow ok"><b>0</b> {esc(label)}</div>')
            continue
        lis = "".join(f"<li>{esc(x)}</li>" for x in items[:150])
        more = f"<li>… and {len(items)-150} more</li>" if len(items) > 150 else ""
        rows.append(f'<details class="hrow bad"><summary><b>{len(items)}</b> {esc(label)}</summary>'
                    f'<ul>{lis}{more}</ul></details>')
    nr = data["totals"]["specs_never_ran"]
    sample = "".join(f"<li>{esc(x)}</li>" for x in data["never_ran_sample"])
    rows.append(f'<details class="hrow"><summary><b>{nr}</b> job specs never ran '
                f'(no queue row by task id or spec_file, no sidecar, no farm-out dir — incl. {data["never_ran_upcoming"]} tracked as upcoming/held)'
                f'</summary><ul>{sample}<li>…</li></ul></details>')
    return "".join(rows)


def render_html(data, lineage):
    # '</' escape stops </script>; '<!--' must ALSO be escaped (HTML5 script-data
    # double-escape rule: '<!--'+'<script' swallows the real closing tag and
    # bricks the page). \\u003c is a JSON-valid escape, so JSON.parse still works.
    payload = (json.dumps(data, ensure_ascii=False, default=str)
               .replace("</", "<\\/").replace("<!--", "\\u003c!--"))
    tree = render_tree_html(lineage, data)
    healthbox = render_health_html(data["health"], data)
    t = data["totals"]
    tot = "".join(
        f'<div class="tot"><b>{esc(v)}</b><span>{esc(k)}</span></div>' for k, v in [
            ("story nodes", t["nodes"]), ("beats", t["beats"]), ("VO beats", t["vo_beats"]),
            ("clip cards", t["cards"]), ("queue runs", f"{t['queue_runs']} ({t['queue_ok']} ok / {t['queue_failed']} failed)"),
            ("media files on disk", t["media_files"]),
            ("farm-out dirs", f"{t['farm_dirs_local']} local + {t['farm_dirs_branch_only']} branch-only"),
            ("job specs", f"{t['specs']} ({t['specs_never_ran']} never ran)"),
            ("ledgered spend", f"${t['spend_usd']:.2f}"),
            ("unresolved items", t["unresolved"]),
        ])
    qm = data.get("queue_meta", {})
    qnote = (f"queue history: {esc(qm.get('_file',''))} measured {esc(qm.get('measured_at','?'))} "
             f"from {esc(qm.get('source_branch','?'))}@{esc(str(qm.get('source_commit',''))[:10])}"
             if qm else "queue history: not found")

    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>banyan-city birdseye</title>
<style>
:root{--bg:#0d1117;--panel:#161b22;--panel2:#1c2330;--line:#2d333b;--fg:#e6edf3;
--mut:#8b949e;--amber:#e3b341;--amber2:#d29922;--green:#3fb950;--red:#f85149;
--blue:#58a6ff;--mono:ui-monospace,SFMono-Regular,Menlo,monospace;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:14px/1.5 Inter,-apple-system,"Segoe UI",system-ui,sans-serif;}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
header{padding:1.2rem 2rem .6rem;border-bottom:1px solid var(--line)}
header h1{margin:0;font-size:1.25rem;color:var(--amber);letter-spacing:.04em}
header .sub{color:var(--mut);font-size:.8rem;font-family:var(--mono)}
main{padding:1rem 2rem 4rem;max-width:1500px;margin:0 auto}
.totals{display:flex;flex-wrap:wrap;gap:.6rem;margin:1rem 0}
.tot{background:var(--panel);border:1px solid var(--line);border-radius:8px;
padding:.5rem .9rem;min-width:8rem}
.tot b{display:block;font-size:1.05rem;color:var(--amber)}
.tot span{color:var(--mut);font-size:.72rem;text-transform:uppercase;letter-spacing:.05em}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
@media(max-width:1000px){.cols{grid-template-columns:1fr}}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem 1.2rem}
.panel h2{margin:.1rem 0 .7rem;font-size:.85rem;color:var(--amber2);
text-transform:uppercase;letter-spacing:.1em}
ul.tree,ul.tree ul{list-style:none;padding-left:1.1rem;margin:.2rem 0;border-left:1px dotted var(--line)}
ul.tree{border-left:none;padding-left:0}
.tn{cursor:pointer;padding:.05rem .3rem;border-radius:5px}
.tn:hover{background:var(--panel2)}
.tn b{color:var(--amber);font-family:var(--mono)}
.st{font-size:.68rem;padding:0 .35rem;border-radius:4px;border:1px solid var(--line);color:var(--mut)}
.st-hot{color:var(--green);border-color:var(--green)}
.trunk{font-size:.68rem;color:var(--amber);border:1px solid var(--amber2);border-radius:4px;padding:0 .35rem}
.mut{color:var(--mut);font-size:.75rem}
.covrow{display:inline-flex;gap:2px;margin-left:.6rem;vertical-align:middle}
.cv{width:11px;height:11px;border-radius:2px;background:#21262d;display:inline-block;cursor:pointer}
.cv-vo{background:#39435a}.cv-still{background:#8f6d1f}.cv-vo\\+still{background:#8f6d1f}
.cv-clip{background:#2ea043}.cv-ship{background:var(--amber);outline:1px solid #fff3}
.legend{margin-top:.5rem;font-size:.72rem;color:var(--mut)}
.legend i{width:10px;height:10px;display:inline-block;border-radius:2px;margin:0 .2rem 0 .7rem;vertical-align:-1px}
.hrow{padding:.25rem .4rem;border-bottom:1px dashed var(--line);font-size:.8rem}
.hrow.ok{color:var(--mut)}.hrow.bad summary{color:var(--red);cursor:pointer}
.hrow b{font-family:var(--mono)}
.hrow ul{max-height:14rem;overflow:auto;font-family:var(--mono);font-size:.72rem;color:var(--mut)}
#filters{position:sticky;top:0;z-index:5;background:var(--bg);padding:.8rem 0;
display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;border-bottom:1px solid var(--line);margin-top:1.4rem}
#filters select,#filters input[type=text]{background:var(--panel);color:var(--fg);
border:1px solid var(--line);border-radius:6px;padding:.35rem .5rem;font:inherit;font-size:.82rem}
#filters input[type=text]{min-width:22rem;font-family:var(--mono)}
#filters label{font-size:.8rem;color:var(--mut)}
#count{color:var(--amber);font-family:var(--mono);font-size:.8rem;margin-left:auto}
#cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:.7rem;margin-top:1rem}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;
padding:.7rem .9rem;cursor:pointer;overflow:hidden}
.card:hover{border-color:var(--amber2)}
.card.open{grid-column:1/-1;cursor:default;background:var(--panel2)}
.card .cid{font-family:var(--mono);font-size:.8rem;color:var(--amber);word-break:break-all}
.chips{margin:.3rem 0;display:flex;flex-wrap:wrap;gap:.3rem}
.chip{font-size:.68rem;padding:.05rem .45rem;border-radius:10px;border:1px solid var(--line);color:var(--mut)}
.chip.nb{color:var(--fg);border-color:#444c56}
.chip.era{color:var(--blue)}
.chip.ship{color:#0d1117;background:var(--amber);border-color:var(--amber);font-weight:700}
.chip.prob{color:var(--red);border-color:var(--red)}
.snip{color:var(--mut);font-size:.75rem;max-height:3.2em;overflow:hidden}
.meta1{color:var(--mut);font-size:.72rem;font-family:var(--mono);margin-top:.3rem}
.dossier{margin-top:.8rem;border-top:1px solid var(--line);padding-top:.8rem;font-size:.82rem}
.dossier h4{margin:.9rem 0 .3rem;color:var(--amber2);font-size:.72rem;
text-transform:uppercase;letter-spacing:.09em}
.dossier .src{color:var(--mut);font-size:.7rem;font-style:italic}
pre{background:#0a0d12;border:1px solid var(--line);border-radius:6px;padding:.5rem .7rem;
white-space:pre-wrap;word-break:break-word;font-family:var(--mono);font-size:.76rem;color:#c9d1d9;margin:.3rem 0}
table{border-collapse:collapse;width:100%;font-size:.76rem}
.tblwrap{overflow-x:auto}
th,td{border-bottom:1px solid var(--line);padding:.25rem .5rem;text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:.68rem;text-transform:uppercase}
td{font-family:var(--mono);word-break:break-all}
.ok{color:var(--green)}.bad{color:var(--red)}
video{max-width:280px;max-height:400px;border-radius:6px;border:1px solid var(--line);display:block;margin:.3rem 0}
.voline .who{color:var(--green);font-family:var(--mono);font-size:.72rem;font-weight:700}
#more{margin:1.2rem auto;display:block;background:var(--panel);border:1px solid var(--amber2);
color:var(--amber);padding:.5rem 2rem;border-radius:8px;font:inherit;cursor:pointer}
.problems li{color:var(--red);font-size:.76rem}
footer{color:var(--mut);text-align:center;font-size:.72rem;padding:2rem;font-family:var(--mono)}
</style></head><body>
<header><h1>banyan-city · birdseye</h1>
<div class="sub">read-only console · generated __GENERATED__ · __QNOTE__ · repo __ROOTPATH__</div></header>
<main>
<div class="totals">__TOTALS__</div>
<div class="cols">
<div class="panel"><h2>Story tree — 16 nodes, coverage per beat</h2>__TREE__
<div class="legend">click a node or beat cell to filter the clip view below · beat cells:
<i style="background:#21262d"></i>nothing <i style="background:#39435a"></i>VO only
<i style="background:#8f6d1f"></i>still <i style="background:#2ea043"></i>clip
<i style="background:var(--amber)"></i>shipped pick</div></div>
<div class="panel"><h2>Data health — what could NOT be resolved</h2>__HEALTH__</div>
</div>
<div id="filters">
<label>node <select id="f-node"><option value="">all</option></select></label>
<label>beat <select id="f-beat"><option value="">all</option></select></label>
<label>era <select id="f-era"><option value="">all</option></select></label>
<label><input type="checkbox" id="f-prob"> has problems</label>
<label><input type="checkbox" id="f-ship"> shipped picks</label>
<input type="text" id="f-q" placeholder="search task ids, slugs, prompt text, VO…">
<span id="count"></span>
</div>
<div id="cards"></div>
<button id="more">show more</button>
</main>
<footer>pipeline/birdseye.py · reads only · no server, no network · regenerate = rerun</footer>
<script id="data" type="application/json">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const NODES = DATA.nodes, CARDS = DATA.cards;
const esc = s => String(s==null?'':s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const relurl = p => '../' + p.split('/').map(encodeURIComponent).join('/');
const fileurl = p => 'file://' + (DATA.root + '/' + p).split('/').map(encodeURIComponent).join('/');
const fmtB = b => b==null?'?':(b>1048576?(b/1048576).toFixed(1)+' MB':(b/1024).toFixed(0)+' KB');

// search corpus per card (lazy)
CARDS.forEach(c=>{
  const nd = NODES[c.node]||{};
  const bt = c.retired_era ? {} : ((nd.beats||[])[c.beat-1]||{});
  const vo = c.retired_era ? [] : (((nd.vo||{})[c.beat]||{}).lines||[]);
  c._q = [c.id, c.tasks&&c.tasks.join(' '), c.node, bt.title, c.model, c.prompt,
          (c.files||[]).map(f=>f.p).join(' '), vo.map(l=>l[1]).join(' ')].join(' ').toLowerCase();
});

// filter controls
const sel = id => document.getElementById(id);
const nodeSel=sel('f-node'), beatSel=sel('f-beat'), eraSel=sel('f-era');
Object.keys(NODES).sort().forEach(s=>{
  const o=document.createElement('option'); o.value=s;
  o.textContent=NODES[s].id+' — '+NODES[s].title+' ('+CARDS.filter(c=>c.node===s).length+')';
  nodeSel.appendChild(o);});
const uo=document.createElement('option'); uo.value='__none__'; uo.textContent='(node unresolved)';
nodeSel.appendChild(uo);
[...new Set(CARDS.map(c=>c.era))].sort().forEach(e=>{
  const o=document.createElement('option'); o.value=e; o.textContent=e; eraSel.appendChild(o);});
function fillBeats(){
  const ns=nodeSel.value; beatSel.innerHTML='<option value="">all</option>';
  const beats=[...new Set(CARDS.filter(c=>!ns||c.node===ns).map(c=>c.beat).filter(b=>b!=null))].sort((a,b)=>a-b);
  beats.forEach(b=>{const o=document.createElement('option');o.value=b;o.textContent='beat '+b;beatSel.appendChild(o);});
}
fillBeats();

let shown = 0; const CHUNK = 120; let current = CARDS;
function apply(){
  const ns=nodeSel.value, bs=beatSel.value, es=eraSel.value;
  const pr=sel('f-prob').checked, sh=sel('f-ship').checked;
  const q=sel('f-q').value.trim().toLowerCase();
  current = CARDS.filter(c=>
    (!ns || (ns==='__none__' ? !c.node : c.node===ns)) &&
    (!bs || c.beat===+bs) && (!es || c.era===es) &&
    (!pr || (c.problems&&c.problems.length)) && (!sh || c.shipped) &&
    (!q || c._q.includes(q)));
  shown=0; document.getElementById('cards').innerHTML=''; more();
  sel('count').textContent = current.length + ' / ' + CARDS.length + ' cards';
}
function more(){
  const box=document.getElementById('cards');
  const slice=current.slice(shown, shown+CHUNK);
  slice.forEach(c=>box.insertAdjacentHTML('beforeend', cardHtml(c)));
  shown+=slice.length;
  document.getElementById('more').style.display = shown<current.length?'block':'none';
}
['f-node','f-beat','f-era','f-prob','f-ship'].forEach(id=>sel(id).addEventListener('change',()=>{if(id==='f-node')fillBeats();apply();}));
let deb; sel('f-q').addEventListener('input',()=>{clearTimeout(deb);deb=setTimeout(apply,200);});
document.getElementById('more').addEventListener('click',more);
document.querySelectorAll('.tn').forEach(el=>el.addEventListener('click',()=>{
  nodeSel.value=el.dataset.node; fillBeats(); apply();
  document.getElementById('filters').scrollIntoView({behavior:'smooth'});}));
document.querySelectorAll('.cv').forEach(el=>el.addEventListener('click',()=>{
  nodeSel.value=el.dataset.node; fillBeats(); beatSel.value=el.dataset.beat; apply();
  document.getElementById('filters').scrollIntoView({behavior:'smooth'});}));

function cardHtml(c){
  const nd=NODES[c.node]||{}; const bt=c.retired_era?null:(nd.beats||[])[c.beat-1];
  const idx=CARDS.indexOf(c);
  const nb = c.support ? 'support — no story node'
    : (nd.id?nd.id:'?') + (c.beat!=null?(' · beat '+String(c.beat).padStart(2,'0')):' · beat ?')
      + (c.retired_era?(' · RETIRED SCRIPT ERA (slug '+c.retired_era.slug+')'):(bt?(' · '+bt.title):''));
  let chips = '<span class="chip nb">'+esc(nb)+'</span><span class="chip era">'+esc(c.era)+'</span>';
  if(c.shipped) chips+='<span class="chip ship">SHIPPED PICK</span>';
  if(c.problems&&c.problems.length) chips+='<span class="chip prob">'+c.problems.length+' problem'+(c.problems.length>1?'s':'')+'</span>';
  const nfiles=(c.files||[]).length, nq=(c.queue||[]).length;
  return '<div class="card" data-i="'+idx+'" onclick="toggle(event,this)">'
    +'<div class="cid">'+esc(c.id)+'</div><div class="chips">'+chips+'</div>'
    +'<div class="snip">'+esc((c.prompt||'').slice(0,150)||'(no prompt recorded)')+'</div>'
    +'<div class="meta1">'+esc(c.model?String(c.model).slice(0,48):'model ?')
    +' · '+nfiles+' file'+(nfiles!==1?'s':'')+' · '+nq+' queue run'+(nq!==1?'s':'')+'</div>'
    +'<div class="dz"></div></div>';
}
function toggle(ev,el){
  if(ev.target.closest('a,video,pre,table,button')) return;
  const open = el.classList.toggle('open');
  const dz = el.querySelector('.dz');
  if(open && !dz.innerHTML) dz.innerHTML = dossier(CARDS[+el.dataset.i]);
  if(!open) dz.innerHTML='';
}
function kv(rows){
  return '<div class="tblwrap"><table>'+rows.filter(r=>r[1]!=null&&r[1]!=='')
    .map(r=>'<tr><th>'+esc(r[0])+'</th><td>'+r[1]+'</td></tr>').join('')+'</table></div>';
}
function dossier(c){
  const nd=NODES[c.node]||{};
  // a retired-era clip was made for a script that no longer exists — showing
  // the CURRENT script's title/text/VO on it would state a falsehood
  const bt=c.retired_era?null:(nd.beats||[])[c.beat-1];
  const vo=c.retired_era?null:(nd.vo||{})[c.beat];
  const shot=c.retired_era?null:(nd.shots||{})[c.beat];
  let beatRow = 'unresolved';
  if(c.retired_era)
    beatRow = esc(c.beat)+' — <b>RETIRED SCRIPT ERA</b> — filename slug \\''+esc(c.retired_era.slug)
      +'\\' \\u2260 current beat title \\''+esc(c.retired_era.current_title)
      +'\\'; current-script text/VO suppressed (see this node\\'s leaves/*-t3-*.yaml for that era\\'s own record)'
      +' <span class="src">(resolved via '+esc(c.beat_src)+')</span>';
  else if(c.beat!=null)
    beatRow = esc(c.beat+(bt?(' — '+bt.title+' ('+bt.range+')'):''))+' <span class="src">(resolved via '+esc(c.beat_src)+')</span>';
  let h='<div class="dossier">';
  // story
  h+='<h4>Story</h4>'+kv([
    ['support', c.support?esc(c.support):null],
    ['node', c.support&&!c.node?null:esc((nd.id||'?')+' — '+(nd.title||c.node||'unresolved'))+' <span class="src">('+esc(c.node_src||'?')+')</span>'],
    ['beat', c.support&&c.beat==null?null:beatRow],
  ]);
  if(c.beat_conflicts&&c.beat_conflicts.length)
    h+='<pre class="bad">BEAT CONFLICT — all sources: \\n'+esc(c.beat_conflicts.join('\\n'))+'</pre>';
  if(bt&&bt.text) h+='<h4>Script (node.md, struck-through staging excluded)</h4><pre>'+esc(bt.text)+'</pre>';
  if(vo){ h+='<h4>VO — '+esc(vo.engine)+' · '+esc(vo.total_s)+'s · '+esc(vo.path)+'</h4>';
    h+=vo.lines.map(l=>'<div class="voline"><span class="who">'+esc(l[0])+':</span> '+esc(l[1])+'</div>').join('');}
  else if(!c.retired_era && c.beat!=null && nd.vo) h+='<h4>VO</h4><div class="mut">silent beat — no NN-vo.json</div>';
  // prompt
  h+='<h4>Prompt '+(c.prompt_src?'<span class="src">— source: '+esc(c.prompt_src)+'</span>':'')+'</h4>';
  h+= c.prompt? '<pre>'+esc(c.prompt)+'</pre>' : '<div class="bad">no prompt recorded anywhere for this render</div>';
  if(c.negative) h+='<h4>Negative</h4><pre>'+esc(c.negative)+'</pre>';
  if(shot&&shot.prompt&&shot.prompt!==c.prompt)
    h+='<h4>Beat\\u2019s authored prompt <span class="src">— shots.md registry (may differ from what rendered)</span></h4><pre>'+esc(shot.prompt)+'</pre>';
  // settings
  h+='<h4>Model / settings</h4>'+kv([
    ['model',esc(c.model)],['platform',esc(c.platform)],['seed',esc(c.seed)],
    ['steps',esc(c.steps)],['size',esc(c.size)],['guidance',esc(c.guidance)],
    ['seconds',esc(c.seconds)],['kind',esc(c.kind)],
    ['task(s)',esc((c.tasks||[]).join('  +  '))],
    ['job spec', c.spec?('<a href="'+fileurl(c.spec)+'">'+esc(c.spec)+'</a>'):null],
    ['sidecar(s)', (c.sidecars||[]).map(s=>'<a href="'+fileurl(s)+'">'+esc(s)+'</a>').join('<br>')||null],
  ].concat(Object.entries(c.extras||{}).map(e=>[e[0], esc(e[1])])));
  // refs
  if(c.init||c.refs.length){
    h+='<h4>Init plate / image refs</h4>';
    if(c.init) h+='<pre>init: '+esc(JSON.stringify(c.init))+'</pre>';
    c.refs.forEach(r=>h+='<pre>ref: '+esc(JSON.stringify(r))+'</pre>');
  }
  // files
  if(c.files&&c.files.length){
    h+='<h4>Files on disk</h4><div class="tblwrap"><table><tr><th>path</th><th>size</th><th>sha256</th><th>where</th></tr>';
    c.files.forEach(f=>{
      const local = f.where==='local';
      h+='<tr><td>'+(local?'<a href="'+fileurl(f.p)+'">'+esc(f.p)+'</a>':esc(f.p))+'</td>'
        +'<td>'+fmtB(f.bytes)+'</td><td>'+esc(f.sha?f.sha.slice(0,12):'—')+'</td>'
        +'<td class="'+(local?'ok':'bad')+'">'+esc(f.where)+'</td></tr>';});
    h+='</table></div>';
    c.files.filter(f=>f.kind==='video'&&f.where==='local').slice(0,3).forEach(f=>{
      h+='<video controls preload="none" src="'+relurl(f.p)+'"></video>';});
  }
  // grades
  const gr=(nd.grades||{})[c.beat];
  if(gr){ h+='<h4>Grades (plate finish pass)</h4>';
    gr.forEach(g=>h+='<pre>'+esc(g.tag)+' · station '+esc(g.station)+' · hue drift '+esc(g.hue_drift_deg)
      +'° · ink lift '+esc(g.ink_lift)
      +'\\ngraded png: '+(g.png?('<a href="'+fileurl(g.png)+'">'+esc(g.png)+'</a>'):'(not on disk)')
      +(g.out_sha256?(' · out_sha256 '+esc(g.out_sha256)+'…'):'')
      +'\\ngrade json: <a href="'+fileurl(g.file)+'">'+esc(g.file)+'</a>'
      +'\\nplate: '+esc(g.plate)+'\\nknobs: '+esc(JSON.stringify(g.knobs))
      +'\\nbefore: '+esc(JSON.stringify(g.before))+'\\nafter:  '+esc(JSON.stringify(g.after))+'</pre>');}
  // queue
  if(c.queue&&c.queue.length){
    h+='<h4>Queue history ('+c.queue.length+' runs)</h4><div class="tblwrap"><table><tr><th>run id</th><th>rc</th><th>failed step</th><th>attempts</th><th>host</th><th>started</th><th>dur s</th></tr>';
    c.queue.forEach(q=>h+='<tr><td>'+esc(q.id)+'</td><td class="'+(q.rc===0?'ok':'bad')+'">'+esc(q.rc)+'</td>'
      +'<td>'+esc(q.step||'')+'</td><td>'+esc(q.attempts)+'</td><td>'+esc(q.host)+'</td>'
      +'<td>'+esc(q.start)+'</td><td>'+esc(q.dur)+'</td></tr>');
    h+='</table></div>';}
  if(c.verdict) h+='<h4>Founder verdict (episode-progress)</h4><pre>'+esc(c.verdict.state||'')
    +(c.verdict.picked?' · PICKED':'')+'\\n'+esc(c.verdict.note||'')+'</pre>';
  const sh=(nd.ship||{})[c.beat];
  if(sh) h+='<h4>Shipped cut (ep2-ship-0821)</h4><pre>pick: '+esc(sh.take)+' · sha '+esc(sh.sha256)
    +' · '+(sh.on_disk?'<span class=ok>on disk</span>':'<span class=bad>NOT in sources/ — swap mid-flight</span>')
    +'\\nverdict: '+esc(sh.verdict)+'</pre>';
  if(c.cost&&c.cost.length){
    h+='<h4>Cost — ALL ledger rows for this (node, beat) <span class="src">— ledger/render-spend.csv joins money at (node, beat) granularity only; these rows are NOT this clip\\u2019s spend (July provider-era rows included)</span></h4><div class="tblwrap"><table><tr><th>date</th><th>provider</th><th>model</th><th>$</th><th>note</th></tr>';
    c.cost.forEach(r=>h+='<tr><td>'+esc(r.date)+'</td><td>'+esc(r.provider)+'</td><td>'+esc(r.model)+'</td><td>'+esc(r.usd)+'</td><td>'+esc(r.note)+'</td></tr>');
    h+='</table></div>';}
  if(c.problems&&c.problems.length)
    h+='<h4>Problems</h4><ul class="problems">'+c.problems.map(p=>'<li>'+esc(p)+'</li>').join('')+'</ul>';
  return h+'</div>';
}
apply();
</script>
</body></html>""" \
        .replace("__GENERATED__", esc(data["generated"])) \
        .replace("__QNOTE__", qnote) \
        .replace("__ROOTPATH__", esc(data["root"])) \
        .replace("__TOTALS__", tot) \
        .replace("__TREE__", tree) \
        .replace("__HEALTH__", healthbox) \
        .replace("__DATA__", payload)


if __name__ == "__main__":
    sys.exit(main())
