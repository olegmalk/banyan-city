#!/usr/bin/env python3
"""When will an episode be finished — the half of that question a machine can answer.

Founder, 2026-08-13: "on the banyan.city/status page, lets start working on ETA,
basically the estimated time we finish something, so we have a good idea of for
example when we will finished episode 2, this is an important feature."

THE ONE THING THIS FILE REFUSES, and it is the whole design. An episode is
finished when the machine has rendered every beat AND the author has looked at
every beat and said yes. Those are two different clocks. The first is
measurable: the box writes down when each job started and stopped, and it has
done so 336 times. The second is a person deciding, and a person's decision
latency is not a quantity — the same call has taken four minutes and it has
taken three days, and nothing in this repo predicts which. Adding them produces
a single confident number whose error bars are a human being, which is exactly
the kind of figure that gets quoted back as a promise.

So this prints machine hours, and beside them it prints the decisions those
hours are waiting on, BY NAME, and it never adds the two together and never
turns either into a calendar date. "Three hours of rendering, once these four
calls are made" is honest and actionable. "Ready Thursday" is neither.

WHY ROUNDS RATHER THAN JOBS. A remaining beat does not cost one render, it costs
however many attempts that beat needs before it is right — ep1 beat 7 took 17.
So the estimate is (median rounds a FINISHED beat needed) x (median minutes a
job of that kind takes), and the rounds are counted only over beats that
actually reached `done`. Counting rounds over every beat would average "took 4
and finished" together with "has had 12 and is still wrong", and the second
number is not an estimate of anything: it is a beat that has not converged yet,
and folding it in makes the projection worse the more trouble we are in.

THREE HONEST FLOORS, all printed rather than buried:
  * The sidecars start 2026-08-10. Rounds spent on a beat before that date are
    not in the record, so the rounds medians — and therefore the hours — are a
    LOWER bound, not a best guess.
  * A beat nobody has decided to keep or cut costs zero machine minutes if it is
    cut. Its hours are reported separately from the firm ones, never merged in.
  * Fewer than MIN_SAMPLE finished beats and the projection is labelled thin
    with its n, and still printed — a thin measurement stated as thin beats a
    round number with no provenance.

    python3 pipeline/episode_eta.py            # the report
    python3 pipeline/episode_eta.py --yaml     # the block for measured/eta.yaml

WHAT LIVES IN WHICH FILE, which is the same split box-queue.yaml argues for.
`measured/episode-progress.yaml` holds the per-beat STATES and the lanes rewrite
it as they score. `measured/eta.yaml` holds only what a build machine cannot
re-derive — the rounds medians, which need the farm-results branch this script
reads and Vercel's checkout does not have. The kind medians are NOT copied here;
they are read from `measured/box-queue.yaml` where they already live, so the two
pages cannot come to disagree about how long an LTX take runs. And the hours
themselves are stored NOWHERE: build_sim multiplies at build time, so a lane
flipping one beat to `done` moves the number on the next build without anyone
re-running this script. A stored total would keep printing yesterday's backlog
against today's states.

Read-only. `git show` against a remote-tracking ref: no checkout, no fetch, and
nothing on this machine is written except by the person pasting the yaml.
"""
import argparse
import re
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import box_job_minutes as bjm

REPO = Path(__file__).resolve().parent.parent
PROGRESS_FILE = "pipeline/measured/episode-progress.yaml"
ETA_FILE = "pipeline/measured/eta.yaml"
BOX_QUEUE_FILE = "pipeline/measured/box-queue.yaml"
INBOX_FILE = "review/inbox.yaml"

# The five states a beat can be in. They are exhaustive on purpose: every beat
# of every episode carries exactly one, so a beat can never fall out of the
# arithmetic by being unlabelled.
STATES = ("done", "candidate-awaiting-founder", "fix-known",
          "blocked-decision", "never-rendered")
