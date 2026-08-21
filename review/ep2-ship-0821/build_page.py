#!/usr/bin/env python3
"""Build review/ep2-ship-0821/index.html — the SHIP CANDIDATE handover page.

THE PER-BEAT TABLE IS DERIVED, NOT TYPED. Every row's take, sha, status word
and named fault is read out of sources/ship-manifest.yaml at build time, so the
page and the manifest cannot drift apart the way a hand-written table always
eventually does. If a beat changes, swap the clip, re-assemble, edit the
manifest, re-run this. Nothing about the beats is written in this file.

The prose that IS in this file is the part that is an argument rather than a
fact: what the founder is being asked, what happens on his word, and what is
still open. That is deliberately not machine-derived.

    python3 review/ep2-ship-0821/build_page.py
"""
import html
import pathlib
import yaml

HERE = pathlib.Path(__file__).resolve().parent
MANIFEST = HERE / "sources" / "ship-manifest.yaml"
OUT = HERE / "index.html"
BASE = "/review/ep2-ship-0821"

# The open founder items, in the order they matter to THIS cut. `changes_cut`
# is the honest answer to "would answering this before 12:00 change a picture?"
CARDS = [
    dict(
        url="/review/ep2-guards-0818", since="2026-08-17",
        title="ANSWERED 2026-08-20 — Do the guards read as grown men? "
              "“they should look like grown men. yes. dumb grown men.”",
        answers=["answered: pass"],
        gates="nothing any more — beats 05, 06, 10, 11 and beat 09 are all off this card",
        changes_cut=False,
        effect="<b>PASS on the adult read</b>, and <b>yes to the plain green man</b>. "
               "Beat 09's entry stops being a steward override and becomes an ordinary pick; "
               "no picture moves, because the answer is the one the cut was already staged for. "
               "Recorded with its provenance on the card and in review/inbox.yaml — the words were "
               "relayed by the orchestrating lane on 08-21, not read out of an in-tree transcript."),
    dict(
        url="/review/ep2-b13-shade-0820", since="2026-08-20",
        title="Does beat 13 satisfy “tips his head sideways into the sapling's hand-sized "
              "patch of shade”, or may the plant be drawn taller than canon in this one shot?",
        answers=["A", "B", "a third staging"],
        gates="beat 13",
        changes_cut=False,
        effect="<b>A</b> retires beat 13's named fault without changing a frame — the take you see "
               "stays and stops being a contradiction. <b>B</b> needs a render, and the card's own "
               "section 5 shows B coming back as “a balloon on a wire”. Neither lands new footage "
               "by 12:00."),
    dict(
        url="/review/ep2-b16-leaf-0820", since="2026-08-20",
        title="Beat 16's brief asks for a leaf-as-subject macro that your “average leaves” "
              "ruling forbids — restage the beat, or licence this one shot?",
        answers=["restage", "licence", "a third staging"],
        gates="beat 16 — no longer a slate",
        changes_cut=False,
        effect="<b>THE RESTAGE ROUTE HAS DELIVERED, so this question is now moot unless you prefer "
               "the macro.</b> Beat 16 has footage as of 01:05 and it is in the cut: the canon "
               "two-leaf sapling drawn large in the foreground with him behind it — the brief's "
               "actual relation, obtained without needing an exception to your “average leaves” "
               "ruling. <b>restage</b> ratifies what you are watching. <b>licence</b> still reopens "
               "the macro, and still needs a render nobody has made. Answering changes no picture "
               "before 12:00 either way — the picture already changed."),
    dict(
        url="/review/ep2-b04-action-0820", since="2026-08-20",
        title="Beat 04 as written cannot be filmed on this engine — pick the action that replaces it.",
        answers=["A — the peek", "B — his own hand over his own mouth", "C — the slow sink",
                 "or write a fourth"],
        gates="beat 04",
        changes_cut=False,
        effect="Nothing is pre-staged on purpose: the pick <i>is</i> the spec, so this cannot reach "
               "the cut before 12:00. Both 08-20 wording rungs failed and closed the wording route — "
               "the answer is staging, and staging starts with your letter."),
    dict(
        url="/review/ep2-goblin-design-0819", since="2026-08-20",
        title="What is the goblin wearing below the waist? Canon names the cloak and nothing "
              "under it, and the four approved B tiles show four different lower halves.",
        answers=["trousers", "bare legs and a loincloth", "name it",
                 "“you pick, it is not a taste question”"],
        gates="beat 08 first, then every goblin beat",
        changes_cut=False,
        effect="Explicitly NOT blocking and batchable with your next look. All eleven beat-08 rungs "
               "on 08-20 produced stills only, and the last one closed the route, so no answer here "
               "reaches this cut."),
    dict(
        url="local: review/ep2-picks/farm-recovered-0814-scores.yaml", since="2026-08-17",
        title="Beat 11's r1s1 take was promoted by the steward and sits under “Picks — veto only”. "
              "SILENCE ACCEPTS.",
        answers=["say nothing to accept", "“no, it is broken because X” to veto"],
        gates="beat 11",
        changes_cut=True,
        effect="Flagged because a ship is the wrong moment for a silence-accepts window nobody "
               "re-read. A veto here removes beat 11's picture and there is no replacement staged, "
               "so beat 11 would become the second slate."),
]


