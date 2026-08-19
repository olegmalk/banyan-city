#!/usr/bin/env python3
"""Status DATA — what is finished, what is waiting, what each step costs.

Dad's ask (2026-07-28): clearly see what is running, what is blocked on whom,
and where the time goes. The page itself is composed by `build_sim.py` from the
helpers in this file. Until 2026-07-30 both modules wrote `_site/status.html`,
so build_sim silently overwrote everything edited here — one generator, one
file, from now on (stranger-eyes audit).

House rule for anything a visitor reads: plain English. Internally a shot is a
"beat" and an approved frame is "canon"; on the page they are a **scene** and
**final**. Model codenames survive only with a prefix that explains them
("animated by: POST, LTX"). Repo files + the public GitHub API only — the
deploy server has no local git refs and no `gh` CLI.
"""
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from generate_shots import parse_shots  # noqa: E402
import repo_slug  # noqa: E402  one source for "which repo is this"

GH_URL = repo_slug.REPO_URL
REQUESTS_URL = f"{GH_URL}/issues?q=label%3Arender-request"
THREAD_URL = f"{GH_URL}/issues/1"
GENOME = "sapling"
EPISODE = REPO / "genomes/sapling/nodes/001-capability-inventory"

# What a stranger who arrived from TikTok is owed, in one breath.
PITCH = ("Sapling — the first series growing in Banyan City — is an AI-animated "
         "micro-drama about an engineer who wakes up as a tree. It branches: you "
         "watch, you react, and the story grows a new limb. This page is the "
         "workshop floor — the show being made, live.")
# "beat" and "canon" are translated away in our own labels, but they survive in
# quoted thread comments — so the legend names them once instead of leaving a
# stranger to guess (stranger-eyes audit, 2026-07-30).
LEGEND = ("<b>scene</b> = one shot of an episode (the crew says <b>beat</b>) · "
          "<b>approved</b> = the author picked this scene's frame · "
          "<b>canon</b> = the cut currently leading the story — a working cut "
          "until the author passes it · "
          "<b>take</b> = one attempt at a scene, anyone may hand one in")

# Measured medians from the ledgered runs of 2026-07-27/28, written as
# step → time & money so the two columns actually have names (they used to
# ship headerless under a heading that said "costs" over mostly durations).
STEPS = [
    ("A round of candidate frames for one scene (free GPU)", "~15 min including queue time"),
    ("The author looking at a round and picking a winner", "minutes of attention — the real variable"),
    ("Animating a chosen frame on our own machines", "~1 min · $0"),
    ("Animating a chosen frame with a paid AI service", "~3 min · about $0.28"),
    ("Assembling the whole episode and checking it", "~4 min · $0"),
]
ESTIMATES = STEPS  # older name, kept so nothing importing it breaks


def scenes(d: Path = None) -> list:
    """One dict per scene of the episode — the whole state of the show.

    final       : the author has approved this scene's frame
    candidates  : how many rival frames are waiting for that call
    animations   : which engines have produced a moving version (codenames)
    request     : issue number where anyone can hand one in
    waiting_for : plain-English bottleneck, "" when the scene is done
    """
    d = d or EPISODE
    reqs = {}
    rq = d / "requests.yaml"
    if rq.exists():
        reqs = (yaml.safe_load(rq.read_text()) or {}).get("render_requests", {})
    cand_dir, clip_dir = d / "takes" / "stills", d / "takes" / "clips"
    out = []
    for s in parse_shots((d / "shots.md").read_text()):
        num, slug = s["num"], s["slug"]
        final = (d / "stills" / f"{num:02d}-{slug}.png").exists()
        cands = len(list(cand_dir.glob(f"{num:02d}-*.png"))) if cand_dir.is_dir() else 0
        anims = sorted({t.suffixes[-2].lstrip(".") for t in clip_dir.glob(f"{num:02d}-*.mp4")}) \
            if clip_dir.is_dir() else []
        out.append({
            "num": num,
            "slug": slug,
            "name": slug.replace("-", " "),
            "final": final,
            "candidates": cands,
            "animations": anims,
            "request": reqs.get(num),
            "waiting_for": "" if final else ("the author's pick" if cands else "a render"),
        })
    return out


