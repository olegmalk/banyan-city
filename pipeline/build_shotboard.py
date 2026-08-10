#!/usr/bin/env python3
"""The shot board — every beat's full generation recipe, forkable by anyone.

D11 (founder, 2026-07-27): the main artifact is a multiplayer system — people
take the inputs (approved still + exact prompts + settings), generate with
their OWN accounts and credits on any platform, and submit their take of a
beat. The beat (~4s) is the fork unit. This builder renders that interface:
one page per node showing, for every beat, everything needed to reproduce or
beat the current take. Transparency is the interface, not just the record
(§7.2).

    python3 pipeline/build_shotboard.py sapling 001 [--out shotboard-001.html]

Taste verdicts stay the founder's (R4): the board widens the option pool,
screening decides what the show keeps.

Design (2026-07-30 redesign): same data, three tiers. The episode plays first
with a plain-English line, then a filmstrip index of the shots, then per shot
the take that is IN the episode, the alternates, and the recipe one tap down.
The contributor instructions live ONCE (#submit) instead of once per beat, and
the page speaks stranger English — no D-numbers, no R-numbers, no bare tags.
"""

import argparse
import base64
import yaml
import html
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
import licence_gate as lg  # noqa: E402 — the tolerant sidecar reader
import repo_slug  # noqa: E402  one source for "which repo is this"
from generate_shots import parse_shots  # noqa: E402
from sd_prompt import compress, extra_negatives, suppressed_negatives  # noqa: E402
from site_theme import THEME_CSS  # noqa: E402  — one palette for every page

# What the Kaggle notebook actually sends — keep in sync with render-kaggle.ipynb.
NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, low quality, "
       "blurry, extra limbs, deformed, jpeg artifacts, realistic skin texture")
STILL_MODEL = "cagliostrolab/animagine-xl-3.1"
STILL = {"width": 832, "height": 1216, "steps": 40, "cfg": 7.5, "seed_base": 20260719}
MOTION = {"engine": "LTX-Video (Lightricks/LTX-Video) under evaluation; "
                    "prior takes: Stable Video Diffusion",
          "size": "512x768", "note": "commercial platforms are welcome — Kling, Veo, "
          "Pika, Runway: start from the SAME frame and prompt, and say what you used"}

CANONICAL = "https://banyan.city"       # same host build_site.py publishes to
GH_REPO = repo_slug.GH_REPO       # pipeline/repo_slug.py — never hardcode the owner
REPO_URL = repo_slug.REPO_URL

# Bare uppercase filename tags are meaningless to a stranger. Name the engine,
# and say in one clause why it was tried at all.
ENGINES = {
    "POST":      ("In-house code (no AI motion)",
                  "python moves the approved frame — a push-in, a glow, a fade. $0, "
                  "identical every run, and the floor every AI take has to beat."),
    "HAILUO":    ("MiniMax Hailuo 2.3",
                  "paid image-to-video via fal.ai — the strongest hand motion so far."),
    "PIXVERSE":  ("PixVerse V6",
                  "contributed from someone else's free web account."),
    "PIXVERSE2": ("PixVerse V6 — second attempt",
                  "re-shot by the same contributor after the first read wrong on screen."),
    "LTX":       ("LTX-Video",
                  "free GPU on Kaggle — fast, and the cheapest way to test a motion note."),
    "LTX2":      ("LTX-Video — second attempt",
                  "same engine, different settings."),
    "SVD":       ("Stable Video Diffusion",
                  "the first free engine the show ran on; kept as the baseline."),
    "WAN":       ("Alibaba Wan 2.7",
                  "free provider quota, since spent."),
    "VEO":       ("Google Veo",
                  "photoreal pilot footage, kept only as evidence of the old look."),
    "KLING":     ("Kling",
                  "commercial engine, submitted with provenance."),
}


def engine_label(tag: str) -> tuple:
    """Filename tag → (human engine name, one clause on why it was tried)."""
    return ENGINES.get(tag.upper(), (tag, "submitted with its own provenance sidecar."))


def beat_neg(prompt: str) -> str:
    neg = NEG
    for term in suppressed_negatives(prompt):
        neg = neg.replace(term + ", ", "")
    extra = extra_negatives(prompt)
    return f"{neg}, {extra}" if extra else neg


def neg_delta(prompt: str) -> str:
    """The only interesting part of a negative prompt: this beat's changes to the
    shared baseline. The full string still ships, one tap down."""
    bits = []
    dropped = [t for t in suppressed_negatives(prompt) if t + ", " in NEG]
    if dropped:
        bits.append("− " + ", ".join(dropped))
    extra = extra_negatives(prompt)
    if extra:
        bits.append("+ " + extra)
    return " · ".join(bits) or "the shared baseline, unchanged"


FFMPEG = shutil.which("ffmpeg")          # optional: no ffmpeg → full-size images
_THUMBS: dict = {}


def _site_build():
    """The build_site module currently running, if any — it owns _site/ and knows
    where media was copied. Looked up instead of imported so the standalone CLI
    (and any build_site without these helpers) degrades instead of failing."""
    for name in ("build_site", "__main__"):     # imported, or run as the script
        mod = sys.modules.get(name)
        if mod and getattr(mod, "_POSTERS", None) is not None:
            return mod
    return None


def _scale(src: Path, dst: Path, width: int) -> bool:
    """ffmpeg one image down to `width`, JPEG. False on any failure."""
    if not (FFMPEG and src.exists()):
        return False
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-i", str(src),
                        "-vf", f"scale={width}:-2", "-q:v", "5", str(dst)],
                       check=True, timeout=90)
        return dst.exists() and dst.stat().st_size > 0
    except Exception:
        return False