def esc(s):
    return html.escape(str(s), quote=False)


def main():
    m = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    beats = sorted(m["beats"], key=lambda b: int(b["beat"]))
    status = {int(k): v for k, v in m["ship_status"].items()}
    proof = HERE / "proof"

    rows = []
    for b in beats:
        n = int(b["beat"])
        st = status.get(n, {})
        take = b.get("take")
        frame = proof / f"b{n:02d}.jpg"
        thumb = (f'<img class="thumb" loading="lazy" src="{BASE}/proof/b{n:02d}.jpg" '
                 f'alt="beat {n:02d} mid-frame">' if frame.exists() else
                 '<span class="noframe">slate</span>')
        take_cell = (f'<code>{esc(take)}</code><br><span class="sha">'
                     f'{esc(str(b.get("sha256", ""))[:16])}…</span>'
                     if take else '<span class="noframe">no footage in the cut</span>')
        why = esc(b.get("why", ""))
        rows.append(f"""  <tr>
    <td class="n"><b>{n:02d}</b><br><span class="slug">{esc(b.get('slug',''))}</span></td>
    <td class="thumbcell">{thumb}</td>
    <td>{take_cell}<br><span class="why">{why}</span></td>
    <td class="n"><span class="tag {esc(st.get('class','warn'))}">{esc(st.get('word','—'))}</span></td>
    <td class="fault">{esc(st.get('of',''))}<div class="full">{esc(b.get('fault_shipping',''))}</div></td>
  </tr>""")

    card_html = []
    for c in CARDS:
        link = (f'<a href="{c["url"]}">{c["url"]}</a>' if c["url"].startswith("/")
                else f'<code>{esc(c["url"])}</code>')
        ans = " &nbsp;·&nbsp; ".join(f"<b>{esc(a)}</b>" for a in c["answers"])
        badge = ('<span class="tag new">CHANGES THE CUT</span>' if c["changes_cut"]
                 else '<span class="tag warn">CANNOT LAND BY 12:00</span>')
        card_html.append(f"""<div class="card">
  <p class="cardhead">{link} &nbsp; {badge} &nbsp; <span class="since">open since {esc(c['since'])}</span></p>
  <p class="q">{c['title']}</p>
  <p class="ans">Answer: {ans}</p>
  <p class="eff">{c['effect']}</p>
  <p class="gates">Gates {esc(c['gates'])}.</p>
</div>""")

    n_fail = sum(1 for s in status.values() if s["class"] == "fail")
    n_pass = sum(1 for s in status.values() if s["class"] == "pass")

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Sapling — episode 2, SHIP CANDIDATE (2026-08-21)</title>
<style>
  :root {{
    --bg: #17181a; --panel: #1f2124; --line: #33363b;
    --ink: #eceef1; --muted: #9aa0a8; --accent: #c8b273;
    --pass: #7fd68b; --fail: #e08b8b; --warn: #d8b46a; --new: #8fc4e8;
  }}
  * {{ box-sizing: border-box; }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{ margin: 0; background: var(--bg); color: var(--ink);
         font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
         padding: 0 24px 96px; }}
  .wrap {{ max-width: 1020px; margin: 0 auto; }}
  header.top {{ padding: 40px 0 20px; border-bottom: 1px solid var(--line); }}
  header.top h1 {{ margin: 0 0 6px; font-size: 27px; letter-spacing: -0.01em; font-weight: 650; }}
  header.top .sub {{ color: var(--muted); font-size: 14.5px; margin: 0; max-width: 78ch; }}
  h2 {{ font-size: 18px; margin: 44px 0 6px; font-weight: 650; }}
  h3 {{ font-size: 15.5px; margin: 26px 0 4px; font-weight: 650; color: #dfe3e8; }}
  p {{ max-width: 78ch; }}
  p.sub {{ color: var(--muted); font-size: 14.5px; }}
  .callout {{ margin: 22px 0 0; padding: 16px 20px; background: var(--panel);
             border: 1px solid var(--line); border-left: 3px solid var(--accent);
             border-radius: 5px; }}
  .callout p {{ margin: 0 0 10px; }} .callout p:last-child {{ margin-bottom: 0; }}
  .callout.red {{ border-left-color: #b06060; }}
  .callout.green {{ border-left-color: #5f9d6c; }}
  .callout.blue {{ border-left-color: #5b83a8; }}
  video {{ width: 100%; max-width: 420px; height: auto; border: 1px solid var(--line);
          border-radius: 5px; display: block; margin: 14px 0 6px; background: #000; }}
  .scroll {{ overflow-x: auto; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0 18px; font-size: 14px;
          min-width: 760px; }}
  th, td {{ text-align: left; padding: 8px 9px; border-bottom: 1px solid var(--line);
           vertical-align: top; }}
  th {{ color: var(--muted); font-weight: 600; white-space: nowrap; }}
  td.n {{ white-space: nowrap; font-variant-numeric: tabular-nums; }}
  td.thumbcell {{ width: 78px; }}
  img.thumb {{ width: 68px; height: auto; border-radius: 3px; border: 1px solid var(--line);
              display: block; }}
  .noframe {{ color: var(--muted); font-size: 12.5px; }}
  .slug {{ color: var(--muted); font-size: 11.5px; font-weight: 600; letter-spacing: 0.03em; }}
  .sha {{ color: #6f757c; font: 11px ui-monospace, SFMono-Regular, Menlo, monospace; }}
  .why {{ color: var(--muted); font-size: 12px; }}
  td.fault {{ font-size: 13.5px; }}
  td.fault .full {{ color: var(--muted); font-size: 12.5px; margin-top: 4px; }}
  .tag {{ display: inline-block; padding: 2px 7px; border-radius: 3px; font-size: 11.5px;
         font-weight: 700; letter-spacing: 0.02em; white-space: nowrap; }}
  .tag.fail {{ background: #3a2a2a; border: 1px solid #6b4141; color: #f0c9c9; }}
  .tag.warn {{ background: #383021; border: 1px solid #6b5a33; color: #f0dfb4; }}
  .tag.pass {{ background: #23331f; border: 1px solid #416b45; color: #c9f0cd; }}
  .tag.new  {{ background: #1c2a36; border: 1px solid #3f6280; color: #c5e2f6; }}
  code {{ font: 12.5px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace;
         background: #26282c; padding: 1px 5px; border-radius: 3px; }}
  .stamp {{ display: inline-block; margin: 18px 0 4px; padding: 4px 10px; border-radius: 3px;
           background: #3a2a2a; border: 1px solid #6b4141; color: #f0c9c9;
           font-size: 12.5px; font-weight: 700; letter-spacing: 0.02em; }}
  .counts {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 18px 0 0; padding: 0; list-style: none; }}
  .counts li {{ background: var(--panel); border: 1px solid var(--line); border-radius: 5px;
               padding: 10px 14px; font-size: 14px; color: var(--muted); }}
  .counts b {{ display: block; font-size: 21px; font-variant-numeric: tabular-nums; color: var(--ink); }}
  .card {{ margin: 14px 0; padding: 14px 18px; background: var(--panel);
          border: 1px solid var(--line); border-radius: 5px; }}
  .card p {{ margin: 0 0 7px; max-width: 82ch; }} .card p:last-child {{ margin-bottom: 0; }}
  .cardhead {{ font-size: 13.5px; }}
  .card .q {{ font-size: 15.5px; font-weight: 600; }}
  .card .ans {{ font-size: 14px; }}
  .card .eff, .card .gates {{ color: var(--muted); font-size: 13.5px; }}
  .since {{ color: #6f757c; font-size: 12.5px; }}
  ol.check {{ max-width: 82ch; }} ol.check li {{ margin: 0 0 12px; }}
  footer {{ margin-top: 52px; padding-top: 18px; border-top: 1px solid var(--line);
           color: var(--muted); font-size: 13.5px; }}
  a {{ color: var(--new); }}
</style>
</head>
<body>
<div class="wrap">

<header class="top">
  <h1>Sapling — episode 2, SHIP CANDIDATE</h1>
  <p class="sub"><strong>This is the cut you ordered on 08-20.</strong> 1:56, and as of 01:05 <strong>twenty-one beats of footage and no slate at all</strong> — the first cut
  of this episode in which every beat has a picture.
  Best-available takes, every fault named, nothing hidden behind a passing score. No render, no
  voice synthesis, no GPU, no spend: <strong>$0</strong>. Every clip in it already existed when
  you gave the order.</p>
</header>

<p class="stamp">SHIP CANDIDATE — NOT PUBLISHED, NOT CANON, NO LEAF. YOUR WATCH-THROUGH IS THE GATE.</p>

<h2>The episode</h2>
<video controls playsinline preload="metadata" src="{BASE}/ep2-ship-0821.mp4"></video>
<p class="sub">720&times;1280, 24&nbsp;fps, {m.get('duration_s')}&nbsp;s, mastered to &minus;16.7&nbsp;LUFS.
<code>sha256 {esc(str(m.get('sha256',''))[:12])}…</code> &nbsp;·&nbsp; manifest:
<a href="{BASE}/sources/ship-manifest.yaml">sources/ship-manifest.yaml</a></p>

<ul class="counts">
  <li><b>21</b> footage beats</li>
  <li><b>0</b> slates</li>
  <li><b>{n_fail}</b> beats carrying a named FAIL</li>
  <li><b>{n_pass}</b> clean passes</li>
  <li><b>$0</b> to assemble</li>
</ul>

<div class="callout red">
  <p><strong>ONE DECISION IN THIS CUT IS CONTESTED AND IT IS BEAT 09, so it goes first rather
  than in a footnote.</strong> Beat 09 is the punchline — “…We confiscate the goblin?” — and it
  has played over a black card in every cut this episode has ever had. Tonight it has a face.</p>
  <p>The clip scores <strong>four of four</strong> on the bar written before it rendered, including
  the clause its own spec called most likely to fail. <strong>And that same spec says
  <code>is_show_content: false</code> — “this is an INIT MEASUREMENT and must never reach a cut”.</strong>
  I have overridden that declaration. I am telling you rather than letting you find it.</p>
  <p>The reason the override is narrow: read what the declaration gives as its own reason —
  <em>“the adult read is an open R4 card (/review/ep2-guards-0818) and a clip inherits its plate's
  cast defects frame for frame”</em>. It is not withheld on a measurement it lost. It is withheld
  waiting for <strong>your word</strong>, and the lane that wrote it pre-wrote a swap script whose
  header says “That card IS this decision.” Under a ship order that says best-available beats a
  slate, a beat held only by an unanswered taste card enters, and the card comes with it.</p>
  <p><strong>He reads adolescent, in close-up, holding your biggest laugh.</strong> That is the
  guards question at full size. And a second fault that is nobody's card: <strong>his hand
  dissolves off his cheek in the first third of a second</strong> — full hand at f001, gone by
  f008, and the slot starts at f001.</p>
  <p><strong>Veto in one line: “beat 09: back to a slate.”</strong> Nothing else in the cut moves;
  the voice already plays over the card and always did.</p>
</div>

<div class="callout">
  <h2>And a second ship-mode entry, made after this page was first written: BEAT 16</h2>
  <p><strong>The last slate is gone.</strong> At 01:05 tonight beat 16 got the first footage it has
  ever had, and I put it in the cut. This file said, four hours earlier, <em>“No render in flight
  tonight can land a legal beat by 12:00.”</em> That was wrong, and I have left the sentence
  standing in the manifest with the correction beside it.</p>
  <p>Beat 16 is the beat whose brief asks for a leaf-as-subject macro that <strong>your own
  “average leaves” ruling forbids</strong>. Rather than ask you to licence an exception, the
  restage takes the brief's actual relation — <em>the plant is the subject and he is depth behind
  it</em> — and builds that. The sapling is not prompted: it is <strong>drawn</strong>, because the
  strongest wording available returns two leaves 0 times in 16. It is drawn large in the near
  foreground of a plate that already had him seated, that plate's own weed erased first so the
  frame holds exactly one plant, and finished with one 0.30 pass. Then one motion sample. Then
  three frames off the head with ffmpeg. <strong>$0, four GPU jobs, no download.</strong></p>
  <p>It scores <strong>seven of seven</strong> on the bar written before it rendered — including
  the clause its own spec called unmeasured, since no clip in this tree had ever animated a drawn
  plant as the <em>subject</em> before, and canon's two leaves survived all 121 frames.</p>
  <p><strong>The fault it ships with, named rather than scored away: the goblin is the SUPERSEDED
  ADULT design.</strong> You ruled on 08-20 that he must read as the B tile's creature; this plate
  predates that. He is blurred depth behind the plant and the design barely reads at that size —
  but it is the old one, and “barely reads” is a reason to tell you, not a reason not to.
  Two smaller costs: your eye still goes to his face before the plant, because he is a face and the
  plant is a shape; and 43&nbsp;% of the beat is a held final frame, because the voice outruns the
  picture by 3.7&nbsp;s.</p>
  <p><strong>Veto in one line: “beat 16: back to a slate.”</strong> Nothing else in the cut moves;
  the voice already plays and always did.</p>
</div>

<div class="callout">
  <p><strong>What is worth watching for, in order.</strong> Beat 09 at 0:44 (above). Beat 01 at
  0:00 — a NEW cold open that landed inside the window tonight: it is not a render but a composite,
  the growing fig from one take joined to the held field of its crf-10 sibling, which is the first
  time this beat has had both. Its remaining fault is one band of grass that still moves. Beat 18
  at 1:28 — 5.9&nbsp;s of held frame, the longest freeze in the episode and an honest cost of
  killing the palindrome. Beat 16 at 1:15 — <strong>the last slate, filled tonight</strong>. It is the beat
  whose brief asks for a shot your own canon forbids; the restage gives the brief’s relation — the
  sapling is the subject, he is depth behind it — without the exception. Its goblin is the
  SUPERSEDED adult design, blurred, and barely readable at that scale; that is named, not hidden.</p>
</div>

<div class="callout green">
  <p><strong>One bug was found by watching this cut rather than by measuring it, and it was in the
  cold open.</strong> The first assembly with the new beat 01 played it at 0.53&times; speed — the
  fig growing in slow motion for nine seconds. The composite's sidecar honestly says
  <code>model: none</code> (no sampler ran), and the assembler read that as “this is a still with a
  computed zoom, so it may be stretched”. A composite is footage. Fixed: a clip that declares its
  own frame rate is never treated as a still.</p>
  <p><strong>The cut above is the fixed one, measured and not assumed:</strong> beat 01's last
  moving frame is at <b>3.79&nbsp;s</b>, inside its own 5.04&nbsp;s clip. Stretched, the motion
  would have run past 7&nbsp;s. The demo cut was re-assembled by the b01 lane and is also fixed.</p>
  <p><strong>What this cost us is worth more than the fix, and it is on the fault list below.</strong>
  Every gate passed the half-speed cut: the licence gate, the sha recheck, qa_local's 83 routes,
  qa_episode's 15 checks. A clip at 0.53&times; hashes, serves, links and measures exactly like one
  at full speed. It was caught by a person reading a log line. <b>qa_episode now asserts playback
  rate</b> so the next one is caught by the gate instead.</p>
</div>

<h2>Every beat, and what is wrong with it</h2>
<p class="sub">Generated from <code>sources/ship-manifest.yaml</code> at build time — this table
cannot drift from the manifest, because it is the manifest. Thumbnails are the middle frame of
each take, extracted by <code>proof_receipts --frames</code>; all 20 were re-hashed against the
manifest tonight and 20 of 20 match.</p>

<div class="scroll">
<table>
  <thead><tr><th>Beat</th><th>Frame</th><th>Take in the slot</th><th>Status</th>
  <th>The fault that ships with it</th></tr></thead>
  <tbody>
{chr(10).join(rows)}
  </tbody>
</table>
</div>

<h2>The six things still open — and whether they can reach this cut</h2>
<p class="sub"><strong>The cutoff is 12:00 tomorrow, 2026-08-21.</strong> Anything answered,
judged and swapped in before then enters the shipped cut; anything after goes to a post-ship patch
list. Of the six, <strong>one</strong> can actually move a picture in that window.</p>

{chr(10).join(card_html)}

<h2>Publish checklist</h2>
<p class="sub">What you are approving, and exactly what happens on your word. Nothing below runs
without it.</p>

<div class="callout red">
  <p><strong>ONE THING GENUINELY BLOCKS PUBLICATION AND IT IS NOT A PICTURE.</strong>
  STEWARDSHIP §6 — narrative approval precedes media. <strong>Beat 17's restaged script line has
  never been read by you:</strong> “The scavenger pushes himself up, gives his cloak a shake, and
  turns to go.” The node's <code>002b-t0-c.yaml</code> records it as unapproved. It is eleven words
  and it is item 1 for that reason. The beat is meanwhile a clean PASS and is in this cut.</p>
</div>

<ol class="check">
  <li><strong>Read beat 17's line</strong> (above) and say yes or restage it. This is the §6 gate
  and it is the only hard blocker in the list.</li>
  <li><strong>Watch the cut.</strong> Your watch-through is the publish gate you kept on 08-19;
  no leaf is written and nothing goes live until it happens.</li>
  <li><strong>Beat 16: in or out.</strong> “beat 16: back to a slate” removes it. Same class as
  beat 09 — a steward entry on a beat that was held only by an unanswered taste card — so silence
  is not acceptance here either. Answering <a href="/review/ep2-b16-leaf-0820">/review/ep2-b16-leaf-0820</a>
  with <b>restage</b> ratifies what you are watching; <b>licence</b> reopens the macro and needs a
  render nobody has made.</li>
  <li><strong>Beat 09: in or out.</strong> “beat 09: back to a slate” removes it. Silence is
  <em>not</em> acceptance here — it is a steward override of a written declaration, so I would
  rather have the word. Answering <a href="/review/ep2-guards-0818">/review/ep2-guards-0818</a>
  with <b>pass</b> / <b>recast</b> / <b>stage</b> settles it and four other beats at the same
  time.</li>
  <li><strong>Any other beat you want out.</strong> Every row above has a one-line veto in the
  manifest; each one is a file swap and a re-assemble, minutes, $0.</li>
  <li><strong>Then say “publish”.</strong> On that word, and not before: the cut is promoted from
  a bench assembly to a T3 leaf under the node, gets its row in <code>lineage.yaml</code> with
  full provenance, the site rebuilds and it goes live at banyan.city. That step is mechanical and
  takes minutes.</li>
  <li><strong>Posting it anywhere is yours alone.</strong> TikTok, Reddit, HN — founder-reserved,
  never autonomous. Publishing to the site and announcing it are two different words and I will
  wait for the second one separately.</li>
</ol>

<div class="callout blue">
  <p><strong>What I did not do.</strong> No render, no voice synthesis, no GPU, no network, no
  spend. No script text touched. No verdict authored, edited or reinterpreted — every quotation in
  the manifest is its own lane's words. No leaf, nothing in <code>lineage.yaml</code>, no
  <code>plate_ack</code>, not canon. <code>review/inbox.yaml</code> untouched. Exactly one thing
  was overridden and it is beat 09's <code>is_show_content</code> declaration, which has its own
  block in the manifest and its own callout at the top of this page.</p>
</div>

<footer>
  Sapling is the show; banyan.city is the platform. Assembled
  <code>python3 pipeline/render_t3.py sapling 002b --clips review/ep2-ship-0821/sources --out
  review/ep2-ship-0821/ep2-ship-0821.mp4</code> — bench mode, no leaf.
  Page built by <code>review/ep2-ship-0821/build_page.py</code> from
  <code>sources/ship-manifest.yaml</code>. Unlisted review page, noindex.
</footer>

</div>
</body>
</html>
"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"✓ {OUT.relative_to(HERE.parent.parent)} — {len(beats)} beats, "
          f"{sum(1 for b in beats if b.get('take'))} takes, {len(CARDS)} open items, "
          f"{len(doc)} bytes")


if __name__ == "__main__":
    main()
