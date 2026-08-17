# Box queue: triage of the accumulated `failed/` pile (2026-08-17)

Read-only diagnosis of `C:\banyan-queue\failed\` on rtx5090. Nothing was
re-fired, moved or deleted. Ground truth is the box; `queue-history.json` was
deliberately not opened.

**Inventory correction.** The heartbeat says `failed: 33`; the directory holds
**35 logs** and 33 job jsons. Two entries have a log but *no* json —
`ep2-b04-balloon-pair-0813` and `ep2-b19-overhead-0812`. The heartbeat counts
jsons, so **two failures are invisible to the heartbeat**, and both belong to
the crash class below (see group 2). Any count derived from the heartbeat
undercounts by exactly those two.

## Cause groups

Return codes sort the pile first; two rc values then split across causes, so the
six cause groups are not one-to-one with rc. **35 logs, six causes:**

| group | cause | entries | rc | GPU spent |
|---|---|---|---|---|
| 1 | declared-artifact path/name mismatch | 8 | 92 | **yes, full** |
| 2 | process killed, console teardown | 2 | 3221225786 | yes, partial |
| 3 | spec aimed at a beat that cannot answer | 9 | 4 (8), 30 (1) | none |
| 4 | prompt/draft self-consistency refusal | 10 | 1 | none |
| 5 | box out of date (drafts, sampler, clone) | 5 | 4 (2), 1 (2), 2 (1) | none |
| 6 | quoting bug in a smoke probe | 1 | 1 | none |

**Thirty-five entries are six causes, and 25 of them never drew a pixel**
(groups 3–6). The guards are largely doing their job. The two expensive groups
are the ones where a check fired *after* the render instead of before it — and
group 1, the most expensive, is where the check itself was wrong.

---

## Group 1 — rc=92, "declared artifacts missing": 8 entries. FAKE FAILURES.

`ep2-b01-final055-r2-0812`, `ep2-b01-shape-0813`, `ep2-b05-scene-0814`,
`ep2-b09-scene-0814`, `ep2-b11-scene-0814`, `ep2-b12-scene-0814`,
`ep2-b18-scene-0814`, `ep2-b21-scene-0814`.

**In all eight the render step returned rc=0.** The GPU did the work, the
frames are on disk, and the job was then marked FAIL by its own closing
artifact-existence check because the *declared* filename does not match the
name the renderer actually writes. Two distinct spellings of the same bug:

- **Missing slug segment.** The spec declares
  `out-b05-scene\05-ipa-r2-w015-s0.png`; the renderer writes
  `05-the-patrol-ipa-r2-w015-s0.png` — it interpolates the beat slug
  (`the-patrol`, `the-pause`, `related`) that the declaration omits. Hits
  b05, b09, b11, b12, b18, b21.
- **Three different output paths in one job.** `ep2-b01-final055-r2` renders to
  `OUT = C:\banyan-farm\out-b01-styleprobe`, declares its artifacts under
  `C:\banyan-farm\out-b01-final055r2` (a directory that does not exist), and
  its publish step globs `out-b01-final055r2\b01-styleprobe-*` — so it
  "published 0 file(s) + manifest" and still wrote the manifest.
  `ep2-b01-shape-0813` declares `01-cold-open-LTX-shape-0813.mp4` while the
  file on disk is `01-cold-open-LTX-shapeB-0813.mp4`.

### This changes what we believe is filmed — 60 published images marked FAIL

Verified present **both** in the render dir on the box and staged under
`C:\banyan-farm\courier-box\farm-out\`, each with a complete `.sha256` manifest
whose entry count matches its file count (32 = 16 png + 16 yaml; 8 = 4 + 4):

| job | farm-out PNGs | on-box dir |
|---|---|---|
| `ep2-b05-scene-0814` | 16 | `goblin-ipa-0812\out-b05-scene` (16 png + 16 yaml) |
| `ep2-b09-scene-0814` | 16 | `goblin-ipa-0812\out-b09-scene` (16 + 16) |
| `ep2-b11-scene-0814` | 16 | `goblin-ipa-0812\out-b11-scene` (16 + 16) |
| `ep2-b12-scene-0814` | 4 | `wave-goblin-prep\out-b12-scene` (4 + 4) |
| `ep2-b18-scene-0814` | 4 | `wave-goblin-prep\out-b18-scene` (4 + 4) |
| `ep2-b21-scene-0814` | 4 | `wave-goblin-prep\out-b21-scene` (4 + 4) |

Beats **5, 9, 11** each have a complete 16-image IPA scene sheet and beats
**12, 18, 21** each have a 4-image wave sheet that the board records as
failures. Nobody has looked at them.

**And none of the six is in the repo.** `git ls-files farm-out/<job>` returns 0
for all six, and the filenames (`the-patrol-ipa`, `the-pause-ipa`,
`related-wave1`) appear nowhere in the tree. So 60 rendered, manifest-attested
images are staged in `courier-box\farm-out` on the box and were never
couriered/committed. **They exist in exactly one place.** If the box is wiped
or reimaged they are gone, and the only record of them is a `failed/` entry.

The `publish` step is implicated separately for b12/b18/b21, and my first pass
had this wrong: their publish did **not** merely fail a count assertion, it
copied **nothing**. b12's glob is
`out-b12-scene/12-wave1-s*.*` against files actually named
`12-related-wave1-s*` — the same missing-slug bug as the declaration, so it
logged `published 0 file(s) + manifest` and wrote a one-line manifest before
`SystemExit(0 if len(src) == 8 else 1)` failed it. The 8 correct files and the
correct 8-line manifest now in farm-out were put there by a **later repair**:
the manifest's mtime is 14/08 05:23 local, 44 minutes after the job finished at
04:39, and there is no rerun of b12/b18/b21 anywhere in `done\`. So the frames
were rescued by hand once and then left unpublished.

Not in farm-out but present on the box:

- `ep2-b01-final055-r2` → 2 png + 2 sidecars as
  `C:\banyan-farm\out-b01-styleprobe\b01-final055-i55-s0/s1.png`
  (plus the i25 and i40 arms of the same probe, 6 png total).
- `ep2-b01-shape-0813` → `01-cold-open-LTX-shapeB-0813.mp4` in
  `C:\banyan-farm\ep2-b01-figgrow-055-r3\`.

**Do not re-fire any of group 1.** The pixels exist; re-rendering would repay
GPU cost for frames already on disk. What these need is a look and a
declaration fix, not a re-run.

---

## Group 2 — rc=3221225786: 2 entries. THE RUNNER HAS DIED SILENTLY BEFORE.

`ep2-b19-overhead-0812` (killed 2026-08-12T19:41:50Z, mid `render`) and
`ep2-b04-balloon-pair-0813` (killed 2026-08-13T09:13:40Z, mid `encode`).

`3221225786` is `0xC000013A` = `STATUS_CONTROL_C_EXIT`, and both logs carry the
Intel Fortran runtime's console-teardown handler firing:

```
forrtl: error (200): program aborting due to window-CLOSE event
```

That is a `CTRL_CLOSE_EVENT` delivered to the process's console — something
tore the runner's console down while the box itself kept running. b19 was
**4/8 diffusion steps in (`50%|█████ | 4/8 [01:43<01:15, 18.80s/it]`)** when it
died.

**Not a WDDM bugcheck, and not a reboot.** The System event log's last
unexpected-shutdown/bugcheck triple (EventID 41 / 6008 / 1001) is
**2026-08-06** — before both kills. The only boots since are 6005 events at
2026-08-12T06:46–06:48Z, unaccompanied by 41/6008, i.e. a clean restart, and
b19 died ~13h after it with no shutdown event of any kind. So the
WDDM-thrash-bugcheck hypothesis is **rejected for this pile**: the machine
stayed up and the *process* was killed.

**These are the two entries with no json, and that is not a coincidence.** The
runner never got to write the job json back, which is exactly why the heartbeat
says 33 while the directory holds 35 logs. A silent runner death is therefore
*self-concealing*: it removes its own evidence from the failure count. This is
the third instance of today's silent-wrongness pattern — the first two being
the green canon guard that checked nothing and the runner reporting `Running`
at 0% GPU.

Scope, measured rather than assumed: the `window-CLOSE` signature appears in
**0 of the 1742 logs in `done\`**. So this is rare, not endemic — but it has
happened on two separate days and was noticed neither time.

Nothing was filmed that we think was filmed, and nothing filmed is missing:

- `ep2-b04-balloon-pair-0813` got as far as its init crop
  (`ep2-b04-balloon-pair-0813\b04-init-704x1280.png`); the LTX i2v encode never
  ran and there is **no `*balloon*` directory in farm-out**.
- `ep2-b19-overhead-0812` produced no clip. A farm-out dir `ep2-b19-overhead`
  (5 entries) exists but is undated and is not this job's output.

**Worth re-firing: both.** This is genuinely unrun GPU work destroyed by an
external kill, the only group where a re-run buys frames that do not exist.
Re-fire them attached to something that cannot be closed out from under them,
and treat a missing json in `failed/` as an alarm rather than an absence.

---

## Group 3 — spec pointed at the wrong beat: 9 entries. Zero GPU cost.

Preflight refusals, all before any pixel was drawn. Two wordings, one fault:

- rc=4, `!! beat NN (slug, kind=goblin) carries no {{GOBLIN}} marker, so the
  founder's definition would have nowhere to go and this render would test
  nothing about the goblin` — 8 entries: `ep2-goblin-design-d1`…`d6` (all six
  arms of one 2026-08-14 fan-out), `ep3-charref-assessor-0812`,
  `ep3-charref-farmer-0812`.
- rc=30, `!! beat 7 is not one of the goblin beats (2, 3, 4, 8, 13, 14, 15, 17,
  19, 20) — its draft has no goblin, so nothing it drew could answer whether
  they hold. Refusing.` — 1 entry: `ep2-b07-plate-0814`.

These are the guards working exactly as intended: loud, specific, cheap, and
they name the fix. Six of the eight are one badly-aimed fan-out, so **9 entries
are really 3 authoring mistakes** (the d1–d6 batch, the two ep3 charrefs, b07).

**Not worth re-firing as-is** — re-running reproduces the refusal. Re-aim at a
goblin/two-subject beat first. Also note d1–d6: six arms queued at once against
a beat that could not answer the question, which is ONE SAMPLE BEFORE ANY BATCH
in the negative.

## Group 4 — prompt/draft self-consistency refusals: 10 entries. Zero GPU cost.

All rc=1. Nine end with `!! FAULTS — nothing drawn:` in the `dry`/`measure`
step; the tenth (`motion-poscontrol`) is the same shape from a `verify-embeds`
step. Nothing rendered, nothing spent. Four distinct faults:

- **Style anchor lost to CLIP truncation** (5): the positive overran CLIP's
  77-token budget and the tail — including the `very aesthetic` style anchor —
  was dropped, so the render would have been off-style.
  `ep2-b06-ipa-guardcast-0812`, `ep2-b08-refresh-0811`,
  `ep2-b20-canonword-0816` **×2** (17:33 and 17:49 the same evening — the
  second is a straight re-fire of the first with the prompt unchanged, i.e.
  someone already re-fired an entry instead of the cause),
  `ep3-charref-assessor-r2-0812`.
- **Count tag vs draft disagreement** (3): `!! COUNT TAG is '2boys', draft
  declares '1boy'`. `ep2-b06-plate-0815`, `ep2-b09-scene2-0815`,
  `ep3-003b-b01-dialect-0812`.
- **Beat negates its own subject** (1): `!! peopled beat negates its own
  subject: ['boy', 'man'] — the person-singulars block belongs on plant-only
  plates only`. `ep3-sapling-reference-0812`.
- **Experiment design not what it claims** (1): `!! two arms share a positive`
  / `!! the four embeds files are not four positives against one negative`.
  `motion-poscontrol-0816`.

**Worth re-firing only after the prompt is fixed** — the guard is right in every
case. The b20 double-entry is the warning: re-firing an entry without touching
its cause just makes two entries.

## Group 5 — box is out of date: 5 entries. Confirms the divergence hypothesis.

The stale-harness/divergence hypothesis is confirmed, in three different
flavours, and one of them **failed a job today**:

- **Stale `wave-drafts.yaml` on the box** (2, rc=4) — `ep2-guard-sheet-a-0814`,
  `ep2-guard-sheet-b-0814`: `!! beat 07 (confiscate) has no
  authored_guard_sheet_a key in wave-drafts.yaml. Keys present: [...]. This
  box's copy of wave-drafts.yaml is older than the job that was queued against
  it — copy the repo's pipeline/wave-drafts.yaml over and re-run. Refusing
  rather than falling back.` A model guard: it diagnoses itself and names the
  remedy.
- **Sampler crashes instead of refusing** (2, rc=1) — the same divergence
  without a guard in front of it:
  `ep3-charref-magistrate-0812` dies `KeyError: 'kind'` at
  `wave-goblin-prep\render_wave_sample.py:193`
  (`if wg.GOBLIN_SLOT not in authored and d["kind"] != "guard"` — the draft
  entry has no `kind`), and `ep2-b04-goblin-ipa-content` dies
  `NameError: name 'CELLS' is not defined` at `goblin_ipa_sample.py:300`.
  Same root cause as the two above, but as a traceback rather than a refusal.

### The box's repo clone is two days stale — and this is still live

`C:\banyan-farm\banyan-city` is at **755036a6**, committed
**2026-08-15T22:35+04:00**. The repo is at f34436fe (2026-08-17T17:14). The
clone's `farm-out` holds **3 directories**.

That is what broke the newest failure in the pile, `ep2-b10-attrbind-eyewear-0817`
(rc=2, **today at 12:14Z**):

```
!! init not found: C:\banyan-farm\banyan-city\farm-out\ep2-b10-mac-plate-0817\10-no-form-mac-plate-r1s1.png
```

**That plate is not missing.** `farm-out/ep2-b10-mac-plate-0817/10-no-form-mac-plate-r1s1.png`
is committed and clean in the repo; it is absent from the box's clone and from
`courier-box\farm-out` only because the clone has not pulled since 08-15. So
this is not a missing dependency, it is a stale checkout — and **any queued job
whose init comes from the box's repo clone will fail the same way for anything
couriered after 2026-08-15T22:35**. This is a systemic, still-open fault, not a
one-off.

**Worth re-firing: all of group 5, after `git -C C:\banyan-farm\banyan-city pull`
and refreshing the box's `wave-drafts.yaml`.** These are real jobs blocked by a
stale box, not bad specs.

## Group 6 — trivial: 1 entry.

`autofill-proof-0816` (rc=1): a `SyntaxError: unterminated string literal` in a
one-line `python -c` autofill smoke probe — the `\n` in the string was eaten by
quoting. Not a render, no GPU, no bearing on footage.

---

## Answers to the four hypotheses

1. **Silent runner death — YES, twice, and it hides itself.** Group 2. Both
   instances predate today and neither was noticed. Not a bugcheck, not a
   reboot. Because the kill also prevents the job json being written, the
   heartbeat's `failed:` count is structurally blind to exactly this failure —
   which is why 35 logs read as 33.
2. **Frame-count threshold mismatch — present, but as a *glob* mismatch, not a
   count one.** No entry in this pile failed a `>= N` check on a correct
   directory. The 8 group-1 failures are name/path mismatches upstream of the
   count, so the counter saw 0 and was right to fail. The live `>= 16` vs 12
   specs are a separate, real bug; this pile does not add evidence for it, and
   the shape it *does* show is worse: the check passes a manifest through while
   copying nothing.
3. **Stale harness / drafts divergence — YES, 4 entries plus a live one.**
   Group 5. The box's repo clone at 755036a6 is two days behind and is still
   breaking jobs as of today.
4. **WDDM-thrash bugchecks — NO.** Last EventID 41/6008/1001 triple is
   2026-08-06, before every failure in the pile. No failure clusters with a
   reboot; the 08-12 06:46–06:48 boots carry no unexpected-shutdown events.

## Re-fire recommendation, by cause

| group | entries | re-fire? |
|---|---|---|
| 1 — artifact declaration mismatch | 8 | **No.** Frames exist. Fix declarations, look at the images, courier the 60. |
| 2 — console kill | 2 | **Yes.** Only genuinely lost GPU work. |
| 3 — wrong beat | 9 (3 mistakes) | No, re-aim first. |
| 4 — prompt self-consistency | 10 | No, fix the prompt first. |
| 5 — stale box | 5 | **Yes, after pulling the clone and the drafts.** |
| 6 — quoting bug | 1 | Trivial; fix the one-liner. |

## The most valuable single item

Group 1: 60 rendered images for beats 5, 9, 11, 12, 18 and 21 that the board
files as failures, that nobody has ever looked at, and that exist **only** on
the box. The release picture is better than the failure count says — and it is
one disk away from being worse than either.
