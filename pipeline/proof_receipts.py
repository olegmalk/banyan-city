#!/usr/bin/env python3
"""THE RECEIPTS — every per-beat claim on /status traced to the bytes behind it.

The founder, 2026-08-19: *"since you are an ai, you can hallucinate and say
something completely wrong with complete confidence, so i need concrete proof we
are making progress. banyan.city/status isn't shaped very well to show that."*

So the design rule for everything in this module: **a claim a reader cannot
click through to the bytes is not a claim worth printing.** Each beat of episode
2 gets one receipt, and every field on it is read out of a committed file:

  frame     a mid-frame of the take, extracted by ffmpeg into the cut's own
            directory and COMMITTED — see `--frames`. Not extracted at page
            build: the canonical host has no ffmpeg (build_site.poster()'s
            docstring is the scar), so a build-time extract would publish the
            episode as 21 empty rectangles on the one host that matters.
  artifact  the take itself, at the URL the site already publishes it on. The
            demo cut directories carry an index.html, so build_site publishes
            every file in them — the mp4 the reader clicks is the same object
            that was muxed into the cut.
  sha       the take's sha256 as recorded in the cut's own `ingredients:` block
            (written by render_t3 at assembly time), AND recomputed here off the
            bytes in this checkout. Those two agreeing is the strongest single
            fact this page can offer; them disagreeing is a defect the row
            prints rather than hides.
  verdict   quoted VERBATIM out of the `verdict*:` key in the job spec that
            licensed the take, with a blob link to that spec. Never paraphrased
            and never summarised — the whole point is that the reader can open
            the file and find the same sentence.
  landed    which commit last touched that spec, and when.

TWO THINGS ARE GIT-DERIVED AND THEREFORE COMMITTED MEASUREMENTS, exactly like
`pipeline/measured/queue-history.json` (SITE.md, "the queue history's refresh
duty"): the landed dates above, and the 14-day delta counts in the footer line.
A deploy checkout is shallow — GitHub Pages' actions/checkout takes depth 1 —
so `git log` there answers nothing, and a page whose dates silently emptied on
the host that serves banyan.city would be the exact failure this module exists
to prevent. `--write` computes them on a laptop with real history; the builder
reads the JSON and prints its age beside the numbers.

WHAT THIS MODULE WILL NOT DO. It computes no verdict, ranks nothing, promotes
nothing and writes into no cut manifest. If a beat has no verdict block, the
receipt says so in those words: eight beats of episode 2 have ridden five
consecutive cuts with no bar ever answered for them, and printing "no verdict
block exists" is the honest render of that. Inventing a verdict from a filename
or from a clip's mere presence in five cuts is how a bar gets bent to fit the
clip.

Usage:
    python3 pipeline/proof_receipts.py --write     # the git measurement + frames
    python3 pipeline/proof_receipts.py             # print what a build would see
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
import repo_slug  # noqa: E402  one source for "which repo is this"

LEDGER = REPO / "pipeline" / "measured" / "proof-ledger.json"
FRAMES_DIR = "proof"                 # inside the cut's own directory
FRAMES_FILE = "frames.yaml"
LEDGER_CMD = "python3 pipeline/proof_receipts.py --write"
WINDOW_DAYS = 14

# A spec may carry several `verdict*` keys. This order is not arbitrary: a spec
# derived from a parent keeps the parent's blocks RENAMED rather than deleted
# (`*_INHERITED_from_the_crf33_parent_NOT_this_job`), and the picks manifests
# say in as many words to read the `_this_job` keys for that file's own result.
# Anything with INHERITED in the key is skipped outright below.
VERDICT_ORDER = ("verdict_this_job", "verdict", "verdict_cut", "verdict_the_slate")
SPEC_RE = re.compile(r"(pipeline/jobs/[A-Za-z0-9._\-]+\.ya?ml)")
# `- beat: N` / `  sha256: …` pairs out of an assembly manifest. Parsed with the
# yaml module when it is importable and by this pattern when it is not; the
# builder must never lose a whole section to a missing dependency.
_INGREDIENT_RE = re.compile(
    r"^- beat:\s*(\d+)\s*$\n(?:^\s+.*$\n)*?^\s+sha256:\s*([0-9a-f]{64})\s*$",
    re.M)


def _yaml():
    try:
        import yaml
        return yaml
    except Exception:
        return None


def sha256_of(path: Path, chunk: int = 1 << 20) -> str:
    """The file's own sha256, or "" if it cannot be read. Never raises: this runs
    inside a page build, and a page that dies over one unreadable mp4 takes 20
    good receipts down with it."""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            while True:
                b = fh.read(chunk)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()
    except OSError:
        return ""


def blob_url(rel: str, ref: str = "main") -> str:
    return f"{repo_slug.REPO_URL}/blob/{ref}/{rel}"


def commit_url(sha: str) -> str:
    return f"{repo_slug.REPO_URL}/commit/{sha}"


def compare_url(a: str, b: str) -> str:
    return f"{repo_slug.REPO_URL}/compare/{a}...{b}"


# --------------------------------------------------------------- the cut ------

def cut_shas(repo: Path, cut_dir: str) -> dict:
    """{beat -> sha256} for every CLIP in the cut, off the assembly's own record.

    The assembly manifest is `<dir>/<dir>.mp4.meta.yaml`, written by render_t3 at
    mux time. Its `ingredients:` rows are the hashes AS MUXED, which is the only
    hash worth quoting: a hash computed later off a file someone re-encoded would
    agree with itself and prove nothing about what is in the video.
    """
    d = repo / "review" / cut_dir
    meta = d / f"{cut_dir}.mp4.meta.yaml"
    if not meta.is_file():
        return {}
    try:
        text = meta.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    y = _yaml()
    if y is not None:
        try:
            doc = y.safe_load(text) or {}
            out = {}
            for row in doc.get("ingredients") or []:
                if not isinstance(row, dict) or row.get("kind") != "clip":
                    continue
                try:
                    out[int(row["beat"])] = str(row.get("sha256") or "")
                except (KeyError, TypeError, ValueError):
                    continue
            if out:
                return out
        except Exception:
            pass
    # The regex floor. It cannot tell a clip row from an audio row, so it keeps
    # the FIRST hash per beat — which is the clip, because render_t3 writes the
    # clip before the audio for every beat that has one. A beat that is audio
    # only would hash its mp3 here; the sha recheck below compares against the
    # take's own bytes and would print a mismatch rather than a false match.
    return {int(n): h for n, h in _INGREDIENT_RE.findall(text)}


def frame_index(repo: Path, cut_dir: str) -> dict:
    """{beat -> row} from the cut's committed frame manifest, or {}.

    Each row carries the sha256 of the CLIP the frame came out of. That is what
    lets the builder refuse a stale picture: if the clip in the slot changed and
    nobody re-ran `--frames`, the recorded clip hash no longer matches the cut's
    and the receipt says the frame is stale instead of showing last week's shot
    under this week's filename.
    """
    p = repo / "review" / cut_dir / FRAMES_DIR / FRAMES_FILE
    y = _yaml()
    if not p.is_file() or y is None:
        return {}
    try:
        doc = y.safe_load(p.read_text(encoding="utf-8", errors="replace")) or {}
    except Exception:
        return {}
    out = {}
    for row in doc.get("frames") or []:
        if not isinstance(row, dict):
            continue
        try:
            out[int(row["beat"])] = row
        except (KeyError, TypeError, ValueError):
            continue
    return out


# -------------------------------------------------------------- the specs -----

def spec_path(field: str) -> str:
    """The `pipeline/jobs/*.yaml` a picks row cites, or "".

    The picks manifests write the citation as prose — "pipeline/jobs/x.yaml —
    verdict PASS, verdict_cut CUT-PREFERRED" — so the path is extracted and the
    prose after it is DISCARDED. The verdict printed on the page is read out of
    the spec itself, never out of the sentence that points at it, because a
    paraphrase written by the lane that wanted the take in the cut is exactly the
    claim a reader has no way to check.
    """
    m = SPEC_RE.search(str(field or ""))
    return m.group(1) if m else ""


def spec_verdicts(repo: Path, rel: str) -> list:
    """Every `verdict*:` string the spec carries, verbatim, in reading order.

    ALL OF THEM AND NOT THE FIRST ONE. Beat 07's spec answers its bar across
    three keys — `verdict: PASS`, `verdict_cut: CUT-PREFERRED`, and
    `verdict_the_slate:` explaining that the beat's `done_when` is met — so a
    page quoting only the first would print the word "PASS" and drop the two
    sentences that say what passed. VERDICT_ORDER goes first because a derived
    spec's `_this_job` key is the one that describes THIS file's run; the rest
    follow alphabetically so two builds order them identically.

    Only string values: `verdict_measured:` is a mapping of per-clause readings
    and belongs in the spec, not in a quote. Keys carrying INHERITED are another
    job's numbers under a name that says so, and quoting one here would
    attribute a parent's result to this file.
    """
    p = repo / rel
    y = _yaml()
    if not p.is_file() or y is None:
        return []
    try:
        doc = y.safe_load(p.read_text(encoding="utf-8", errors="replace")) or {}
    except Exception:
        return []
    if not isinstance(doc, dict):
        return []
    keys = [k for k in doc
            if isinstance(k, str) and k.startswith("verdict")
            and "INHERITED" not in k and isinstance(doc[k], str) and doc[k].strip()]
    ordered = ([k for k in VERDICT_ORDER if k in keys]
               + sorted(k for k in keys if k not in VERDICT_ORDER))
    return [(k, " ".join(str(doc[k]).split())) for k in ordered]


def call_word(verdicts: list) -> str:
    """PASS / FAIL / "" — read off the START of the verdict text and nowhere else.

    Mechanical on purpose. The spec's own sentence either opens with the word or
    it does not; anything cleverer would be this page deciding what a lane's
    paragraph amounts to, which is the one job it must never do. A verdict that
    opens some other way gets no chip and the reader gets the sentence.
    """
    for _k, text in verdicts:
        head = text.strip().upper()
        for word in ("PASS", "FAIL"):
            if head.startswith(word):
                return word
    return ""


# ------------------------------------------------------------- the receipts ---

def receipts(cut: dict, repo: Path = REPO, ledger: dict | None = None) -> list:
    """One receipt per beat of `cut`, in beat order. [] when there is no cut.

    `cut` is `build_sim.read_latest_cut()`'s shape. Nothing here reaches the
    network, and every failure degrades to a field that says what is missing —
    the caller renders "no verdict block exists" and "frame not extracted" as
    facts, because they are.
    """
    rows = (cut or {}).get("beats") or []
    cut_dir = str((cut or {}).get("dir") or "")
    if not rows or not cut_dir:
        return []
    shas = cut_shas(repo, cut_dir)
    frames = frame_index(repo, cut_dir)
    landed = ((ledger or read_ledger()).get("landed") or {})
    out = []
    for r in sorted(rows, key=lambda b: int(b.get("n") or 0)):
        n = int(r.get("n") or 0)
        take = str(r.get("take") or "")
        rec = {"n": n, "slug": str(r.get("slug") or ""), "take": take,
               "why": str(r.get("why") or ""), "slate": not take,
               "artifact": "", "artifact_gh": "", "bytes": 0,
               "sha": str(shas.get(n) or ""), "sha_recomputed": "",
               "sha_check": "absent", "frame": "", "frame_why": "",
               "spec": "", "spec_gh": "", "verdicts": [], "call": "",
               "verdict_key": "", "verdict": "",
               "landed_at": "", "landed_sha": "", "landed_url": "",
               "landed_what": ""}
        if take:
            rel = f"review/{cut_dir}/sources/{take}"
            src = repo / rel
            rec["artifact"] = rel
            rec["artifact_gh"] = blob_url(rel)
            if src.is_file():
                rec["bytes"] = src.stat().st_size
                rec["sha_recomputed"] = sha256_of(src)
                if rec["sha"] and rec["sha_recomputed"]:
                    rec["sha_check"] = ("match" if rec["sha_recomputed"] == rec["sha"]
                                        else "differs")
                elif rec["sha_recomputed"]:
                    # The bytes are here and the assembly recorded no hash for
                    # this beat. Not a match and not a mismatch — an unrecorded
                    # ingredient, which is its own thing and is named as one.
                    rec["sha_check"] = "unrecorded"
            else:
                rec["sha_check"] = "missing"
            fr = frames.get(n) or {}
            fname = str(fr.get("frame") or "")
            if fname and (repo / "review" / cut_dir / FRAMES_DIR / fname).is_file():
                if rec["sha"] and str(fr.get("clip_sha256") or "") != rec["sha"]:
                    rec["frame_why"] = ("the committed frame was cut from a "
                                        "different take — re-run " + LEDGER_CMD
                                        .replace("--write", "--frames"))
                else:
                    rec["frame"] = f"review/{cut_dir}/{FRAMES_DIR}/{fname}"
                    rec["frame_at"] = fr.get("at_seconds")
                    # Shipped as width/height attributes so 18 thumbnails cannot
                    # reflow the strip as they load. 0 when the manifest predates
                    # the pair, in which case the page omits the attributes
                    # rather than guessing an aspect ratio.
                    rec["frame_w"] = int(fr.get("width") or 0)
                    rec["frame_h"] = int(fr.get("height") or 0)
            else:
                rec["frame_why"] = "no frame committed for this take"
        spec = spec_path(r.get("verdict"))
        if spec:
            rec["spec"] = spec
            rec["spec_gh"] = blob_url(spec)
            rec["verdicts"] = spec_verdicts(repo, spec)
            rec["call"] = call_word(rec["verdicts"])
            if rec["verdicts"]:
                rec["verdict_key"], rec["verdict"] = rec["verdicts"][0]
        key = spec or take
        got = landed.get(key) or {}
        if got:
            rec["landed_at"] = str(got.get("date") or "")[:10]
            rec["landed_sha"] = str(got.get("sha") or "")
            rec["landed_what"] = str(got.get("what") or "")
            if rec["landed_sha"]:
                rec["landed_url"] = commit_url(rec["landed_sha"])
        out.append(rec)
    return out


def sha_tally(recs: list) -> dict:
    """How many takes re-hashed clean, and how many did not. The one claim on
    this page that a reader can falsify with `shasum -a 256`, so it is counted
    rather than asserted."""
    t = {"match": 0, "differs": 0, "missing": 0, "unrecorded": 0, "absent": 0}
    for r in recs:
        if r.get("slate"):
            continue
        t[r.get("sha_check", "absent")] = t.get(r.get("sha_check", "absent"), 0) + 1
    t["takes"] = sum(1 for r in recs if not r.get("slate"))
    return t


# ---------------------------------------------------------------- the ledger --

def read_ledger(path: Path = LEDGER) -> dict:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return doc if isinstance(doc, dict) else {}
    except (OSError, ValueError):
        return {}


def _git(repo: Path, *args, timeout: int = 30) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def _count_added(repo: Path, pattern: str, *pathspec, since: str) -> int:
    """Added lines matching `pattern` in `pathspec` over the window.

    `-U0` because the count must not see a line that merely moved into a diff
    hunk as context. This is a DIFF measurement and it is labelled as one on the
    page: it counts what the repository's history did, not what is true now.
    """
    diff = _git(repo, "log", f"--since={since}", "-U0", "-p", "--", *pathspec,
                timeout=180)
    rx = re.compile(pattern, re.M)
    return len(rx.findall(diff))


def measure(repo: Path = REPO, days: int = WINDOW_DAYS) -> dict:
    """The git-derived half: landed dates + the 14-day deltas. Needs real history.

    Returns a dict shaped for the JSON. A shallow checkout produces small or
    empty numbers, so `shallow: true` is recorded and the writer refuses rather
    than committing a measurement taken through a keyhole.
    """
    since = f"{days}.days"
    shallow = _git(repo, "rev-parse", "--is-shallow-repository").strip() == "true"
    # SHALLOW IS NOT THE QUESTION — WHETHER THE WINDOW IS WHOLE IS. This Mac's
    # checkout reports shallow (there is a `.git/shallow` graft) and still holds
    # 2,093 commits reaching back months, so refusing on shallowness alone
    # refused a measurement it could take perfectly well. The real test is
    # whether anything OLDER than the window exists in this history: if it does,
    # every commit inside the window is present and the counts below are
    # complete. If it does not, the graft boundary is inside the window and the
    # counts are a floor, which is what `covers_window: false` says.
    covers = bool(_git(repo, "log", f"--until={since}", "-1", "--format=%h").strip())
    head = _git(repo, "rev-parse", "HEAD").strip()[:9]
    # The oldest commit still inside the window, as the compare range's base.
    win = [ln for ln in _git(repo, "log", f"--since={since}",
                             "--format=%h %cI").splitlines() if ln.strip()]
    base = win[-1].split()[0] if win else ""
    verdicts = _count_added(repo, r"^\+\s*verdict[a-z_]*\s*:", "pipeline/jobs",
                            since=since)
    rulings = _count_added(repo, r"^\+\s*resolved\s*:", "review/inbox.yaml",
                           since=since)
    cuts = []
    for ln in _git(repo, "log", f"--since={since}", "--diff-filter=A",
                   "--format=%h\t%cI", "--name-only", "--",
                   "review/ep2-demo-*/ep2-demo-*.mp4").splitlines():
        if "/" in ln and ln.endswith(".mp4"):
            cuts.append(ln.strip())
    doc = {"generated_by": LEDGER_CMD, "window_days": days, "shallow": shallow,
           "covers_window": covers,
           "head": head, "range_base": base, "commits_in_window": len(win),
           "verdict_lines_added": verdicts, "resolved_blocks_added": rulings,
           "cuts_shipped": len(cuts), "cut_files": sorted(cuts),
           "generated": _git(repo, "log", "-1", "--format=%cI").strip()[:10],
           "landed": {}}
    return doc


def measure_landed(repo: Path, cut: dict) -> dict:
    """{spec-or-take -> {sha, date, what}} for one cut's beats.

    A spec's landed commit is the last commit that touched the spec, and that is
    stated in those words on the page rather than as "the verdict commit": a
    verdict is appended to a spec as the spec's final edit, so the two coincide
    in practice, and claiming the stronger thing would be a claim the query does
    not actually make.
    """
    out = {}
    for r in (cut or {}).get("beats") or []:
        take = str(r.get("take") or "")
        spec = spec_path(r.get("verdict"))
        if spec:
            ln = _git(repo, "log", "-1", "--format=%h\t%cI", "--", spec).strip()
            what = "last commit that touched the spec"
            key = spec
        elif take:
            # The take's FIRST appearance anywhere in the tree, by basename: the
            # file is copied into each new cut's sources/, so a query scoped to
            # this cut's directory would date every carry-forward to today and
            # quietly turn a five-day-old clip into fresh work.
            lines = [x for x in _git(
                repo, "log", "--diff-filter=A", "--format=%h\t%cI", "--",
                f"*{take}").splitlines() if x.strip()]
            ln = lines[-1].strip() if lines else ""
            what = "first commit that added this take"
            key = take
        else:
            continue
        if not ln or "\t" not in ln:
            continue
        sha, when = ln.split("\t", 1)
        out[key] = {"sha": sha.strip(), "date": when.strip()[:10], "what": what}
    return out


# ---------------------------------------------------------------- the frames --

def extract_frames(repo: Path, cut: dict, width: int = 240) -> dict:
    """A committed mid-frame per take, plus the manifest that dates them.

    MID-FRAME AND NOT THE FIRST FRAME. Every one of these clips is i2v: frame 1
    IS the init plate, so a first-frame thumbnail would show the still the clip
    was conditioned on and tell a reader nothing about what the motion did. The
    middle of the clip is the only sample point that is evidence.
    """
    ff = shutil.which("ffmpeg")
    fp = shutil.which("ffprobe")
    if not ff:
        return {"ok": False, "why": "no ffmpeg on this machine"}
    cut_dir = str(cut.get("dir") or "")
    outdir = repo / "review" / cut_dir / FRAMES_DIR
    outdir.mkdir(parents=True, exist_ok=True)
    shas = cut_shas(repo, cut_dir)
    rows, made = [], 0
    for r in sorted(cut.get("beats") or [], key=lambda b: int(b.get("n") or 0)):
        n = int(r.get("n") or 0)
        take = str(r.get("take") or "")
        if not take:
            continue
        src = repo / "review" / cut_dir / "sources" / take
        if not src.is_file():
            continue
        dur = 0.0
        if fp:
            try:
                dur = float(subprocess.run(
                    [fp, "-v", "error", "-show_entries", "format=duration",
                     "-of", "csv=p=0", str(src)], capture_output=True, text=True,
                    encoding="utf-8", errors="replace",
                    timeout=60).stdout.strip() or 0)
            except (ValueError, OSError, subprocess.SubprocessError):
                dur = 0.0
        at = round(dur / 2.0, 2) if dur > 0.2 else 0.5
        dst = outdir / ("b%02d.jpg" % n)
        try:
            subprocess.run([ff, "-loglevel", "error", "-y", "-ss", str(at),
                            "-i", str(src), "-frames:v", "1",
                            "-vf", f"scale={width}:-2", "-q:v", "5", str(dst)],
                           check=True, timeout=120)
        except (OSError, subprocess.SubprocessError):
            continue
        if not (dst.is_file() and dst.stat().st_size):
            continue
        made += 1
        # The frame's own pixel size, recorded so the page can ship width/height
        # attributes. Without them 18 thumbnails reflow the strip as they arrive,
        # and the founder reads this on a phone.
        w = h = 0
        if fp:
            try:
                dims = subprocess.run(
                    [fp, "-v", "error", "-select_streams", "v:0", "-show_entries",
                     "stream=width,height", "-of", "csv=p=0:s=x", str(dst)],
                    capture_output=True, text=True, encoding="utf-8",
                    errors="replace", timeout=30).stdout.strip()
                w, h = (int(x) for x in dims.split("x")[:2])
            except (ValueError, OSError, subprocess.SubprocessError):
                w = h = 0
        rows.append({"beat": n, "take": take, "frame": dst.name,
                     "width": w, "height": h,
                     "at_seconds": at, "clip_duration_s": round(dur, 2),
                     "clip_sha256": shas.get(n) or sha256_of(src),
                     "frame_sha256": sha256_of(dst),
                     "frame_bytes": dst.stat().st_size})
    y = _yaml()
    if y is None:
        return {"ok": False, "why": "no yaml module — manifest not written"}
    head = (
        "# MID-FRAMES OF THE TAKES IN %s — committed on purpose.\n"
        "#\n"
        "# Written by `python3 pipeline/proof_receipts.py --frames`. The status\n"
        "# page shows these beside each beat's receipt; it does NOT extract\n"
        "# frames itself, because the canonical host has no ffmpeg and would\n"
        "# publish the episode as empty rectangles on the one host that\n"
        "# matters (build_site.poster()'s docstring is that scar).\n"
        "#\n"
        "# `clip_sha256` is the guard, not decoration: the page compares it to\n"
        "# the sha the cut's own `ingredients:` block records for that beat, and\n"
        "# prints the frame as STALE rather than showing it when the two differ.\n"
        "# A swapped take with an unrefreshed frame is exactly the defect the\n"
        "# review pages already learned the hard way (SITE.md, \"a review page\n"
        "# shows the CURRENT best take of a beat\").\n"
        "#\n"
        "# The frame is the MIDDLE of the clip. These are all i2v takes, so\n"
        "# frame 1 is the init plate — a first-frame thumbnail would show the\n"
        "# still the clip was conditioned on and say nothing about the motion.\n" % cut_dir)
    doc = {"cut": cut_dir, "generated_by": "pipeline/proof_receipts.py --frames",
           "frames": rows}
    (outdir / FRAMES_FILE).write_text(
        head + y.safe_dump(doc, sort_keys=False, allow_unicode=True),
        encoding="utf-8")
    return {"ok": True, "made": made, "dir": str(outdir)}


# ------------------------------------------------------------------- the CLI --

def _latest_cut(repo: Path) -> dict:
    import build_sim
    return build_sim.read_latest_cut(repo)


def main(argv: list) -> int:
    repo = REPO
    cut = _latest_cut(repo)
    if not cut:
        print("! no cut manifest found under review/ep2-demo-*/sources/picks-*.yaml")
        return 1
    want_frames = "--frames" in argv or "--write" in argv
    want_ledger = "--ledger" in argv or "--write" in argv

    if want_frames:
        got = extract_frames(repo, cut)
        if got.get("ok"):
            print(f"✓ {got['made']} frames + {FRAMES_FILE} → {got['dir']}")
            # THE STEP THAT IS EASY TO MISS AND SILENTLY BREAKS THE PAGE.
            # `.gitignore` carries `review/**/*.jpg` on purpose (render media
            # pulled off the farm boxes must not ride in on a `git add -A`), so
            # these frames need `-f` exactly like every mp4 in the cut beside
            # them. Without it the manifest commits, the pictures do not, and
            # /status ships eighteen broken images — which is how this was found:
            # qa_local's link sweep failed the build, before anyone saw the page.
            print(f"  next: git add -f review/{cut['dir']}/{FRAMES_DIR}/*.jpg "
                  f"review/{cut['dir']}/{FRAMES_DIR}/{FRAMES_FILE}\n"
                  f"  (review/**/*.jpg is gitignored — an unforced add commits "
                  f"the manifest and none of the pictures)")
        else:
            print(f"! frames not written — {got.get('why')}")

    if want_ledger:
        doc = measure(repo)
        if not doc.get("covers_window"):
            print(f"! this checkout's history does not reach past "
                  f"{doc['window_days']} days — the counts would be a floor, not "
                  f"a measurement. Refusing to write one taken through a keyhole "
                  f"(deepen with `git fetch --unshallow`).")
            return 2
        doc["landed"] = measure_landed(repo, cut)
        doc["cut"] = cut["dir"]
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n",
                          encoding="utf-8")
        print(f"✓ {LEDGER.relative_to(repo)} — {doc['verdict_lines_added']} verdict "
              f"lines, {doc['cuts_shipped']} cuts, {doc['resolved_blocks_added']} "
              f"resolved blocks over {doc['window_days']}d "
              f"({doc['commits_in_window']} commits, {doc['range_base']}..{doc['head']})")

    recs = receipts(cut, repo)
    tally = sha_tally(recs)
    print(f"\n{cut['dir']} — {len(recs)} beats, {tally['takes']} takes")
    for r in recs:
        if r["slate"]:
            print("  %02d %-16s SLATE" % (r["n"], r["slug"][:16]))
            continue
        print("  %02d %-16s %-8s sha %-8s %s %s" % (
            r["n"], r["slug"][:16], "frame" if r["frame"] else "NO-FRAME",
            r["sha_check"], (r["verdict_key"] or "no-verdict-block"),
            r["landed_at"] or "no-date"))
    print(f"\nsha recheck: {tally}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
