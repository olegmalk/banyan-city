#!/usr/bin/env python3
"""002b beat 5 — ROUND 5, THE PATROL. The register words come back. 2026-08-09.

WHAT r4 FOUND, WHICH IS THIS ROUND'S WHOLE DIRECTION. r4 sent
`WAVE-PREP-0810-drafts.yaml` beat 5 verbatim and was rejected on every axis
(ledger `ep2-b05-r4-sample`, commit 5f103b0). Its finding was not "the words did
not work" — it was that the draft had SOLD two of the founder's own words to buy
the count tag. His pass condition is "they are supposed to be round and harmless
in a morning field"; the draft deleted `harmless`, one of those two words, and
`shapes`, whose function in r3's sentence was to decline to say *man*. It then
added `men` — a male-human noun — in the same round. Both edits pull the same
way, and the frames came back knights in matched plate, dark-fantasy 4 of 4.

WHAT r4 PROVED AND THIS ROUND KEEPS. `2boys` bound gender: no girl and no child
clean 4 of 4, which r3 could not claim. That is the one unambiguous win on this
beat in five rounds and it is not given back.

THE THREE CHANGES, AND WHY IT IS NOT "RESTORE THE WORDS AND RE-RENDER". Putting
`round harmless shapes` back on its own would be r3, and r3 IS A KNOWN FAILURE:
it already contained `round harmless shapes` and `an empty morning field`
verbatim, already had the style anchor intact, and still returned a dark forest
of dangerous figures on 4 of 4. Words alone have been tried on this beat. So:

    1. `harmless` and `shapes` RETURN, and `men` GOES. The tag is kept anyway —
       see the next paragraph, this is the only reason this file exists.
    2. `plump` is added: a Danbooru corpus tag for the roundness his sentence
       asks for. Record 39's finding, one beat over, is that a tag beats prose
       3 of 4 on this checkpoint. `round` stays as prose beside it.
    3. Defect 3's eight prescribed negatives are sent VERBATIM — `dark fantasy,
       night, glowing eyes, hood, weapon, sword, knife, armor plate` — the
       costed, untried lever that r4 deliberately left on the table. Measured on
       this box: 19 tokens against 32 free in r4's negative. It fits.

THE COUNT TAG IS INJECTED SCRIPT-SIDE, AND THAT IS A DELIBERATE, DECLARED
TRANSFORM. `_tag_from_clause` DERIVES the tag from the first comma-clause and
tests `_MALE` before `_OTHER`. r4 got `2boys` because it typed the word `men`;
delete `men` and the same code returns `2others`, which is the indeterminate
humanoid tag three rounds of failures came out of. Keeping the tag and dropping
the word are therefore incompatible through the derived path — so this round
takes the tag AFTER `compress()` and rewrites the leading token, exactly the
script-level transform `render_b06r5.py` used on node 001 beat 6 (and which
commit 1aab710 identified as the actual mechanism behind that round's clean
frames). The prose never says a male noun; the model still receives `2boys`.
Trap 4 asserts BOTH halves: derived must be `2others`, sent must be `2boys`.

WHAT IS **NOT** IN THIS ROUND, SAID OUT LOUD. Defect 3 also prescribes
`chibi-proportioned` and `comedic` leading the guard clause, and `chibi` is
legal here — the `no chibi / no mascot / no creature / no face` block is beat
01's, written for a PLANT beat after three of four candidates drew a mascot
creature as the sapling, and beat 5 carries no plant. It is left out anyway.
Defect 4 on the same page is the founder's "twenty different shows" complaint,
and the beats it names as failures are the "flat cartoon mascots" — `chibi` is
the heaviest tag in the vocabulary toward exactly that, so sending it in the
same round as the register fix risks trading a dark-fantasy failure for a
mascot failure he has already named, with no way to attribute either. Measured
cost on this box is 2 tokens, and the positive has room. It stays a costed,
untried lever for r6 rather than a fourth simultaneous variable.

SEEDS ARE HELD FOR THE THIRD ROUND RUNNING — r3's own k=4..7. Same noise as the
r3 sheet he rejected and the r4 sheet he rejected, so the words remain the only
variable across all three. b13's convention from r4 through r9.

SHOTS.MD IS NOT EDITED. The r5 wording is not canon and the founder has not read
it; it is injected script-side and the r3 fence is asserted byte-for-byte first
(trap 1), so a stale checkout cannot start.

MEASURE ON THE BOX OR NOT AT ALL. `sd_prompt._token_estimate` falls back to a
prose approximation without `transformers` and over-counts near 77 — it read
b13's r8 as 61 tokens WITH THE ANCHOR DROPPED, a false failure of that beat's
own gate. This script exits 8 rather than report an estimate as a measurement.

Usage:
    python render_b05r5.py --root C:\\banyan-farm\\banyan-city --measure
    python render_b05r5.py --root C:\\banyan-farm\\banyan-city --dry
    python render_b05r5.py --root C:\\banyan-farm\\banyan-city
"""
import argparse
import hashlib
import sys
import time
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, "
       "low quality, blurry, extra limbs, deformed, jpeg artifacts, "
       "realistic skin texture")
