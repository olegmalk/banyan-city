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
STILL = {"width": 832, "height": 1216, "steps": 40, "cfg": 7.5, "seed_base": 20260719}
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


def img_tag(p: Path, w: int = 240, rel: str = "") -> str:
    """rel="" embeds base64 (self-contained local file); rel=prefix links the
    copied file instead — the site build copies media next to the page."""
    if not p.exists():
        return '<div class="noimg">no approved still yet — still in review</div>'
    if rel:
        return f'<img width="{w}" src="{rel}/{p.name}" alt="{p.name}">'
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f'<img width="{w}" src="data:image/png;base64,{b64}" alt="{p.name}">'


def take_cells(takes_clips: Path, num: int, slug: str, rel: str) -> str:
    """Motion takes for a beat, newest engines first, each with its sidecar link."""
    if not takes_clips.is_dir() or not rel:
        return ""
    vids = sorted(takes_clips.glob(f"{num:02d}-{slug}.*.mp4"))
    if not vids:
        return ""
    cells = "".join(
        f'<div><video width="200" controls muted loop src="{rel}-clips/{v.name}"></video>'
        f'<br><small>{html.escape(v.suffixes[-2].lstrip("."))} · '
        f'<a href="{rel}-clips/{v.with_suffix("").name}.meta.yaml">provenance</a></small></div>'
        for v in vids)
    return f'<h3>Motion takes</h3><div class="cols">{cells}</div>'


def beat_notes(shots_md: str) -> dict:
    """num → the human note between the beat heading and its prompt fence —
    the INTENT ('Line: ... Camera on ...') a voter needs to judge any image."""
    import re
    notes = {}
    heads = list(re.finditer(r"^## Beat (\d+) — [^\n]*$", shots_md, re.M))
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(shots_md)
        body = shots_md[h.end():end]
        fence = body.find("```")
        note = body[:fence if fence >= 0 else len(body)].strip()
        notes[int(h.group(1))] = note
    return notes


def variant_cells(takes_stills: Path, num: int, rel: str) -> str:
    """Candidate stills for an unapproved beat, labelled A/B/C…, votable."""
    if not takes_stills.is_dir():
        return ""
    files = sorted(f for f in takes_stills.glob(f"{num:02d}-*.png"))
    if not files:
        return ""
    cells = "".join(
        f'<figure><img width="170" src="{rel}-takes/{f.name}" alt="{f.name}">'
        f'<figcaption><b>{chr(65 + i)}</b></figcaption></figure>'
        if rel else
        f'<figure>{img_tag(f, 170)}<figcaption><b>{chr(65 + i)}</b></figcaption></figure>'
        for i, f in enumerate(files))
    return f'<h3>Candidates — vote below</h3><div class="cols variants">{cells}</div>'


def board_html(genome: str, d: Path, rel: str = "") -> str:
    """The full page HTML. rel='' → self-contained (base64); rel='NAME' → site
    mode, images at NAME/ and clips at NAME-clips/ next to the page."""
    raw = (d / "shots.md").read_text()
    shots = parse_shots(raw)
    notes = beat_notes(raw)
    stills_dir = d / "stills"
    import yaml as _yaml
    try:
        vote_url = _yaml.safe_load((d / "sap" / "reactions.yaml").read_text())["url"]
    except Exception:
        vote_url = ""
    a = type("A", (), {"genome": genome})  # keep the fork-text f-string working

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
  <p class="intent"><b>This beat:</b> {html.escape(notes.get(s['num'], '') or '(no note)')}</p>
  <div class="cols">
    <div class="col">{img_tag(still, rel=rel)}</div>
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
  {'' if approved else variant_cells(d / "takes" / "stills", s["num"], rel)}
  {f'<p class="vote">🗳 <b>Vote:</b> comment <code>beat {s["num"]:02d}: A</code> (or B/C/D, or <code>none</code> + why) on <a href="{vote_url}">the reactions thread</a> — every vote counts the same way, the founder&#39;s included (weights per D3).</p>' if not approved and vote_url else ''}
  {take_cells(d / "takes" / "clips", s["num"], s["slug"], rel)}
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

    return f"""<!doctype html><meta charset="utf-8">
<title>Shot board — {html.escape(d.name)}</title>
<style>
 body{{font:15px/1.5 -apple-system,system-ui,sans-serif;margin:2rem auto;max-width:960px;
      background:#0e0e12;color:#e8e8ee;padding:0 1rem}}
 h1{{font-size:1.5rem}} h2{{font-size:1.1rem;border-top:1px solid #333;padding-top:1rem}}
 pre{{white-space:pre-wrap;background:#1a1a22;padding:.6rem;border-radius:6px;font-size:.85em}}
 .cols{{display:flex;gap:1.2rem;flex-wrap:wrap}} .col{{flex:1;min-width:260px}}
 .tag{{font-size:.7em;padding:.15em .6em;border-radius:99px;vertical-align:middle}}
 .ok{{background:#1d4d2b}} .wip{{background:#4d3a1d}}
 .intent{{background:#14141c;padding:.5rem .8rem;border-radius:6px}}
 .variants figure{{margin:0;text-align:center}}
 .vote{{background:#12202b;padding:.5rem .8rem;border-radius:6px}}
 .noimg{{width:240px;height:350px;display:flex;align-items:center;justify-content:center;
        background:#1a1a22;border-radius:6px;color:#888;text-align:center;font-size:.85em}}
 img{{border-radius:6px}} details{{margin:.6rem 0 1.2rem}} summary{{cursor:pointer;color:#8ab4ff}}
</style>
<h1>Shot board — {html.escape(d.name)}</h1>
<p>Every beat of this episode, with the <b>complete recipe</b> that made it.
Take the still and the prompts, generate a better take with <i>your</i> tools and
credits, and submit it — the beat is the fork unit. Built {date.today()} (D11).</p>
{''.join(rows)}
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
