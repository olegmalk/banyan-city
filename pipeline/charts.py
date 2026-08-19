#!/usr/bin/env python3
"""The status page's pictures — inline SVG, no library, no external request.

Roman, 2026-08-13: "we really need the status page to have more cool charts and
be less boring worklike, not just to make it fun but also make it much easier to
understand."

The second half of that sentence is the brief. The page was not boring because
it lacked ornament; it was boring because it made WORDS DO A CHART'S JOB. Thirty
six beats, each in one of five states, were published as a paragraph of counts —
a reader had to hold five numbers in their head to picture something a picture
states instantly. Everything in this module replaces counting-by-reading with
seeing, and nothing in it invents a number: every mark here is one row of one
measured file, and where a file is thin the chart says so on its face rather
than smoothing the gap.

THE THREE RULES THIS MODULE IS BUILT TO OBEY

1. ONE MARK, ONE MEASURED ROW. A leaf on the tree is a beat in
   `pipeline/measured/episode-progress.yaml`. A bar on the work chart is a day
   of the render box's own per-job sidecars. If a datum is missing, its mark is
   drawn as *missing* (hollow, and named in the tooltip) — never dropped, which
   would shrink the denominator and flatter the picture, and never filled in.

2. COLOUR CARRIES THE ARGUMENT, AND IT IS THE SAME ARGUMENT EVERYWHERE.
   `STATE_STYLE` below is the single definition of what each beat state looks
   like, and both the tree here and the ETA bars in `build_sim.py` read it.
   GREEN is the machine's business, AMBER is the author's. Two files each
   holding "done is green" is two files that drift, and the day they disagree
   the page is telling a reader that green means two things.

3. NO EXTERNAL ANYTHING. The published site's CSP allows no CDN, no font, no
   script host. These are `<svg>` elements with class names, styled by the CSS
   below, which uses only the theme's own custom properties — so the charts
   follow the reader's light/dark setting for free, and there is no second
   palette to keep in sync with the first.

WHY SVG AND NOT DIVS. The tree needs curves and the bars need a shared baseline
that survives a 320px phone; both are one element that scales, rather than a
dozen absolutely-positioned boxes that have to be re-reasoned at every width.
Every chart here is authored in its own viewBox coordinates and then told to be
100% wide, so there is exactly one layout to get right.
"""
import html
import math

# --- the five beat states, once ------------------------------------------------
# Read by the tree below AND by build_sim's episode ETA bars. The order is the
# order the bars stack in and the tree's key lists, and it is grouped BY WHOSE
# CLOCK rather than by pipeline stage on purpose: the two green states sit
# together and the two amber ones sit together, so the bar reads as two blocks
# and the separation the feature exists to show is visible before any word is.
#
# Grouping them this way also fixed a real legibility bug. In pipeline order the
# two DARK shades — leaf-deep and sap-deep — were adjacent segments, and they are
# genuinely hard to tell apart: measured at ΔE 11.1 in OKLab for a normal-vision
# reader and 5.2 under deuteranopia, both under the thresholds where colour alone
# can be trusted. Grouped by clock, the worst adjacent pair is ΔE 35.6 / 34.1.
# Same five colours, same argument, one reordering.
STATE_STYLE = (
    # key,                          css,      label,                    whose
    ("done",                        "done",   "passed",                 "machine"),
    ("fix-known",                   "mach",   "the card’s to do",       "machine"),
    ("never-rendered",              "mach",   "the card’s to do",       "machine"),
    ("candidate-awaiting-founder",  "look",   "waiting for your look",  "author"),
    ("blocked-decision",            "gate",   "waiting on a decision",  "author"),
    # Assigned by episode_eta._apply_gate_correction, never read off disk: a
    # `blocked-decision` whose named gate has demonstrably already been opened.
    # It maps to `unk` ON PURPOSE. The beat's real state is unknown — nobody has
    # re-scored it since the gate opened — and a hollow leaf is the honest mark
    # for that. Colouring it as progress would replace a false block with a
    # false pass, which is the worse of the two lies.
    ("stale-gate-closed",           "unk",    "no current state on file", "author"),
)
# css class -> the words for it, in bar/legend order. Two states share "mach"
# because the ETA bar has always merged them: "no candidate yet" and "we know
# what to fix" are the same job from the card's side, and splitting them here
# would put two identical greens next to each other for no reader's benefit.
STATE_ORDER = ("done", "mach", "look", "gate")
STATE_LABEL = {"done": "passed", "mach": "the card’s to do",
               "look": "waiting for your look", "gate": "waiting on a decision",
               # "no CURRENT state": this bucket holds two populations and the
               # older wording was wrong about one of them. A beat nobody has
               # scored has no state on file at all; a `stale-gate-closed` beat
               # HAS one on file and it is out of date. Both lack a state you
               # can act on today, which is what the column means.
               "unk": "no current state on file"}
STATE_CLASS = {k: css for k, css, _l, _w in STATE_STYLE}


def _e(s) -> str:
    return html.escape(str(s), quote=True)


# =============================================================================
#  THE SAPLING — the show, drawn as the thing it is named after
# =============================================================================
#
# The show is called Sapling and the page that shows it being made had no
# picture of it. This one is not an illustration with numbers written on it: it
# is a dot plot of every beat in the series, laid out as foliage. Each leaf is
# one beat, coloured by that beat's state, linked to that beat on its shot
# board, and named in a tooltip. Counting them gives the same answer as the ETA
# cards because it is the same file.
#
# WHY A TREE AND NOT A GRID. A grid would be marginally easier to count and
# would say nothing about what this is. The compromise the geometry makes: the
# leaves inside one canopy sit on a REGULAR grid — same row pitch, same column
# pitch, offset rows only — so a reader can still count a row and multiply. The
# tree is in the arrangement of the canopies, not in scattering the marks.
#
# WHY EPISODE ORDER IS BOTTOM-UP. Episode 1 is the lowest limb and the newest
# episode is the highest, because that is how a tree grows and because the
# newest episode is the one being worked on — it wants the eye.