# A SIXTH STATE THIS FILE ASSIGNS ITSELF, and never reads off disk. See
# _apply_gate_correction below: it is what a `blocked-decision` becomes when the
# decision it names has demonstrably already been made. It is deliberately NOT
# in STATES, so a lane cannot write it into the measurement by hand — it is a
# reading of a stale row, not a measurement of a beat.
STALE_GATE = "stale-gate-closed"
# What `read_progress()` may EMIT, as against what it may READ. The distinction
# is the point: STATES gates the file, this gates the output, and a typo in
# either still fails the suite rather than sliding through as a new category.
EMITTED_STATES = STATES + (STALE_GATE,)
# Machine work we can commit to: something is wrong and we know the fix, or
# nothing has ever been rendered. Both need the card, neither needs a decision.
NEEDS_RENDER = ("fix-known", "never-rendered")
# Machine work that exists only if a human says "keep it". Costed separately —
# a cut beat costs nothing, so folding these in would inflate the firm figure.
CONDITIONAL = ("blocked-decision",)
# `candidate-awaiting-founder` appears in neither list, and that is the point:
# it is waiting on a pair of eyes, not on the card. Counting it as machine work
# is how you get a page that says the box is three hours from done when the box
# has nothing to do.

# The states in which the CARD has finished with a beat — which is not the same
# as the beat being finished. The machine's deliverable is a take the author can
# look at; the yes is the other clock. Sampling rounds over `done` alone would
# quietly couple the machine estimate to the author's review speed, which is the
# one thing this whole file exists to avoid: on 2026-08-13 episode 2 had nine
# beats the box had rendered to a showable take and zero the author had passed,
# so a done-only sample would have reported "not estimable" about an episode the
# box has measurably spent days on.
MACHINE_FINISHED = ("done", "candidate-awaiting-founder")

# The render kinds a beat actually costs. `charref`, `inpaint` and `other` are
# per-episode or per-character setup, not per-beat, so multiplying them by a
# beat count would bill every remaining beat for work done once.
BEAT_KINDS = ("ltx", "still")
# Below this many finished beats the projection still prints, labelled thin.
MIN_SAMPLE = 4


def _yaml():
    import yaml
    return yaml


def _load(rel):
    """A repo yaml, or None. Absent, unreadable and malformed are one answer."""
    try:
        doc = _yaml().safe_load((REPO / rel).read_text(encoding="utf-8"))
    except Exception:
        return None
    return doc


# TWO WORDINGS FOR ONE GATE, and the second was found by counting. Eleven beats
# say "character gate"; beat 2 says "held by the character-first ruling", which
# is the same ruling under a different phrase — canon subject
# `ep2-goblin-character-gate` enumerates all twelve (2, 3, 4, 7, 8, 13, 14, 15,
# 16, 17, 19, 20) as one decision. Matching only the first phrase left beat 2
# publishing a block, which is how a partial fix reads as a complete one.
_GATE_NOTE = re.compile(r"character[ -](?:gate|first)", re.I)


def _apply_gate_correction(state: str, note: str) -> str:
    """`blocked-decision -- ... character gate` -> STALE_GATE. Everything else through.

    WHY THIS EXISTS. `pipeline/measured/episode-progress.yaml` was measured
    2026-08-14 09:40Z. The founder answered the goblin character gate at
    11:09:07Z the SAME MORNING -- ninety minutes later -- and twelve episode-2
    beats (2, 3, 4, 7, 8, 13, 14, 15, 16, 17, 19, 20) still carry
    `state: blocked-decision` with a note naming that gate. The file says so
    itself, at length, in its own `goblin_gate_CORRECTION_0816` key; what it
    does NOT do is change the rows, so every reader downstream kept publishing
    the block. status.html was rendering "waiting on a decision" eighteen times,
    twelve of them for a decision that was made four days ago. A status page
    that tells the author he is holding up work he already unblocked is worse
    than no status page.

    WHAT THIS DELIBERATELY DOES NOT DO: promote those beats to `done`, or to
    anything else that claims progress. Their true state is UNKNOWN -- nobody
    has re-scored them since the gate opened -- and the honest rendering of an
    unknown is a hollow leaf, not a green one. This function downgrades a false
    certainty to an admitted absence. Re-measuring them is the real fix and this
    is not a substitute for it.
    """
    if state == "blocked-decision" and _GATE_NOTE.search(note):
        return STALE_GATE
    return state


