#!/usr/bin/env python3
"""THE PATH TO EPISODE 2 — what happened, what is happening, what is planned.

Founder, 2026-08-20: "the full path of making the episode with estimated time
for each part, viewable on the website."

He asked for the whole path with a time against each part. This builds it from
the files that already know the answer, at site-build time, and it hand-types
none of it. That constraint is the whole design and it is not fussiness: a
status paragraph is correct for exactly as long as nobody does any work, and
this project assembled five episode-2 cuts in five days. Every count, every
scene name and every minute figure below comes out of a file on disk.

WHERE EACH NUMBER COMES FROM
  STATE.md `## <date> — SHIP ORDER`      the ship order and the upgrade cutoff
  review/ep2-ship-*/sources/ship-manifest.yaml   the ship cut, when it exists
  review/ep2-ship-*/*.mp4.meta.yaml      the ship cut's own record until then
  review/ep2-picks/cut-readiness-*.yaml  per-scene status and the named faults
  pipeline/measured/queue-history.json   1,045 dated jobs with per-job seconds
  pipeline/build_status.py STEPS         the assembly figure, measured on ep1

THREE TENSES, because "status" with no tense is the thing he could not read.
What happened is the last day off the job records. What is happening is the
cut as it stands right now. What is planned is the five remaining steps, each
one with a state, a named owner and a time.

THE TWO CLOCKS RULE APPLIES HERE TOO (episode_eta.py's header argues it at
length, charts._epl_lines draws it). Machine minutes are measured and printed.
A person deciding is not a quantity — the same call in this project has taken
four minutes and it has taken three days — so the author's steps are named and
never added to the machine's. Nothing here produces a finish date.

MEASURED vs ESTIMATE IS PRINTED, NEVER IMPLIED. Every figure carries one of two
words. "Measured" means it is the median of dated runs in a file you can open;
the sample size travels with it. "Estimate" means nobody has measured it and
this page says so rather than dressing a guess as a reading.

WHAT IT DOES WHEN THE SHIP LANE HAS NOT LANDED. The ship manifest is written by
another lane and may not exist when this builds. Then the section renders the
truthful pending state — the order, the cutoff, the steps, and a line saying
the manifest is not there yet — off the readiness ledger alone. It never
crashes and it never invents a cut. Same rule one level down: any single read
that fails costs its own line, not the section.

Read-only, repo files only, no network and no `git`: a deploy checkout is one
commit deep and has neither refs nor a `gh` CLI.

    python3 pipeline/ship_path.py        # the section's data, as text
"""
import datetime
import json
import re
import statistics
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The ship candidate's directories. `ep2-demo-*` is the daily bench cut and is
# NOT this: the ship dir is the one the ship order names.
SHIP_GLOB = "ep2-ship-*"
READINESS_GLOB = "cut-readiness-*.yaml"
READINESS_DIR = "review/ep2-picks"
QUEUE_HISTORY = "pipeline/measured/queue-history.json"
STATE_FILE = "STATE.md"
EPISODE = 2

# The window the digest reports over. A ROLLING DAY, not "since midnight", for
# the same reason build_sim.finished_recent gives: a page read at 00:30 that
# says "nothing today" about a night of work is true and useless.
DIGEST_HOURS = 24

# The heading STATE.md writes for a ship order, and the one line inside it that
# carries a time. Anchored on the heading rather than on free prose so a later
# entry about shipping something else cannot be read as this order. Two spellings
# because the founder has used two — `SHIP ORDER` on 08-20, `SHIP TODAY` on
# 08-21 — and a heading shape this file does not know reads as no order at all,
# which would silently drop the newest one.
SHIP_HEAD = re.compile(
    r"^##\s*(\d{4}-\d{2}-\d{2})[^\n]*?[-—–]\s*SHIP (?:ORDER|TODAY)\b(.*)$", re.M)
CUTOFF_RE = re.compile(r"cutoff:.*?by\s+(\d{1,2}:\d{2})\s+(\d{4}-\d{2}-\d{2})",
                       re.I | re.S)

# What the author's own step costs. THE ONLY NUMBER ON THIS PAGE NOBODY HAS
# MEASURED, and it is labelled as an estimate everywhere it appears. The watch
# itself is measured — it is the cut's own duration — but how long a person
# spends answering the cards beside it is the other clock, and this file's whole
# argument is that the other clock is not a quantity. Ten minutes is an
# allowance so the step has a size on the page; it is not a prediction.
WATCH_ALLOWANCE_MIN = 10


def _yaml():
    import yaml
    return yaml


def _load_yaml(path: Path):
    """A yaml file, or None. Absent, unreadable and malformed are one answer."""
    try:
        return _yaml().safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _dt(s):
    """An ISO stamp from the job records -> aware datetime, or None."""
    try:
        d = datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)


def one_sentence(text, limit: int = 150) -> str:
    """A ledger's own first sentence, whitespace-collapsed, never re-worded.

    The readiness ledger writes a paragraph per scene, for a reader deciding
    from it. The page needs the headline. A run of dots is an elision and not a
    full stop — the same rule build_sim.first_sentence applies everywhere else
    on this site.
    """
    t = re.sub(r"\.{2,}", "…", " ".join(str(text or "").split()))
    if not t:
        return ""
    head = t.split(". ")[0].rstrip(" .")
    if len(head) > limit:
        head = head[:limit].rsplit(" ", 1)[0].rstrip(" ,;:—-") + "…"
    return head


def minutes_words(minutes) -> str:
    """'6 min' · 'about 1.8 h' — build_sim.hours_words' wording, one source of
    phrasing for two sections so they cannot come to disagree about a duration."""
    try:
        m = float(minutes)
    except (TypeError, ValueError):
        return ""
    if m <= 0:
        return ""
    if m < 1:
        return "under a minute"
    return f"{round(m)} min" if m < 90 else f"about {m / 60:.1f} h"


def secs_words(seconds) -> str:
    """'24 s' · '6.2 min' — a duration in the unit it was actually timed in.

    minutes_words ROUNDS TO THE WHOLE MINUTE and that is right for a step's
    headline figure and wrong for a range: the day's motion jobs run 6.15 to
    6.40 minutes, which minutes_words printed as "6 min–6 min each" — a range
    with no width, published beside the word measured.
    """
    try:
        s = float(seconds)
    except (TypeError, ValueError):
        return ""
    if s <= 0:
        return ""
    if s < 90:
        return f"{round(s)} s"
    if s < 5400:
        return f"{s / 60:.1f} min"
    return f"{s / 3600:.1f} h"


def span_words(low_s, high_s) -> str:
    """'6.2–6.4 min' — a low-to-high range, or "" when either end is unusable."""
    lo, hi = secs_words(low_s), secs_words(high_s)
    if not lo or not hi:
        return ""
    # One unit for the pair, so "24 s–1.2 min" cannot happen: the reader is
    # comparing two numbers and they must be in the same units to compare.
    if lo.split()[-1] != hi.split()[-1]:
        return f"{lo}–{hi}"
    return f"{lo.split()[0]}–{hi}"