LEAF_PATH = "M0 0C2.6-3.4 8-4.2 11.4-1.2 8.8 2.4 3.2 3.4 0 0Z"
LEAF_W, LEAF_H = 11.4, 7.0
# The cells are DELIBERATELY smaller than the leaf. Neighbouring leaves overlap
# by a pixel or two and are separated by the 1.6-unit background-coloured stroke
# in the CSS below — which is the standard "2px surface gap between fills", and
# is what makes a canopy read as foliage instead of as a scatter plot of seeds.
# Spaced apart on a true grid (the first cut of this) it looked like graph paper
# with a tree drawn behind it.
CELL_W, CELL_H = 12.5, 8.8
TIER_H = 58.0


def _canopy_grid(n: int):
    """Columns and rows for n leaves — wider than tall, like a canopy.

    The target is a canopy about half again as wide as it is deep. Much wider
    and the limb reads as a hedge; much narrower and it reads as a bush. The
    caller spreads the leaves evenly across the rows this returns, so `rows` is
    a row count, not a promise that every row is full.
    """
    if n <= 0:
        return 0, 0
    # Aim at the SHAPE, not the count: a cell is wider than it is tall, so
    # `sqrt(n)` columns would give a canopy two and a half times wider than
    # deep — a hedge. Solving cols·CELL_W / (rows·CELL_H) ≈ 1.5 for cols is what
    # gives a limb something the eye reads as round.
    cols = max(3, round(math.sqrt(n * 1.5 * CELL_H / CELL_W)))
    rows = math.ceil(n / cols)
    return cols, rows


def _leaf_state(state: str) -> str:
    """A beat's css class, or "unk" for a state this module does not know.

    `episode_eta.read_progress()` already drops beats whose state is outside the
    five, so this branch is for beats that were never in the file at all — the
    difference between the episode's `total_beats` and the beats listed. Those
    are drawn hollow. A beat nobody has scored is a real and reportable fact and
    the picture must not quietly renumber itself around one.
    """
    return STATE_CLASS.get(state, "unk")


def _counts(beats: list, total: int) -> dict:
    """css class -> how many, including the hollow "never scored" remainder."""
    out = {k: 0 for k in STATE_ORDER}
    for b in beats:
        out[_leaf_state(b.get("state"))] = out.get(_leaf_state(b.get("state")), 0) + 1
    # `unk` is TWO populations and the sum of both, not the later one. Beats with
    # no line in the file at all (total minus listed), PLUS listed beats whose
    # state this module cannot place — which now really happens, because
    # `stale-gate-closed` maps here deliberately. This line used to ASSIGN
    # rather than add, so every listed-but-unplaceable beat counted in the loop
    # above was silently thrown away one line later and the column under-read.
    out["unk"] = out.get("unk", 0) + max(0, total - len(beats))
    return out


def _beat_title(ep: dict, n: int, css: str, note: str, extra: str = "") -> str:
    """The tooltip: which beat, what state, and the reason on file for it.

    The note is the same sentence the states file carries, trimmed — it is the
    most useful string in this whole picture and the only place on the page a
    reader can get a per-beat "why" without opening a yaml on GitHub.

    `extra` is the caller's per-beat receipt line (the take's filename and the
    head of its sha256) and it goes LAST, unclamped, because the whole value of
    it is being the exact string a reader can check the leaf against.
    """
    words = STATE_LABEL.get(css, "no state on file")
    t = f'Episode {ep.get("number")} · beat {n:02d} — {words}'
    note = " ".join(str(note or "").split())
    if note:
        if len(note) > 150:
            note = note[:150].rsplit(" ", 1)[0] + "…"
        t += f'\n{note}'
    extra = " ".join(str(extra or "").split())
    if extra:
        t += f'\n{extra}'
    return t


