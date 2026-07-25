#!/usr/bin/env python3
"""T1 renderer — storyboard leaves from T0 scripts, at $0.

Compiles a node's script (node.md, the T0 leaf) into a vertical 9:16
storyboard: one frame per scene beat, with action text, dialogue, and
on-screen overlays. Output is a self-contained HTML filmstrip plus a
provenance yaml (PRD §7.2: every render publishes its metadata).

This is the cheapest rung of the render ladder above text (§7.4) —
deterministic, reproducible from the T0 leaf, no API spend. Image and
video tiers plug in beside it later without changing the leaf format.

Usage:
    python3 pipeline/render_t1.py <genome> <node-id>     # e.g. sapling 001
    python3 pipeline/render_t1.py <genome> --all
"""

import html
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent

FRAME_CSS = """
:root { --bg:#0e1410; --screen:#0a0f0b; --ink:#e6efe8; --muted:#93a698;
  --leaf:#6fce8a; --amber:#e8b464; --line:#263529; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font: 15px/1.5 Georgia, serif; }
main { max-width: 420px; margin: 0 auto; padding: 1.5rem 1rem 4rem; }
h1 { font-size: 1.2rem; } .sub { color: var(--muted); font-size: 0.85rem; }
.frame { aspect-ratio: 9/16; background: var(--screen); border: 1px solid var(--line);
  border-radius: 16px; margin: 1.2rem 0; padding: 1.2rem; display: flex;
  flex-direction: column; overflow: hidden; position: relative; }
.frame .slug { font: 700 0.7rem/1 ui-monospace, Menlo, monospace; color: var(--amber);
  text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.8rem; }
.frame .action { color: var(--muted); font-style: italic; margin: 0.4rem 0; }
.frame .line { margin: 0.5rem 0; }
.frame .who { font: 700 0.72rem/1 ui-monospace, Menlo, monospace; color: var(--leaf); }
.frame .overlay { font-family: ui-monospace, Menlo, monospace; font-size: 0.78rem;
  color: var(--leaf); background: rgba(111,206,138,0.07); border: 1px solid var(--line);
  border-radius: 8px; padding: 0.6rem 0.8rem; white-space: pre-wrap; margin: 0.5rem 0; }
.frame .num { position: absolute; bottom: 0.7rem; right: 1rem; color: var(--line);
  font: 700 0.75rem/1 ui-monospace, Menlo, monospace; }
footer { color: var(--muted); font-size: 0.8rem; text-align: center; margin-top: 2rem; }
a { color: var(--leaf); }
"""


def extract_script(md: str) -> str:
    m = re.search(r"^## Script\s*\n(.*?)(?=^## |^---\s*$)", md, re.M | re.S)
    if not m:
        raise SystemExit("no '## Script' section found in node.md")
    return m.group(1)


def parse_frames(script: str) -> list:
    """Split on bold beat headings (**SCENE — 0:00–0:12**); collect
    action paragraphs, dialogue blockquotes, and code-fence overlays.

    Markdown hard-wraps prose, so consecutive non-blank action lines are one
    paragraph and merge into a single item — a blank line (or any other
    element) starts a new one. Keeps sentences whole downstream (T2 cuts one
    shot per item)."""
    frames = []
    current = None
    par_break = True
    # a blockquote that markdown hard-wrapped is still ONE spoken line. Without
    # this, every wrapped line after the first became ("line", "", text) — an
    # unattributed fragment, which synth_vo casts as the narrator and captions
    # show mid-sentence. Cleared by a blank line or any other element, so two
    # quotes separated by a blank stay two lines.
    quote_open = False
    lines = script.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        heading = re.match(r"^\*\*(.+?)\*\*\s*$", line.strip())
        # a beat heading always carries its timing range (SCENE — 0:00–0:12);
        # a full-bold line WITHOUT one is emphasis inside the scene, not a beat
        if heading and re.search(r"\d+:\d+\s*[–—-]\s*\d+:\d+", heading.group(1)):
            current = {"slug": heading.group(1), "items": []}
            frames.append(current)
            par_break = True
        elif heading and current is not None:
            current["items"].append(("action", strip_inline_md(heading.group(1))))
            par_break = True
        elif current is not None:
            if not line.strip():
                par_break = True
                quote_open = False
            elif line.strip().startswith("```"):
                block = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    block.append(lines[i])
                    i += 1
                current["items"].append(("overlay", "\n".join(block)))
                par_break = True
                quote_open = False
            elif line.strip().startswith(">"):
                text = re.sub(r"^>\s?", "", line.strip())
                # a speaker heading always carries a colon (inside or right
                # after the bold) — bold WITHOUT one is emphasis inside a
                # wrapped speech line, not a new speaker
                m = (re.match(r"\*\*(.+?)\s*[:：]\s*\*\*\s*(.*)", text)
                     or re.match(r"\*\*(.+?)\*\*\s*[:：]\s*(.*)", text))
                if m:
                    current["items"].append(("line", m.group(1).rstrip(":"), m.group(2)))
                elif text and quote_open and current["items"] and current["items"][-1][0] == "line":
                    prev = current["items"][-1]
                    current["items"][-1] = ("line", prev[1], (prev[2] + " " + text).strip())
                elif text:
                    current["items"].append(("line", "", text))
                par_break = True
                quote_open = True
            elif line.strip().startswith("#"):
                par_break = True
                quote_open = False
            else:
                if not par_break and current["items"] and current["items"][-1][0] == "action":
                    current["items"][-1] = ("action", current["items"][-1][1] + " " + line.strip())
                else:
                    current["items"].append(("action", line.strip()))
                par_break = False
                quote_open = False
        i += 1
    return frames


