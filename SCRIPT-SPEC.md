# SCRIPT-SPEC — the T0 episode script format

Instated from `banyan-repair-brief-001.md` §5 (founder-issued, the tree's
first molt, 2026-07-25). Every T0 leaf from now on follows this. The
brief's text is the spec; this file restates it verbatim with repo
mappings noted in brackets.

## Header block

Node id · parent id · leaf id · tier · target length (60–90s) · aspect
9:16. *(Repo mapping: the node.md header block.)*

## Beat format

Timestamped beats (`00:00–00:05`, etc.). Each beat contains only what a
camera can see and a speaker can hear. **If it can't be filmed, it can't
be written.** No abstract narration of themes, no interiority except
through the POV device below.

### One beat = one shot (added 2026-07-25, loop cycle 007)

**A beat is a single shot, 3–6 seconds, carrying at most two spoken
lines.** A beat with seven lines is not a beat; it is a scene, and the
renderer will hold one image on screen while the story moves past it.
Measured on the first filmed season: one shot every 18 seconds carrying
4.4 lines each, against a short-form norm of a cut every 1.5–3s — the
founding author's verdict was *"the video is not matching the audio at
all… random video playing that isn't correlating to the script."*

Two rules follow, and both are checkable:

1. **The camera is on the referent.** Whatever the line is *about* is
   what the frame shows. When the protagonist thinks, the shot is on the
   protagonist — his lines are the ones most often orphaned, and he is
   the character a viewer must learn to read.
2. **A 60–90s episode is therefore 15–25 beats**, not 4–7. Its shot list
   (`shots.md`) is 1:1 with its beats — same numbers, same time ranges,
   one generation prompt each.

*(Repo note: story-critical physical performance — "One leaf tilts." —
must be written as a primary, filmable beat action, never buried inside a
camera-direction paragraph. The pipeline renders short stage directions
as on-screen beats; long paragraphs are treated as production language
and never reach the viewer.)*

## Cold open (R7, first ~5 seconds)

Every episode — every one, because platform feeds serve episodes out of
order — visually re-grounds the premise in one shot plus one VO line.
Example of the register:

> 00:00–00:05 — Macro shot: a tiny two-leaf banyan sapling trembling in
> wind. VO (dry, tired engineer): "Day three of being a tree.
> Capabilities: sense, grow. That's the whole changelog."

## The POV device

The protagonist cannot move or speak. His interiority is a **voiceover in
engineer register** — dry, precise, debugging the world (log entries,
capability inventories, incident reports). The world's characters speak
normally and cannot hear him. All comedy per R3 lives in the gap between
his VO and what the world does.

## Causality

Every beat is caused by the previous one. At any pause point, a viewer
can answer: what is happening, and why is it happening now.

## Ending

Exactly one clear state change (R1) stated or shown unambiguously, then
the hook (R5) as the final beat. The viewer must be able to *say the
question* the hook raises.

## Continuity

Nothing appears in an episode that isn't in its seed leaf, the shared
premise, or an explicitly committed prior node. No invented characters,
powers, lore, or names. Expansion means *rendering the beats already
implied*, not adding material.

## The comprehension gate (brief §6.4, mandatory before commit)

A fresh reader with only the script text answers: (1) who/what is the
main character; (2) what can he do and not do; (3) what happened, in two
sentences; (4) what changed by the end; (5) what question does the ending
leave. Pass = 1–4 correct and a specific, statable question for 5. Any
failure → revise and retest. No untested leaf is committed; transcripts
are recorded in the node's `sap/` as pre-release sap.