BASE = "cagliostrolab/animagine-xl-3.1"
LICENCE = "CreativeML Open RAIL++-M (use restrictions travel; D15)"
SEED = 20260719
W, H, STEPS, CFG = 832, 1216, 40, 7.5
DROP_NEG = "tall tree"
EXPECT_DROP = 0
CANDIDATE_SET = "r5"
QUEUE_ENTRY = "ep2-b05-r5-register-0810"
TASK = "ep2-b05-r5-register-0810"
BEAT = 5

# the tag the derived path returns for this round's prose, and the tag actually
# sent. They differ ON PURPOSE and trap 4 asserts both.
DERIVED_TAG = "2others"
EXPECT_TAG = "2boys"
R3_TAG = "2others"
R4_TAG = "2boys"

SEED_K0 = SEED + BEAT
FIRST_K = 4

# defect 3's prescribed negatives, verbatim off PROVISIONAL-PICKS-0809.md.
# 19 tokens measured on this box's real CLIP against 32 free in r4's negative.
EXTRA_NEG = ("dark fantasy, night, glowing eyes, hood, weapon, sword, knife, "
             "armor plate")
EXTRA_NEG_TIER = "guard-defect3"

ANCHOR = ("Wide static camera, long soft shadows, cinematic lighting, detailed, "
          "newest, masterpiece, best quality, very aesthetic")

# THE r3 FENCE, BYTE-FOR-BYTE, from genomes/.../002b-first-citizen/shots.md.
# Control and staleness guard in one.
AUTHORED_R3 = (
    "Two patrol guards drawn as round harmless shapes in mismatched ill-fitting "
    "armor jog into frame and halt, heads turning as they scan an empty morning "
    "field; one carries a clipboard made of tree bark. Wide static camera, long "
    "soft shadows, cinematic lighting, detailed, newest, masterpiece, best "
    "quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, "
    "no text.")

# THE r4 DRAFT, BYTE-FOR-BYTE, from WAVE-PREP-0810-drafts.yaml beat 5 — the
# sheet he rejected. Rebuilt in this run as the second control.
AUTHORED_R4 = (
    "Two round guard men in mismatched ill-fitting armor jog into frame and "
    "halt, scanning an empty morning field, one carrying a bark clipboard. Wide "
    "static camera, long soft shadows, cinematic lighting, detailed, newest, "
    "masterpiece, best quality, very aesthetic No girl, no child. No "
    "photorealism, no 3D render look. 9:16 vertical, no text.")

# THIS ROUND. r3's subject clause with `harmless` and `shapes` restored, `patrol`
# traded for the corpus tag `plump`, r4's tightened action clauses and its
# `No girl, no child.` kept. No male noun anywhere — the tag is injected.
AUTHORED_R5 = (
    "Two plump guards drawn as round harmless shapes in mismatched ill-fitting "
    "armor jog into frame and halt, scanning an empty morning field, one "
    "carrying a bark clipboard. Wide static camera, long soft shadows, "
    "cinematic lighting, detailed, newest, masterpiece, best quality, very "
    "aesthetic No girl, no child. No photorealism, no 3D render look. 9:16 "
    "vertical, no text.")

