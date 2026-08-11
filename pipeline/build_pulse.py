#!/usr/bin/env python3
"""THE PULSE — the farm's work queue and the render box's vitals, over time.

Oleg, 2026-08-10: "put in a page for me to see graph of work queue and bare
resources utilizaion of 5090 over time."

Two questions on one x axis, which is the whole point of putting them on one
page: **was there work waiting, and was the machine doing it?** Either graph
alone can be read charitably. Stacked and time-aligned they cannot: a filled
queue above a flat GPU line is the standing directive being broken, in a shape
that needs no explanation.

WHERE THE NUMBERS COME FROM, and why this page is not `/status`. `/status`
draws the box's own last 24 hours live in the reader's browser, straight off
the courier branch, and that is the right instrument for "what is it doing this
minute". It cannot show anything older, because the courier force-pushes and
the file it publishes is the only copy that has ever existed. This page reads
`pipeline/pulse-series.json` — the cache `pulse_series.py` extends from git
history — so it can show days, at the cost of being exactly as fresh as the
last time that cache was extended. The page prints both timestamps and never
implies the second is the first.

EVERY CHART IS INLINE SVG BUILT HERE. No library, no canvas, no client-side
drawing: the graphs are in the HTML, so they render with JavaScript off, in a
feed reader, and in the screenshot Oleg will actually look at on his phone.

THE TIME-WINDOW SELECTOR KEEPS THAT PROMISE (Roman, 2026-08-10: "status page UX
is not production grade. in partucular there is no time window selection").
Every offered window is drawn HERE, at build time, by this same engine, and the
selector only decides which of the finished panels is on screen. No second chart
engine in JavaScript, so there is nothing that can drift from what the tests
check; with JavaScript off the default window is still a real chart and the
selector hides itself rather than sitting there dead. A chart that changes shape
after load is a chart you cannot cite — so every panel is stamped with the span
it draws, and the caption says how much of that span was actually measured.

ONE SELECTOR FOR THE WHOLE PAGE, not one per chart. The page's argument is that
you can read straight down a moment across the queue and the machine; charts on
different windows would not be stacked on one clock any more, which is the one
thing this layout exists to guarantee.

ONE SERIES PER CHART, inherited from build_sim's telemetry section and for the
same measured reason: leaf green and sap amber are 4.5 ΔE apart under
protanopia, so encoding identity in that difference fails for some readers. A
chart carries one quantity and says which in its title. Mean and peak of the
SAME quantity are the one exception — they are one series' envelope, drawn in
one hue, distinguished by fill against stroke rather than by colour.
"""
from __future__ import annotations

import datetime
import html
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
import repo_slug  # noqa: E402  one source for "which repo is this"

CACHE = REPO / "pipeline" / "pulse-series.json"

# Oleg reads this page, and he reads it in Dubai. Every clock face on it is
# +04 and says so; the cache underneath is unix seconds and stays that way.
TZ = datetime.timezone(datetime.timedelta(hours=4))
TZ_LABEL = "+04"
# Spelled out for the hover readout, which formats its own clock face: the
# browser's own month names would be the READER's locale, and every other stamp
# on this page is +04 in English. One page, one clock.
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# 48 hours: two nights, so "it idled overnight" and "it idles every night" are
# different pictures rather than the same one. That stays the DEFAULT — the view
# with no choice made, and the one a reader with JavaScript off gets — and the
# selector offers the rest.
WINDOW_HOURS = 48
LONG_WINDOW_HOURS = 24 * 7

# (hours, button label, the words the page uses for it, the bare span). The short
# end is there because "what is it doing right now" is a different question from
# "did it work last night", and answering the first on a 48-hour axis means
# reading a machine from two pixels.
WINDOWS = [
    (1, "1h", "the last hour", "1 hour"),
    (6, "6h", "the last 6 hours", "6 hours"),
    (24, "24h", "the last 24 hours", "24 hours"),
    (48, "48h", "the last 48 hours", "48 hours"),
    (24 * 7, "7d", "the last 7 days", "7 days"),
]

# A window is OFFERED only when the cache reaches back across at least this much
# of it. The alternative — offering every window always — hands the reader a
# seven-day frame holding nothing at all, and a blank stretch on this page means
# "the machine was not reporting". It must not also mean "you picked a window
# older than the cache". Nine tenths rather than the whole span so that a cache
# 6.6 days deep still offers 7d — a full picture with a sliver missing.
#
# THE TEST IS ACROSS THE WHOLE CACHE, NOT PER SERIES, and the two do not agree:
# the queue is sampled per commit and reaches back a week, while the box's
# vitals are a rolling day. Greying 7d because the GPU grid is one day deep
# would hide a week of backlog history that genuinely exists. So the button
# offers what SOME chart can draw, and each panel that personally has no cache
# for part of its span HATCHES that part — see uncached_band. Greying is the
# page's answer to "there is nothing here"; hatching is its answer to "this
# chart's share of it starts later".
COVERAGE = 0.9

GH = repo_slug.GH_REPO            # pipeline/repo_slug.py — never hardcode the owner
RAW = repo_slug.RAW_URL
TELEMETRY_URL = f"{RAW}/farm-results-rtx5090/telemetry.json"
QUEUE_URL = f"{RAW}/main/pipeline/farm-queue.yaml"

# Geometry shared by every chart on the page, so that stacking two of them
# aligns their x axes to the pixel. This is load-bearing, not tidiness: the
# page's argument is made by reading a queue chart and a GPU chart at the same
# horizontal position.
W, H = 760, 168
PAD_L, PAD_R, PAD_T, PAD_B = 46, 12, 14, 24
PLOT_W = W - PAD_L - PAD_R
PLOT_H = H - PAD_T - PAD_B


# The hatch the CSS has always pointed at. One definition for the page: an SVG
# pattern is addressable by url(#id) from any other SVG in the same document, so
# twenty panels share one. var(--faint) rather than currentColor — currentColor
# inside a detached <defs> resolves against the defs' own context, not the chart
# that uses it, and would come out the wrong colour in one of the two themes.
HATCH_DEFS = (
    '<svg width="0" height="0" aria-hidden="true" focusable="false" '
    'style="position:absolute">'
    '<defs><pattern id="pulse-hatch" width="7" height="7" '
    'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
    '<line x1="0" y1="0" x2="0" y2="7" stroke="var(--faint)" stroke-width="1.4" '
    'opacity=".45"/></pattern></defs></svg>')

