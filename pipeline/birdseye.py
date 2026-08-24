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
        entry["r1"] = None
        if node_md.exists():
            md_text = node_md.read_text(encoding="utf-8", errors="replace")
            entry["beats"] = parse_node_beats(md_text)
            # R1 one-liner: first sentence of the "## State change" section
            m = re.search(r"^## State change[^\n]*\n(.*?)(?=^## |\Z)", md_text, re.M | re.S)
            if m:
                prose = re.sub(r"[*_`]", "", " ".join(m.group(1).split())).strip()
                sm = re.match(r"(.+?[.!?])(\s|$)", prose)
                entry["r1"] = (sm.group(1) if sm else prose[:200]).strip() or None
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
    media = {}        # relpath -> bytes
    media_mtime = {}  # relpath -> mtime (same stat call; newest-render ordering)
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
                        st = p.stat()
                        media[rel(p)] = st.st_size
                        media_mtime[rel(p)] = st.st_mtime
                    except OSError:
                        pass
    return sidecars, still_yamls, grades, manifests, media, media_mtime


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

    sidecar_paths, still_yaml_paths, grade_paths, manifest_paths, media, media_mtime = walk_repo()

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
                              "where": where, "kind": kind,
                              "mt": media_mtime.get(path)})

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

    # per-beat "best clip" pointer: shipped pick wins, else newest local
    # playable render (mp4/webm — .mov is not reliably playable in <video>)
    PLAYABLE = {".mp4", ".webm"}
    best_clip: dict[str, dict] = {}
    best_rank: dict[tuple, tuple] = {}
    for c in cards.values():
        if c["retired_era"] or not c["node"] or c["beat"] is None:
            continue
        for f in c["files"]:
            if f["kind"] != "video" or f["where"] != "local":
                continue
            if os.path.splitext(f["p"])[1].lower() not in PLAYABLE:
                continue
            shipped = (os.path.basename(f["p"]), c["beat"]) in take_index
            rank = (1 if shipped else 0, f.get("mt") or 0, f["p"])
            key = (c["node"], c["beat"])
            if key not in best_rank or rank > best_rank[key]:
                best_rank[key] = rank
                best_clip.setdefault(c["node"], {})[str(c["beat"])] = {
                    "p": f["p"], "shipped": shipped, "card": c["id"]}

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
        "best": best_clip,
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
# Render layer — "SAPLING · production atlas". A screening room, not a
# console: dark, calm, the show's own frames providing the color.
# Three levels of progressive disclosure: story tree (left rail) →
# filmstrip of the selected node's beats (the hero) → beat dossier.

def esc(s):
    return html_mod.escape(str(s if s is not None else ""))


def render_tree_html(lineage, data):
    children = {}
    for slug, n in lineage.items():
        children.setdefault(n["parent"], []).append(slug)

    def branch(parent_id):
        out = []
        for slug in sorted(children.get(parent_id, [])):
            n = lineage[slug]
            cov = data["coverage"].get(slug) or []
            segs = []
            for i, st in enumerate(cov):
                cls = []
                if st in ("clip", "ship"):
                    cls.append("f")
                if st == "ship":
                    cls.append("s")
                segs.append(f'<i class="{" ".join(cls)}" title="beat {i+1}: {esc(st)}"></i>')
            covh = f'<span class="covrow" aria-hidden="true">{"".join(segs)}</span>' if segs else ""
            hot = " hot" if n["status"] == "hot" else ""
            out.append(
                f'<li><button class="tn" type="button" data-node="{esc(slug)}">'
                f'<span class="trow"><span class="tid">{esc(n["id"])}</span>'
                f'<span class="ttl">{esc(n["title"])}</span>'
                f'<span class="sdot{hot}" title="{esc(n["status"])}"></span></span>'
                f'{covh}</button>')
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
    # bricks the page). < is a JSON-valid escape, so JSON.parse still works.
    payload = (json.dumps(data, ensure_ascii=False, default=str)
               .replace("</", "<\\/").replace("<!--", "\\u003c!--"))
    tree = render_tree_html(lineage, data)
    healthbox = render_health_html(data["health"], data)
    t = data["totals"]
    stat = (f"{t['nodes']} story nodes · {t['beats']} beats · "
            f"{t['cards']:,} renders on disk · {t['queue_runs']:,} queue runs · "
            f"${t['spend_usd']:.2f} ever spent")
    hline = f"{t['unresolved']:,} links the generator could not resolve — view details"
    qm = data.get("queue_meta", {})
    qnote = (f"queue history: {esc(qm.get('_file',''))} measured {esc(qm.get('measured_at','?'))} "
             f"from {esc(qm.get('source_branch','?'))}@{esc(str(qm.get('source_commit',''))[:10])}"
             if qm else "queue history: not found")

    return r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SAPLING · production atlas</title>