def growth(rows: list) -> dict:
    """The episode's growth score — two verifiable steps per scene.

    A scene grows twice: its frame is approved by the author, and a moving
    version of it exists. Both are file-existence facts from `scenes()`, so
    the meter on the page can never claim progress the repo cannot show.
    """
    done = sum(1 for r in rows if r["final"]) + sum(1 for r in rows if r["animations"])
    return {"done": done, "total": 2 * len(rows)}


def takes_tally(d: Path = None) -> dict:
    """Every take anyone has ever handed in for this episode, from takes/."""
    d = d or EPISODE
    stills, clips = d / "takes" / "stills", d / "takes" / "clips"
    return {
        "stills": len(list(stills.glob("*.png"))) if stills.is_dir() else 0,
        "clips": len(list(clips.glob("*.mp4"))) if clips.is_dir() else 0,
    }


def vo_scenes(d: Path = None) -> int:
    """How many scenes carry recorded narration (NN-vo.mp3 in clips/)."""
    d = d or EPISODE
    clips = d / "clips"
    return len(list(clips.glob("[0-9][0-9]-vo.mp3"))) if clips.is_dir() else 0


# Where a WHOLE-EPISODE ruling lives. The leaf convention below records an
# approval per node, and it works when the pass arrives as a leaf; episode 1's
# did not. On 2026-08-13 the founder closed the episode out loud — "we have
# already published it dude, we are done. lets move on to episode 2." — recorded
# three times in review/inbox.yaml's `resolved:` entries and carried verbatim and
# dated in this file's `ep1_publication_CORRECTION_0819`. No T3 leaf was ever
# stamped for it, so the leaf test returned False for six days and every page
# built on it kept asking a man to pass a cut he had already published (the same
# defect the correction key describes for /status's per-beat counts, one surface
# over). The ruling is read where it actually lives.
PROGRESS_FILE = REPO / "pipeline" / "measured" / "episode-progress.yaml"


def publication_ruling(path: Path = None) -> dict | None:
    """The founder's recorded whole-episode pass for episode 1, or None.

    Shape-checked rather than trusted: a correction key missing either the date
    or the words he actually said is not a ruling and returns None, so a
    half-written record can never flip a page to "passed".
    """
    try:
        doc = yaml.safe_load((path or PROGRESS_FILE).read_text(
            encoding="utf-8", errors="replace")) or {}
    except Exception:
        return None
    if not isinstance(doc, dict):
        return None
    for key, val in doc.items():
        if not (isinstance(key, str)
                and key.startswith("ep1_publication_CORRECTION_")
                and isinstance(val, dict)):
            continue
        date = str(val.get("ruling_date") or "").strip()
        said = str(val.get("ruling_verbatim") or "").strip()
        if date and said:
            return {"date": date, "verbatim": said,
                    "recorded_in": str(val.get("ruling_recorded_in") or "")}
    return None


def cut_passed(d: Path = None) -> bool:
    """Has the author passed a full cut? True when a T3 leaf carries
    `approved_by: founder` — the same convention T0 scripts already use
    (STEWARDSHIP.md §6) — or when he closed the whole episode and that ruling is
    on the record (`publication_ruling`, above). Until one of those exists the
    page must call the cut 'working'."""
    if publication_ruling():
        return True
    d = d or EPISODE
    for f in (d / "leaves").glob("*.yaml"):
        try:
            meta = yaml.safe_load(f.read_text()) or {}
        except Exception:
            continue
        if str(meta.get("tier")) == "T3" and \
                str(meta.get("approved_by", "")).startswith("founder"):
            return True
    return False


def day_count() -> int:
    """Day N of production — days since the root node was released, from
    lineage.yaml (a repo fact, so the deploy server can compute it). 0 means
    the lineage could not be read and the page should not show a day at all."""
    import datetime
    try:
        nodes = (yaml.safe_load((REPO / f"genomes/{GENOME}/lineage.yaml").read_text())
                 or {}).get("nodes", [])
        root = next(n for n in nodes if not n.get("parent"))
        return (datetime.datetime.now(datetime.timezone.utc).date()
                - root["released"]).days + 1
    except Exception:
        return 0