def read_progress(path=PROGRESS_FILE) -> list:
    """The per-episode beat states, or [] — never a guess at one.

    Shape checked here rather than trusted: an episode without a beat list, or a
    beat carrying a state this file does not define, is dropped with the rest of
    its episode rather than silently counted as zero work. A typo'd state that
    quietly became "no beats need rendering" is the failure mode this catches.
    """
    doc = _load(path)
    if not isinstance(doc, dict):
        return []
    out = []
    for ep in doc.get("episodes") or []:
        if not isinstance(ep, dict):
            continue
        beats = ep.get("beats")
        if not isinstance(beats, list) or not beats:
            continue
        rows = []
        for b in beats:
            if not isinstance(b, dict):
                continue
            state = str(b.get("state") or "")
            try:
                n = int(b.get("n"))
            except (TypeError, ValueError):
                continue
            if state not in STATES:
                continue
            note = str(b.get("note") or "")
            rows.append({"n": n, "state": _apply_gate_correction(state, note),
                         "note": note})
        if not rows:
            continue
        out.append({"number": ep.get("number"), "node": str(ep.get("node") or ""),
                    "title": str(ep.get("title") or ""),
                    "total_beats": ep.get("total_beats") or len(rows),
                    "states_read_from": str(ep.get("states_read_from") or ""),
                    "review_url": str(ep.get("review_url") or ""),
                    "beats": rows})
    return out


def read_kind_medians(path=BOX_QUEUE_FILE) -> dict:
    """kind -> median minutes, off the file the queue tile already uses, or {}.

    Deliberately not a copy in eta.yaml. Two files holding the same median is
    two files that drift, and the day they disagree the status page states two
    different job times in two sections and neither is wrong on its face.
    """
    doc = _load(path)
    med = (doc or {}).get("kind_medians") if isinstance(doc, dict) else None
    if not isinstance(med, dict):
        return {}
    out = {}
    for k, v in med.items():
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if f > 0:
            out[str(k)] = f
    return out


def read_rounds(path=ETA_FILE) -> dict:
    """node -> {'rounds': {kind: n}, 'sample': n, ...} as last measured, or {}."""
    doc = _load(path)
    if not isinstance(doc, dict):
        return {}
    out = {}
    for ep in doc.get("episodes") or []:
        if not isinstance(ep, dict):
            continue
        r = ep.get("rounds_median")
        if not isinstance(r, dict):
            continue
        rounds = {}
        for k, v in r.items():
            try:
                f = float(v)
            except (TypeError, ValueError):
                continue
            if f > 0:
                rounds[str(k)] = f
        try:
            sample = int(ep.get("finished_beats_sampled") or 0)
        except (TypeError, ValueError):
            sample = 0
        out[str(ep.get("node") or "")] = {
            "rounds": rounds, "sample": sample,
            "measured_at": str(doc.get("measured_at") or ""),
            "window": str(doc.get("sidecar_window") or "")}
    return out


def open_decisions(episode, path=INBOX_FILE) -> dict:
    """The open inbox entries tagged to this episode, plus how many are untagged.

    `episode:` is an OPTIONAL key on an inbox entry, added by whichever lane
    files the entry. Untagged entries are NOT attributed to an episode by
    guessing at their wording — they are counted, and the count is printed, so a
    reader can see that the gate list is as complete as the tagging is and not
    mistake "three listed" for "three exist".

    Open means no `resolved:`, the same test build_sim's review_inbox_open() and
    the inbox page's regen.py both apply, so the ETA line and the page it links
    to cannot report different numbers.
    """
    doc = _load(path)
    if not isinstance(doc, list):
        return {"ok": False, "entries": [], "untagged": 0}
    entries, untagged = [], 0
    for e in doc:
        if not isinstance(e, dict) or e.get("resolved"):
            continue
        tag = e.get("episode")
        if tag in (None, ""):
            untagged += 1
            continue
        try:
            same = int(tag) == int(episode)
        except (TypeError, ValueError):
            same = str(tag) == str(episode)
        if same:
            # `what` / `url` / `since` are the inbox's own field names — this
            # reader takes the file's shape rather than asking the file to grow
            # keys for it. There is no id in that file and none is invented: the
            # url is what a reader clicks and what identifies the call.
            entries.append({"what": str(e.get("what") or "").strip(),
                            "url": _linkable(e.get("url")),
                            "since": str(e.get("since") or "").strip()})
    return {"ok": True, "entries": entries, "untagged": untagged}