<style>
:root{
  --bg:#131313; --panel:#1c1c1a; --edge:#2c2c28;
  --ink:#f2efe6; --dim:#a8a49a; --faint:#6b675f;
  --leaf:#8fbf6f; --warn:#d9a53f; --bad:#cf5f56;
  --disp:"Avenir Next","Helvetica Neue",sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
}
*{box-sizing:border-box}
html,body{overflow-x:hidden}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.55 Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--leaf);text-decoration:none}
a:hover{text-decoration:underline}
:focus-visible{outline:2px solid var(--leaf);outline-offset:2px;border-radius:4px}
.mono{font-family:var(--mono)}

/* ---- header ---- */
header{padding:1.6rem 2.4rem 1.2rem}
.bar{display:flex;align-items:baseline;gap:1.1rem;flex-wrap:wrap}
.wordmark{font-family:var(--disp);font-weight:700;font-size:1.3rem;letter-spacing:.3em;white-space:nowrap}
.wordmark i{display:inline-block;width:.44em;height:.44em;background:var(--leaf);border-radius:2px;margin-left:.15em}
.atlas{font-family:var(--disp);font-weight:600;font-size:.82rem;letter-spacing:.18em;color:var(--dim)}
.bar .right{margin-left:auto;display:flex;align-items:center;gap:1.1rem}
.gen{color:var(--faint);font-size:.76rem;font-family:var(--mono)}
#q{width:240px;background:var(--panel);border:1px solid var(--edge);border-radius:6px;
  color:var(--ink);padding:.42rem .7rem;font:inherit;font-size:.85rem}
#q::placeholder{color:var(--faint)}
.statline{margin:.9rem 0 0;color:var(--dim);font-size:.95rem}

/* ---- layout ---- */
#wrap{display:flex;gap:2.2rem;padding:.4rem 2.4rem 3rem;align-items:flex-start}
#rail{width:300px;flex:0 0 300px;position:sticky;top:0;max-height:100vh;overflow-y:auto;
  padding:.8rem 0 2rem}
