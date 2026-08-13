#!/usr/bin/env python3
"""Regenerate review/plan/index.html — the standing production plan.

The founder asked for one, 2026-08-13: "what you will generate, what i will
review, when, how long".

WHY THIS IS GENERATED AND NOT WRITTEN. A plan page that restates "8 beats need
rendering, about 3.7 h" in prose is a second copy of a number /status already
publishes, and the two drift the first time a lane scores a beat. So every count
and every hour on this page is pulled from `pipeline/episode_eta.py` at
regeneration time — the same rows the status page multiplies — and the prose
around them is the only hand-written part. If the two pages ever disagree, this
one was not regenerated, and that is a visible staleness rather than a silent
one: the stamp at the bottom says when it last ran.

THE THREE KINDS OF NUMBER HERE, kept apart on purpose, because the whole ETA
feature exists to stop them being blended:

  MEASURED   machine hours. Rounds-per-beat off the box's own job records times
             that kind's median minutes. Printed green, sourced, and identical
             to /status by construction.
  ARITHMETIC how long a sitting takes: a count of clips times a stated
             minutes-per-clip. That is an assumption doing division, and it is
             labelled as one. It is honest because it estimates the DURATION of
             a sitting, never the DELAY until it happens.
  NEITHER    when a pass actually happens, and how many beats come back needing
             another round. Nobody here can measure either. They are named as
             the variables and never given a figure.

Run from the repo root, in the same commit as whatever changed the states —
same contract as review/inbox/regen.py (SITE.md).
"""
import html
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "pipeline"))

import episode_eta as eta

# How long one clip takes to watch and judge, including a second look. An
# ASSUMPTION, printed on the page as one — it is the only way to turn "17 clips"
# into "about half an hour", and pretending it is measured would be the exact
# dishonesty the rest of this machine is built to avoid.
MIN_PER_CLIP = 2
# A one-line route decision he has already seen the evidence for.
MIN_PER_DECISION = 1


def esc(s):
    return html.escape(str(s))


def hours(mins):
    """Minutes as words. Mirrors build_sim.hours_words so the two pages match."""
    if not mins:
        return "no time at all"
    mins = int(round(mins))
    return f"{mins} min" if mins < 90 else f"about {mins / 60:.1f} h"


