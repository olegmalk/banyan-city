# Repair 001 — audit (brief §6.1)

Executed 2026-07-25 against `banyan-repair-brief-001.md` (founder-issued,
relayed and ordered executed by the founder in session). All four audited
scripts are **byte-identical to Phase 0** (commit 16338b8) — what the
author reviewed is exactly what is on disk, and what 001/002b's published
films were made from.

## §2 integrity — VIOLATION (repairable)

The canonical seed texts (shared premise; candidates A/B/C) were never
committed as verbatim leaf-0001 files. Phase 0 committed the *expansions*
as the founding node.mds directly; the seeds exist nowhere in the repo.
Distinctive seed phrases ("something in the system responds to him",
"…Did you just answer me?" in seed form) have zero verbatim matches.
**Repair:** instate the §2 texts as immutable seed leaves per node
(`<id>-seed.md` + provenance yaml, author: founder, verbatim from the
brief); map the brief's "leaf-0001" to these.

## PRD provenance — FLAGGED (needs the author)

The repo's `PRD.md` (217 lines, committed by the agent at Phase 0) is the
only PRD present; the author-supplied `banyan-city-PRD.md` does not exist
in the repo under that name and no byte-reference is available to verify
against. Marked here rather than guessed at: **the author should supply
the original file** so it can be committed as the canonical master.
No other agent-generated PRD variants exist (checked).

## Naming mapping (brief ↔ repo)

The repo's leaf scheme predates the brief: `<id>-t0-a` = the Phase-0
expansion (what the author reviewed), `leaf-0001` (brief) = the §2 seed,
`leaf-0002` (brief) = the new molt script = `<id>-t0-b`, becoming
node.md (the file every render tier reads).

## Per-script violations (§5 / R1–R7)

**Systemic, all four:**
- **R7 cold open: FAIL.** Every episode opens on a serial-viewing
  callback (001: pre-transformation desk scene, premise legible only at
  ~13s — measured; 002a: "The footsteps have arrived"; 002b: "The
  footsteps from 001 arrive"; 002c: "Day nine."). No episode re-grounds
  who/what/capabilities in the first ~5 seconds. This is the single
  largest script-level comprehension failure and matches the independent
  cold-viewer evidence (three context-free viewers, 6/10 comprehension).
- **§5 filmability: PARTIAL.** The VO device is respected throughout
  (interiority only via engineer-register VO). But story-critical
  *performance* — the tree's replies ("One leaf tilts."), the fig drop —
  lives in stage directions the pipeline cannot reliably film; the
  cycle-006 assembly fix (stage-direction beats) mitigates, and molt
  scripts must state such beats as filmable primary actions.

**Per node:**
- **001:** premise arrival too late (R7); protagonist unnamed as a tree
  for the first quarter. Ending/hook: PASS (statable question).
  Causality: PASS.
- **002a:** strongest §5 compliance (concrete diagnosis→fix→response
  chain); R7 open fails as above. Ending/hook PASS.
- **002b:** guard pair with a name (Dren) — §5 continuity: PASS with
  note (the seed's "a patrol" implies them; no new lore invented).
  Rapid three-party dialogue needs speaker legibility downstream (fixed
  in assembly, cycle 006). R7 open fails as above.
- **002c:** test-log structure is §5-exemplary; R7 open fails as above
  ("Day nine" presumes the premise); the corrupted ADMIN(?) label is
  mystery-not-confusion (statable question) — R7-compliant hook.

## Filmed-canon adaptation (brief written pre-film)

001 and 002b were filmed, voiced, published, and partially distributed
after the brief's snapshot. Molt handling per R6: published video leaves
REMAIN as takes of the t0-a script era; the molt script becomes node.md
(canon for all future renders, including the regrow-era re-film). Nothing
is deleted; nothing already public is retracted.
