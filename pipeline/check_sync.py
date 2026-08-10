#!/usr/bin/env python3
"""Does each beat's PICTURE match the words spoken over it?

    python3 pipeline/check_sync.py sapling 001
    python3 pipeline/check_sync.py sapling 001 --strict   # exit 1 on any finding

WHY THIS EXISTS. Founder, 2026-08-03, on the assembled episode 1:

    "there is again some dialogue out of sync, when he says 'huh, blue' it is
     showing the coffee scene. reflect why this is happening and why you still
     have not implemented guard to make sure it will not happen again."

The word **again** is the whole point. This class of defect had been found by eye
and fixed beat-by-beat several times, and each fix was a fix to one beat rather
than to the pipeline. Beat 05 of episode 1 had THREE script eras fossilized in it
simultaneously:

    beat title        HUH. BLUE.              (current era)
    VO line           "Huh. Blue."            (current era)
    image prompt      broken coffee mug,      (an older era: the apartment)
                      spilled coffee, dark
                      wooden floorboards
    still filename    05-huh-GREEN.png        (an even older era: waking in grass)

Nothing in the pipeline compared those four things, so all four could drift apart
silently and only an eye watching the finished cut would ever notice.

`qa_episode.py` does not cover this and cannot: it inspects the rendered video
(black frames, caption bands, durations). By the time a video exists the mismatch
is already rendered, voiced and assembled. This runs on the TEXT, before anything
is generated, which is where the error actually is.

WHAT IT DOES NOT DO. No vision model, no semantic judgement, no LLM call. Three
pure string checks, each of which would have caught a real bug we actually shipped.
A cheap deterministic check that catches the class beats a clever one that needs a
model and a budget. Where a check cannot be sure it says WARN, not FAIL, because a
gate that cries wolf gets bypassed and then protects nothing.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Colours a viewer can see in the frame. If a line NAMES one, the picture had
# better contain it — this is the beat-05 bug, stated as a rule. Kept short and
# concrete on purpose: "blue" is checkable, "cold" is not.
COLOURS = ("blue", "green", "red", "orange", "yellow", "purple", "white",
           "black", "brown", "grey", "gray", "gold", "amber", "pink")

# Words in a prompt that legitimately satisfy a colour without naming it. The
# beat-05 prompt said "dying screen glow" and "near darkness"; neither is blue.
COLOUR_SYNONYMS = {
    "blue": ("sky", "azure", "cyan", "teal"),
    "green": ("grass", "leaf", "leaves", "foliage", "sprout", "moss"),
    "black": ("darkness", "dark", "night", "unlit", "shadow"),
    "white": ("pale", "bright"),
    "brown": ("soil", "dirt", "wood", "wooden", "earth"),
    "amber": ("warm light", "sunset", "golden"),
    "gold": ("golden", "amber", "sunlight"),
}


def slugify(title: str) -> str:
    """Beat title -> the filename stem convention used in stills/ and clips/."""
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s


def parse_shots(path: Path) -> dict:
    """beat number -> {title, note, prompt} from shots.md."""
    txt = path.read_text(encoding="utf-8")
    out = {}
    # Anchor on the TIMESTAMP, not on the first "(". A beat titled
    # "ZERO (0) MOVING PARTS (0:29-0:35)" truncated to "ZERO" under `\(`, and the
    # check then reported a beat-order mismatch against node.md that did not
    # exist. A gate whose parser invents findings gets bypassed, so this matters
    # more than the check it feeds.
    parts = re.split(r"^## Beat (\d+) — (.+?) \(\d+:\d+", txt, flags=re.M)
    for i in range(1, len(parts) - 2, 3):
        num, title, body = int(parts[i]), parts[i + 1].strip(), parts[i + 2]
        m = re.search(r"```\n(.+?)\n```", body, re.S)
        # the prose above the fence is the director's note; the fence is the prompt
        note = body.split("```")[0]
        out[num] = {"title": title, "note": note.strip(),
                    "prompt": (m.group(1) if m else "").strip()}
    return out


def parse_script(path: Path) -> list:
    """Ordered [{title, lines[]}] from node.md's ## Script section.

    Beats are `**TITLE — m:ss–m:ss**`; spoken lines are `> **WHO:** text`. The
    order here is the EPISODE order, which is what beat numbers must follow.
    """
    txt = path.read_text(encoding="utf-8")
    body = txt.split("## Script", 1)[-1].split("\n## ", 1)[0]
    beats = []
    cur = None
    for ln in body.splitlines():
        m = re.match(r"\*\*(.+?) — \d+:\d+[–-]\d+:\d+\*\*\s*$", ln.strip())
        if m:
            cur = {"title": m.group(1).strip(), "lines": []}
            beats.append(cur)
            continue
        m = re.match(r">\s*\*\*(.+?):?\*\*\s*(.+)", ln.strip())
        if m and cur is not None:
            cur["lines"].append(m.group(2).strip())
    return beats


def spoken_text(node_dir: Path, beat: int) -> str | None:
    """What the RECORDED voice actually says, from the VO manifest."""
    p = node_dir / "clips" / f"{beat:02d}-vo.json"
    if not p.is_file():
        return None
    try:
        j = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return " ".join(l.get("text", "") for l in j.get("lines", [])).strip()


def norm(s: str) -> str:
    """Compare on words, not punctuation: VO manifests normalise dashes and
    ellipses differently from the script and that is not a defect."""
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).split().__str__()


def check(genome: str, node: str) -> list:
    nodes = REPO / "genomes" / genome / "nodes"
    d = next((x for x in sorted(nodes.iterdir())
              if x.is_dir() and x.name.startswith(node)), None)
    if not d:
        raise SystemExit(f"no node dir starting with {node!r}")

    shots = parse_shots(d / "shots.md")
    script = parse_script(d / "node.md")
    findings = []

    def add(sev, beat, what, detail):
        findings.append({"sev": sev, "beat": beat, "what": what, "detail": detail})

    # ---- 0. THIS GATE MUST NOT PASS ON NOTHING -------------------------------
    # Every check below is a loop over `script` or `shots`, and the verdict is
    # "no findings". So a parse that returns zero beats — a node.md with no
    # `## Script` heading, a heading style that drifts from the
    # `**TITLE — 0:00–0:05**` line parse_script matches, a shots.md that moved —
    # ran every loop zero times and printed "picture, script and voice agree on
    # every beat". Green, in the exact words a reader trusts, having compared
    # nothing at all. Both files empty is even quieter: `len(script) != len(shots)`
    # is 0 != 0, so the one structural check also stays silent.
    #
    # The question every check has to answer is what it would print if the thing
    # it reads were completely broken. This one printed a tick. It is a render
    # gate (render_local.py) and its sentence is quoted verbatim in the review
    # READMEs the founder reads, so the tick travels.
    if not script:
        add("FAIL", 0, "unreadable script",
            f"parsed 0 beats out of {d.name}/node.md — this gate compared nothing. "
            f"Expected `## Script` and beats headed `**TITLE — 0:00–0:05**`")
    if not shots:
        add("FAIL", 0, "unreadable shots",
            f"parsed 0 beats out of {d.name}/shots.md — this gate compared nothing. "
            f"Expected beats headed `## Beat NN — TITLE`")

    # ---- A. the script's beat order must equal shots.md's beat order ----------
    # Caught by hand tonight: node.md's flail beat sat at 0:29 while shots.md
    # beat 06 was TOO BLUE at 0:24, so "beat 6" meant two different shots
    # depending on which file you opened.
    if len(script) != len(shots):
        add("FAIL", 0, "beat count",
            f"node.md has {len(script)} beats, shots.md has {len(shots)}")
    for i, sb in enumerate(script, start=1):
        st = shots.get(i)
        if not st:
            continue
        if slugify(sb["title"]) != slugify(st["title"]):
            add("FAIL", i, "beat order",
                f"node.md #{i} is {sb['title']!r} but shots.md #{i} is "
                f"{st['title']!r} — the two files disagree about what beat {i} IS")

    # ---- B. the still's filename must match the beat's title -----------------
    # `05-huh-green.png` under a beat titled HUH. BLUE. is a fossil of a dead
    # script era, and it is the cheapest possible signal that one exists.
    for num, st in shots.items():
        want = slugify(st["title"])
        found = [p.name for p in sorted((d / "stills").glob(f"{num:02d}-*.png"))
                 if "REVOKED" not in p.name]
        if not found:
            continue
        stem = found[0][3:].rsplit(".", 1)[0]
        # the convention truncates long titles, so require a prefix relationship
        if not (want.startswith(stem) or stem.startswith(want[:len(stem)])):
            add("FAIL", num, "stale still",
                f"beat is {st['title']!r} (slug {want!r}) but the still is "
                f"{found[0]!r} — renamed beat, or a still from an older cut")

    # ---- C. the recorded voice must say what the script says -----------------
    # A script edit does not re-voice anything, so an approved line and a shipped
    # line can differ with nothing complaining.
    for i, sb in enumerate(script, start=1):
        rec = spoken_text(d, i)
        if rec is None or not sb["lines"]:
            continue
        want = " ".join(sb["lines"])
        if norm(rec) != norm(want):
            # Show WHERE they diverge, not the first 60 characters of each. A
            # finding that reads "script says 'Growth includes...' but the mp3 says
            # 'Growth includes...'" is indistinguishable from a formatting artifact
            # and gets waved away; the first differing word is actionable.
            a_w = re.sub(r"[^a-z0-9 ]+", " ", want.lower()).split()
            b_w = re.sub(r"[^a-z0-9 ]+", " ", rec.lower()).split()
            j = next((k for k in range(max(len(a_w), len(b_w)))
                      if k >= len(a_w) or k >= len(b_w) or a_w[k] != b_w[k]), 0)
            ctx = " ".join(a_w[max(0, j - 4):j])
            add("FAIL", i, "stale VO",
                f"after ...{ctx!r} the script says "
                f"{(a_w[j] if j < len(a_w) else '(ends)')!r} but {i:02d}-vo.mp3 says "
                f"{(b_w[j] if j < len(b_w) else '(ends)')!r} — recording predates "
                f"the current script")

    # ---- C2. a beat the script silenced must not keep its recording ----------
    # Check C is driven off the SCRIPT's lines, so `not sb["lines"]` skips the
    # beat entirely and a take that outlived its line is invisible to it. That
    # is not hypothetical: on 2026-08-03 the founder moved "Huh. Blue." off
    # beat 05 to beat 06 where the blue is actually on screen, the retake ran
    # `synth_vo --beats 06`, and synth_vo's own silent-beat archiver never
    # visited beat 05 because --beats skips it before that check. So 05-vo.mp3
    # survived, and the assembly spoke "Huh. Blue." twice — the second time
    # over near-black mug shards, which is verbatim the defect this file was
    # written to end. The gate watched script→picture and never asked whether a
    # recording existed that the script no longer accounted for.
    for i, sb in enumerate(script, start=1):
        if sb["lines"]:
            continue
        rec = spoken_text(d, i)
        if rec is None:
            continue
        add("FAIL", i, "orphan take",
            f"beat {i} ({sb['title']}) has no line in the script, but "
            f"{i:02d}-vo.json says {rec[:44]!r} — a take that outlived its "
            f"line. Archive it (R6) or restore the line")

    # ---- D. a colour named in the line must be visible in the picture --------
    # The beat-05 bug, as a rule: "Huh. Blue." over a prompt whose subject is a
    # broken coffee mug on dark floorboards.
    for i, sb in enumerate(script, start=1):
        st = shots.get(i)
        if not st or not sb["lines"]:
            continue
        line, prompt = " ".join(sb["lines"]).lower(), st["prompt"].lower()
        for c in COLOURS:
            if not re.search(rf"\b{c}\b", line):
                continue
            ok = re.search(rf"\b{c}\b", prompt) or any(
                s in prompt for s in COLOUR_SYNONYMS.get(c, ()))
            if not ok:
                add("FAIL", i, "colour mismatch",
                    f"the line says {c!r} — {' '.join(sb['lines'])[:44]!r} — but "
                    f"beat {i}'s picture has no {c} in it: "
                    f"{st['prompt'][:56]!r}...")
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("genome")
    ap.add_argument("node")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on any FAIL (what CI and the render gate use)")
    a = ap.parse_args()

    findings = check(a.genome, a.node)
    if not findings:
        print(f"  ✓ {a.node}: picture, script and voice agree on every beat")
        return 0
    for f in sorted(findings, key=lambda x: (x["beat"], x["what"])):
        print(f"  {f['sev']}  beat {f['beat']:02d}  [{f['what']}]  {f['detail']}")
    fails = sum(1 for f in findings if f["sev"] == "FAIL")
    print(f"\n  {fails} FAIL, {len(findings) - fails} WARN")
    return 1 if (a.strict and fails) else 0


if __name__ == "__main__":
    sys.exit(main())