def _linkable(url) -> str:
    """The entry's url if a browser can follow it, else "" — never a half-link.

    `review/inbox.yaml` is a human-written file and one open entry's url reads
    `local: review/ep2-picks/farm-recovered-0814-scores.yaml` — a note to a lane
    about a file on someone's disk, not an address. Emitted as an href it becomes
    a link to a path that does not exist on the site, and `build_site.py`'s
    broken-link gate fails the whole build on it (it did, the moment the KeyError
    above stopped swallowing this list). "" is the right answer rather than a
    guess at the intended path: `_eta_card` already prints an unlinked call as
    plain text, so the call is still NAMED and only the dead href is dropped.
    Deliberately not fixed by editing the inbox: that file is the founder's, its
    `local:` prefix is telling a lane something true, and a page must not fail
    because a human wrote a note where a URL was optional anyway.
    """
    u = str(url or "").strip()
    if not u or " " in u or ":" in u.split("/")[0]:
        # A scheme is the one colon-before-slash that IS an address.
        return u if u.split("://")[0] in ("http", "https") and "://" in u else ""
    return u


def per_beat_minutes(rounds: dict, kind_medians: dict):
    """Minutes one more beat costs the card, or None when it cannot be known.

    rounds x medians, summed over the kinds a beat actually consumes. None
    rather than zero when either input is missing: zero would render as "no work
    left", which is the single most misleading thing this page could say.
    """
    if not rounds or not kind_medians:
        return None
    total = 0.0
    for kind in BEAT_KINDS:
        r, m = rounds.get(kind), kind_medians.get(kind)
        if r and m:
            total += r * m
    return total or None


def episode_row(ep: dict, rounds_doc: dict, kind_medians: dict, inbox_path=INBOX_FILE) -> dict:
    """One episode's whole answer: what is where, what is left, what it waits on."""
    # OVER `EMITTED_STATES`, NOT `STATES`, and that distinction is a live bug fix
    # (2026-08-19). `read_progress()` may hand back `stale-gate-closed`, which is
    # by design absent from `STATES` — and this dict was built from `STATES`, so
    # the first stale row raised `KeyError: 'stale-gate-closed'` out of
    # `episode_row`. `build_sim.episode_eta_rows()` catches every exception and
    # returns `[]`, so the failure was SILENT and total: with twelve stale rows on
    # file, /status published no ETA cards and no ETA glance cell for five days
    # while the sapling tree beside them drew fine (it calls `read_progress()`
    # direct). A count over what the reader may EMIT can never be surprised by
    # what it emits; a count over what it may READ can, every time the two sets
    # differ. `unk` in the card's own bar already carried this bucket.
    counts = {s: 0 for s in EMITTED_STATES}
    for b in ep["beats"]:
        counts[b["state"]] = counts.get(b["state"], 0) + 1

    firm = sum(counts[s] for s in NEEDS_RENDER)
    cond = sum(counts[s] for s in CONDITIONAL)
    meas = rounds_doc.get(ep["node"]) or {}
    pbm = per_beat_minutes(meas.get("rounds") or {}, kind_medians)
    sample = int(meas.get("sample") or 0)

    dec = open_decisions(ep.get("number"), inbox_path)
    return {
        "number": ep.get("number"),
        "node": ep["node"],
        "title": ep.get("title") or "",
        "total": int(ep.get("total_beats") or len(ep["beats"])),
        "counted": len(ep["beats"]),
        "counts": counts,
        "ready": counts["done"],
        "awaiting_founder": counts["candidate-awaiting-founder"],
        "needs_render": firm,
        "conditional_beats": cond,
        "per_beat_minutes": pbm,
        "machine_minutes": round(firm * pbm) if pbm is not None else None,
        "conditional_minutes": round(cond * pbm) if pbm is not None else None,
        "rounds": meas.get("rounds") or {},
        "sample": sample,
        "thin": bool(pbm is not None and sample < MIN_SAMPLE),
        "decisions": dec["entries"],
        "decisions_untagged": dec["untagged"],
        "measured_at": meas.get("measured_at", ""),
        "window": meas.get("window", ""),
        "states_read_from": ep.get("states_read_from", ""),
        "review_url": ep.get("review_url", ""),
    }


