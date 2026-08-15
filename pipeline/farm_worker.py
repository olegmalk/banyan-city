#!/usr/bin/env python3
"""The farm worker — one script that turns any capable machine into a renderer.

Born 2026-07-29, the day the RunPod heartbeat pattern was proven: a worker
clones the repo, renders candidate stills with the exact recipe the whole
project uses, and pushes results to its own branch with a heartbeat at every
stage. This generalizes that worker from "a rented pod" to "any machine" —
the family laptop farm first, and later any contributor's GPU (D11/D12: the
same script IS the compute-donation daemon; a stranger running it is a
citizen watering the tree with cycles instead of clips).

    python3 pipeline/farm_worker.py --name dads-msi [--once]

Loop: poll pipeline/farm-queue.yaml on origin/main; when it lists work for
--name (or "any"), render those beats and push to farm-results-<name>;
repeat. The steward merges results to ballots, credits the machine's owner
in the watering ledger (type: compute), and clears the queue entry.

- picks the best device it has: cuda -> mps -> refuse (cpu is not worth the
  electricity for SDXL; a machine without a real GPU should not be farming)
- §6 gate: renders only founder-approved nodes, same as every other tool
- MPS is fp32 (fp16 NaNs to black — the 2026-07-27 lesson); cuda uses
  bf16/fp16 by capability, same as runpod_render
- heartbeats + full log ship with every stage; a silent worker is impossible

Queue entry shape (pipeline/farm-queue.yaml):
    tasks:
      - id: r12                # unique; results land on farm-results-<name>
        worker: any            # or a specific --name
        node: 001-capability-inventory
        beats: "4,6"
        seeds: 4
        init: ""               # optional repo-relative path (img2img)
        strength: 0.5
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))

QUEUE = "pipeline/farm-queue.yaml"
POLL_SECONDS = 60
# How many times a task may be ATTEMPTED before this worker stops picking it up.
# 2 = one retry for a transient drop, then move on — see heartbeat_attempts().
MAX_ATTEMPTS = 2
# Child exit codes that mean "a human or the OS stopped this", not "this task is
# broken". Windows reports both as NTSTATUS values in the exit code, and the
# render is usually minutes or tens of minutes in when it happens.
INTERRUPT_EXITS = (
    3221225786,   # 0xC000013A STATUS_CONTROL_C_EXIT — Ctrl+C, or a second
                  # worker started on top of a running one
    3221225794,   # 0xC000013B STATUS_PIPE_BROKEN — console went away mid-write
    -1073741510,  # the same 0xC000013A seen as a signed 32-bit value
)


def sh(*args, check=True, capture=False):
    # encoding= is not optional. `text=True` alone decodes with the LOCALE
    # codec, which on Windows is cp1252 — and the queue yaml legitimately holds
    # an em dash and the Chinese terms from Wan's negative prompt. cp1252 hits
    # 静 (E9 9D 99), raises UnicodeDecodeError inside subprocess's reader
    # THREAD, and the exception never reaches this frame: .stdout is simply set
    # to None, so the caller dies later with "'NoneType' has no attribute
    # 'read'" and nothing points at the encoding (2026-08-02, the 5090 could
    # not read a queue it had fetched fine).
    return subprocess.run(args, cwd=REPO, check=check, capture_output=capture,
                          text=True, encoding="utf-8", errors="replace")


_stale_fetches = 0


def queue_head():
    """The queue as of origin/main, without touching the working tree.

    The fetch used to run `-q ... check=False`. When it failed, this read a
    STALE origin/main and returned whatever the queue said the last time the
    network worked — and since every task in that old queue was already in the
    worker's done set, the console printed "queue empty for me" and the machine
    idled for hours next to five queued jobs (2026-08-01, after the 5090's
    network dropped). "I can't see the queue" and "the queue is empty" are
    opposite facts and they looked identical.
    """
    global _stale_fetches
    r = sh("git", "fetch", "origin", "main", check=False, capture=True)
    if r.returncode:
        _stale_fetches += 1
        print(f"!! FETCH FAILED ({_stale_fetches} in a row) — the queue below is "
              f"STALE, not empty; this machine cannot see new work.\n"
              f"   {(r.stderr or r.stdout or '').strip()[-300:]}", flush=True)
    elif _stale_fetches:
        print(f"fetch recovered after {_stale_fetches} failure(s)", flush=True)
        _stale_fetches = 0
    r = sh("git", "show", f"origin/main:{QUEUE}", check=False, capture=True)
    if r.returncode != 0:
        # THE SAME FACT AS THE TWO BRANCHES EITHER SIDE OF THIS ONE, and it was
        # the only one of the three that said nothing. A worker whose origin/main
        # ref is missing (a fresh or re-imaged clone that has never fetched), or
        # one where the queue file moved, printed "queue empty for me" once a
        # minute forever beside a queue full of work. The whole docstring above
        # is about that distinction; this branch was left out of it.
        print(f"!! CANNOT READ {QUEUE} at origin/main (git show exit "
              f"{r.returncode}) — this is NOT an empty queue, it is a queue this "
              f"machine cannot see.\n"
              f"   {(r.stderr or r.stdout or '').strip()[-300:]}", flush=True)
        return []
    if not r.stdout:
        # Exit 0 with no text = the read itself broke (decode failure in the
        # reader thread sets .stdout to None). Say so; do NOT return [], which
        # this worker would print as "queue empty for me" and idle on.
        print("!! queue read returned NOTHING at exit 0 — cannot see the queue; "
              "this is not an empty queue.", flush=True)
        return []
    try:
        parsed = yaml.safe_load(r.stdout) or {}
    except yaml.YAMLError as e:
        # A MALFORMED QUEUE MUST NOT KILL THE DAEMON. This raised straight out of
        # queue_head into main(), which has no handler, so one lane pushing a
        # queue with a bad indent would end unattended rendering on the 5090 until
        # a human logged in to restart the worker. It is the sharpest version of
        # loud-taken-too-far: the queue is fixable in one push, but nothing is
        # left running to notice the fix.
        #
        # Loud and alive instead: say what broke, treat the queue as unreadable
        # (which prints as such above, never as empty), and poll again — the next
        # good push is picked up without anyone touching the box.
        print(f"!! {QUEUE} at origin/main DOES NOT PARSE ({type(e).__name__}) — "
              f"treating as unreadable, NOT as empty. The worker stays up and will "
              f"re-read it every {POLL_SECONDS}s; fix the file and it resumes.\n"
              f"   {str(e).strip()[:300]}", flush=True)
        return []
    return parsed.get("tasks", []) or []


def pick_device():
    import torch
    if torch.cuda.is_available():
        cap = torch.cuda.get_device_capability()[0]
        return "cuda", (torch.bfloat16 if cap >= 8 else torch.float16)
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps", torch.float32          # fp16 NaNs to black on MPS
    raise SystemExit("no cuda or mps device — this machine should not farm")


class Courier:
    """Heartbeats + results on farm-results-<name>, RunPod-boot style."""

    def __init__(self, name: str):
        self.branch = f"farm-results-{name}"
        self.out = REPO / "farm-out"
        self.log = []
        self.unpushed = 0
        # the task currently in flight, set by the loop below. video_task names it
        # in VIDEO_DEAD so a failure line stands on its own instead of relying on
        # whoever reads it to scroll up to the last STARTED.
        self.task = None

    def mark(self, stage: str):
        self.out.mkdir(exist_ok=True)
        stamp = time.strftime("%H:%M:%SZ", time.gmtime())
        # utf-8 on every WRITE too, not just prints: Windows defaults these to
        # cp1252, and the log carries Wan's Chinese negative prompt plus the
        # em-dashes from shots.md, so writing it raised UnicodeEncodeError and
        # killed the worker mid-task (the 5090, 2026-07-31). Fifth cp1252
        # casualty; the lesson each time is that logging must not be able to
        # kill the thing it logs.
        with (self.out / "heartbeat.txt").open("a", encoding="utf-8") as f:
            f.write(f"{stamp} {stage}\n")
        (self.out / "worker-log.txt").write_text("\n".join(self.log[-400:]),
                                                 encoding="utf-8", errors="replace")
        sh("git", "checkout", "-qB", self.branch, check=False)
        sh("git", "add", "-A", str(self.out), check=False)
        # PATHSPEC, NOT THE WHOLE INDEX. The add above was correctly scoped and
        # the commit under it was not: a bare `git commit` writes everything
        # staged, and this runs on a five-minute timer in a checkout a human or
        # another script may be using. Anything they had staged got swept into a
        # heartbeat commit titled "hb: <stage>" and force-pushed to a courier
        # branch — their work under our message, on a branch nobody reads for
        # content. With `-- <path>` git commits the working-tree state of that
        # path and leaves the rest of the index untouched, so the two lines now
        # agree about what this commit is for.
        # Note for whoever reads a heartbeat that still looks wrong: this only
        # takes effect on a box once its checkout turns over.
        c = sh("git", "commit", "-qm", f"hb: {stage}", "--", str(self.out),
               check=False, capture=True)
        # AND READ WHAT THE COMMIT SAID. Only the push below was checked, so a
        # commit that failed — an index.lock held by one of the other lanes
        # sharing this checkout is the everyday way — left the push to succeed
        # against the PREVIOUS state and say nothing. The courier then printed
        # its usual silence, which reads as delivered, while the branch stopped
        # advancing: the same "a courier that cannot deliver has to SAY SO"
        # lesson as the push, one call earlier. box_runner.Courier._publish has
        # checked this since it was written; this one had not caught up.
        #
        # "nothing to commit" is not a failure: mark() runs on a timer and most
        # ticks change nothing but the heartbeat line, and an unchanged tree is
        # the normal quiet case.
        if c.returncode and "nothing to commit" not in (
                (c.stdout or "") + (c.stderr or "")):
            print(f"!! HEARTBEAT COMMIT FAILED — the push below will ship the "
                  f"PREVIOUS state, so this stage ({stage}) is not on the branch\n"
                  f"   {((c.stderr or '') + (c.stdout or '')).strip()[-300:]}",
                  flush=True)
        # The push is the ONLY thing that makes any of this visible, and it ran
        # with its error suppressed AND -q. On 2026-08-01 the 5090 rendered its
        # way through the whole queue — "7 task(s) done this session" — while
        # GitHub received nothing for nearly six hours. From outside it looked
        # like a hung machine; the work was on disk the whole time. A courier
        # that cannot deliver has to SAY SO, or the heartbeat is theatre.
        r = sh("git", "push", "-f", "origin", self.branch,
               check=False, capture=True)
        if r.returncode:
            self.unpushed += 1
            print(f"!! PUSH FAILED ({self.unpushed} in a row) — results are on "
                  f"local disk only, in {self.out}\n"
                  f"   {(r.stderr or r.stdout or '').strip()[-400:]}", flush=True)
        elif self.unpushed:
            print(f"push recovered after {self.unpushed} failure(s)", flush=True)
            self.unpushed = 0

    def say(self, line: str):
        print(line, flush=True)
        self.log.append(line)

    def blame(self, text: str):
        """Append a failure to a log NOTHING later overwrites.

        worker-log.txt is rewritten from self.log on every mark(), and self.log
        starts empty in a new process — so when a task failed and the next task
        marked STARTED, the traceback was erased. AnimeGen failed after 76 minutes
        on 2026-08-01 and its error survived nineteen seconds; by the time anyone
        looked, worker-log.txt was zero bytes.

        A diagnosis that can be overwritten by routine progress is not a
        diagnosis. This file only ever grows.
        """
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with (self.out / "errors.txt").open("a", encoding="utf-8",
                                            errors="replace") as f:
            f.write(f"\n===== {stamp} =====\n{text}\n")


def lock_path(name: str) -> Path:
    """Outside the repo on purpose: farm-out is committed and force-pushed by
    Courier.mark(), and a lock file living there would be shipped to the branch
    and then clobbered by the other worker — the very thing it exists to stop."""
    return Path(tempfile.gettempdir()) / f"banyan-farm-{name}.lock"


def acquire(name: str, force: bool = False) -> Path:
    """One worker per machine handle. Exits rather than sharing a GPU.

    TWO of these ran on the 5090 on 2026-07-31 — started 21 minutes apart, both
    polling the same queue, both claiming the same tasks. The heartbeat shows it
    plainly: `2x STARTED task=vid-720p-all-1785529520`, two prefetch starts, and
    two timeouts firing at 14430s and 14404s against a 14400s limit.

    The damage was not just duplicated effort. Single beats had been rendering in
    ~13 minutes; under contention the same work took ~26. That is what made an
    8-clip batch overrun four hours and lose everything — the batch was sized
    against uncontended throughput and then run at half of it. Both processes
    also `git push -qf` the same branch from the same working tree, so results
    can erase each other.

    O_CREAT|O_EXCL, and NO automatic staleness takeover: two workers racing to
    decide whose lock is stale is the same bug wearing a hat. A human starts this
    process, so a human can clear a stale lock — the message says how.
    """
    lock = lock_path(name)
    if force and lock.exists():
        lock.unlink()
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        try:
            held = lock.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            held = "(unreadable)"
        raise SystemExit(
            f"another worker already holds this machine: {held}\n"
            f"Two workers on one GPU halve each other's speed and overwrite each\n"
            f"other's results — that is what cost the 8-clip 704x1280 batch four\n"
            f"hours on 2026-07-31.\n\n"
            f"If the other window is still open, close THIS one — nothing is lost.\n"
            f"If nothing else is running, the lock is stale:\n"
            f"  del {lock}\n"
            f"or start with --force to clear it.")
    with os.fdopen(fd, "w") as f:
        f.write(f"pid {os.getpid()} started {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    return lock


def release(lock: Path) -> bool:
    """Drop the lock only if this process is the one holding it."""
    try:
        held = lock.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if f"pid {os.getpid()} " not in held + " ":
        print(f"not releasing {lock.name}: held by another worker ({held.strip()})",
              flush=True)
        return False
    lock.unlink(missing_ok=True)
    return True


def heartbeat_attempts(text: str) -> tuple:
    """`(done_ids, attempts_by_id)` from heartbeat text. Pure: no disk, no git.

    COUNT STARTS, NOT FAILURES. This used to count `FAIL task=<id>` lines, and a
    FAIL line only exists if the worker SURVIVES the failure — so every failure
    mode that takes down the OS was invisible to the attempt counter. On
    2026-08-04 (DIAG-20260804.md) an AnimeGen task crashed its child at
    0xC0000005 and then bluescreened the host; the heartbeat holds exactly one
    line about it:

        07:12:18Z STARTED task=bench-animegen-b01-1785827400 beats=1 on cuda

    No FAIL, therefore 0 recorded attempts, therefore a restarted worker treats
    a task that just killed the machine as brand new — forever. A guard that
    only learns from failures it survived cannot stop a crash loop.

    `STARTED` is written BEFORE the render begins and was pushed and survived the
    bluescreen, so it is the one record every attempt leaves behind.

    Three corrections on top of a naive start count:

    - DONE excludes. A completed task is finished, not abandoned, and must never
      be reported as "failed Nx already".
    - INTERRUPTED subtracts. A console interrupt is not a failed render (the
      window-CLOSE on 2026-08-02, the second worker on 2026-08-03), and the task
      loop deliberately marks it so it costs no attempt. Counting its START back
      in would undo that.
    - max() with the FAIL count, so a history whose STARTED lines predate this
      change still counts its failures.

    RE-QUEUES ARE UNAFFECTED because ids carry an epoch stamp — queue_keeper
    writes `f"{slug}-msi-{stamp}"` with `stamp = int(time.time())`, and the
    hand-written entries follow it (`bench-animegen-b01-1785827400`). A re-queue
    is a NEW id with a zero count. Re-queueing the same id verbatim keeps the old
    count, which is the conservative half of the trade and is what the skip
    message tells the reader to fix.
    """
    done, starts, interrupts, fails = set(), {}, {}, {}
    # \b so a future `RESTARTED task=` mark cannot be read as a start
    for line in text.splitlines():
        for pat, bucket in ((r"\bSTARTED task=(\S+)", starts),
                            (r"\bINTERRUPTED task=(\S+)", interrupts),
                            (r"\bFAIL task=(\S+)", fails)):
            m = re.search(pat, line)
            if m:
                bucket[m.group(1)] = bucket.get(m.group(1), 0) + 1
        m = re.search(r"\bDONE task=(\S+)", line)
        if m:
            done.add(m.group(1))
    attempts = {}
    for tid in set(starts) | set(fails):
        attempts[tid] = max(starts.get(tid, 0) - interrupts.get(tid, 0),
                            fails.get(tid, 0), 0)
    return done, attempts


def farm_result_heartbeats():
    """Every `farm-results-*` heartbeat on origin as one blob of text, or None.

    NONE MEANS "COULD NOT READ", and that is a different fact from "nobody has
    finished anything" — the same distinction queue_head() had to learn on
    2026-08-01, one level down. An empty done set is what re-renders the whole
    queue, so a failed read must never be able to produce one; the caller falls
    back to this machine's own file and says so out loud.

    EVERY BRANCH, not `farm-results-hand` alone. The hand ledger is what prompted
    this (a hand-run that claims a queue id writes its STARTED and DONE there —
    claim_task.HAND_BRANCH), but globbing is what queue_promoter and the status
    page already do (queue_promoter.fetch_heartbeats), and it buys one thing the
    hand ledger cannot: a re-imaged box, or one whose farm-out was wiped, reads
    its OWN completed history back off its OWN branch instead of re-rendering
    everything it has ever rendered.

    Stale refs beat no refs. If the fetch fails but remote-tracking branches are
    already on disk, their text is returned rather than None: `DONE` is monotone,
    an id that finished does not un-finish, so an old copy can only ever
    under-report — and under-reporting is exactly the conservative direction.
    """
    fetched = sh("git", "fetch", "-q", "origin",
                 "refs/heads/farm-results-*:refs/remotes/origin/farm-results-*",
                 check=False, capture=True).returncode == 0
    refs = sh("git", "for-each-ref", "--format=%(refname:short)",
              "refs/remotes/origin/farm-results-*", check=False, capture=True)
    texts = []
    for ref in (refs.stdout or "").split():
        hb = sh("git", "show", f"{ref}:farm-out/heartbeat.txt",
                check=False, capture=True)
        if hb.returncode == 0 and hb.stdout:
            texts.append(hb.stdout)
    if texts:
        return "\n".join(texts)
    # no text at all: only an honest fetch can call that an empty ledger
    return "" if fetched else None


def finished_tasks(courier: Courier, fetch=farm_result_heartbeats) -> tuple:
    """`(ids not to pick up, {id: attempts} for the ones we gave up on)`.

    `done_ids` used to live only in memory, and this worker RESTARTS ITSELF
    whenever pipeline code changes on main — so any push during a long task
    meant the finished task ran again from zero on the next poll. A 4-hour
    720p batch would have been rendered twice for nothing (caught before it
    happened, 2026-08-01, with an 8-clip batch mid-flight).

    The heartbeat already records every completion as `DONE task=<id>`, so the
    answer was on disk the whole time. Reading it back makes a restart cheap,
    which is what lets the self-update behaviour stay aggressive.

    A FAILED task retries — a dropped download or a transient CUDA error
    deserves another go, which is why only DONE counted here at first. But
    "retry forever" is its own bug: a task that fails by hitting its own
    timeout burns the full timeout EVERY attempt, and because this worker
    processes the queue in order, the tasks behind it never run at all. A
    4-hour video batch that times out would have looped 4 hours at a time
    while the licence-clean re-render queued behind it starved (the exact
    shape of the 8-clip 704x1280 batch in flight on 2026-08-01).
    One retry, then leave it alone and let the queue move.

    SILENT. This used to print "giving up so the queue can move" for every task
    that had ever failed twice — including tasks deleted from the queue hours
    earlier, on every single startup, forever. Alarming messages about work
    nobody is waiting on train you to ignore the log, which is the opposite of
    what a heartbeat is for. The skip is still recorded; the WARNING now happens
    in the task loop, where we know the task is actually queued (and once).

    IT IS NOT ONLY THIS MACHINE'S LEDGER ANY MORE. A hand-run that borrows a
    queue id is obliged to claim it (the 2026-08-08 ruling at the top of
    farm-queue.yaml) and claim_task writes that id's STARTED and DONE to
    `farm-results-hand` — but this function opened one file on one disk, so a
    hand-completed id stayed invisible to every worker and its entry read as
    unstarted for as long as it sat in `tasks:`. On the night of 2026-08-09 every
    entry in `tasks:` was a hand-run on a queue id, which made each finished one a
    ghost re-render waiting for the next worker to wake up on the 5090.

    THE UNION TAKES `DONE` AND NOTHING ELSE. Another lane's STARTED or FAIL is
    that lane's attempt, not this worker's; counting it would let a hand run
    exhaust a task's retries on a machine that has never touched it, and the
    machine would then skip work nobody is doing. `attempts` is therefore still
    read from the local file alone, and only the done set is widened.

    `fetch` is injected so this stays testable without a network (the queue entry
    that asked for this fix asked for exactly that): it returns heartbeat text, or
    None for "could not read", which falls back to the local file and never to an
    empty set. And the word for the queue file's PLANNING list is deliberately
    not spelled anywhere in this module, not even in a comment: a test asserts
    this file never mentions it, so that no reader can mistake prose for a code
    path into work that is gated on purpose.
    """
    hb = courier.out / "heartbeat.txt"
    text = hb.read_text(encoding="utf-8", errors="replace") if hb.exists() else ""
    done, attempts = heartbeat_attempts(text)
    try:
        shared = fetch()
    except Exception as e:                       # noqa: BLE001 — a read, not the job
        print(f"!! farm-results-* ledger read raised {type(e).__name__}: {e}",
              flush=True)
        shared = None
    if shared is None:
        print("!! could not read the farm-results-* ledgers — using THIS machine's "
              "heartbeat alone. Work another lane already finished may be picked "
              "up again; this is a stale view, not an empty one.", flush=True)
    else:
        done |= heartbeat_attempts(shared)[0]
    gave_up = {tid: n for tid, n in attempts.items()
               if n >= MAX_ATTEMPTS and tid not in done}
    return done | set(gave_up), gave_up


def still_sidecar(model, task, beat, seed, size, steps, prompt, negative,
                  init=None, strength=None, init_crop=None) -> str:
    """§7.2 provenance beside a generated STILL. Pure — returns the text.

    THE VIDEO PATH HAS HAD THIS SINCE 2026-08-02 AND THE STILLS PATH NEVER DID.
    `video_task.write_sidecar` was written because clips were landing on the
    courier branch as bare mp4s with the model recorded nowhere; the frames
    beside them were landing the same way and nobody noticed, because a still
    looks self-explanatory in a way a clip does not. It is not. A png on the
    courier branch answers none of: which model drew it (a bake-off task can
    name any open model in `model:`), which seed, which of the four seeds in
    the batch, how many steps, and — the one that has actually cost us time —
    what prompt it was given AFTER compress() got through with it.

    That last one is the reason this is not cosmetic. §7.2 says every render
    publishes model, prompt and cost. sd_prompt.compress() rewrites the shot's
    text to fit CLIP's 77 tokens, and what the model saw is the compressed
    string, not the one in shots.md. On 2026-08-02 a beat came back wrong and
    telling a bad direction from a bad model meant re-running the pipeline to
    reconstruct the string, because it existed nowhere on disk. Record what was
    actually asked for, not what we meant to ask for.

    LICENCE COMES FROM THE GATE, not from a table kept here. licence_gate is
    the thing that will later refuse or pass this frame, so asking it now means
    the sidecar can never disagree with the tool that judges it — and a model
    it does not know gets "UNVERIFIED" rather than a hopeful Apache-2.0. A
    wrong allow is the direction that publishes things.
    """
    import licence_gate as lg
    from video_task import _yaml_block, worker_id

    lic = lg.engine_licence(model) or "UNVERIFIED — licence not read"
    text = (
        "# Still provenance (7.2) — written by farm_worker at render time\n"
        # Same generic "local-gpu (<worker>)" spelling the video path uses, and
        # for the same reason: the gate classifies on the prefix, so the form is
        # recognised on ANY machine while still naming which one drew the frame.
        # Spelling it "local-dads-msi" made every clip from a new handle an
        # unclassified violation once already.
        # And the same worker_id() the video path uses as of 2026-08-08, for the
        # same reason: `task['worker']` is a routing field, and the hostname it
        # otherwise fell back to is "MSI" on both boxes.
        f"platform: local-gpu ({worker_id(task)})\n"
        f"model: {model}\n"
        f"model_licence: {lic}\n"
        f"shot_beat: {beat}\n"
        f"size: {size}\n"
        f"steps: {steps}\n"
        f"guidance: {task.get('guidance', 7.5)}\n"
        f"seed: {seed}\n"
        f"seeds_in_batch: {int(task.get('seeds', 4))}\n"
        f"task: {task.get('id')}\n"
        "cost_usd: 0\n")
    # img2img only. An absent field reads as "not measured"; a `strength: none`
    # on a txt2img frame reads as a measurement of nothing.
    if init:
        text += f"init: {init}\nstrength: {strength}\n"
        # AND WHICH PIXELS OF IT THE MODEL SAW. The init used to be stretched to
        # the target shape by a bare resize (fixed 2026-08-08), and the reason
        # that survived is that the record said `init: <path>` and stopped —
        # naming a file is not naming a framing. Double-quoted: the note carries
        # "policy: scale to cover", and a colon-space in a plain scalar is a
        # parse error that takes licence_gate down with the sidecar.
        if init_crop:
            text += f'init_crop: "{init_crop}"\n'
    return text + _yaml_block("prompt", prompt) + _yaml_block("negative", negative)


_WEIGHTS_VERDICT = None


def require_intact_weights(courier=None) -> None:
    """Refuse to render if this machine's weight files are not really there.

    macbook1 and macbook3 rendered SDXL as pure noise for days because their
    5.1 GB UNet blob had the exact right length and was 88%/93% zeros -- an
    rsync that left holes. Nothing errored. Every size, file-count and
    manifest check passed, and a lane burned 22 seeds partly around it. A
    worker that hands back noise is worse than one that stops, so this stops.

    Once per process: the audit reads the cache, which costs a few seconds
    against a task that costs minutes, but there is no reason to repeat it.
    """
    global _WEIGHTS_VERDICT
    if _WEIGHTS_VERDICT is None:
        import mac_preflight
        _WEIGHTS_VERDICT = mac_preflight.weights_ok()
    ok, why = _WEIGHTS_VERDICT
    if ok:
        return
    msg = ("!! REFUSING TO RENDER — this machine's model weights fail a content "
           "check, so anything it produced would be noise:\n  " + "\n  ".join(why)
           + "\n  Repair with a verified copy (hash the result against the blob's "
             "own name), then re-run: python3 pipeline/mac_preflight.py")
    if courier is not None:
        # MARK IT, not just print it — a print dies with the console, and the
        # whole point is that someone outside the room learns this machine is
        # not usable rather than reading its noise as art.
        try:
            courier.blame(msg)
        except Exception:
            pass
    raise SystemExit(msg)


def render_task(task: dict, courier: Courier, device: str, dtype) -> None:
    # video tasks live in their own venv (Wan needs a modern diffusers; the
    # stills path is pinned to 0.29.2 for SDXL) — dispatch before importing
    # anything from this process's pinned stack
    if task.get("video"):
        d = REPO / "genomes/sapling/nodes" / task["node"]
        leaves = sorted((d / "leaves").glob("*-t0-*.yaml"))
        who = str((yaml.safe_load(leaves[-1].read_text(encoding="utf-8")) or {}).get(
            "approved_by", "none")) if leaves else "none"
        if not who.startswith("founder"):
            raise SystemExit(f"{task['node']} NOT founder-approved — STEWARDSHIP §6")
        import video_task
        return video_task.run(task, courier, d)

    from generate_shots import parse_shots
    from sd_prompt import beat_negative, compress
    import torch
    from diffusers import (StableDiffusionXLImg2ImgPipeline,
                           StableDiffusionXLPipeline)

    NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, "
           "low quality, blurry, extra limbs, deformed, jpeg artifacts, "
           "realistic skin texture")
    # task may name another OPEN model (bake-offs); default = house model
    BASE = task.get("model") or "cagliostrolab/animagine-xl-3.1"
    SEED = int(task.get("seed_base", 20260719))

    d = REPO / "genomes/sapling/nodes" / task["node"]
    leaves = sorted((d / "leaves").glob("*-t0-*.yaml"))
    who = str((yaml.safe_load(leaves[-1].read_text(encoding="utf-8")) or {}).get(
        "approved_by", "none")) if leaves else "none"
    if not who.startswith("founder"):
        raise SystemExit(f"{task['node']} NOT founder-approved — STEWARDSHIP §6")

    init_rel = task.get("init") or ""
    cls = StableDiffusionXLImg2ImgPipeline if init_rel else StableDiffusionXLPipeline
    require_intact_weights(courier)
    pipe = cls.from_pretrained(BASE, torch_dtype=dtype, use_safetensors=True)
    pipe.to(device)
    courier.mark(f"MODEL_LOADED {device}/{dtype}".replace("torch.", ""))

    # encoding pinned: Windows defaults to cp1252, which mangles the em-dash
    # in "## Beat NN —" headings and parse_shots finds zero beats (KeyError,
    # the msi worker's first-light failure, 2026-07-29)
    shots = {s["num"]: s for s in parse_shots((d / "shots.md").read_text(encoding="utf-8"))}
    # a task may carry its own prompt (world-reference renders anchored to an
    # APPROVED node's world — §6 checked above; slug names the output)
    if task.get("prompt"):
        jobs = [{"num": 0, "slug": task.get("slug", "custom"),
                 "prompt": task["prompt"]}]
    else:
        jobs = [shots[int(b)] for b in str(task["beats"]).split(",")]

    # ONCE PER TASK, NOT ONCE PER SEED — these are all read off `task` and never
    # vary inside the loops below, and the init image in particular was being
    # decoded and resampled again for every one of the four seeds.
    w, h = int(task.get("width", 832)), int(task.get("height", 1216))
    steps = int(task.get("steps", 40))
    init_img, init_crop = None, None
    if init_rel:
        # NOT `.resize((w, h))`, which is what stood here until 2026-08-08 and
        # is the same defect plate_prep.py was written for: two arguments, no
        # aspect term, so an 832x1216 canon still handed to a task targeting any
        # other shape was silently pulled to fit. img2img keeps the init's
        # composition by construction — a stretched init is a stretched output,
        # for every seed, with nothing in the record saying so.
        #
        # Refuse means CROP, on render_t3's own cover-centre policy, so a farm
        # frame is anchored to the composition the episode would show. Same call
        # wan_i2v.load_init makes, deliberately — one policy, one helper.
        from PIL import Image

        import plate_prep

        with Image.open(REPO / init_rel) as raw:
            init_img, crop = plate_prep.fit_cover(raw.convert("RGB"), w, h)
        init_crop = crop["crop_note"]
        if crop["box"] is not None:
            courier.say(f"  init {Path(init_rel).name}: {init_crop}")

    for s in jobs:
        num = s["num"]
        ptext, _ = compress(s["prompt"])
        neg = beat_negative(NEG, s["prompt"])
        for k in range(int(task.get("seeds", 4))):
            t0 = time.time()
            seed = SEED + num + k * 1000
            g = torch.Generator(device="cpu").manual_seed(seed)
            kw = dict(prompt=ptext, negative_prompt=neg,
                      num_inference_steps=steps,
                      guidance_scale=7.5, generator=g)
            if init_img is not None:
                kw["image"] = init_img
                kw["strength"] = float(task.get("strength", 0.5))
            else:
                kw["width"], kw["height"] = w, h
            img = pipe(**kw).images[0]
            # EVERY task prefixes outputs with its id: two tasks touching the
            # same beat otherwise overwrite each other on the courier branch
            # (prod-hires clobbered prod-open's beat 3, 2026-07-30 — the
            # frames survived only in git history)
            prefix = f"{task.get('id')}-"
            f = courier.out / f"{prefix}{num:02d}-{s['slug']}-s{k}.png"
            img.save(f)
            # BESIDE THE FRAME, NOT AFTER THE BATCH. Written per image so a run
            # killed mid-batch leaves every frame it did finish with its record
            # attached — the courier branch's whole point is that a machine that
            # dies is still readable. `<name>.png.meta.yaml`, the full-name
            # convention hold_still and video_task already use (licence_gate
            # .sidecar_for reads both).
            Path(str(f) + ".meta.yaml").write_text(
                still_sidecar(BASE, task, num, seed, f"{w}x{h}", steps,
                              ptext, neg,
                              init=init_rel or None,
                              strength=task.get("strength", 0.5) if init_rel else None,
                              init_crop=init_crop),
                encoding="utf-8")
            courier.say(f"  {f.name} in {time.time()-t0:.0f}s")


def main() -> int:
    # A Windows console is cp1252, and this worker echoes its children's output
    # — which carries em-dashes from shots.md and a Chinese negative prompt. A
    # print() of any of it raised UnicodeEncodeError IN THE WORKER, which is
    # why the msi went silent mid-task instead of reporting its own timeout
    # (2026-07-31: "charmap codec can't encode character"). Never let logging
    # kill the process it is logging.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True,
                    help="this machine's handle (branch: farm-results-<name>)")
    ap.add_argument("--once", action="store_true",
                    help="do one queue pass and exit (no polling loop)")
    ap.add_argument("--force", action="store_true",
                    help="clear a stale single-instance lock and run anyway")
    a = ap.parse_args()

    # one worker per machine handle, before the GPU is touched
    lock = acquire(a.name, force=a.force)
    device, dtype = pick_device()
    courier = Courier(a.name)
    # BEFORE it claims anything. A worker with holed weights that takes a task
    # and returns noise costs the queue that task plus the seeds a lane spends
    # believing the output; a worker that refuses at startup costs nothing.
    require_intact_weights(courier)
    print(f"farm worker '{a.name}' on {device} — polling {QUEUE} every {POLL_SECONDS}s")
    done_ids, gave_up = finished_tasks(courier)
    if done_ids:
        print(f"{len(done_ids)} task(s) already done or abandoned — recovered from "
              f"heartbeat, will not re-run")
    warned = set()
    while True:
        ran_one = False
        for task in queue_head():
            tid = str(task.get("id"))
            if tid in gave_up and tid not in warned:
                warned.add(tid)
                # MARK IT, do not just print it. A print dies with the console,
                # and the failure this guard now catches is the one that takes the
                # console down with the machine — so the refusal has to reach the
                # branch or nobody outside the room learns the worker is skipping
                # work (DIAG-20260804.md). Once per task per process: mark()
                # commits and force-pushes.
                why = (f"!! {tid} is QUEUED but has {gave_up[tid]} start(s) with no "
                       f"DONE — skipping it so the rest of the queue can run "
                       f"(MAX_ATTEMPTS={MAX_ATTEMPTS}, counted from STARTED lines so "
                       f"a crash that kills the host still spends an attempt). Fix "
                       f"the cause, or remove it from {QUEUE}, or re-queue it under "
                       f"a fresh id.")
                print(why, flush=True)
                courier.mark(f"SKIPPED task={tid} after {gave_up[tid]} attempt(s) "
                             f"— MAX_ATTEMPTS={MAX_ATTEMPTS}")
            if tid in done_ids or task.get("worker", "any") not in ("any", a.name):
                continue
            # render from CURRENT main, not whatever checkout the machine was
            # born with (the msi's first task ran from its USB-era files)
            # fingerprint EVERY pipeline module, not just this file: video_task
            # and wan_i2v changed while this process kept its already-imported
            # video_task in memory, so a new script ran against old caller code
            # (2026-07-30 canary 2, exit 2 on missing --stage)
            def _fp():
                return sorted((p.name, p.stat().st_mtime_ns, p.stat().st_size)
                              for p in Path(__file__).parent.glob("*.py"))
            before = _fp()
            # sync code files from main WITHOUT switching branches: a branch
            # switch deletes farm-out (tracked here, absent on main), which is
            # how each task erased its predecessors' results (2026-07-29 late)
            sh("git", "checkout", "-q", "origin/main", "--", ".", check=False)
            if _fp() != before:
                # a running process can't hot-swap its source or its imports
                # (the 2026-07-29 lesson: workers synced the new file but kept
                # executing the old one from memory). Relaunch.
                print("pipeline code updated — restarting myself", flush=True)
                # release FIRST: the child re-runs main() and calls acquire(),
                # which would fail against our own still-held lock and kill the
                # worker on every code update.
                #
                # But release ONLY OUR OWN. A bare unlink() deletes whichever
                # lock is there, so a second worker restarting would quietly free
                # the FIRST worker's lock and then take it — which is exactly
                # what happened on 2026-08-01: worker 2 came out of its prefetch
                # at 02:19, restarted, wiped worker 1's lock, and both ran on.
                # A mutex you can release on someone else's behalf is not a mutex.
                release(lock)
                # NOT os.execv: on Windows it replaces the process in a way that
                # detaches it from the console, so the worker vanished after
                # exactly one task every time pipeline code changed (the msi, twice
                # on 2026-07-31). Re-run as a CHILD sharing this console, then exit
                # with its status — works the same on POSIX.
                sys.exit(subprocess.run([sys.executable] + sys.argv).returncode)
            courier.task = tid
            courier.mark(f"STARTED task={tid} beats={task.get('beats')} on {device}")
            try:
                render_task(task, courier, device, dtype)
                courier.mark(f"DONE task={tid}")
            except Exception:                     # noqa: BLE001 — ship it, don't die
                import traceback
                tb = traceback.format_exc()
                courier.say(tb)
                courier.blame(f"task={tid}\n{tb}")
                # A CONSOLE INTERRUPT IS NOT A FAILED RENDER, and recording it as
                # one spends an attempt the task never got. This has now cost two
                # renders: beat 7 died to `forrtl: error (200): program aborting
                # due to window-CLOSE event` when the machine was shut down
                # mid-render (2026-08-02), and the first AnimeGen canary died at
                # 22 minutes to exit 3221225786 = 0xC000013A =
                # STATUS_CONTROL_C_EXIT when a second worker was started on top
                # of a running one (2026-08-03).
                #
                # Nothing about the task caused either. Mark it INTERRUPTED so
                # finished_tasks() does not count it toward MAX_ATTEMPTS — the
                # work is still queued and will simply be picked up again.
                if any(str(c) in tb for c in INTERRUPT_EXITS):
                    courier.mark(f"INTERRUPTED task={tid} (console interrupt, "
                                 f"not counted as an attempt)")
                else:
                    courier.mark(f"FAIL task={tid}")
            done_ids.add(tid)
            # RE-READ THE QUEUE AFTER EVERY TASK, not after the whole list.
            #
            # queue_head() returns a list and this loop walked all of it before
            # polling again. With twelve tasks at ~9 minutes each, a queue change
            # took TWO HOURS to take effect — so a prompt fix pushed at 18:15 was
            # still being ignored at 18:30, and beats 3 and 4 rendered with the very
            # instruction the fix removed (2026-08-02). The steward spent the
            # afternoon rewriting a queue the worker could not see.
            #
            # Breaking here costs one git fetch (~1s) against a 9-minute task and
            # makes the queue what it looks like: the current instruction, not a
            # snapshot from whenever the list was last exhausted.
            ran_one = True
            break
        if a.once:
            return 0
        # DO NOT SLEEP AFTER DOING WORK. Breaking out of the queue loop after
        # every task (so the queue stays current) meant falling straight into an
        # unconditional 60s sleep — with the next beat already sitting in the
        # queue. Measured on the 2026-08-02 hi-res set: 242s of rendering per
        # clip and a 72s gap after it, ~60s of which was this sleep. Fifteen
        # beats paid it fifteen times: 15 minutes of a 91-minute run spent
        # waiting for a queue that had not changed.
        #
        # The sleep exists for an EMPTY queue, so only sleep when the queue was
        # actually empty for us. It also printed "queue empty for me" right after
        # finishing a task, which was simply untrue.
        if ran_one:
            continue
        print(f"[{time.strftime('%H:%M:%S')}] polling — queue empty for me, {len(done_ids)} task(s) done this session", flush=True)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    sys.exit(main())
