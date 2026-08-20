# DO NOT FIRE THE SIX `ep2-b02-adultplate-*-0820` SPECS AS WRITTEN

Left here 2026-08-20 ~22:45 by the **goblin reference-route lane**, beside the
files rather than inside them: all seven of those files are still `??` in
`git status` at 22:43 with an mtime of 21:07, so they belong to whoever authored
them and this lane does not edit another lane's uncommitted work. Two separate
defects, both verified against the emitted YAML and against the driver source,
not inferred.

---

## DEFECT 1 — the publish step reports every successful render as a FAILURE

**Verified in all six specs.** Each one runs:

    --arm nocontrol

and `pipeline/controlnet_plate.py:491` names the output from the arm:

    out_png = out_dir / ("%s-%s.png" % (a.task, a.arm))

so the file that lands is `ep2-b02-adultplate-s2026082N-0820-**nocontrol**.png`.
The publish step inherited from the parent globs for

    out_dir + "/ep2-b02-adultplate-s2026082N-0820-**hintskel**.png*"

finds nothing, and ends `raise SystemExit(0 if len(files) >= 4 else 1)` — so the
job exits **rc=1 on a render that succeeded**, and the courier pushes nothing.
`artifacts:` names the `-hintskel.png` path too, so the runner's own artifact
check will miss it as well.

**This already happened tonight.** The eight `ep2-b04-tileread-v*-0820` rungs
each exited rc=0 on the render and rc=1 on the job; eight finished pictures sat
on the card while the queue said failure and had to be copied off by hand.

### The fix, three edits per spec, no re-derivation needed

1. in the publish step's `files = sorted(glob.glob(...))`, change
   `-hintskel.png*` to `-nocontrol.png*`;
2. in `artifacts:`, change `-hintskel.png` to `-nocontrol.png`;
3. re-count the `>= N` at the end of the publish step against what the glob
   list can actually return.

**Or take the structural fix instead**, which is what this lane did for its own
batch: derive from a parent whose publish glob is written off its own `--arm`.
`pipeline/jobs/ep2-jerry-skel-n1-0820.yaml` is a worked example — `--arm
posehint`, glob `-posehint.png*` — and `pipeline/derive_jerry_skel_0820.py`
shows the derivation. The general rule worth carrying into a guard: **the
publish glob and `artifacts:` must be derived from `--arm`, never typed.**

---

## DEFECT 2 — the six specs reason from canon that was retired the same night

Their `why:` reasons from *"the defect is not the adult — it is the MIX"*, and
their `prompt.txt` is the string

    lean wiry adult goblin man, green skin, bald head, patchwork cloak

verbatim. `pipeline/canon.yaml` → `correction_2026_08_20` **strikes `adult` as
steward drift**: the founder ruled on tile B's *pixels*, not on the sentence
printed beside them, and that sentence contains `adult` and `man` while the
picture contains neither. Fired as written these six render the man-read six
more times — which is the exact defect beat 02 is on the re-render list for.

**The wording is solved and it is not this one.** The ratified recipe
(`work-ladder-0819.md`, rung v6, four-for-four on the tile bar) is:

    masterpiece, best quality, very aesthetic, 1other, solo, colored skin,
    green skin, bald, patchwork cloak, blank eyes, tsurime, jitome, no nose,
    closed mouth, :|, expressionless, <framing>
    neg: lowres, worst quality, low quality, text, watermark, pointy ears,
    long pointy ears, elf, monster boy, pointy nose, dot nose, human face,
    wrinkled skin, old man, thick eyebrows, hair, beard, child, chibi,
    grey skin, pale skin, 2boys

Two live caveats on it, both from tonight and both measured:

- `patchwork cloak` **paints the skull** — stitch marks and a red patch on the
  head in six of eight rungs. `ep2-b04-tilefix-w1..w3-0820` were filed against
  exactly this.
- **The recipe holds the FACE and loses the BODY.** Twelve poses off it are
  twelve bobbleheads — head about a third of standing height where the tile is
  a fifth to a sixth. Beat 02's own recorded defect is *"round child cranium and
  body"*, so a beat-02 plate that adopts the recipe without a body instrument
  swaps one child-read for another. The body instrument is being fought right
  now in `ep2-jerry-skel-n1..n8-0820`; **read that verdict on the ladder before
  authoring a beat-02 plate**, and note beat 02's other break is that he is
  **bone grey, not green** — `grey skin` and `pale skin` are already in the
  negative above.

---

## STATUS AT THE TIME OF WRITING

- **Nothing has been touched.** No edit to any of the seven files, no enqueue.
- **None of the six is queued.** `C:\banyan-queue\{ready,running,backlog}` held
  no `ep2-b02-adultplate-*` entry at 22:43, and none is in `farm-out/`.
- If the authoring lane is gone and nobody has claimed these by the next pass,
  fixing them in place is the right call — but re-deriving them off the
  corrected canon is better than repairing the wording of a retired premise.