#stage{flex:1;min-width:0;padding-top:.8rem}
@media(max-width:900px){#wrap{flex-direction:column}
  #rail{position:static;width:100%;flex:none;max-height:none}}

/* ---- level 1: story tree ---- */
.tree,.tree ul{list-style:none;margin:0;padding:0}
.tree ul{padding-left:.95rem}
.tn{display:block;width:100%;text-align:left;background:none;border:0;
  border-left:3px solid transparent;padding:.4rem .6rem .45rem;margin:.1rem 0;
  border-radius:6px;cursor:pointer;color:var(--ink);font:inherit}
.tn:hover{background:var(--panel)}
.tn.sel{border-left-color:var(--leaf);background:var(--panel);border-radius:0 6px 6px 0}
.trow{display:flex;align-items:baseline;gap:.45rem;min-width:0}
.tid{font-family:var(--mono);font-size:.7rem;color:var(--faint);flex:none}
.ttl{font-size:.86rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sdot{flex:none;width:6px;height:6px;border-radius:50%;background:var(--faint);margin-left:auto;align-self:center}
.sdot.hot{background:var(--leaf)}
.covrow{display:flex;gap:2px;margin-top:.38rem;height:4px}
.covrow i{flex:1;min-width:2px;border-radius:1px;box-shadow:inset 0 0 0 1px var(--edge);position:relative}
.covrow i.f{background:var(--leaf);box-shadow:none}
.covrow i.s::after{content:"";position:absolute;left:50%;top:-5px;width:4px;height:4px;
  margin-left:-2px;border-radius:50%;background:var(--warn)}

/* ---- level 2: filmstrip ---- */
#nodehead h2{font-family:var(--disp);font-weight:700;font-size:1.75rem;margin:.1rem 0 .15rem;letter-spacing:.01em}
#nodehead .nmeta{color:var(--faint);font-size:.82rem}
#nodehead .nmeta .mono{font-size:.78rem}
#nodehead .r1{color:var(--dim);max-width:56rem;margin:.45rem 0 0}
.strip{display:flex;gap:14px;overflow-x:auto;overflow-y:hidden;
  padding:1.1rem .2rem 1.2rem;scrollbar-width:thin;scrollbar-color:var(--edge) transparent}
.fcard{flex:none;width:132px;cursor:pointer;background:none;border:0;padding:0;
  color:var(--ink);font:inherit;text-align:left}
.fmedia{width:132px;height:235px;border-radius:10px;overflow:hidden;background:var(--panel);
  box-shadow:inset 0 0 0 1px var(--edge);position:relative}
.fmedia video,.fmedia img{width:100%;height:100%;object-fit:cover;display:block;background:var(--panel)}
.fcard.sel .fmedia{box-shadow:0 0 0 2px var(--leaf)}
.ph{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:.4rem}
.ph b{font-family:var(--disp);font-weight:600;font-size:2.1rem;color:var(--faint)}
.ph span{color:var(--faint);font-size:.7rem}
.fmeta{margin-top:.5rem;width:132px}
.fnum{font-family:var(--mono);font-size:.7rem;color:var(--faint)}
.ftitle{font-size:.8rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ftc{font-family:var(--mono);font-size:.68rem;color:var(--faint)}
.fdots{display:flex;gap:4px;margin-top:.32rem;height:6px}
.fdots i{width:6px;height:6px;border-radius:50%}
.fdots .d-ship{background:var(--warn)}
.fdots .d-prob{background:var(--bad)}
.unplaced{color:var(--faint);font-size:.82rem;background:none;border:0;cursor:pointer;
  font-family:inherit;padding:0;text-decoration:underline dotted var(--faint)}

/* ---- search results ---- */
#results{margin:.2rem 0 1.6rem}
.rline{color:var(--dim);font-size:.9rem;display:flex;align-items:center;gap:.7rem}
#clr{background:var(--panel);border:1px solid var(--edge);color:var(--dim);border-radius:6px;
  width:1.6rem;height:1.6rem;cursor:pointer;font:inherit;line-height:1}
.rlabel{font-family:var(--mono);font-size:.66rem;color:var(--faint);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;width:132px}

/* ---- level 3: dossier ---- */
#dossier{max-width:900px;margin-top:1.2rem}
.dhead{display:flex;align-items:baseline;gap:.8rem;flex-wrap:wrap}
.dhead h3{font-family:var(--disp);font-weight:700;font-size:1.3rem;margin:0;letter-spacing:.01em}
.dhead .tc{font-family:var(--mono);color:var(--faint);font-size:.82rem}
.bship{font-family:var(--disp);font-weight:600;font-size:.66rem;letter-spacing:.12em;
  color:#131313;background:var(--warn);border-radius:6px;padding:.14rem .5rem}
.shipline{color:var(--dim);font-size:.84rem;margin:.4rem 0 0}
.hist{margin:10px 0}
.hist summary{color:var(--faint);font-size:13px;cursor:pointer;list-style:none}
.hist summary::before{content:"▸ ";color:var(--faint)}
.hist[open] summary::before{content:"▾ "}
.hist p{color:var(--dim);font-size:13.5px;line-height:1.6;margin-top:8px}
.scriptpage{background:var(--panel);border-radius:10px;padding:1.2rem 1.5rem;margin:1.1rem 0}
.scriptpage .act{color:var(--dim);margin:.55rem 0}
.scriptpage .dlg{margin:.6rem 0 .6rem 1.3rem}
.who{font-variant:small-caps;letter-spacing:.06em;font-weight:600}
.cue{color:var(--dim);font-style:italic;font-size:.92em}
.vohead{color:var(--faint);font-size:.74rem;font-family:var(--mono);
  margin:1.1rem 0 .2rem;padding-top:.8rem;border-top:1px solid var(--edge)}
details.authored{margin:.4rem 0 1rem;color:var(--dim);font-size:.86rem}
details.authored summary{cursor:pointer;color:var(--faint)}
details.authored pre{white-space:pre-wrap;word-break:break-word;font-family:var(--mono);
  font-size:.78rem;color:var(--dim);margin:.4rem 0 0}
.takecount{color:var(--faint);font-size:.82rem;margin:1.3rem 0 .2rem}
.cliprow{display:flex;gap:1.2rem;padding:1.1rem 0;border-top:1px solid var(--edge)}
.cliprow .cvid{flex:none;width:96px}
.cliprow video,.cliprow img{width:96px;height:170px;object-fit:cover;border-radius:6px;
  background:var(--panel);display:block}
.rowph{width:96px;height:170px;border-radius:6px;background:var(--panel);
  display:flex;align-items:center;justify-content:center;color:var(--faint);
  font-size:.66rem;text-align:center;padding:.5rem}
.facts{flex:1;min-width:0}
.rid{font-family:var(--mono);font-size:.8rem;margin-bottom:.4rem;overflow-wrap:anywhere}
.rid .tag{margin-left:.5rem}
.tag{font-size:.66rem;border:1px solid var(--edge);border-radius:6px;padding:.05rem .4rem;
  color:var(--dim);white-space:nowrap}
.tag.gold{color:var(--warn);border-color:var(--warn)}
.fgrid{display:grid;grid-template-columns:108px 1fr;gap:.3rem 1rem;font-size:.85rem;margin:0}
.fgrid dt{color:var(--faint);font-variant:small-caps;letter-spacing:.05em;font-size:.8rem}
.fgrid dd{margin:0;min-width:0;overflow-wrap:break-word}
.quote{border-left:2px solid var(--edge);padding:.1rem 0 .1rem .8rem;white-space:pre-wrap;word-break:break-word}
.qsrc{color:var(--faint);font-size:.74rem;font-style:italic}
.frow{font-family:var(--mono);font-size:.75rem;color:var(--dim);overflow-wrap:anywhere;padding:.06rem 0}
.xtra{color:var(--faint);font-size:.76rem;font-family:var(--mono);overflow-wrap:anywhere}
.amber{color:var(--warn);font-size:.84rem;margin-top:.55rem}
.dsec{margin:1.2rem 0 0}
.dsec h4{color:var(--faint);font-variant:small-caps;letter-spacing:.06em;font-weight:600;
  font-size:.85rem;margin:0 0 .3rem}
.dnote{color:var(--faint);font-size:.78rem;font-style:italic}

/* ---- health footer ---- */
footer{padding:2.4rem 2.4rem 3rem;color:var(--dim)}
#hline{background:none;border:0;color:var(--dim);font:inherit;font-size:.9rem;
  cursor:pointer;padding:0;text-decoration:underline dotted var(--faint)}
#hbox{background:var(--panel);border-radius:10px;padding:1rem 1.4rem;margin-top:1rem}
.hrow{padding:.32rem 0;border-bottom:1px solid var(--edge);font-size:.82rem;color:var(--dim)}
.hrow.ok{color:var(--faint)}
.hrow.bad summary{color:var(--bad);cursor:pointer}
.hrow b{font-family:var(--mono)}
.hrow ul{max-height:14rem;overflow:auto;font-family:var(--mono);font-size:.72rem;color:var(--dim)}
.buildnote{color:var(--faint);font-size:.74rem;font-family:var(--mono);margin-top:1.3rem}

@media (prefers-reduced-motion: reduce){
  html{scroll-behavior:auto}
}
</style></head><body>
<header>
  <div class="bar">
    <span class="wordmark">SAPLING<i aria-hidden="true"></i></span>
    <span class="atlas">production atlas</span>
    <span class="right">
      <span class="gen">generated __GENERATED__</span>
      <input id="q" type="search" placeholder="search tasks, prompts, VO…"
             aria-label="search task ids, slugs, prompts, VO">
    </span>
  </div>
  <p class="statline">__STAT__</p>
</header>
<div id="wrap">
  <nav id="rail" aria-label="story tree">__TREE__</nav>
  <main id="stage">
    <section id="results" hidden></section>
    <section id="nodehead"></section>
    <div id="strip" class="strip"></div>
    <p id="unplacedline"></p>
    <section id="dossier"></section>
  </main>
</div>
<footer>
  <button id="hline" type="button" aria-expanded="false">__HLINE__</button>
  <div id="hbox" hidden>__HEALTH__</div>
  <p class="buildnote">__QNOTE__<br>pipeline/birdseye.py · reads only · no server, no network · regenerate = rerun</p>
</footer>
<script id="data" type="application/json">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const NODES = DATA.nodes, CARDS = DATA.cards, BEST = DATA.best || {};
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const esc = s => String(s==null?'':s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const relurl = p => '../' + p.split('/').map(encodeURIComponent).join('/');
const fileurl = p => 'file://' + (DATA.root + '/' + p).split('/').map(encodeURIComponent).join('/');
const fmtB = b => b==null?'?':(b>1048576?(b/1048576).toFixed(1)+' MB':(b/1024).toFixed(0)+' KB');
const pad2 = n => String(n).padStart(2,'0');
const $ = id => document.getElementById(id);
const PLAYABLE = /\.(mp4|webm)$/i;

// ---- indexes: cards by node|beat, per-card newest mtime + search corpus
const byNB = {};
CARDS.forEach((c,i) => {
  c._i = i;
  const k = (c.node||'') + '|' + (c.beat==null?'':c.beat);
  (byNB[k] = byNB[k] || []).push(c);
  c._mt = Math.max(0, ...(c.files||[]).map(f=>f.mt||0));
  const nd = NODES[c.node]||{};
  const bt = c.retired_era ? {} : ((nd.beats||[])[c.beat-1]||{});
  const vo = c.retired_era ? [] : (((nd.vo||{})[c.beat]||{}).lines||[]);
  c._q = [c.id,(c.tasks||[]).join(' '),c.node,bt.title,c.model,c.prompt,
          (c.files||[]).map(f=>f.p).join(' '),vo.map(l=>l[1]).join(' ')].join(' ').toLowerCase();
});
function beatCards(slug,beat){ return byNB[slug+'|'+(beat==null?'':beat)]||[]; }
function bestLocalVideo(c){
  const vids=(c.files||[]).filter(f=>f.kind==='video'&&f.where==='local'&&PLAYABLE.test(f.p));
  vids.sort((a,b)=>(b.mt||0)-(a.mt||0));
  return vids[0]||null;
}
function bestLocalImage(c){
  const ims=(c.files||[]).filter(f=>f.kind==='image'&&f.where==='local');
  ims.sort((a,b)=>(b.mt||0)-(a.mt||0));
  return ims[0]||null;
}

// ---- lazy first frames: when a card scrolls into view, load metadata only
const IO = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if(!e.isIntersecting) return;
    const v = e.target.querySelector('video');
    if(v && v.preload==='none'){ v.preload='metadata'; v.load(); }
    IO.unobserve(e.target);
  });
}, {rootMargin:'250px'});