# WHAT r3 ACTUALLY SENT, from takes/stills/05-the-patrol-r3-s0.png.meta.yaml.
R3_POS_SENT = (
    "2others, two patrol guards drawn as round harmless shapes in mismatched "
    "ill-fitting armor jog into frame and halt, heads turning as they scan an "
    "empty morning field; one carries a clipboard made of tree bark. Wide "
    "static camera, long soft shadows, cinematic lighting, detailed, newest, "
    "masterpiece, best quality, very aesthetic")
R3_NEG_SENT = (
    "photorealistic, 3d render, abstract, text, watermark, signature, low "
    "quality, blurry, extra limbs, deformed, jpeg artifacts, realistic skin "
    "texture, photorealism, text")

# every term this round adds to the negative against the r3 control: r4's two,
# plus defect 3's eight. All ten must survive fit_negative's 77-token trim.
EXPECT_NEG_ADDS = ("girl", "child", "dark fantasy", "night", "glowing eyes",
                   "hood", "weapon", "sword", "knife", "armor plate")

NOTE = (
    'round 5, THE REGISTER WORDS RETURN. r4 was rejected on every axis and its '
    'finding is this round\'s direction: the draft sold `harmless` and `shapes` '
    '— one of the two words in the founder\'s pass condition, and the word that '
    'declined to say *man* — to buy the count tag, then added `men` in the same '
    'round, and came back knights in matched plate. THREE CHANGES. (1) '
    '`harmless` and `shapes` return and `men` goes, while `2boys` is KEPT: r4 '
    'proved that tag binds gender (no girl / no child clean 4 of 4, which r3 '
    'could not claim). Those are incompatible through the derived path — delete '
    '`men` and _tag_from_clause returns `2others` — so the tag is rewritten '
    'AFTER compress(), the same declared script-level transform render_b06r5.py '
    'used, and trap 4 asserts derived=2others AND sent=2boys. (2) `plump` is '
    'added as a corpus tag for the roundness his sentence asks for, per record '
    '39\'s tag-beats-prose finding one beat over. (3) Defect 3\'s eight '
    'prescribed negatives go in VERBATIM — the costed lever r4 left on the '
    'table — measured at 19 tokens against 32 free. WORDS ALONE WERE NOT AN '
    'OPTION: r3 already sent `round harmless shapes` and `an empty morning '
    'field` with the anchor intact and still returned a dark forest, so '
    'restoring the words without the tag and the negatives would have re-run a '
    'known failure. `chibi` is LEGAL here (the no-chibi block is beat 01\'s, '
    'written for a plant beat) and is still left out: defect 4 names flat '
    'cartoon mascots as their own failure, so it stays a costed untried lever '
    'at 2 measured tokens rather than a fourth variable. Seeds are r3\'s own '
    'four, held for the third round running, so the words remain the only '
    'variable across the two sheets he has rejected.')

PRESCRIPTION_NOTE = (
    "Defect 3 prescribes `round, harmless, comedic, chibi-proportioned, "
    "daylight` leading the guard clause with `dark fantasy, night, glowing "
    "eyes, hood, weapon, sword, knife, armor plate` negated. THE EIGHT "
    "NEGATIVES ARE SENT VERBATIM THIS ROUND. Of the positive half, `round` and "
    "`harmless` are present; `comedic` (2 tokens) and `chibi-proportioned` "
    "(`chibi`, 2 tokens) are measured, affordable and deliberately NOT sent, "
    "so that a result here is attributable to the register fix rather than to "
    "a style tag that pulls toward defect 4's flat cartoon mascots.")

ARMOR_RISK = (
    "PRE-REGISTERED BEFORE A STEP. `armor plate` is negated while the positive "
    "still carries the founder's own `mismatched ill-fitting armor`. CLIP does "
    "not compose negations, so the negative may suppress armor generally and "
    "return unarmoured guards, which the script does not describe. The term is "
    "sent anyway because defect 3 prescribes it verbatim and the picks page is "
    "the founder's own diagnosis; this note exists so that if the armor "
    "vanishes, the cause is already on the record rather than discovered after "
    "the fact.")


