#!/usr/bin/env python3
"""The one visual language for every page this repo publishes.

Direction: THE GROVE AT NIGHT — a bioluminescent reading room. The story is
an engineer reincarnated as a tree, and the site wears that tension: organic
serif display type for the story, terminal monospace for the machine and its
receipts. Deep forest dark by default (daylight paper in light mode), a soft
canopy glow, film grain, sap-amber for every call to action.

Constraints (same as build_site.py): self-contained — no external fonts, no
CDN, no client JS required. Pure CSS, system font stacks, data-URI textures.

Every builder (build_site, build_shotboard, build_status, build_sim, lab
regenerators) imports THEME_CSS and appends only page-specific rules.
"""

# Film grain: inline SVG turbulence, self-contained, ~0 bytes over the wire.
GRAIN = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
         "width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence "
         "type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E"
         "%3Crect width='160' height='160' filter='url(%23n)' opacity='0.5'/%3E"
         "%3C/svg%3E\")")

DISPLAY = "'Iowan Old Style','Palatino Nova',Palatino,'Book Antiqua',Georgia,serif"
BODY = "'Iowan Old Style',Palatino,Georgia,'Times New Roman',serif"
MONO = "ui-monospace,'SF Mono',Menlo,Consolas,monospace"

THEME_CSS = f"""
:root {{
  --bg: #070d09; --bg-glow: #10241a; --panel: #0d1610; --panel-2: #111c14;
  --ink: #e9f2ea; --muted: #9cb2a1; --faint: #6d8273;
  --leaf: #8ade9f; --leaf-deep: #2e6b44; --leaf-dim: #234631;
  --sap: #ffc76a; --sap-deep: #6b4c1a; --sap-ink: #1a1206;
  --line: rgba(138,222,159,.16); --line-soft: rgba(138,222,159,.09);
  --code-bg: #060a07; --shadow: 0 18px 50px -18px rgba(0,0,0,.65);
  --display: {DISPLAY};
  --body: {BODY};
  --mono: {MONO};
}}
@media (prefers-color-scheme: light) {{
  :root {{
    --bg: #f4f1e6; --bg-glow: #e3ecdb; --panel: #fbf9f1; --panel-2: #f2efe2;
    --ink: #1c291f; --muted: #55694f; --faint: #7d8f76;
    --leaf: #1e7a3f; --leaf-deep: #9cc4a8; --leaf-dim: #c4d9c9;
    --sap: #b06f10; --sap-deep: #e8c98d; --sap-ink: #fffdf5;
    --line: rgba(30,90,50,.22); --line-soft: rgba(30,90,50,.11);
    --code-bg: #ebe7d8; --shadow: 0 14px 40px -18px rgba(60,80,55,.35);
  }}
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  margin: 0; background: var(--bg); color: var(--ink);
  font: 17px/1.7 var(--body);
  -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
  background-image:
    radial-gradient(1100px 520px at 50% -180px, var(--bg-glow), transparent 70%),
    radial-gradient(700px 420px at 85% 8%, rgba(255,199,106,.05), transparent 70%);
  background-repeat: no-repeat;
  /* NOT background-attachment: fixed — with the grain layer below it, a fixed
     gradient made the compositor repaint the whole viewport continuously and
     pinned a Chrome GPU process at 100% of a core for hours (found on the
     founder's Mac, 2026-07-31, with several of these pages open). */
}}
body::after {{ /* film grain over the page, never intercepting a tap */
  content: ""; position: absolute; inset: 0; pointer-events: none; z-index: 2;
  background: {GRAIN}; opacity: .045;
  /* absolute + no blend mode, deliberately: a POSITION:FIXED layer with
     mix-blend-mode forces the compositor to re-blend the whole viewport every
     frame, forever, on every open tab. That is what pinned a Chrome GPU
     process at 100% of a core for 13 hours on the founder's Mac
     (2026-07-31) — and it would have been quietly eating viewers' phone
     batteries too. Texture is not worth a spinning fan. */
}}
main {{ max-width: 720px; margin: 0 auto; padding: 1.6rem 1.25rem 5rem; position: relative; }}
a {{ color: var(--leaf); text-decoration: none; }}
a:hover {{ text-decoration: underline; text-underline-offset: 3px; }}
h1, h2, h3 {{ font-family: var(--display); line-height: 1.15; font-weight: 600;
  letter-spacing: -0.015em; text-wrap: balance; }}
h1 {{ font-size: clamp(2rem, 6.5vw, 3rem); margin: .4rem 0 .6rem; }}
h2 {{ font-size: 1.45rem; margin: 2.6rem 0 .8rem; }}
h3 {{ font-size: 1.1rem; }}
p {{ margin: .8rem 0; }}
hr {{ border: 0; border-top: 1px solid var(--line); margin: 2.4rem 0; }}
img, video {{ max-width: 100%; }}

/* ---- voice: the machine annotates the story ---- */
.eyebrow {{ font: 700 .72rem/1 var(--mono); letter-spacing: .22em; text-transform: uppercase;
  color: var(--sap); margin: 0 0 .4rem; }}
.eyebrow a {{ color: inherit; }}
.lede {{ font-size: 1.12rem; color: var(--muted); max-width: 36em; }}
code, pre {{ font-family: var(--mono); font-size: .84em; }}
code {{ background: var(--code-bg); border: 1px solid var(--line-soft);
  border-radius: 5px; padding: .08em .35em; }}
pre {{ background: var(--code-bg); border: 1px solid var(--line); border-radius: 10px;
  padding: .9rem 1.1rem; overflow-x: auto; color: var(--leaf); }}
pre code {{ background: none; border: 0; padding: 0; }}
blockquote {{ margin: 1.1rem 0; padding: .5rem 1.15rem; border-left: 3px solid var(--sap);
  color: var(--ink); background: linear-gradient(90deg, var(--panel-2), transparent 85%);
  border-radius: 0 10px 10px 0; font-style: italic; }}
blockquote strong {{ font-style: normal; font-family: var(--mono); font-size: .78em;
  letter-spacing: .08em; text-transform: uppercase; color: var(--sap); }}

/* ---- navigation ---- */
.crumbs {{ font: 600 .78rem/1.9 var(--mono); color: var(--faint);
  margin-bottom: 1.4rem; letter-spacing: .02em; }}
.crumbs a {{ color: var(--muted); }}
.crumbs a:first-child {{ color: var(--leaf); }}

/* ---- chips → badges ---- */
.chip {{ display: inline-block; font: 700 .68rem/1 var(--mono); letter-spacing: .07em;
  text-transform: uppercase; padding: .34rem .6rem; border-radius: 999px;
  border: 1px solid var(--line); color: var(--muted); vertical-align: middle;
  margin: 0 .35rem .3rem 0; background: var(--panel); }}
.chip.hot {{ color: var(--sap); border-color: var(--sap-deep);
  background: linear-gradient(180deg, rgba(255,199,106,.12), transparent); }}
.chip.trunk, .chip.live {{ color: var(--leaf); border-color: var(--leaf-deep); }}

/* ---- surfaces ---- */
.panel, .card, .notice {{ background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 16px; box-shadow: var(--shadow); }}
.card {{ padding: 1rem 1.2rem; }}
.card .title {{ font-family: var(--display); font-size: 1.15rem; font-weight: 600; }}
.card .teaser {{ color: var(--muted); font-size: .95rem; margin: .4rem 0 .55rem; }}
.card .meta {{ font: 600 .78rem/1.7 var(--mono); color: var(--faint); }}
.notice {{ padding: .85rem 1.1rem; font-size: .93rem; color: var(--muted);
  border-style: solid; box-shadow: none; }}

/* ---- drawers: the receipts live one fold down ---- */
details.drawer {{ background: var(--panel); border: 1px solid var(--line);
  border-radius: 14px; margin: 1rem 0; overflow: hidden; }}
details.drawer > summary {{ cursor: pointer; list-style: none; padding: .85rem 1.1rem;
  font: 700 .8rem/1.4 var(--mono); letter-spacing: .06em; text-transform: uppercase;
  color: var(--muted); user-select: none; }}
details.drawer > summary::-webkit-details-marker {{ display: none; }}
details.drawer > summary::before {{ content: "▸"; display: inline-block; margin-right: .6rem;
  color: var(--sap); transition: transform .2s ease; }}
details.drawer[open] > summary::before {{ transform: rotate(90deg); }}
details.drawer > summary:hover {{ color: var(--ink); }}
details.drawer > .drawer-body {{ padding: 0 1.1rem 1rem; }}

/* ---- buttons ---- */
.btn {{ display: inline-block; background: linear-gradient(180deg, var(--sap), #e8a94a);
  color: var(--sap-ink); font: 700 .95rem/1 var(--body); padding: .78rem 1.4rem;
  border-radius: 999px; margin: .3rem .35rem .3rem 0;
  box-shadow: 0 6px 24px -8px rgba(255,199,106,.45); }}
.btn:hover {{ text-decoration: none; transform: translateY(-1px);
  box-shadow: 0 10px 28px -8px rgba(255,199,106,.6); }}
.btn.ghost {{ background: transparent; color: var(--leaf);
  border: 1px solid var(--leaf-deep); box-shadow: none; }}
.btn.ghost:hover {{ border-color: var(--leaf); box-shadow: none; }}
.btn {{ transition: transform .15s ease, box-shadow .15s ease; }}

/* ---- the phone: episodes are 9:16 and shown that way ---- */
.phone {{ margin: 1.4rem auto; max-width: 320px; }}
.phone video {{ width: 100%; aspect-ratio: 9 / 16; object-fit: contain; display: block;
  background: var(--code-bg); border: 1px solid var(--line); border-radius: 22px;
  box-shadow: var(--shadow), 0 0 80px -30px rgba(138,222,159,.35); }}
.phone figcaption {{ font: 600 .78rem/1.5 var(--mono); color: var(--faint);
  text-align: center; margin-top: .6rem; }}

/* ---- tables: hairlines, not cages ---- */
table {{ border-collapse: collapse; width: 100%; font-size: .88em;
  display: block; overflow-x: auto; }}
th, td {{ border: 0; border-bottom: 1px solid var(--line-soft);
  padding: .55rem .7rem; text-align: left; }}
th {{ font: 700 .72rem/1.4 var(--mono); letter-spacing: .08em; text-transform: uppercase;
  color: var(--faint); border-bottom: 1px solid var(--line); background: none; }}
td code {{ font-size: .95em; }}

/* ---- entrance: one staggered rise on load, then stillness ---- */
@keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }}
  to {{ opacity: 1; transform: none; }} }}
.rise {{ animation: rise .6s cubic-bezier(.2,.7,.3,1) both; }}
.rise:nth-child(2) {{ animation-delay: .06s; }} .rise:nth-child(3) {{ animation-delay: .12s; }}
.rise:nth-child(4) {{ animation-delay: .18s; }} .rise:nth-child(5) {{ animation-delay: .24s; }}
@media (prefers-reduced-motion: reduce) {{
  .rise {{ animation: none; }} html {{ scroll-behavior: auto; }}
  .btn {{ transition: none; }}
}}

/* ---- footer ---- */
footer {{ margin-top: 4.5rem; padding-top: 1.4rem; border-top: 1px solid var(--line);
  color: var(--faint); font: 500 .84rem/1.8 var(--mono); text-align: center; }}

/* ---- the one-breath glossary strangers actually need ---- */
.legend {{ font: 600 .76rem/1.8 var(--mono); color: var(--faint); text-align: center;
  margin: 2.2rem 0 0; }}
.legend b {{ color: var(--leaf); font-weight: 700; }}
"""

if __name__ == "__main__":
    print(f"THEME_CSS: {len(THEME_CSS)} chars")