def still_thumb(src: Path, rel_name: str, width: int = 480) -> str:
    """A ~480px JPEG of one approved frame, written beside the page's posters.

    The sources are 832×1216 PNGs at ~1.2 MB each; fifteen of them is 18 MB of
    page for pictures shown 240–320px wide. The full-resolution PNG stays one
    tap away — this only changes what loads unasked. Returns "" when there is
    no ffmpeg or no _site/ to write into, and the caller falls back to the PNG.
    """
    if rel_name in _THUMBS:
        return _THUMBS[rel_name]
    mod = _site_build()
    out = getattr(mod, "OUT", None) if mod else None
    got = ""
    if out is not None and out.exists() and _scale(src, out / rel_name, width):
        got = f"../{rel_name}"
    _THUMBS[rel_name] = got
    return got


def _embed(p: Path, width: int = 480) -> str:
    """Standalone mode: a downscaled JPEG data-URI, or the raw PNG if no ffmpeg.
    Base64 of 15 source PNGs is a ~24 MB HTML file; nobody opens that twice."""
    with tempfile.TemporaryDirectory() as td:
        jpg = Path(td) / "t.jpg"
        if _scale(p, jpg, width):
            return f"data:image/jpeg;base64,{base64.b64encode(jpg.read_bytes()).decode()}"
    return f"data:image/png;base64,{base64.b64encode(p.read_bytes()).decode()}"


def img_tag(p: Path, rel: str = "", alt: str = "", thumb: str = "") -> str:
    """rel="" embeds base64 (self-contained local file); rel=prefix links the
    copied file instead — the site build copies media next to the page.
    `thumb` (a build-time 480px JPEG) is preferred as the src when present.
    Intrinsic size + lazy loading: 15 full-resolution stills must not all land
    on a phone at once (they are ~1.2 MB each)."""
    if not p.exists():
        return '<div class="noimg">no approved frame yet — this one is still in review</div>'
    dims = f'width="{STILL["width"]}" height="{STILL["height"]}"'
    a = html.escape(alt or p.name)
    if rel:
        return (f'<img {dims} loading="lazy" decoding="async" '
                f'src="{thumb or f"{rel}/{p.name}"}" alt="{a}">')
    return (f'<img {dims} loading="lazy" decoding="async" '
            f'src="{_embed(p)}" alt="{a}">')


def take_meta(v: Path) -> dict:
    """The sidecar next to a take — provenance, and who handed it in.

    BOTH NAMING SHAPES (lg.sidecar_for, 2026-08-07). The old lookup built one
    name by hand — 01-the-keyboard.HAILUO.mp4 → 01-the-keyboard.HAILUO.meta.yaml
    — which is right for the records intake_take writes and blind to the
    `<full name>.mp4.meta.yaml` shape hold_still, video_task and the farm worker
    write. This is the crowd-facing board, so a miss is the §7.2 promise
    silently unmet: the take still plays, with no engine credit and no
    contributor beside it, exactly as if nobody had recorded anything."""
    m = lg.sidecar_for(v, lg.META_EXT)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.read_text()) or {}
    except Exception:
        return {}


def take_list(takes_clips: Path, num: int, slug: str) -> list:
    """Every motion take filed for a beat."""
    if not takes_clips.is_dir():
        return []
    return sorted(takes_clips.glob(f"{num:02d}-{slug}.*.mp4"))


def poster_for(src: Path, rel_name: str) -> str:
    """A 360px still frame for one clip, via the site build's shared extractor.

    Only used when build_site is the thing running (site mode) — this never
    imports it, so the standalone CLI and any build_site without the helper
    simply get players with no poster instead of a hard failure.
    """
    mod = _site_build()
    fn = getattr(mod, "poster", None) if mod else None
    if not fn:
        return ""
    try:
        got = fn(src, rel_name)
    except Exception:
        return ""
    return f"../{got}" if got else ""


def take_cell(v: Path, rel: str, poster_url: str, canon: bool) -> str:
    """One take: a real player, a human engine name, its credit and its receipt.

    preload="none" (+ a light poster frame where one could be extracted) means
    nothing downloads until someone taps — 27 clips were ~31 MB on page load.
    """
    tag = v.suffixes[-2].lstrip(".")
    name, why = engine_label(tag)
    meta = take_meta(v)
    by = str(meta.get("contributed_by") or "").strip()
    credit = (f'<br><span class="by">handed in by '
              f'<a href="https://github.com/{html.escape(by)}">@{html.escape(by)}</a></span>'
              if by else "")
    poster = f' poster="{poster_url}"' if poster_url else ""
    crown = '<span class="chip-canon">IN THE EPISODE</span><br>' if canon else ""
    # only link a receipt that exists — POST clips have no engine-tagged
    # sidecar, so fall back to the beat's base meta, and to nothing over a 404.
    # Both lookups go through lg.sidecar_for for the reason take_meta does: the
    # hand-built name only ever found `<stem>.meta.yaml`, so a take filed with a
    # full-name record showed no "exact settings used" link at all. Safe to link
    # either shape — build_site copies takes/clips/ with iterdir(), so whichever
    # file is found travels to _site under its own name.
    stem = v.with_suffix("").name
    sidecar = lg.sidecar_for(v, lg.META_EXT)
    base = lg.sidecar_for(v.with_name(f"{stem.rsplit('.', 1)[0]}.mp4"), lg.META_EXT)
    if sidecar:
        receipt = f'<br><a href="{rel}-clips/{sidecar.name}">exact settings used</a>'
    elif base:
        receipt = f'<br><a href="{rel}-clips/{base.name}">exact settings used</a>'
    else:
        receipt = ""
    # A take whose licence forbids publication is LISTED but not playable: the
    # file is never copied to _site, so a <video> pointing at it would be a
    # broken player (and the link gate rightly fails the build over it). Saying
    # so beats both hiding the take and shipping a dead frame — the recipe and
    # the receipt are still right here for anyone who wants to beat it.
    from build_site import publishable
    ok, blocked = publishable(v)
    player = (f'<video preload="none"{poster} controls muted loop playsinline '
              f'src="{rel}-clips/{v.name}"></video>' if ok else
              f'<div class="withheld"><b>not published here</b><br>'
              f'{html.escape(blocked)}<br>'
              f'<span>the take exists in the repo; this beat is open to a '
              f're-shoot on a publish-safe route</span></div>')
    return (f'<figure class="take{" canon" if canon else ""}">'
            f'{player}'
            f'<figcaption>{crown}'
            f'<b>{html.escape(name)}</b>{credit}'
            f'<br><span class="why">{html.escape(why)}</span>'
            f'{receipt}</figcaption></figure>')