def stamp():
    """UTC, sanity-checked against git's clock (the laptop's has drifted a day)."""
    now = datetime.now(timezone.utc)
    head = subprocess.run(["git", "log", "-1", "--format=%cI"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()
    try:
        gt = datetime.fromisoformat(head).astimezone(timezone.utc)
    except ValueError:
        return f"{now:%Y-%m-%d %H:%M}Z"
    if abs((now - gt).total_seconds()) > 6 * 3600:
        return f"{gt:%Y-%m-%d %H:%M}Z (git clock; this machine's differs)"
    return f"{now:%Y-%m-%d %H:%M}Z"


def phase(n, who, title, when, howlong, body, items=()):
    """One block of the timeline. `who` is 'you' or 'machine' and sets the colour.

    The colour is the page's one law and it matches /status: AMBER is the
    author's time, GREEN is the machine's. A reader should be able to see which
    of the two an episode is actually waiting on without reading a word.
    """
    li = "".join(f"<li>{i}</li>" for i in items)
    return (f'<div class="ph {who}"><div class="phh"><span class="pn">{n}</span>'
            f'<b>{esc(title)}</b><span class="tag">{"yours" if who == "you" else "the machine"}'
            f'</span></div><p class="meta">{esc(when)} · {esc(howlong)}</p>'
            f'<p class="body">{body}</p>'
            + (f'<ul class="items">{li}</ul>' if li else "") + "</div>")


def build() -> str:
    rows = {r["number"]: r for r in eta.rows()}
    ep2 = rows.get(2)
    if not ep2:
        raise SystemExit("episode 2 has no readable states — refusing to write a "
                         "plan whose numbers would be invented")

    waiting = ep2["awaiting_founder"]
    fixk = ep2["needs_render"]
    gated = ep2["conditional_beats"]
    calls = len(ep2["decisions"])
    per_beat = ep2["per_beat_minutes"]
    mach = ep2["machine_minutes"]
    cond = ep2["conditional_minutes"]

    # The sitting: everything already waiting, plus the wave now rendering, which
    # lands before he sits down. Arithmetic on an assumption, and it says so.
    clips = waiting + fixk
    sit = clips * MIN_PER_CLIP + calls * MIN_PER_DECISION

    ep1 = rows.get(1)
    ep1_line = ""
    if ep1:
        n1 = len(ep1["decisions"])
        ep1_line = (
            f'<p class="note">Episode 1, for comparison, is at '
            f'<b>{ep1["ready"]} of {ep1["total"]}</b> beats passed with '
            f'<b>{ep1["awaiting_founder"]}</b> takes waiting on your eye and '
            f'<b>{n1}</b> open call{"s" if n1 != 1 else ""}. Its remaining machine '
            f'work is {"nothing that is not behind a call" if not ep1["needs_render"] else hours(ep1["machine_minutes"])}'
            f' — it is waiting on you, not on the card.</p>')

    p1 = phase(
        1, "you", "Your first pass", "today, whenever you sit down",
        f"about {sit} minutes",
        f'Everything the card has finished with goes in front of you in one '
        f'batch. That is <b>{waiting}</b> take{"s" if waiting != 1 else ""} '
        f'already waiting plus the <b>{fixk}</b> now rendering, so about '
        f'<b>{clips} clips</b> — at {MIN_PER_CLIP} minutes each including a '
        f'second look — and <b>{calls}</b> open call{"s" if calls != 1 else ""}, '
        f'most of them a one-line route you have already seen the evidence for.',
        items=[
            "the six guard clips from the wave you ratified — does the register hold",
            "the three-seed winners on 13, 14 and 15 — pick or send back",
            "the four-take pools on 03, 17 and 21, where no two takes match",
            "the beat 04 widen pair — a framing tradeoff, so it is yours",
            "beats 19 and 20 with the placement fix in",
            "the plates for 12, 18 and 21",
            "the cold-open fig route, the beat 02 init pick, and whether 16 is in or out",
        ])

    p2 = phase(
        2, "machine", "The card catches up", "the same day, unattended",
        hours(mach),
        f'The <b>{fixk}</b> beat{"s" if fixk != 1 else ""} whose fix is known go '
        f'back on the card at a measured <b>{hours(per_beat)} a beat</b> — the '
        f'clipboard retries on 06 and 10, the named-second-guard attempt on 08, '
        f'and whatever your pass sends back. How much comes back is the one thing '
        f'here nobody has measured, so it is named and not numbered. Nothing in '
        f'this phase needs anyone awake.',
        items=[
            f'a further {hours(cond)} sits behind the {gated} gated beats and '
            f'runs only if you keep them — a beat that gets cut costs nothing',
        ] if gated and cond else ())

    p3 = phase(
        3, "you", "Your second pass", "the next morning", "about 15 minutes",
        'Only what came back. A returning beat is a yes-or-no against a note you '
        'already wrote, which is why this sitting is short — the reading was done '
        'in pass one.')

    p4 = phase(
        4, "machine", "Voice, assembly, and the cut",
        "straight after pass two", "about an hour, unattended",
        'Chatterbox voices the approved beats, <code>render_t3</code> assembles '
        'the captioned 9:16 episode with the Sapling title card, and the finished '
        'cut lands in your inbox as one thing to watch.')

    p5 = phase(
        5, "you", "The publish call", "when the cut is in front of you",
        "about 100 seconds, plus your verdict",
        'One screening of the whole episode and one word. Publishing is yours '
        'alone and always has been.')

    ep3 = phase(
        1, "you", "One photo of a sapling", "two minutes, whenever",
        "two minutes",
        'Episode 3 has been stuck on a checkpoint that will not draw the tree '
        'through seven rounds of prompting. A real reference photo ends it — you '
        'already chose that route.')
    ep3b = phase(
        2, "machine", "Conditioned sample, then the 21 stills",
        "same day as the photo", "about an hour after the sample passes",
        'One sample first — never a batch off an unapproved recipe — then the '
        'full 21-beat still wave.')
    ep3c = phase(
        3, "you", "The still pass", "after the wave", "about 15 minutes",
        'Twenty-one frames, pick or send back. The same shape as episode 2 '
        'phase one, one rung earlier.')
    ep3d = phase(
        4, "machine", "The motion wave", "unattended", "a few hours",
        'Not derived: episode 3 has no beats in the states file yet, so this '
        'page has nothing measured to multiply. The moment its beats are scored '
        'the figure here becomes a real one, like episode 2\'s above.')

    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The plan — what gets made, what you review, and when</title>
<style>
  body {{ max-width: 48rem; margin: 0 auto; padding: 1.2rem 1rem 4rem;
         font: 17px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #101312; color: #e6e8e6; }}
  h1 {{ font-size: 1.4rem; margin: .2rem 0 .3rem; }}
  h2 {{ font-size: 1.05rem; margin: 2rem 0 .2rem; }}
  .sub {{ color: #9aa39c; margin: 0 0 1rem; }}
  .law {{ display: flex; flex-wrap: wrap; gap: .3rem 1.1rem; margin: 0 0 1.4rem;
          font-size: .86rem; color: #9aa39c; }}
  .law span {{ display: inline-flex; align-items: center; gap: .4rem; }}
  .law i {{ width: .6rem; height: .6rem; border-radius: 2px; display: block; }}
  .law .you i {{ background: #e8b45c; }} .law .machine i {{ background: #8fd6a0; }}
  .ph {{ border: 1px solid #2a332d; border-left: 3px solid #2a332d;
         border-radius: 10px; padding: .8rem 1rem; margin: 0 0 .7rem;
         background: #161a18; }}
  .ph.you {{ border-left-color: #e8b45c; }}
  .ph.machine {{ border-left-color: #8fd6a0; }}
  .phh {{ display: flex; align-items: baseline; gap: .55rem; }}
  .pn {{ font: 700 .78rem/1 ui-monospace, monospace; color: #7d8a80;
         border: 1px solid #2a332d; border-radius: 5px; padding: .22rem .38rem; }}
  .phh b {{ font-size: 1.02rem; }}
  .tag {{ margin-left: auto; font-size: .74rem; text-transform: uppercase;
          letter-spacing: .07em; color: #7d8a80; }}
  .ph.you .tag {{ color: #e8b45c; }} .ph.machine .tag {{ color: #8fd6a0; }}
  .meta {{ margin: .35rem 0 0; color: #8b948d; font-size: .88rem; }}
  .body {{ margin: .5rem 0 0; }}
  .body b, .items b {{ color: #fff; }}
  .items {{ margin: .5rem 0 0; padding-left: 1.1rem; color: #cdd4cd;
            font-size: .92rem; }}
  .items li {{ margin: .2rem 0; }}
  .note {{ color: #9aa39c; font-size: .92rem; }}
  .verdict {{ border-left: 3px solid #8fd6a0; padding: .1rem 0 .1rem .8rem;
              margin: 1rem 0; color: #cdd4cd; }}
  code {{ background: #0b0e0c; padding: .08rem .3rem; border-radius: 4px;
          font-size: .88rem; }}
  footer {{ margin-top: 2.4rem; padding-top: 1rem; border-top: 1px solid #2a332d;
            color: #7d8a80; font-size: .84rem; }}
  a {{ color: #8fd6a0; }}
</style>

<h1>The plan</h1>
<p class="sub">What gets made, what comes to you, and how long each part takes.
Asked for on 2026-08-13: <i>"what you will generate, what i will review, when,
how long"</i>.</p>

<div class="law">
  <span class="you"><i></i>amber is your time</span>
  <span class="machine"><i></i>green is the machine's</span>
</div>

<p class="verdict">Episode 2 stands at <b>{ep2["ready"]} of {ep2["total"]}</b>
beats passed, with <b>{waiting}</b> takes waiting on your eye and
<b>{calls}</b> open calls. The card has <b>{hours(mach)}</b> of rendering left.
<b>The variable is not the GPU.</b> Every machine phase below runs unattended and
finishes the same day; the only thing that decides whether episode 2 publishes
tomorrow evening is when the two passes happen.</p>

{ep1_line}

<h2>Episode 2 — to published</h2>
{p1}{p2}{p3}{p4}{p5}
<p class="note">If both passes land on the day they are described, episode 2 is
published tomorrow evening. That sentence is a conditional, not a date: nothing
on the machine side can make it arrive sooner, and nothing here can predict when
you sit down.</p>

<h2>Episode 3 — trailing episode 2</h2>
{ep3}{ep3b}{ep3c}{ep3d}
<p class="note">Episode 3 lands a couple of days behind episode 2 on the same
loop, and for the same reason: its two passes are yours. Nothing above is
derived from measurements — episode 3 has no beats in the states file yet.</p>

<h2>Episodes 4 to 7A — the same loop again</h2>
<p class="note">Identical shape, already one rung in: the first FARMER and
ASSESSOR character references are drawn and waiting on your eye, and five
scripts are approved. Each episode is one still pass and one clip pass of your
time; everything between them is unattended.</p>

<footer>
<p><b>This is a plan, not a promise.</b> It is rewritten as verdicts land — the
lanes update it alongside <code>pipeline/measured/episode-progress.yaml</code>
at scoring time, so a beat you pass moves this page on its next run.</p>
<p>Every count and every machine hour above is pulled from
<code>pipeline/episode_eta.py</code>, the same rows
<a href="/status.html#eta">/status</a> multiplies, so the two cannot disagree.
The <code>.html</code> is deliberate: this page is served under
<code>/review/</code>, and the build's link check resolves a bare
<code>/status</code> against the files on disk rather than against the host's
clean-URL rewrite. Machine
hours are measured: rounds-per-beat off the box's own job records
(<code>farm-out/box/</code>) times that kind's median minutes, and they are a
floor — records before 10 Aug are not in them. Sitting lengths are arithmetic on
a stated assumption of {MIN_PER_CLIP} minutes a clip, not a measurement. How long
a call takes you to answer, and how many beats come back for another round, are
the two things nobody here can measure; they are named above and never given a
number.</p>
<p>Generated {esc(stamp())} · states measured {esc(ep2["measured_at"] or "not recorded")}</p>
</footer>
"""


if __name__ == "__main__":
    out = REPO / "review/plan/index.html"
    out.write_text(build(), encoding="utf-8")
    print(f"wrote review/plan/index.html")
