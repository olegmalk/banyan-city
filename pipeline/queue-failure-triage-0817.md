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

Return codes partition the pile cleanly:

| rc | step | entries | cause |
|---|---|---|---|
| 92 | publish / artifact check | 8 | declared-artifact path & name mismatch (group 1) |
| 3221225786 | render / encode | 2 | process killed — `0xC000013A` (group 2) |
| 4 | measure | 10 | (group 3) |
| 1 | various | 13 | (group 4) |
| 30 | dry | 1 | (group 5) |
| 2 | mask | 1 | (group 6) |

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

Verified present **both** on the box and under
`C:\banyan-farm\courier-box\farm-out\` (i.e. already couriered into the repo,
not just sitting on the box):

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
failures. Nobody has looked at them. b12/b18/b21 additionally had `publish`
itself return rc=1 — the copy succeeded and the trailing
`len(src) >= N` count assertion is what failed, so those four-image sets are
complete *as rendered*, just short of what the spec expected to see.

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