def beat_notes(shots_md: str) -> dict:
    """num → the human note between the beat heading and its prompt fence —
    the INTENT ('Line: ... Camera on ...') a voter needs to judge any image."""
    notes = {}
    heads = list(re.finditer(r"^## Beat (\d+) — [^\n]*$", shots_md, re.M))
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(shots_md)
        body = shots_md[h.end():end]
        fence = body.find("```")
        note = body[:fence if fence >= 0 else len(body)].strip()
        notes[int(h.group(1))] = note
    return notes


def split_note(note: str) -> tuple:
    """(dialogue, intent, backstory) — the note's own three registers, unedited.

    Line one is audience-facing: an optional spoken line, then the camera intent.
    Anything after it is production history ('three rejected rounds proved…') and
    belongs one fold down, not in a stranger's face."""
    first, _, rest = note.partition("\n")
    dialogue = ""
    m = re.match(r"Line:\s*['\"](.+?)['\"]\s*", first.strip())
    if m:
        dialogue, first = m.group(1), first.strip()[m.end():]
    return dialogue.strip(), " ".join(first.split()), " ".join(rest.split())


def beat_heads(shots_md: str) -> dict:
    """num → {title, span} carried verbatim from '## Beat NN — TITLE (m:ss–m:ss)'.

    The written title is the film's shot name ("HUH. GREEN."); the slug is a
    filename ("huh-green"). Headings get the title."""
    out = {}
    for h in re.finditer(r"^## Beat (\d+) — ([^\n]*)$", shots_md, re.M):
        num, rest = int(h.group(1)), h.group(2)
        m = re.search(r"\((\d+:\d\d)\s*[–—-]\s*(\d+:\d\d)\)", rest)
        title = (rest[:m.start()] if m else re.split(r"[✅⬜]", rest)[0]).strip()
        out[num] = {"title": title, "span": (m.group(1), m.group(2)) if m else None}
    return out


def _secs(t: str) -> int:
    m, s = t.split(":")
    return int(m) * 60 + int(s)


def episode_leaf(d: Path) -> dict:
    """The newest live full-video render of this node — the cut on the site."""
    leaves = d / "leaves"
    if not leaves.is_dir():
        return {}
    best = {}
    for y in sorted(leaves.glob("*.yaml")):          # …t3-a, t3-b, t3-c, t3-d
        try:
            m = yaml.safe_load(y.read_text()) or {}
        except Exception:
            continue
        if (str(m.get("tier")) == "T3" and m.get("status") == "live"
                and str(m.get("content", "")).endswith(".mp4")):
            best = m
    return best


def canon_clips(leaf: dict) -> dict:
    """beat → {take filenames} the published cut actually used. This is what
    lets the board crown one take 'IN THE EPISODE' instead of showing six
    equal black rectangles."""
    out = {}
    for s in leaf.get("sources") or []:
        try:
            b = int(s.get("beat"))
        except (TypeError, ValueError):
            continue
        out[b] = {p.strip() for p in str(s.get("clip", "")).split("+") if p.strip()}
    return out


def variant_cell(f: Path, letter: str, num: int, rel: str, genome: str) -> str:
    """One candidate frame in site mode — linked, or named as not published.

    The publishable() half is take_cell's rule applied to pictures, which it was
    missing: a still whose licence forbids redistribution is never copied to
    _site, so linking it is a 404 in a visitor's face and a build the link gate
    fails. Same answer as for a clip — say so, keep the recipe visible, invite
    the re-shoot.
    """
    from build_site import publishable
    ok, blocked = publishable(f)
    if not ok:
        return (f'<figure class="take"><div class="withheld">'
                f'<b>not published here</b><br>{html.escape(blocked)}<br>'
                f'<span>the frame exists in the repo; this beat is open to a '
                f're-shoot on a publish-safe route</span></div>'
                f'<figcaption><b>{letter}</b></figcaption></figure>')
    thumb = still_thumb(f, f"{genome}/posters/cand-{f.stem}.jpg", 360)
    return (f'<figure class="take"><a href="{rel}-takes/{f.name}">'
            f'<img width="{STILL["width"]}" height="{STILL["height"]}" '
            f'loading="lazy" decoding="async" '
            f'src="{thumb or f"{rel}-takes/{f.name}"}" '
            f'alt="candidate {letter} for shot {num:02d}"></a>'
            f'<figcaption><b>{letter}</b></figcaption></figure>')


