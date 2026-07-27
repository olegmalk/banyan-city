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
"""

import argparse
import base64
import html
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from generate_shots import parse_shots  # noqa: E402
from sd_prompt import compress, extra_negatives, suppressed_negatives  # noqa: E402

# What the Kaggle notebook actually sends — keep in sync with render-kaggle.ipynb.
NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, low quality, "
       "blurry, extra limbs, deformed, jpeg artifacts, realistic skin texture")
STILL_MODEL = "cagliostrolab/animagine-xl-3.1"
STILL = {"width": 832, "height": 1216, "steps": 40, "cfg": 7.0, "seed_base": 20260719}
MOTION = {"engine": "LTX-Video (Lightricks/LTX-Video) under evaluation; "
                    "prior takes: Stable Video Diffusion",
          "size": "512x768", "note": "commercial platforms welcome — Kling, Veo, "
          "Pika, Runway: use the SAME still + prompt, submit with provenance"}


def beat_neg(prompt: str) -> str:
    neg = NEG
    for term in suppressed_negatives(prompt):
        neg = neg.replace(term + ", ", "")
    extra = extra_negatives(prompt)
    return f"{neg}, {extra}" if extra else neg


def img_tag(p: Path, w: int = 240) -> str:
    if not p.exists():
        return '<div class="noimg">no approved still yet — still in review</div>'
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f'<img width="{w}" src="data:image/png;base64,{b64}" alt="{p.name}">'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("genome")
    ap.add_argument("node")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    nodes = REPO / "genomes" / a.genome / "nodes"
    d = next(x for x in sorted(nodes.iterdir())
             if x.is_dir() and x.name.startswith(a.node))
    shots = parse_shots((d / "shots.md").read_text())
    stills_dir = d / "stills"

    rows = []
    for s in shots:
        pos, _ = compress(s["prompt"])
        neg = beat_neg(s["prompt"])
        still = stills_dir / f"{s['num']:02d}-{s['slug']}.png"
        approved = still.exists()
        rows.append(f"""
<section class="beat" id="beat-{s['num']:02d}">
  <h2>Beat {s['num']:02d} — {html.escape(s['slug'].replace('-', ' ').upper())}
      <span class="tag {'ok' if approved else 'wip'}">{'STILL APPROVED' if approved else 'STILL IN REVIEW'}</span></h2>
  <div class="cols">
    <div class="col">{img_tag(still)}</div>
    <div class="col recipe">
      <h3>Recipe — reproduce or beat it</h3>
      <p><b>Still model:</b> {STILL_MODEL}<br>
         <b>Size:</b> {STILL['width']}×{STILL['height']} ·
         <b>Steps:</b> {STILL['steps']} · <b>CFG:</b> {STILL['cfg']} ·
         <b>Seed:</b> {STILL['seed_base']} + {s['num']}</p>
      <p><b>Prompt (as sent):</b></p>
      <pre>{html.escape(pos)}</pre>
      <p><b>Negative prompt:</b></p>
      <pre>{html.escape(neg)}</pre>
      <p><b>Motion:</b> {html.escape(MOTION['engine'])} at {MOTION['size']}.<br>
         {html.escape(MOTION['note'])}</p>
    </div>
  </div>
  <details><summary>Fork this beat</summary>
    <ol>
      <li><b>Better take, same recipe:</b> generate with the still + prompts above
          on your platform and credits, then submit the clip
          (<code>pipeline/t3-trials/intake.py</code> normalizes; provenance required:
          platform, model, your prompt if changed, cost).</li>
      <li><b>Better prompt:</b> edit this beat's fence in
          <code>genomes/{a.genome}/nodes/{d.name}/shots.md</code> and open a PR —
          prompts are text; the diff is the review.</li>
      <li><b>What decides:</b> the founder's screening (R4); contributions land in
          the ledger as compute-watering (WATERING.md).</li>
    </ol>
  </details>
</section>""")

    out = Path(a.out) if a.out else REPO / f"shotboard-{a.node.split('-')[0]}.html"
    out.write_text(f"""<!doctype html><meta charset="utf-8">
<title>Shot board — {html.escape(d.name)}</title>
<style>
 body{{font:15px/1.5 -apple-system,system-ui,sans-serif;margin:2rem auto;max-width:960px;
      background:#0e0e12;color:#e8e8ee;padding:0 1rem}}
 h1{{font-size:1.5rem}} h2{{font-size:1.1rem;border-top:1px solid #333;padding-top:1rem}}
 pre{{white-space:pre-wrap;background:#1a1a22;padding:.6rem;border-radius:6px;font-size:.85em}}
 .cols{{display:flex;gap:1.2rem;flex-wrap:wrap}} .col{{flex:1;min-width:260px}}
 .tag{{font-size:.7em;padding:.15em .6em;border-radius:99px;vertical-align:middle}}
 .ok{{background:#1d4d2b}} .wip{{background:#4d3a1d}}
 .noimg{{width:240px;height:350px;display:flex;align-items:center;justify-content:center;
        background:#1a1a22;border-radius:6px;color:#888;text-align:center;font-size:.85em}}
 img{{border-radius:6px}} details{{margin:.6rem 0 1.2rem}} summary{{cursor:pointer;color:#8ab4ff}}
</style>
<h1>Shot board — {html.escape(d.name)}</h1>
<p>Every beat of this episode, with the <b>complete recipe</b> that made it.
Take the still and the prompts, generate a better take with <i>your</i> tools and
credits, and submit it — the beat is the fork unit. Built {date.today()} (D11).</p>
{''.join(rows)}
""")
    print(f"✓ shot board: {out} ({out.stat().st_size // 1024} KB, {len(shots)} beats)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
