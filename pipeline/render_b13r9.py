#!/usr/bin/env python3
"""002b beat 13 — ROUND 9, the TUSK. 2026-08-09.

WHY THIS ROUND EXISTS, and it is filed rather than invented. Record 39's own
notes name this lever and say why it was not spent in r8:

    THE TUSK IS THE CHEAPEST UNTRIED LEVER AND IT IS FILED HERE SO IT IS NOT
    REDISCOVERED. `tusks` is a real Danbooru tag and the script asks for "one
    broken tusk". It has never been in a positive on this beat. It was left out
    of r8 only because the budget bought two tags and `green skin` and `plump`
    were the two the founder's sentence weighted highest. If he asks where the
    tusk is, the answer is that it was affordable and deferred, not that it was
    tried and failed.

The script's noun is "A small round goblin — enormous ears, ONE BROKEN TUSK,
faded green patchwork cloak". Record 39 observed `broken_tusk` fail on 4 of 4
r8 frames and said plainly that it had never been asked for. This round asks.

ONE AXIS IS ADDED AND IT HAD TO BE PAID FOR, SO THE POSITIVE MOVES IN TWO
PLACES. That is stated first because it is the one thing a reader of this round
could be misled about: r9 is not a clean single-variable round on the positive.
It adds `tusks` and it sells four tokens of the shade clause to afford them (see
THE BUDGET below). The negative, by contrast, does not move at all — this script
refuses to spend a step unless the string it is about to send is BYTE-IDENTICAL
to the negative recorded in the r8 sidecars, all eleven explicit terms included.
The plant sentence and the style tail are r6's byte-for-byte, as in r8, because
P1/P3/P4 were bought there and record 39 already logged one frame (s0) losing
the seedling. `green skin`, `plump`, `solo` and `1boy` all stay.

THE BUDGET FORCED A TRADE AND THE TRADE WAS MEASURED, NOT GUESSED. r8 measured
at EXACTLY 77 of 77 on the box's real CLIP tokenizer, BOS and EOS included.
There is no headroom, so `tusks` cannot be added — it has to be bought, and
record 39 stated the rule: "any round that wants one of them must cut something
to pay for it." The lane opened expecting the tag to cost one token. THE WORD
IS TWO AND THE INSERTION IS THREE, and the difference between those numbers is
the comma: `tusks` is two CLIP subwords, and a tag added to a comma-separated
list brings its own separator, which is a third token. What the budget has to
pay for is the insertion, so the number that matters here is three (`--measure`
on the box: `, tusks` 3, `, tusk` 3, `, fangs` 3, `, broken tusk` 4, `, single
tusk` 4). Selling the indefinite article frees ONE, which would have left the
prompt at 79 and shed the style anchor — the r4 defect this beat already paid
for once, and it is what four of the first candidates did: 60-62 tokens, anchor
gone, every time.

SO THIS ROUND SELLS TWO THINGS AND BOTH ARE THE CHEAPEST OF THEIR KIND. The
indefinite article — `A small goblin boy` becomes `Small goblin boy` — and
`patch of`, so `folds into a thin patch of shade` becomes `folds into thin
shade`. That frees four for a three-token axis and lands at 76 with one token
of headroom. The action, its quality and its subject all survive; what is lost
is the countable-area framing of the shade, and that is named here rather than
smoothed over. Nothing else in sentence 1 was eligible: `small`, `green skin`
and `plump` are axes the founder's own sentence named, `solo` and `1boy` are
tags measured to bind on this beat, and the plant sentence and style anchor are
r6's byte-for-byte.

WHY THE PLURAL TAG AND NOT THE SCRIPT'S OWN PHRASE — MEASURED IN THE CORPUS,
NOT PREFERRED. Three candidates were checked against Danbooru before one was
chosen, and every answer came back against the intuitive reading:

  `tusk`, singular — NOT a usable token. The corpus aliases it away, so it
      carries no learned signal of its own, and it does not even share subwords
      with the plural. Asking for one tusk with `tusk` asks for nothing.
  `broken tusk` — 15 posts in a corpus of roughly 12 million. Unlearnable: the
      checkpoint has no concept attached to it. Worse, in a caption vocabulary
      `broken` neighbours the quality-defect words, so it risks being read as
      something wrong with the PICTURE rather than with the tooth. It also fits
      at exactly 77 of 77, spending the last headroom on a phrase the model
      cannot use.
  `fangs` — a real, heavy tag, rejected on evidence: it DEEPENS the female skew
      this beat is fighting. It would have made his complaint worse while
      looking like progress.

`tusks` is the one that survives, and the corpus says it does more than draw a
tooth. IT IS ALSO A GENDER LEVER, WHICH IS THE THING HE ACTUALLY COMPLAINED
ABOUT: `tusks` co-occurs male to female 1.92 to 1, and on posts that also carry
`goblin` it takes the female skew from 3.14 down to 1.59 — it halves it. Record
39 established that "all the goblin images look like female demihumans" is the
corpus sampled faithfully rather than a mis-render; this tag pulls the sample
the other way. So the cheapest untried lever is not only the missing noun from
his script, it is a second and independent pull on the axis r8 delivered least
cleanly — male read unambiguously on s0 alone. That is why this round is worth
its four seeds even if the tusks themselves come out wrong. It is also the
general finding of r6 and r8 holding a third time: on this checkpoint the tag
name beats the mechanism, and which tag is a corpus question, answerable from
outside this repo in minutes.

`boy` STAYS IN THE CLAUSE AND THAT IS NOT COSMETIC. `_tag_from_clause` tests
`_MALE` before `_OTHER` on the leading clause, so `small goblin boy` still
yields `1boy`; drop the word and the clause matches `_OTHER` and hands back
`1other`, the indeterminate-humanoid tag that cost r3-r5 three rounds at 0/4.
Trap 2 below reads the tag off the real code path and refuses to render without
it.

SHOTS.MD IS NOT TOUCHED. The axis is injected script-side, and the fence is
checked BYTE-FOR-BYTE against the r8 text before the injection runs (trap 1).
r8 edited the fence and a stale checkout could therefore render r6's wording
under r8's id; here a stale checkout cannot even start, and the founder's
approved shot list keeps one authored version of this beat rather than nine.

MEASURE ON THE BOX OR NOT AT ALL. `sd_prompt._token_estimate` silently falls
back to an approximation when `transformers` is absent and it over-counts this
prompt by about 3 near the 77 boundary — on the Mac it read r8 as 61 tokens
WITH THE ANCHOR DROPPED, which is a false failure of r8's own hard gate
(STATE.md 2026-08-09). This script refuses to run at all without a real CLIP
tokenizer (exit 8) rather than reporting an estimate as a measurement, and
`--measure` prints the r8 control beside r9 on the SAME tokenizer so the delta
is read off one instrument.

THE KNOWN RISKS, STATED IN ADVANCE. The script says "one broken tusk" and this
round asks for `tusks`. The plural is what the corpus can draw; "one" and
"broken" stay CHARACTER PROSE, and if he wants the break visible the lever for
it is an inpaint or a close-up, NOT a prompt token — filed here so the next
round does not rediscover it as a prompt problem. If r9 returns two symmetric
intact tusks, that is the trade, and it is still the first frame on this beat
with a tusk in it. Second risk: `tusks` co-occurs with `orc`, a heavier, adult,
muscular tag than this small round creature, and it may pull build away from
`plump`, which r8 had at 3 of 4. Third: the round pays for its axis out of the
shade clause, so a change in the composition has two possible causes and this
file says so rather than crediting the tag.

    python render_b13r9.py --root C:\\banyan-farm\\banyan-city --measure
    python render_b13r9.py --root C:\\banyan-farm\\banyan-city --dry
    python render_b13r9.py --root C:\\banyan-farm\\banyan-city
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
CANDIDATE_SET = "r9"
QUEUE_ENTRY = "ep2-b13-r9-tusks-1786320000"
TASK = "ep2-b13-r9-tusks-1786320000"
BEAT = 13
EXPECT_DROP = 1  # `tiny`, `40cm`, `seedling` all fire _SMALL
EXPECT_TAG = "1boy"
# r6's nine fusion tags plus r8's two species tags. UNCHANGED — this round buys
# nothing in the negative, which is what makes the positive the only variable.
EXTRA_NEG = ("leaf on head, plant girl, alraune, monster girl, flower on head, "
             "head wreath, hair ornament, leaf hair ornament, plant hair, "
             "female goblin, elf")
# the style anchor. r8 sat at exactly 77/77; r9 buys its one tag and sits there
# too, so this stays checked rather than assumed.
ANCHOR = ("Midday light, cinematic lighting, detailed, newest, masterpiece, "
          "best quality, very aesthetic")

# THE r8 FENCE, BYTE-FOR-BYTE. This is the control and the staleness guard in
# one: if shots.md beat 13 is not exactly this, the checkout is not the one r8
# was measured on and no comparison below means anything.
AUTHORED_R8 = (
    "A small goblin boy, green skin, plump, solo, folds into a thin patch of "
    "shade, knees up around his ears, no girl, no child. Plant, grass, "
    "outdoors, a tiny 40cm seedling with two oversized cotyledon leaves rooted "
    "in the ground beside him. Midday light, cinematic lighting, detailed, "
    "newest, masterpiece, best quality, very aesthetic No photorealism, no 3D "
    "render look. 9:16 vertical, no text.")

# THE ONE AXIS AND WHAT IT COST, both measured on the box before a step was
# spent (`--measure`, 2026-08-09):
#
#     `, tusks`  3 tokens    `, tusk`   3      `, fangs`  3
#     `, broken tusk`  4     `, single tusk`  4     the article `a `  1
#
# r8 is 77 of 77, so a 3-token axis needs 3 tokens sold, and selling the article
# alone (1) leaves the prompt at 79 with the STYLE ANCHOR SHED — measured, not
# feared: every trade under 3 tokens came back 60-62 with the anchor gone. The
# minimum admissible sell is the article plus `patch of`, which frees 4 and lands
# at 76 with one token of headroom. Asserted as a substring before it is applied,
# so a fence that drifts cannot be silently half-injected.
INJECT_FROM = ("A small goblin boy, green skin, plump, solo, folds into a thin "
               "patch of shade")
INJECT_TO = ("Small goblin boy, green skin, plump, tusks, solo, folds into thin "
             "shade")
AXIS_TAG = "tusks"

# what r8 actually sent, from takes/stills/13-the-shade-r8-s0.png.meta.yaml:36.
# r9's whole claim is that this string does not move.
R8_NEG_SENT = (
    "photorealistic, 3d render, text, mature tree, large tree, thick trunk, "
    "full canopy, forest, bush, shrubbery, girl, child, photorealism, leaf on "
    "head, plant girl, alraune, monster girl, flower on head, head wreath, "
    "hair ornament, leaf hair ornament, plant hair, female goblin, elf")

NOTE = ('round 9, THE TUSK, and it is the lever record 39 filed rather than a '
        'new idea: "`tusks` is a real Danbooru tag and the script asks for one '
        'broken tusk. It has never been in a positive on this beat. It was left '
        'out of r8 only because the budget bought two tags and `green skin` and '
        '`plump` were the two the founder\'s sentence weighted highest. If he '
        'asks where the tusk is, the answer is that it was affordable and '
        'deferred, not that it was tried and failed." Record 39 observed '
        'broken_tusk fail on 4 of 4 r8 frames while noting it had never been '
        'asked for; this round asks. EXACTLY ONE AXIS MOVES and the negative '
        'does not move at all — this script refuses to spend a step unless the '
        'string it is about to send is byte-identical to the negative recorded '
        'in the r8 sidecars, all eleven explicit terms included, so the positive '
        'is demonstrably the only variable. `green skin`, `plump`, `solo` and '
        '`1boy` stay; the plant sentence and the style tail are r6\'s '
        'byte-for-byte, as in r8, because P1/P3/P4 were bought there and record '
        '39 already logged s0 losing the seedling. THE BUDGET FORCED A TRADE AND '
        'THE TRADE WAS MEASURED, NOT GUESSED: r8 measured at exactly 77 of 77 on '
        'the box\'s real CLIP tokenizer, BOS and EOS included, so `tusks` could '
        'not be added, only bought — record 39\'s own rule, "any round that wants '
        'one of them must cut something to pay for it". The lane opened expecting '
        'the tag to cost one token; THE WORD IS TWO AND THE INSERTION IS THREE, '
        'the difference being the comma — `tusks` is two CLIP subwords and a tag '
        'added to a comma-separated list brings its own separator. What the '
        'budget pays for is the insertion, so three is the number that binds '
        '(measured on the box: `, tusks` 3, `, tusk` 3, `, fangs` 3, `, broken '
        'tusk` 4, `, single tusk` 4), and selling the indefinite article frees '
        'only one, which leaves the '
        'prompt at 79 and SHEDS THE STYLE ANCHOR — the r4 defect this beat has '
        'already paid for once, and what four of the first candidates did at '
        '60-62 tokens. So this round sells two things, both the cheapest of their '
        'kind: the indefinite article (`A small goblin boy` becomes `Small goblin '
        'boy`) and `patch of` (`folds into a thin patch of shade` becomes `folds '
        'into thin shade`). That frees four for a three-token axis and lands at '
        '76 with one token of headroom, anchor intact. The action, its quality '
        'and its subject all survive; what is lost is the countable-area framing '
        'of the shade, said plainly rather than smoothed over. Nothing else in '
        'sentence 1 was eligible: `small`, `green skin` and `plump` are axes his '
        'own sentence named, `solo` and `1boy` are tags measured to bind here, '
        'and the plant sentence and style anchor are r6\'s byte-for-byte. WHY THE '
        'PLURAL TAG AND NOT HIS OWN PHRASE, MEASURED IN THE CORPUS RATHER THAN '
        'PREFERRED — three candidates were checked against Danbooru before one '
        'was chosen and every answer came back against the intuitive reading. '
        '`tusk` singular is NOT a usable token: the corpus aliases it away, so it '
        'carries no learned signal of its own and does not even share subwords '
        'with the plural — asking for one tusk with `tusk` asks for nothing. '
        '`broken tusk` is 15 posts in roughly 12 million, which is unlearnable, '
        'and in a caption vocabulary `broken` neighbours the QUALITY-DEFECT '
        'words, so it risks reading as something wrong with the picture rather '
        'than with the tooth; it also fits at exactly 77 of 77, spending the last '
        'headroom on a phrase the model cannot use. `fangs` is a real heavy tag '
        'and was rejected on evidence: it DEEPENS the female skew this beat is '
        'fighting, so it would have made his complaint worse while looking like '
        'progress. `tusks` is the one that survives, AND THE CORPUS SAYS IT DOES '
        'MORE THAN DRAW A TOOTH — it is also a gender lever, which is the thing '
        'he actually complained about: `tusks` co-occurs male to female 1.92 to '
        '1, and on posts also carrying `goblin` it takes the female skew from '
        '3.14 down to 1.59, halving it. Record 39 established that "all the '
        'goblin images look like female demihumans" is the corpus sampled '
        'faithfully rather than a mis-render; this tag pulls the sample the other '
        'way. So the cheapest untried lever is not only the missing noun from his '
        'script, it is a second and independent pull on the axis r8 delivered '
        'least cleanly — male read unambiguously on s0 alone — and that is why '
        'the round is worth four seeds even if the tusks come out wrong. It is '
        'also r6\'s and r8\'s general finding holding a third time: on this '
        'checkpoint the tag name beats the mechanism, and WHICH tag is a corpus '
        'question answerable from outside this repo in minutes. `boy` stays in '
        'the clause and that is not cosmetic: '
        '_tag_from_clause tests _MALE before _OTHER, so `small goblin boy` still '
        'yields `1boy`, while dropping the word matches _OTHER and hands back '
        '`1other`, the indeterminate-humanoid tag that cost r3-r5 three rounds '
        'at 0/4. SHOTS.MD IS NOT TOUCHED — the axis is injected script-side and '
        'the fence is checked byte-for-byte against the r8 text before the '
        'injection runs, so a stale checkout cannot start rather than silently '
        'rendering the wrong round under this id, and the approved shot list '
        'keeps one authored version of this beat rather than nine. MEASURED ON '
        'THE BOX AND ONLY THERE, with the r8 fence as the control on the same '
        'tokenizer: this script refuses to run without a real CLIP tokenizer, '
        'because _token_estimate silently falls back to an approximation that '
        'over-counts this prompt by ~3 near the 77 boundary and read r8 on the '
        'Mac as 61 tokens with the anchor dropped — a false failure of r8\'s own '
        'hard gate. Same four seeds as r4-r8, a controlled column. STATED RISKS: '
        'the script says "one broken tusk" and this round asks for `tusks` — the '
        'plural is what the corpus can draw, so "one" and "broken" stay CHARACTER '
        'PROSE, and if he wants the break visible the lever is an inpaint or a '
        'close-up rather than a prompt token, filed so the next round does not '
        'rediscover it as a prompt problem; if r9 returns two symmetric intact '
        'tusks that is the trade, and it is still the first frame on this beat '
        'with a tusk in it. `tusks` also co-occurs with `orc`, a heavier, adult, '
        'muscular tag that may pull build away from `plump`, which r8 had at 3 of '
        '4. And the round pays for its axis out of the shade clause, so a change '
        'in the composition has two possible causes and this record says so '
        'rather than crediting the tag. NOT A GATE '
        'ATTEMPT: record 32 ruled "P2 is not a valid gate until he defines the '
        'goblin, and no r8 may be scored against the old one", and that '
        'constraint has not been lifted, so this round is observation and exists '
        'to give him one more thing to define the goblin with. Ledger record '
        'written BEFORE the sheet. No pick, no wave fires off this beat, and '
        'nothing goes on his screen tonight. AND SAID FIRST BECAUSE IT IS WHAT A '
        'READER COULD BE MISLED ABOUT: r9 is NOT a clean single-variable round on '
        'the positive. It adds one axis and it sells four tokens of the shade '
        'clause to afford it, so the positive moves in two places; only the '
        'negative is byte-identical and only that is asserted. If the shade or '
        'the composition changes, the payment is as likely a cause as the axis.')


def sidecar(png: Path, *, seed: int, pos: str, neg: str, neg_full: str,
            secs: float, warns: list, task: str, shots_sha: str,
            pos_tokens: int, neg_tokens: int, out_dir: Path) -> None:
    def block(text: str) -> str:
        return "\n".join("  " + ln for ln in text.strip().splitlines())
    lines = ["# Still provenance (7.2), written AT RENDER TIME by render_b13r9.py",
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
            f"negative_terms_removed: {DROP_NEG}",
            f"count_tag: {EXPECT_TAG}",
            "extra_negative_tier: explicit",
            "extra_negative: >-",
            block(EXTRA_NEG),
            f"shots_md_sha256: {shots_sha}",
            "shots_md_edited: false",
            "tokenizer: openai/clip-vit-large-patch14 (transformers, on the box)",
            f"positive_tokens: {pos_tokens}",
            f"negative_tokens_sent: {neg_tokens}",
            "negative_identical_to_r8: true",
            f"axis_added: {AXIS_TAG}",
            "axis_cost_tokens: 3",
            "axis_paid_for_with: >-",
            block("the indefinite article AND `patch of`, measured. r8 sat at "
                  "exactly 77 of 77 on this tokenizer, BOS and EOS included, so "
                  "`tusks` had to be bought rather than added (record 39: any "
                  "round that wants another tag must cut something to pay for "
                  "it). `, tusks` costs 3 tokens, not the 1 this lane opened "
                  "expecting; selling the article alone frees 1, leaves 79, and "
                  "sheds the style anchor. So `A small goblin boy` becomes "
                  "`Small goblin boy` and `folds into a thin patch of shade` "
                  "becomes `folds into thin shade` — 4 freed for a 3-token axis, "
                  "76 sent, one token of headroom, anchor intact. What is lost "
                  "is the countable-area framing of the shade; the action, its "
                  "quality and its subject survive. `boy` is kept because "
                  "_tag_from_clause would otherwise return `1other`."),
            "axis_alternatives_rejected: >-",
            block("measured against the Danbooru corpus, not preferred. `tusk` "
                  "singular is aliased away and carries no learned signal, and "
                  "does not share subwords with the plural. `broken tusk` is 15 "
                  "posts in ~12M — unlearnable — and `broken` neighbours the "
                  "quality-defect words, so it risks reading as a fault in the "
                  "picture rather than the tooth; it also fits only by spending "
                  "the last token of headroom. `fangs` is real and heavy but "
                  "DEEPENS the female skew this beat is fighting."),
            "axis_second_effect: >-",
            block("`tusks` is also a gender lever, which is the axis the founder "
                  "actually named: it co-occurs male to female 1.92 to 1, and on "
                  "posts also carrying `goblin` it takes the female skew from "
                  "3.14 to 1.59 — halving it. Record 39 established his "
                  "complaint was the corpus sampled faithfully; this tag pulls "
                  "the sample the other way."),
            "provisional: true",
            "approved: false",
            "recipe_inherited_from: >-",
            block("round 8, takes/stills/13-the-shade-r8-s*.png — model, size, "
                  "steps, cfg, seed rule, the one-term negative removal, the "
                  "eleven explicit negatives, the plant sentence and the style "
                  "tail are r8's unchanged, and the SENT NEGATIVE is asserted "
                  "byte-identical to r8's before a step is spent. r8 inherited "
                  "those in turn from r6, and r6 from node 001 "
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
                    help="print the r8 control and the candidate trades on this "
                         "box's tokenizer, draw nothing")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "pipeline"))
    from generate_shots import parse_shots                          # noqa: E402
    from sd_prompt import (beat_negative, compress,                 # noqa: E402
                           negative_tokens, _clip_tokenizer)

    node = root / "genomes/sapling/nodes/002b-first-citizen"
    shots_path = node / "shots.md"
    out = Path(__file__).resolve().parent / "out"
    out.mkdir(exist_ok=True)

    raw = shots_path.read_bytes()
    shots_sha = hashlib.sha256(raw).hexdigest()
    shots = {s["num"]: s for s in parse_shots(raw.decode("utf-8"))}
    s = shots[BEAT]
    authored_r8 = s["prompt"]

    # THE TOKENIZER IS THE WHOLE POINT OF RUNNING THIS HERE. Without it every
    # number below is the estimator that is known to be wrong near 77 — it read
    # r8 as 61 with the anchor dropped, a false failure of r8's own hard gate.
    if _clip_tokenizer() is None:
        print("!! NO CLIP TOKENIZER — transformers is not importable, so every "
              "token count here would be the estimator that over-counts this "
              "prompt by ~3 near the 77 boundary. Run this on the box's venv; "
              "stopping.", flush=True)
        return 8

    # trap 1: the fence must be r8's, byte for byte. r8 edited shots.md, so a
    # stale checkout is a live possibility and it would render the wrong round
    # under this id. r9 does NOT edit shots.md — the axis is injected below.
    if authored_r8 != AUTHORED_R8:
        print("!! shots.md Beat 13 is not the r8 fence, byte for byte — the "
              "checkout is stale or the fence moved, and neither the control "
              "nor the injection below would mean anything.\n"
              f"   expected: {AUTHORED_R8}\n"
              f"   found:    {authored_r8}\n   stopping.", flush=True)
        return 4
    if INJECT_FROM not in authored_r8:
        print(f"!! INJECTION SITE `{INJECT_FROM}` is not in the fence; "
              f"stopping.", flush=True)
        return 4
    authored = authored_r8.replace(INJECT_FROM, INJECT_TO)

    pos, neg, neg_full, dropped, warns, removed = build(
        authored, compress, beat_negative)

    print(f"\n== beat {BEAT} {s['slug']} [{CANDIDATE_SET}] "
          f"seeds {SEED + BEAT}..{SEED + BEAT + 3000}", flush=True)
    print(f"   shots.md: {shots_path}", flush=True)
    print(f"   sha256:   {shots_sha}  (NOT edited by this round)", flush=True)
    print(f"   AUTHORED(r8 fence): {authored_r8}", flush=True)
    print(f"   AUTHORED(r9 inject): {authored}", flush=True)
    print(f"   POS: {pos}", flush=True)
    print(f"   NEG(recipe): {neg_full}", flush=True)
    print(f"   NEG(sent):   {neg}", flush=True)
    pos_tokens = negative_tokens(pos)
    neg_tokens = negative_tokens(neg)
    print(f"   positive tokens: {pos_tokens} (budget 77)", flush=True)
    print(f"   negative tokens: recipe {negative_tokens(neg_full)} -> "
          f"sent {neg_tokens} (budget 77)", flush=True)
    for w in warns:
        print(f"   NEGWARN: {w}", flush=True)

    if a.measure:
        cpos, cneg, _, cdropped, _, _ = build(
            AUTHORED_R8, compress, beat_negative)
        ctok = negative_tokens(cpos)
        print("\n-- r8 CONTROL on this same tokenizer --", flush=True)
        print(f"   POS: {cpos}", flush=True)
        print(f"   positive tokens: {ctok}  "
              f"anchor {'INTACT' if cpos.rstrip().endswith(ANCHOR) else 'DROPPED'}"
              f"  dropped={cdropped}", flush=True)
        print(f"   negative identical_to_recorded_r8={cneg == R8_NEG_SENT}",
              flush=True)
        print("\n-- what the vocabulary costs, alone --", flush=True)
        for label, frag in (("`, tusks`", ", tusks"),
                            ("`, tusk`", ", tusk"),
                            ("`, fangs`", ", fangs"),
                            ("`, broken tusk`", ", broken tusk"),
                            ("`, single tusk`", ", single tusk"),
                            ("the article `a `", " a ")):
            print(f"   {label:<18} {negative_tokens(frag) - 2} tokens", flush=True)

        # THE WHOLE POINT OF THIS TABLE. r8 is at 77 of 77, so any axis has to be
        # BOUGHT, and the only currency in sentence 1 that is not an axis the
        # founder named, a tag measured to bind, or the beat's own action is the
        # function words. Every row prints what it costs and what it sells, and
        # the only admissible rows are `<= 77 anchor INTACT`.
        SELL = {
            "nothing": (INJECT_FROM, "A small goblin boy, green skin, plump, "
                        "{AXIS}solo,"),
            "the article": (INJECT_FROM,
                            "Small goblin boy, green skin, plump, {AXIS}solo,"),
            "article+thin": ("A small goblin boy, green skin, plump, solo, "
                             "folds into a thin patch",
                             "Small goblin boy, green skin, plump, {AXIS}solo, "
                             "folds into a patch"),
            "article+patch of": ("A small goblin boy, green skin, plump, solo, "
                                 "folds into a thin patch of shade",
                                 "Small goblin boy, green skin, plump, {AXIS}"
                                 "solo, folds into thin shade"),
            "article+thin patch of": ("A small goblin boy, green skin, plump, "
                                      "solo, folds into a thin patch of shade",
                                      "Small goblin boy, green skin, plump, "
                                      "{AXIS}solo, folds into shade"),
        }
        print("\n-- candidate trades: axis x what it sells --", flush=True)
        print(f"   {'sells':<22}{'axis':<15}{'tok':>4}  anchor   axis  neg_same",
              flush=True)
        for axis in ("tusks, ", "tusk, ", "broken tusk, ", "fangs, "):
            for label, (frm, to) in SELL.items():
                if frm not in AUTHORED_R8:
                    print(f"   {label:<22}{axis:<15} SITE NOT FOUND", flush=True)
                    continue
                vpos, vneg, _, vdrop, _, _ = build(
                    AUTHORED_R8.replace(frm, to.replace("{AXIS}", axis)),
                    compress, beat_negative)
                ok = vpos.rstrip().endswith(ANCHOR)
                print(f"   {label:<22}{axis:<15}{negative_tokens(vpos):>4}  "
                      f"{'INTACT ' if ok else 'DROPPED'}  "
                      f"{'yes ' if 'tusk' in vpos.lower() or 'fang' in vpos.lower() else 'NO  '}  "
                      f"{vneg == R8_NEG_SENT}"
                      f"{'' if not vdrop else '  dropped=' + str(len(vdrop))}",
                      flush=True)
        print(f"\n-- r9 as configured --\n   positive tokens: {pos_tokens}  "
              f"anchor {'INTACT' if pos.rstrip().endswith(ANCHOR) else 'DROPPED'}"
              f"  dropped={dropped}", flush=True)
        print(f"   delta r9-r8: {pos_tokens - ctok} tokens on the positive",
              flush=True)
        return 0

    # trap 2: read the count tag off the real path and confirm it BEFORE spending
    # a step. Selling the article must not have cost the male tag.
    if not pos.startswith(EXPECT_TAG + ","):
        print(f"   !! COUNT TAG is not `{EXPECT_TAG}` — POS opens `{pos[:40]}`. "
              f"Deleting the male token would hand back `1other`; stopping.",
              flush=True)
        return 5
    # trap 3: the axis itself has to survive the budget. If compress() trimmed at
    # a comma boundary the round would render r8 again under r9's id.
    if AXIS_TAG not in pos.lower():
        print(f"   !! THE AXIS `{AXIS_TAG}` IS NOT IN THE SENT POSITIVE — this "
              f"round would be r8 again under a new id; stopping.", flush=True)
        return 11
    # trap 4: the negative must not have moved. This is what makes it ONE variable.
    if neg != R8_NEG_SENT:
        print("   !! SENT NEGATIVE DIFFERS FROM r8's. This round's whole claim is "
              "that only the positive moved.\n"
              f"      r8: {R8_NEG_SENT}\n      r9: {neg}\n   stopping.",
              flush=True)
        return 9
    # trap 5: fit_negative must sacrifice house boilerplate, never these eleven.
    missing = [t.strip() for t in EXTRA_NEG.split(",")
               if t.strip().lower() not in
               [p.strip().lower() for p in neg.split(",")]]
    if missing:
        print(f"   !! EXPLICIT NEGATIVES DROPPED by the 77-token budget: "
              f"{', '.join(missing)} — r8 bought those; stopping.", flush=True)
        return 6
    # trap 6: the positive sits at the budget ceiling, so the style anchor is the
    # thing that silently disappears first. r4 shipped without it once already.
    if not pos.rstrip().endswith(ANCHOR):
        print(f"   !! STYLE ANCHOR DROPPED — the positive does not end with "
              f"`{ANCHOR}`. compress() shed the trailing sentence to reach 77, "
              f"which is the r4 defect; stopping.", flush=True)
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

    for i in range(4):
        seed = SEED + BEAT + i * 1000
        g = torch.Generator(device="cpu").manual_seed(seed)
        t0 = time.time()
        img = pipe(prompt=pos, negative_prompt=neg, num_inference_steps=STEPS,
                   guidance_scale=CFG, generator=g, width=W, height=H).images[0]
        f = out / f"{BEAT}-{s['slug']}-{CANDIDATE_SET}-s{i}.png"
        img.save(f)
        secs = time.time() - t0
        sidecar(f, seed=seed, pos=pos, neg=neg, neg_full=neg_full, secs=secs,
                warns=warns, task=TASK, shots_sha=shots_sha,
                pos_tokens=pos_tokens, neg_tokens=neg_tokens, out_dir=out)
        print(f"   {f.name} seed={seed} {secs:.0f}s  ({i + 1}/4)", flush=True)

    print("\nDONE 4 stills", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
