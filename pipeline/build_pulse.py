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
The only script on the page is the live tail, which adds a sentence about now
and never redraws a chart — a chart that changes shape after load is a chart
you cannot cite.

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

# 48 hours: two nights, so "it idled overnight" and "it idles every night" are
# different pictures rather than the same one. The cache keeps seven days and
# the backlog chart below spends them.
WINDOW_HOURS = 48
LONG_WINDOW_HOURS = 24 * 7

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
  border: 1px solid var(--line); border-radius: 12px; }
.pchart .why { font: 500 .78rem/1.65 var(--mono); color: var(--faint);
  margin: .15rem 0 0; }
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


def chart(title: str, cap: str, klass: str, points: list, vmax: float,
          unit: str, ylabels: list, t0: int, t1: int, why: str = "",
          envelope: list = None, step: bool = False, ticks: list = None,
          empty_note: str = "") -> str:
    """One quantity, one hue, one chart. `points` is [(unix, value|None)].

    `envelope` is an optional second array of the SAME quantity (peak against
    mean) drawn as a filled band under the line. `ticks` are discrete moments
    marked on the baseline — job completions under the queue.
    """
    body = [_frame(t0, t1, vmax, unit, ylabels)]
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

    why_html = f'<p class="why">{why}</p>' if why else ""
    return (f'<figure class="pchart {klass}">'
            f'<figcaption><span>{html.escape(title)}</span>'
            f'<span class="cap">{html.escape(cap)}</span></figcaption>'
            f'<svg viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{html.escape(title)} — {html.escape(cap)}">'
            f'{"".join(body)}</svg>{why_html}</figure>')


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

    t1 = now
    t0 = t1 - WINDOW_HOURS * 3600
    lt0 = t1 - LONG_WINDOW_HOURS * 3600

    vram_total = float(gpu.get("vram_total_gb") or 24)
    vmax_gb = max(4.0, round(vram_total))

    u_pts = gpu_points(gpu, "u", t0, t1)
    up_pts = gpu_points(gpu, "up", t0, t1)
    v_pts = gpu_points(gpu, "v", t0, t1)

    done = sorted(e[0] for e in events if len(e) > 1 and e[1] == "done")
    done_win = [t for t in done if t0 <= t <= t1]

    mins, measured, total_b = busy_minutes(gpu, t0, t1)
    idle_h, idle_from = idle_stretch(gpu, t0, t1)
    # DENOMINATED BY WHAT WAS MEASURED, never by the width of the chart. The
    # window is 48 hours and the cache currently holds 24, so dividing by the
    # window would have quietly halved the figure and reported a busier machine
    # as a lazier one — the first draft of this tile said 2.4% when the measured
    # answer was 4.7%. Unmeasured time is not idle time and cannot be a
    # denominator.
    bucket_min = int(gpu.get("bucket_seconds") or 300) / 60
    measured_min = measured * bucket_min
    measured_h = measured_min / 60
    pct = (mins / measured_min * 100) if measured_min else 0

    runnable_now = last_known(qsamples, 1)
    planned_now = last_known(qsamples, 2)

    # The left edge of a young cache is not machine downtime, and the caption
    # has to say which it is before the reader decides for himself.
    grid_t0 = gpu.get("t0")
    short = ""
    if grid_t0 and grid_t0 > t0 + 3600:
        short = (f" · nothing is cached before {stamp(grid_t0)} — this cache was "
                 f"started then, and the blank left-hand side is its age, not the "
                 f"machine's")

    stats = [
        (f"{mins:.0f} min", f"of GPU work in the {measured_h:.0f} h measured "
                            f"· {pct:.1f}% of the card"),
        (f"{idle_h:.1f} h", "longest unbroken idle stretch"
                            + (f" (from {clock(idle_from)})" if idle_from else "")),
        (str(runnable_now) if runnable_now is not None else "—", "runnable when last written down"),
        (str(planned_now) if planned_now is not None else "—", "planned (backlog)"),
        (str(len(done_win)), f"jobs finished in {WINDOW_HOURS} h"),
    ]
    stat_html = "".join(f"<li><b>{html.escape(a)}</b><span>{html.escape(b)}</span></li>"
                        for a, b in stats)

    gpu_name = html.escape(str(gpu.get("gpu_name") or "the render box"))
    measured_cap = (f"{measured} of {total_b} five-minute slots measured"
                    if total_b else "no slots measured")

    charts = [
        chart(
            "GPU utilisation", f"{gpu_name} · {measured_cap}{short}", "p-gpu",
            u_pts, 100, "%", [0, 50, 100], t0, t1,
            envelope=up_pts,
            empty_note="no GPU samples cached for this window",
            why="The line is each five minutes' average; the band behind it is the "
                "highest single reading in the same five minutes. They separate when "
                "the card works in bursts — a tall band over a low line is a short "
                "render, not a busy afternoon. A break in the line is a stretch the "
                "box did not report, which is not the same as a stretch it spent idle."),
        chart(
            "Video memory in use", f"of {vram_total:g} GB on the card", "p-mem",
            v_pts, vmax_gb, " GB", [0, vmax_gb / 2, vmax_gb], t0, t1,
            empty_note="no memory samples cached for this window",
            why="Weights stay resident between beats, so this stays high while a "
                "model is loaded and drops when the process exits — it reads as "
                "'a pipeline is up', where the chart above reads as 'it is computing'."),
        chart(
            "Work queue — runnable now", "entries under tasks: · marks below are finished jobs",
            "p-run",
            queue_points(qsamples, 1, t0, t1, now), axis_top(qsamples, 1, 6),
            "", [0, axis_top(qsamples, 1, 6)], t0, t1,
            step=True, ticks=done_win,
            empty_note="no queue commits in this window",
            why="A step, because the queue is only written down when someone commits "
                "the file — it held the last value through the flat parts rather than "
                "being unmeasured there. Every worker reads this list and nothing else, "
                "so a raised line here is work the farm was free to start. Each tick on "
                "the floor is a job a machine logged as finished."),
    ]

    long_q = queue_points(qsamples, 2, lt0, t1, now)
    qmax = axis_top(qsamples, 2, 4)
    first_backlog = next((s[0] for s in qsamples if s[2] is not None), None)
    backlog_why = ("The backlog is invisible to every worker by design — it is where "
                   "work waits with its blocker written down. Growing while the chart "
                   "above stays flat means the planning is outrunning the machine.")
    if first_backlog and first_backlog > lt0 + 3600:
        backlog_why += (f" The line starts at {stamp(first_backlog)} because the file "
                        f"had no <code>backlog:</code> list before then — the days to "
                        f"its left are unrecorded, not empty.")
    charts.append(chart(
        "Planned work (backlog) — seven days", "entries under backlog:", "p-plan",
        long_q, qmax, "", [0, qmax / 2, qmax], lt0, t1, step=True,
        empty_note="no queue commits cached",
        why=backlog_why))

    src = data.get("jobs", {}).get("branches") or []
    return f"""<style>{CSS}</style>
<h1>The pulse</h1>
<p class="lede">What the farm had to do, and what the render box was actually doing
while it had to do it. Both graphs share one clock, so you can read straight down
a moment and see whether the machine was on the work.</p>
<ul class="pstat">{stat_html}</ul>
{live}
<div class="pulse-grid">{"".join(charts)}</div>
<h2>What this page can and cannot know</h2>
<p class="pnote">
<b>Clocks are {TZ_LABEL}.</b> The cache underneath is UTC; every face on this page
is converted once, here.<br>
<b>The graphs are as old as the cache: extended {stamp(cached_at)}
({ago(cached_at, now)}).</b> They are drawn into the HTML when the site builds, from
<code>pipeline/pulse-series.json</code>. Nothing on this page redraws itself — the one
live line is the sentence above the charts, which your browser fetches straight from
the machine and the queue file.<br>
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
    from build_site import page   # late import: build_site calls us
    data = load()
    body = render(data)
    tail = ("<script>" +
            LIVE_JS.replace("__TEL__", TELEMETRY_URL).replace("__Q__", QUEUE_URL) +
            "</script>")
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
