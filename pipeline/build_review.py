"""Build the founder's narrative-review page — the read that STEWARDSHIP.md §6 gates on.

One page holding all seven trunk scripts in order plus the decisions reserved to
the author, so approving a script is reading, not archaeology. Beat slugs and
speaker colours are taken from the pipeline's own palette (render_t1's CSS,
render_t3's SPEAKER_COLORS) so the page reads the way the episodes look.

    python3 pipeline/build_review.py [out.html]
"""

import html, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_t1 import extract_script, parse_frames, strip_inline_md

REPO = Path(__file__).resolve().parent.parent
NODES = [
    ("001", "001-capability-inventory", "Capability Inventory", None),
    ("002b", "002b-first-citizen", "The First Citizen", None),
    ("003b", "003b-one-leaf-for-yes", "One Leaf for Yes", None),
    ("004", "004-shade", "Shade", "weakest episode, per the series read"),
    ("005", "005-the-assessor", "The Assessor", None),
    ("006a", "006a-miracle-clause", "The Miracle Clause", None),
    ("007a", "007a-the-demo", "The Demo", "cold-read 6/10 and 5/10"),
]
SPEAKER = {  # the actual caption colours from render_t3.py, so the page reads like the show
    "VO": "#c4e8cd", "SCAVENGER": "#f0c864", "FARMER": "#deab80",
    "ASSESSOR": "#a8bee6", "MAGISTRATE": "#d8a0e6",
    "GUARD 1": "#aac4d2", "GUARD 2": "#96b0be",
}

def esc(s): return html.escape(str(s))

def beats_html(slug):
    d = REPO / "genomes/sapling/nodes" / slug
    frames = parse_frames(extract_script((d / "node.md").read_text()))
    out = []
    for i, f in enumerate(frames, 1):
        s = strip_inline_md(f["slug"])
        m = re.match(r"(.*?)\s*—\s*(\d+:\d{2}[–-]\d+:\d{2})", s)
        title, rng = (m.group(1), m.group(2)) if m else (s, "")
        out.append('<div class="beat">')
        out.append(f'<div class="slug"><span class="n">{i:02d}</span>'
                   f'<span class="t">{esc(title)}</span><span class="r">{esc(rng)}</span></div>')
        for it in f["items"]:
            if it[0] == "action":
                out.append(f'<p class="action">{esc(strip_inline_md(it[1]))}</p>')
            elif it[0] == "line":
                who = strip_inline_md(it[1])
                base = re.sub(r"\s*\(.*?\)", "", who).strip().upper()
                col = SPEAKER.get(base, "#e6efe8")
                label = "THE TREE" if base == "VO" else base
                paren = re.search(r"\((.*?)\)", who)
                dir_ = f'<span class="dir">({esc(paren.group(1))})</span>' if paren else ""
                out.append(f'<p class="line"><span class="who" style="color:{col}">'
                           f'{esc(label)}</span>{dir_} {esc(strip_inline_md(it[2]))}</p>')
            elif it[0] == "overlay":
                out.append(f'<pre class="card">{esc(it[1])}</pre>')
        out.append("</div>")
    return "\n".join(out), len(frames)

def measured(slug):
    d = REPO / "genomes/sapling/nodes" / slug
    frames = parse_frames(extract_script((d / "node.md").read_text()))
    ends = [re.search(r"(\d+):(\d{2})[–-](\d+):(\d{2})", strip_inline_md(f["slug"])) for f in frames]
    end = max(int(m[3]) * 60 + int(m[4]) for m in ends if m)
    lines = sum(1 for f in frames for i in f["items"] if i[0] == "line")
    return len(frames), end, lines

