#!/usr/bin/env python3
"""Measure what the machine path actually sends for every `no humans` fence.

WHY THIS EXISTS. Queue entry `no-humans-negative-sweep-1786293900` asked for the
eight fences in node 001 carrying `no humans` to be rewritten so the phrase leads
the positive, per the r5 proof (82fd4ff: on animagine-xl-3.1 `no humans` is a
POSITIVE Danbooru tag, and `sd_prompt._NEGATION` inverts it into the negative).
Run before making that edit, this says the edit cannot work: `_NEGATION` matches
`no <noun>` in ANY position — leading, medial, or in the trailing `No …` sentence
— so no wording in a shots.md fence can put the tag into the positive prompt.

It prints three columns per beat:

  A  what the fence as written sends today
  B  the same fence with `no humans` moved to the front — the sweep's edit
  C  what r5's post-`compress()` transform sends: the tag re-injected at the head
     of the positive and bare `humans` deleted from the negative

A and B are the same instruction (B is one token worse — the orphan comma left
where the leading tag was lifted out). C is the number a proposal to teach
`_NEGATION` this one exception would have to live with.

RUN IT WHERE A REAL CLIP TOKENIZER LIVES. It refuses rather than guessing: the
prose estimator over-counts a tag list and on 2026-08-09 it invented three
positive-tail drops that the box's real tokenizer showed were not happening. On
the rtx5090:

    ssh rtx5090 "set PYTHONUTF8=1& C:\\banyan-farm\\venv\\Scripts\\python.exe ^
                 C:\\banyan-farm\\banyan-city\\pipeline\\measure_no_humans.py"

$0, CPU only, no model load and no render.
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))

import sd_prompt  # noqa: E402

# farm_worker.py:523 — the house negative every renderer starts from.
HOUSE = ("photorealistic, 3d render, abstract, text, watermark, signature, "
         "low quality, blurry, extra limbs, deformed, jpeg artifacts, "
         "realistic skin texture")

DEFAULT_SHOTS = ("genomes/sapling/nodes/001-capability-inventory/shots.md",
                 "genomes/sapling/nodes/002b-first-citizen/shots.md")

_BEAT = re.compile(r"^##\s*Beat\s*(\d+)", re.I)


def fences(path: Path, phrase: str = "no humans") -> list:
    """(beat, line_number, text) for every fenced prompt containing `phrase`.

    Reads the FENCES, not the prose: 002b's only two hits are notes, and counting
    those is how the sweep entry came to say eight when the answer was seven.
    """
    out, beat, start, body = [], "?", None, []
    for i, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        m = _BEAT.match(line)
        if m:
            beat = m.group(1)
        if line.strip().startswith("```"):
            if start is None:
                start, body = i, []
            else:
                text = " ".join(x for x in body if x.strip())
                if phrase in text.lower():
                    out.append((beat, start + 1, text))
                start = None
        elif start is not None:
            body.append(line)
    return out


def lead_form(text: str) -> str:
    """The fence rewritten so `no humans` leads — the sweep's prescribed edit."""
    t = text.replace("plant focus, no humans, ", "no humans, plant focus, ")
    t = t.replace(", no humans.", ".")
    if not t.lower().startswith("no humans"):
        t = "no humans, " + t
    return t


def r5_transform(pos: str, neg: str) -> tuple:
    """r5's one named deviation, applied to already-compressed strings."""
    return ("no humans, " + pos.lstrip(", "),
            ", ".join(t.strip() for t in neg.split(",") if t.strip() != "humans"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("shots", nargs="*", default=list(DEFAULT_SHOTS))
    ap.add_argument("--phrase", default="no humans")
    args = ap.parse_args()

    tok = sd_prompt._clip_tokenizer()
    if tok is None:
        print("*** no CLIP tokenizer here — refusing to print estimates.\n"
              "    Run this on a box that can render; see the module docstring.")
        return 2
    print("REAL CLIP TOKENIZER: openai/clip-vit-large-patch14")
    n = lambda s: len(tok(s)["input_ids"])  # noqa: E731

    rows = 0
    for rel in args.shots:
        path = REPO / rel
        if not path.exists():
            print("!! missing:", rel)
            continue
        found = fences(path, args.phrase)
        print("\n%s — %d fence(s) carrying %r" % (rel, len(found), args.phrase))
        for beat, line, text in found:
            rows += 1
            print("=" * 74)
            print("BEAT %s (line %d)" % (beat, line))
            a_pos = a_neg = ""
            for label, variant in (("A today", text), ("B lead-form", lead_form(text))):
                pos, dropped = sd_prompt.compress(variant)
                warn = []
                neg = sd_prompt.beat_negative(HOUSE, variant, warn=warn.append)
                print("  %-12s POS %2d | NEG %2d | tag in POS: %-5s | bare noun in NEG: %s"
                      % (label, n(pos), n(neg),
                         args.phrase in pos.lower(),
                         any(x.strip() == args.phrase.split()[-1] for x in neg.split(","))))
                if dropped:
                    print("               POS DROPPED:", dropped)
                for w in warn:
                    print("              ", w.strip())
                if label == "A today":
                    a_pos, a_neg = pos, neg
            c_pos, c_neg = r5_transform(a_pos, a_neg)
            print("  %-12s POS %2d | NEG %2d   <- r5 post-compress transform"
                  % ("C r5-fix", n(c_pos), n(c_neg)))
    print("=" * 74)
    print("%d fence(s) measured" % rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