def _sapling_canopy(ep: dict, cx: float, cy: float, side: int, board: str,
                    links: dict = None) -> tuple:
    """One episode's leaves, plus the geometry the branch has to reach.

    Returns (svg, anchor_x, anchor_y, width, height). The anchor is the point on
    the canopy nearest the trunk, which is where the branch is drawn to — so the
    branch always meets the foliage rather than ending in the air beside it.
    """
    beats = list(ep.get("beats") or [])
    total = int(ep.get("total_beats") or len(beats)) or len(beats)
    # A beat with no line in the file still gets a leaf. Its number is unknown,
    # so it is drawn after the known ones and says so.
    known = sorted(beats, key=lambda b: int(b.get("n") or 0))
    slots = [(int(b.get("n") or 0), _leaf_state(b.get("state")), b.get("note"))
             for b in known]
    slots += [(0, "unk", "")] * max(0, total - len(known))

    cols, rows = _canopy_grid(len(slots))
    # Spread the remainder across the rows instead of dumping it in the last
    # one. Twenty-one beats over five rows is 5,4,4,4,4 — not 5,5,5,5,1, which
    # drew a canopy with one leaf dangling under it. The pitch is still uniform
    # so a reader can still count a row and multiply.
    per_row = [len(slots) // rows + (1 if r < len(slots) % rows else 0)
               for r in range(rows)] if rows else []
    w = cols * CELL_W
    h = rows * CELL_H
    x0 = cx - w / 2.0
    y0 = cy - h / 2.0

    marks, i = [], 0
    for r, count in enumerate(per_row):
        # Short rows are CENTRED under the wide ones. Left-aligned they gave the
        # canopy a ragged corner that read as a rendering fault.
        row_x = x0 + (w - count * CELL_W) / 2.0
        for c in range(count):
            n, css, note = slots[i]
            i += 1
            lx = row_x + c * CELL_W + (CELL_W - LEAF_W) / 2.0
            ly = y0 + r * CELL_H + (CELL_H - LEAF_H) / 2.0
            # Deterministic tilt — derived from the position, never random, so
            # two builds of the same data produce byte-identical HTML and a
            # diff of the page is a diff of the facts.
            tilt = -26 + ((i * 37) % 53)
            # A LEAF THAT IS A RENDERED TAKE OPENS THAT TAKE. `links` is the
            # caller's per-beat receipt map (build_sim.leaf_links) and it only
            # ever holds beats whose artifact is a real published file, so a
            # slate keeps the shot-board link rather than being pointed at a
            # 404. Absent `links`, every leaf behaves exactly as it always has —
            # this module stays a renderer and decides no destinations of its own.
            got = (links or {}).get((int(ep.get("number") or 0), n)) or {}
            href = (got.get("href")
                    or (f'{board}#beat-{n:02d}' if (board and n) else board))
            title = _beat_title(ep, n, css, note, got.get("note", ""))
            # AN INVISIBLE HIT RECT OVER THE WHOLE CELL. Measured on a 320px
            # phone the leaf itself is 17 × 7 CSS pixels — a fine mark and a
            # hopeless finger target. The rect takes the full cell, which
            # nearly doubles the tappable height, and it also gives the hover
            # tooltip somewhere to live in the gaps between leaves. Thirty-six
            # marks in a 280px canopy cannot each reach the 24px ideal; that is
            # what the table view underneath is for, and it carries every value
            # the leaves do.
            hit_x = row_x + c * CELL_W
            hit_y = y0 + r * CELL_H
            body = (f'<title>{_e(title)}</title>'
                    f'<path class="lf lf-{css}" d="{LEAF_PATH}" '
                    f'transform="translate({lx:.1f} {ly:.1f}) rotate({tilt} '
                    f'{LEAF_W / 2:.1f} {LEAF_H / 2:.1f})"/>'
                    f'<rect class="lfhit" x="{hit_x:.1f}" y="{hit_y:.1f}" '
                    f'width="{CELL_W:.1f}" height="{CELL_H:.1f}"/>')
            marks.append(f'<a class="lfa" href="{_e(href)}">{body}</a>' if href
                         else f'<g class="lfa">{body}</g>')

    # The limb ends just INSIDE the foliage rather than beside it. Stopping at
    # the canopy's bounding box left a visible gap, because the centred rows do
    # not all start at that edge.
    tuck = CELL_W * 0.7
    anchor_x = (x0 + w - tuck) if side < 0 else (x0 + tuck)
    return "".join(marks), anchor_x, cy, w, h


def sapling_svg(eps: list, boards: dict, links: dict = None) -> tuple:
    """The whole tree. Returns (svg, per-episode summary rows).

    `eps` is `episode_eta.read_progress()` — the same rows the ETA cards use,
    so the two cannot disagree. `boards` maps episode number -> shot-board URL.
    """
    eps = sorted([e for e in eps if e.get("beats")],
                 key=lambda e: int(e.get("number") or 0))
    n_eps = len(eps)
    if not n_eps:
        return "", []

    # Room for the widest canopy on each side, plus the gap to the trunk, plus a
    # margin for the labels. Computed rather than fixed: an episode with forty
    # beats must not run off its own picture.
    widths = []
    for e in eps:
        total = int(e.get("total_beats") or len(e["beats"]))
        cols, _r = _canopy_grid(total)
        widths.append(cols * CELL_W)
    half = max(widths) / 2.0
    gap = 16.0
    # 30 rather than 20: the episode labels are pinned to the inner canopy edge
    # and flow outward, so the margin has to hold whatever overhangs a narrow
    # canopy. Measured against the longest label the format can produce.
    cx = 30.0 + gap + max(widths)
    W = cx * 2.0
    H = 46.0 + TIER_H * n_eps
    ground = H - 18.0
    # The trunk stops just short of the highest canopy's centre so the top limb
    # comes off a tapering tip rather than off the side of a pole that carries
    # on past the leaves.
    top = ground - 44.0 - TIER_H * (n_eps - 1) - 8.0

    canopies, branches, labels, summary = [], [], [], []
    for i, ep in enumerate(eps):
        side = -1 if i % 2 == 0 else 1
        cy = ground - 44.0 - TIER_H * i
        c_cx = cx + side * (gap + half)
        svg, ax, ay, w, h = _sapling_canopy(ep, c_cx, cy, side, boards.get(
            int(ep.get("number") or 0), ""), links)
        canopies.append(svg)
        # The limb: out of the trunk and up into the foliage. One quadratic —
        # its control point below the canopy and out from the trunk is what
        # gives a limb its droop instead of a straight stick.
        by = min(ground - 14.0, cy + TIER_H * 0.42)
        branches.append(
            f'<path class="limb" d="M{cx + side * 1.5:.1f} {by:.1f} '
            f'Q{cx + side * (gap * 0.9):.1f} {by - 1:.1f} {ax:.1f} {ay:.1f}"/>')
        cnt = _counts(ep["beats"], int(ep.get("total_beats") or len(ep["beats"])))
        total = sum(cnt.values())
        # THE LABEL GROWS AWAY FROM THE TRUNK, never toward it. It is pinned to
        # the canopy edge NEAREST the trunk and flows outward, so a label wider
        # than its canopy — which "EP 1 · 4/15 passed" is, under a four-column
        # limb — runs into the empty margin instead of through the trunk. Pinned
        # the other way it did exactly that, and the bigger type made it obvious.
        lx = (c_cx + w / 2.0) if side < 0 else (c_cx - w / 2.0)
        labels.append(
            f'<text class="epl" x="{lx:.1f}" y="{cy + h / 2 + 11:.1f}" '
            f'text-anchor="{"end" if side < 0 else "start"}">EP '
            f'{_e(ep.get("number"))} · {cnt["done"]}/{total} passed</text>')
        summary.append({"number": ep.get("number"), "title": ep.get("title"),
                        "counts": cnt, "total": total,
                        "board": boards.get(int(ep.get("number") or 0), "")})

    # The trunk, tapering. Drawn once, from the soil to just above the top limb,
    # so the highest canopy sits ON the tree rather than floating over it.
    mid = (ground + top) / 2.0
    trunk = (f'<path class="trunk" d="M{cx - 5:.1f} {ground:.1f} '
             f'C{cx - 3.2:.1f} {ground - 18:.1f} {cx - 2.4:.1f} {mid:.1f} '
             f'{cx - 0.9:.1f} {top:.1f} L{cx + 0.9:.1f} {top:.1f} '
             f'C{cx + 2.4:.1f} {mid:.1f} {cx + 3.2:.1f} {ground - 18:.1f} '
             f'{cx + 5:.1f} {ground:.1f}Z"/>')
    roots = (f'<path class="root" d="M{cx - 4:.1f} {ground - 1:.1f}'
             f'C{cx - 11:.1f} {ground + 2:.1f} {cx - 15:.1f} {ground + 5:.1f} '
             f'{cx - 23:.1f} {ground + 6:.1f}"/>'
             f'<path class="root" d="M{cx + 4:.1f} {ground - 1:.1f}'
             f'C{cx + 11:.1f} {ground + 2:.1f} {cx + 15:.1f} {ground + 5:.1f} '
             f'{cx + 23:.1f} {ground + 6:.1f}"/>')
    soil = (f'<path class="soil" d="M{cx - half - gap:.1f} {ground + 9:.1f}'
            f'Q{cx:.1f} {ground + 3:.1f} {cx + half + gap:.1f} {ground + 9:.1f}"/>')

    total_all = sum(s["total"] for s in summary)
    passed = sum(s["counts"]["done"] for s in summary)
    alt = (f'A sapling drawn from the beat states file: {total_all} leaves, one '
           f'per beat across {n_eps} episode{"s" if n_eps != 1 else ""}, '
           f'{passed} of them passed by the author. The counts are listed in '
           'the table below the picture.')
    svg = (f'<svg class="sap-svg" viewBox="0 0 {W:.0f} {H:.0f}" '
           f'role="img" aria-label="{_e(alt)}" '
           f'preserveAspectRatio="xMidYMid meet">'
           f'{soil}{roots}{trunk}{"".join(branches)}'
           f'{"".join(canopies)}{"".join(labels)}</svg>')
    return svg, summary