function wireCard(el){
  IO.observe(el);
  const v = el.querySelector('video');
  if(v && !RM){
    el.addEventListener('mouseenter', ()=>{ v.muted=true; v.play().catch(()=>{}); });
    el.addEventListener('mouseleave', ()=>{ v.pause(); try{v.currentTime=0;}catch(_){} });
  }
}

// ---- level 1: tree selection
let selNode=null, selBeat=null;
function selectNode(slug, openBeat){
  selNode=slug; selBeat=null;
  document.querySelectorAll('#rail .tn').forEach(b=>b.classList.toggle('sel', b.dataset.node===slug));
  renderNode();
  $('dossier').innerHTML='';
  if(openBeat!=null) openDossier(openBeat);
}
document.querySelectorAll('#rail .tn').forEach(b=>{
  b.addEventListener('click', ()=>selectNode(b.dataset.node));
});

// ---- level 2: filmstrip
function stripCardHtml(slug, i, bt){
  const best = (BEST[slug]||{})[i];
  const nd = NODES[slug]||{};
  const cs = beatCards(slug, i);
  const SERIOUS = /conflict|retired|ship-manifest|missing on disk|never reached/i;
  const prob = cs.some(c=>(c.problems||[]).some(p=>SERIOUS.test(p)));
  const sp = (nd.ship||{})[i];
  const shipped = !!(sp&&sp.take) || !!(best&&best.shipped);
  const dots = (shipped?'<i class="d-ship" title="shipped pick"></i>':'')
             + (prob?'<i class="d-prob" title="has problems — see dossier"></i>':'');
  const media = best
    ? '<video muted playsinline preload="none" src="'+esc(relurl(best.p))+'" tabindex="-1"></video>'
    : '<div class="ph"><b>'+pad2(i)+'</b><span>no footage</span></div>';
  return '<div class="fcard" role="button" tabindex="0" data-beat="'+i+'" '
    +'aria-label="beat '+i+' — '+esc(bt.title)+'">'
    +'<div class="fmedia">'+media+'</div>'
    +'<div class="fmeta"><span class="fnum">'+pad2(i)+'</span> '
    +'<span class="ftitle" title="'+esc(bt.title)+'">'+esc(bt.title)+'</span>'
    +'<div class="ftc">'+esc(bt.range)+'</div>'
    +'<div class="fdots">'+dots+'</div></div></div>';
}
function renderNode(){
  const nd = NODES[selNode]||{};
  const beats = nd.beats||[];
  const nrec = CARDS.filter(c=>c.node===selNode).length;
  let head = '<h2>'+esc(nd.title||selNode)+'</h2>'
    +'<div class="nmeta"><span class="mono">'+esc(nd.id||'?')+' · '+esc(selNode)+'</span>'
    +' · '+esc(nd.status||'?')+(nd.released?' · released '+esc(nd.released):'')
    +' · '+beats.length+' beat'+(beats.length!==1?'s':'')+' · '+nrec+' record'+(nrec!==1?'s':'')+'</div>';
  if(nd.r1) head += '<p class="r1">'+esc(nd.r1)+'</p>';
  $('nodehead').innerHTML = head;
  const strip = $('strip');
  if(!beats.length){
    strip.innerHTML = '<p class="dnote">no script beats yet — '+nrec+' record'+(nrec!==1?'s':'')+' findable via search</p>';
  } else {
    strip.innerHTML = beats.map((bt,ix)=>stripCardHtml(selNode, ix+1, bt)).join('');
    strip.querySelectorAll('.fcard').forEach(el=>{
      wireCard(el);
      const open = ()=>openDossier(+el.dataset.beat);
      el.addEventListener('click', open);
      el.addEventListener('keydown', e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); open(); } });
    });
  }
  const un = beatCards(selNode, null).length;
  const ul = $('unplacedline');
  if(un){
    ul.innerHTML = '<button class="unplaced" type="button">'+un+' record'+(un!==1?'s':'')+' not tied to a beat</button>';
    ul.querySelector('button').addEventListener('click', ()=>openDossier(null));
  } else {
    ul.innerHTML = '';
  }
}

