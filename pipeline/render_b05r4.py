#!/usr/bin/env python3
"""002b beat 5 — ROUND 4, THE PATROL. The guard register. 2026-08-09.

WHY THIS BEAT AND NOT ANOTHER GUARD BEAT, PICKED ON THE PAGE'S OWN COUNT.
PROVISIONAL-PICKS-0809.md diagnoses six guard beats (05, 06, 07, 09, 10, 11 —
beat 08 is a two-subject beat and carries a goblin, so it is gated on the
founder's definition and is NOT in this lane). Counting the faults his verdict
column names, one per clause:

    05 THE PATROL     dark forest · they look dangerous · not round ·
                      not harmless · not a morning field          FIVE
    06 THE CLIPBOARD  serious · armoured men · at night · not funny   four
    09 THE PAUSE      glowing eyes · black helmet · not daylight      three
    10 NO FORM        indoors · back to us · board reads as a screen  three
    11 THEY LEAVE     specks · dusk · a different place entirely      three
    07 CONFISCATE     a hero from another show — "the field is RIGHT"  one

Beat 05 names the most, and it is the only guard beat where all four candidates
took BOTH A2 and A5 to −2. It is also the first guard beat in cut order, so it
is the frame that sets the register the other five are read against.

WHAT THIS ROUND CHANGES, AND IT IS THE DRAFT'S CHANGE, NOT THIS LANE'S. The
authored text is `WAVE-PREP-0810-drafts.yaml` beat 5 verbatim, asserted against
that file at run time (trap 2) so a drifting draft cannot be silently rendered.
Against the r3 fence it moves in four places:

    1. the count tag, which is DERIVED and not typed: `two patrol guards …`
       matches `_OTHER` and returns `2others`; `Two round guard men …` tests
       `_MALE` first and returns `2boys`. This is the r8 finding one beat over —
       the indeterminate-humanoid tag is what three rounds of female demihumans
       came out of — applied to a beat that came back as indeterminate
       dark-fantasy humanoids.
    2. `round` moves to the front of the noun phrase: `two round guard men`
       rather than `two patrol guards drawn as round harmless shapes`.
    3. `No girl, no child.` is appended, which `_NEGATION` lifts into the
       negative as `girl, child`. That is the ONLY negative delta.
    4. the action clauses are tightened (`heads turning as they scan` →
       `scanning`, `a clipboard made of tree bark` → `a bark clipboard`).

WHAT THIS ROUND DOES **NOT** DO, SAID OUT LOUD BECAUSE IT IS THE OBVIOUS
READING OF THE DIAGNOSIS AND THE DRAFT DOES NOT CONTAIN IT. Defect 3 on the
picks page prescribes `round, harmless, comedic, chibi-proportioned, daylight`
leading the guard clause with `dark fantasy, night, glowing eyes, hood, weapon,
sword, knife, armor plate` NEGATED. **None of those negatives are in this
draft**, and the draft additionally DROPS the word `harmless`, which the r3
prompt did carry. So this sample is not a test of defect 3's prescription. It
is a test of the cheaper thing that sits in front of it — whether the count tag
and a tighter subject clause move the register on their own — and if it fails,
the prescribed negatives are a known, costed, untried lever rather than a new
idea. That is stated here so the next round does not rediscover it.

THE r3 CONTROL IS NOT A GUESS, IT IS REBUILT IN THIS RUN. `r3` sent a positive
that ALREADY CONTAINED the style anchor, `round harmless shapes` and `an empty
morning field`, and came back dark-forest and dangerous on 4 of 4. That matters
more than it looks: beat 5 was NOT one of the eleven beats whose anchor
`compress()` was shedding, so the r4-b13 register win — anchor restored, soft
cinematic anime 4 of 4 — CANNOT be the mechanism here, because the anchor was
never missing on this beat. The words were right and the picture was wrong.
This script rebuilds the r3 pair from the current checkout and asserts it
byte-for-byte against the strings recorded in the r3 sidecars (trap 1) before
it will spend a step, so the comparison is measured on one instrument.

SEEDS ARE HELD, NOT ADVANCED, AND THAT INVERTS r3's OWN RULE ON PURPOSE. The
r3 sidecar says it drew the NEXT four of the beat's series (k=4..7) because "no
fault was named on this beat … same words on the same noise is the same
picture, and new noise is the only honest lever a no-axis redraw leaves". A
fault IS named now and the words DO move, so the reasoning runs the other way:
holding k=4..7 makes r4 a direct A/B against the exact four frames he rejected,
and any change in the picture is attributable to the words. This is b13's
convention from r4 through r9 — same four seeds, moving text.

SHOTS.MD IS NOT TOUCHED. The draft is not canon and the founder has not
approved it as script text; it is injected here and the fence is asserted
byte-for-byte against the r3 text first, so a stale checkout cannot start.

MEASURE ON THE BOX OR NOT AT ALL. `sd_prompt._token_estimate` falls back to a
prose approximation when `transformers` is absent and it over-counts near the
77 boundary — on the Mac it read b13's r8 as 61 tokens WITH THE ANCHOR DROPPED,
a false failure of that beat's own gate. This script refuses to run without a
real CLIP tokenizer (exit 8) rather than reporting an estimate as a
measurement, and `--measure` prints the r3 control beside r4 on the SAME
tokenizer so the delta is read off one instrument.

Usage:
    python render_b05r4.py --root C:\\banyan-farm\\banyan-city --measure
    python render_b05r4.py --root C:\\banyan-farm\\banyan-city --dry
    python render_b05r4.py --root C:\\banyan-farm\\banyan-city
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
# r3's sidecar: "negative_terms_removed: none (tall tree not present)". `_SMALL`
# does not fire on this prompt — there is no seedling in a guard beat — so
# SCALE_NEGATIVES is never appended and the removal is a no-op, not a skip.
EXPECT_DROP = 0
CANDIDATE_SET = "r4"
QUEUE_ENTRY = "ep2-b05-r4-guard-0810"
TASK = "ep2-b05-r4-guard-0810"
BEAT = 5
EXPECT_TAG = "2boys"
R3_TAG = "2others"
# k=4..7 of this beat's own series — the four r3 drew, held so the words are the
# only variable. 20260719 + 5 = 20260724 is k=0.
SEED_K0 = SEED + BEAT
FIRST_K = 4
# the extra-negative tier. The draft says `guard`: no goblin in frame, so
# neither r6's nine fusion tags nor r8's two species tags apply — spending ~20
# tokens suppressing a goblin/plant collision that cannot happen would be the
# budget paying for nothing.
EXTRA_NEG = ""
EXTRA_NEG_TIER = "guard"
# the style anchor. It was ALREADY INTACT on r3; this round must not lose what
# r3 had, which is the only thing the b13-r4 finding can contribute here.
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

# THE DRAFT, BYTE-FOR-BYTE, from WAVE-PREP-0810-drafts.yaml beat 5. Held here as
# a constant AND re-read from that file at run time (trap 2), so neither copy can
# move without the other and the round cannot render an unreviewed wording.
DRAFT_PATH = "WAVE-PREP-0810-drafts.yaml"
AUTHORED_R4 = (
    "Two round guard men in mismatched ill-fitting armor jog into frame and "
    "halt, scanning an empty morning field, one carrying a bark clipboard. Wide "
    "static camera, long soft shadows, cinematic lighting, detailed, newest, "
    "masterpiece, best quality, very aesthetic No girl, no child. No "
    "photorealism, no 3D render look. 9:16 vertical, no text.")

# WHAT r3 ACTUALLY SENT, from takes/stills/05-the-patrol-r3-s0.png.meta.yaml.
# The claim that this round is a controlled comparison rests on the current
# checkout reproducing BOTH of these exactly.
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
# the two terms `No girl, no child.` is expected to lift into the negative, and
# the whole of this round's negative delta.
EXPECT_NEG_ADDS = ("girl", "child")

NOTE = (
    'round 4, THE GUARD REGISTER. Beat 5 was picked off PROVISIONAL-PICKS-0809, '
    'which names five faults in its verdict ("it is a dark forest and they look '
    'dangerous; they are supposed to be round and harmless in a morning field") '
    'against four, three, three, three and one on the other five guard beats, '
    'and is the only guard beat with all four candidates at BOTH A2 -2 and A5 '
    '-2. Authored text is WAVE-PREP-0810-drafts.yaml beat 5 verbatim, asserted '
    'against that file before a step. Four changes from the r3 fence: the count '
    'tag moves 2others -> 2boys (derived, not typed — `two patrol guards` '
    'matches _OTHER, `Two round guard men` tests _MALE first), `round` moves to '
    'the front of the noun phrase, `No girl, no child.` is appended and lifts '
    'into the negative, and the action clauses tighten. THE ANCHOR WAS ALREADY '
    'INTACT ON r3, so the b13-r4 register win cannot be the mechanism here: this '
    'beat never lost it, and the words were already right — `round harmless '
    'shapes`, `an empty morning field` — when it came back a dark forest. '
    'DEFECT 3\'S PRESCRIBED NEGATIVES (dark fantasy, night, glowing eyes, hood, '
    'weapon, sword, knife) ARE NOT IN THIS DRAFT and `harmless` was dropped from '
    'the positive, so a failure here leaves those a known untried lever rather '
    'than a new idea. Seeds are r3\'s own four, held rather than advanced, so '
    'the words are the only variable against the sheet he rejected.')


def sidecar(png: Path, *, seed: int, pos: str, neg: str, neg_full: str,
            secs: float, warns: list, task: str, shots_sha: str, draft_sha: str,
            pos_tokens: int, neg_tokens: int, r3_pos_tokens: int,
            out_dir: Path) -> None:
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())
    lines = ["# Still provenance (7.2), written AT RENDER TIME by render_b05r4.py",
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
            f"count_tag_r3: {R3_TAG}",
            "count_tag_note: >-",
            block("DERIVED, NOT TYPED. sd_prompt._tag_from_clause reads the "
                  "first comma-clause of the first sentence and tests _MALE "
                  "before _OTHER. r3's `two patrol guards drawn as round "
                  "harmless shapes` reaches neither male word and matches "
                  "`guards` under _OTHER, returning `2others`; the draft's `Two "
                  "round guard men` hits `men` and returns `2boys`. Nothing in "
                  "the draft types a tag — the wording change is the tag "
                  "change, which is why the wording could not be tightened "
                  "without moving it."),
            f"extra_negative_tier: {EXTRA_NEG_TIER}",
            "extra_negative_tier_note: >-",
            block("No goblin and no plant in this frame, so neither r6's nine "
                  "fusion tags nor r8's two species tags apply. They would "
                  "spend roughly twenty tokens of a 77-token budget suppressing "
                  "a collision that cannot occur in a beat with two guards and "
                  "an empty field in it."),
            f"shots_md_sha256: {shots_sha}",
            "shots_md_edited: false",
            "authored_source: >-",
            block(f"{DRAFT_PATH} beat 5, verbatim. NOT shots.md and NOT canon — "
                  f"the draft is unapproved script text, injected script-side "
                  f"and asserted byte-for-byte against that file before a step "
                  f"is spent. The guard beats carry no {{{{GOBLIN}}}} slot, so "
                  f"this one waits on nothing the founder has yet to define."),
            f"authored_source_sha256: {draft_sha}",
            "tokenizer: openai/clip-vit-large-patch14 (transformers, on the box)",
            f"positive_tokens: {pos_tokens}",
            f"positive_tokens_r3_control: {r3_pos_tokens}",
            f"negative_tokens_sent: {neg_tokens}",
            "negative_delta_from_r3: girl, child",
            "r3_control_reproduced: true",
            "r3_control_note: >-",
            block("The r3 positive and negative were rebuilt from this checkout "
                  "in the same run and asserted byte-for-byte against the "
                  "strings recorded in the r3 sidecars, on this tokenizer. "
                  "Without that the token delta below would be two "
                  "instruments, not one measurement."),
            "anchor_intact: true",
            "anchor_note: >-",
            block("THE ANCHOR WAS ALREADY INTACT ON r3. Beat 5 was not one of "
                  "the eleven beats compress() was shedding the style sentence "
                  "from, so the b13-r4 finding — anchor restored, soft "
                  "cinematic anime 4 of 4 — is NOT the mechanism available "
                  "here. r3 sent the anchor, sent `round harmless shapes` and "
                  "sent `an empty morning field`, and returned a dark forest "
                  "with dangerous-looking figures on all four. This round tests "
                  "the count tag and the tightened subject clause instead."),
            "prescription_not_tested: >-",
            block("PROVISIONAL-PICKS-0809 defect 3 prescribes `round, harmless, "
                  "comedic, chibi-proportioned, daylight` leading the guard "
                  "clause and `dark fantasy, night, glowing eyes, hood, weapon, "
                  "sword, knife, armor plate` negated. NONE of those negatives "
                  "are in this draft, and the draft drops `harmless` from the "
                  "positive, which r3 had. This round is therefore not a test "
                  "of that prescription; it is a test of the cheaper change in "
                  "front of it, and the prescription stays a costed untried "
                  "lever."),
            "seeds_held_from: >-",
            block("r3's own four (k=4..7 of this beat's series), NOT advanced. "
                  "r3 advanced because no fault was named and new noise was its "
                  "only lever; a fault is named now and the words move, so "
                  "holding the noise makes r4 a direct A/B against the four "
                  "frames he rejected. This is b13's convention from r4 to r9."),
            "provisional: true",
            "approved: false",
            "recipe_inherited_from: >-",
            block("round 3, takes/stills/05-the-patrol-r3-s*.png — model, size, "
                  "steps, cfg, the seed series and the one-term negative "
                  "removal are r3's unchanged. r3 inherited those from node 001 "
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


def build(authored: str, compress, beat_negative) -> tuple:
    """The full prompt pair for one authored fence, through the real code path."""
    pos, dropped = compress(authored)
    warns = []
    neg_full = beat_negative(NEG, authored, EXTRA_NEG, warn=warns.append)
    neg, removed = strip_term(neg_full, DROP_NEG)
    return pos, neg, neg_full, dropped, warns, removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--measure", action="store_true",
                    help="print the r3 control beside r4 on this box's real "
                         "tokenizer, draw nothing")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "pipeline"))
    from generate_shots import parse_shots                          # noqa: E402
    from sd_prompt import (beat_negative, compress,                 # noqa: E402
                           negative_tokens, _clip_tokenizer, _tag_from_clause)

    node = root / "genomes/sapling/nodes/002b-first-citizen"
    shots_path = node / "shots.md"
    draft_path = root / DRAFT_PATH
    out = Path(__file__).resolve().parent / "out"
    out.mkdir(exist_ok=True)

    raw = shots_path.read_bytes()
    shots_sha = hashlib.sha256(raw).hexdigest()
    shots = {s["num"]: s for s in parse_shots(raw.decode("utf-8"))}
    s = shots[BEAT]
    authored_r3 = s["prompt"]

    # THE TOKENIZER IS THE WHOLE POINT OF RUNNING THIS HERE. Without it every
    # number below is the estimator known to be wrong near 77 — it read b13's r8
    # as 61 with the anchor dropped, a false failure of that beat's own gate.
    if _clip_tokenizer() is None:
        print("!! NO CLIP TOKENIZER — transformers is not importable, so every "
              "token count here would be the estimator that over-counts near "
              "the 77 boundary. Run this on the box's venv; stopping.",
              flush=True)
        return 8

    # trap 1: the fence must be r3's, byte for byte. This round does not edit
    # shots.md, so a stale checkout would render the wrong control silently.
    if authored_r3 != AUTHORED_R3:
        print("!! shots.md Beat 5 is not the r3 fence, byte for byte — the "
              "checkout is stale or the fence moved, and neither the control "
              "nor the draft comparison below would mean anything.\n"
              f"   expected: {AUTHORED_R3}\n"
              f"   found:    {authored_r3}\n   stopping.", flush=True)
        return 4

    # trap 2: the draft in the file must be the draft this script was reviewed
    # against. The wave-prep file is a working document and it is edited by
    # other lanes; an unreviewed wording must not reach the GPU under this id.
    draft_raw = draft_path.read_bytes()
    draft_sha = hashlib.sha256(draft_raw).hexdigest()
    import yaml                                                      # noqa: E402
    drafts = yaml.safe_load(draft_raw.decode("utf-8"))
    try:
        on_file = " ".join(drafts["beats"][BEAT]["authored"].split())
        on_file_tag = drafts["beats"][BEAT]["tag"]
        on_file_tier = drafts["beats"][BEAT]["extra_neg"]
    except (KeyError, TypeError):
        print(f"!! {DRAFT_PATH} has no beat {BEAT} draft; stopping.", flush=True)
        return 12
    if on_file != AUTHORED_R4:
        print(f"!! {DRAFT_PATH} beat {BEAT} has MOVED since this script was "
              f"written — rendering it would spend the GPU on wording nobody "
              f"has read.\n   script: {AUTHORED_R4}\n   file:   {on_file}\n"
              f"   stopping.", flush=True)
        return 12
    if on_file_tag != EXPECT_TAG or on_file_tier != EXTRA_NEG_TIER:
        print(f"!! {DRAFT_PATH} beat {BEAT} asserts tag={on_file_tag!r} "
              f"tier={on_file_tier!r}; this script expects {EXPECT_TAG!r} / "
              f"{EXTRA_NEG_TIER!r}; stopping.", flush=True)
        return 12
    authored = AUTHORED_R4

    pos, neg, neg_full, dropped, warns, removed = build(
        authored, compress, beat_negative)
    cpos, cneg, _, cdropped, _, _ = build(AUTHORED_R3, compress, beat_negative)

    seeds = [SEED_K0 + (FIRST_K + i) * 1000 for i in range(4)]
    print(f"\n== beat {BEAT} {s['slug']} [{CANDIDATE_SET}] "
          f"seeds {', '.join(str(x) for x in seeds)}", flush=True)
    print(f"   shots.md: {shots_path}", flush=True)
    print(f"   sha256:   {shots_sha}  (NOT edited by this round)", flush=True)
    print(f"   draft:    {draft_path}", flush=True)
    print(f"   sha256:   {draft_sha}", flush=True)
    print(f"   AUTHORED(r3 fence): {authored_r3}", flush=True)
    print(f"   AUTHORED(r4 draft): {authored}", flush=True)
    print(f"   POS: {pos}", flush=True)
    print(f"   NEG(recipe): {neg_full}", flush=True)
    print(f"   NEG(sent):   {neg}", flush=True)
    pos_tokens = negative_tokens(pos)
    neg_tokens = negative_tokens(neg)
    ctok = negative_tokens(cpos)
    print(f"   positive tokens: {pos_tokens} (budget 77)", flush=True)
    print(f"   negative tokens: recipe {negative_tokens(neg_full)} -> "
          f"sent {neg_tokens} (budget 77)", flush=True)
    for w in warns:
        print(f"   NEGWARN: {w}", flush=True)

    # trap 3: the r3 control must reproduce from THIS checkout, or the delta
    # below compares two different instruments rather than measuring one change.
    if cpos != R3_POS_SENT or cneg != R3_NEG_SENT:
        print("!! THE r3 CONTROL DOES NOT REPRODUCE from this checkout, so no "
              "comparison in this round is controlled.\n"
              f"   pos match: {cpos == R3_POS_SENT}\n"
              f"   neg match: {cneg == R3_NEG_SENT}\n"
              f"   rebuilt pos: {cpos}\n   rebuilt neg: {cneg}\n   stopping.",
              flush=True)
        return 10

    if a.measure:
        print("\n-- r3 CONTROL on this same tokenizer --", flush=True)
        print(f"   POS: {cpos}", flush=True)
        print(f"   positive tokens: {ctok}  "
              f"anchor {'INTACT' if cpos.rstrip().endswith(ANCHOR) else 'DROPPED'}"
              f"  dropped={cdropped}", flush=True)
        print(f"   count tag: {_tag_from_clause(AUTHORED_R3.split('.')[0].split(',')[0])}",
              flush=True)
        print(f"   negative identical_to_recorded_r3={cneg == R3_NEG_SENT}",
              flush=True)
        print("\n-- r4 as configured --", flush=True)
        print(f"   positive tokens: {pos_tokens}  "
              f"anchor {'INTACT' if pos.rstrip().endswith(ANCHOR) else 'DROPPED'}"
              f"  dropped={dropped}", flush=True)
        print(f"   count tag: "
              f"{_tag_from_clause(AUTHORED_R4.split('.')[0].split(',')[0])}",
              flush=True)
        print(f"   delta r4-r3: {pos_tokens - ctok} tokens on the positive",
              flush=True)
        print(f"   negative delta: "
              f"{[t for t in neg.split(', ') if t not in cneg.split(', ')]}",
              flush=True)
        print("\n-- what defect 3's prescribed negatives would cost, alone --",
              flush=True)
        for frag in (", dark fantasy", ", night", ", glowing eyes", ", hood",
                     ", weapon", ", sword", ", knife", ", armor plate",
                     ", harmless", ", chibi", ", comedic", ", daylight"):
            print(f"   {frag:<18} {negative_tokens(frag) - 2} tokens",
                  flush=True)
        return 0

    # trap 4: read the count tag off the real path. This round's headline change
    # is the tag; if it did not move, r4 is r3 again under a new id.
    if not pos.startswith(EXPECT_TAG + ","):
        print(f"   !! COUNT TAG is not `{EXPECT_TAG}` — POS opens `{pos[:40]}`. "
              f"The whole change this round is testing; stopping.", flush=True)
        return 5
    if cpos.startswith(EXPECT_TAG + ","):
        print(f"   !! THE r3 CONTROL ALSO OPENS `{EXPECT_TAG}` — then the tag "
              f"did not move and there is nothing to test; stopping.",
              flush=True)
        return 5
    # trap 5: the two negative terms the draft buys must survive the 77-token
    # budget. They are this round's entire negative delta.
    sent_terms = [p.strip().lower() for p in neg.split(",")]
    missing = [t for t in EXPECT_NEG_ADDS if t not in sent_terms]
    if missing:
        print(f"   !! NEGATIVE TERMS DROPPED by the 77-token budget: "
              f"{', '.join(missing)} — the draft's only negative change; "
              f"stopping.", flush=True)
        return 6
    # trap 6: nothing else in the negative may move, or the round has two
    # variables and the comparison is not attributable.
    unexpected = [t for t in sent_terms
                  if t not in [p.strip().lower() for p in cneg.split(",")]
                  and t not in EXPECT_NEG_ADDS]
    if unexpected:
        print(f"   !! UNEXPECTED NEGATIVE TERMS beyond `girl, child`: "
              f"{', '.join(unexpected)} — this round claims one negative "
              f"delta; stopping.", flush=True)
        return 9
    # trap 7: the anchor. r3 HAD it; losing it here would make the round a test
    # of the b13-r4 defect instead of the register, on a beat that never had it.
    if not pos.rstrip().endswith(ANCHOR):
        print(f"   !! STYLE ANCHOR DROPPED — the positive does not end with "
              f"`{ANCHOR}`. r3 sent it intact, so losing it now would change a "
              f"second variable in the wrong direction; stopping.", flush=True)
        return 7
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
                warns=warns, task=TASK, shots_sha=shots_sha, draft_sha=draft_sha,
                pos_tokens=pos_tokens, neg_tokens=neg_tokens, r3_pos_tokens=ctok,
                out_dir=out)
        print(f"   {f.name} seed={seed} {secs:.0f}s  ({i + 1}/4)", flush=True)

    print("\nDONE 4 stills", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