def _sapling_key(summary: list) -> str:
    """The legend. Present whenever there is more than one state on the tree —
    identity is never carried by colour alone (the tooltips and this key are the
    two other ways to get it), and a key listing states that do not occur would
    be teaching a reader to look for marks that are not there."""
    tot = {k: 0 for k in list(STATE_ORDER) + ["unk"]}
    for s in summary:
        for k, v in s["counts"].items():
            tot[k] = tot.get(k, 0) + v
    bits = [f'<span class="sk-{k}">{tot[k]} {_e(STATE_LABEL[k])}</span>'
            for k in list(STATE_ORDER) + ["unk"] if tot.get(k)]
    return f'<div class="sap-key">{"".join(bits)}</div>' if bits else ""


def _sapling_table(summary: list) -> str:
    """The table view. Every chart on this page has one — a reader who cannot
    separate two greens, or who is reading this with a screen reader, or who
    just wants the number, gets the same facts without the picture."""
    head = "".join(f'<th>{_e(STATE_LABEL[k])}</th>'
                   for k in list(STATE_ORDER) + ["unk"])
    body = ""
    for s in summary:
        cells = "".join(f'<td>{s["counts"].get(k, 0)}</td>'
                        for k in list(STATE_ORDER) + ["unk"])
        body += (f'<tr><th scope="row">Episode {_e(s["number"])} · '
                 f'{_e(s["title"])}</th>{cells}<td>{s["total"]}</td></tr>')
    return ('<details class="drawer"><summary>The same tree as a table</summary>'
            '<div class="drawer-body"><div class="scroll">'
            f'<table class="ctab"><thead><tr><th scope="col">Episode</th>{head}'
            '<th>beats</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>'
            '<p class="cnote">One row per episode, one column per state — the '
            'same counts the leaves above are drawn from, off '
            '<code>pipeline/measured/episode-progress.yaml</code>.</p>'
            '</div></details>')


def sapling_html(eps: list, boards: dict, links: dict = None) -> str:
    """The tree, its key, its caption and its table. "" when there is nothing.

    Fails to nothing, like the ETA section it sits with: a picture of a series
    with no beats on file would be a picture of our own broken read.
    """
    svg, summary = sapling_svg(eps, boards, links)
    if not svg:
        return ""
    total = sum(s["total"] for s in summary)
    passed = sum(s["counts"]["done"] for s in summary)
    looking = sum(s["counts"]["look"] for s in summary)
    caption = (f'<b>{total} leaves, one per beat — {passed} have greened.</b> '
               f'Amber is the author’s to answer ({looking} '
               f'take{"s" if looking != 1 else ""} sitting in front of him), '
               'green is the card’s to render. Hover any leaf for that beat’s '
               'state and the reason on file; click it to open the beat.')
    # WHAT A CLICK ACTUALLY DOES, said only when it is true of some leaf. The
    # sentence above is the standing behaviour and stays; this adds the receipt
    # the caller supplied, and the count is measured off `links` so the caption
    # cannot claim playable leaves a build did not draw.
    if links:
        playable = len(links)
        caption += (f' <b>{playable} of them open the actual clip</b> — the mp4 '
                    'in the newest cut, with its filename and the head of its '
                    'sha256 in the tooltip, so the leaf and the receipt further '
                    'down the page are checkably the same object. A beat with no '
                    'footage keeps its shot board, because a slate has no clip '
                    'to open.')
    # A HOLLOW LEAF IS NOT A SETBACK AND THE PAGE HAS TO SAY WHY. Twelve of
    # these went hollow the day the character gate was found already open: their
    # rows still read `blocked-decision` from a measurement taken ninety minutes
    # before the founder answered, so the page was crediting him with holding up
    # work he had released. Downgrading a false block to an admitted unknown is
    # honest, but without this sentence it reads as twelve beats going backwards.
    hollow = sum(s["counts"].get("unk", 0) for s in summary)
    if hollow:
        caption += (f' <b>{hollow} leaves are hollow</b> — nobody has scored '
                    'them since the last measurement, so the page says so '
                    'rather than guessing. Hollow is missing data, not a '
                    'setback: re-scoring them is what fills them in.')
    return (f'<figure class="sap">{svg}'
            f'{_sapling_key(summary)}'
            f'<figcaption class="ccap">{caption}</figcaption>'
            f'</figure>{_sapling_table(summary)}')


