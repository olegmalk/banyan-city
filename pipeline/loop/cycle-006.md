# Loop cycle 006 — comprehension (2026-07-25)

Opened by the founder: **"these episodes are usually really hard to
understand and sometimes feels like just nonsense — figure out why the
scripts are so bad or why they aren't working."**

## Method

Cold-viewer simulation. Three agents each "watched" one episode (002b,
005, 006a) receiving ONLY what a viewer receives — the timed caption
stream with **no speaker names** and the frames — then retold the story
and mapped exactly where they got lost. Plus a structural diff of script
vs screen.

## Verdict: the scripts are fine — the translation loses the story

All three viewers called the writing charming/funny and scored
comprehension **6/10**, failing at the SAME points:

1. **No speaker attribution** (unanimous #1). Multi-party volleys read
   as one continuous voice; both of ep 5's emotional turns "floated
   free"; ep 2's guard banter untanglable; ep 6's cold open read as one
   person monologuing. Viewers reverse-engineered speakers from content
   the whole way.
2. **The protagonist is mute AND invisible.** 250–280 words of story-
   critical stage direction per episode — including the tree's ENTIRE
   performance ("One leaf tilts.") — reach the screen nowhere. Viewers
   watch characters converse with an entity whose replies don't exist;
   ep 5's closing line (the tree's first as a citizen) was
   unattributable "maybe the tree? a guess."
3. **Character/style drift breaks scenes at climaxes** (re-confirmed:
   "wondered if this was a different goblin" / "read as a different
   video spliced in"). Gated on render capacity (regrow rail).
4. **Cold opens are unanchored** — in-medias-res dialogue with no
   who/where; only make sense retroactively. Evidence that anchors
   work: 006a's mid-episode status-bar overlay ("SHADE · shrine
   (provisional) · MIRACLE: due full moon") "clarified more than any
   caption" — but arrives ~65% in. One viewer thought Shade was the
   goblin's name.
5. Cross-episode callbacks ("the apple incident") read as holes cold.

## Fixes shipped this cycle (assembly-level; scripts untouched)

- **Speaker-attributed captions** (`render_t3.py`): colored name tag on
  the first chunk when the speaker changes (SCAVENGER amber, FARMER
  clay, ASSESSOR ledger-blue, MAGISTRATE violet, guards steel); the
  tree's inner voice is tinted pale leaf-green with no tag — thought,
  not speech, visually distinct at a glance.
- **Stage-direction beats** (`synth_vo.py` v3 + renderer): short
  actions (≤14 words, first sentence of longer ones; camera language
  filtered out) are timed into the track as real pauses and rendered
  as centered green captions — the tree performs on screen at last.

## Deferred

- Style/character drift → regrow rail (reference conditioning).
- Cold-open anchor placement and callback micro-context → script
  grammar for FUTURE nodes (R4-adjacent: the fix touches writing);
  propose alongside the next taste conversation.

## Verdict

Pending founder screening of the 006a bench (tonight's drop).