def rows(progress_path=PROGRESS_FILE, eta_path=ETA_FILE,
         box_path=BOX_QUEUE_FILE, inbox_path=INBOX_FILE) -> list:
    """Every episode's row, newest episode first. [] when nothing can be read."""
    prog = read_progress(progress_path)
    if not prog:
        return []
    rounds_doc, med = read_rounds(eta_path), read_kind_medians(box_path)
    out = [episode_row(ep, rounds_doc, med, inbox_path) for ep in prog]
    return sorted(out, key=lambda r: (r["number"] is None, -(r["number"] or 0)))


# --------------------------------------------------------------- measuring ---
# Everything below needs the farm-results branch and is therefore a laptop job,
# not a build job. It is what writes eta.yaml.

def beat_rounds(branch=None) -> dict:
    """(node, beat) -> {kind: how many jobs of that kind the box ran on it}.

    Off the per-job sidecars for the same reason box_job_minutes.py is: the step
    logs are tail-truncated at 200 lines and the truncation is biased toward the
    long jobs, while `farm-out/box/<id>.json` covers every job and carries the
    `node` and `beat` the runner filed it under.
    """
    import json
    branch = branch or bjm.BRANCH
    names = bjm._run(["git", "ls-tree", "-r", "--name-only", branch]).split()
    out, seen = {}, []
    for path in names:
        if not (path.startswith(bjm.SIDECARS) and path.endswith(".json")):
            continue
        try:
            spec = json.loads(bjm._run(["git", "show", f"{branch}:{path}"]))
        except json.JSONDecodeError:
            continue
        end = bjm._iso(spec.get("finished_at"))
        if end:
            seen.append(end)
        kind = bjm.job_kind(spec)
        beat, node = spec.get("beat"), spec.get("node")
        if kind not in BEAT_KINDS or beat in (None, "") or not node:
            continue
        out.setdefault((str(node), str(beat)), {}).setdefault(kind, 0)
        out[(str(node), str(beat))][kind] += 1
    return {"rounds": out,
            "window": (f"{min(seen):%d %b} - {max(seen):%d %b}" if seen else ""),
            "jobs": len(seen)}


def rounds_medians(progress: list, scan: dict) -> list:
    """Per episode, the median rounds a beat needed to become showable, and the n.

    Sampled over MACHINE_FINISHED — the beats the card has delivered a take for,
    whether or not the author has passed it. See that constant for why `done`
    alone is the wrong sample: it would make the machine's estimate depend on
    how fast a person answers, and the estimate would vanish entirely for an
    episode nobody has reviewed yet, which is precisely the episode someone is
    asking about.

    Beats still in trouble are excluded either way. A beat that has had twelve
    rounds and is still wrong has not converged, so its round count is not an
    estimate of what a beat costs — and folding it in would make the projection
    rise the worse the work was going, which is a metric that punishes you for
    measuring it.
    """
    out = []
    for ep in progress:
        node = ep["node"]
        done = [str(b["n"]) for b in ep["beats"] if b["state"] in MACHINE_FINISHED]
        per = {k: [] for k in BEAT_KINDS}
        hit = 0
        for beat in done:
            counts = scan["rounds"].get((node, beat))
            if not counts:
                continue      # finished before the sidecars start; not a zero
            hit += 1
            for k in BEAT_KINDS:
                per[k].append(counts.get(k, 0))
        med = {k: round(statistics.median(v), 1) for k, v in per.items()
               if v and statistics.median(v) > 0}
        out.append({"number": ep.get("number"), "node": node,
                    "machine_finished_beats": len(done),
                    "finished_beats_sampled": hit, "rounds_median": med})
    return out