def request_url(num) -> str:
    """Where a stranger hands in a take for a scene ("open request" on the page)."""
    return f"{GH_URL}/issues/{num}"


def hero(d: Path = None) -> dict:
    """The episode itself — what belongs above everything machine-facing.

    Returns the newest LIVE full-episode video (top tier wins, then the later
    leaf letter), its poster still, and the pages a visitor can go to. Paths are
    relative to _site/ so status.html can play the file build_site.py copies.
    """
    d = d or EPISODE
    slug, media = d.name, f"{GENOME}/{d.name}-media"
    pick = None  # (sortable rank, relative video path)
    for f in sorted((d / "leaves").glob("*.yaml")):
        try:
            meta = yaml.safe_load(f.read_text()) or {}
        except Exception:
            continue
        content = str(meta.get("content", ""))
        if meta.get("status") != "live" or not content.endswith(".mp4"):
            continue
        rank = (str(meta.get("tier", "")) == "T3", f.name)
        if pick is None or rank > pick[0]:
            pick = (rank, f"{GENOME}/leaves/{content}")
    stills = sorted((d / "stills").glob("[0-9]*.png"))
    title = slug.split("-", 1)[-1].replace("-", " ")
    try:  # the author's own title for the episode, never rewritten here (R4)
        for n in (yaml.safe_load((REPO / f"genomes/{GENOME}/lineage.yaml").read_text())
                  or {}).get("nodes", []):
            if n.get("slug") == slug:
                title = n.get("title") or title
                break
    except Exception:
        pass
    return {
        "number": 1,
        "title": title,
        "video": pick[1] if pick else None,
        "poster": f"{media}/{stills[0].name}" if stills else None,
        "page": f"{GENOME}/{slug}.html",
        "board": f"{GENOME}/{slug}-shots.html",
        "watch": "watch.html",
    }


# The next episode's node — 002b "The First Citizen", the branch the studio is
# actually filming (the ep2-* / 002b-* render jobs of 2026-08-10/11). Hardcoded
# the same way EPISODE is above; when the trunk call lands on a different
# branch, this is the one line to move.
NEXT_EPISODE = REPO / "genomes/sapling/nodes/002b-first-citizen"


def next_episode(d: Path = None) -> dict | None:
    """Episode 2's counts for the glance strip — file-existence facts only.

    `started` = scenes with at least one candidate frame handed in (or an
    approved still); `approved` = scenes whose frame carries the author's pick.
    Returns None when the node cannot be read, so the strip simply says
    nothing about a next episode rather than guessing at one.
    """
    d = d or NEXT_EPISODE
    try:
        shots = parse_shots((d / "shots.md").read_text())
    except Exception:
        return None
    if not shots:
        return None
    tdir, sdir = d / "takes" / "stills", d / "stills"
    takes = ({p.name[:2] for p in tdir.glob("[0-9][0-9]-*.png")}
             if tdir.is_dir() else set())
    approved = ({p.name[:2] for p in sdir.glob("[0-9][0-9]-*.png")
                 if "REVOKED" not in p.name} if sdir.is_dir() else set())
    nums = {f"{s['num']:02d}" for s in shots}
    return {"number": 2, "total": len(shots),
            "started": len(nums & (takes | approved)),
            "approved": len(nums & approved),
            "board": f"{GENOME}/{d.name}-shots.html"}


def summary(rows: list) -> dict:
    """The one line that replaces fifteen near-identical table rows."""
    return {
        "total": len(rows),
        "final": sum(1 for r in rows if r["final"]),
        "awaiting_render": sum(1 for r in rows if r["waiting_for"] == "a render"),
        "awaiting_pick": sum(1 for r in rows if r["waiting_for"] == "the author's pick"),
    }