def variant_cells(takes_stills: Path, num: int, rel: str, genome: str = "") -> str:
    """Candidate stills for an unapproved beat, labelled A/B/C…, votable.

    Thumbnailed like the approved frames: these are the same 1.2 MB PNGs, and a
    beat in review can have four of them.

    SITE MODE LISTS ONLY WHAT THE DEPLOY HAS (2026-08-08). Candidate frames are
    gitignored by design, so on the box that drew them this globbed 185 PNGs and
    emitted 164 <a href>s to files that are not in the tree — links that 404 on
    banyan.city and that failed the local build while CI, lacking the files
    entirely, stayed green. Standalone mode (rel="") is deliberately NOT
    filtered: the local board embeds base64 and its whole reason to exist is
    looking at exactly those uncommitted candidates in review.
    """
    if not takes_stills.is_dir():
        return ""
    files = sorted(f for f in takes_stills.glob(f"{num:02d}-*.png"))
    if rel:
        from build_site import in_the_tree
        files = in_the_tree(files)
    if not files:
        return ""
    cells = "".join(
        variant_cell(f, chr(65 + i), num, rel, genome) if rel else
        f'<figure class="take">{img_tag(f, alt=f"candidate {chr(65 + i)}")}'
        f'<figcaption><b>{chr(65 + i)}</b></figcaption></figure>'
        for i, f in enumerate(files))
    return ('<h3>Candidate frames — vote for one</h3>'
            f'<div class="takes">{cells}</div>')


def node_title(d: Path) -> str:
    """'# Node 001 — Capability Inventory' → 'Capability Inventory'."""
    try:
        first = (d / "node.md").read_text().splitlines()[0]
    except Exception:
        return d.name
    return first.split("—")[-1].strip().lstrip("# ").strip() or d.name


def node_hook(d: Path) -> str:
    """The episode's own one-line hook, verbatim (story text — never rewritten)."""
    try:
        md = (d / "node.md").read_text()
    except Exception:
        return ""
    m = re.search(r"^## Hook[^\n]*\n+(.+?)(?:\n\n|\n#)", md, re.M | re.S)
    if not m:
        return ""
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", m.group(1))
    return " ".join(re.sub(r"[*_`>#]", "", t).split())


def episode_label(d: Path) -> str:
    """'001-capability-inventory' → 'EPISODE 1'; '002b-…' → 'EPISODE 2B'."""
    m = re.match(r"(\d+)([a-z]?)", d.name)
    return f"EPISODE {int(m.group(1))}{m.group(2).upper()}" if m else d.name.upper()


# ------------------------------------------------------------------ page css --
# Appended after THEME_CSS — page-specific rules only, never a second palette.
BOARD_CSS = """
/* ---- the shot board: a contributor's workbench that still reads on a phone ---- */
main { max-width: 900px; }
figure { margin: 0; }
code, pre { overflow-wrap: anywhere; word-break: break-word; }
pre { white-space: pre-wrap; }

/* sticky shot index + a pure-CSS read-progress hairline */
.railwrap { position: sticky; top: 0; z-index: 1; margin: 0 -1.25rem 1.4rem;
  background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border-bottom: 1px solid var(--line); }
.rail { display: flex; gap: .15rem; overflow-x: auto; padding: .45rem 1.25rem;
  font: 700 .72rem/1 var(--mono); scrollbar-width: none; }
.rail::-webkit-scrollbar { display: none; }
.rail a { flex: 0 0 auto; padding: .42rem .5rem; border-radius: 8px; color: var(--muted); }
.rail a:hover { color: var(--sap-ink); background: var(--sap); text-decoration: none; }
.rail .lbl { flex: 0 0 auto; padding: .42rem .45rem .42rem 0; color: var(--faint);
  letter-spacing: .16em; text-transform: uppercase; }
.prog { height: 3px; background: var(--sap); transform-origin: 0 50%; opacity: 0; }
@supports (animation-timeline: scroll()) {
  .prog { opacity: 1; animation: readprog linear both; animation-timeline: scroll(); }
}
@keyframes readprog { from { transform: scaleX(0); } to { transform: scaleX(1); } }

/* the visual index: 15 shots as one filmstrip */
.strip { display: flex; gap: .4rem; overflow-x: auto; padding: .2rem 0 .9rem; }
.strip a { flex: 0 0 74px; text-align: center; color: var(--faint);
  font: 700 .6rem/1.9 var(--mono); }
.strip img, .strip .ph { width: 74px; aspect-ratio: 2 / 3; object-fit: cover; display: block;
  border-radius: 8px; border: 1px solid var(--line); background: var(--code-bg); }
.strip a:hover { color: var(--sap); text-decoration: none; }
.strip a:hover img { border-color: var(--sap); }

/* one shot */
.beat { border-top: 1px solid var(--line); margin-top: 2.8rem; padding-top: 1.3rem;
  scroll-margin-top: 3.4rem; }
.beat h2 { margin: .15rem 0 .7rem; font-size: clamp(1.25rem, 5vw, 1.6rem); }
.beat h3 { margin: 1.4rem 0 .5rem; font-family: var(--mono); font-size: .78rem;
  letter-spacing: .12em; text-transform: uppercase; color: var(--faint); font-weight: 700; }
.intent { color: var(--muted); font-size: .98rem; margin: .5rem 0 .2rem; }
.media { max-width: 320px; margin: 1rem 0; }
.media figcaption, .take figcaption { font: 600 .7rem/1.5 var(--mono); color: var(--faint);
  margin-top: .45rem; }
.media img, .noimg { width: 100%; height: auto; display: block; border-radius: 12px;
  border: 1px solid var(--line); background: var(--code-bg); }
abbr[title] { text-decoration: underline dotted; cursor: help; }
.noimg { aspect-ratio: 2 / 3; display: flex; align-items: center; justify-content: center;
  padding: .8rem; text-align: center; color: var(--faint); font: 600 .72rem/1.5 var(--mono); }

/* takes: 1-up on the narrowest phone, 2-up at 390px, 3–4-up on a desktop */
.takes { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: .8rem; margin: .6rem 0 .2rem; }
.takes.lead { max-width: 300px; }   /* the crowned take gets phone width, not 900px */
.take video { width: 100%; aspect-ratio: 9 / 16; object-fit: contain; display: block;
  background: var(--code-bg); border: 1px solid var(--line); border-radius: 12px; }
.take img { width: 100%; aspect-ratio: 2 / 3; object-fit: cover; display: block;
  background: var(--code-bg); border: 1px solid var(--line); border-radius: 12px; }
.take.canon video { border-color: var(--sap);
  box-shadow: 0 0 44px -18px rgba(255,199,106,.75); }
/* a take we may not publish: same footprint as the player it replaces, so the
   grid does not reflow, and legible enough to be read as an invitation */
.take .withheld { width: 100%; aspect-ratio: 9 / 16; display: flex; gap: .5rem;
  flex-direction: column; align-items: center; justify-content: center;
  text-align: center; padding: 1rem; box-sizing: border-box; font-size: .82rem;
  line-height: 1.45; color: var(--muted); background: var(--code-bg);
  border: 1px dashed var(--line); border-radius: 12px; }
.take .withheld b { color: var(--ink); font-size: .9rem; }
.take .withheld span { opacity: .8; }
.chip-canon { display: inline-block; font: 700 .62rem/1 var(--mono); letter-spacing: .1em;
  color: var(--sap-ink); background: var(--sap); padding: .3rem .5rem; border-radius: 999px;
  margin-bottom: .3rem; }
.by { color: var(--muted); }
.why { color: var(--faint); }

/* the recipe, one tap down: mono, dense, complete */
.recipe .k { font: 700 .72rem/1.9 var(--mono); letter-spacing: .08em; text-transform: uppercase;
  color: var(--faint); }
.recipe pre { margin: .3rem 0 1rem; }
.recipe details { margin: .2rem 0 1rem; }
.recipe summary { cursor: pointer; color: var(--leaf); font: 600 .8rem/1.6 var(--mono); }
.actions { margin: 1.1rem 0 .3rem; }
.actions .also { font: 600 .78rem/1.9 var(--mono); color: var(--faint); }
.request, .vote { font-size: .95rem; }
.steps { padding-left: 1.2rem; }
.steps li { margin: .55rem 0; }
.steps b { color: var(--ink); }
.cost { font: 600 .78rem/1.6 var(--mono); color: var(--faint); }
@media (min-width: 640px) { .strip a { flex-basis: 86px; } .strip img, .strip .ph { width: 86px; } }
"""


