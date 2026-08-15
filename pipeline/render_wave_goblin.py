#!/usr/bin/env python3
"""002b goblin wave, round-next — the r8 green-skin stack on every goblin beat.

WHY THIS SCRIPT EXISTS AND WHY THE PROMPTS ARE NOT IN shots.md YET.
Round 8 of beat 13 established, on the founder's order ("all the goblin images
look like female demihumans"), that two Danbooru tags move the species in 4 of 4:
positive `green skin` + `plump` behind the `1boy` count tag, negative `female
goblin` + `elf` in the explicit tier. What it did NOT establish is the goblin —
taste ledger record 32 ruled "P2 is not a valid gate until he defines the goblin,
and no r8 may be scored against the old one". So this wave is PREPARED, measured
and staged, and it does not fire until he defines it. The drafts therefore live
in a data file next to this script rather than in shots.md: writing them into
shots.md would change the string every other renderer sends for these beats,
before the author has agreed to a word of it.

    python render_wave_goblin.py --root <repo> --drafts wave-drafts.yaml --dry
    python render_wave_goblin.py --root <repo> --drafts wave-drafts.yaml \
        --goblin-def "green skin, plump, tusks" --dry
    python render_wave_goblin.py --root <repo> --drafts wave-drafts.yaml --beat 07

THE GOBLIN SLOT. Every draft carries the marker {{GOBLIN}} exactly once, in the
species position immediately after the count tag's noun. `--goblin-def` fills it.
The default fill is r8's own two tags, which is the WORST CASE THAT HAS BEEN
MEASURED: r8 sits at 77/77 with the style anchor intact, and the r8 note records
that every variant carrying three or more species tags came back at 62 tokens
WITH THE ANCHOR DELETED. So the number this script prints as `headroom` is the
budget the founder's definition may spend before it starts eating the anchor, and
a headroom of 0 means his pick cannot be longer than r8's without a re-measure.

MEASUREMENT IS BOX-ONLY AND THAT IS NOT A PREFERENCE. sd_prompt.compress() sizes
the positive with _token_estimate(), which falls back to a calibrated word-count
approximation when transformers is absent — and the Mac has no transformers. The
fallback does not merely report a different NUMBER; compress() drops trailing
SENTENCES until the estimate fits, so the same draft compresses to a different
positive prompt on the two machines. This script asserts a real CLIP tokenizer is
present and refuses to run without one.
"""
import argparse
import re
import sys
import time
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# ---- the r8 recipe, byte-for-byte from pipeline/render_b13r8.py -------------
NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, "
       "low quality, blurry, extra limbs, deformed, jpeg artifacts, "
       "realistic skin texture")
BASE = "cagliostrolab/animagine-xl-3.1"
LICENCE = "CreativeML Open RAIL++-M (use restrictions travel; D15)"
SEED = 20260719
W, H, STEPS, CFG = 832, 1216, 40, 7.5
DROP_NEG = "tall tree"
# r6's nine fusion tags plus the two species tags r8 bought — split into the two
# halves they actually are, because they answer two different failures and only
# one of them can happen on a given beat.
#
# FUSION is the plant/humanoid collision: it exists because a goblin and a sapling
# in one frame came back as a plant girl. On beat 06, a guard reading a clipboard
# indoors of nothing, those nine tags spend ~20 of 77 negative tokens forbidding a
# collision that has no second object to collide with — and the budget they spend
# is the budget the founder's goblin definition needs. SPECIES is `female goblin,
# elf`, the two Danbooru names of what he rejected, and that risk travels with the
# goblin wherever he goes.
#
# r8 sent both halves as one string. That was right for beat 13, which has a
# goblin AND a sapling. Applying it unchanged to a guard beat is cargo-culting a
# recipe past the conditions it was measured under, so the tier is per-beat and
# the drafts file says which and why.
FUSION_NEG = ("leaf on head, plant girl, alraune, monster girl, flower on head, "
              "head wreath, hair ornament, leaf hair ornament, plant hair")