def sidecar(png: Path, *, seed: int, pos: str, neg: str, neg_full: str,
            secs: float, warns: list, task: str, shots_sha: str,
            pos_tokens: int, neg_tokens: int, r3_pos_tokens: int,
            r4_pos_tokens: int, derived_pos: str, out_dir: Path) -> None:
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())
    lines = ["# Still provenance (7.2), written AT RENDER TIME by render_b05r5.py",
             f"# on the rtx5090 ({out_dir}).",
             "# The negative below is what the model actually saw. The recipe's own",
             "# negative, before this script's one deliberate removal, was:",
             f"#   {neg_full}"]
    lines += [f"#   NEGWARN: {w}" for w in warns]
    body = ["platform: local-gpu (rtx5090)",
            f"model: {BASE}",
            f"model_licence: {LICENCE}",
            f"shot_beat: {BEAT}",
            f"size: {W}x{H}",
            f"steps: {STEPS}",
            f"guidance: {CFG}",
            f"seed: {seed}",
            "seeds_in_batch: 4",
            f"task: {task}",
            f"queue_entry: {QUEUE_ENTRY}",
            f"render_round: {CANDIDATE_SET}",
            f"candidate_set: {CANDIDATE_SET}",
            f"negative_terms_removed: none ({DROP_NEG} not present)",
            f"count_tag: {EXPECT_TAG}",
            f"count_tag_derived: {DERIVED_TAG}",
            f"count_tag_r3: {R3_TAG}",
            f"count_tag_r4: {R4_TAG}",
            "count_tag_injected: true",
            "count_tag_note: >-",
            block("INJECTED SCRIPT-SIDE, NOT DERIVED, AND THE PROSE CONTAINS NO "
                  "MALE NOUN. sd_prompt._tag_from_clause tests _MALE before "
                  "_OTHER on the first comma-clause: r4's `Two round guard men` "
                  "hit `men` and returned 2boys, and deleting `men` — which is "
                  "this round's point, it composed with the armor into a knight "
                  "— returns 2others, the indeterminate humanoid tag the "
                  "earlier failures came out of. Keeping r4's one proven win "
                  "while dropping the word that caused its failure is therefore "
                  "impossible through the derived path. The leading tag is "
                  "rewritten after compress(), the same declared transform "
                  "render_b06r5.py used on node 001 beat 6 and that commit "
                  "1aab710 identified as the real mechanism behind that round's "
                  "clean frames. Derived and sent are both asserted at run "
                  "time."),
            f"positive_before_tag_injection: {derived_pos[:120]}…",
            f"extra_negative_tier: {EXTRA_NEG_TIER}",
            "extra_negative_tier_note: >-",
            block(PRESCRIPTION_NOTE),
            "armor_negative_risk: >-",
            block(ARMOR_RISK),
            f"shots_md_sha256: {shots_sha}",
            "shots_md_edited: false",
            "authored_source: >-",
            block("this lane, from the r4 finding (ledger ep2-b05-r4-sample, "
                  "commit 5f103b0). NOT shots.md, NOT canon and NOT the "
                  "WAVE-PREP draft — r4 rendered that draft verbatim and it was "
                  "rejected. Injected script-side; the r3 fence is asserted "
                  "byte-for-byte before a step is spent."),
            f"authored_r5_sha256: {hashlib.sha256(AUTHORED_R5.encode()).hexdigest()}",
            "tokenizer: openai/clip-vit-large-patch14 (transformers, on the box)",
            f"positive_tokens: {pos_tokens}",
            f"positive_tokens_r3_control: {r3_pos_tokens}",
            f"positive_tokens_r4_control: {r4_pos_tokens}",
            f"negative_tokens_sent: {neg_tokens}",
            "negative_delta_from_r3: girl, child, dark fantasy, night, "
            "glowing eyes, hood, weapon, sword, knife, armor plate",
            "negative_delta_from_r4: dark fantasy, night, glowing eyes, hood, "
            "weapon, sword, knife, armor plate",
            "r3_control_reproduced: true",
            "r4_control_reproduced: true",
            "controls_note: >-",
            block("BOTH rejected rounds are rebuilt from this checkout in the "
                  "same run on the same tokenizer — r3 asserted byte-for-byte "
                  "against its recorded sidecars, r4 against the draft text it "
                  "rendered — so the two deltas below are one measurement "
                  "rather than three instruments."),
            "anchor_intact: true",
            "anchor_note: >-",
            block("Intact on r3, on r4 and here. Beat 5 was never one of the "
                  "eleven beats compress() shed the style sentence from, so the "
                  "b13-r4 anchor finding is not and has never been the "
                  "mechanism available on this beat."),
            "seeds_held_from: >-",
            block("r3's own four (k=4..7 of this beat's series), held for the "
                  "third round running. Same noise as both sheets the founder "
                  "rejected, so the wording stays the only variable."),
            "provisional: true",
            "approved: false",
            "recipe_inherited_from: >-",
            block("round 4, takes/stills/05-the-patrol-r4-s*.png — model, size, "
                  "steps, cfg, the seed series and the one-term negative "
                  "removal are unchanged from r4, which inherited them from r3 "
                  "and ultimately from node 001 "
                  "takes/stills/15-something-s-coming-r3-s1.png, the ONE SAMPLE "
                  "the founder passed on 2026-08-08."),
            f"wall_seconds: {secs:.0f}",
            "cost_usd: 0",
            "note: |-", block(NOTE),
            "prompt: |-", block(pos),
            "negative: |-", block(neg)]
    png.with_suffix(".png.meta.yaml").write_text("\n".join(lines + body) + "\n",
                                                 encoding="utf-8")