def board_html(genome: str, d: Path, rel: str = "") -> str:
    """The full page HTML. rel='' → self-contained (base64); rel='NAME' → site
    mode, images at NAME/ and clips at NAME-clips/ next to the page."""
    raw = (d / "shots.md").read_text()
    _mo = d / "motion.yaml"
    motion_prompts = ((yaml.safe_load(_mo.read_text()) or {}).get("motion_prompts", {})
                      if _mo.exists() else {})
    _rq = d / "requests.yaml"
    requests = ((yaml.safe_load(_rq.read_text()) or {}).get("render_requests", {})
                if _rq.exists() else {})
    shots = parse_shots(raw)
    notes = beat_notes(raw)
    heads = beat_heads(raw)
    stills_dir = d / "stills"
    try:
        vote_url = yaml.safe_load((d / "sap" / "reactions.yaml").read_text())["url"]
    except Exception:
        vote_url = ""

    leaf = episode_leaf(d)
    canon = canon_clips(leaf)
    ep_video = str(leaf.get("content", "")) if leaf else ""
    title = node_title(d)
    label = episode_label(d)
    node_page = f"{d.name}.html"
    # '{n}' is a placeholder the per-shot buttons fill with their own number —
    # one prefilled issue form instead of fifteen copies of the instructions.
    submit_new = (f"{REPO_URL}/issues/new?title=take%3A%20{d.name}%20beat%20"
                  "{n}&amp;body=Beat%3A%20{n}%0AWhat%20I%20used%3A%20%0ALink%20to%20"
                  "my%20clip%3A%20%0AAnything%20I%20changed%3A%20")

    # ---- the page's own honest numbers (a build date is not a fact a viewer can use)
    spans = [heads[s["num"]]["span"] for s in shots if heads.get(s["num"], {}).get("span")]
    runtime = f"{_secs(spans[-1][1]) // 60}:{_secs(spans[-1][1]) % 60:02d}" if spans else ""
    approved_n = sum(1 for s in shots
                     if (stills_dir / f"{s['num']:02d}-{s['slug']}.png").exists())
    all_takes = {s["num"]: take_list(d / "takes" / "clips", s["num"], s["slug"])
                 for s in shots}
    if rel:
        # Same rule as the candidate frames, for the same reason: takes/clips/
        # mp4s are gitignored too (001's committed archive excepted), and a
        # <video src> or a receipt link into a clip the deploy does not have is
        # the identical dangling reference. It has not bitten yet only because
        # every clip on the board today happens to be one of 001's tracked ones
        # — which is luck, not a rule. This is the rule.
        from build_site import in_the_tree
        all_takes = {n: in_the_tree(v) for n, v in all_takes.items()}
    # The take a shot leads with, and its extracted 360px frame. The frame does
    # double duty: the player's poster AND the filmstrip thumbnail, so the index
    # costs ~20 KB a shot instead of a 1.2 MB source PNG apiece.
    leads, thumbs = {}, {}
    for s in shots:
        n = s["num"]
        cn = canon.get(n, set())
        crowned = [v for v in all_takes[n] if v.name in cn]
        others = [v for v in all_takes[n] if v.name not in cn]
        lead, rest = (crowned, others) if crowned else (others[:1], others[1:])
        leads[n] = (lead, rest, bool(crowned))
        if rel and lead:
            thumbs[n] = poster_for(lead[0], f"{genome}/posters/take-{lead[0].stem}.jpg")
    # A 480px JPEG of every approved frame — what a phone actually downloads.
    # The 832×1216 PNG stays linked under each picture and in its own folder.
    sthumbs = {}
    if rel:
        for s in shots:
            st = stills_dir / f"{s['num']:02d}-{s['slug']}.png"
            if st.exists():
                sthumbs[s["num"]] = still_thumb(st, f"{genome}/posters/still-{st.stem}.jpg")
    n_takes = sum(len(v) for v in all_takes.values())
    engines = {v.suffixes[-2].lstrip(".").upper() for vs in all_takes.values() for v in vs}
    handed = {str(take_meta(v).get("contributed_by") or "").strip()
              for vs in all_takes.values() for v in vs}
    handed.discard("")
    facts = [f"{len(shots)} shots"]
    if runtime:
        facts.append(f"scripted length {runtime}")  # the cut's real runtime can differ
    facts.append(f"{approved_n}/{len(shots)} frames approved")
    if n_takes:
        facts.append(f"{n_takes} motion takes from {len(engines)} engines")
    facts.append(f"updated {date.today().strftime('%d %b %Y')}")

    # ---- tier 1: the episode, playable, with one plain sentence -------------
    hook = node_hook(d)
    player = ""
    if rel and ep_video:
        # Same poster name build_site already extracted for the node page, so this
        # is a cache hit rather than a second ffmpeg run — and the player at the
        # top of the page shows a picture instead of a black rectangle.
        ep_poster = poster_for(d / "leaves" / ep_video,
                               f"{genome}/posters/{leaf.get('leaf', d.name + '-ep')}.jpg")
        pa = f' poster="{ep_poster}"' if ep_poster else ""
        player = (f'<figure class="phone"><video controls playsinline preload="metadata"'
                  f'{pa} src="leaves/{html.escape(ep_video)}"></video>'
                  f'<figcaption>Episode as it stands · {html.escape(str(leaf.get("form", "")))}'
                  f'</figcaption></figure>')

    # ---- tier 2: the filmstrip index ---------------------------------------
    strip, railnums = [], []
    for s in shots:
        n = s["num"]
        t = heads.get(n, {}).get("title", s["slug"])
        still = stills_dir / f"{n:02d}-{s['slug']}.png"
        src = (thumbs.get(n) or sthumbs.get(n)
               or (f"{rel}/{still.name}" if rel and still.exists() else ""))
        thumb = (f'<img loading="lazy" decoding="async" src="{src}" '
                 f'alt="shot {n:02d} — {html.escape(t)}">'
                 if src else '<div class="ph"></div>')
        strip.append(f'<a href="#beat-{n:02d}" title="{html.escape(t)}">{thumb}{n:02d}</a>')
        railnums.append(f'<a href="#beat-{n:02d}">{n:02d}</a>')

    # ---- tier 3: one section per shot --------------------------------------
    rows = []
    for s in shots:
        n = s["num"]
        pos, _ = compress(s["prompt"])
        neg = beat_neg(s["prompt"])
        still = stills_dir / f"{n:02d}-{s['slug']}.png"
        approved = still.exists()
        h = heads.get(n, {})
        span = h.get("span")
        dialogue, intent, backstory = split_note(notes.get(n, ""))
        takes = all_takes.get(n, [])
        submit_this = submit_new.replace("{n}", f"{n:02d}")

        # badges mark exceptions only — a badge on all 15 shots says nothing
        chips = []
        if n in requests:
            chips.append('<span class="chip hot">OPEN REQUEST</span>')
        if not approved:
            chips.append('<span class="chip">FRAME IN REVIEW</span>')
        if len(takes) > 1:
            chips.append(f'<span class="chip">{len(takes)} TAKES</span>')

        eyebrow = f"SHOT {n:02d}"
        if span:
            eyebrow += (f" · {span[0]}–{span[1]} · "
                        f"{max(1, _secs(span[1]) - _secs(span[0]))}s")

        # ONE crowned player for the take that is actually in the episode; the
        # alternates fold away instead of stacking six black rectangles.
        lead, rest, crowned = leads.get(n, ([], [], False))
        takes_html = ""
        if lead:
            cells = "".join(
                take_cell(v, rel,
                          thumbs.get(n, "") if i == 0 else "", crowned)
                for i, v in enumerate(lead))
            takes_html = (f'<h3>{"The take in the episode" if crowned else "Takes so far"}'
                          f' — tap to play</h3><div class="takes lead">{cells}</div>')
        if rest:
            cells = "".join(take_cell(v, rel, "", False) for v in rest)
            takes_html += (f'<details class="drawer"><summary>Other takes of this shot '
                           f'({len(rest)}) — same frame, different engines</summary>'
                           f'<div class="drawer-body"><div class="takes">{cells}</div>'
                           f'</div></details>')

        req_html = ""
        if n in requests:
            req_html = (f'<p class="request">🎬 <b>This shot is asking for a take.</b> '
                        f'<a href="{REPO_URL}/issues/{requests[n]}">Read the request and '
                        f'claim it</a> — your tools, your account, your name on the credit.</p>')
        vote_html = ""
        if not approved and vote_url:
            vote_html = (f'<p class="vote">🗳 <b>Vote on the frame:</b> comment '
                         f'<code>beat {n:02d}: A</code> (or B/C/D, or <code>none</code> + why) '
                         f'on <a href="{vote_url}">the reactions thread</a> — every vote '
                         f'counts the same, the author&#39;s included.</p>')

        rows.append(f"""
<section class="beat" id="beat-{n:02d}">
  <p class="eyebrow">{eyebrow}</p>
  <h2>{html.escape(h.get('title') or s['slug'])}</h2>
  {' '.join(chips)}
  {f'<blockquote><strong>said aloud</strong><br>{html.escape(dialogue)}</blockquote>' if dialogue else ''}
  {f'<p class="intent">{html.escape(intent)}</p>' if intent else ''}
  {f'''<details class="drawer"><summary>Why this shot looks like this</summary>
    <div class="drawer-body">{html.escape(backstory)}</div></details>''' if backstory else ''}
  {req_html}
  <div class="media">
    <figure>{f'<a href="{rel}/{still.name}">' if (rel and approved) else ''}
      {img_tag(still, rel=rel, alt=f"shot {n:02d} — the approved frame",
               thumb=sthumbs.get(n, ""))}
      {'</a>' if (rel and approved) else ''}
      <figcaption>The approved frame — every take starts here{
        f' · <a href="{rel}/{still.name}">full resolution '
        f'({STILL["width"]}×{STILL["height"]})</a>' if (rel and approved) else ''
      }</figcaption></figure>
  </div>
  {'' if approved else variant_cells(d / "takes" / "stills", n, rel, genome)}
  {vote_html}
  {takes_html}
  <p class="actions"><a class="btn" href="{submit_this}">🎬 Hand in a take for shot {n:02d}</a><br>
    <span class="also"><a href="#submit">how it works &amp; free routes</a>
    · <a href="#beat-{n:02d}-recipe">the exact recipe</a></span></p>
  <details class="drawer recipe" id="beat-{n:02d}-recipe">
    <summary>Recipe — everything needed to reproduce or beat this shot</summary>
    <div class="drawer-body">
      <p class="k">Frame</p>
      <p>Model <code>{STILL_MODEL}</code> · {STILL['width']}×{STILL['height']} ·
         {STILL['steps']} steps ·
         <abbr title="classifier-free guidance — how hard the model is pushed toward the prompt">CFG</abbr>
         {STILL['cfg']} ·
         <abbr title="the random starting number; same seed + same prompt = same picture">seed</abbr>
         {STILL['seed_base']} + {n} = {STILL['seed_base'] + n}</p>
      <p class="k">Prompt, exactly as sent</p>
      <pre>{html.escape(pos)}</pre>
      <p class="k">Things to keep out</p>
      <p>{html.escape(neg_delta(s['prompt']))} <span class="cost">(baseline listed once at the
         top of this page)</span></p>
      <details><summary>show the full negative prompt as sent</summary>
        <pre>{html.escape(neg)}</pre></details>
      <p class="k">What should move (for image-to-video)</p>
      <pre>{html.escape(motion_prompts.get(n, '(push-in only — no AI motion)'))}</pre>
      <p class="k">Do it with your own key</p>
      <pre>python3 pipeline/generate_shots.py {genome} {d.name.split('-')[0]} --provider fal --beats {n:02d} --from-stills --yes</pre>
      <p class="cost">Your provider bills you, never the show. A 4-second shot is
         typically under $0.10 on your own key; the free routes below cost nothing.</p>
    </div>
  </details>
</section>""")

    # ---- the ask, written once instead of fifteen times ---------------------
    credited = ""
    if handed:
        who = ", ".join(f'<a href="https://github.com/{html.escape(p)}">@{html.escape(p)}</a>'
                        for p in sorted(handed))
        credited = (f"<p>Real, not hypothetical: {who} handed in takes that are in the cut "
                    f"above, each one credited in the "
                    f"<a href=\"{REPO_URL}/blob/main/ledger/watering.csv\">public ledger</a> "
                    f"and in the clip's own settings file.</p>")

    submit_first = submit_new.replace("{n}", f"{shots[0]['num']:02d}" if shots else "01")
    submit_html = f"""
<h2 id="submit">Hand in a take</h2>
<p>Pick any shot, remake it better, and it gets screened against what is in the
episode now. Routes, cheapest first:</p>
<ol class="steps">
  <li><b>Free, with a tool you already have.</b> Feed that shot's approved frame and
      prompt to any generator with a free tier — PixVerse, Kling, Runway, Pika, Veo.
      Then open an issue with the link:
      <a href="{submit_first}">start one here</a>. A person files it — tool, settings
      and your name saved alongside the clip (<code>pipeline/intake_take.py</code>).
      <span class="cost">cost to you: $0</span></li>
  <li><b>Free GPU.</b> Fork <code>pipeline/kaggle/render-kaggle.ipynb</code> into your own
      Kaggle account and run it there — that is how most frames on this page were made.
      <span class="cost">cost to you: $0, needs a Kaggle login</span></li>
  <li><b>Your own API key.</b> Clone the repo, put <code>FAL_KEY=…</code> in
      <code>.env</code>, and run the command in any shot's recipe. Your key never
      leaves your machine and your provider bills you, not the show.
      <span class="cost">usually under $0.10 for a 4-second shot</span></li>
  <li><b>Change the words instead.</b> Every prompt lives in
      <code>genomes/{genome}/nodes/{d.name}/shots.md</code> — edit a shot and open a
      pull request. A better prompt is worth as much as a better render.
      <span class="cost">cost to you: $0, needs git</span></li>
  <li><b>What happens next.</b> A human screens everything; the author picks the take
      the episode keeps. Nothing is published unscreened, and nothing you send is
      silently used.</li>
</ol>
{credited}
<p>Current motion settings for reference: {html.escape(MOTION['engine'])}, rendered at
{html.escape(MOTION['size'])} — {html.escape(MOTION['note'])}.</p>
<p class="cost">Your take stays yours. Everything published here is
<a href="{REPO_URL}/blob/main/LICENSE-CONTENT.md">CC BY 4.0</a>: if the show uses your
clip it ships credited to you under that licence, and the credit is a line in a public
file, not a promise in a DM.</p>
<p><a class="btn ghost" href="{REPO_URL}/blob/main/ledger/watering.csv">📒 The credit ledger</a>
<a class="btn ghost" href="{REPO_URL}/blob/main/CONTRIBUTING.md">📖 Contributing</a></p>
"""

    # The glossary rides high (collapsed, ~0 cost) so the words are explained
    # before they are used; the routes above sit below the shots.
    glossary_html = f"""
<details class="drawer"><summary>Plain words for the words on this page</summary>
  <div class="drawer-body">
    <p><b>Shot</b> — about 4 seconds of screen time, one camera setup. The smallest piece
    you can remake on your own and hand back.<br>
    <b>Frame</b> — the single approved still image a shot's motion is generated from.<br>
    <b>Take</b> — one attempt at animating that frame. Several can exist per shot; one is
    in the episode.<br>
    <b>Episode / branch</b> — episodes continue from each other, and the audience's votes
    decide which continuation becomes the main line.<br>
    <b>Ledger</b> — a public CSV in the repo recording who spent what and who made what.<br>
    <b>Prompt / negative prompt</b> — what to draw, and what to keep out.</p>
  </div>
</details>

<details class="drawer"><summary>The one &quot;keep out&quot; list every shot sends</summary>
  <div class="drawer-body">
    <p>Stated once here so the recipes can list only their own additions and removals —
    it is the least interesting text on the page and it used to be repeated fifteen times.</p>
    <pre>{html.escape(NEG)}</pre>
  </div>
</details>
"""

    # ---- head: viewport, description, share card — this page gets pasted ----
    desc = (f"How every shot of {title} was made: the approved frame, the exact prompt "
            f"and settings, and every take — remake any shot with your own tools.")
    page_url = f"{CANONICAL}/{genome}/{d.name}-shots.html"
    first_still = next((stills_dir / f"{s['num']:02d}-{s['slug']}.png" for s in shots
                        if (stills_dir / f"{s['num']:02d}-{s['slug']}.png").exists()), None)
    # Share card: the small JPEG of the opening frame when one exists — scrapers
    # choke on 1.2 MB PNGs — else the full frame, else the site card.
    first_thumb = next((v for v in (sthumbs.get(s["num"]) for s in shots) if v), "")
    og_image = (f"{CANONICAL}/{first_thumb.removeprefix('../')}" if first_thumb else
                (f"{CANONICAL}/{genome}/{rel}/{first_still.name}"
                 if rel and first_still else f"{CANONICAL}/og.png"))
    esc_t = html.escape(f"Shot board — {label.title()}: {title} · banyan.city")
    esc_d = html.escape(desc)
    favicon = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
               "viewBox='0 0 32 32'%3E%3Ctext y='26' font-size='26'%3E🌳%3C/text%3E%3C/svg%3E")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{esc_d}">