def spend() -> float:
    """Lifetime cash actually billed by any render provider, from the ledger."""
    total = 0.0
    led = REPO / "ledger" / "render-spend.csv"
    if not led.exists():
        return total
    for line in led.read_text().splitlines()[1:]:
        if line.strip():
            try:
                total += float(line.split(",")[5])
            except (ValueError, IndexError):
                pass
    return total


# ---- the infra meter (D18's second obligation) --------------------------------
# On 2026-08-08 this project billed over $100 of Vercel build time in under a
# month, because every courier heartbeat and every 5-minute telemetry pulse
# triggered a full site rebuild on a branch nobody reads: 2,344 courier pushes in
# 29 days, 78% of all builds non-main. The ref allowlist stopped the spending.
# D18 also says a metered service gets a monitoring line, and it had none — the
# meter ran for a month with nothing anywhere in this repo reporting it, which is
# why an invoice was the first anyone knew.
#
# BUILD TRIGGERS, NOT DOLLARS, and the difference is the whole design. Nobody has
# a $0 source for the money: the new account is a cardless Hobby team and no
# usage endpoint on it is known to be free (unverified — and buying a plan to
# read a spend number would be the joke writing itself). Vercel's git integration
# creates a GitHub DEPLOYMENT per build, and that list is public, free, and
# CORS-enabled. Trigger count is therefore the number we can actually verify, and
# it is also the number that went wrong.
#
# FETCHED BY THE READER'S BROWSER, like the machines' logs and the render box's
# vitals (LIVE_JS in build_sim). A build-time read would make the meter as fresh
# as the last deploy — and the failure being watched for is a flood of deploys,
# so a counter that only advances when one happens is the wrong instrument. The
# deploy server also has no `gh` CLI and no local refs, so this was never going
# to be a repo fact.
DEPLOY_API = f"https://api.github.com/repos/{GH_URL.split('github.com/')[-1]}/deployments"

# A DAY, NOT A MONTH, and the reason is arithmetic rather than preference. One
# unauthenticated request returns at most 100 deployments and the readers of this
# page share a 60-request hour by IP, so paging a whole month would cost eight
# requests a view and take the meter down for everybody. At the rate this repo
# actually builds, 100 production deployments reach back about four days —
# measured 2026-08-09: 100 rows spanning 08-05 to 08-09 — so a 24-hour window
# fits inside one page with room, and stops being a window only when the rate
# doubles, which is the alarm rather than a gap. `environment=Production` is
# filtered SERVER-side because two thirds of this repo's deployments are the free
# github-pages mirror, and counting those would inflate a bill nobody is paying.
METER_HOURS = 24
DEPLOY_PER_PAGE = 100


def infra_meter() -> dict:
    """Copy + source for the infra tile. No numbers: this module cannot know one.

    Every string the tile can show lives here, including the ones for failure.
    SITE.md's honesty rule bites hardest on a meter: an unavailable number is
    said in words, never filled in from the last build and never estimated — a
    stale meter is worse than no meter, because it reads as reassurance on
    exactly the failure it exists to catch.
    """
    return {
        "api": f"{DEPLOY_API}?environment=Production&per_page={DEPLOY_PER_PAGE}",
        "hours": METER_HOURS,
        "page": DEPLOY_PER_PAGE,
        "title": "Site builds in the last 24 hours",
        "counting": "counting them now…",
        "unavailable": "GitHub did not answer, so this page will not put a "
                       "number on it",
        "unit_one": "build of this site was triggered in the last 24 hours",
        "unit_many": "builds of this site were triggered in the last 24 hours",
        "note": "Every one of these is billable build time on the host. In July "
                "an automated push every five minutes triggered a build each "
                "time — over $100 in under a month, publishing nothing new — so "
                "builds are now limited to the main branch and this is the line "
                "that would show it happening again. It counts triggers and not "
                "dollars because the trigger count is the number checkable from "
                "a free, public source: the host publishes no spend figure this "
                "page can read without paying for a plan. Read live from "
                f"GitHub's own record of the last {DEPLOY_PER_PAGE} production "
                "builds; a figure shown with a + means there were more than this "
                "page could see, which is itself the warning.",
    }