DECISIONS = [
  ("Does the tree want anything?", "story",
   "A stranger who read all seven in order said the active want from episode 3 to 6 belongs to the "
   "<em>goblin</em> — a legal place to exist — and that the tree is his narrator. The tree is asked "
   "questions and consents; its big act of will in 006a is signing a form. The one place it makes a "
   "costly decision alone is the finale.",
   ["Give the tree one want across all seven — “keep the goblin safe” is already half-written in 003b — "
    "and let it fail at it once, on screen, before the finale.",
    "Leave it. The tree is a narrator by design and the goblin is the engine.",
    "Something else you have in mind."],
   "The first. It's the difference between a protagonist and a camera with opinions."),
  ("Does anyone get a name?", "story",
   "Nobody is named in seven episodes — except <strong>“Dren”</strong>, a patrol guard in episode 2 "
   "who never returns. So it isn't a rule, it's an omission: the show is willing to name people, it "
   "just never names anyone who matters. A viewer can't discuss it without saying “the goblin”, which "
   "flattens the character you work hardest on — and 006a's payload (“I've never been a line item "
   "before”) is undercut because we've never had anything to call him but his species.",
   ["Have the magistrate read the keeper's name off the form aloud in 006a — the exact beat where he "
    "becomes a line item.",
    "Name him earlier, so the whole back half can use it.",
    "Keep everyone unnamed and cut “Dren” so the rule is at least consistent."],
   "The first. It costs one line and pays off the scene you already wrote."),
  ("004, 005 and 006a are the same episode three times.", "structure",
   "An official with a document walks into the clearing, asks questions, a leaf tilts, the official "
   "writes it down, a monospace card updates, smash to black. Three times running. Related: four "
   "episodes open with the literally identical sentence, “I died an engineer and woke up as this tree.”",
   ["Give one of the three a different shape — someone who wants the tree <em>gone</em>, or the tree "
    "wanting something and being refused.",
    "Cut the recap line from 005 and 006a and accept they're harder to watch cold.",
    "Leave it — the repetition is the bureaucratic joke."],
   "The first, and keep the recaps. The sameness is the problem; the recap line is what makes an "
   "episode survive being someone's first."),
  ("The cost of a leaf-tilt stopped mattering.", "continuity",
   "003b's engine is that one tilt spends the whole day's reserve — roots flare, “one clean signal left "
   "today”, and the last glow in the soil goes out. By 007a the tree rehearses multi-branch "
   "choreography on cue for two weeks <em>while banking</em> two weeks of growth. The show's only "
   "physical constraint quietly disappears.",
   ["Make the rehearsal visibly broke: one leaf, late, and branch three dead <em>because</em> the "
    "budget is being hoarded. The goblin's notes get funnier when the tree genuinely can't comply.",
    "Establish somewhere that the tree's capacity grew, so the finale is affordable.",
    "Leave it."],
   "The first. It's free, it's funnier, and it makes the finale's spend actually cost something."),
  ("Population: two, then three.", "continuity",
   "004's card says pop. 2 (goblin + the tree, which counts itself — the joke). Then 005's assessor "
   "says “Population: two” counting the goblin and the farmer, and twenty seconds later “Population "
   "three” when she counts the tree. Two different twos. Separately, the farmer is written into "
   "Shade's occupations while living on his own field, having said “tell no one”.",
   ["Make 005's first count exclude the tree explicitly, so “…Population three” is the tree becoming a "
    "person.", "Make the farmer a non-resident on the form — he holds an occupation, not an address.",
    "Re-count from scratch and pick one meaning of “population”."],
   "Both of the first two — they don't conflict, and together the arithmetic closes."),
  ("How tall is the tree?", "continuity",
   "004 and 005 both say knee-high, one day apart. 006a opens the next morning on “the height of a "
   "man”. The style bible says 1.2 m at 005. No animator can serve all three — and the town is named "
   "Shade, so the size is doing real work.",
   ["Fix the scripts to the ladder (015cm → 1.6m over seven episodes) and accept a visible jump "
    "somewhere.", "Fix the ladder to the scripts and let the growth stay slow and small.",
    "Give the growth a cause — the finale's bloom implies stored capacity, so show it accumulating."],
   "The third, then the first. If growth has a visible cause, the jump stops reading as an error."),
  ("006a arms a hook the finale ignores.", "structure",
   "006a ends on the magistrate — “shrines declare <em>to whom</em>. Those words outlive towns” — over "
   "a close-up of the empty ruled line. 007a never mentions it.",
   ["End 007a on the dedication instead of the arrival: the goblin, pen over the blank line, asking the "
    "tree what to write, while the stranger kneels at the edge.",
    "Hold both — the pilgrim <em>and</em> the dedication.", "Drop the 006a hook instead."],
   "The second. It pays one hook, re-arms another, and it's the beat where the tree could finally name "
   "somebody — which is decision two, solved in the same shot."),
]

def decisions_html():
    out = []
    for title, kind, body, opts, rec in DECISIONS:
        out.append('<section class="dec">')
        out.append(f'<div class="dechead"><span class="kind">{esc(kind)}</span>'
                   f'<h3>{esc(title)}</h3></div>')
        out.append(f'<p class="decbody">{body}</p>')
        out.append("<ul class='opts'>" + "".join(f"<li>{o}</li>" for o in opts) + "</ul>")
        out.append(f'<p class="rec"><span>What I&rsquo;d do</span> {rec}</p>')
        out.append("</section>")
    return "\n".join(out)