<link rel="icon" href="{favicon}">
<link rel="canonical" href="{page_url}">
<link rel="alternate" type="application/rss+xml" title="new nodes" href="{CANONICAL}/feed.xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Banyan City">
<meta property="og:title" content="{esc_t}">
<meta property="og:description" content="{esc_d}">
<meta property="og:url" content="{page_url}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc_t}">
<meta name="twitter:description" content="{esc_d}">
<meta name="twitter:image" content="{og_image}">
<title>{esc_t}</title>
<style>{THEME_CSS}{BOARD_CSS}</style>
</head>
<body>
<main>
<nav class="crumbs"><a href="../index.html">🌳 banyan.city</a> ·
  <a href="{node_page}">{html.escape(label.title())} — {html.escape(title)}</a> ·
  shot board · <a href="{REPO_URL}">source</a></nav>
<div class="railwrap">
  <div class="rail"><span class="lbl">shots</span>{''.join(railnums)}</div>
  <div class="prog"></div>
</div>
<p class="eyebrow">{label} · SHOT BOARD</p>
<h1>Every shot of “{html.escape(title)}”, and how it was made</h1>
<p class="lede">Sapling is an AI-animated series growing at banyan.city — it branches on the
audience's votes. This page opens up one episode completely: for every shot, the picture it was
built from, the exact words and settings that made it, and every attempt at animating
it — so you can remake a shot with your own tools and hand it back.</p>
{f'<p class="intent">{html.escape(hook)}</p>' if hook else ''}
{player}
<p><a class="btn" href="#submit">🎬 Hand in a take</a>
  <a class="btn ghost" href="{node_page}">▶ Watch the episode &amp; read the script</a>
  {f'<a class="btn ghost" href="{vote_url}">💧 React &amp; vote</a>' if vote_url else ''}</p>
<p class="cost">{html.escape(' · '.join(facts))}</p>
<h2>The {len(shots)} shots</h2>
<div class="strip">{''.join(strip)}</div>
{glossary_html}
<h2>Shot by shot</h2>
{''.join(rows)}
{submit_html}
<p class="legend"><b>frame</b> = the approved still · <b>take</b> = one animation of it ·
<b>episode</b> = the cut the show ships</p>
<footer>Every render on this page publishes its model, prompt, seed and cost —
that is the whole point. Auditable in <a href="{REPO_URL}">git</a>. ·
<a href="../index.html">banyan.city</a></footer>
</main>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("genome")
    ap.add_argument("node")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    nodes = REPO / "genomes" / a.genome / "nodes"
    d = next(x for x in sorted(nodes.iterdir())
             if x.is_dir() and x.name.startswith(a.node))
    out = Path(a.out) if a.out else REPO / f"shotboard-{a.node.split('-')[0]}.html"
    out.write_text(board_html(a.genome, d))
    print(f"✓ shot board: {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