# =============================================================================
#  HOW HARD THE CARD WORKED — the box's own day, in hours
# =============================================================================
#
# Off `pipeline/measured/box-work-daily.yaml`, which `box_work_daily.py` writes
# from the render box's per-job sidecars. See that script's header for why the
# measurement is a committed file and why the bars are MINUTES rather than a
# count of jobs (short version: on 11 Aug the box finished 119 jobs in four
# hours and on 12 Aug it finished 104 in nine — a job count would have called
# the harder day the quieter one).
#
# ONE HUE, ORDERED STEPS — NOT FOUR COLOURS. The brief asked for the kind
# breakdown in colour, and the page could not afford it: green and amber are
# already spoken for here (green is the machine's business, amber is the
# author's), and a second, unrelated four-colour scheme would have made green
# mean two different things one section apart. So the split is drawn as one
# green in three ordered steps — the darkest slab is the kind that ate the most
# machine time — which is the standard treatment for ordered categories and
# keeps the page's colour argument intact. Both step sets were run through the
# ordinal checks against their own surface (monotone lightness, adjacent ΔL
# ≥ .06, faintest step clear of the background) and pass in light and dark.
#
# THREE SERIES, NOT FIVE. The box records five job kinds and two of them are
# rounding error (four inpaint jobs in the whole record). The two biggest by
# machine time get a step each and the rest fold into "everything else" — the
# tail is in the tooltip and in the table, never in a fourth colour nobody can
# separate.

WORK_H = 140.0          # viewBox height
WORK_PLOT_TOP = 14.0
WORK_BASE = 96.0        # the baseline every bar stands on
WORK_LEFT = 4.0
WORK_RIGHT = 4.0
SEG_GAP = 1.8           # the surface-coloured gap between stacked segments
BAR_R = 2.6             # the rounded data-end, top corners only


def _hrs(minutes) -> str:
    """Minutes as the founder reads them. Under an hour stays in minutes —
    "0.4 h" is a number nobody has a feel for."""
    m = int(round(minutes or 0))
    if m < 60:
        return f"{m} min"
    h = m / 60.0
    return f"{h:.0f} h" if h >= 10 else f"{h:.1f} h"


def _bar_top(x, y, w, h, r) -> str:
    """A bar with its TOP corners rounded and its foot square on the baseline.

    Rounding all four corners floats the bar off its own axis; rounding none
    makes a chart of blunt slabs. The data end is the end that gets the radius.
    """
    r = max(0.0, min(r, w / 2.0, h))
    return (f'M{x:.2f} {y + h:.2f}V{y + r:.2f}'
            f'a{r:.2f} {r:.2f} 0 0 1 {r:.2f}-{r:.2f}'
            f'h{w - 2 * r:.2f}'
            f'a{r:.2f} {r:.2f} 0 0 1 {r:.2f} {r:.2f}'
            f'V{y + h:.2f}Z')


def _fold_kinds(doc: dict) -> tuple:
    """(the two biggest kinds by total machine time, the label for the rest)."""
    tot = {}
    for d in doc.get("days") or []:
        for k, v in (d.get("by_kind") or {}).items():
            tot[k] = tot.get(k, 0) + (v or 0)
    top = [k for k, _v in sorted(tot.items(), key=lambda kv: -kv[1])][:2]
    return top, "everything else"


KIND_WORDS = {"ltx": "motion clips", "still": "still frames",
              "charref": "character sheets", "inpaint": "inpainting",
              "other": "other jobs"}


def _kind_label(k: str) -> str:
    return KIND_WORDS.get(k, k)


