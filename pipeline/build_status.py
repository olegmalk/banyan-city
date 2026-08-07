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
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from generate_shots import parse_shots  # noqa: E402

GH_URL = "https://github.com/olegmlkvorg/banyan-city"
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


def cut_passed(d: Path = None) -> bool:
    """Has the author passed a full cut? True only when a T3 leaf carries
    `approved_by: founder` — the same convention T0 scripts already use
    (STEWARDSHIP.md §6). Until then the page must call the cut 'working'."""
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


def inbox() -> list:
    """The author's decision queue — written for strangers in the yaml itself."""
    try:
        return (yaml.safe_load((REPO / "pipeline/pending-founder.yaml").read_text())
                or {}).get("pending") or []
    except Exception:
        return []


def build(out_dir: Path):
    """Kept so build_site.py's call order stays valid. The page is written by
    build_sim.build() — which reads this module — so there is exactly one
    generator for _site/status.html."""
    from build_sim import build as build_page
    build_page(out_dir)


if __name__ == "__main__":
    build(REPO / "_site")
