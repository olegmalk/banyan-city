# The stale rebase state of 2026-08-16, and what its autostash actually held

**Decision (2026-08-19): `git rebase --quit`, autostash dropped — it held nothing
that does not already exist somewhere else in this repo.** Written down because a
dropped stash is unrecoverable once gc runs, and "it looked like a duplicate" is
not a record anyone can check later.

## What was there

`.git/rebase-merge/` had sat since **Aug 16 14:45** containing exactly one file,
`autostash` → commit `41f27494d441992672cbd54bc087151784347f1f` (a stash-shaped
merge of `3472f8d9` "the guards were cast a day ago…" and `51b62444` "index on
main"). No `head-name`, no `onto`, no `git-rebase-todo` — the directory was a
husk, but it was enough to make `git status` announce "You are currently
rebasing. (all conflicts fixed: run `git rebase --continue`)" on top of every
other thing anyone read, for three days and roughly forty commits.

`--quit` and not `--abort` **because `--abort` resets HEAD to the rebase's
original branch**, and that original branch was three days and forty commits
stale. `--quit` leaves HEAD, the index and the working tree exactly as they are;
verified here — HEAD was `855beb92` before and after, and the six staged
`pipeline/jobs/ep2-b1{4,5,7}-s49*.yaml` deletions belonging to a peer lane were
still staged afterwards. (HEAD did move during the pass, to `7dd53049` — that was
another lane committing in this shared tree, not this operation. The reflog shows
no entry for the quit, which is the point.)

## What the autostash held, file by file

Git declined to discard it on `--quit` ("Autostash exists; creating a new stash
entry") and turned it into `stash@{0}`, same SHA, so the comparison below was made
against a real stash entry rather than a dangling object.

| file | verdict |
|---|---|
| `pipeline/body_motion.py` | **byte-identical** to the working tree — 0-line diff |
| `pipeline/judge_clip.py` | **byte-identical** — 0-line diff |
| `pipeline/loop/measurements-poscontrol-0816.txt` | **byte-identical** — 0-line diff |
| `pipeline/jobs/ep2-b17-s49-0815.yaml` | deletion, **already staged** in the index |
| `pipeline/jobs/ep2-b17-s49B-0815.yaml` | deletion, **already staged** in the index |
| `pipeline/measured/local-disk.yaml` | **superseded**: 3 differing lines, all of them auto-measured (`measured_on`, `free_bytes`, `cached_media_bytes`) and all of them the 2026-08-16 reading of a file whose own header says `box_cache.py disk` rewrites it. The tree carries the 2026-08-19 reading. |
| `pipeline/plate_scratch.py` | **behind, and its 17 unique lines survive elsewhere**: beat-08 plate prompt/negative strings, every one of the 17 found verbatim in `HEAD` by `git grep -F` — in `pipeline/plate_scratch.py` itself and in the `farm-out/ep2-b08-mac-plate-0816/*.yaml` provenance sidecars. The tree's copy is *ahead* of the stash (it has the 2026-08-16 "what a plate is evidence of" block the stash lacks). |

Nothing unique in any of the seven, so there was no branch worth pushing and
`stale-autostash-0816` was never created. Note that the first three survive only
as **uncommitted** working-tree edits belonging to live lanes — that is their
lanes' state to commit or revert, not this pass's, but it is why the check was
made file-by-file instead of trusting the shared filenames.

Within the gc grace window the object is still readable:
`git show 41f27494 --stat`.