SPECIES_NEG = "female goblin, elf"
EXTRA_NEG_TIERS = {
    "full": FUSION_NEG + ", " + SPECIES_NEG,   # r8's exact string, byte-for-byte
    "species": SPECIES_NEG,
    "guard": "",
}
ANCHOR_TAIL = "very aesthetic"
GOBLIN_SLOT = "{{GOBLIN}}"
GOBLIN_DEFAULT = "green skin, plump"

NODE = "genomes/sapling/nodes/002b-first-citizen"

# The person nouns proven to bind. d17a685: "`no humans` does not bind and `no
# person` does". A plant-only plate must negate the singulars, not the plural.
SINGULARS = ("woman", "girl", "boy", "child", "person")


def load_drafts(path: Path) -> dict:
    """beat -> dict(slug, tag, kind, gist, authored). Deliberately a tiny parser
    rather than a yaml dependency: the box venv is a render environment and this
    file is ours, not a schema anybody else writes."""
    import yaml
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {int(k): v for k, v in data["beats"].items()}


def apply_variant_declaration(d: dict, variant: str) -> dict:
    """Return the beat dict as it applies TO ONE VARIANT.

    Only one thing travels per-variant today: `object_sheet_variants`, the
    explicit list of draft keys on this beat that are OBJECT sheets and so
    declare no count tag at all (see the count guard in `check`). A variant named
    there — and only a variant named there — gets `declares_no_count: True`.

    Naming is a deliberate authoring act. An unlisted variant, a missing list and
    an empty list all leave the dict untouched, so every draft written before this
    existed is measured under exactly the rule it was measured under before.
    """
    if variant in (d.get("object_sheet_variants") or []):
        return dict(d, declares_no_count=True)
    return d


def strip_term(neg: str, term: str) -> tuple:
    parts = [p.strip() for p in neg.split(",")]
    kept = [p for p in parts if p.lower() != term.lower()]
    return ", ".join(kept), len(parts) - len(kept)