def work_days_html(doc: dict) -> str:
    """The box's day, in hours, as a column chart. "" when there is nothing.

    Fails to nothing on purpose. A "how hard did the machine work" chart drawn
    from a file that could not be read would be a picture of an idle box, which
    is the single most misleading thing this page could publish about the farm.
    """
    days = [d for d in (doc.get("days") or []) if isinstance(d, dict)]
    if not days:
        return ""
    top_kinds, rest_label = _fold_kinds(doc)
    peak = max((d.get("minutes") or 0) for d in days) or 1
    # A ceiling on the hour, so the top gridline is a number a person says out
    # loud ("nine hours") instead of "533 minutes".
    ceil_h = max(1, math.ceil(peak / 60.0))
    ceil_m = ceil_h * 60.0

    # One step per series, fixed for the whole chart — see the loop below.
    step_of = {k: i + 1 for i, k in enumerate(top_kinds)}
    step_of[None] = 3
    slot = (300.0 - WORK_LEFT - WORK_RIGHT) / len(days)
    bw = min(30.0, slot * 0.66)
    plot_h = WORK_BASE - WORK_PLOT_TOP

    bars, labels, ticks = [], [], []
    for i, d in enumerate(days):
        cx = WORK_LEFT + slot * (i + 0.5)
        x = cx - bw / 2.0
        mins = d.get("minutes") or 0
        by = d.get("by_kind") or {}
        # Biggest kind at the foot of the bar, in the darkest step: the eye
        # lands on the baseline first and that is where the main story is.
        parts = [(k, by.get(k) or 0) for k in top_kinds]
        parts.append((None, sum(v for k, v in by.items() if k not in top_kinds)))
        parts = [(k, v) for k, v in parts if v > 0]

        y = WORK_BASE
        segs = []
        for j, (kind, v) in enumerate(parts):
            h = plot_h * v / ceil_m
            y -= h
            # THE STEP FOLLOWS THE SERIES, NEVER ITS POSITION IN THIS BAR. The
            # first cut numbered the steps by stack index, so on a day with no
            # still frames the "everything else" slab slid from the third step
            # to the second and the same series was two different greens in two
            # neighbouring bars. A reader who learns "faintest is the tail" has
            # to keep being right about it.
            step = f"w{step_of[kind]}"
            gap = min(SEG_GAP, h / 2.0) if j < len(parts) - 1 else 0.0
            top_seg = (j == len(parts) - 1)
            shape = (_bar_top(x, y, bw, max(0.6, h - gap), BAR_R) if top_seg
                     else None)
            segs.append(
                f'<path class="wk {step}" d="{shape}"/>' if shape else
                f'<rect class="wk {step}" x="{x:.2f}" y="{y:.2f}" '
                f'width="{bw:.2f}" height="{max(0.6, h - gap):.2f}"/>')

        # The tooltip is where the whole day lives: every kind, the job count,
        # and any failure. Nothing here is only reachable by hovering — the
        # table below carries all of it too.
        tip = [f'{_day_words(d.get("date"))} — {_hrs(mins)} of machine time, '
               f'{d.get("jobs")} job{"s" if d.get("jobs") != 1 else ""}']
        for k, v in sorted(by.items(), key=lambda kv: -(kv[1] or 0)):
            if v:
                tip.append(f'{_kind_label(k)}: {_hrs(v)}')
        if d.get("failed"):
            tip.append(f'{d["failed"]} failed')
        if d.get("partial"):
            tip.append("still running — this day is not finished")
        bars.append(f'<g class="wkbar"><title>{_e(chr(10).join(tip))}</title>'
                    f'{"".join(segs)}</g>')

        # The value on top of the bar. Four bars is few enough that every one
        # can be labelled without the chart turning into a wall of digits.
        top_y = WORK_BASE - plot_h * mins / ceil_m
        labels.append(f'<text class="wkv" x="{cx:.2f}" y="{top_y - 4:.2f}" '
                      f'text-anchor="middle">{_e(_hrs(mins))}</text>')
        short = str(d.get("date") or "")[-2:].lstrip("0") or "?"
        day_lab = short if len(days) > 7 else f'{short} {_month(d.get("date"))}'
        ticks.append(f'<text class="wkx" x="{cx:.2f}" y="{WORK_BASE + 12:.2f}" '
                     f'text-anchor="middle">{_e(day_lab)}</text>')
        if d.get("partial"):
            ticks.append(f'<text class="wkx dim" x="{cx:.2f}" '
                         f'y="{WORK_BASE + 21:.2f}" text-anchor="middle">'
                         'so far</text>')

    # One gridline, at the ceiling, and the baseline. Solid hairlines a shade
    # off the surface — a chart with five dashed rules is a chart you read past.
    grid = (f'<line class="wkgrid" x1="{WORK_LEFT}" y1="{WORK_PLOT_TOP:.1f}" '
            f'x2="{300 - WORK_RIGHT}" y2="{WORK_PLOT_TOP:.1f}"/>'
            f'<line class="wkaxis" x1="{WORK_LEFT}" y1="{WORK_BASE:.1f}" '
            f'x2="{300 - WORK_RIGHT}" y2="{WORK_BASE:.1f}"/>'
            f'<text class="wkx" x="{WORK_LEFT}" y="{WORK_PLOT_TOP - 3:.1f}">'
            f'{ceil_h} h</text>')

    alt = ('Machine time the render box spent per day: '
           + ", ".join(f'{_day_words(d.get("date"))} {_hrs(d.get("minutes"))}'
                        for d in days)
           + '. The same figures are in the table below.')
    svg = (f'<svg class="wk-svg" viewBox="0 0 300 {WORK_H:.0f}" role="img" '
           f'aria-label="{_e(alt)}" preserveAspectRatio="xMidYMid meet">'
           f'{grid}{"".join(bars)}{"".join(labels)}{"".join(ticks)}</svg>')

    key = "".join(
        f'<span class="wk-k w{i + 1}">{_e(_kind_label(k))}</span>'
        for i, k in enumerate(top_kinds))
    key += f'<span class="wk-k w3">{_e(rest_label)}</span>'

    total_m = sum(d.get("minutes") or 0 for d in days)
    total_j = sum(d.get("jobs") or 0 for d in days)
    busiest = max(days, key=lambda d: d.get("minutes") or 0)
    stamp = doc.get("measured_at") or ""
    # TWO LINES. The first cut of this caption ran to five and argued its own
    # method inside them, which on a phone is a screen of prose under a chart
    # that had already said the thing. The argument is real and it kept every
    # word — it moved into the drawer below, where the rest of this page keeps
    # its workings.
    caption = (
        f'<b>{_hrs(total_m)} of machine time across {total_j} jobs</b>, '
        f'busiest on {_e(_day_words(busiest.get("date")))} at '
        f'{_hrs(busiest.get("minutes"))}. Height is minutes the box’s own clock '
        'recorded, not a count of jobs; the solid block at the foot is the kind '
        'that ate the most of that day.')
    foot = ""

    # WHERE THE DATA IS THIN, THE CHART SAYS SO. The box's per-job records begin
    # on 10 Aug and nothing before that is recoverable, so for the first fortnight
    # this is a chart of a handful of bars — which is worth drawing (the shape is
    # already load-bearing) but is not worth letting a reader mistake for a
    # settled rhythm. The note removes itself once there is a week of it.
    thin = (f'<p class="cnote">Only {len(days)} day'
            f'{"s" if len(days) != 1 else ""} of it so far — the box began '
            'writing per-job records on 10 Aug and nothing before that is '
            'recoverable, so this is a rhythm still forming, not one to read '
            'a trend off.</p>' if len(days) < 7 else "")
    # THE DENSE VIEW LIVES AT /pulse, AND STAYS THERE. Roman took the
    # minute-by-minute telemetry charts off this page on 2026-08-11 — "it has
    # too much unnecessary stuff, its hard to understand whats going on from a
    # glance" — and they moved to their own page. This chart is deliberately the
    # story-level one: four numbers a person can hold. The link is how a reader
    # who wants the per-minute view gets there, instead of it being rebuilt here.
    deep = ('<p class="cnote">Minute-by-minute — GPU load, memory, queue depth '
            'as they happened — lives on <a href="pulse.html">the pulse page</a>. '
            'This chart is the day-level shape only.</p>')
    return (f'<figure class="wkfig">{svg}'
            f'<div class="wk-key">{key}</div>'
            f'<figcaption class="ccap">{caption}</figcaption></figure>'
            + thin + deep + _work_table(doc, top_kinds, stamp) + foot)