def strip_inline_md(s: str) -> str:
    return re.sub(r"[*_`]", "", s)


def render_frame(f: dict, num: int, total: int) -> str:
    parts = [f'<div class="slug">{html.escape(strip_inline_md(f["slug"]))}</div>']
    for item in f["items"]:
        if item[0] == "action":
            parts.append(f'<div class="action">{html.escape(strip_inline_md(item[1]))}</div>')
        elif item[0] == "line":
            who = f'<span class="who">{html.escape(item[1])}</span> ' if item[1] else ""
            parts.append(f'<div class="line">{who}{html.escape(strip_inline_md(item[2]))}</div>')
        elif item[0] == "overlay":
            parts.append(f'<div class="overlay">{html.escape(item[1])}</div>')
    parts.append(f'<div class="num">{num}/{total}</div>')
    return f'<div class="frame">{"".join(parts)}</div>'


def render_node(genome: str, node: dict, genome_dir: Path) -> str:
    node_dir = genome_dir / "nodes" / node["slug"]
    md = (node_dir / "node.md").read_text()
    frames = parse_frames(extract_script(md))
    if not frames:
        raise SystemExit(f"{node['id']}: no beats found in script")

    leaf_id = f"{node['id']}-t1-a"
    body = "".join(render_frame(f, i + 1, len(frames)) for i, f in enumerate(frames))
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(node['title'])} — T1 storyboard</title>
<style>{FRAME_CSS}</style></head><body><main>
<h1>{html.escape(node['id'])} — {html.escape(node['title'])}</h1>
<div class="sub">T1 storyboard leaf <code>{leaf_id}</code> · compiled from the T0 script · 9:16</div>
{body}
<footer>A leaf of the <a href="https://github.com/olegmlkvorg/banyan-city">Banyan City</a> tree.
Rendered by pipeline/render_t1.py at $0 — provenance in leaves/{leaf_id}.yaml</footer>
</main></body></html>"""

    leaves_dir = node_dir / "leaves"
    (leaves_dir / f"{leaf_id}.html").write_text(doc)
    (leaves_dir / f"{leaf_id}.yaml").write_text(
        f"""# Leaf metadata — every render publishes its full provenance (§7.2)
leaf: {leaf_id}
node: "{node['id']}"
tier: T1
form: storyboard-html
content: {leaf_id}.html
author: pipeline/render_t1.py (deterministic compile of ../node.md)
model: none
prompt: none            # deterministic — the T0 leaf is the prompt
seed: none
cost_usd: 0.00
status: live
platform_urls: []
"""
    )
    return leaf_id


def register_leaf(lineage_text: str, node_id: str, leaf_id: str) -> str:
    """Append a leaf to a node's `leaves: [...]` in lineage.yaml text,
    preserving comments. The separator is emitted only when the list already
    has entries — a bare ', ' into an empty list would write 'leaves: [, X]',
    which is invalid YAML. (render_t2/t3 inline this same pattern.)"""
    return re.sub(
        rf"(- id: \"{re.escape(node_id)}\"\n(?:.*\n)*?    leaves: \[)([^\]]*)",
        lambda m: m.group(1) + (f"{m.group(2)}, {leaf_id}" if m.group(2).strip() else leaf_id),
        lineage_text,
        count=1,
    )


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    genome, target = sys.argv[1], sys.argv[2]
    genome_dir = REPO / "genomes" / genome
    lineage_file = genome_dir / "lineage.yaml"
    lineage_text = lineage_file.read_text()
    lineage = yaml.safe_load(lineage_text)

    for node in lineage["nodes"]:
        if target != "--all" and node["id"] != target:
            continue
        leaf_id = render_node(genome, node, genome_dir)
        if leaf_id not in (node.get("leaves") or []):
            # register the new leaf in lineage.yaml, preserving comments
            lineage_text = register_leaf(lineage_text, node["id"], leaf_id)
        print(f"✓ rendered {leaf_id}")
    lineage_file.write_text(lineage_text)


if __name__ == "__main__":
    main()