// ---- level 3: beat dossier
function scriptHtml(text){
  const out=[];
  text.split(/\n\s*\n/).forEach(par=>{
    par=par.trim(); if(!par) return;
    if(par.startsWith('>')){
      const body = par.replace(/^>\s?/gm,'').trim();
      const m = body.match(/^\*\*(.+?):\*\*\s*([\s\S]*)$/);
      if(m){
        let who=m[1], cue='';
        const cm=who.match(/^(.*?)\s*\((.+)\)\s*$/);
        if(cm){ who=cm[1]; cue=cm[2]; }
        out.push('<p class="dlg"><span class="who">'+esc(who)+'</span>'
          +(cue?' <span class="cue">('+esc(cue)+')</span>':'')
          +' — '+esc(stripMd(m[2]))+'</p>');
        return;
      }
    }
    const flat = stripMd(par.replace(/\s*\n\s*/g,' '));
    if(flat.length>260 || /^(restaged|PROVENANCE|Record:)/i.test(flat)){
      out.push('<details class="hist"><summary>production history — '+esc(flat.slice(0,72))
        +'…</summary><p>'+esc(flat)+'</p></details>');
      return;
    }
    out.push('<p class="act">'+esc(flat)+'</p>');
  });
  return out.join('');
}
function stripMd(s){ return String(s).replace(/\*/g,'').replace(/`/g,''); }
function voHtml(nd, beat){
  const vo = beat!=null ? (nd.vo||{})[beat] : null;
  if(!vo){
    return (beat!=null && nd.vo && Object.keys(nd.vo).length)
      ? '<p class="vohead">silent beat — no VO manifest</p>' : '';
  }
  let h='<p class="vohead">VO — '+esc(vo.engine)+' · '+esc(vo.total_s)+'s · '+esc(vo.path)+'</p>';
  h+=(vo.lines||[]).map(l=>'<p class="dlg"><span class="who">'+esc(l[0])+'</span> — '+esc(l[1])+'</p>').join('');
  return h;
}

function kv(label, valueHtml){
  return valueHtml ? '<dt>'+esc(label)+'</dt><dd>'+valueHtml+'</dd>' : '';
}
function recipeLine(c){
  const parts=[];
  if(c.model) parts.push(esc(String(c.model)));
  if(c.seed!=null) parts.push('seed <span class="mono">'+esc(c.seed)+'</span>');
  if(c.steps!=null) parts.push('steps '+esc(c.steps));
  if(c.size) parts.push(esc(c.size));
  if(c.guidance!=null) parts.push('guidance '+esc(c.guidance));
  if(c.seconds!=null) parts.push(esc(c.seconds)+'s');
  if(c.platform) parts.push(esc(c.platform));
  if(c.kind) parts.push(esc(c.kind));
  if(c.era) parts.push(esc(c.era));
  return parts.join(' · ');
}
function clipRowHtml(c){
  const v = bestLocalVideo(c), im = v?null:bestLocalImage(c);
  const media = v
    ? '<video controls muted playsinline preload="metadata" src="'+esc(relurl(v.p))+'"></video>'
    : (im ? '<a href="'+esc(relurl(im.p))+'"><img loading="lazy" src="'+esc(relurl(im.p))+'" alt=""></a>'
          : '<div class="rowph">'+esc(c.era||'no local video')+'</div>');
  let tags='';
  if(c.shipped) tags+=' <span class="tag gold">shipped pick</span>';
  if(c.support) tags+=' <span class="tag">'+esc(c.support)+'</span>';
  let g='<dl class="fgrid">';
  g+=kv('recipe', recipeLine(c)||null);
  if(Object.keys(c.extras||{}).length)
    g+=kv('also recorded', '<span class="xtra">'+esc(Object.entries(c.extras).map(e=>e[0]+': '+e[1]).join(' · '))+'</span>');
  if(c.prompt)
    g+=kv('prompt', '<div class="quote">'+esc(c.prompt)+'</div>'
      +(c.prompt_src?'<div class="qsrc">from '+esc(c.prompt_src)+'</div>':''));
  else
    g+=kv('prompt', '<span class="dnote">no prompt recorded anywhere for this render</span>');
  if(c.negative) g+=kv('negative', '<div class="quote">'+esc(c.negative)+'</div>');
  if(c.files&&c.files.length){
    g+=kv('files', c.files.map(f=>{
      const local=f.where==='local';
      return '<div class="frow">'+(local?'<a href="'+esc(fileurl(f.p))+'">'+esc(f.p)+'</a>':esc(f.p))
        +' · '+fmtB(f.bytes)+(f.sha?' · '+esc(f.sha.slice(0,8)):'')
        +(local?'':' <span class="tag">on farm branch</span>')+'</div>';
    }).join(''));
  }
  const prov=[];
  if(c.spec) prov.push('<div class="frow">spec <a href="'+esc(fileurl(c.spec))+'">'+esc(c.spec)+'</a></div>');
  (c.sidecars||[]).forEach(s=>prov.push('<div class="frow">sidecar <a href="'+esc(fileurl(s))+'">'+esc(s)+'</a></div>'));
  if(c.init) prov.push('<div class="frow">init '+esc(JSON.stringify(c.init))+'</div>');
  (c.refs||[]).forEach(r=>prov.push('<div class="frow">ref '+esc(JSON.stringify(r))+'</div>'));
  if(prov.length) g+=kv('provenance', prov.join(''));
  if(c.queue&&c.queue.length){
    g+=kv('queue', c.queue.map(q=>'<div class="frow">'+esc(q.start||'?')
      +' · rc '+esc(q.rc==null?'?':q.rc)+(q.step?' at '+esc(q.step):'')
      +' · '+esc(q.host||'?')+' · '+esc(q.dur==null?'?':q.dur)+'s</div>').join(''));
  }
  if(c.verdict)
    g+=kv('founder verdict', '<div class="quote">'+esc(c.verdict.state||'')
      +(c.verdict.picked?' · PICKED':'')+(c.verdict.note?'\n'+esc(c.verdict.note):'')+'</div>'
      +'<div class="qsrc">verbatim — episode-progress record</div>');
  if(c.cost&&c.cost.length)
    g+=kv('cost', c.cost.map(r=>'<div class="frow">'+esc(r.date)+' · '+esc(r.provider)
      +' · '+esc(r.model)+' · $'+esc(r.usd)+' · '+esc(r.note)+'</div>').join('')
      +'<div class="qsrc">ledger joins money at (node, beat) granularity — not necessarily this clip’s spend</div>');
  g+='</dl>';
  // disagreements + problems: one amber line, factual
  const notes=[];
  if(c.retired_era) notes.push('retired script era — filename slug ‘'+c.retired_era.slug
    +'’ is not current beat title ‘'+c.retired_era.current_title+'’; current script text/VO do not describe this clip');
  if(c.beat_conflicts&&c.beat_conflicts.length)
    notes.push('beat-number sources disagree: '+c.beat_conflicts.join('; ')+' (precedence applied: '+(c.beat_src||'?')+')');
  (c.problems||[]).forEach(p=>{
    if(!/^retired script era|^beat-number conflict/.test(p)) notes.push(p);
  });
  const amber = notes.length?'<p class="amber">'+esc(notes.join(' · '))+'</p>':'';
  return '<div class="cliprow"><div class="cvid">'+media+'</div>'
    +'<div class="facts"><div class="rid">'+esc(c.id)+tags+'</div>'+g+amber+'</div></div>';
}
function openDossier(beat){
  selBeat=beat;
  document.querySelectorAll('#strip .fcard').forEach(el=>el.classList.toggle('sel', +el.dataset.beat===beat));
  const nd = NODES[selNode]||{};
  const bt = beat!=null ? (nd.beats||[])[beat-1] : null;
  const sp = beat!=null ? (nd.ship||{})[beat] : null;
  let h='<div class="dhead">';
  if(beat!=null)
    h+='<h3>Beat '+pad2(beat)+(bt?' — '+esc(bt.title):'')+'</h3>'
      +(bt&&bt.range?'<span class="tc">'+esc(bt.range)+'</span>':'')
      +(sp&&sp.take?'<span class="bship">SHIPPED</span>':'');
  else
    h+='<h3>Records not tied to a beat</h3>';
  h+='</div>';
  if(sp&&sp.take)
    h+='<p class="shipline">shipped pick: <span class="mono">'+esc(sp.take)+'</span>'
      +(sp.sha256?' · sha <span class="mono">'+esc(sp.sha256.slice(0,8))+'</span>':'')
      +(sp.on_disk?'':' · <span class="amber">named in ship-manifest but NOT in sources/</span>')
      +(sp.verdict?' — '+esc(sp.verdict):'')+'</p>';
  if(bt&&bt.text) h+='<div class="scriptpage">'+scriptHtml(bt.text)+voHtml(nd,beat)+'</div>';
  else if(beat!=null) h+='<div class="scriptpage"><p class="act">no script text for this beat</p>'+voHtml(nd,beat)+'</div>';
  const shot = beat!=null ? (nd.shots||{})[beat] : null;
  if(shot&&shot.prompt)
    h+='<details class="authored"><summary>authored prompt — shots.md registry (may differ from what rendered)</summary><pre>'+esc(shot.prompt)+'</pre></details>';
  const rows = beatCards(selNode,beat).slice().sort((a,b)=>b._mt-a._mt);
  h+='<p class="takecount">'+rows.length+' record'+(rows.length!==1?'s':'')+' on file, newest first</p>';
  const CAP=12;
  h+=rows.slice(0,CAP).map(clipRowHtml).join('');
  if(rows.length>CAP)
    h+='<p id="morerows"><button class="unplaced" type="button">show all '+rows.length+' records</button></p>';
  if(!rows.length) h+='<p class="dnote">nothing rendered for this beat yet</p>';
  // grades are a per-beat finish pass — shown once, not per clip row
  const gr = beat!=null ? (nd.grades||{})[beat] : null;
  if(gr&&gr.length){
    h+='<div class="dsec"><h4>grades — plate finish pass</h4>';
    gr.forEach(g=>{
      h+='<div class="frow">'+esc(g.tag)+' · station '+esc(g.station)
        +' · hue drift '+esc(g.hue_drift_deg)+'° · ink lift '+esc(g.ink_lift)
        +(g.out_sha256?' · out sha '+esc(g.out_sha256.slice(0,8)):'')
        +' · <a href="'+esc(fileurl(g.file))+'">grade json</a>'
        +(g.png?' · <a href="'+esc(fileurl(g.png))+'">graded png</a>':' · graded png not on disk')
        +'</div>';
      if(g.knobs) h+='<div class="xtra">knobs '+esc(JSON.stringify(g.knobs))+' · plate '+esc(g.plate)+'</div>';
    });
    h+='</div>';
  }
  const dz=$('dossier');
  dz.innerHTML=h;
  const mr=dz.querySelector('#morerows');
  if(mr) mr.querySelector('button').addEventListener('click', ()=>{
    mr.insertAdjacentHTML('beforebegin', rows.slice(12).map(clipRowHtml).join(''));
    mr.remove();
  });
  return dz;
}

// ---- search
const qEl=$('q');
let deb;
qEl.addEventListener('input', ()=>{ clearTimeout(deb); deb=setTimeout(doSearch,180); });
document.addEventListener('keydown', e=>{
  if(e.key==='Escape'&&qEl.value){ qEl.value=''; doSearch(); }
});
function resultCardHtml(c){
  const v=bestLocalVideo(c), im=v?null:bestLocalImage(c);
  const nd=NODES[c.node]||{};
  const cap=(nd.id?nd.id:'?')+(c.beat!=null?' · beat '+pad2(c.beat):'');
  const media=v
    ?'<video muted playsinline preload="none" src="'+esc(relurl(v.p))+'" tabindex="-1"></video>'
    :(im?'<img loading="lazy" src="'+esc(relurl(im.p))+'" alt="">'
        :'<div class="ph"><b>·</b><span>'+esc(c.era||'record')+'</span></div>');
  return '<div class="fcard" role="button" tabindex="0" data-i="'+c._i+'">'
    +'<div class="fmedia">'+media+'</div>'
    +'<div class="fmeta"><div class="rlabel" title="'+esc(c.id)+'">'+esc(c.id)+'</div>'
    +'<div class="ftc">'+esc(cap)+'</div></div></div>';
}
function doSearch(){
  const q=qEl.value.trim().toLowerCase();
  const box=$('results');
  if(!q){ box.hidden=true; box.innerHTML=''; return; }
  const hits=CARDS.filter(c=>c._q.includes(q));
  const shown=hits.slice(0,60);
  box.hidden=false;
  box.innerHTML='<div class="rline">'+hits.length+' result'+(hits.length!==1?'s':'')
    +' for “'+esc(q)+'”'+(hits.length>60?' (showing 60)':'')
    +' <button id="clr" type="button" aria-label="clear search">×</button></div>'
    +'<div class="strip">'+shown.map(resultCardHtml).join('')+'</div>';
  $('clr').addEventListener('click', ()=>{ qEl.value=''; doSearch(); });
  box.querySelectorAll('.fcard').forEach(el=>{
    wireCard(el);
    const jump=()=>{
      const c=CARDS[+el.dataset.i];
      if(c.node&&NODES[c.node]){ selectNode(c.node, c.beat!=null?c.beat:null);
        const dz=$('dossier'); if(dz.innerHTML) dz.scrollIntoView({behavior:RM?'auto':'smooth'}); }
    };
    el.addEventListener('click', jump);
    el.addEventListener('keydown', e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); jump(); } });
  });
}

// ---- health footer
$('hline').addEventListener('click', ()=>{
  const hb=$('hbox');
  hb.hidden=!hb.hidden;
  $('hline').setAttribute('aria-expanded', String(!hb.hidden));
});

// ---- boot: hash deep link (#n=<slug>&b=<beat>&q=<query>) else node with most cards
(function(){
  const hp=new URLSearchParams(location.hash.slice(1));
  const counts={};
  CARDS.forEach(c=>{ if(c.node) counts[c.node]=(counts[c.node]||0)+1; });
  let slug=hp.get('n');
  if(!slug||!NODES[slug])
    slug=Object.keys(NODES).sort((a,b)=>(counts[b]||0)-(counts[a]||0))[0];
  const b=hp.get('b');
  selectNode(slug, b!=null&&b!==''?+b:null);
  if(b!=null&&b!==''){ const dz=$('dossier'); if(dz.innerHTML) dz.scrollIntoView(); }
  if(hp.get('q')){ qEl.value=hp.get('q'); doSearch(); }
})();
</script>
</body></html>""" \
        .replace("__GENERATED__", esc(data["generated"])) \
        .replace("__STAT__", esc(stat)) \
        .replace("__HLINE__", esc(hline)) \
        .replace("__QNOTE__", qnote) \
        .replace("__TREE__", tree) \
        .replace("__HEALTH__", healthbox) \
        .replace("__DATA__", payload)


if __name__ == "__main__":
    sys.exit(main())