def gap_words(delta: datetime.timedelta) -> str:
    """A future gap in the words a person uses. Negative is the caller's problem
    — a countdown that has run out is a different sentence, not a negative one."""
    mins = int(delta.total_seconds() // 60)
    if mins <= 0:
        return "none"
    h, m = divmod(mins, 60)
    if h >= 24:
        d, h = divmod(h, 24)
        return f"{d}d {h}h" if h else f"{d}d"
    return f"{h}h {m:02d}m" if h else f"{m} min"


# ---------------------------------------------------------------- the order ---
def _utc_stamp(value):
    """"YYYY-MM-DD HH:MM" -> aware UTC datetime, or None. Nothing is guessed."""
    try:
        return datetime.datetime.strptime(
            str(value), "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return None


def _end_of_day(value):
    """The last instant of "YYYY-MM-DD" in UTC, or None.

    A DAY IS NOT A CLOCK. The 08-21 order names a day — "finish it today" — and
    the only honest way to ask "has the target passed" of a day is to ask it of
    the day's end. Reading it as midnight-at-the-start would have the page
    declaring a slip before breakfast.
    """
    try:
        d = datetime.datetime.strptime(str(value), "%Y-%m-%d")
    except (ValueError, TypeError):
        return None
    return d.replace(hour=23, minute=59, second=59,
                     tzinfo=datetime.timezone.utc)


def read_ship_order(repo: Path = None) -> dict:
    """The founder's ship order and the day or clock in it. {} if none.

    Shape-checked rather than trusted: an order whose block carries no parsable
    time returns the order WITHOUT one, and the page then says there is no time
    on record instead of inventing a deadline. A half-read record must never
    become a countdown.

    TWO SHAPES, because the orders have two shapes. The 2026-08-20 order set an
    upgrade CUTOFF — a clock inside the day, after which nothing new entered the
    cut. The 2026-08-21 order that replaced it sets a TARGET DAY — "you must aim
    to finish it today" — with no cutoff at all. Both are read; neither is
    invented from the other, and a page holding a target day never prints a
    countdown to a cutoff nobody set.

    THE ZONE IS NOT IN THE RECORD. STATE.md writes "12:00" and names no
    timezone. This reads it as UTC because every other stamp this repo
    publishes is UTC, and the page SAYS it did so — a clock printed without
    saying which clock it is, is the defect this project keeps re-finding.
    """
    repo = repo or REPO
    doc = _load_yaml(repo / SHIP_PATH_MEASURED)
    row = doc.get("order") if isinstance(doc, dict) else None
    if isinstance(row, dict) and row.get("date"):
        # THE TRANSCRIBED RECORD WINS, and the reason is the build guard rather
        # than a preference. STATE.md is appended to several times a day and is
        # deliberately NOT a site input (pipeline/vercel-ignore-build.sh says so
        # at length); a page whose countdown lived there would either force a
        # rebuild per append or go stale between them. The transcription lives
        # in a file that IS an input, so the page moves when the order does.
        out = {"date": str(row["date"]), "headline": str(row.get("headline") or ""),
               "words": " ".join(str(row.get("words") or "").split()),
               "supersedes": " ".join(str(row.get("supersedes") or "").split()),
               "cutoff": None, "cutoff_text": "",
               "target_date": str(row.get("target_date") or ""),
               "target_end": _end_of_day(row.get("target_date")),
               "plates_by": _utc_stamp(row.get("plates_by_utc")),
               "plates_by_text": ""}
        if out["plates_by"]:
            out["plates_by_text"] = str(row["plates_by_utc"]).split()[1]
        out["cutoff"] = _utc_stamp(row.get("cutoff_utc"))
        if out["cutoff"]:
            hh, dd = str(row["cutoff_utc"]).split()[1], str(row["cutoff_utc"]).split()[0]
            out["cutoff_text"] = f"{hh} on {dd}"
        return out
    try:
        text = (repo / STATE_FILE).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}
    heads = list(SHIP_HEAD.finditer(text))
    if not heads:
        return {}
    m = heads[-1]                       # the newest order wins
    body = text[m.end():]
    nxt = re.search(r"^## ", body, re.M)
    block = body[:nxt.start()] if nxt else body
    # The heading is written `SHIP ORDER (founder): episode 2 ships within 24h`.
    # Who gave the order is already the sentence the page wraps this in, so the
    # parenthetical is dropped rather than printed twice in one line.
    head = re.sub(r"^\s*\([^)]*\)\s*", "", m.group(2)).strip(" :—-")
    out = {"date": m.group(1), "headline": head,
           "words": " ".join(block.split()), "supersedes": "",
           "cutoff": None, "cutoff_text": "", "target_date": "",
           "target_end": None, "plates_by": None, "plates_by_text": ""}
    c = CUTOFF_RE.search(block)
    if c:
        try:
            out["cutoff"] = datetime.datetime.strptime(
                f"{c.group(2)} {c.group(1)}", "%Y-%m-%d %H:%M"
            ).replace(tzinfo=datetime.timezone.utc)
            out["cutoff_text"] = f"{c.group(1)} on {c.group(2)}"
        except ValueError:
            out["cutoff"] = None
    return out


# ------------------------------------------------------- the design patch wave ---
def read_patch_wave(repo: Path = None) -> dict:
    """The scenes being re-rendered to the ruled goblin design. {} if none.

    WHICH SCENES IS THE ONE RENDER FACT NO JOB RECORD HOLDS. A job knows its own
    beat and its own seconds; nothing in the queue knows that seven particular
    scenes failed a design audit. So the list is transcribed into
    `pipeline/measured/ship-path.yaml` with the audit block that produced it
    named, and this reads it. An absent or shapeless block returns {} and the
    page describes the wave as unlisted rather than guessing at its size.
    """
    repo = repo or REPO
    doc = _load_yaml(repo / SHIP_PATH_MEASURED)
    row = doc.get("patch_wave") if isinstance(doc, dict) else None
    if not isinstance(row, dict):
        return {}
    beats = sorted({int(n) for n in (row.get("beats") or [])
                    if str(n).strip().lstrip("-").isdigit()})
    if not beats:
        return {}
    return {"beats": beats,
            "reference": sorted({int(n) for n in (row.get("reference_beats") or [])
                                 if str(n).strip().lstrip("-").isdigit()}),
            "stamp": str(row.get("stamp") or "").strip(),
            "source": " ".join(str(row.get("source") or "").split()),
            "standard": " ".join(str(row.get("standard") or "").split())}


def wave_progress(wave: dict, cut: dict) -> dict:
    """How many of the wave's scenes have actually landed in the ship cut.

    DERIVED FROM THE CUT, NEVER DECLARED. The manifest names one take file per
    scene and a take re-rendered for this wave carries the wave's date stamp in
    its own filename, so a scene counts as swapped when the manifest says so and
    at no other moment. Nobody ticks a box here; the render lane writing the
    manifest moves this page, and if it writes nothing the page reports nothing
    landed rather than reporting progress it cannot see.

    A SUBSTRING TEST WAS WRONG AND THE BUG IS WORTH KEEPING WRITTEN DOWN. Takes
    carry two kinds of number: a date stamp `-0821` and a SEED `s20260821`. The
    first version asked whether "0821" appeared anywhere in the filename and so
    read `03-bad-cover-LTX-midend-s20260821-0820.mp4` — a take from the 20th,
    seeded 20260821 — as a scene the wave had already landed. The stamp must sit
    behind a hyphen and end there, which is how the render lane writes it.

    With no stamp on record every scene reads as still to come — the safe
    direction, because the failure it produces is a page under-claiming.
    """
    beats = (wave or {}).get("beats") or []
    stamp = (wave or {}).get("stamp") or ""
    takes = {b["n"]: (b.get("take") or "") for b in (cut or {}).get("beats", [])}
    pat = re.compile("-" + re.escape(stamp) + r"(?![0-9])") if stamp else None
    done = [n for n in beats if pat and pat.search(str(takes.get(n, "")))]
    return {"beats": beats, "swapped": done,
            "remaining": [n for n in beats if n not in done],
            "stamp": stamp, "checked": bool(takes)}


# ------------------------------------------------------------- the ship cut ---
def read_ship_cut(repo: Path = None) -> dict:
    """The ship candidate as it stands. {} when the ship lane has landed nothing.

    TWO SOURCES, IN THIS ORDER, and the page prints which one it read. The ship
    lane's `sources/ship-manifest.yaml` is the intended record and wins whenever
    it exists. Until it does, the assembled cut's OWN `*.mp4.meta.yaml` — which
    render_t3 writes and cannot write without assembling — already lists every
    scene, its clip and its slates. Reading the second is not a guess at the
    first: it is the same facts from the file that produced the video.

    Newest by directory NAME. The names are `ep2-ship-MMDD` and a deploy
    checkout's mtimes are all "whenever git wrote them", so mtime would pick a
    cut at random on the machine that actually builds the site.
    """
    repo = repo or REPO
    try:
        dirs = sorted(p for p in (repo / "review").glob(SHIP_GLOB) if p.is_dir())
    except Exception:
        return {}
    for d in reversed(dirs):
        for cut in (_from_manifest(d), _from_meta(d)):
            if cut:
                return cut
    return {}


def _beats_from_rows(rows) -> list:
    """[{n, slug, take}] out of a manifest's `beats:` list, or []."""
    out = []
    for b in rows or []:
        if not isinstance(b, dict):
            continue
        try:
            n = int(b.get("beat"))
        except (TypeError, ValueError):
            continue
        take = b.get("take") or b.get("clip") or b.get("file")
        if isinstance(take, dict):
            take = take.get("file") or take.get("path")
        out.append({"n": n, "slug": str(b.get("slug") or "").strip(),
                    "take": str(take).strip() if take else ""})
    return sorted(out, key=lambda r: r["n"])


def _from_manifest(d: Path) -> dict:
    """The ship lane's own manifest, when it has written one."""
    picks = sorted(d.glob("sources/ship-manifest*.yaml"))
    if not picks:
        return {}
    doc = _load_yaml(picks[-1])
    if not isinstance(doc, dict):
        return {}
    beats = _beats_from_rows(doc.get("beats"))
    if not beats:
        return {}
    return {"dir": d.name, "manifest": picks[-1].name, "source": "manifest",
            "beats": beats, "runtime_s": doc.get("duration_s"),
            "video": _video_rel(d), "assembled": _newest_mtime(d)}


def _from_meta(d: Path) -> dict:
    """The assembled cut's own sidecar — the record render_t3 writes."""
    metas = sorted(d.glob("*.mp4.meta.yaml"))
    if not metas:
        return {}
    doc = _load_yaml(metas[-1])
    if not isinstance(doc, dict):
        return {}
    beats = _beats_from_rows(doc.get("sources"))
    slates = {int(n) for n in (doc.get("slate_beats") or [])
              if str(n).strip().lstrip("-").isdigit()}
    if not beats:
        # `sources` absent but the totals present: the scene list is still
        # recoverable from footage_beats/slate_beats, which is less than the
        # manifest carries and more than nothing.
        foot = [int(n) for n in (doc.get("footage_beats") or [])
                if str(n).strip().lstrip("-").isdigit()]
        beats = [{"n": n, "slug": "", "take": "in the cut"} for n in sorted(foot)]
        beats += [{"n": n, "slug": "", "take": ""} for n in sorted(slates)]
        beats.sort(key=lambda r: r["n"])
    if not beats:
        return {}
    for b in beats:                     # a slate is named by the sidecar itself
        if b["n"] in slates:
            b["take"] = ""
    return {"dir": d.name, "manifest": metas[-1].name, "source": "meta",
            "beats": beats, "runtime_s": doc.get("duration_s"),
            "provisional": sorted(int(n) for n in (doc.get("provisional_beats") or [])
                                  if str(n).strip().lstrip("-").isdigit()),
            "video": _video_rel(d), "assembled": _newest_mtime(d)}


def _video_rel(d: Path) -> str:
    """The cut's own mp4 as a site-relative path, or "" — the page links what a
    reader can actually open, and links nothing when there is nothing there."""
    vids = sorted(d.glob("*.mp4"))
    return f"review/{d.name}/{vids[-1].name}" if vids else ""


def _newest_mtime(d: Path):
    """When this cut was assembled, off the mp4's own mtime, or None.

    A LOCAL FACT AND LABELLED AS ONE. A deploy checkout's mtimes are all
    "whenever git wrote them", so callers must treat a None here as normal and
    must not print this as a build-server truth.
    """
    try:
        vids = sorted(d.glob("*.mp4"))
        if not vids:
            return None
        return datetime.datetime.fromtimestamp(vids[-1].stat().st_mtime,
                                               datetime.timezone.utc)
    except Exception:
        return None


# ------------------------------------------------------- the readiness ledger ---
def read_readiness(repo: Path = None) -> dict:
    """Per-scene status and the written fault against each one. {} if unread.

    This is where "named faults" is an actual count rather than a phrase: the
    ship order says best-available takes ship WITH NAMED FAULTS, and the ledger
    is the file that names them. A scene whose status is anything but PASS has a
    written reason on the same row, and the count of those is what ships.
    """
    repo = repo or REPO
    files = sorted((repo / READINESS_DIR).glob(READINESS_GLOB)) \
        if (repo / READINESS_DIR).is_dir() else []
    if not files:
        return {}
    doc = _load_yaml(files[-1])
    if not isinstance(doc, dict) or not isinstance(doc.get("beats"), list):
        return {}
    beats = {}
    for b in doc["beats"]:
        if not isinstance(b, dict):
            continue
        try:
            n = int(b.get("beat"))
        except (TypeError, ValueError):
            continue
        status = str(b.get("status") or "").strip()
        # The ledger's own words for what is wrong, in the order it writes them:
        # the blocker first, then a one-line diagnosis, then a note on the
        # status. Never re-worded here — a paraphrase of a fault is not a fault.
        # ORDER MATTERS AND THE LAST ENTRY IS THE POINT. A row that names a
        # blocker gets its blocker; most rows name none — `blocked_on: None` is
        # the commonest value in the ledger — and their fault is precisely that
        # nobody ever scored them, which is what `verdict` says out loud ("NONE
        # — a 0814 carry-forward with no verdict block"). Stopping before
        # `verdict` printed "No reason written on its row" over ten scenes whose
        # reason was written, one key along.
        fault, quoted = "", True
        for key in ("blocked_on", "diagnosis_one_line", "status_note",
                    "open_taste_question", "blocked_on_note", "verdict"):
            v = b.get(key)
            if isinstance(v, str) and v.strip() and v.strip().lower() != "none":
                fault = one_sentence(v)
                break
        # THE COMMONEST FAULT IN THIS EPISODE IS A WORD, AND THE WORD IS JARGON.
        # Ten rows say only "NONE for the clip" or "NONE — a 0814 carry-forward
        # with no verdict block", which to anyone outside the crew reads as
        # "no fault" — the exact opposite of what it means. It means nobody has
        # ever judged this scene. That is worth a sentence rather than a quote,
        # so it gets one, and `quoted` tells the caption which lines are which.
        if fault.upper().startswith("NONE"):
            fault = ("Never scored against a written bar — it is in the cut "
                     "because it is the best footage there is, not because "
                     "anyone judged it good")
            quoted = False
        beats[n] = {"n": n, "slug": str(b.get("slug") or "").strip(),
                    "status": status, "fault": fault, "quoted": quoted}
    if not beats:
        return {}
    summary = doc.get("summary") if isinstance(doc.get("summary"), dict) else {}
    return {"file": files[-1].name, "beats": beats, "summary": summary,
            "generated": str(doc.get("generated") or "")}


# ------------------------------------------------------------- the job record ---
def read_jobs(repo: Path = None) -> dict:
    """The box's dated per-job records. {} when unreadable.

    `pipeline/measured/queue-history.json` is committed, so this is the one
    source of measured minutes a deploy checkout can actually read — the
    sidecar branch it was distilled from is not in a one-commit clone.
    """
    repo = repo or REPO
    try:
        doc = json.loads((repo / QUEUE_HISTORY).read_text(encoding="utf-8"))
    except Exception:
        return {}
    jobs = doc.get("jobs") if isinstance(doc, dict) else None
    if not isinstance(jobs, list) or not jobs:
        return {}
    meta = doc.get("_meta") if isinstance(doc.get("_meta"), dict) else {}
    return {"jobs": [j for j in jobs if isinstance(j, dict)],
            "measured_at": str(meta.get("measured_at") or ""),
            "source_branch": str(meta.get("source_branch") or "")}


def kind_median(jobs: list, kind: str, since=None) -> dict:
    """{minutes, n, low, high} for one render kind, or {} when nothing measured.

    NEVER A FALLBACK NUMBER. A kind with no dated runs returns {} and the caller
    prints that it is not measured; substituting another kind's median would be
    this page inventing the one thing it exists to stop inventing.
    """
    # `duration_s > 0` and not merely present. The record holds jobs that
    # finished in the same second they started — a resumed run, a cache hit —
    # and a zero in the sample rendered the printed range as "–14 min each",
    # which is a page saying a render can take no time at all.
    secs = [j["duration_s"] for j in jobs
            if str(j.get("kind")) == kind
            and isinstance(j.get("duration_s"), (int, float))
            and j["duration_s"] > 0
            and (since is None or (_dt(j.get("finished_at")) or since) >= since)]
    if not secs:
        return {}
    return {"minutes": statistics.median(secs) / 60.0, "n": len(secs),
            "low": min(secs) / 60.0, "high": max(secs) / 60.0}


def _outputs(j) -> list:
    return [o for o in (j.get("outputs") or []) if isinstance(o, dict)]


def is_motion_job(j) -> bool:
    """A job that produced moving pictures.

    CLASSIFIED BY WHAT CAME OUT, not by the label on the way in. The `kind`
    field is written by whoever authored the spec and today's plate wave runs
    under `kind: other` — a page that trusted the label counted 37 of the day's
    plate jobs as neither plates nor motion. The outputs cannot be mislabelled
    that way: a video came out or it did not. `kind` stays as the fallback for
    the older rows that list no outputs at all.
    """
    outs = _outputs(j)
    if outs:
        return any(str(o.get("kind")) == "video" for o in outs)
    return str(j.get("kind")) in ("motion", "ltx")


def is_plate_job(j) -> bool:
    """A job that produced still images and no video — one plate batch."""
    outs = _outputs(j)
    if outs:
        return all(str(o.get("kind")) == "image" for o in outs)
    return str(j.get("kind")) in ("still", "still-ipa", "inpaint")


def window_median(jobs: list, pred, now=None, hours: int = DIGEST_HOURS) -> dict:
    """{seconds, minutes, n, low, high} over the jobs in the window that match.

    NEVER A FALLBACK NUMBER. Nothing matching returns {} and the caller prints
    that it is not measured; widening the window until a number appears would be
    this page inventing the one thing it exists to stop inventing.

    THE WINDOW IS THE POINT. A recipe changes daily here, so the median of every
    run ever made is not the cost of the next run. `duration_s > 0` and not
    merely present: the record holds jobs that finished in the second they
    started — a resumed run, a cache hit — and a zero in the sample once
    rendered a printed range as "–14 min each".
    """
    now = now or utcnow()
    since = now - datetime.timedelta(hours=hours)
    secs = [j["duration_s"] for j in jobs
            if isinstance(j.get("duration_s"), (int, float))
            and j["duration_s"] > 0
            and (_dt(j.get("finished_at")) or since -
                 datetime.timedelta(days=1)) >= since
            and pred(j)]
    if not secs:
        return {}
    med = statistics.median(secs)
    return {"seconds": med, "minutes": med / 60.0, "n": len(secs),
            "low": min(secs), "high": max(secs)}


def digest(jobs: list, now=None, hours: int = DIGEST_HOURS) -> dict:
    """What the machines actually did in the last `hours`, off their own stamps."""
    now = now or utcnow()
    span = datetime.timedelta(hours=hours)
    rows = [j for j in jobs
            if (_dt(j.get("finished_at")) or now - span * 9) > now - span]
    beats, kinds = set(), {}
    for j in rows:
        try:
            beats.add(int(j.get("beat")))
        except (TypeError, ValueError):
            pass
        kinds[str(j.get("kind") or "other")] = kinds.get(
            str(j.get("kind") or "other"), 0) + 1
    ok = sum(1 for j in rows if j.get("rc") == 0)
    secs = sum(j.get("duration_s") or 0 for j in rows)
    return {"jobs": len(rows), "ok": ok, "failed": len(rows) - ok,
            "beats": sorted(beats), "kinds": kinds, "hours": hours,
            "machine_minutes": secs / 60.0,
            "hosts": sorted({str(j.get("runner_host") or "") for j in rows} - {""})}


# ----------------------------------------------------------------- the scenes ---
def rollup(cut: dict, ready: dict, worked: set) -> list:
    """One row per scene: what is in the cut, whether a fault is named on it,
    and whether an upgrade attempt ran for it inside the window.

    THE JOIN IS OUTER FROM THE LEDGER SIDE. The readiness ledger knows all
    twenty-one scenes; a cut can be missing rows. A scene the ledger names and
    the cut does not must show as unknown rather than vanish off a strip whose
    whole job is completeness.
    """
    nums = sorted(set(list((ready or {}).get("beats", {}).keys())
                      + [b["n"] for b in (cut or {}).get("beats", [])]))
    in_cut = {b["n"]: b for b in (cut or {}).get("beats", [])}
    out = []
    for n in nums:
        b = in_cut.get(n)
        r = (ready or {}).get("beats", {}).get(n, {})
        if b is None:
            state = "unk"
        elif b["take"]:
            state = "foot"
        else:
            state = "slate"
        if state == "foot" and n in worked:
            state = "up"
        status = str(r.get("status") or "")
        # THE LEDGER IS DATED AND THE CUT IS NEWER, so the two can honestly
        # disagree: a row still reading `slate` for a scene that has since been
        # given footage has not been re-scored, it has not been contradicted.
        # Printing "shipping as slate" beside a strip that shows the scene
        # filled would be the page arguing with itself; saying the row is out of
        # date is the same fact without the contradiction.
        stale = state in ("foot", "up") and status.lower() == "slate"
        out.append({"n": n, "slug": (b or {}).get("slug") or r.get("slug") or "",
                    "state": state,
                    "status": "not re-scored since it got footage" if stale
                              else status,
                    "stale": stale, "fault": r.get("fault") or "",
                    "quoted": bool(r.get("quoted", True)),
                    "named_fault": bool(status) and status.upper() != "PASS"})
    return out


# ------------------------------------------------------------------ the steps ---
def nums_words(ns) -> str:
    """'02, 03 and 04' — scene numbers in a sentence, never a bare python list."""
    xs = ["%02d" % int(n) for n in ns or []]
    if len(xs) <= 1:
        return xs[0] if xs else ""
    return ", ".join(xs[:-1]) + " and " + xs[-1]


def steps(order: dict, cut: dict, ready: dict, jobs: list, rows: list,
          now=None, wave: dict = None) -> list:
    """The five remaining steps, each with a state, an owner and a time.

    A step's STATE is derived, never declared: step 1 is in flight until the
    last of its scenes is in the cut, and every later step waits on the one in
    front of it. That is the only ordering the files support, and writing it as
    a chain means a page built after the last swap moves on its own.

    Each step's `measured` flag is what licenses the word on the page. True and
    the figure is the median of dated runs with its n; False and the page says
    "estimate" out loud.

    A SLIP IS SHOWN, NEVER ABSORBED. Where the order names a clock and the clock
    has passed with the work still running, the step carries a `slip` line
    saying by how much. The target is not re-drawn to meet the present; a page
    that quietly moves its own deadline is a diary of successes.
    """
    now = now or utcnow()
    out = []

    # 1 — the design patch wave. Its state is read off the cut: a scene has
    # landed when the manifest's take for it carries the wave's date stamp.
    wp = wave_progress(wave, cut)
    left, done = wp["remaining"], wp["swapped"]
    plate = window_median(jobs, is_plate_job, now)
    motion = window_median(jobs, is_motion_job, now)
    if not wp["beats"]:
        est, label, measured = "not on record", "On record", False
        basis = ("No patch wave is listed in "
                 f"{SHIP_PATH_MEASURED}, so this page names no scenes and puts "
                 "no time on them.")
    elif not left:
        est, label, measured = "all landed", "On record", False
        basis = ("Every scene in the wave now carries a take stamped "
                 f"{wp['stamp']} in the ship cut's own manifest — that is the "
                 "whole test, and it is one a reader can run against the file.")
    elif plate and motion:
        est, label, measured = (
            minutes_words(len(left) * (plate["seconds"] + motion["seconds"])
                          / 60.0), "Estimate", False)
        basis = (
            f"One plate batch and one motion job for each of the {len(left)} "
            "scenes still to come, at the medians this box measured in the last "
            f"{DIGEST_HOURS} hours: a plate batch {secs_words(plate['seconds'])} "
            f"(middle of {plate['n']} dated runs, "
            f"{span_words(plate['low'], plate['high'])} each) and a motion job "
            f"{secs_words(motion['seconds'])} (middle of {motion['n']}, "
            f"{span_words(motion['low'], motion['high'])} each), off "
            f"{QUEUE_HISTORY}. Both halves are measured and the SUM IS AN "
            "ESTIMATE, because it assumes one plate and one motion attempt per "
            "scene: in practice a scene takes several of each before one "
            "passes, and the judging in between is a person looking, which is "
            "the other clock.")
    else:
        est, label, measured = "not measured", "Estimate", False
        basis = ("Neither a plate batch nor a moving-picture job has finished "
                 f"inside the last {DIGEST_HOURS} hours that this page can "
                 "see, so it claims no time for the scenes still to come.")
    ref = (wp["beats"] and (wave or {}).get("reference")) or []
    out.append({
        "n": 1,
        "title": (f"Re-render the {len(wp['beats'])} scenes whose goblin is "
                  "off-model" if wp["beats"] else
                  "Re-render the scenes whose goblin is off-model"),
        "state": ("unknown" if not wp["beats"]
                  else ("done" if not left else "flight")),
        "owner": "the machines (the design patch wave)",
        "estimate": est, "measured": measured, "label": label, "basis": basis,
        "note": (
            (f"{len(wp['beats'])} scenes — {nums_words(wp['beats'])} — draw the "
             "goblin as somebody other than the character you ruled, so each is "
             "being drawn again to the committed design and dropped into the "
             "ship cut the moment it passes, not held back to the end. Plates "
             "through the middle of the day, moving pictures through the "
             "afternoon."
             + (f" Scenes {nums_words(ref)} already match him and are the "
                "reference for the rest, not work." if ref else "")
             + (f" {len(done)} of {len(wp['beats'])} are in the cut already "
                f"({nums_words(done)})." if done else
                " None of them is in the cut yet."))
            if wp["beats"] else
            "The wave's scene list is not on file, so this page will not "
            "describe one."),
        "slip": _wave_slip(order, wp, now)})

    # 2 — assembly and the screening gate, both timed on this episode's files.
    asm = assembly_minutes()
    out.append({
        "n": 2, "title": "Assemble the final cut and run the screening gate",
        "state": "ready" if (wp["beats"] and not left) else "wait-machine",
        "owner": "the machines (the ship lane)",
        "estimate": minutes_words(asm["minutes"]) if asm else "not measured",
        "measured": bool(asm and asm.get("measured")),
        "basis": (asm or {}).get("basis", ""),
        "note": ("It starts the moment the last swap lands. One run of the "
                 "assembler stitches every scene, burns the captions, lays the "
                 "voice tracks in and writes the record of what went in. Then "
                 "the site's own screening gate re-walks every page before "
                 "anyone is handed a link.")})

    # 3 — the author's watch-through. HIS step, and the gate he kept.
    runtime = (cut or {}).get("runtime_s")
    watch = ""
    if isinstance(runtime, (int, float)) and runtime > 0:
        watch = f"{int(runtime) // 60}:{int(runtime) % 60:02d}"
    out.append({
        "n": 3, "title": "You watch it through and answer the open cards",
        "state": "wait-you", "owner": "you — the author, this evening",
        "estimate": f"~{WATCH_ALLOWANCE_MIN} min", "measured": False,
        "basis": (f"The cut itself runs {watch}, measured off the assembled "
                  f"file. The rest is an ESTIMATE — how long a person takes to "
                  "decide is the one thing on this page nobody can measure."
                  if watch else
                  "An ESTIMATE. How long a person takes to decide is the one "
                  "thing on this page nobody can measure."),
        "note": ("This is the gate you chose to keep: nothing publishes until "
                 "you have watched it. It is the only step here that stops "
                 "everything behind it, and it is the evening's work in the "
                 "plan you set.")})

    # 4 — applying whatever he says. Costed per swap off TODAY's own runs.
    swap = swap_minutes(jobs, now)
    out.append({
        "n": 4, "title": "Apply your verdicts — the last swaps, if any",
        "state": "wait-you", "owner": "the machines, once you have ruled",
        "estimate": (f"{minutes_words(swap['minutes'])} per swap"
                     if swap else "not measured"),
        "measured": bool(swap),
        "basis": ((f"Middle of the {swap['n']} moving-picture jobs this box "
                   f"finished in the last day "
                   f"({span_words(swap['low'] * 60, swap['high'] * 60)} each), "
                   f"off {QUEUE_HISTORY}. Add one more assembly run for "
                   "the round.")
                  if swap else
                  "No moving-picture job has finished inside the window, so "
                  "nothing is claimed."),
        "note": ("IF ANY — you may have none. A swap is one scene re-rendered "
                 "and dropped into the cut. Several swaps ride in one "
                 "re-assembly, so a round costs the slowest swap plus one "
                 "assembly, not the sum of them.")})

    # 5 — publication. His word, and then a chain of machine steps.
    out.append({
        "n": 5, "title": "You say publish, and it goes out tonight",
        "state": "wait-you", "owner": "you — the author",
        "estimate": "minutes, once you say it", "measured": False,
        "basis": "An ESTIMATE of the deploy, which nobody here has timed.",
        "note": ("On your word the cut is stamped into the tree with your "
                 "approval on it, the site is rebuilt from the tree, and the "
                 "push goes to the host, which builds and serves it. Nothing "
                 "in that chain needs a person after the word.")})
    return out


def _wave_slip(order: dict, wp: dict, now) -> str:
    """The one sentence a missed clock earns, or "".

    THE PAGE SHOWS THE SLIP AND LEAVES THE TARGET ALONE. The founder's plan puts
    plates at midday; when midday passes with scenes still to draw, this says by
    how much rather than the page quietly re-drawing midday to suit. It costs
    nothing when the work is on time, because then there is nothing to say.
    """
    by = (order or {}).get("plates_by")
    if not by or not wp.get("remaining") or now <= by:
        return ""
    return (f"Behind the plan: plates were due {order.get('plates_by_text') or ''} "
            f"UTC and that was {gap_words(now - by)} ago, with "
            f"{len(wp['remaining'])} of {len(wp['beats'])} scenes still to "
            f"land ({nums_words(wp['remaining'])}). The plan is not re-drawn to "
            "meet the clock — this is what running late looks like here.")


SHIP_PATH_MEASURED = "pipeline/measured/ship-path.yaml"


def assembly_minutes(repo: Path = None) -> dict:
    """The measured cost of one assembly plus the screening gate.

    FIRST CHOICE is `pipeline/measured/ship-path.yaml`, which holds wall clock
    from timing the two commands on THIS episode's own inputs. That file exists
    because the fallback below is a measurement of the wrong thing: episode 1,
    fifteen scenes, a different assembler run on a different day. It is a real
    number and it is not a number about this episode.

    FALLBACK is build_status.STEPS, read rather than copied — typing "4 min"
    into this file would be a second copy of a figure that already lives one
    import away, and two copies is how one page starts disagreeing with the page
    beside it. A bad edit to the measured file therefore degrades to the older
    figure rather than to silence.
    """
    repo = repo or REPO
    doc = _load_yaml(repo / SHIP_PATH_MEASURED)
    if isinstance(doc, dict):
        secs, parts = 0.0, []
        for key, words in (("assembly", "the assembler"),
                           ("screening_gate", "the screening gate")):
            row = doc.get(key)
            if isinstance(row, dict) and isinstance(row.get("seconds"),
                                                    (int, float)):
                secs += float(row["seconds"])
                # SECONDS, not minutes, for the parts. Both halves round to a
                # figure that reads as the whole ("the assembler under a minute
                # plus the screening gate 2 min" summing to "2 min" is a
                # sentence nobody can check), and these are small enough that
                # the honest unit is the one they were timed in.
                parts.append(f"{words} {round(float(row['seconds']))} s")
        if secs > 0:
            return {"minutes": secs / 60.0, "measured": True,
                    "basis": ("Wall clock, timed on this episode's own files — "
                              + " plus ".join(parts) + ". Recorded with the "
                              "commands that produced them in "
                              f"{SHIP_PATH_MEASURED}; re-run them and the "
                              "number here moves.")}
    try:
        import sys
        sys.path.insert(0, str(repo / "pipeline"))
        import build_status
        for label, cost in build_status.STEPS:
            if "assembl" not in label.lower():
                continue
            m = re.search(r"~?\s*([\d.]+)\s*min", str(cost))
            if not m:
                continue
            return {"minutes": float(m.group(1)), "measured": True,
                    "basis": ("Measured on episode 1's assembly runs and kept "
                              "in pipeline/build_status.py. Episode 1 is "
                              "fifteen scenes and this one is twenty-one, so "
                              "treat it as a FLOOR rather than a best guess.")}
    except Exception:
        pass
    return {}


def swap_minutes(jobs: list, now=None, hours: int = DIGEST_HOURS) -> dict:
    """What one scene swap costs, off the moving-picture jobs of the last day.

    TODAY'S RUNS AND NOT THE LIFETIME MEDIAN, because the recipe changed: the
    same box's motion median over the whole record is not the median of the
    recipe currently being run, and the estimate that matters is the cost of the
    next swap, not the average of every swap ever made.

    CLASSIFIED BY OUTPUT, see `is_motion_job` — the `kind` label is written by
    whoever authored the spec and today's wave runs under `kind: other`.
    """
    m = window_median(jobs, is_motion_job, now, hours)
    if not m:
        return {}
    # The older callers read `low`/`high` in minutes; window_median speaks
    # seconds because a plate batch is not a thing you say in minutes.
    return {"minutes": m["minutes"], "n": m["n"],
            "low": m["low"] / 60.0, "high": m["high"] / 60.0}


def open_cards(ready: dict) -> int:
    """How many scenes carry a taste question nobody has answered — the ledger's
    own `open_taste_question` rows. 0 when the ledger cannot be read."""
    return sum(1 for b in (ready or {}).get("beats", {}).values()
               if b.get("fault") and str(b.get("status", "")).upper() != "PASS")


# --------------------------------------------------------------------- report ---
def collect(repo: Path = None, now=None) -> dict:
    """Every fact the section prints, in one read of each file."""
    repo, now = repo or REPO, now or utcnow()
    order = read_ship_order(repo)
    cut = read_ship_cut(repo)
    ready = read_readiness(repo)
    wave = read_patch_wave(repo)
    jr = read_jobs(repo)
    jobs = jr.get("jobs", [])
    dig = digest(jobs, now)
    rows = rollup(cut, ready, set(dig["beats"]))
    return {"order": order, "cut": cut, "ready": ready, "jobs": jr,
            "wave": wave, "progress": wave_progress(wave, cut),
            "digest": dig, "rows": rows,
            "steps": steps(order, cut, ready, jobs, rows, now, wave),
            "now": now}


# ===================================================================== the page ==
# PLAIN LANGUAGE, and the house rule build_status.py sets is the standard: a
# shot is a SCENE here, never a "beat"; a model codename never appears without
# the words that explain it. The founder asked for this to be readable, and the
# test he set is a sharp fourteen-year-old getting it in one pass.
#
# THE COLOUR LAW (SITE.md, and charts.STATE_STYLE is its single definition):
# GREEN is the machine's clock, AMBER is the author's. Every value is a var() so
# both survive a reader's light/dark setting — a hex literal in this block would
# be a colour that does not know which theme it is in.

PATH_CSS = """
/* ---- THE PATH TO EPISODE 2. Three tenses, one panel: what happened, what is
   happening, what is planned. Amber left rule, like .ep2now — this panel exists
   because the author asked what the path is, and it is his panel. ---- */
.spath { border: 1px solid var(--line); border-left: 3px solid var(--sap);
  border-radius: 14px; padding: .9rem 1rem; margin: 0 0 1.4rem;
  background: var(--code-bg); text-align: left; }
.spath > h3 { font: 700 1.02rem/1.3 var(--sans, inherit); color: var(--ink);
  margin: 0 0 .25rem; }
.spath .sub { font: 400 .82rem/1.6 var(--sans, inherit); color: var(--muted);
  margin: 0 0 .9rem; }
.spath .tense { border-top: 1px solid var(--line-soft); padding: .8rem 0 0;
  margin: .8rem 0 0; }
.spath .tense:first-of-type { border-top: 0; padding-top: 0; margin-top: 0; }
.spath .sh { font: 700 .62rem/1 var(--mono); letter-spacing: .09em;
  text-transform: uppercase; color: var(--faint); margin: 0 0 .55rem; }
.spath .pl { list-style: none; margin: 0; padding: 0;
  font: 400 .84rem/1.6 var(--sans, inherit); color: var(--muted); }
.spath .pl li { position: relative; padding: 0 0 0 1.1rem; margin: 0 0 .4rem; }
.spath .pl li:last-child { margin-bottom: 0; }
.spath .pl li::before { content: ""; position: absolute; left: 0; top: .5rem;
  width: .55rem; height: .55rem; border-radius: 2px; background: var(--leaf); }
.spath .pl li.you::before { background: var(--sap); }
.spath .pl li.hollow::before { background: transparent;
  box-shadow: inset 0 0 0 1px var(--line); }
.spath .pl b { color: var(--ink); font-weight: 700; }
.spath .pl a { color: var(--ink); }
/* The scene strip. One cell per scene of the episode, in order, with the number
   readable in it — a colour with no number beside it is a picture nobody can
   check against the table under it. */
.pbeats { display: flex; flex-wrap: wrap; gap: .22rem; margin: .1rem 0 .5rem; }
.pbc { width: 1.75rem; height: 1.55rem; border-radius: 4px; flex: none;
  display: inline-flex; align-items: center; justify-content: center;
  font: 700 .64rem/1 var(--mono); font-variant-numeric: tabular-nums;
  border: 1px solid transparent; }
.pbc.pb-foot { background: var(--leaf); color: var(--sap-ink); }
.pbc.pb-up { background: var(--leaf-deep); color: var(--ink); }
.pbc.pb-slate { background: transparent; color: var(--faint);
  border-color: var(--line); }
.pbc.pb-unk { background: transparent; color: var(--faint);
  border: 1px dashed var(--line); }
.pbkey { display: flex; flex-wrap: wrap; gap: .1rem .8rem; margin: 0 0 .55rem;
  font: 400 .7rem/1.7 var(--sans, inherit); color: var(--muted); }
.pbkey span { display: inline-flex; align-items: center; gap: .34rem; }
.pbkey span::before { content: ""; width: .55rem; height: .55rem; flex: none;
  border-radius: 2px; background: var(--line); }
.pbkey .k-foot::before { background: var(--leaf); }
.pbkey .k-up::before { background: var(--leaf-deep); }
.pbkey .k-slate::before { background: transparent;
  box-shadow: inset 0 0 0 1px var(--line); }
/* The five steps. A numbered list that reads down: what it is, who it waits on,
   how long, and where the number came from. */
.spsteps { list-style: none; margin: 0; padding: 0; counter-reset: sp; }
.spstep { counter-increment: sp; position: relative; border: 1px solid var(--line);
  border-radius: 10px; background: var(--bg); padding: .6rem .7rem .65rem 2.5rem;
  margin: 0 0 .5rem; }
.spstep:last-child { margin-bottom: 0; }
.spstep::before { content: counter(sp); position: absolute; left: .65rem;
  top: .62rem; width: 1.35rem; height: 1.35rem; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font: 700 .7rem/1 var(--mono); background: var(--panel-2); color: var(--muted);
  border: 1px solid var(--line); }
.spstep .st { display: flex; flex-wrap: wrap; align-items: baseline;
  gap: .4rem .55rem; }
.spstep .st b { font: 700 .92rem/1.35 var(--sans, inherit); color: var(--ink); }
.spstep .when { margin-left: auto; font: 700 .82rem/1.2 var(--mono);
  font-variant-numeric: tabular-nums; color: var(--leaf); white-space: nowrap; }
.spstep .when.you { color: var(--sap); }
.spchip { font: 700 .6rem/1 var(--mono); letter-spacing: .06em;
  text-transform: uppercase; padding: .22rem .36rem; border-radius: 3px;
  border: 1px solid var(--line); color: var(--muted); white-space: nowrap; }
.spchip.c-mach { color: var(--leaf); border-color: var(--leaf-deep); }
.spchip.c-you { color: var(--sap); border-color: var(--sap-deep); }
.spchip.c-done { color: var(--leaf); border-color: var(--leaf); }
.spstep .sd { margin: .35rem 0 0; font: 400 .8rem/1.6 var(--sans, inherit);
  color: var(--muted); }
.spstep .sb { margin: .3rem 0 0; font: 400 .72rem/1.65 var(--sans, inherit);
  color: var(--faint); }
.spstep .sb b { color: var(--muted); font-weight: 700; }
/* A SLIP. Amber, because a plan running late is the author's clock intruding on
   the machine's, and it is set apart so it cannot be skimmed past. It appears
   only when a clock on record has passed with work still to do, and it never
   edits the clock it is late against. */
.spstep .sl { margin: .35rem 0 0; padding: .3rem .5rem; border-radius: 6px;
  border-left: 2px solid var(--sap); background: var(--panel-2);
  font: 400 .74rem/1.6 var(--sans, inherit); color: var(--muted); }
.spath .target { margin: 0 0 .9rem; padding: .45rem .6rem; border-radius: 8px;
  border: 1px solid var(--line); background: var(--panel-2);
  font: 400 .78rem/1.6 var(--sans, inherit); color: var(--muted); }
.spath .target b { color: var(--ink); }
.spath .cnote { margin: .8rem 0 0; text-align: left;
  font: 400 .72rem/1.65 var(--sans, inherit); color: var(--faint); }
.spath .cnote code { font: 400 .68rem/1.5 var(--mono); }
.spath details { margin: .5rem 0 0; }
.spath details > summary { cursor: pointer; color: var(--faint);
  font: 500 .72rem/1.7 var(--sans, inherit); }
.spath .fl { list-style: none; margin: .4rem 0 0; padding: 0;
  font: 400 .78rem/1.6 var(--sans, inherit); color: var(--muted); }
.spath .fl li { padding: .35rem 0; border-top: 1px solid var(--line-soft); }
.spath .fl li:first-child { border-top: 0; }
.spath .fl b { color: var(--ink); }
.spath .fl .fs { font: 700 .62rem/1 var(--mono); letter-spacing: .05em;
  text-transform: uppercase; color: var(--faint); margin-left: .3rem; }
"""

# state -> (chip css, the words for it). Derived states only: nothing here is
# declared by hand, so a page built after the cutoff moves without an edit.
STEP_CHIP = {
    "flight": ("c-mach", "running now"),
    "ready": ("c-mach", "ready to run"),
    "wait-machine": ("c-mach", "next, on the machines"),
    "wait-you": ("c-you", "waiting on you"),
    "done": ("c-done", "done"),
    "unknown": ("", "no state on record"),
}
CELL_WORDS = {"foot": "footage in the cut", "up": "footage in the cut, and a "
              "fresh attempt for it finished today", "slate": "a title card "
              "where the scene goes", "unk": "not listed in the cut"}


def _e(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _strip_html(rows: list) -> str:
    """The 21 scenes as one row of cells, each carrying its own number."""
    cells = []
    for r in rows:
        why = CELL_WORDS.get(r["state"], "")
        if r["named_fault"]:
            why += f" · shipping as {r['status']}"
        cells.append(f'<span class="pbc pb-{r["state"]}" '
                     f'title="{_e("scene %02d %s — %s" % (r["n"], r["slug"], why))}">'
                     f'{r["n"]:02d}</span>')
    foot = sum(1 for r in rows if r["state"] in ("foot", "up"))
    return (f'<div class="pbeats" role="img" aria-label="{foot} of {len(rows)} '
            f'scenes have footage in the ship cut">{"".join(cells)}</div>'
            '<div class="pbkey">'
            '<span class="k-foot">has its footage</span>'
            '<span class="k-up">has footage, and a fresh attempt for it landed '
            'today</span>'
            '<span class="k-slate">still a title card</span></div>')


def _faults_html(rows: list, ready: dict) -> str:
    """One line per scene shipping with a fault, in the ledger's own words."""
    bad = [r for r in rows if r["named_fault"]]
    if not bad:
        return ""
    items = "".join(
        f'<li><b>Scene {r["n"]:02d} {_e(r["slug"] or "")}</b>'
        f'<span class="fs">{_e(r["status"])}</span><br>'
        f'{_e(r["fault"] or "No reason written on its row.")}</li>' for r in bad)
    when = (ready or {}).get("generated", "")
    return (f'<details><summary>The {len(bad)} named faults, one line each — '
            'what is wrong with each scene that is not a clean pass</summary>'
            f'<ul class="fl">{items}</ul>'
            f'<p class="cnote">Each line above is the first sentence of that '
            f'scene\'s own row in <code>review/ep2-picks/'
            f'{_e((ready or {}).get("file", ""))}</code>, quoted and not '
            'rewritten — including where it says "beat", which is the crew\'s '
            'word for a scene. The exception is a row whose only verdict is the '
            'word NONE: that reads as "no fault" and means the opposite, so '
            'this page says what it means instead of quoting it. '
            + (f'That ledger was written {_e(when)} and the cut is newer, so a '
               'row that has not been re-scored since its scene got footage is '
               'marked as such rather than printed as a contradiction. '
               if when else "")
            + 'It makes no taste call and neither does this page: it records '
              'what is wrong, and what to do about it is yours.'
              '</p></details>')


def html(data: dict = None, repo: Path = None, now=None) -> str:
    """The whole section. "" only if every source failed — see the docstring.

    Fails SOFT and per-line: a source that cannot be read costs its own fact,
    never the section, and never a zero. "0 scenes have footage" published off a
    failed read would be a picture of our own bug on a panel about progress.
    """
    try:
        d = data if data is not None else collect(repo, now)
    except Exception:
        return ""
    order, cut, ready = d["order"], d["cut"], d["ready"]
    rows, dig, sts = d["rows"], d["digest"], d["steps"]
    wp = d.get("progress") or {}
    if not order and not cut and not rows:
        return ""

    # ---- ① what happened -----------------------------------------------------
    was = []
    if dig["jobs"]:
        scenes = ", ".join("%02d" % n for n in dig["beats"])
        was.append(
            f'<li><b>{dig["jobs"]} render jobs finished</b> in the last '
            f'{dig["hours"]} hours — {minutes_words(dig["machine_minutes"])} of '
            f'machine time, on scenes {_e(scenes)}.'
            + (f' {dig["failed"]} of them failed, which is normal and is why a '
               'scene takes several tries.' if dig["failed"] else "")
            + '</li>')
    else:
        was.append('<li class="hollow">No render job has finished in the last '
                   f'{dig["hours"]} hours that this page can see.</li>')
    if cut.get("dir"):
        was.append(
            f'<li><b>A whole-episode cut was put together</b> — '
            + (f'<a href="{_e(cut["video"])}">{_e(cut["dir"])}</a>'
               if cut.get("video") else _e(cut["dir"]))
            + ', the candidate the ship order is about. It is a working cut: no '
              'leaf, nothing in the tree, nobody has passed it.</li>')
    if order.get("date"):
        was.append(
            f'<li class="you"><b>You gave the ship order</b> on '
            f'{_e(order["date"])} — {_e(one_sentence(order.get("headline") or "", 90))}'
            '. Best-available takes ship, with what is wrong with them named '
            'out loud, and the design patch goes in today rather than after.'
            + (f' It replaces '
               f'{_e(one_sentence(order.get("supersedes") or "", 120))}.'
               if order.get("supersedes") else "")
            + '</li>')

    # ---- ② what is happening -------------------------------------------------
    foot = [r for r in rows if r["state"] in ("foot", "up")]
    slates = [r for r in rows if r["state"] == "slate"]
    faults = [r for r in rows if r["named_fault"]]
    now_facts = []
    if rows:
        now_facts.append(
            f'<li><b>{len(foot)} of {len(rows)} scenes have their footage</b> in '
            f'the cut'
            + (f', and {len(slates)} '
               + ("is" if len(slates) == 1 else "are")
               + ' still a title card where the picture goes ('
               + _e(", ".join("%02d" % r["n"] for r in slates)) + ')'
               if slates else ', and none of them is a title card any more')
            + '.</li>')
    if faults:
        now_facts.append(
            f'<li class="you"><b>{len(faults)} of them ship with a named '
            'fault</b> — footage good enough to ship that nobody is calling '
            'clean. Each one has a written reason, and they are listed '
            'below.</li>')
    if wp.get("beats"):
        left = wp.get("remaining") or []
        now_facts.append(
            '<li><b>The design patch wave is running now</b> — '
            + (f'{len(wp["swapped"])} of {len(wp["beats"])} scenes re-drawn to '
               f'the goblin you ruled are already in the cut '
               f'({_e(nums_words(wp["swapped"]))})'
               + (f', and {len(left)} still to come '
                  f'({_e(nums_words(left))})' if left else
                  ', which is all of them')
               if wp.get("swapped") else
               f'all {len(wp["beats"])} of its scenes are still to land '
               f'({_e(nums_words(left))})')
            + '. Each one goes in the moment it passes, not at the end.</li>')
    if dig["beats"]:
        now_facts.append(
            f'<li><b>{len(dig["beats"])} scenes were worked on today</b> '
            f'({_e(", ".join("%02d" % n for n in dig["beats"]))}) — those are '
            'the ones that can still change before the cut is final.</li>')
    if not cut:
        now_facts.append(
            '<li class="hollow"><b>The ship lane is still assembling</b> — no '
            'cut record on disk yet, so this page will not describe one. The '
            'plan below is real; the scene counts appear when the cut does.</li>')

    # ---- ③ what is planned ---------------------------------------------------
    cards = []
    for s in sts:
        chip_css, chip_words = STEP_CHIP.get(s["state"], ("", s["state"]))
        you = chip_css == "c-you"
        cards.append(
            f'<li class="spstep"><div class="st"><b>{_e(s["title"])}</b>'
            + (f'<span class="spchip {chip_css}">{_e(chip_words)}</span>'
               if chip_words else "")
            + f'<span class="when{" you" if you else ""}">{_e(s["estimate"])}'
              '</span></div>'
            f'<p class="sd">{_e(s["note"])}</p>'
            + (f'<p class="sl">{_e(s["slip"])}</p>' if s.get("slip") else "")
            + f'<p class="sb"><b>'
            f'{_e(s.get("label") or ("Measured" if s["measured"] else "Estimate"))}'
            f':</b> {_e(s["basis"])} <b>Waits on:</b> {_e(s["owner"])}.</p></li>')

    # ---- the target, and what it looks like when it is missed ----------------
    # THE DATE IS THE FOUNDER'S AND THE PAGE DOES NOT OWN IT. It is printed as
    # he set it, and when the day runs out the page says the day ran out instead
    # of sliding the date along to keep the panel looking on schedule.
    tnow = d.get("now") or now or utcnow()
    td, tend = order.get("target_date"), order.get("target_end")
    target = ""
    if td and tend and tnow > tend:
        target = ('<p class="target"><b>Target: episode 2 finished on '
                  f'{_e(td)}</b> — the day you named. It has passed. The date '
                  'stays where you set it and the steps below show what is '
                  'still open; this page does not move a target to meet a '
                  'clock.</p>')
    elif td:
        target = ('<p class="target"><b>Target: episode 2 finishes today, '
                  f'{_e(td)}</b> — your own date, from that morning\'s ship '
                  'order. '
                  + (f'{_e(gap_words(tend - tnow))} of the day left when this '
                     'page was built.' if tend else "")
                  + ' Times are UTC: the record names no timezone and every '
                    'other stamp on this site is UTC.</p>')

    src = []
    if cut.get("dir"):
        src.append(f'the ship cut\'s own <code>{_e(cut["manifest"])}</code>')
    if ready.get("file"):
        src.append(f'<code>review/ep2-picks/{_e(ready["file"])}</code>')
    src.append(f'<code>{_e(QUEUE_HISTORY)}</code>')
    src.append('<code>STATE.md</code>’s ship order')

    return (
        '<section class="spath rise" id="path" aria-labelledby="path-h">'
        '<h3 id="path-h">🚩 The path to episode 2 — live</h3>'
        '<p class="sub">Every step still between here and the episode being '
        'published, with how long each one takes and who it is waiting on. '
        'Machine time is measured; a person deciding is not, and this page '
        'never adds the two together. When a step runs past the time on '
        'record, the page says so and leaves the time alone.</p>'
        + target +

        '<div class="tense"><p class="sh">① What happened — the last 24 hours'
        f'</p><ul class="pl">{"".join(was)}</ul></div>'

        '<div class="tense"><p class="sh">② What is happening right now</p>'
        + (_strip_html(rows) if rows else "")
        + f'<ul class="pl">{"".join(now_facts)}</ul>'
        + _faults_html(rows, ready)
        + '</div>'

        '<div class="tense"><p class="sh">③ What is planned — five steps to live'
        f'</p><ol class="spsteps">{"".join(cards)}</ol></div>'

        '<p class="cnote">Every number in this panel is counted while the page '
        'is built, out of ' + " · ".join(src) + '. Nothing in it is typed by '
        'hand, so it moves when the work does and it cannot quietly go stale. '
        'A figure marked <b>measured</b> is the middle of a set of dated runs '
        'you can open and count; a figure marked <b>estimate</b> is one nobody '
        'has measured, and it says so rather than dressing a guess as a '
        'reading.</p></section>')


def main():
    d = collect()
    o, c, r = d["order"], d["cut"], d["ready"]
    print("SHIP ORDER:", o.get("date") or "none on file", "· target",
          o.get("target_date") or "none", "· cutoff",
          o.get("cutoff_text") or "none")
    wp = d.get("progress") or {}
    if wp.get("beats"):
        print(f"PATCH WAVE: {len(wp['swapped'])} of {len(wp['beats'])} landed "
              f"({nums_words(wp['swapped']) or 'none'}) · still to come "
              f"{nums_words(wp['remaining']) or 'none'}")
    print("SHIP CUT  :", c.get("dir") or "PENDING",
          f"(read from its {c.get('source')})" if c else "")
    print("READINESS :", r.get("file") or "unread")
    dg = d["digest"]
    print(f"LAST {dg['hours']}h: {dg['jobs']} jobs ({dg['failed']} failed) on "
          f"scenes {dg['beats']} · {minutes_words(dg['machine_minutes'])} of "
          "machine time")
    foot = [x for x in d["rows"] if x["state"] in ("foot", "up")]
    print(f"SCENES    : {len(foot)} of {len(d['rows'])} with footage · "
          f"{sum(1 for x in d['rows'] if x['state'] == 'slate')} slate · "
          f"{sum(1 for x in d['rows'] if x['named_fault'])} named faults")
    for s in d["steps"]:
        print(f"  {s['n']}. [{s['state']:>12}] {s['title']}  — {s['estimate']}"
              + ("  (measured)" if s["measured"] else "  (estimate)"))


if __name__ == "__main__":
    main()