def strip_term(neg: str, term: str) -> tuple:
    parts = [p.strip() for p in neg.split(",")]
    kept = [p for p in parts if p.lower() != term.lower()]
    return ", ".join(kept), len(parts) - len(kept)


def inject_tag(pos: str, derived: str, target: str):
    """Rewrite compress()'s leading count tag. Returns None if it is not there."""
    head = derived + ", "
    if not pos.startswith(head):
        return None
    return target + ", " + pos[len(head):]


def build(authored: str, compress, beat_negative, extra: str) -> tuple:
    """The full prompt pair for one authored fence, through the real code path."""
    pos, dropped = compress(authored)
    warns = []
    neg_full = beat_negative(NEG, authored, extra, warn=warns.append)
    neg, removed = strip_term(neg_full, DROP_NEG)
    return pos, neg, neg_full, dropped, warns, removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--measure", action="store_true",
                    help="print the r3 and r4 controls beside r5 on this box's "
                         "real tokenizer, draw nothing")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "pipeline"))
    from generate_shots import parse_shots                          # noqa: E402
    from sd_prompt import (beat_negative, compress,                 # noqa: E402
                           negative_tokens, _clip_tokenizer, _tag_from_clause)

    node = root / "genomes/sapling/nodes/002b-first-citizen"
    shots_path = node / "shots.md"
    out = Path(__file__).resolve().parent / "out"
    out.mkdir(exist_ok=True)

    raw = shots_path.read_bytes()
    shots_sha = hashlib.sha256(raw).hexdigest()
    shots = {s["num"]: s for s in parse_shots(raw.decode("utf-8"))}
    s = shots[BEAT]
    authored_r3 = s["prompt"]

    if _clip_tokenizer() is None:
        print("!! NO CLIP TOKENIZER — transformers is not importable, so every "
              "token count here would be the estimator that over-counts near "
              "the 77 boundary. Run this on the box's venv; stopping.",
              flush=True)
        return 8

    # trap 1: the fence must still be r3's, byte for byte. This round does not
    # edit shots.md, so a stale checkout would render the wrong control.
    if authored_r3 != AUTHORED_R3:
        print("!! shots.md Beat 5 is not the r3 fence, byte for byte — the "
              "checkout is stale or the fence moved, and neither control below "
              "would mean anything.\n"
              f"   expected: {AUTHORED_R3}\n"
              f"   found:    {authored_r3}\n   stopping.", flush=True)
        return 4

    derived_pos, neg, neg_full, dropped, warns, removed = build(
        AUTHORED_R5, compress, beat_negative, EXTRA_NEG)
    cpos, cneg, _, cdropped, _, _ = build(AUTHORED_R3, compress, beat_negative, "")
    c4pos, c4neg, _, _, _, _ = build(AUTHORED_R4, compress, beat_negative, "")

    # the one deliberate script-level transform in this round.
    derived_tag = _tag_from_clause(AUTHORED_R5.split(".")[0].split(",")[0])
    pos = inject_tag(derived_pos, DERIVED_TAG, EXPECT_TAG)

    seeds = [SEED_K0 + (FIRST_K + i) * 1000 for i in range(4)]
    print(f"\n== beat {BEAT} {s['slug']} [{CANDIDATE_SET}] "
          f"seeds {', '.join(str(x) for x in seeds)}", flush=True)
    print(f"   shots.md: {shots_path}", flush=True)
    print(f"   sha256:   {shots_sha}  (NOT edited by this round)", flush=True)
    print(f"   AUTHORED(r3 fence): {AUTHORED_R3}", flush=True)
    print(f"   AUTHORED(r4 draft): {AUTHORED_R4}", flush=True)
    print(f"   AUTHORED(r5 this):  {AUTHORED_R5}", flush=True)
    print(f"   r5 sha256: "
          f"{hashlib.sha256(AUTHORED_R5.encode()).hexdigest()}", flush=True)
    print(f"   POS(derived): {derived_pos}", flush=True)
    print(f"   POS(sent):    {pos}", flush=True)
    print(f"   NEG(recipe):  {neg_full}", flush=True)
    print(f"   NEG(sent):    {neg}", flush=True)

    if pos is None:
        print(f"   !! compress() did not open with `{DERIVED_TAG}, ` — the tag "
              f"injection has nothing to rewrite and the round would send an "
              f"untagged prompt. POS opens `{derived_pos[:48]}`; stopping.",
              flush=True)
        return 11

    pos_tokens = negative_tokens(pos)
    neg_tokens = negative_tokens(neg)
    ctok = negative_tokens(cpos)
    c4tok = negative_tokens(c4pos)
    print(f"   positive tokens: {pos_tokens} (budget 77)", flush=True)
    print(f"   negative tokens: recipe {negative_tokens(neg_full)} -> "
          f"sent {neg_tokens} (budget 77)", flush=True)
    for w in warns:
        print(f"   NEGWARN: {w}", flush=True)

    # trap 3: both controls must reproduce from THIS checkout.
    if cpos != R3_POS_SENT or cneg != R3_NEG_SENT:
        print("!! THE r3 CONTROL DOES NOT REPRODUCE from this checkout, so no "
              "comparison in this round is controlled.\n"
              f"   pos match: {cpos == R3_POS_SENT}\n"
              f"   neg match: {cneg == R3_NEG_SENT}\n"
              f"   rebuilt pos: {cpos}\n   rebuilt neg: {cneg}\n   stopping.",
              flush=True)
        return 10
    if not c4pos.startswith(R4_TAG + ","):
        print(f"!! THE r4 CONTROL does not open `{R4_TAG}` — it rebuilt as "
              f"`{c4pos[:48]}`, so the r4 delta below is not measured against "
              f"the round he rejected; stopping.", flush=True)
        return 10

    if a.measure:
        print("\n-- r3 CONTROL on this same tokenizer --", flush=True)
        print(f"   POS: {cpos}", flush=True)
        print(f"   positive tokens: {ctok}  "
              f"anchor {'INTACT' if cpos.rstrip().endswith(ANCHOR) else 'DROPPED'}"
              f"  dropped={cdropped}", flush=True)
        print(f"   count tag: "
              f"{_tag_from_clause(AUTHORED_R3.split('.')[0].split(',')[0])}",
              flush=True)
        print("\n-- r4 CONTROL on this same tokenizer --", flush=True)
        print(f"   positive tokens: {c4tok}  count tag: "
              f"{_tag_from_clause(AUTHORED_R4.split('.')[0].split(',')[0])}",
              flush=True)
        print("\n-- r5 as configured --", flush=True)
        print(f"   positive tokens: {pos_tokens}  "
              f"anchor {'INTACT' if pos.rstrip().endswith(ANCHOR) else 'DROPPED'}"
              f"  dropped={dropped}", flush=True)
        print(f"   count tag: derived={derived_tag} sent={pos.split(',')[0]}",
              flush=True)
        print(f"   delta r5-r3: {pos_tokens - ctok} tokens on the positive",
              flush=True)
        print(f"   delta r5-r4: {pos_tokens - c4tok} tokens on the positive",
              flush=True)
        print(f"   negative delta vs r3: "
              f"{[t for t in neg.split(', ') if t not in cneg.split(', ')]}",
              flush=True)
        return 0

    # trap 4: BOTH halves of the tag transform. Derived must be the tag the
    # prose earns, sent must be the tag r4 proved. If derived came back 2boys
    # the prose still contains a male noun and this round did not do its job.
    if derived_tag != DERIVED_TAG:
        print(f"   !! DERIVED TAG is `{derived_tag}`, expected "
              f"`{DERIVED_TAG}` — the r5 prose is not male-free, so dropping "
              f"`men` did not actually happen; stopping.", flush=True)
        return 5
    if not pos.startswith(EXPECT_TAG + ","):
        print(f"   !! SENT TAG is not `{EXPECT_TAG}` — POS opens "
              f"`{pos[:40]}`. r4's one proven win would be given back; "
              f"stopping.", flush=True)
        return 5
    # trap 4b: the male noun must really be gone from the prose.
    for word in (" men ", " man ", " men,", " man,"):
        if word in AUTHORED_R5.lower():
            print(f"   !! r5 prose still contains `{word.strip()}` — the whole "
                  f"point of this round; stopping.", flush=True)
            return 5
    # trap 5: every term this round buys must survive the 77-token trim.
    sent_terms = [p.strip().lower() for p in neg.split(",")]
    missing = [t for t in EXPECT_NEG_ADDS if t not in sent_terms]
    if missing:
        print(f"   !! NEGATIVE TERMS DROPPED by the 77-token budget: "
              f"{', '.join(missing)} — defect 3's prescription is this round's "
              f"costed lever and a partial send is not a test of it; stopping.",
              flush=True)
        return 6
    # trap 6: nothing else in the negative may move.
    unexpected = [t for t in sent_terms
                  if t not in [p.strip().lower() for p in cneg.split(",")]
                  and t not in EXPECT_NEG_ADDS]
    if unexpected:
        print(f"   !! UNEXPECTED NEGATIVE TERMS beyond the declared ten: "
              f"{', '.join(unexpected)}; stopping.", flush=True)
        return 9
    # trap 7: the anchor. Intact on r3 and r4; losing it here would change a
    # second variable in the wrong direction.
    if not pos.rstrip().endswith(ANCHOR):
        print(f"   !! STYLE ANCHOR DROPPED — the positive does not end with "
              f"`{ANCHOR}`; stopping.", flush=True)
        return 7
    # trap 8: the founder's two pass-condition words must actually be in the
    # sent positive. Restoring them IS this round.
    for word in ("round", "harmless", "shapes", "plump"):
        if word not in pos.lower():
            print(f"   !! `{word}` is NOT in the sent positive — this round is "
                  f"defined by its presence; stopping.", flush=True)
            return 13
    if removed != EXPECT_DROP:
        print(f"   !! EXPECTED to remove {EXPECT_DROP} x '{DROP_NEG}', removed "
              f"{removed} — stopping so a human decides.", flush=True)
        return 2
    if dropped:
        print(f"   !! POSITIVE DROPPED: {' | '.join(dropped)} — stopping.",
              flush=True)
        return 3

    if a.dry:
        print("\nDRY OK — 1 beat x 4 seeds = 4 frames, nothing drawn", flush=True)
        return 0

    import torch
    from diffusers import StableDiffusionXLPipeline
    t_load = time.time()
    pipe = StableDiffusionXLPipeline.from_pretrained(BASE, torch_dtype=torch.bfloat16,
                                                     use_safetensors=True)
    pipe.to("cuda")
    print(f"MODEL_LOADED cuda/bfloat16 in {time.time() - t_load:.0f}s", flush=True)

    for i, seed in enumerate(seeds):
        g = torch.Generator(device="cpu").manual_seed(seed)
        t0 = time.time()
        img = pipe(prompt=pos, negative_prompt=neg, num_inference_steps=STEPS,
                   guidance_scale=CFG, generator=g, width=W, height=H).images[0]
        f = out / f"{BEAT:02d}-{s['slug']}-{CANDIDATE_SET}-s{i}.png"
        img.save(f)
        secs = time.time() - t0
        sidecar(f, seed=seed, pos=pos, neg=neg, neg_full=neg_full, secs=secs,
                warns=warns, task=TASK, shots_sha=shots_sha,
                pos_tokens=pos_tokens, neg_tokens=neg_tokens, r3_pos_tokens=ctok,
                r4_pos_tokens=c4tok, derived_pos=derived_pos, out_dir=out)
        print(f"   {f.name} seed={seed} {secs:.0f}s  ({i + 1}/4)", flush=True)

    print("\nDONE 4 stills", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