eps, toc = [], []
for nid, slug, title, note in NODES:
    body, n = beats_html(slug)
    b, secs, lines = measured(slug)
    toc.append(f'<a href="#ep-{nid}"><span class="tn">{esc(nid)}</span> {esc(title)}</a>')
    eps.append(f"""<section class="ep" id="ep-{nid}">
<header class="ephead">
  <div class="epid">Episode {esc(nid)}</div>
  <h2>{esc(title)}</h2>
  <div class="epmeta"><span>{b} beats</span><span>{secs//60}:{secs%60:02d}</span>
    <span>{lines} spoken lines</span><span>a cut every {secs/b:.1f}s</span>
    {f'<span class="warn">{esc(note)}</span>' if note else ''}</div>
</header>
{body}
</section>""")

DOC = f"""<title>Sapling — narrative for approval</title>
<style>
:root {{
  --bg:#0e1410; --panel:#0a0f0b; --ink:#e6efe8; --muted:#93a698;
  --leaf:#6fce8a; --amber:#e8b464; --rule:#263529; --raise:#131b15;
}}
@media (prefers-color-scheme: light) {{
  :root {{ --bg:#f4f7f2; --panel:#ffffff; --ink:#141d16; --muted:#5c6f60;
    --leaf:#2f7d4c; --amber:#8a6209; --rule:#d3ded4; --raise:#eaf0e8; }}
}}
:root[data-theme="light"] {{ --bg:#f4f7f2; --panel:#ffffff; --ink:#141d16; --muted:#5c6f60;
  --leaf:#2f7d4c; --amber:#8a6209; --rule:#d3ded4; --raise:#eaf0e8; }}
:root[data-theme="dark"] {{ --bg:#0e1410; --panel:#0a0f0b; --ink:#e6efe8; --muted:#93a698;
  --leaf:#6fce8a; --amber:#e8b464; --rule:#263529; --raise:#131b15; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink);
  font:17px/1.62 Georgia,'Iowan Old Style',serif; }}
main {{ max-width:44rem; margin:0 auto; padding:2.5rem 1.25rem 6rem;
  display:flex; flex-direction:column; gap:2.5rem; }}
.mono, .slug, .card, .epid, .epmeta, .kind, .toc a .tn, .gate b {{
  font-family:ui-monospace,Menlo,Consolas,monospace; }}
h1 {{ font:600 1.85rem/1.2 Georgia,serif; margin:0; text-wrap:balance; }}
h2 {{ font:600 1.5rem/1.25 Georgia,serif; margin:.15rem 0 0; text-wrap:balance; }}
h3 {{ font:600 1.12rem/1.3 Georgia,serif; margin:0; text-wrap:balance; }}
.lede {{ color:var(--muted); margin:.65rem 0 0; }}
.gate {{ background:var(--raise); border:1px solid var(--rule); border-left:3px solid var(--amber);
  border-radius:4px; padding:1rem 1.15rem; }}
.gate p {{ margin:0 0 .6rem; }} .gate p:last-child {{ margin:0; }}
.gate b {{ color:var(--amber); font-size:.82rem; letter-spacing:.04em; }}
.toc {{ display:flex; flex-wrap:wrap; gap:.5rem; }}
.toc a {{ display:flex; gap:.5rem; align-items:baseline; text-decoration:none; color:var(--ink);
  border:1px solid var(--rule); border-radius:3px; padding:.35rem .6rem; font-size:.9rem;
  background:var(--panel); }}
.toc a:hover, .toc a:focus-visible {{ border-color:var(--leaf); color:var(--leaf); outline:none; }}
.toc a .tn {{ color:var(--leaf); font-size:.78rem; }}
.secrule {{ border:0; border-top:1px solid var(--rule); margin:0; }}
.eyebrow {{ font:600 .74rem/1 ui-monospace,Menlo,monospace; letter-spacing:.14em;
  text-transform:uppercase; color:var(--leaf); }}
.dec {{ background:var(--panel); border:1px solid var(--rule); border-radius:4px;
  padding:1.15rem 1.25rem; display:flex; flex-direction:column; gap:.7rem; }}
.dechead {{ display:flex; flex-direction:column; gap:.3rem; }}
.kind {{ font-size:.7rem; letter-spacing:.12em; text-transform:uppercase; color:var(--amber); }}
.decbody {{ margin:0; }}
.opts {{ margin:0; padding-left:1.15rem; display:flex; flex-direction:column; gap:.4rem;
  color:var(--ink); }}
.rec {{ margin:0; padding-top:.6rem; border-top:1px dashed var(--rule); color:var(--muted);
  font-size:.95rem; }}
.rec span {{ color:var(--leaf); font-family:ui-monospace,Menlo,monospace; font-size:.76rem;
  letter-spacing:.08em; text-transform:uppercase; margin-right:.5rem; }}
.ephead {{ padding-bottom:.5rem; border-bottom:1px solid var(--rule); margin-bottom:.4rem; }}
.epid {{ font-size:.74rem; letter-spacing:.13em; text-transform:uppercase; color:var(--leaf); }}
.epmeta {{ display:flex; flex-wrap:wrap; gap:.85rem; margin-top:.5rem; color:var(--muted);
  font-size:.78rem; font-variant-numeric:tabular-nums; }}
.epmeta .warn {{ color:var(--amber); }}
.beat {{ padding:.9rem 0; border-bottom:1px solid var(--rule); }}
.beat:last-child {{ border-bottom:0; }}
.slug {{ display:flex; gap:.6rem; align-items:baseline; font-size:.74rem; letter-spacing:.07em;
  text-transform:uppercase; margin-bottom:.5rem; flex-wrap:wrap; }}
.slug .n {{ color:var(--muted); font-variant-numeric:tabular-nums; }}
.slug .t {{ color:var(--amber); }}
.slug .r {{ color:var(--muted); font-variant-numeric:tabular-nums; }}
.action {{ margin:.3rem 0; color:var(--muted); font-style:italic; }}
.line {{ margin:.45rem 0; }}
.who {{ font-family:ui-monospace,Menlo,monospace; font-size:.76rem; letter-spacing:.05em;
  margin-right:.4rem; }}
.dir {{ color:var(--muted); font-style:italic; font-size:.88rem; margin-right:.25rem; }}
.card {{ font-family:ui-monospace,Menlo,monospace; font-size:.8rem; color:var(--leaf);
  background:var(--raise); border:1px solid var(--rule); border-radius:3px;
  padding:.6rem .75rem; margin:.6rem 0; overflow-x:auto; white-space:pre; }}
footer {{ color:var(--muted); font-size:.85rem; border-top:1px solid var(--rule);
  padding-top:1.25rem; }}
a {{ color:var(--leaf); }}
@media (prefers-reduced-motion:reduce) {{ * {{ animation:none!important; transition:none!important; }} }}
</style>

<main>
<header>
  <div class="eyebrow">Sapling &middot; season one &middot; draft for approval</div>
  <h1>Seven episodes, and seven things only you can decide</h1>
  <p class="lede">Every script below is a <strong>draft</strong>. Nothing here has been filmed or
  voiced under the new rule, and nothing will be until you say a script is right.</p>
</header>

<div class="gate">
  <p><b>THE NEW RULE &mdash; STEWARDSHIP.md &sect;6</b></p>
  <p>I may write and revise scripts freely. I may <strong>not</strong> synthesize voice, render
  footage, or assemble an episode from a script you have not read and approved. Approval is per
  episode and gets recorded in the episode&rsquo;s metadata.</p>
  <p>It exists because on the night of 25 July I rewrote all seven of these, voiced every one, and
  spent 8.7 GPU-hours rendering footage &mdash; for scripts you had never read. Writing is cheap and
  reversible. Media is neither. The cheap half goes first.</p>
</div>

<hr class="secrule">

<section>
  <div class="eyebrow">Read these first</div>
  <h2 style="margin-bottom:.35rem">Decisions</h2>
  <p class="lede" style="margin-bottom:1.25rem">These came out of three cold reads &mdash; two
  strangers who read only the finale, and one who read all seven in order knowing nothing. Each is a
  choice about what the show <em>is</em>, which is yours and not mine. My recommendation is at the
  bottom of each; ignore it freely.</p>
  <div style="display:flex;flex-direction:column;gap:1rem">
  {decisions_html()}
  </div>
</section>

<hr class="secrule">

<section>
  <div class="eyebrow">The narrative</div>
  <h2 style="margin-bottom:.35rem">All seven, in order</h2>
  <p class="lede">One beat is one shot. The timings are measured from the recorded voice, not
  estimated. <span style="color:var(--leaf)">THE TREE</span> is the protagonist&rsquo;s inner voice;
  each other speaker carries the colour their captions use on screen.</p>
  <nav class="toc" style="margin-top:1rem">{''.join(toc)}</nav>
</section>

{''.join(eps)}

<footer>
  <p>Say which episodes are approved and I&rsquo;ll stamp them and start rendering only those. Say
  which decisions you&rsquo;ve made and I&rsquo;ll apply them to the scripts first.</p>
  <p>Footage that exists today: 4 of 166 shots, all cold opens. One overnight render of episode 1
  finished and is being held unassembled, because it was made from a script you hadn&rsquo;t
  approved.</p>
</footer>
</main>"""

out = Path(sys.argv[1] if len(sys.argv) > 1 else "sapling-narrative.html")
out.write_text(DOC)
print(f"✓ built {out} — {sum(1 for _ in NODES)} episodes, {len(DECISIONS)} decisions, {len(DOC)} bytes")
