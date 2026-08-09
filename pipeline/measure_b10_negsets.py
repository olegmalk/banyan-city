#!/usr/bin/env python3
"""What each candidate person-negative set COSTS on node 001 beat 10. Box only.

The r5 lane's first measured set (defect 2's five plus `arm` and `foot`) fit
inside 77 tokens and every added term survived — and it paid for them by
shedding six more house-tier negatives than r4 did, including `low quality` and
`blurry`. That is a confound, not a detail: if the sheet comes back softer, the
round cannot say whether the person terms did it or the quality negatives leaving
did. `fit_negative` names what it drops, so the cost is measurable before a step
rather than arguable after one.

This prints, for each candidate set, the terms shed relative to r4's own two, so
the set can be chosen on what it costs instead of on what it contains.
"""
import sys
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, "
       "low quality, blurry, extra limbs, deformed, jpeg artifacts, "
       "realistic skin texture")

# what r4 already shed, and therefore what this round is not responsible for.
R4_BASELINE_DROPS = {"realistic skin texture", "jpeg artifacts"}

# the two the round must not buy its terms with: they are quality negatives and
# losing them would confound any judgment of the frames.
PROTECTED = ("low quality", "blurry")

CANDIDATES = [
    ("r4 control (none)", ""),
    ("defect 2 verbatim", "1girl, 1boy, child, person, hand"),
    ("defect 2 + foot", "1girl, 1boy, child, person, hand, foot"),
    ("defect 2 + foot + arm", "1girl, 1boy, child, person, hand, arm, foot"),
    ("no child", "1girl, 1boy, person, hand, foot"),
    ("minimal pair", "1girl, 1boy, person"),
    ("solo humans", "1girl, 1boy, person, hand"),
]

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "pipeline"))
    from generate_shots import parse_shots
    from sd_prompt import beat_negative, compress, negative_tokens, _clip_tokenizer

    if _clip_tokenizer() is None:
        print("!! NO CLIP TOKENIZER — run on the box venv; stopping.", flush=True)
        return 8

    shots_path = root / "genomes/sapling/nodes/001-capability-inventory/shots.md"
    shots = {s["num"]: s for s in parse_shots(shots_path.read_text(encoding="utf-8"))}
    authored = shots[10]["prompt"]
    pos, _ = compress(authored)
    print(f"positive: {negative_tokens(pos)} tokens (unchanged by every row below)\n",
          flush=True)

    for label, extra in CANDIDATES:
        warns = []
        neg = beat_negative(NEG, authored, extra, warn=warns.append)
        sent = {p.strip().lower() for p in neg.split(",")}
        dropped = set()
        for w in warns:
            if "DROPPED:" in w:
                dropped = {t.strip().lower()
                           for t in w.split("DROPPED:", 1)[1].split(",")}
        extra_cost = sorted(dropped - R4_BASELINE_DROPS)
        added = [t.strip() for t in extra.split(",") if t.strip()]
        missing = [t for t in added if t.lower() not in sent]
        lost_protected = [t for t in PROTECTED if t in dropped]
        verdict = "OK"
        if missing:
            verdict = f"UNUSABLE — trimmed away: {', '.join(missing)}"
        elif lost_protected:
            verdict = f"CONFOUNDED — loses {', '.join(lost_protected)}"
        print(f"{label:<24} {negative_tokens(neg):>3} tok  "
              f"adds {len(added)}  {verdict}", flush=True)
        if extra_cost:
            print(f"{'':<24} pays with: {', '.join(extra_cost)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