def check(beat: int, d: dict, authored: str, sd, verbose: bool = True) -> dict:
    """Compress, build the negative, measure on the real CLIP, and run every
    dialect assertion this week paid for. Returns a row; never raises."""
    compress, beat_negative, negative_tokens, count_tag = (
        sd.compress, sd.beat_negative, sd.negative_tokens, sd.count_tag)

    extra = EXTRA_NEG_TIERS[d["extra_neg"]]
    pos, dropped = compress(authored)
    warns = []
    neg_full = beat_negative(NEG, authored, extra, warn=warns.append)
    neg, removed = strip_term(neg_full, DROP_NEG)
    neg_parts = [p.strip() for p in neg.split(",")]

    pos_tok = negative_tokens(pos)
    neg_tok = negative_tokens(neg)
    tag = count_tag(authored)

    faults = []
    if ANCHOR_TAIL not in pos:
        faults.append(f"STYLE ANCHOR MISSING (`{ANCHOR_TAIL}` not in positive)")
    if dropped:
        faults.append(f"POSITIVE DROPPED: {' | '.join(dropped)}")
    # THE COUNT GUARD, AND ITS ONE EXEMPTION.
    # The rule is `derived == declared`, and it earns its keep: it is what caught
    # ep2-b06-plate-0815 on 2026-08-14, whose draft opened "Two adult guard men"
    # under a `1boy` beat slot. That path is NOT weakened below and must never be.
    #
    # THE EXEMPTION IS FOR OBJECT SHEETS AND NOTHING ELSE. Every beat slot in this
    # file declares a person because every BEAT has one, so an object-reference
    # sheet — a prop drawn alone, with `no people` fenced, precisely so nothing
    # competes with it for the composition — can never satisfy the slot it borrows.
    # That mismatch is structural, not a typo, so a draft may declare that it has
    # NO count, and `declares_no_count: true` is that declaration.
    #
    # WHAT IT MUST NEVER COVER:
    #   * it is set per-VARIANT, by naming the variant in `object_sheet_variants`
    #     (see apply_variant_declaration) — never beat-wide, or one careless draft
    #     would disarm the guard for every other draft on the same beat;
    #   * an OMITTED key is not a declaration. Absent means "this beat's slot
    #     applies", which is the old behaviour, byte for byte;
    #   * it permits ONE outcome only — derived EMPTY. A draft that declares no
    #     count and then derives `1boy` has a person in it and still fails, so the
    #     exemption can never launder a miscounted figure.
    if d.get("declares_no_count") is True:
        if tag:
            faults.append(f"draft declares NO count (object sheet) but derives "
                          f"{tag!r} — a person reached a sheet meant to hold only "
                          "the prop")
    elif tag != d["tag"]:
        faults.append(f"COUNT TAG is {tag!r}, draft declares {d['tag']!r}")
    if "text" not in neg_parts:
        faults.append("'text' is NOT negated (suppressed_negatives regression)")
    if "humans" in neg_parts:
        faults.append("'humans' reached the negative — it does not bind (d17a685); "
                      "use the singulars")
    if re.search(r"\bno\s+humans\b", authored, re.I):
        faults.append("draft still says `no humans`")
    # THE PERSON-SINGULARS RULE DOES NOT APPLY TO THIS WAVE AND SAYING SO IS THE
    # POINT. `no woman, no girl, no boy, no child, no person` is the plant-only
    # plate's defence — it is how 002b beat 01 returned 0 people in 4 of 4 — and
    # every one of this wave's 15 beats is PEOPLED. Negating `boy` or `person`
    # here would forbid the subject. So the rule inverts: the assertion is that
    # these terms are ABSENT, not present.
    # ONLY on beats that declare a person. The comment above was written when every
    # beat in the wave was peopled; beats 12/18/21 are plant-only, and for them the
    # person-singulars block is the CORRECT defence, not a self-negation -- it is how
    # 002b beat 01 returned 0 people in 4 of 4. `tag` is the predicate: an empty count
    # tag means the draft declares nobody in frame.
    selfneg = ([t for t in ("boy", "person", "man", "male") if t in neg_parts]
               if d.get("tag") else [])
    if selfneg:
        faults.append(f"peopled beat negates its own subject: {selfneg} — the "
                      "person-singulars block belongs on plant-only plates only")
    if GOBLIN_SLOT in pos or GOBLIN_SLOT in neg:
        faults.append("goblin slot survived into the sent prompt — not filled")
    # A gaze tag describes a subject looking out of the frame; on a plate with no
    # character it invents one. No beat here is empty, so this is a tripwire for a
    # later edit rather than a live check.
    if not tag and re.search(r"looking at viewer|eye contact", pos, re.I):
        faults.append("gaze tag on a plate that declares no character")
    if d["extra_neg"] == "full" and "plant hair" not in neg_parts:
        faults.append("fusion tier requested but its tags did not survive the "
                      "budget — the collision it exists for is unguarded")
    if d["kind"] in ("goblin", "two-subject") and "female goblin" not in neg_parts:
        faults.append("goblin in frame but `female goblin` did not survive the "
                      "budget — this is the exact failure he ordered fixed")

    row = dict(beat=beat, slug=d["slug"], kind=d["kind"], tag=tag,
               pos=pos, neg=neg, neg_full=neg_full, removed=removed,
               pos_tok=pos_tok, neg_tok=neg_tok, headroom=77 - pos_tok,
               warns=warns, faults=faults, authored=authored)

    if verbose:
        print(f"\n== beat {beat:02d} {d['slug']} [{d['kind']}] — {d['gist']}",
              flush=True)
        print(f"   AUTHORED: {authored}", flush=True)
        print(f"   POS: {pos}", flush=True)
        print(f"   NEG(sent): {neg}", flush=True)
        print(f"   positive tokens (real CLIP): {pos_tok}/77   "
              f"headroom for the goblin definition: {77 - pos_tok}", flush=True)
        print(f"   negative tokens: recipe {negative_tokens(neg_full)} -> "
              f"sent {neg_tok} (budget 77)", flush=True)
        print(f"   count tag: {tag!r} (draft declares {d['tag']!r})", flush=True)
        print(f"   STYLE ANCHOR PRESENT: {ANCHOR_TAIL in pos}", flush=True)
        print(f"   'text' negated: {'text' in neg_parts}", flush=True)
        print(f"   scale negatives: {'mature tree' in neg_parts}   "
              f"'tall tree' removed: {removed}", flush=True)
        print(f"   person singulars in negative: "
              f"{[t for t in SINGULARS if t in neg_parts]}", flush=True)
        for w in warns:
            print(f"   NEGWARN: {w}", flush=True)
        for f in faults:
            print(f"   !! {f}", flush=True)
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="repo checkout the box reads")
    ap.add_argument("--drafts", default=None, help="wave-drafts.yaml")
    ap.add_argument("--beat", type=int, default=None, help="one beat, else all")
    ap.add_argument("--goblin-def", default=GOBLIN_DEFAULT,
                    help="tags that fill {{GOBLIN}}; default is r8's measured pair")
    ap.add_argument("--dry", action="store_true", help="measure, draw nothing")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    sys.path.insert(0, str(root / "pipeline"))
    import sd_prompt as sd                                            # noqa: E402

    if sd._clip_tokenizer() is None:
        print("!! no CLIP tokenizer in this environment. Every number below "
              "would be an estimate AND compress() would drop different "
              "sentences than the box does. Refusing.", flush=True)
        return 9

    drafts_path = Path(a.drafts) if a.drafts else Path(__file__).with_name(
        "wave-drafts.yaml")
    drafts = load_drafts(drafts_path)
    beats = [a.beat] if a.beat else sorted(drafts)

    origin = ("  (r8's own pair — this is the MEASURED WORST CASE, not the "
              "founder's definition)" if a.goblin_def == GOBLIN_DEFAULT else
              "  (supplied on the command line)")
    print(f"WAVE 002b goblin, round-next — {len(beats)} beat(s)", flush=True)
    print(f"goblin definition filling {GOBLIN_SLOT}: {a.goblin_def!r}{origin}",
          flush=True)

    rows = []
    for b in beats:
        d = drafts[b]
        authored = d["authored"]
        if GOBLIN_SLOT not in authored and d["kind"] != "guard":
            print(f"\n!! beat {b:02d} has a goblin in frame but no {GOBLIN_SLOT} "
                  "marker — his definition would have nowhere to go", flush=True)
        if GOBLIN_SLOT in authored and d["kind"] == "guard":
            print(f"\n!! beat {b:02d} is a guard beat carrying a goblin slot",
                  flush=True)
        rows.append(check(b, d, authored.replace(GOBLIN_SLOT, a.goblin_def), sd))
        # a beat may carry a second phrasing whose count tag is the open question
        if d.get("authored_untagged"):
            alt = dict(d, tag="", slug=d["slug"] + "*untagged")
            print(f"\n   -- beat {b:02d} SECOND VARIANT, the no-count-tag "
                  "phrasing the module docstring argues for --", flush=True)
            rows.append(check(b, alt,
                              d["authored_untagged"].replace(GOBLIN_SLOT,
                                                             a.goblin_def), sd))

    bad = [r for r in rows if r["faults"]]
    print("\n" + "=" * 72, flush=True)
    print(f"{'beat':>4} {'slug':<18} {'kind':<11} {'tag':<9} {'pos':>4} "
          f"{'head':>5} {'neg':>4}  faults", flush=True)
    for r in rows:
        print(f"{r['beat']:>4} {r['slug']:<18} {r['kind']:<11} {r['tag']:<9} "
              f"{r['pos_tok']:>4} {r['headroom']:>5} {r['neg_tok']:>4}  "
              f"{len(r['faults']) or ''}", flush=True)
    print(f"\n{len(rows)} beats measured, {len(bad)} with faults", flush=True)
    if bad:
        print("BEATS WITH FAULTS: " + ", ".join(f"{r['beat']:02d}" for r in bad),
              flush=True)
        return 1
    if a.dry:
        print(f"\nDRY OK — {len(rows)} beats x 4 seeds = {len(rows) * 4} frames, "
              "nothing drawn", flush=True)
        return 0

    print("\n!! RENDERING IS GATED. This wave does not fire until the founder "
          "defines the goblin (taste ledger record 32) — and then it fires ONE "
          "SAMPLE first, not fifteen. Re-run with --beat <n> once he has.",
          flush=True)
    return 8


if __name__ == "__main__":
    sys.exit(main())
