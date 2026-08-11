#!/usr/bin/env python3
"""Read the founder's answers off one GitHub issue and write them down. Nothing else.

WHY THIS EXISTS. Every review surface this project has built lives at
`127.0.0.1:8787`. On 2026-08-10 the founder left for a hotel with a phone and no
laptop, which is the first time the answer channel and the review surface had to
be two different things: he reads the published review page, and he answers in
the GitHub app. This turns those replies into a file the supervisor can read.

WHAT IT WILL NOT DO, and the boundary is the point of the file:

    IT NEVER ACTS ON AN ANSWER. It parses and it records.

Promoting a still, firing a render, marking a card settled and spending money are
all dispatch decisions, and a comment is not a dispatch. A regex that mis-reads
"no, not the r5 one" as a pick must not be able to put a frame into canon — so
the only power this script has is to append a line to a log. Something else, with
a human in it, reads that log. This mirrors STEWARDSHIP.md §6 one level down: §6
says do not render an unapproved script; this says do not let a *parse* stand in
for an approval.

Anything it cannot read confidently is recorded as `intent: unparsed` with the
comment's text preserved verbatim. Unparsed is a normal outcome, not an error —
the founder writes in sentences, and a sentence that means something to a person
and nothing to this grammar must survive intact rather than be guessed at.

IDEMPOTENCY. The answer log is the watermark. Before writing, the script reads
every `comment_id` already in `founder-answers.jsonl` and skips those comments.
A separate high-water timestamp is also kept (`--state`), but only to say when we
last looked — correctness does not depend on it, so losing, deleting or corrupting
it re-reads comments and still writes nothing new. The reverse design (trust the
timestamp) loses an answer whenever a comment is edited or arrives out of order.

    python3 pipeline/poll_decisions.py --issue 42
    python3 pipeline/poll_decisions.py --issue 42 --dry-run
    python3 pipeline/poll_decisions.py --issue 42 --json      # for a supervisor

Needs the `gh` CLI, authenticated. No new dependencies; stdlib only.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ANSWERS = REPO / "pipeline" / "founder-answers.jsonl"
STATE = REPO / "pipeline" / ".decisions-state.json"

# The one answer channel, opened 2026-08-10 when the founder left with a phone
# and no laptop. One issue on purpose: eight of them would be eight places to
# forget to look, and he answers in whatever order he likes anyway.
DEFAULT_ISSUE = 31

# ---------------------------------------------------------------------------
# The grammar. Deliberately small.
# ---------------------------------------------------------------------------
# One answer per line, `key: answer`. The key names the card he is answering —
# either the number printed on it or a short slug — and both are listed on the
# issue itself so the two cannot drift apart in his head. A line whose key we do
# not recognise is `unparsed`; a recognised key with an answer we do not
# recognise is `note`, which keeps his words attached to the right card without
# pretending they are a verdict.

# Card slugs → the checklist card they answer. Kept beside the numbers because a
# number is easy to mistype on a phone and a slug is not.
SLUGS = {
    "repo": "repo-owner",
    "github": "repo-owner",
    "b06": "ep1-beat06",
    "beat6": "ep1-beat06",
    "beat06": "ep1-beat06",
    "v34": "ep1-v34",
    "ep1": "ep1-v34",
    "ltx": "ltx-publish",
    "crop": "crop-704",
    "framing": "crop-704",
    "b01": "ep2-b01-r9",
    "ep2b01": "ep2-b01-r9",
    "ep2": "ep2-first-pass",
    "wan": "wan-vs-ltx",
}

# Card numbers as PRINTED on the review page (`n:` in cuts.yaml), which is the
# only number he can see. These are not the yaml list positions and must not be.
NUMBERS = {
    22: "repo-owner",
    10: "ep1-beat06",
    19: "ep1-v34",
    20: "ltx-publish",
    11: "crop-704",
    6: "ep2-b01-r9",
    13: "ep2-first-pass",
    14: "wan-vs-ltx",
}

# A frame address: `b06-r5-s2`, or episode-qualified `002b-b18-r3-s0`.
FRAME_RE = re.compile(
    r"^(?:(?P<node>\d{3}[a-z]?)-)?b(?P<beat>\d{1,2})-r(?P<round>\d+)-s(?P<seed>\d+)$",
    re.I,
)
YES = {"yes", "y", "yep", "yeah", "ok", "okay", "approve", "approved", "ship it"}
NO = {"no", "n", "nope", "nah", "reject", "rejected"}
GO = {"go", "render", "run it"}

LINE_RE = re.compile(r"^\s*(?P<key>[A-Za-z0-9 ]{1,20}?)\s*[:=]\s*(?P<val>.+?)\s*$")


def resolve_key(key: str):
    """`10`, `b06`, `ep2 b01` → a card id, or None if we do not know it."""
    k = key.strip().lower().replace(" ", "").replace("-", "").replace("#", "")
    if k.isdigit():
        return NUMBERS.get(int(k))
    return SLUGS.get(k)


def _frame_fields(m, text: str):
    """The four numbers in a frame address, off an already-matched FRAME_RE."""
    return {
        "frame": text.strip().lower(),
        "node": (m.group("node") or "").lower() or None,
        "beat": int(m.group("beat")),
        "round": int(m.group("round")),
        "seed": int(m.group("seed")),
    }


def parse_answer(value: str):
    """One answer string → (intent, extra fields). Never raises, never guesses."""
    v = value.strip().rstrip(".").strip()
    low = v.lower()
    if low in YES:
        return "yes", {"value": True}
    if low in NO:
        return "no", {"value": False}
    if low in GO:
        return "go", {}
    m = FRAME_RE.match(v)
    if m:
        return "pick_frame", _frame_fields(m, v)
    return "note", {"text": v}


def parse_comment(body: str):
    """One comment → a list of answer records (without the envelope fields).

    A comment can hold several answers, one per line, because batching is the
    cheapest thing a phone can do. Blank lines and markdown quotes (`>`) are
    skipped — quoting the question above the answer is the GitHub app's default
    reply gesture and must not read as an answer to itself.
    """
    out = []
    for raw in (body or "").splitlines():
        line = raw.strip()
        if not line or line.startswith(">") or line.startswith("#"):
            continue
        line = re.sub(r"^[-*+]\s+", "", line)          # bullet
        line = re.sub(r"^\d+[.)]\s+", "", line)         # "1. " numbered list

        # A bare frame address, no key. Episode 2 has twenty-one canon picks
        # spread over four contact sheets and they belong to no single card
        # number, so requiring one would mean inventing a key for him to get
        # wrong. The address is self-identifying — node, beat, round, seed — so
        # `card` stays null and whatever reads this log resolves it from the
        # frame itself rather than from a number he had to remember.
        bare = FRAME_RE.match(line)
        if bare:
            rec = {"intent": "pick_frame", "card": None, "raw_line": line}
            rec.update(_frame_fields(bare, line))
            out.append(rec)
            continue

        m = LINE_RE.match(line)
        if not m:
            out.append({"intent": "unparsed", "raw_line": raw.strip()})
            continue
        card = resolve_key(m.group("key"))
        if card is None:
            out.append({"intent": "unparsed", "raw_line": raw.strip()})
            continue
        intent, extra = parse_answer(m.group("val"))
        rec = {"intent": intent, "card": card, "raw_line": raw.strip()}
        rec.update(extra)
        out.append(rec)
    if not out:
        out.append({"intent": "unparsed", "raw_line": (body or "").strip()})
    return out


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------
def fetch_comments(issue: int, repo: str | None = None):
    """Every comment on the issue, oldest first, via `gh`. Raises on failure."""
    cmd = ["gh", "issue", "view", str(issue), "--json", "comments"]
    if repo:
        cmd += ["--repo", repo]
    # encoding= is not optional here and test_pipeline.py enforces it: his
    # comments carry em-dashes and the frame names carry none of them, but a
    # locale-decoded read would mangle the former and lose the raw text we
    # promise to preserve verbatim.
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"gh issue view failed: {proc.stderr.strip()}")
    data = json.loads(proc.stdout or "{}")
    return data.get("comments") or []


def recorded_ids(path: Path):
    """Comment ids already in the log — the real watermark.

    A malformed line is skipped rather than fatal: the log is append-only and
    the cost of one unreadable line must not be that no answer is ever recorded
    again.
    """
    ids = set()
    if not path.exists():
        return ids
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "comment_id" in rec:
            ids.add(str(rec["comment_id"]))
    return ids


def comment_id_of(c):
    """`gh` gives a url and sometimes an id; the url is always there and unique."""
    return str(c.get("id") or c.get("url") or "")


def build_records(comments, seen, issue):
    """New comments → the records that would be appended. Pure; no side effects."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    records = []
    for c in comments:
        cid = comment_id_of(c)
        if not cid or cid in seen:
            continue
        author = (c.get("author") or {}).get("login", "")
        for parsed in parse_comment(c.get("body", "")):
            rec = {
                "comment_id": cid,
                "issue": issue,
                "author": author,
                "created_at": c.get("createdAt", ""),
                "recorded_at": now,
                "raw": c.get("body", ""),
            }
            rec.update(parsed)
            records.append(rec)
    return records


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--issue", type=int, default=DEFAULT_ISSUE,
                    help=f"the answer-channel issue number (default: {DEFAULT_ISSUE})")
    ap.add_argument("--repo", default=None, help="owner/name (default: the checkout's remote)")
    ap.add_argument("--answers", default=str(ANSWERS), help="append-only answer log")
    ap.add_argument("--state", default=str(STATE), help="last-looked timestamp (not authoritative)")
    ap.add_argument("--dry-run", action="store_true", help="print what would be written; write nothing")
    ap.add_argument("--json", action="store_true", help="machine-readable summary on stdout")
    a = ap.parse_args(argv)

    answers = Path(a.answers)
    try:
        comments = fetch_comments(a.issue, a.repo)
    except (RuntimeError, json.JSONDecodeError) as e:
        print(f"poll_decisions: {e}", file=sys.stderr)
        return 1

    seen = recorded_ids(answers)
    records = build_records(comments, seen, a.issue)

    if not a.dry_run and records:
        answers.parent.mkdir(parents=True, exist_ok=True)
        with answers.open("a", encoding="utf-8") as fh:
            for r in records:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        Path(a.state).write_text(
            json.dumps(
                {
                    "issue": a.issue,
                    "last_polled": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "comments_seen": len(comments),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    if a.json:
        print(json.dumps({"new_records": records, "comments": len(comments)}, ensure_ascii=False, indent=2))
    else:
        verb = "would record" if a.dry_run else "recorded"
        print(f"poll_decisions: {len(comments)} comment(s) on issue #{a.issue}, {verb} {len(records)} answer(s)")
        for r in records:
            card = r.get("card", "-")
            detail = r.get("frame") or r.get("text") or r.get("value")
            print(f"  [{r['intent']:>10}] {card:<16} {str(detail)[:60] if detail is not None else ''}")
        if records:
            print("  NOTE: recorded only. Nothing has been rendered, promoted or settled.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