def _inbox_id(e: dict) -> str:
    """A stable id for a board entry, which writes none of its own.

    `founder_gate_map` attaches parked queue work to a call by finding the
    call's id inside a backlog entry's `gate_ref`, so the ids have to be
    nameable in prose. Derived from the entry's own `url` — the one field the
    board writes per entry — and from nothing else: an id invented from the
    text would change every time the text is reworded, which is how a gate_ref
    stops matching the thing it names.
    """
    u = str(e.get("url") or "").strip()
    if u.lower().startswith("local:"):
        u = u.split(":", 1)[1].strip()
    slug = u.rstrip("/").rpartition("/")[2]
    return slug.rpartition(".")[0] if "." in slug else slug


def _inbox_halves(text) -> tuple:
    """(headline, the rest) — a board entry's own words, split, never rewritten.

    The board writes one paragraph per entry and the status page has a bold
    line and a quiet one under it. The headline is the paragraph's first
    sentence and the rest is the remainder verbatim; a run of dots is an
    elision and not a full stop, the same rule `build_sim.first_sentence`
    applies to every other sentence this site prints.
    """
    t = re.sub(r"\.{2,}", "…", " ".join(str(text or "").split()))
    head, sep, rest = t.partition(". ")
    return (head if sep else t.rstrip(". ")), rest.strip()


def inbox() -> list:
    """The author's decision queue — the OPEN entries of `review/inbox.yaml`.

    THIS READ USED TO POINT AT `pipeline/pending-founder.yaml`, and that is the
    defect the founder reported four times over. That file was RETIRED on
    2026-08-14 — it says so in its own `retired:` block, naming
    review/inbox.yaml as its successor — and all four of its entries carry a
    `resolved:` disposition. This function filtered on nothing, so /status's
    "Waiting on the author" kept printing all four as open and aging them off
    their own `since:` dates: the guards call in wording superseded on 08-14, a
    beat-04 length call superseded the same day, the episode-1 frame pick he
    closed with "we have already published it dude, we are done" (08-13), and
    the script read he abolished outright ("lets not waste time by having me
    read the entire script", 08-13). The same build was already reading the live
    board correctly in `build_sim.review_inbox_open()`, so the strip's own cell
    said 2 waiting while the section under it listed 4 — the page disagreed
    with itself, out of two files, in one build.

    An entry is open until it carries `resolved:`. That is the one test
    `review/inbox/regen.py` and `review_inbox_open()` apply, so the board, the
    count on the tile and this section cannot drift apart about what is
    waiting; there is now one file to answer, and answering it anywhere
    answers it everywhere.

    Returned in the shape `waiting_html` renders, with nothing invented: the
    headline and the line under it are the entry's own `what`, split, and the
    age is measured from the entry's own `since`. A `local:` url names a file on
    a render machine rather than a page, so it is not offered as a link — its
    `fallback_url` is, when the entry writes one.
    """
    try:
        doc = yaml.safe_load((REPO / "review/inbox.yaml").read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(doc, list):
        return []
    out = []
    for e in doc:
        if not isinstance(e, dict) or e.get("resolved"):
            continue
        head, rest = _inbox_halves(e.get("what"))
        url = str(e.get("url") or "").strip()
        if url.lower().startswith("local:"):
            url = str(e.get("fallback_url") or "").strip()
        out.append({
            "id": _inbox_id(e),
            "title": head,
            # His own continuation when he wrote one; otherwise what answering
            # this looks like, which is the only other line the board carries.
            "detail": rest or str(e.get("verdict_hint") or ""),
            "public": url or None,
            "link_text": e.get("link_text"),
            "since": e.get("since"),
            "group": e.get("group"),
        })
    return out


def build(out_dir: Path):
    """Kept so build_site.py's call order stays valid. The page is written by
    build_sim.build() — which reads this module — so there is exactly one
    generator for _site/status.html."""
    from build_sim import build as build_page
    build_page(out_dir)


if __name__ == "__main__":
    build(REPO / "_site")
