# v1's three sample frames, recovered from the results branch

THESE WERE NEVER ON `main`. The v1 training job published them to
`farm-out/lora-sapling-0822/` on `farm-results-rtx5090` and nowhere else, and
on 2026-08-22 the **v2** job published its own three frames over the same
path — because the v1->v2 path rewrite in `train-sapling-v2-0822.yaml` matched
`C:\banyan-farm\lora-sapling-0822` and the publish destination string
`courier-box\farm-out\lora-sapling-0822` does not contain it. That is this
lane's defect, it is recorded in the train spec, and the spec is fixed for any
re-run.

**Nothing was lost.** Both blobs are in the results branch's history and both
are recovered here, on `main` this time, under names that cannot collide:

| directory | run | recovered from |
|---|---|---|
| `farm-out/lora-sapling-v1-samples-0822/` | v1, 44 frames | `b99c6c257` |
| `farm-out/lora-sapling-v2-samples-0822/` | v2, 59 frames | `b34fc57ae` |

Neither directory is renamed on the box and neither spec is edited to describe
a run it did not produce — the same ruling the sapnat4 misfiling was settled
under. What changed is that both are now durable on `main` instead of living
only on a branch that the next same-named job would overwrite again.