CSS = """
.pulse-grid { display: grid; gap: 1.5rem; margin: 1.2rem 0 0; }
.pchart { margin: 0; }
.pchart figcaption { font: 700 .72rem/1.5 var(--mono); letter-spacing: .06em;
  text-transform: uppercase; color: var(--muted); display: flex; flex-wrap: wrap;
  justify-content: space-between; gap: .2rem .8rem; }
.pchart figcaption .cap { font-weight: 500; text-transform: none;
  letter-spacing: 0; color: var(--faint); }
.pchart svg { width: 100%; height: auto; display: block; margin: .35rem 0 .1rem;
  background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 12px; touch-action: pan-y; }
/* ---- the reasoning, one fold down -------------------------------------------
   Every chart on this page carries a paragraph explaining how to read it, and
   those paragraphs are the reason the page can be trusted. They are also six
   lines each on a phone, which pushed the queue chart a full screen below the
   GPU chart — and reading one against the other AT THE SAME MOMENT is the only
   thing this page is for. Folded, not cut: every word is still here, one tap
   away, and the coverage caption that says what the chart does not know stays
   in the open where it has to be. ---- */
.pchart .why { margin: .15rem 0 0; }
.pchart .why > summary { cursor: pointer; list-style: none;
  font: 500 .72rem/1.6 var(--mono); color: var(--faint); }
.pchart .why > summary::-webkit-details-marker { display: none; }
.pchart .why > summary::before { content: "▸"; display: inline-block;
  margin-right: .4rem; transition: transform .15s ease; }
.pchart .why[open] > summary::before { transform: rotate(90deg); }
.pchart .why > summary:hover { color: var(--ink); }
.pchart .why p { font: 500 .78rem/1.65 var(--mono); color: var(--faint);
  margin: .3rem 0 0; }

/* PHONE AXIS TEXT. The SVG is drawn at a fixed 760-unit width and scaled to the
   column, so a 10px label renders at 6px on a 460px phone — measured, and not
   readable. The label has to grow in the chart's own units as the chart shrinks
   in the reader's. */
@media (max-width: 640px) {
  .pchart .axis { font-size: 16px; }
  .pchart .nodata { font-size: 15px; }
}

/* ---- the time-window selector ------------------------------------------------
   Emitted hidden and unhidden by the script: with JavaScript off the buttons
   could not switch anything, and a control that does nothing is worse than no
   control. A window the cache cannot cover is DISABLED and says why on hover,
   rather than being left out — "7d is greyed out because the cache is one day
   deep" is a fact about the farm worth reading, and a selector whose buttons
   come and go between deploys cannot be learned. ---- */
.winbar { display: flex; flex-wrap: wrap; align-items: baseline; gap: .5rem .8rem;
  margin: 1.2rem 0 .2rem; padding: .7rem .85rem; border: 1px solid var(--line);
  border-radius: 12px; background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.winbar > .lbl { font: 700 .68rem/1.6 var(--mono); letter-spacing: .08em;
  text-transform: uppercase; color: var(--faint); }
.winbtns { display: flex; flex-wrap: wrap; gap: .3rem; }
.winbtns button { font: 700 .74rem/1 var(--mono); letter-spacing: .04em;
  color: var(--muted); background: var(--code-bg); border: 1px solid var(--line);
  border-radius: 999px; padding: .42rem .68rem; cursor: pointer;
  min-height: 32px; min-width: 44px; }
.winbtns button:hover:not([disabled]) { color: var(--ink); border-color: var(--leaf-deep); }
.winbtns button:focus-visible { outline: 2px solid var(--sap); outline-offset: 2px; }
.winbtns button[aria-pressed="true"] { color: var(--sap-ink); background: var(--sap);
  border-color: var(--sap); }
.winbtns button[disabled] { opacity: .38; cursor: not-allowed;
  border-style: dashed; }
.winbar .winnote { flex: 1 1 100%; margin: 0; font: 500 .76rem/1.6 var(--mono);
  color: var(--faint); }
.pwin[hidden] { display: none; }
.pwin .pcap { font: 500 .72rem/1.6 var(--mono); color: var(--faint);
  margin: .3rem 0 0; }

/* the hover readout: one line under each chart that holds the value at the
   pointer, and the window's own headline number when the pointer is away. It is
   always present so the chart never needs to be read off its own pixels. */
.pchart .rdout { font: 500 .76rem/1.7 var(--mono); color: var(--faint);
  min-height: 1.7em; font-variant-numeric: tabular-nums; margin: .1rem 0 0; }
.pchart .rdout b { color: var(--ink); }
.pchart .cross { stroke: var(--muted); stroke-width: 1; stroke-dasharray: 2 3; }
.pchart .grid { stroke: var(--line-soft); stroke-width: 1; }
.pchart .axis { fill: var(--faint); font: 500 10px var(--mono); }
.pchart .ln { fill: none; stroke: currentColor; stroke-width: 2;
  stroke-linejoin: round; stroke-linecap: round; }
.pchart .fill { fill: currentColor; stroke: none; opacity: .15; }
.pchart .env { fill: currentColor; stroke: none; opacity: .18; }
.pchart .tick { stroke: currentColor; stroke-width: 2; opacity: .75; }
.pchart .nodata { fill: var(--faint); font: 500 10px var(--mono); opacity: .8; }
.pchart .hatch { fill: url(#pulse-hatch); }
.p-gpu { color: var(--sap); }
.p-mem { color: var(--leaf); }
.p-run { color: var(--sap); }
.p-plan { color: var(--leaf); }
.pstat { display: flex; flex-wrap: wrap; gap: .5rem; margin: 1rem 0 0; padding: 0;
  list-style: none; }
.pstat li { flex: 1 1 150px; padding: .6rem .8rem; border: 1px solid var(--line);
  border-radius: 10px; background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.pstat b { display: block; font: 700 1.28rem/1.25 var(--mono); color: var(--ink);
  font-variant-numeric: tabular-nums; }
.pstat span { font: 500 .72rem/1.5 var(--mono); color: var(--faint); }
.pnote { font: 500 .82rem/1.75 var(--mono); color: var(--faint); }
#pulse-live { font: 500 .82rem/1.75 var(--mono); color: var(--muted); }
"""


# ---- reading the cache ---------------------------------------------------------

def load(path: Path = None) -> dict | None:
    p = path or CACHE
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def clock(ts: int) -> str:
    return datetime.datetime.fromtimestamp(int(ts), TZ).strftime("%H:%M")


def stamp(ts: int) -> str:
    return datetime.datetime.fromtimestamp(int(ts), TZ).strftime("%Y-%m-%d %H:%M") + f" {TZ_LABEL}"


def ago(ts: int, now: int) -> str:
    """Plain English for how old a reading is — the page never shows a bare
    timestamp for freshness, because working out whether 00:45 was twenty
    minutes or twenty hours ago is the reader's job only if we shirk it."""
    d = max(0, int(now) - int(ts))
    if d < 90:
        return "just now"
    if d < 5400:
        return f"{d // 60} min ago"
    if d < 172800:
        return f"{d // 3600} h ago"
    return f"{d // 86400} days ago"


# ---- the chart engine ----------------------------------------------------------