_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _month(date_str) -> str:
    try:
        return _MONTHS[int(str(date_str).split("-")[1]) - 1]
    except (ValueError, IndexError, TypeError):
        return ""


def _day_words(date_str) -> str:
    """2026-08-12 -> "12 Aug". The ISO form is right for a file and wrong for a
    sentence a person reads."""
    m = _month(date_str)
    try:
        return f'{int(str(date_str).split("-")[2])} {m}' if m else str(date_str)
    except (ValueError, IndexError, TypeError):
        return str(date_str)


def _work_table(doc: dict, top_kinds: list, stamp: str = "") -> str:
    """Every bar as a row, with the folded tail broken back out."""
    days = doc.get("days") or []
    kinds = list(doc.get("kinds") or top_kinds)
    head = "".join(f'<th>{_e(_kind_label(k))}</th>' for k in kinds)
    body = ""
    for d in days:
        by = d.get("by_kind") or {}
        cells = "".join(f'<td>{_hrs(by[k]) if by.get(k) else "—"}</td>'
                        for k in kinds)
        body += (f'<tr><th scope="row">{_e(_day_words(d.get("date")))}'
                 + (' <span class="cflag">so far</span>' if d.get("partial")
                    else "")
                 + f'</th><td>{d.get("jobs")}</td>'
                 f'<td>{d.get("failed") or "—"}</td>'
                 f'<td>{_hrs(d.get("minutes"))}</td>{cells}</tr>')
    return ('<details class="drawer"><summary>The same days as a table, and '
            'where these numbers come from</summary>'
            '<div class="drawer-body"><div class="scroll">'
            f'<table class="ctab"><thead><tr><th scope="col">Day</th>'
            '<th>jobs</th><th>failed</th><th>machine time</th>'
            f'{head}</tr></thead><tbody>{body}</tbody></table></div>'
            '<p>The bars are MINUTES rather than a count of jobs, and the '
            'difference is not pedantry: on 11 Aug the box finished 119 jobs in '
            'four hours and on 12 Aug it finished 104 in nine, because the 12th '
            'was mostly five-minute motion clips and the 11th was mostly still '
            'frames. A chart counting jobs would have called the harder day the '
            'quieter one.</p>'
            '<p>“Failed” is a job whose runner recorded a non-zero exit. A job '
            'whose exit code was never written down is counted in neither '
            'column — unknown is not the same as fine. A job counts on the day '
            'it FINISHED, so one that spans midnight puts all of its minutes on '
            'the second day; and this is busy time, not GPU utilisation — a job '
            'that spends four of its five minutes loading weights counts all '
            f'five. Measured {_e(stamp)} off the box’s own per-job records, '
            'which live on its results branch and are re-read by '
            '<code>python3 pipeline/box_work_daily.py</code>.</p>'
            '</div></details>')