def _stamp() -> str:
    """A UTC stamp, sanity-checked against the newest commit's clock.

    The laptop's clock has drifted a day inside this project's memory and the
    founder caught it on the page. If the two disagree by more than a few hours
    the stamp is written from git's time instead, and says so, because a wrong
    date on a measurement is worse than an ugly one.
    """
    now = datetime.now(timezone.utc)
    head = bjm._run(["git", "log", "-1", "--format=%cI"]).strip()
    try:
        gt = datetime.fromisoformat(head).astimezone(timezone.utc)
    except ValueError:
        return f"{now:%Y-%m-%d %H:%M}Z"
    if abs((now - gt).total_seconds()) > 6 * 3600:
        return f"{gt:%Y-%m-%d %H:%M}Z (git clock; this machine's differs)"
    return f"{now:%Y-%m-%d %H:%M}Z"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--branch", default=bjm.BRANCH)
    ap.add_argument("--yaml", action="store_true",
                    help=f"print the block to paste into {ETA_FILE}")
    a = ap.parse_args()

    progress = read_progress()
    if not progress:
        print(f"no readable episode states in {PROGRESS_FILE} — no ETA is claimed")
        return 1

    if a.yaml:
        scan = beat_rounds(a.branch)
        if not scan["jobs"]:
            print(f"no job sidecars under {a.branch}:{bjm.SIDECARS}")
            return 1
        eps = rounds_medians(progress, scan)
        print(f"# Written by `python3 pipeline/episode_eta.py --yaml`. See that")
        print(f"# file's docstring for what these are and what they are not.")
        print(f"measured_at: {_stamp()}")
        print(f"sidecar_branch: {a.branch}")
        print(f"sidecar_window: {scan['window']}")
        print(f"sidecar_jobs: {scan['jobs']}")
        print("episodes:")
        for e in eps:
            print(f"  - number: {e['number']}")
            print(f"    node: {e['node']}")
            print(f"    machine_finished_beats: {e['machine_finished_beats']}")
            print(f"    finished_beats_sampled: {e['finished_beats_sampled']}")
            if e["rounds_median"]:
                print("    rounds_median:")
                for k in sorted(e["rounds_median"]):
                    print(f"      {k}: {e['rounds_median'][k]}")
            else:
                print("    rounds_median: {}   # no finished beat is in the window")
        return 0

    med = read_kind_medians()
    if not med:
        print(f"no kind medians in {BOX_QUEUE_FILE} — hours are not claimed")
    for r in rows():
        print(f"\nEpisode {r['number']} — {r['node']}")
        print(f"  {r['ready']} of {r['total']} beats founder-ready"
              + (f"  ({r['counted']} beats have a state on file)"
                 if r["counted"] != r["total"] else ""))
        # EMITTED_STATES, so a stale-gate row is printed rather than silently
        # dropped from a listing that adds up to less than the beat count.
        for s in EMITTED_STATES:
            if r["counts"].get(s):
                print(f"    {s:<27} {r['counts'][s]}")
        if r["per_beat_minutes"] is None:
            print("  machine work left: not claimed — no rounds median, or no "
                  "job times to multiply it by")
        else:
            print(f"  per remaining beat: {r['per_beat_minutes']:.0f} min "
                  f"(rounds {r['rounds']} x kind medians {med})")
            print(f"  machine work left:  {r['machine_minutes'] / 60:.1f} h "
                  f"over {r['needs_render']} beats"
                  + (f"  [thin — n={r['sample']}]" if r["thin"]
                     else f"  [n={r['sample']} finished beats]"))
            if r["conditional_beats"]:
                print(f"  plus, only if kept:  {r['conditional_minutes'] / 60:.1f} h "
                      f"over {r['conditional_beats']} undecided beats")
        if r["decisions"]:
            print(f"  gated on {len(r['decisions'])} open decision(s):")
            for d in r["decisions"]:
                print(f"    - since {d['since'] or '?'}: {d['what'][:78]}")
        else:
            print("  gated on: nothing tagged to this episode in the inbox")
        if r["decisions_untagged"]:
            print(f"    ({r['decisions_untagged']} open inbox entries carry no "
                  "episode: tag and are not attributed here)")
    print("\nMachine hours only. The author's decisions are listed, never timed — "
          "\nhow long a call takes is not a measurable quantity and this file "
          "will not invent one.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