def _x(t: float, t0: int, t1: int) -> float:
    if t1 <= t0:
        return PAD_L
    return PAD_L + (t - t0) / (t1 - t0) * PLOT_W


def _y(v: float, vmax: float) -> float:
    if vmax <= 0:
        return PAD_T + PLOT_H
    return PAD_T + PLOT_H - min(v / vmax, 1.0) * PLOT_H


def _frame(t0: int, t1: int, vmax: float, unit: str, ylabels: list) -> str:
    """Gridlines, y labels and six-hourly x ticks — identical on every chart."""
    out = []
    for v in ylabels:
        y = _y(v, vmax)
        out.append(f'<line class="grid" x1="{PAD_L}" y1="{y:.1f}" '
                   f'x2="{W - PAD_R}" y2="{y:.1f}"/>')
        txt = f"{v:g}{unit}"
        out.append(f'<text class="axis" x="{PAD_L - 6}" y="{y + 3.5:.1f}" '
                   f'text-anchor="end">{html.escape(txt)}</text>')
    # Ticks on round marks of the reader's own clock, not on offsets from "now" —
    # a tick that says 18:00 is a time he can compare with his memory. The
    # spacing follows the span because it has to: six-hourly ticks over a week
    # is twenty-eight labels in 700 pixels, which renders as a smear of digits
    # and is how the first draft of this page shipped its long chart.
    span = max(1, t1 - t0)
    if span <= 60 * 3600:
        step, fmt = 6 * 3600, "%H:%M"
    elif span <= 4 * 86400:
        step, fmt = 12 * 3600, "%H:%M"
    else:
        step, fmt = 86400, "%-d %b"
    first = datetime.datetime.fromtimestamp(t0, TZ).replace(
        minute=0, second=0, microsecond=0)
    first -= datetime.timedelta(hours=first.hour % (step // 3600))
    t = int(first.timestamp())
    while t <= t1:
        if t >= t0:
            x = _x(t, t0, t1)
            out.append(f'<line class="grid" x1="{x:.1f}" y1="{PAD_T}" '
                       f'x2="{x:.1f}" y2="{PAD_T + PLOT_H}"/>')
            lbl = datetime.datetime.fromtimestamp(t, TZ)
            # Midnight names its day even on an hourly axis: without it a
            # two-night chart is four identical clock faces and the reader has
            # to count gridlines to work out which night he is looking at.
            txt = lbl.strftime("%-d %b" if (step < 86400 and lbl.hour == 0) else fmt)
            anchor = "start" if x < PAD_L + 12 else ("end" if x > W - PAD_R - 12 else "middle")
            out.append(f'<text class="axis" x="{x:.1f}" y="{H - 8}" '
                       f'text-anchor="{anchor}">{html.escape(txt)}</text>')
        t += step
    return "".join(out)


def _runs(points: list) -> list:
    """Split [(t, v|None)] into the maximal stretches that carry data.

    A gap must break the path. Joining across one would draw a straight line
    through hours nobody measured and give it the same visual weight as a
    measurement — which on this page would specifically mean drawing an idle
    GPU through a period when the box was unreachable.
    """
    runs, cur = [], []
    for t, v in points:
        if v is None:
            if cur:
                runs.append(cur)
                cur = []
        else:
            cur.append((t, v))
    if cur:
        runs.append(cur)
    return runs


def _path(run: list, t0: int, t1: int, vmax: float, step: bool) -> str:
    d = []
    for i, (t, v) in enumerate(run):
        x, y = _x(t, t0, t1), _y(v, vmax)
        if i == 0:
            d.append(f"M{x:.1f} {y:.1f}")
        elif step:
            d.append(f"H{x:.1f}V{y:.1f}")
        else:
            d.append(f"L{x:.1f} {y:.1f}")
    return " ".join(d)


def uncached_band(t0: int, t1: int, cached_from: int | None) -> str:
    """Hatch the stretch of this window that predates the series entirely.

    THE WHOLE POINT OF THIS PAGE is that an empty chart means the machine was
    not working. The time-window selector broke that: pick seven days and the
    GPU chart's left-hand six are blank because the cache is a rolling day, not
    because the card sat still for six days. Words under the chart were not
    enough — the shape is what gets screenshotted. So the span with no cache
    behind it is struck out inside the plot, and the reader can see at a glance
    where the record starts.

    Only for the leading edge. A hole in the MIDDLE of a series is a real
    measurement gap and must keep looking like one.
    """
    if not cached_from or cached_from <= t0:
        return ""
    x = min(_x(cached_from, t0, t1), W - PAD_R)
    if x <= PAD_L + 1:
        return ""
    label = ""
    if x - PAD_L > 90:
        label = (f'<text class="nodata" x="{(PAD_L + x) / 2:.1f}" '
                 f'y="{PAD_T + PLOT_H / 2:.1f}" text-anchor="middle">'
                 f'not cached — the record starts here →</text>')
    return (f'<rect class="hatch" x="{PAD_L}" y="{PAD_T}" width="{x - PAD_L:.1f}" '
            f'height="{PLOT_H}"/>{label}')


def panel_svg(title: str, points: list, vmax: float, unit: str, ylabels: list,
              t0: int, t1: int, envelope: list = None, step: bool = False,
              ticks: list = None, empty_note: str = "",
              cached_from: int | None = None) -> str:
    """ONE WINDOW of one quantity, as a finished `<svg>`.

    `envelope` is an optional second array of the SAME quantity (peak against
    mean) drawn as a filled band under the line. `ticks` are discrete moments
    marked on the baseline — job completions under the queue.

    The window is stamped onto the element as data-t0/data-t1 so the hover
    script can turn a pointer position back into a time without knowing
    anything about how the path was drawn.
    """
    body = [uncached_band(t0, t1, cached_from), _frame(t0, t1, vmax, unit, ylabels)]
    runs = _runs(points)

    if envelope:
        for run in _runs(envelope):
            if len(run) < 2:
                continue
            base = PAD_T + PLOT_H
            d = _path(run, t0, t1, vmax, step)
            d += f" V{base:.1f} H{_x(run[0][0], t0, t1):.1f} Z"
            body.append(f'<path class="env" d="{d}"/>')

    for run in runs:
        if len(run) < 2:
            t, v = run[0]
            body.append(f'<circle class="fill" cx="{_x(t, t0, t1):.1f}" '
                        f'cy="{_y(v, vmax):.1f}" r="2.5" opacity=".9"/>')
            continue
        d = _path(run, t0, t1, vmax, step)
        base = PAD_T + PLOT_H
        fill = d + f" V{base:.1f} H{_x(run[0][0], t0, t1):.1f} Z"
        if not envelope:
            body.append(f'<path class="fill" d="{fill}"/>')
        body.append(f'<path class="ln" d="{d}"/>')

    for t in (ticks or []):
        if t0 <= t <= t1:
            x = _x(t, t0, t1)
            body.append(f'<line class="tick" x1="{x:.1f}" y1="{PAD_T + PLOT_H - 7}" '
                        f'x2="{x:.1f}" y2="{PAD_T + PLOT_H}"/>')

    if not runs and empty_note:
        body.append(f'<text class="nodata" x="{W / 2}" y="{PAD_T + PLOT_H / 2}" '
                    f'text-anchor="middle">{html.escape(empty_note)}</text>')

    # The crosshair is drawn hidden and moved by the hover script. It is part of
    # the built SVG rather than injected later so that the chart geometry has
    # exactly one definition — the script never computes a y, only an x.
    body.append(f'<line class="cross" x1="0" y1="{PAD_T}" x2="0" '
                f'y2="{PAD_T + PLOT_H}" style="display:none"/>')
    body.append(f'<rect x="{PAD_L}" y="{PAD_T}" width="{PLOT_W}" height="{PLOT_H}" '
                f'fill="transparent"/>')

    span = f"{stamp(t0)} to {stamp(t1)}"
    return (f'<svg viewBox="0 0 {W} {H}" role="img" data-t0="{t0}" data-t1="{t1}" '
            f'aria-label="{html.escape(title)}, {html.escape(span)}">'
            f'{"".join(body)}</svg>')


def chart(title: str, klass: str, panels: list, why: str = "",
          points_json: str = "", dec: int = 0, unit: str = "",
          step: bool = False, hint: str = "") -> str:
    """One quantity, one hue, one figure — with a finished panel per window.

    `panels` is [(hours, is_default, caption, svg)]. Every one of them is a real
    chart built above; the selector only decides which is displayed, so a reader
    switching windows is never shown a shape this file did not draw.

    `points_json` is the series ONCE, for the hover readout to name a value at
    the pointer. Once and not per panel: the panels are five views of the same
    numbers, and five copies of them is five times the page for no new fact.
    `hint` is what the readout says while nothing is under the pointer — the line
    holds its height either way, so the chart below it does not jump on hover.
    """
    wins = ""
    for hours, is_default, cap, svg in panels:
        wins += (f'<div class="pwin" data-h="{hours}"{"" if is_default else " hidden"}>'
                 f'{svg}<p class="pcap">{cap}</p></div>')
    why_html = (f'<details class="why"><summary>how to read this chart</summary>'
                f'<p>{why}</p></details>') if why else ""
    pts_attr = ""
    if points_json:
        pts_attr = (f' data-pts="{html.escape(points_json, quote=True)}"'
                    f' data-dec="{dec}" data-unit="{html.escape(unit, quote=True)}"'
                    f' data-dflt="{html.escape(hint, quote=True)}"'
                    + (' data-step="1"' if step else ""))
    return (f'<figure class="pchart {klass}"{pts_attr}>'
            f'<figcaption><span>{html.escape(title)}</span></figcaption>'
            f'{wins}<div class="rdout">{html.escape(hint)}</div>{why_html}</figure>')


# ---- turning the cache into points ---------------------------------------------

def gpu_points(gpu: dict, key: str, t0: int, t1: int) -> list:
    """The dense grid → [(unix, value|None)], clipped to the window.

    Buckets outside the cached range are absent rather than None-padded, so
    "the cache does not go back that far" and "the box was not sampling" stay
    distinguishable: the first is a shorter line, the second is a hole in one.
    """
    grid_t0, arr = gpu.get("t0"), gpu.get(key) or []
    if grid_t0 is None or not arr:
        return []
    bucket = int(gpu.get("bucket_seconds") or 300)
    out = []
    for i, v in enumerate(arr):
        t = grid_t0 + i * bucket
        if t0 <= t <= t1:
            out.append((t, v))
    return out


def queue_points(samples: list, idx: int, t0: int, t1: int, now: int) -> list:
    """Irregular commit-time samples → a step series over the window.

    The queue has a value at every instant but is only WRITTEN DOWN when
    someone commits, so the honest reading is a step: it held the last value
    until the next commit says otherwise. The series is extended to the right
    edge for that reason — the depth did not stop existing because nobody
    edited the file, and a line that stops at the last commit reads as an empty
    queue rather than an unchanged one.
    """
    if not samples:
        return []
    pts, carried = [], None
    for s in samples:
        t, v = s[0], s[idx]
        if t < t0:
            carried = v
            continue
        if t > t1:
            break
        if not pts and carried is not None:
            pts.append((t0, carried))
        pts.append((t, v))
    if not pts and carried is not None:
        pts = [(t0, carried)]
    # A revision that had no such list at all contributes a null, which breaks
    # the step rather than carrying a value across it: the queue did not hold
    # zero then, we simply have no reading. Only a real number is carried to
    # the right edge for the same reason.
    if pts and pts[-1][1] is not None:
        pts.append((min(t1, now), pts[-1][1]))
    return pts


def last_known(samples: list, idx: int):
    """The most recent value that was actually recorded, skipping the nulls a
    revision without that list leaves behind."""
    for s in reversed(samples or []):
        if s[idx] is not None:
            return s[idx]
    return None


def axis_top(samples: list, idx: int, floor: int) -> int:
    """A y-axis ceiling that never collapses onto the data and never rescales
    on a single busy hour: the tallest recorded value, or `floor` if the queue
    has never been deeper than that."""
    vals = [s[idx] for s in (samples or []) if s[idx] is not None]
    return max(floor, max(vals, default=floor))


def extent(data: dict) -> tuple[int | None, int | None]:
    """The oldest and newest moment ANY series in the cache carries a reading at.

    This is what decides which windows the selector offers, so it deliberately
    takes the union rather than the GPU grid alone: the queue is sampled per
    commit and reaches back days further than the five-minute vitals do, and a
    seven-day window that is real for the backlog chart should not be greyed out
    because the card's history is one day deep.
    """
    lo, hi = [], []
    gpu = data.get("gpu") or {}
    t0, bucket = gpu.get("t0"), int(gpu.get("bucket_seconds") or 300)
    n = max((len(gpu.get(k) or []) for k in ("u", "up", "v")), default=0)
    if t0 is not None and n:
        lo.append(t0)
        hi.append(t0 + (n - 1) * bucket)
    for s in (data.get("queue") or {}).get("samples") or []:
        lo.append(s[0])
        hi.append(s[0])
    for e in (data.get("jobs") or {}).get("events") or []:
        lo.append(e[0])
        hi.append(e[0])
    return (min(lo) if lo else None, max(hi) if hi else None)


def window_menu(earliest: int | None, latest: int | None, now: int) -> list:
    """[(hours, label, words, span, enabled, why_disabled)] — the selector's state.

    A window is enabled when the cache reaches back across COVERAGE of it AND
    holds something recent enough to land inside it. The second test is not
    redundant: a cache that stopped extending yesterday spans a week and still
    has nothing at all to say about the last hour, and offering "1h" there would
    hand the reader an empty frame with no explanation on it.
    """
    out = []
    for hours, label, words, span in WINDOWS:
        if earliest is None or latest is None:
            why = "there is nothing in the cache to draw"
        elif earliest > now - COVERAGE * hours * 3600:
            why = (f"the cache only reaches back to {stamp(earliest)}, which is "
                   f"less than {span}")
        elif latest < now - hours * 3600:
            why = (f"nothing has been cached since {stamp(latest)}, so {span} "
                   f"holds no reading at all")
        else:
            out.append((hours, label, words, span, True, ""))
            continue
        out.append((hours, label, words, span, False, why))
    return out


def busy_minutes(gpu: dict, t0: int, t1: int) -> tuple[float, int, int]:
    """GPU-equivalent busy minutes in the window, and how much was measured.

    Mean utilisation × bucket length, summed. This is the closest thing to an
    honest "how much of the card did we actually use" from a percentage series,
    and it deliberately reads LOW against a human's memory of the day: a bucket
    at 100% peak and 8% mean was 24 seconds of work and four and a half minutes
    of nothing, and it should count as the former.
    """
    bucket = int(gpu.get("bucket_seconds") or 300)
    pts = gpu_points(gpu, "u", t0, t1)
    measured = sum(1 for _, v in pts if v is not None)
    mins = sum((v / 100) * (bucket / 60) for _, v in pts if v is not None)
    return mins, measured, len(pts)


def idle_stretch(gpu: dict, t0: int, t1: int) -> tuple[float, int | None]:
    """The longest run of consecutive measured buckets whose PEAK stayed under
    5%, in hours, plus when it started. Peak and not mean: a bucket whose peak
    never left the floor is a bucket in which the card did nothing at all, and
    that is the claim this number makes. Unmeasured buckets end a run — an
    unreachable box is not an idle one."""
    bucket = int(gpu.get("bucket_seconds") or 300)
    pts = gpu_points(gpu, "up", t0, t1)
    best = run = 0
    best_start = start = None
    for t, v in pts:
        if v is not None and v < 5:
            if run == 0:
                start = t
            run += 1
            if run > best:
                best, best_start = run, start
        else:
            run = 0
    return best * bucket / 3600, best_start


# ---- the page ------------------------------------------------------------------

LIVE_JS = """
/* THE LIVE TAIL. The charts above are built and never move; this adds one
   sentence about right now, from the same two files the graphs are made of.
   Fetched in the reader's browser because a build-time read would be as fresh
   as the last deploy, and "is the box working at this moment" is exactly the
   question a half-hourly snapshot cannot answer.
   raw.githubusercontent sends Access-Control-Allow-Origin: * and sits behind a
   CDN, hence the per-minute cache-buster: without it a reader who reloads gets
   the same edge copy back and reads it as a frozen machine. */
(function () {
  var TEL = "__TEL__", Q = "__Q__";
  var el = document.getElementById("pulse-live");
  if (!el) return;
  function bust() { return Math.floor(Date.now() / 60000); }
  function grab(url) {
    return fetch(url + "?_=" + bust(), { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.text();
    });
  }
  function mins(sec) { return Math.round((Date.now() / 1000 - sec) / 60); }
  function queueCounts(text) {
    var sec = null, n = { tasks: 0, backlog: 0 }, saw = {};
    var lines = text.split("\\n");
    for (var i = 0; i < lines.length; i++) {
      var L = lines[i];
      if (/^tasks:\\s*$/.test(L)) { sec = "tasks"; saw.tasks = 1; continue; }
      if (/^backlog:\\s*$/.test(L)) { sec = "backlog"; saw.backlog = 1; continue; }
      if (/^[A-Za-z_][\\w-]*:/.test(L)) { sec = null; continue; }
      if (sec && /^-\\s+id:\\s*\\S+/.test(L)) { n[sec]++; }
    }
    return { tasks: saw.tasks ? n.tasks : null, backlog: saw.backlog ? n.backlog : null };
  }
  Promise.all([grab(TEL).catch(function () { return null; }),
               grab(Q).catch(function () { return null; })])
    .then(function (r) {
      var bits = [];
      if (r[0]) {
        try {
          var tel = JSON.parse(r[0]);
          var age = mins(tel.last_sample);
          /* Ten minutes is two publish intervals. Past that the box is not
             reporting and this line says so rather than quoting a number that
             stopped being true. */
          if (age > 10) {
            bits.push("the render box has not published a sample for " + age +
              " minutes, so nothing here is a reading of right now");
          } else {
            var u = tel.u || [], v = tel.v || [], last = null, lv = null;
            for (var i = u.length - 1; i >= 0; i--) {
              if (u[i] !== null) { last = u[i]; lv = (v[i] === undefined ? null : v[i]); break; }
            }
            bits.push("the render box checked in " + (age <= 1 ? "just now" : age + " min ago") +
              (last === null ? "" : " at " + last + "% GPU" +
                (lv === null ? "" : " and " + lv + " GB of video memory")));
          }
        } catch (e) { bits.push("the render box's file could not be read"); }
      } else {
        bits.push("the render box's file could not be fetched just now");
      }
      if (r[1]) {
        var q = queueCounts(r[1]);
        if (q.tasks !== null) {
          bits.push("the queue holds " + q.tasks + " runnable and " +
            (q.backlog === null ? "an unread number of" : q.backlog) + " planned right now");
        }
      } else {
        bits.push("the queue could not be re-read just now");
      }
      el.textContent = "Read live in your browser: " + bits.join("; ") + ".";
    });
})();
"""


WIN_JS = """
/* ---- the time-window selector ------------------------------------------------
   Every panel on this page was drawn by the builder. This switches which one is
   shown and nothing else: no path is computed here, no axis is scaled here, and
   there is no second chart engine to drift from the one the tests cover. The bar
   is emitted hidden and unhidden below, so a reader with JavaScript off sees the
   default window and no dead buttons.

   The hover readout is the other half. It maps a pointer position back to a time
   through the panel's own data-t0/data-t1 — the same two numbers the builder
   scaled the path with — then names the nearest reading. It never draws a value;
   it reads one out. */
(function () {
  var bar = document.getElementById("winbar");
  if (!bar) return;
  var note = document.getElementById("winnote");
  var btns = bar.querySelectorAll("button[data-h]");
  var figs = document.querySelectorAll(".pchart");
  var tiles = document.querySelectorAll(".pstat[data-h]");
  bar.hidden = false;

  function show(h) {
    var i, j, panels;
    for (i = 0; i < figs.length; i++) {
      panels = figs[i].querySelectorAll(".pwin");
      for (j = 0; j < panels.length; j++) {
        panels[j].hidden = panels[j].getAttribute("data-h") !== h;
      }
    }
    for (i = 0; i < tiles.length; i++) {
      tiles[i].hidden = tiles[i].getAttribute("data-h") !== h;
    }
    for (i = 0; i < btns.length; i++) {
      var on = btns[i].getAttribute("data-h") === h;
      btns[i].setAttribute("aria-pressed", on ? "true" : "false");
      if (on && note) { note.textContent = btns[i].getAttribute("data-words"); }
    }
    for (i = 0; i < figs.length; i++) { reset(figs[i]); }
  }

  for (var k = 0; k < btns.length; k++) {
    (function (b) {
      if (b.disabled) return;
      b.addEventListener("click", function () { show(b.getAttribute("data-h")); });
    })(btns[k]);
  }

  /* ---- hover: the value under the pointer, in words --------------------- */
  var PAD_L = WIN_PAD_L, PLOT_W = WIN_PLOT_W, VW = WIN_W;

  function fmt(v, dec, unit) {
    return v === null || v === undefined ? "\\u2014" : v.toFixed(dec) + unit;
  }
  function hhmm(sec) {
    var d = new Date((sec + WIN_TZ_OFFSET) * 1000);
    return ("0" + d.getUTCHours()).slice(-2) + ":" + ("0" + d.getUTCMinutes()).slice(-2);
  }
  function dayhhmm(sec) {
    var d = new Date((sec + WIN_TZ_OFFSET) * 1000);
    return d.getUTCDate() + " " + WIN_MONTHS[d.getUTCMonth()] + " " + hhmm(sec);
  }
  function reset(fig) {
    var out = fig.querySelector(".rdout");
    if (out) { out.textContent = fig.getAttribute("data-dflt") || ""; }
    var lines = fig.querySelectorAll(".cross");
    for (var i = 0; i < lines.length; i++) { lines[i].style.display = "none"; }
  }

  for (var f = 0; f < figs.length; f++) {
    (function (fig) {
      var raw = fig.getAttribute("data-pts");
      if (!raw) return;
      var pts;
      try { pts = JSON.parse(raw); } catch (e) { return; }
      var dec = +(fig.getAttribute("data-dec") || 0);
      var unit = fig.getAttribute("data-unit") || "";
      var step = fig.getAttribute("data-step") === "1";
      var out = fig.querySelector(".rdout");
      var svgs = fig.querySelectorAll("svg");

      for (var s = 0; s < svgs.length; s++) {
        (function (svg) {
          var t0 = +svg.getAttribute("data-t0"), t1 = +svg.getAttribute("data-t1");
          var cross = svg.querySelector(".cross");
          svg.addEventListener("pointermove", function (e) {
            var r = svg.getBoundingClientRect();
            /* viewBox units, not pixels: the SVG is scaled to the column width
               and the geometry below is the builder's, in its own coordinates. */
            var vx = (e.clientX - r.left) / r.width * VW;
            var frac = Math.max(0, Math.min(1, (vx - PAD_L) / PLOT_W));
            var want = t0 + frac * (t1 - t0), best = -1, i, d;
            if (step) {
              /* A STEP SERIES HOLDS ITS VALUE BETWEEN SAMPLES, so the reading at
                 the pointer is the last one written down at or before it — not
                 the nearest one. Nearest would report a queue depth from a
                 commit that had not happened yet, which is the one thing the
                 step drawing exists to avoid. */
              for (i = 0; i < pts.length; i++) {
                if (pts[i][0] <= want && pts[i][1] !== null) { best = i; }
              }
            } else {
              var bd = Infinity;
              for (i = 0; i < pts.length; i++) {
                if (pts[i][0] < t0 || pts[i][0] > t1 || pts[i][1] === null) continue;
                d = Math.abs(pts[i][0] - want);
                if (d < bd) { bd = d; best = i; }
              }
              /* Nothing within a twentieth of the window is nothing to report —
                 without this the readout names a point off the edge of a gap and
                 makes an unmeasured stretch look measured. */
              if (best >= 0 && bd > (t1 - t0) / 20) { best = -1; }
            }
            if (best < 0) { reset(fig); return; }
            var px = PAD_L + (Math.max(t0, Math.min(t1, want)) - t0) / (t1 - t0) * PLOT_W;
            cross.setAttribute("x1", px.toFixed(1));
            cross.setAttribute("x2", px.toFixed(1));
            cross.style.display = "";
            if (out) {
              out.innerHTML = dayhhmm(step ? want : pts[best][0]) + " " + WIN_TZ +
                " \\u00b7 <b>" + fmt(pts[best][1], dec, unit) + "</b>" +
                (step ? " <span>(set " + dayhhmm(pts[best][0]) + ")</span>" : "");
            }
          });
          svg.addEventListener("pointerleave", function () { reset(fig); });
        })(svgs[s]);
      }
      reset(fig);
    })(figs[f]);
  }
})();
"""


def coverage_note(gpu: dict, t0: int, t1: int) -> str:
    """How much of this window the five-minute cache actually holds.

    Printed under every GPU/memory panel, because the same blank left-hand side
    means two opposite things — a young cache and a machine that was not
    reporting — and only this sentence can tell them apart.
    """
    bucket = int(gpu.get("bucket_seconds") or 300)
    total = max(1, (t1 - t0) // bucket)
    measured = sum(1 for _, v in gpu_points(gpu, "u", t0, t1) if v is not None)
    grid_t0 = gpu.get("t0")
    txt = f"{measured} of {total} five-minute slots measured"
    if grid_t0 and grid_t0 > t0 + bucket:
        txt += (f" · nothing is cached before {stamp(grid_t0)} — the blank on the "
                f"left is this cache's age, not the machine's")
    return txt


def queue_note(samples: list, t0: int, t1: int) -> str:
    """How many times the queue file was written inside this window."""
    n = sum(1 for s in samples if t0 <= s[0] <= t1)
    if not n:
        return ("no commit to the queue file inside this window — the line is the "
                "depth carried in from before it")
    return f"{n} commit{'' if n == 1 else 's'} to the queue file in this window"


def words_line(words: str, ok: bool, why: str) -> str:
    """The sentence under the selector for one window."""
    if not ok:
        return f"{words} is not available — {why}."
    return f"Showing {words}, to {TZ_LABEL} clocks."


def stat_tiles(gpu: dict, qsamples: list, done: list, span: str,
               t0: int, t1: int, now: int) -> str:
    """The headline numbers FOR ONE WINDOW.

    They move with the selector because they have to: "68 min of GPU work" is
    not a fact about the farm, it is a fact about a span, and leaving a 48-hour
    total sitting over a one-hour chart would make the page contradict itself on
    the reader's first click. The two queue depths are the exception — they are
    the newest reading there is, at every span.
    """
    mins, measured, _total = busy_minutes(gpu, t0, t1)
    idle_h, idle_from = idle_stretch(gpu, t0, t1)
    bucket_min = int(gpu.get("bucket_seconds") or 300) / 60
    measured_min = measured * bucket_min
    # DENOMINATED BY WHAT WAS MEASURED, never by the width of the chart. The
    # window can be wider than the cache, and dividing by the window would
    # quietly report a busy machine as a lazy one — the first draft of this tile
    # said 2.4% when the measured answer was 4.7%. Unmeasured time is not idle
    # time and cannot be a denominator.
    pct = (mins / measured_min * 100) if measured_min else 0
    measured_h = measured_min / 60

    stats = [
        (f"{mins:.0f} min", f"of GPU work in the {measured_h:.1f} h measured "
                            f"· {pct:.1f}% of the card"),
        (f"{idle_h:.1f} h", "longest unbroken idle stretch"
                            + (f" (from {clock(idle_from)})" if idle_from else "")),
        (str(last_known(qsamples, 1)) if last_known(qsamples, 1) is not None else "—",
         "runnable when last written down"),
        (str(last_known(qsamples, 2)) if last_known(qsamples, 2) is not None else "—",
         "planned (backlog)"),
        (str(sum(1 for t in done if t0 <= t <= t1)), f"jobs finished in {span}"),
    ]
    return "".join(f"<li><b>{html.escape(a)}</b><span>{html.escape(b)}</span></li>"
                   for a, b in stats)


def render(data: dict | None, now: int = None) -> str:
    """The page body. Returns HTML; every unavailable series says so in words."""
    now = now or int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    live = ('<p id="pulse-live">Reading the machine and the queue live…</p>')

    if not data:
        return (f"<style>{CSS}</style>"
                "<h1>The pulse</h1>"
                '<p class="lede">The work queue and the render box\'s resource use, '
                "over time.</p>"
                '<p class="notice">There is no cached series to draw. '
                "<code>pipeline/pulse-series.json</code> could not be read, so this page "
                "will not put a shape on the screen — an invented chart of a farm nobody "
                "measured would be worse than this sentence. Run "
                "<code>python3 pipeline/pulse_series.py</code> on a machine with the git "
                "refs and the graphs come back.</p>"
                f"{live}")

    gpu = data.get("gpu") or {}
    qsamples = (data.get("queue") or {}).get("samples") or []
    events = (data.get("jobs") or {}).get("events") or []
    cached_at = int(data.get("generated") or 0)

    vram_total = float(gpu.get("vram_total_gb") or 24)
    vmax_gb = max(4.0, round(vram_total))
    done = sorted(e[0] for e in events if len(e) > 1 and e[1] == "done")

    # ---- which windows this cache can honestly draw ----------------------------
    earliest, latest = extent(data)
    menu = window_menu(earliest, latest, now)
    offered = [m for m in menu if m[4]]
    # The default is 48 h when the cache can cover it — two nights, the picture
    # this page was built to show — and otherwise the widest window it can.
    default_h = WINDOW_HOURS if any(m[0] == WINDOW_HOURS for m in offered) else (
        max((m[0] for m in offered), default=WINDOW_HOURS))

    # Y-AXIS CEILINGS ARE FIXED ACROSS EVERY WINDOW, computed from the whole
    # cache rather than from the window on screen. A queue axis that rescaled on
    # each pick would redraw a quiet hour as a busy one at 1h and a busy day as a
    # quiet one at 7d, and the reader would be comparing two different rulers
    # without being told. The GPU axis is a percentage and was never free to move.
    run_top = axis_top(qsamples, 1, 6)
    plan_top = axis_top(qsamples, 2, 4)
    first_queue = next((s[0] for s in qsamples if s[1] is not None), None)
    first_backlog = next((s[0] for s in qsamples if s[2] is not None), None)

    gpu_name = html.escape(str(gpu.get("gpu_name") or "the render box"))

    # ---- the panels: every offered window, drawn here --------------------------
    gpu_panels, mem_panels, run_panels, plan_panels, tiles = [], [], [], [], []
    for hours, label, words, span, ok, _why in menu:
        if not ok:
            continue
        t0, t1 = now - hours * 3600, now
        is_def = hours == default_h
        cov = coverage_note(gpu, t0, t1)
        qn = queue_note(qsamples, t0, t1)

        gpu_panels.append((hours, is_def, html.escape(f"{gpu_name} · {cov}"),
                           panel_svg("GPU utilisation", gpu_points(gpu, "u", t0, t1),
                                     100, "%", [0, 50, 100], t0, t1,
                                     envelope=gpu_points(gpu, "up", t0, t1),
                                     cached_from=gpu.get("t0"),
                                     empty_note="no GPU samples cached for this window")))
        mem_panels.append((hours, is_def,
                           html.escape(f"of {vram_total:g} GB on the card · {cov}"),
                           panel_svg("Video memory in use", gpu_points(gpu, "v", t0, t1),
                                     vmax_gb, " GB", [0, vmax_gb / 2, vmax_gb], t0, t1,
                                     cached_from=gpu.get("t0"),
                                     empty_note="no memory samples cached for this window")))
        run_panels.append((hours, is_def, html.escape(qn),
                           panel_svg("Work queue — runnable now",
                                     queue_points(qsamples, 1, t0, t1, now),
                                     run_top, "", [0, run_top], t0, t1, step=True,
                                     ticks=[t for t in done if t0 <= t <= t1],
                                     cached_from=first_queue,
                                     empty_note="no queue commits in this window")))
        plan_panels.append((hours, is_def, html.escape(qn),
                            panel_svg("Planned work (backlog)",
                                      queue_points(qsamples, 2, t0, t1, now),
                                      plan_top, "", [0, plan_top / 2, plan_top], t0, t1,
                                      step=True, cached_from=first_backlog,
                                      empty_note="no queue commits cached")))
        tiles.append((hours, is_def, stat_tiles(gpu, qsamples, done, span, t0, t1, now)))

    # ---- the selector ----------------------------------------------------------
    buttons = ""
    for hours, label, words, _span, ok, why in menu:
        pressed = "true" if (ok and hours == default_h) else "false"
        dis = "" if ok else f' disabled title="{html.escape(why, quote=True)}"'
        buttons += (f'<button type="button" data-h="{hours}" '
                    f'data-words="{html.escape(words_line(words, ok, why), quote=True)}" '
                    f'aria-pressed="{pressed}"{dis}>{html.escape(label)}</button>')
    default_words = next((words_line(w, True, "") for h, _l, w, _s, ok, _y in menu
                          if ok and h == default_h), "")
    greyed = [m[1] for m in menu if not m[4]]
    grey_line = ""
    if greyed:
        grey_line = (" Greyed out: " + ", ".join(greyed) +
                     " — the cache does not reach back that far yet; hover one to "
                     "see how far it does reach.")
    winbar = (f'<div class="winbar" id="winbar" role="group" '
              f'aria-label="Time window" hidden>'
              f'<span class="lbl">Time window</span>'
              f'<div class="winbtns">{buttons}</div>'
              f'<p class="winnote" id="winnote">{html.escape(default_words)}'
              f'{html.escape(grey_line)}</p></div>')

    stat_html = "".join(
        f'<ul class="pstat" data-h="{hours}"{"" if is_def else " hidden"}>{body}</ul>'
        for hours, is_def, body in tiles)

    charts = [
        chart("GPU utilisation", "p-gpu", gpu_panels,
              hint="point anywhere on the chart to read the card's load at that minute",
              points_json=json.dumps(gpu_points(gpu, "u", 0, now), separators=(",", ":")),
              dec=0, unit="%",
              why="The line is each five minutes' average; the band behind it is the "
                  "highest single reading in the same five minutes. They separate when "
                  "the card works in bursts — a tall band over a low line is a short "
                  "render, not a busy afternoon. A break in the line is a stretch the "
                  "box did not report, which is not the same as a stretch it spent idle."),
        chart("Video memory in use", "p-mem", mem_panels,
              hint="point anywhere on the chart to read the memory in use at that minute",
              points_json=json.dumps(gpu_points(gpu, "v", 0, now), separators=(",", ":")),
              dec=1, unit=" GB",
              why="Weights stay resident between beats, so this stays high while a "
                  "model is loaded and drops when the process exits — it reads as "
                  "'a pipeline is up', where the chart above reads as 'it is computing'."),
        chart("Work queue — runnable now", "p-run", run_panels, step=True,
              hint="point anywhere on the chart to read the depth in force at that moment",
              points_json=json.dumps([[s[0], s[1]] for s in qsamples],
                                     separators=(",", ":")),
              dec=0, unit=" runnable",
              why="A step, because the queue is only written down when someone commits "
                  "the file — it held the last value through the flat parts rather than "
                  "being unmeasured there. Every worker reads this list and nothing else, "
                  "so a raised line here is work the farm was free to start. Each tick on "
                  "the floor is a job a machine logged as finished."),
    ]

    backlog_why = ("The backlog is invisible to every worker by design — it is where "
                   "work waits with its blocker written down. Growing while the chart "
                   "above stays flat means the planning is outrunning the machine.")
    if first_backlog and qsamples and first_backlog > qsamples[0][0] + 3600:
        backlog_why += (f" The line starts at {stamp(first_backlog)} because the file "
                        f"had no <code>backlog:</code> list before then — the days to "
                        f"its left are unrecorded, not empty.")
    charts.append(chart("Planned work (backlog)", "p-plan", plan_panels, step=True,
                        hint="point anywhere on the chart to read the depth in force "
                             "at that moment",
                        points_json=json.dumps([[s[0], s[2]] for s in qsamples],
                                               separators=(",", ":")),
                        dec=0, unit=" planned",
                        why=backlog_why))

    src = data.get("jobs", {}).get("branches") or []
    return f"""<style>{CSS}</style>
<h1>The pulse</h1>
<p class="lede">What the farm had to do, and what the render box was actually doing
while it had to do it. Both graphs share one clock, so you can read straight down
a moment and see whether the machine was on the work.</p>
{HATCH_DEFS}
{winbar}
{stat_html}
{live}
<div class="pulse-grid">{"".join(charts)}</div>
<h2>What this page can and cannot know</h2>
<p class="pnote">
<b>Clocks are {TZ_LABEL}.</b> The cache underneath is UTC; every face on this page
is converted once, here.<br>
<b>Every window on the selector is a chart built when the site built.</b> Switching
window swaps in another finished panel — nothing on this page is redrawn in your
browser, so the shape you are looking at is the shape that was published. A window
the cache cannot reach across is greyed out rather than drawn half-empty.<br>
<b>The y axis does not move when the window does.</b> Each chart's ceiling is set
from the whole cache, so a quiet hour looks quiet at every span instead of being
rescaled into a busy one.<br>
<b>The graphs are as old as the cache: extended {stamp(cached_at)}
({ago(cached_at, now)}).</b> They are drawn into the HTML when the site builds, from
<code>pipeline/pulse-series.json</code>. The one live line is the sentence above the
charts, which your browser fetches straight from the machine and the queue file.<br>
<b>Where each series comes from.</b> GPU and memory: the box samples itself every ten
seconds and publishes a rolling 24-hour summary to its courier branch, which
<code>pulse_series.py</code> folds into a five-minute grid — that folding is the only
reason a history exists at all, because the courier force-pushes and keeps no past.
Queue depth: one sample per commit to <code>pipeline/farm-queue.yaml</code>. Finished
jobs: the check-in logs of {len(src)} machine branches ({html.escape(", ".join(src)) or "none"}).<br>
<b>Job times are stamped from the commit that carried them.</b> The boxes log a
time of day and no date, so each line is dated by the push that published it — right
to within a courier interval for a machine, and wrong for a line written by hand
about earlier work, which lands where it was recorded rather than where it happened.<br>
<b>A gap is a gap.</b> No series here is filled in with zero when a reading is
missing. An unreported stretch leaves a hole in the line, because a dead network
link and a resting GPU are opposite facts that look identical at zero.
</p>
<p class="pnote">The minute-by-minute view of the same box, drawn live in your
browser, is on <a href="status.html">the studio page</a>. This page is the long
one.</p>
"""


def build(out_dir: Path):
    # page() carries the build-commit stamp (see build_commit.py), so this
    # builder is stamped by using it and needs no second mechanism — pulse.html
    # is the only file it writes, and it writes it through page().
    from build_site import page   # late import: build_site calls us
    data = load()
    body = render(data)
    # The selector script is handed the SAME geometry and the SAME clock the
    # panels were drawn with, rather than repeating either as a literal. A
    # crosshair placed by a second copy of PAD_L would sit next to the line it is
    # supposed to be on, and a readout on a second copy of the timezone would
    # name a different hour than the axis under it.
    consts = (f"var WIN_W={W},WIN_PAD_L={PAD_L},WIN_PLOT_W={PLOT_W},"
              f"WIN_TZ={json.dumps(TZ_LABEL)},"
              f"WIN_TZ_OFFSET={int(TZ.utcoffset(None).total_seconds())},"
              f"WIN_MONTHS={json.dumps(MONTHS)};")
    tail = ("<script>" + consts +
            LIVE_JS.replace("__TEL__", TELEMETRY_URL).replace("__Q__", QUEUE_URL) +
            WIN_JS + "</script>")
    out = Path(out_dir) / "pulse.html"
    out.write_text(page(
        "The pulse — queue and machine over time",
        body,
        path="pulse.html",
        desc="Work queued against the render box's GPU and memory use over time, "
             "on one shared clock.",
        tail=tail,
    ))
    print("✓ pulse.html")


if __name__ == "__main__":
    build(REPO / "_site")