# =============================================================================
#  THE CSS
# =============================================================================
# Only theme custom properties — no literal colour appears below, so the charts
# follow the reader's light/dark setting with no second palette to maintain.
CHART_CSS = """
/* ---- shared chart furniture ------------------------------------------------
   Every chart on this page is an <svg> that is 100% wide inside a <figure>,
   with its caption below it and a table view one fold down. The captions are
   sentences, not titles: the heading says what the chart is, the caption says
   what it MEANS, which is the part a number cannot carry. ---- */
/* The one-line sub-heading a chart section opens with. Sits between the h2 and
   the picture and says what the picture is, so the caption underneath is free
   to say what it MEANS. */
.chead { font: 600 .82rem/1.6 var(--mono); color: var(--muted);
  margin: .2rem 0 .6rem; }
.ccap { font: 400 .8rem/1.65 var(--sans, inherit); color: var(--muted);
  margin: .55rem 0 0; text-align: left; }
.ccap b { color: var(--ink); font-weight: 700; }
.cnote { font: 400 .74rem/1.7 var(--sans, inherit); color: var(--faint);
  margin: .5rem 0 0; }
table.ctab { border-collapse: collapse; width: 100%; font-size: .8rem;
  font-variant-numeric: tabular-nums; }
table.ctab th, table.ctab td { padding: .4rem .55rem; text-align: right;
  border-bottom: 1px solid var(--line-soft); white-space: nowrap; }
table.ctab thead th { color: var(--faint); font: 600 .7rem/1.4 var(--mono);
  text-transform: uppercase; letter-spacing: .04em; }
table.ctab tbody th { text-align: left; color: var(--ink); font-weight: 600; }
table.ctab tbody tr:last-child th, table.ctab tbody tr:last-child td {
  border-bottom: 0; }

/* ---- the sapling ------------------------------------------------------------
   The tree is the page's one piece of identity that is also its densest chart:
   36 marks, each a real beat, each clickable. It gets the full width it can
   take because the leaves are already near the smallest a finger can hit. ---- */
.sap { margin: 0 0 .4rem; padding: 0; }
/* Capped rather than full-bleed: past about 34rem the leaves stop gaining
   legibility and the tree starts looking like wallpaper. On a phone it takes
   the whole column, which is where it is smallest and needs it. */
.sap-svg { display: block; width: 100%; max-width: 34rem; height: auto;
  margin: 0 auto; overflow: visible; }
/* THE WOOD WEARS NO DATA COLOUR. The first cut drew the trunk in --leaf-deep,
   which is also the colour of "the card's to do" — so in the light theme the
   trunk and one of the four states were the same green, and the structure of
   the picture was competing with its content. Bark is --faint: muted, neutral,
   and not a state. */
.sap-svg .trunk { fill: var(--faint); }
.sap-svg .limb { fill: none; stroke: var(--faint); stroke-width: 2.6;
  stroke-linecap: round; }
.sap-svg .root { fill: none; stroke: var(--faint); stroke-width: 1.8;
  stroke-linecap: round; opacity: .55; }
.sap-svg .soil { fill: none; stroke: var(--line); stroke-width: 1.6;
  stroke-linecap: round; }
.sap-svg .epl { font: 700 6px/1 var(--mono); letter-spacing: .04em;
  fill: var(--faint); }
/* The 2px surface-coloured stroke is the gap between neighbouring leaves. It is
   what stops a dense canopy reading as one blob, and it is drawn in the page's
   own background so it reads as space rather than as an outline. */
.sap-svg .lf { stroke: var(--bg); stroke-width: 1.6; stroke-linejoin: round; }
.sap-svg .lf-done { fill: var(--leaf); }
.sap-svg .lf-mach { fill: var(--leaf-deep); }
.sap-svg .lf-look { fill: var(--sap); }
.sap-svg .lf-gate { fill: var(--sap-deep); }
/* Never scored: hollow, so it reads as an absence at a glance. */
.sap-svg .lf-unk { fill: none; stroke: var(--line); stroke-width: 1.2; }
.sap-svg .lfa { cursor: pointer; }
/* The finger's target, not the eye's: a transparent rect the size of the whole
   grid cell, sitting over the leaf it belongs to. */
.sap-svg .lfhit { fill: transparent; }
.sap-svg .lfa:hover .lf, .sap-svg .lfa:focus-visible .lf {
  stroke: var(--ink); stroke-width: 1.6; }
.sap-svg .lfa:focus-visible { outline: none; }
/* The key. Always present, because identity on a chart must never rest on
   colour alone — this, the tooltips and the table are the three other ways to
   read the same fact. */
.sap-key { display: flex; flex-wrap: wrap; justify-content: center;
  gap: .1rem .8rem; margin: .6rem 0 0;
  font: 400 .72rem/1.8 var(--sans, inherit); color: var(--muted); }
.sap-key span { display: inline-flex; align-items: center; gap: .34rem; }
.sap-key span::before { content: ""; width: .55rem; height: .55rem; flex: none;
  border-radius: 2px; background: var(--line); }
.sap-key .sk-done::before { background: var(--leaf); }
.sap-key .sk-mach::before { background: var(--leaf-deep); }
.sap-key .sk-look::before { background: var(--sap); }
.sap-key .sk-gate::before { background: var(--sap-deep); }
.sap-key .sk-unk::before { background: transparent;
  box-shadow: inset 0 0 0 1px var(--line); }

/* ---- how hard the card worked ----------------------------------------------
   ONE HUE, THREE ORDERED STEPS, expressed as opacity over the page's own
   surface rather than as three new colour tokens. Opacity is what keeps the
   ramp correct in BOTH themes for free: each step blends toward whatever the
   background is, so the steps stay ordered and stay clear of the surface in
   light and in dark. Written as literal steps in each theme they would have
   needed two hand-tuned sets and a way to keep them honest; measured this way,
   1 / .72 / .5 passes the ordinal checks (monotone lightness, adjacent ΔL ≥
   .06, faintest step above the surface) against both surfaces. ---- */
.wkfig { margin: .2rem 0 .4rem; padding: 0; }
.wk-svg { display: block; width: 100%; max-width: 32rem; height: auto;
  margin: 0 auto; }
.wk-svg .wk { fill: var(--leaf); }
.wk-svg .w1 { opacity: 1; }
.wk-svg .w2 { opacity: .72; }
.wk-svg .w3 { opacity: .5; }
.wk-svg .wkbar:hover .wk { fill: var(--sap); }
.wk-svg .wkgrid { stroke: var(--line-soft); stroke-width: .8; }
.wk-svg .wkaxis { stroke: var(--line); stroke-width: .8; }
.wk-svg .wkv { font: 700 9px/1 var(--mono); fill: var(--ink);
  font-variant-numeric: tabular-nums; }
.wk-svg .wkx { font: 500 8.5px/1 var(--mono); fill: var(--faint); }
.wk-svg .wkx.dim { font-size: 7.2px; }
.wk-key { display: flex; flex-wrap: wrap; justify-content: center;
  gap: .1rem .8rem; margin: .55rem 0 0;
  font: 400 .72rem/1.8 var(--sans, inherit); color: var(--muted); }
.wk-key span { display: inline-flex; align-items: center; gap: .34rem; }
.wk-key span::before { content: ""; width: .55rem; height: .55rem; flex: none;
  border-radius: 2px; background: var(--leaf); }
.wk-key .w2::before { opacity: .72; }
.wk-key .w3::before { opacity: .5; }
.cflag { font: 600 .62rem/1 var(--mono); color: var(--faint);
  text-transform: uppercase; letter-spacing: .05em; }
"""
