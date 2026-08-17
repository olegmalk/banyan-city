#!/usr/bin/env python3
"""Catch the failure that has now cost four separate multi-day losses: THE
CANON MOVED AND THE ARTIFACT THAT RUNS DID NOT.

    python3 pipeline/check_canon_drift.py            # sweep this repo
    python3 pipeline/check_canon_drift.py --quiet    # findings only
    python3 pipeline/check_canon_drift.py --root DIR # sweep a fixture tree

$0, no GPU, no network, no model, no yaml round-trip of anything. Exit 0 when
there is no unacknowledged finding, 1 when there is.

THE FIVE RULES, each written against a real loss:

  R1 resolved_but_open — a founder decision recorded as `resolved:` in
     review/inbox.yaml while a record still asserts it is open. On 2026-08-14/15
     the founder cast both guards; the approval reached review/inbox.yaml and
     nothing else, and four beats stayed blocked for a day on a decision that
     already existed.

  R2 prompt_contradicts_canon — a canonical attribute contradicted by prompts
     that run. The reference sheets moved off `bald` on 08-12; 22 of the 57
     guard-beat prompts in wave-drafts.yaml still ask for it, and beat 11's
     logged "identity collapse — the bald scalp fills in with dark hair" was the
     render drifting TOWARD the approved cast, filed as a defect.

  R3 canon_never_ran — a canon no running artifact has ever used. PURPLE was
     written into three beat-20 drafts on 08-13/14 and never rendered: 56
     rendered fig prompts across beats 19 and 20, zero carrying the word. The
     colour sheet then asked the founder to rule on frames whose prompt has no
     colour word in it at all.

  R4 attribute_unpinned — an attribute the prompts describe INCONSISTENTLY WITH
     EACH OTHER. Instance 2's shape with no canon to contradict: the sapling is
     in twelve of twenty-one beats and never had a canonical description, so
     twelve beats improvised one in opposite directions — beat 01 alone carries
     both `wide oval cotyledon leaves` and `deeply lobed fig leaves with five
     fingers` across its own variants.

  R5 bar_serves_two_beats — one beat's judging bar recorded on another beat's
     spec. The ALL-21 wave was authored by copying a spec: 80 job specs carried
     BEAT 02's `success` line and only 13 are beat 02. queue_history.py copies
     `success` into the ledger's `purpose`, so 352 rows published "a LEAN ADULT
     goblin sprints in, skids and dives behind a sapling" as the bar for clips of
     beats that do no such thing. R1-R4 cannot express it: that prose contradicts
     NO canon, it is canonical prose about the wrong beat, and no
     attribute-versus-record rule can see a wrong ATTACHMENT.

LIVE EXAMPLE, unprompted, on the repo as it stands: R3 reports that PURPLE is in
ten drafts across beats 19 and 20 and in ZERO of the 56 rendered prompts in
scope. That is instance 3 caught by the check rather than by a person — the
reason the founder was handed 08-12 frames and asked to rule on a colour nobody
had asked for.

WHAT IT REFUSES TO GUESS, and why each abstention is deliberate:

  * IT DOES NOT MATCH CARDS TO RECORDS BY SIMILARITY. The originally sketched
    design — grep records for stereotyped open phrases, pair them to resolved
    cards by shared content words — was implemented and measured against this
    repo first: 47 hits, the majority pairing the wrong card with the wrong
    line ("guard cast unapproved" in gate-evidence.yaml matched a card about
    publishing episode 1). Subjects are therefore DECLARED in pipeline/canon.yaml.
    A resolved card with no registered subject is reported UNKNOWN, never FAIL.

  * IT DOES NOT FAIL ON PROSE LOGS. STATE.md is append-only; a 2026-08-12 line
    saying the cast is unapproved was true when written, and the same words
    appear in the 08-16 paragraph that RETRACTS it. Markdown records are reported
    at REVIEW and never fail the build. Structured YAML records can fail, because
    there the house convention gives an adjudicable answer: a dated
    `*_CORRECTION_MMDD` sibling key on the entry or any of its ancestors.

  * IT VERIFIES BY CONTENT, NEVER BY PROXY. Every register entry names an
    `evidence:` file plus a literal string that must still be in it; if the canon
    moves and the register is not updated, the check fails on the REGISTER rather
    than reporting a clean repo. `acknowledged:` entries that match nothing fail
    as stale_acknowledgement, so the suppression list prunes itself rather than
    growing into a blindfold.

WHAT IT CANNOT DETECT, stated plainly because knowing the hole matters more than
widening the check until it is noisy:

  * A CANON EXPRESSED AS A RELATION. The sapling canon being written is "knee-high
    on the goblin, ~40 cm, always shorter than he is". This compares STRINGS. It
    catches the six payloads that state the opposite relation in words (`taller
    than he is`) and it will never notice a prompt that violates the relation
    without saying so, nor judge whether `no taller than the grass` satisfies it.
    Deliberately excluded for the same reason: `standing tall`, in 17 prompts, is
    POSTURE, not a height claim — forbidding it would fire seventeen times for no
    defect.
  * AN ATTRIBUTE NOBODY DECLARED. R4 needs its axis named. It finds the
    contradiction without knowing which value is right, but not the attribute
    nobody thought to list.
  * A DECISION MADE OUTSIDE review/inbox.yaml. A ruling given in chat and never
    filed is invisible here; that is what the inbox is for.
  * WHETHER A RENDERED FRAME ACTUALLY SHOWS THE CANON. R3 proves a prompt
    carrying the canon reached a render. It cannot look at the picture — only the
    founder's eye closes that gap.
  * WHETHER A SHARED BAR IS A PASTE OR A POLICY. R5 sees that one `success:` line
    is the recorded bar for several beats. It cannot tell a wave-wide bar written
    that way on purpose ("Plate frames with this beat's own location ALREADY IN
    THEM", six beats, correct on all six) from beat 02's action pasted onto beat
    20. Measured before the rule was written: 13 `success` lines span more than one
    beat on this repo and exactly ONE is the defect. So the collision is REVIEW and
    a `bars:` entry is what makes it a verdict.

FINDING LEVELS: FAIL (exit 1) · ACK (known, named in a record, not fatal) ·
REVIEW (prose log, human eyes) · UNKNOWN (the check abstains and says so).
"""

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - yaml ships with the pipeline venv
    yaml = None

REPO = Path(__file__).resolve().parent.parent

FAIL, ACK, REVIEW, UNKNOWN = "FAIL", "ACK", "REVIEW", "UNKNOWN"


class Finding:
    def __init__(self, level, rule, subject, where, detail):
        self.level = level
        self.rule = rule
        self.subject = subject
        self.where = where
        self.detail = detail

    def __repr__(self):
        return f"{self.level} {self.rule} {self.subject} @{self.where}"

    def line(self):
        return f"  {self.level:<7} {self.rule:<24} {self.subject:<18} {self.where}\n"          f"          {self.detail}"


# ---------------------------------------------------------------------------
# CORPUS READERS — pure text in, plain data out. None of these round-trip YAML
# back to disk, and wave-drafts.yaml is never handed to a YAML parser at all:
# it is 421 KB of hand-written provenance and a round-trip would destroy it.
# ---------------------------------------------------------------------------

_VARIANT_RE = re.compile(r"^    (authored[A-Za-z_0-9]*):\s*>-\s*$")
_BEAT_RE = re.compile(r"^  '?(\d+)'?:\s*$")


def read_draft_variants(text):
    """wave-drafts.yaml → [(beat:int, variant:str, prompt:str)].

    Line-based on purpose. `authored*` block scalars under a numeric beat key are
    the prompts a render job sends; comments between them are provenance and must
    not be read as prompt text.
    """
    beat, variant, buf, out = None, None, [], []

    def flush():
        nonlocal variant, buf
        if variant is not None:
            out.append((beat, variant, " ".join(x.strip() for x in buf).strip()))
        variant, buf = None, []

    for raw in text.split("\n"):
        m = _BEAT_RE.match(raw)
        if m:
            flush()
            beat = int(m.group(1))
            continue
        m = _VARIANT_RE.match(raw)
        if m:
            flush()
            variant = m.group(1)
            continue
        if variant is not None:
            if re.match(r"^      \S", raw):
                buf.append(raw)
            else:
                flush()
    flush()
    return out


_SIDECAR_PROMPT_RE = re.compile(r"^prompt: >-\n((?:[ \t]+.*\n)+)", re.M)
_SIDECAR_BEAT_RE = re.compile(r"^shot_beat:\s*(\d+)", re.M)
_SIDECAR_VARIANT_RE = re.compile(r"^draft_variant:\s*(\S+)", re.M)


RUN_EVIDENCE_DIRS = ("farm-out", "review")


def read_run_evidence(root, dirs=RUN_EVIDENCE_DIRS):
    """Every render-time sidecar → [(path, beat, variant, prompt)].

    These are written AT RENDER TIME by the harness, so a prompt here is proof a
    frame was actually drawn from it. That is the whole basis of R3: the question
    is not what we drafted, it is what reached a picture.

    BOTH directories, and the second one is not optional. The first cut of this
    read farm-out/ alone and reported four job specs as un-fired against the
    guard canon; all four had in fact rendered, with their sidecars under review/.
    Four false positives out of a corpus gap — which is the whole reason this
    counts evidence by reading prompts rather than trusting a directory to be
    the place results live.
    """
    out = []
    files = []
    for d in dirs:
        files += glob.glob(os.path.join(root, d, "**", "*.yaml"), recursive=True)
    for f in sorted(set(files)):
        try:
            t = open(f, errors="replace").read()
        except OSError:
            continue
        pm = _SIDECAR_PROMPT_RE.search(t)
        if not pm or not re.search(r"^(?:platform|render_seconds):", t, re.M):
            continue
        bm = _SIDECAR_BEAT_RE.search(t)
        vm = _SIDECAR_VARIANT_RE.search(t)
        out.append((
            os.path.relpath(f, root),
            int(bm.group(1)) if bm else None,
            vm.group(1) if vm else None,
            " ".join(x.strip() for x in pm.group(1).split("\n")).strip(),
        ))
    return out


def read_job_variants(root):
    """pipeline/jobs/*.yaml → [(job_id, variant)] for every `--variant X` argv pair.

    A job spec is forward-looking: it is what WILL be sent. Line-based for the
    same reason as wave-drafts — these files carry long provenance headers.
    """
    out = []
    for f in sorted(glob.glob(os.path.join(root, "pipeline", "jobs", "*.yaml"))):
        try:
            lines = open(f, errors="replace").read().split("\n")
        except OSError:
            continue
        job = os.path.splitext(os.path.basename(f))[0]
        for i, l in enumerate(lines[:-1]):
            if l.strip() == "- --variant":
                v = lines[i + 1].strip()
                if v.startswith("- "):
                    out.append((job, v[2:].strip()))
    return out


_PROMPT_KEY = re.compile(r"prompt", re.I)
_NEGATIVE_KEY = re.compile(r"negative|neg\b", re.I)


RUN_LEDGER = os.path.join("pipeline", "measured", "queue-history.json")


def read_run_ledger(root):
    """The authoritative record of what has actually fired → (tasks, specs, ok).

    `pipeline/measured/queue-history.json` carries 573 completed runs with `task`,
    `spec_file`, `rc` and the exact prompt sent. It is the ONLY reliable answer to
    "has this spec run", and this checker got that question wrong twice by trying
    to infer it from the filesystem:

      1. farm-out/ alone reported four specs un-fired that had rendered, because
         their sidecars sit under review/.
      2. farm-out IS PRUNED, so age alone manufactures "unrun" — which put
         ep2-b18-plantneg-0812 and ep2-b18-refresh-0811 on the FAIL list when both
         are in the ledger at rc=0.

    A row of any rc counts as "it ran": the prompt reached the box either way, and
    that is what makes the spec a receipt rather than pending work.

    `ok` is False when the ledger cannot be read. The caller must then ABSTAIN on
    anything that depends on run status rather than assume nothing has run — that
    assumption is precisely what produced both false-positive rounds.
    """
    p = Path(root) / RUN_LEDGER
    if not p.exists():
        return set(), set(), False
    try:
        doc = json.loads(p.read_text(errors="replace"))
    except Exception:
        return set(), set(), False
    jobs = doc.get("jobs") if isinstance(doc, dict) else doc
    if not isinstance(jobs, list):
        return set(), set(), False
    tasks, specs = set(), set()
    for r in jobs:
        if not isinstance(r, dict):
            continue
        if r.get("task"):
            tasks.add(str(r["task"]))
        if r.get("spec_file"):
            specs.add(os.path.splitext(os.path.basename(str(r["spec_file"]).replace("\\", "/")))[0])
    return tasks, specs, True


def read_ledger_prompts(root):
    """The run ledger's own `prompt` field → the same shape as a sidecar.

    THIS IS THE HALF THAT MAKES R3 GIVE THE SAME ANSWER IN CI AND ON A LAPTOP.
    farm-out/ is largely UNTRACKED — 456 of the 509 render sidecars on this
    machine are not in the repo — so a CI checkout sees 53 of them and none from
    farm-out at all. R3 asks "has any render ever carried this canon", and
    answering it from a corpus that is 90% absent is how a check invents a
    finding. queue-history.json is tracked, carries 573 completed runs, and each
    row records the exact prompt that was sent.

    Measured the day this was added: the sidecars alone said PURPLE had reached
    zero of 56 rendered prompts on beats 19/20; the ledger has six rows on those
    beats carrying it. The sidecars were not lying, they were missing.
    """
    p = Path(root) / RUN_LEDGER
    if not p.exists():
        return []
    try:
        doc = json.loads(p.read_text(errors="replace"))
    except Exception:
        return []
    jobs = doc.get("jobs") if isinstance(doc, dict) else doc
    if not isinstance(jobs, list):
        return []
    out = []
    for r in jobs:
        if not isinstance(r, dict):
            continue
        prompt = str(r.get("prompt") or "").strip()
        if not prompt:
            continue
        beat = str(r.get("beat", "")).strip()
        out.append((f"{RUN_LEDGER}:{r.get('id') or r.get('task')}",
                    int(beat) if beat.isdigit() else None,
                    r.get("task"),
                    " ".join(prompt.split())))
    return out


_SPEC_CACHE = {}


def read_job_specs(root):
    """pipeline/jobs/*.yaml → [(path, job_id, doc)] for every spec that parses.

    Cached per root because two rules now want the parsed specs and there are 824
    of them; parsing the directory twice doubled the run for no new information.
    A spec that will not parse is skipped, not guessed at — the same abstention
    the payload reader has always made.
    """
    key = os.path.abspath(root)
    hit = _SPEC_CACHE.get(key)
    if hit is not None:
        return hit
    out = []
    for f in sorted(glob.glob(os.path.join(root, "pipeline", "jobs", "*.yaml"))):
        try:
            doc = yaml.safe_load(open(f, errors="replace").read())
        except Exception:
            continue  # a spec we cannot parse is not a spec we may judge
        if not isinstance(doc, dict):
            continue
        out.append((f, os.path.splitext(os.path.basename(f))[0], doc))
    _SPEC_CACHE[key] = out
    return out


def read_job_payload_prompts(root, only_jobs=None):
    """pipeline/jobs/*.yaml `payload:` → [(beat, label, prompt_text)].

    THE PLACE DRIFT ACTUALLY HAPPENS, and the first cut of this checker was blind
    to it. A job spec's `payload:` is a map of destination path → file CONTENT,
    and the prompt the model sees is a `*prompt*.txt` value in there. Neither
    `TALLER THAN HE IS` (six specs) nor `ONE SINGLE ROUND GREEN FIG` (three) nor
    `wide oval cotyledon leaves … not lance-shaped` appears in wave-drafts.yaml at
    all — they exist only in payloads.

    `*negative*.txt` values are SKIPPED on purpose. A negative file listing
    `pointed leaves, lance-shaped leaves` is banning that shape, not asking for
    it; counting it as an assertion would invert every anti-term in the repo.
    """
    out = []
    for f, job, doc in read_job_specs(root):
        payload = doc.get("payload")
        if not isinstance(payload, dict):
            continue
        beat = doc.get("beat")
        beat = int(beat) if isinstance(beat, (int, str)) and str(beat).isdigit() else None
        job = os.path.splitext(os.path.basename(f))[0]
        if only_jobs is not None and job not in only_jobs:
            continue
        for dest, content in payload.items():
            name = os.path.basename(str(dest).replace("\\", "/"))
            if not isinstance(content, str) or not name.lower().endswith(".txt"):
                continue
            if _NEGATIVE_KEY.search(name) or not _PROMPT_KEY.search(name):
                continue
            out.append((beat, f"jobs/{job}:{name}", " ".join(content.split())))
    return out


def walk_yaml_strings(node, path=(), parents=(), in_list=False):
    """Yield (path, parents, string) for every leaf string.

    `parents` carries the chain of enclosing mappings as (mapping, key, is_row)
    so a correction written on an ANCESTOR key suppresses hits inside the block
    it corrects — which is how done-definitions.yaml actually does it
    (`guards_CORRECTION_0816` sits beside `guards`, not beside the line inside it
    that says "do not cast them").

    `is_row` says the mapping was reached as an element of a LIST, so it has no
    key of its own for a correction to name. See correction_sibling.
    """
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk_yaml_strings(v, path + (str(k),), parents + ((node, str(k), in_list),), False)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_yaml_strings(v, path + (f"[{i}]",), parents, True)
    elif isinstance(node, str):
        yield path, parents, node


_CORRECTION_SUFFIX = re.compile(r"^(?P<base>.+?)_[A-Z][A-Z_0-9]*_(?P<date>\d{4})$")


def correction_sibling(parents):
    """A dated `<key>_SOMETHING_MMDD` sibling of the key or any ancestor.

    The house convention since 2026-08-16: superseded text is LEFT STANDING and a
    dated correction key is added beside it. Detecting the correction is what lets
    the check be quiet on a record that was honestly fixed, instead of demanding
    that history be rewritten.

    The base is matched as a PREFIX in either direction, because the corrections
    actually written do both: `guards_CORRECTION_0816` corrects `guards` exactly,
    while `the_second_gate_CORRECTION_0816` corrects the longer key
    `the_second_gate_underneath_it` sitting beside it.

    SECOND FORM, ADDED 2026-08-16 FOR A RECORD THE FIRST FORM COULD NOT REACH. In
    pipeline/measured/episode-progress.yaml the twelve goblin beats are LIST ROWS:

        - n: 2
          state: blocked-decision
          note: goblin beat — held by the character-first ruling; no animation …
          state_CORRECTION_0816: 'CORRECTION, 2026-08-16: the "character gate" …'

    The stale assertion is in `note` and the correction names `state`, so the
    prefix rule misses it and the row reports as uncorrected. A list row has NO
    KEY OF ITS OWN for a correction to name — that is why the lane keyed it to the
    row's load-bearing field — so inside a row a dated correction is a correction
    OF THE ROW. Deliberately narrow in two ways: it applies only to mappings
    reached through a list, and the corrected base must be a real key of that same
    row, so a stray dated key cannot silence anything. It is strictly narrower than
    the ancestor form above, which already lets one correction cover a whole block.
    """
    for mapping, key, is_row in parents:
        for other in mapping:
            other = str(other)
            if other == key:
                continue
            m = _CORRECTION_SUFFIX.match(other)
            if not m:
                continue
            base = m.group("base")
            if base == key or key.startswith(base + "_") or base.startswith(key + "_"):
                return other
            if is_row and base in mapping:
                return other
    return None


def _flat(s):
    """Whitespace-normalised text, for substring checks that must survive the
    line-wrapping every hand-written record in this repo uses — including the
    `# ` that starts each continuation line of a job spec's provenance header."""
    return " ".join(re.sub(r"\n\s*#\s?", "\n", str(s)).split())


_STRUCK_SPAN = re.compile(r"~~.*?~~", re.S)


def live_prose(text):
    """Text with SUPERSEDED spans removed, for evidence assertions only.

    THE HOLE THIS CLOSES, measured 2026-08-17 and not argued. House style §6
    keeps superseded prose VISIBLE FOREVER, struck with `~~`, because the
    provenance is the point. So a `contains:` assertion pointed at prose that is
    later superseded keeps passing on the struck-through corpse of its own claim,
    and passes indefinitely. `sapling-cotyledon-shape` asserted
    'The working canon is ROUND/OVAL COTYLEDONS', which was superseded on
    2026-08-17 and is STILL PHYSICALLY PRESENT at THE-SAPLING.md:81 inside the
    struck block — so the gate was green on dead text and was never going to
    fail. A canon-honesty instrument that has quietly stopped checking is worse
    than none, because it reports a safety it is not measuring.

    ONLY `~~` MEANS DEAD, AND THIS IS THE HALF OF THE WRITTEN FIX THAT WAS WRONG.
    The proposal in canon-patch-cotyledon-0817.md was to skip `~~`-struck AND
    `>`-quoted blocks. Measured over all 8 subjects, stripping quoted blocks too
    turns `sapling-height` red FALSELY: it asserts `about 40 cm, always shorter
    than he`, which lives inside a `>` blockquote. In this repo `>` marks a
    QUOTATION — most often the founder's own words — the most ALIVE text in the
    document. Conflating the two would make this checker fail an entry whose
    canon is current, which is the cry-wolf shape that gets instruments switched
    off. So blockquotes are left alone; see CORRECTION_0817 in that file.

    Deliberately narrow: spans are matched across newlines (a strike in this repo
    wraps over several `>` continuation lines) and replaced with a SPACE, so no
    needle can false-match by joining text across the removed gap. An UNBALANCED
    `~~` cannot be resolved into spans, so it is reported rather than guessed at
    — see the abstention in check_register_freshness.
    """
    return _STRUCK_SPAN.sub(" ", text)


# ---------------------------------------------------------------------------
# REGISTER
# ---------------------------------------------------------------------------

def load_register(root, path=None):
    p = Path(path) if path else Path(root) / "pipeline" / "canon.yaml"
    if not p.exists():
        return None, [Finding(UNKNOWN, "register", "-", str(p), "no canon register; nothing to check against")]
    return yaml.safe_load(p.read_text()), []


def check_register_freshness(root, reg):
    """The register must not be the fourth thing that goes stale.

    Each subject names a file and a literal string that must still be in it. This
    is a CONTENT check on purpose: a weights manifest passed files full of holes
    this week by comparing lengths where a hash would have caught it.
    """
    out = []
    for s in reg.get("subjects", []):
        ev = s.get("evidence") or {}
        f, needle = ev.get("file"), ev.get("contains")
        if not f or not needle:
            out.append(Finding(UNKNOWN, "register_evidence", s["id"], "pipeline/canon.yaml",
                               "entry names no evidence file+string, so its canon cannot be verified"))
            continue
        p = Path(root) / f
        if not p.exists():
            out.append(Finding(FAIL, "register_evidence_missing", s["id"], f,
                               "evidence file is gone; the register is asserting a canon nothing backs"))
            continue
        raw = p.read_text(errors="replace")
        # Superseded prose stays visible forever (house style §6), so the
        # assertion must read only the LIVE text or it passes on a corpse.
        if raw.count("~~") % 2:
            out.append(Finding(UNKNOWN, "register_evidence_unstruckable", s["id"], f,
                               "the file has an odd number of `~~` markers, so superseded spans "
                               "cannot be told from live prose; not guessing which half is canon"))
        if _flat(needle) not in _flat(live_prose(raw)):
            struck = _flat(needle) in _flat(raw)
            out.append(Finding(
                FAIL, "register_evidence_missing", s["id"], f,
                (f"evidence string survives ONLY inside a ~~struck-through~~ block: {needle!r} — "
                 "the file marks that text SUPERSEDED, so this entry is asserting a canon the "
                 "document has already retired. Repoint `contains:` at the live prose that "
                 "replaced it; do not un-strike the old text")
                if struck else
                (f"evidence string is no longer in the file: {needle!r} — "
                 "the canon moved and this register did not")))
    return out


# ---------------------------------------------------------------------------
# R1 — a resolved founder decision that a record still calls open
# ---------------------------------------------------------------------------

def _card_resolution(inbox_cards, spec):
    """Locate the resolving card BY CONTENT. Returns (card, why_not)."""
    want_url = spec.get("card_url_contains")
    want_what = spec.get("card_what_contains")
    want_verdict = spec.get("verdict_matches")
    hits = []
    for c in inbox_cards:
        if not isinstance(c, dict):
            continue
        if want_url and want_url not in str(c.get("url", "")):
            continue
        if want_what and want_what not in str(c.get("what", "")):
            continue
        hits.append(c)
    if not hits:
        return None, "no card in review/inbox.yaml matches the register's locator"
    if len(hits) > 1:
        return None, f"{len(hits)} cards match the locator; it does not identify one decision"
    card = hits[0]
    res = card.get("resolved")
    if not res:
        return None, "the card is still open — subject is legitimately unresolved"
    if want_verdict and not re.search(want_verdict, str(res.get("verdict", "")), re.I):
        return None, (f"the card is resolved but its verdict does not match {want_verdict!r}; "
                      "the register may be pointing at the wrong resolution")
    return card, None


def rule_resolved_but_open(root, reg, inbox_cards):
    out = []
    rec = reg.get("records") or {}
    structured = rec.get("structured") or []
    prose = rec.get("prose") or []

    for s in reg.get("subjects", []):
        if s.get("kind") != "founder_decision":
            continue
        card, why = _card_resolution(inbox_cards, s.get("resolved_by") or {})
        if card is None:
            out.append(Finding(UNKNOWN, "resolved_but_open", s["id"], "review/inbox.yaml", why))
            continue
        date = str((card.get("resolved") or {}).get("date", "?"))
        opens = [re.compile(p, re.I) for p in s.get("open_phrases", [])]
        negs = [re.compile(p, re.I) for p in s.get("negation_cues", [])]

        def asserts_open(text):
            if not any(r.search(text) for r in opens):
                return False
            return not any(r.search(text) for r in negs)

        # -- structured records: adjudicable, so these can FAIL.
        for f in structured:
            p = Path(root) / f
            if not p.exists():
                continue
            try:
                doc = yaml.safe_load(p.read_text(errors="replace"))
            except Exception as e:
                out.append(Finding(UNKNOWN, "resolved_but_open", s["id"], f,
                                   f"record does not parse as YAML ({e.__class__.__name__}); not adjudicated"))
                continue
            for path, parents, text in walk_yaml_strings(doc):
                if not asserts_open(text):
                    continue
                fixed = correction_sibling(parents)
                if fixed:
                    continue
                out.append(Finding(
                    FAIL, "resolved_but_open", s["id"], f"{f}:{'.'.join(path)}",
                    f"still asserts the subject is open, but review/inbox.yaml resolved it on {date} "
                    f"and no dated *_CORRECTION_MMDD sibling exists — {_snip(text, opens)}"))

        # -- prose logs: append-only, so REVIEW only. Measured: pairing prose lines
        #    to decisions by content produced 47 hits and mostly wrong ones.
        for f in prose:
            p = Path(root) / f
            if not p.exists():
                continue
            for ln, line in enumerate(p.read_text(errors="replace").split("\n"), 1):
                if asserts_open(line):
                    out.append(Finding(
                        REVIEW, "resolved_but_open", s["id"], f"{f}:{ln}",
                        f"append-only log asserts the subject is open; resolved {date} — {line.strip()[:120]}"))
    return out


def _snip(text, regexes):
    for r in regexes:
        m = r.search(text)
        if m:
            a, b = max(0, m.start() - 40), min(len(text), m.end() + 40)
            return "…" + " ".join(text[a:b].split()) + "…"
    return " ".join(text.split())[:120]


# ---------------------------------------------------------------------------
# R2 — a canonical attribute contradicted by prompts that run
# ---------------------------------------------------------------------------

def _in_scope(scope, beat, prompt):
    beats = scope.get("beats")
    if beats is not None and beat not in beats:
        return False
    mentions = scope.get("prompt_mentions")
    if mentions and not re.search(mentions, prompt, re.I):
        return False
    return True


def unrun_jobs(root, jobs, runs):
    """Job specs with no render evidence — the ones still pointing forward.

    pipeline/jobs/ is 824 specs and most of them fired days ago; a spec that has
    already produced frames is history and re-reporting it forever is exactly the
    noise that got the runner watchdog switched off. A job counts as RUN when its
    id names a farm-out directory or its variant appears in a render-time sidecar.
    Content, not a status field: the queue's own `ready: 0` was wrong about a real
    3 this week.
    """
    tasks, specs, ledger_ok = read_run_ledger(root)
    if not ledger_ok:
        return []  # cannot tell what ran; the caller reports the abstention
    ran_variants = {v for _, _, v, _ in runs if v}
    ran_dirs = set()
    for d in RUN_EVIDENCE_DIRS:
        p = Path(root) / d
        if p.is_dir():
            ran_dirs |= {c.name for c in p.iterdir() if c.is_dir()}
    out = []
    for job, variant in jobs:
        if job in tasks or job in specs:
            continue
        if variant in ran_variants:
            continue
        if any(job.startswith(d) or d.startswith(job) for d in ran_dirs):
            continue
        out.append((job, variant))
    return out


def rule_prompt_contradicts_canon(root, reg, variants, jobs, all_prompts=None):
    """Compare what the canon says a subject IS against what the prompts ask for.

    The subject scope is what makes this possible at all: `bald` is CANON for the
    goblin (272 rendered prompts) and the DEFECT for the guards (84). Scoping by
    beat plus a content test on the prompt separates them; nothing at word level can.
    """
    out = []
    by_variant = {v: (b, p) for b, v, p in variants}
    # Everything ever written, live or fired. Needed to tell a suppression entry
    # that is WRONG from one that is merely no longer needed.
    ever = {v for _, v, _ in (all_prompts if all_prompts is not None else variants)}
    queued = {}
    for job, v in jobs:
        queued.setdefault(v, []).append(job)

    for s in reg.get("subjects", []):
        if s.get("kind") != "prompt_canon":
            continue
        forbids = [re.compile(p, re.I) for p in s.get("forbids", [])]
        if not forbids:
            continue
        scope = s.get("scope") or {}
        ack = s.get("acknowledged") or {}
        ack_variants = set(ack.get("variants") or [])
        ack_hit = set()

        # The acknowledgement list is only honoured while the record that carries
        # it still says so. Verified by content, not by the list's existence.
        ack_live = True
        if ack_variants:
            rp = Path(root) / str(ack.get("recorded_in", ""))
            needle = str(ack.get("recorded_contains", ""))
            if not rp.exists() or (needle and _flat(needle) not in _flat(rp.read_text(errors="replace"))):
                ack_live = False
                out.append(Finding(FAIL, "acknowledgement_unrecorded", s["id"],
                                   str(ack.get("recorded_in")),
                                   "the record that is supposed to carry these known contradictions no longer "
                                   f"contains {needle!r}; the suppression list is not backed by anything"))

        for beat, variant, prompt in variants:
            if not _in_scope(scope, beat, prompt):
                continue
            hit = next((r for r in forbids if r.search(prompt)), None)
            if not hit:
                continue
            if variant in ack_variants and ack_live:
                ack_hit.add(variant)
                # An acknowledged draft may exist. Sending it is another matter.
                if variant in queued:
                    out.append(Finding(
                        FAIL, "unrun_job_against_canon", s["id"],
                        f"pipeline/jobs/{queued[variant][0]}.yaml",
                        f"a spec with no render evidence still sends beat-{beat} variant `{variant}`, which "
                        f"asks {hit.pattern} against canon since {s.get('since')} — an acknowledged draft may "
                        "sit in history, but nothing may fire it"))
                else:
                    out.append(Finding(
                        ACK, "prompt_contradicts_canon", s["id"], f"wave-drafts.yaml b{beat:02d}:{variant}",
                        f"asks {hit.pattern}; known and recorded in {ack.get('recorded_in')}"))
                continue
            out.append(Finding(
                FAIL, "prompt_contradicts_canon", s["id"], f"wave-drafts.yaml b{beat:02d}:{variant}",
                f"prompt asks {hit.pattern} but the canon since {s.get('since')} says otherwise — "
                f"{_snip(prompt, [hit])}"))

        for v in sorted(ack_variants - ack_hit):
            if v in ever and v not in by_variant:
                # The prompt exists but is a FIRED RECEIPT, so no rule looks at it
                # any more. The entry is not wrong, it is surplus — saying so at
                # ACK keeps a lane's tidy-up off the failure list.
                out.append(Finding(
                    ACK, "acknowledgement_no_longer_needed", s["id"], f"pipeline/canon.yaml:{v}",
                    "the prompt this suppresses belongs to a spec that has already run, so it is no "
                    "longer compared against canon; the entry can be dropped"))
                continue
            known = ("no longer contradicts the canon" if v in by_variant
                     else "matches no prompt anywhere in the repo")
            out.append(Finding(FAIL, "stale_acknowledgement", s["id"], f"pipeline/canon.yaml:{v}",
                               f"acknowledged variant {known}; prune it so the list stays a list of real exceptions"))
    return out


# ---------------------------------------------------------------------------
# R3 — a canon no running artifact has ever used
# ---------------------------------------------------------------------------

def rule_canon_never_ran(root, reg, variants, runs):
    """Has any frame ever been drawn from a prompt carrying this canon?

    Drafts and job specs do not count. Only farm-out sidecars, which the harness
    writes at render time, prove a picture exists — and a picture is the only
    thing the founder is ever shown.
    """
    out = []
    for s in reg.get("subjects", []):
        if s.get("kind") != "prompt_canon" or not s.get("must_have_run"):
            continue
        req = [re.compile(p, re.I) for p in s.get("requires_any", [])]
        if not req:
            out.append(Finding(UNKNOWN, "canon_never_ran", s["id"], "pipeline/canon.yaml",
                               "must_have_run is set but requires_any is empty; nothing to look for"))
            continue
        scope = s.get("scope") or {}

        drafted = [f"b{b:02d}:{v}" for b, v, p in variants
                   if _in_scope(scope, b, p) and any(r.search(p) for r in req)]
        in_scope_runs = [r for r in runs if _in_scope(scope, r[1], r[3])]
        ran = [r for r in in_scope_runs if any(rx.search(r[3]) for rx in req)]

        if not drafted:
            out.append(Finding(UNKNOWN, "canon_never_ran", s["id"], "pipeline/wave-drafts.yaml",
                               "no draft in scope carries this canon at all, so 'never rendered' cannot be "
                               "distinguished from 'never written'"))
            continue
        if not in_scope_runs:
            out.append(Finding(UNKNOWN, "canon_never_ran", s["id"], "farm-out/",
                               f"{len(drafted)} draft(s) carry the canon and NO render evidence exists in scope; "
                               "cannot tell whether it ran elsewhere"))
            continue
        if not ran:
            out.append(Finding(
                FAIL, "canon_never_ran", s["id"], "farm-out/",
                f"canon since {s.get('since')} is in {len(drafted)} draft(s) ({', '.join(sorted(drafted))}) "
                f"and in ZERO of the {len(in_scope_runs)} rendered prompts in scope — every frame anyone can be "
                "shown for this subject predates the canon"))
    return out


# ---------------------------------------------------------------------------
# R4 — an attribute the prompts describe inconsistently with EACH OTHER
# ---------------------------------------------------------------------------

# `no green fig` asserts the opposite of `green fig`. Without this the rule reads
# every anti-term in a negative block as an assertion of the thing it bans, which
# on this repo's prompts is most of them.
_DENIAL = re.compile(r"(?:\bno\b|\bnot\b|\bwithout\b|\bnever\b)[^,.;]{0,30}$", re.I)


def _asserted_values(axis, variants):
    """{value: [(beat, variant, snippet)]} for values POSITIVELY asserted."""
    found = {}
    for value, pats in (axis.get("values") or {}).items():
        for beat, variant, prompt in variants:
            if not _in_scope(axis.get("scope") or {}, beat, prompt):
                continue
            for pat in pats:
                m = None
                for cand in re.finditer(pat, prompt, re.I):
                    if _DENIAL.search(prompt[max(0, cand.start() - 30):cand.start()]):
                        continue
                    m = cand
                    break
                if m:
                    a, b = max(0, m.start() - 35), min(len(prompt), m.end() + 25)
                    found.setdefault(value, []).append(
                        (beat, variant, "…" + " ".join(prompt[a:b].split()) + "…"))
                    break
    return found


def rule_attribute_unpinned(reg, variants):
    """Instance 2's shape with the twist that there was no canon to contradict.

    The sapling has no canonical description at all: twelve beats show the plant
    and the prompts improvised it in opposite directions — `wide oval cotyledon
    leaves` on some beats against `deeply lobed fig leaves with five fingers` on
    others, with BEAT 01 CARRYING BOTH across its own variants.

    This rule does not rule on which value is right — that is taste and it is the
    founder's. It reports only that the drafts disagree and that no registered
    subject pins the attribute, which is a fact about our files. Silencing it means
    writing the canon down, which is the action actually wanted. It fires at most
    once per declared axis, so it cannot become a wall of noise.
    """
    out = []
    # An axis is retired the moment a subject pins it — by explicit `pins_axis`,
    # or by simply carrying the same id, which is how a lane that adopts this
    # register naturally writes it. Without the id rule the sapling canon was
    # reported twice on 2026-08-16: once as a subject violation and once as an
    # unpinned axis. Duplicate reporting is how a check earns its way to /dev/null.
    subjects = reg.get("subjects", [])
    pinned = {s.get("pins_axis") for s in subjects if s.get("pins_axis")}
    pinned |= {s.get("id") for s in subjects if s.get("id")}
    for axis in reg.get("axes", []) or []:
        aid = axis.get("id", "?")
        if aid in pinned:
            continue
        found = _asserted_values(axis, variants)
        if len(found) < 2:
            out.append(Finding(UNKNOWN, "attribute_unpinned", aid, "pipeline/wave-drafts.yaml",
                               f"{len(found)} of {len(axis.get('values') or {})} declared values are asserted "
                               "anywhere; one value is not a contradiction and absence is not proof"))
            continue
        level = FAIL if axis.get("must_be_pinned") else REVIEW
        parts = []
        for value, hits in sorted(found.items()):
            beats = sorted({f"b{b:02d}" for b, _, _ in hits})
            parts.append(f"{value}={len(hits)} draft(s) on {','.join(beats)} e.g. {hits[0][1]} {hits[0][2]}")
        both = sorted({b for hs in found.values() for b, _, _ in hs}
                      .intersection(*[{b for b, _, _ in hs} for hs in found.values()]))
        clash = f" — beat(s) {','.join(f'b{b:02d}' for b in both)} carry BOTH" if both else ""
        out.append(Finding(level, "attribute_unpinned", aid, "pipeline/wave-drafts.yaml",
                           f"prompts disagree and no registered subject pins this attribute{clash}: "
                           + " | ".join(parts)))
    return out


# ---------------------------------------------------------------------------
# R5 — one beat's bar attached to another beat's spec
# ---------------------------------------------------------------------------

DEFAULT_BAR_FIELDS = ("success",)


def _bar_groups(root, fields):
    """{(field, normalised text): [(job, beat)]} over specs that carry the field.

    A spec whose field has a dated `<field>_*_MMDD` correction sibling DROPS OUT.
    That is the house convention for a superseded line, and it is also what keeps
    this rule off its own tail: the corrections written to discharge it quote the
    prose they replace, and a rule that reads its own corrections as fresh
    instances never goes quiet. (The lane that found this paste hit the same wall
    from the other side — its first selector grepped "ALL-21 WAVE" and matched 34
    files because the correction prose names the wave.) The correction TEXT is
    never grouped either: only the `<field>` key itself is read.
    """
    groups = {}
    for _f, job, doc in read_job_specs(root):
        beat = doc.get("beat")
        if not (isinstance(beat, (int, str)) and str(beat).isdigit()):
            continue  # a spec with no beat cannot be attached to the wrong one
        beat = int(beat)
        for field in fields:
            text = doc.get(field)
            if not isinstance(text, str) or not text.strip():
                continue
            if correction_sibling(((doc, field, False),)):
                continue
            groups.setdefault((field, " ".join(text.split())), []).append((job, beat))
    return groups


def rule_bar_serves_two_beats(root, reg):
    """A judging bar that belongs to one beat, recorded on the specs of others.

    THE LOSS, 2026-08-14/16. The ALL-21 wave was authored by copying one spec, and
    the paste went far past the wave: 80 specs in pipeline/jobs/ carried beat 02's
    `success` line and only 13 of them are beat 02 — including beat 16, which was
    never in the wave. queue_history.py copies `success` into the run ledger's
    `purpose` block, so 352 ledger rows published a bar reading "a LEAN ADULT
    goblin sprints in, skids and dives behind a sapling" for clips of beats that
    do no such thing, and /queue showed it. Beat 20 is the fig and the look up.

    WHY NONE OF R1-R4 CAN EXPRESS THIS, and the diagnosis handed over is right:
    the prose contradicts NO canon. It is canonical prose about the wrong beat.
    Every earlier rule compares an attribute to a record; here both halves are
    correct and only the attachment is wrong.

    WHY THIS FIRES AT REVIEW BY DEFAULT AND NOT AT FAIL. The rule as first handed
    over — "no two specs with different `beat:` values may share byte-identical
    purpose prose" — was measured on this repo before it was written, and it does
    NOT have the zero false positives it was credited with:

      * over `consumer` and `why` it produces 45 more cross-beat groups, nearly
        all legitimate. A wave has ONE consumer and ONE rationale across twenty
        beats: "motion-wave, which re-animates this beat off the plate" is shared
        by 24 specs on 13 beats and is correct on every one of them. So the field
        list is `success` only — the bar is the per-beat thing.
      * even over `success` alone, 13 groups span more than one beat on this repo
        and only ONE is the defect. "Plate frames with this beat's own location
        ALREADY IN THEM" is written beat-agnostically ON PURPOSE, and the board
        bar is repeated from beat 06 onto beat 10 deliberately, because the board
        is the subject of both. Failing on all thirteen would be 8% precision —
        the cry-wolf shape that got the runner watchdog switched off.

    So the checker reports what it can see (these specs share a bar across beats)
    and abstains on what it cannot (whether that is a wave-wide bar or a paste),
    and a `bars:` entry in the register turns the abstention into a verdict:

      owned_by_beat: N  → every spec in the group on another beat FAILS.
      shared: true      → deliberate; silent.

    Both are content-checked: an entry whose `contains:` matches no spec fails as
    `stale_bar_entry`, so the register prunes itself rather than aging into a lie.
    """
    entries = reg.get("bars") or []
    fields = tuple(reg.get("bar_fields") or DEFAULT_BAR_FIELDS)
    groups = _bar_groups(root, fields)
    out = []
    matched_entries = set()

    for (field, text), rows in sorted(groups.items()):
        beats = sorted({b for _, b in rows})
        entry = next((e for e in entries
                      if (e.get("field") or "success") == field
                      and _flat(e.get("contains", "\0")) in _flat(text)), None)
        if entry is not None:
            matched_entries.add(entry.get("id"))
        if len(beats) < 2:
            continue
        if entry is None:
            out.append(Finding(
                REVIEW, "bar_serves_two_beats", "-", f"pipeline/jobs/ ({len(rows)} specs)",
                f"one `{field}:` line is the recorded bar for beats "
                f"{', '.join('b%02d' % b for b in beats)} — a wave-wide bar and a paste look "
                f"identical from here, and no `bars:` entry rules on it: {text[:110]}…"))
            continue
        if entry.get("shared"):
            continue
        owner = entry.get("owned_by_beat")
        if owner is None:
            out.append(Finding(
                UNKNOWN, "bar_serves_two_beats", entry.get("id", "?"), "pipeline/canon.yaml",
                "entry says neither `owned_by_beat:` nor `shared: true`, so the collision it "
                "matches is not adjudicated"))
            continue
        ack = entry.get("acknowledged") or {}
        ack_specs = set(ack.get("specs") or [])
        ack_live = True
        if ack_specs:
            rp = Path(root) / str(ack.get("recorded_in", ""))
            needle = str(ack.get("recorded_contains", ""))
            if not rp.exists() or (needle and _flat(needle) not in _flat(rp.read_text(errors="replace"))):
                ack_live = False
                out.append(Finding(FAIL, "acknowledgement_unrecorded", entry.get("id", "?"),
                                   str(ack.get("recorded_in")),
                                   "the record that is supposed to excuse these specs no longer "
                                   f"contains {needle!r}; the suppression list is not backed by anything"))
        seen_specs = {j for j, _ in rows}
        for job, beat in sorted(rows):
            if beat == int(owner):
                continue
            if job in ack_specs and ack_live:
                continue
            out.append(Finding(
                FAIL, "bar_serves_two_beats", entry.get("id", "?"), f"pipeline/jobs/{job}.yaml",
                f"this spec is beat {beat} and records beat {owner}'s bar as its own `{field}:`; "
                "queue_history.py copies it into the ledger's purpose block, so the clip is "
                "published to be judged against another beat's action — write this beat's own bar "
                f"or a dated {field}_CORRECTION_MMDD sibling: {text[:90]}…"))
        for job in sorted(ack_specs - seen_specs):
            out.append(Finding(
                ACK, "acknowledgement_no_longer_needed", entry.get("id", "?"),
                f"pipeline/canon.yaml:{job}",
                "the spec this excuses no longer carries the bar (deleted, or corrected in place), "
                "so the entry can be dropped"))

    for e in entries:
        if e.get("id") in matched_entries:
            continue
        out.append(Finding(
            FAIL, "stale_bar_entry", e.get("id", "?"), "pipeline/canon.yaml",
            f"no job spec carries {str(e.get('contains'))[:70]!r} any more; this entry is asserting "
            "a collision that no longer exists, and a register that cannot go stale is the point"))
    return out


# ---------------------------------------------------------------------------
# COVERAGE — the register's own gaps, reported as abstentions, never as failures
# ---------------------------------------------------------------------------

def rule_unregistered_decisions(reg, inbox_cards, since=None):
    """Which resolved decisions no subject adjudicates — the register's real reach.

    `also_records:` exists because ONE decision can be recorded on more than one
    card. The founder's "seed s0 is the goblin" answers both the numbered picker
    card and the plates card that asked the same question in older words; only one
    of them can be the subject's `resolved_by` locator, because _card_resolution
    must identify exactly ONE card or it abstains. Listing the other here says so
    explicitly instead of leaving the same ruling on the uncovered list forever.
    It is COVERAGE BOOKKEEPING ONLY — it never adjudicates anything, so it cannot
    become the similarity matching this checker refuses to do.
    """
    out = []
    registered = set()
    for s in reg.get("subjects", []):
        for rb in [s.get("resolved_by") or {}] + list(s.get("also_records") or []):
            for k in ("card_url_contains", "card_what_contains"):
                if isinstance(rb, dict) and rb.get(k):
                    registered.add(rb[k])
    for c in inbox_cards:
        if not isinstance(c, dict) or not c.get("resolved"):
            continue
        url, what = str(c.get("url", "")), str(c.get("what", ""))
        if any(t in url or t in what for t in registered):
            continue
        date = str((c.get("resolved") or {}).get("date", ""))
        if since and date < since:
            continue
        out.append(Finding(UNKNOWN, "unregistered_decision", "-", "review/inbox.yaml",
                           f"resolved {date}: {what[:90]} — no subject registered, so no record was checked "
                           "against it"))
    return out


# ---------------------------------------------------------------------------

def run(root, register_path=None, coverage_since=None):
    root = str(root)
    _SPEC_CACHE.clear()  # one run = one read of disk; the cache never outlives it
    reg, findings = load_register(root, register_path)
    if reg is None:
        return findings

    inbox = Path(root) / "review" / "inbox.yaml"
    cards = yaml.safe_load(inbox.read_text(errors="replace")) if inbox.exists() else []
    if not isinstance(cards, list):
        cards = []

    wd = Path(root) / "pipeline" / "wave-drafts.yaml"
    variants = read_draft_variants(wd.read_text(errors="replace")) if wd.exists() else []
    # Render evidence is the union of what the box wrote beside each frame and
    # what the tracked ledger recorded. Neither alone is complete.
    runs = read_run_evidence(root) + read_ledger_prompts(root)
    jobs = read_job_variants(root)

    # THE TWO HALVES OF THE PROMPT CORPUS ARE NOT THE SAME KIND OF THING, and
    # conflating them is what produced 34 findings against already-fired specs.
    #
    #   * wave-drafts.yaml is a LIVE PROMPT BANK. Any `authored*` variant in it can
    #     be sent again tomorrow by `--variant`, so a canon violation there is
    #     pending work no matter how old the text is.
    #   * a job spec's `payload:` is a ONE-SHOT RECEIPT. Once it has fired, its
    #     prompt is history; re-reporting it every run forever is exactly the noise
    #     that got the runner watchdog switched off for four days.
    #
    # So payload prompts are compared against canon only for specs that have NOT
    # run — and if the ledger cannot be read we do not guess, we abstain.
    ledger_tasks, ledger_specs, ledger_ok = read_run_ledger(root)
    all_payloads = read_job_payload_prompts(root)
    if ledger_ok:
        ran = ledger_tasks | ledger_specs
        pending = {j for j, _ in read_job_variants(root)} | {
            lbl.split("/", 1)[1].split(":", 1)[0] for _, lbl, _ in all_payloads}
        pending -= ran
        live_payloads = read_job_payload_prompts(root, only_jobs=pending)
    else:
        live_payloads = []
        findings.append(Finding(
            UNKNOWN, "run_status", "-", RUN_LEDGER,
            f"no readable run ledger, so {len(all_payloads)} job-payload prompt(s) were NOT compared "
            "against canon: without it a fired receipt cannot be told from pending work, and guessing "
            "that produced two rounds of false positives"))

    # R2/R4 judge what can still be sent. R3 asks whether a canon ever reached a
    # render at all, so it may look at every prompt ever written.
    live_prompts = variants + live_payloads
    all_prompts = variants + all_payloads

    findings += check_register_freshness(root, reg)
    findings += rule_resolved_but_open(root, reg, cards)
    findings += rule_prompt_contradicts_canon(root, reg, live_prompts, unrun_jobs(root, jobs, runs),
                                              all_prompts=all_prompts)
    findings += rule_canon_never_ran(root, reg, all_prompts, runs)
    findings += rule_attribute_unpinned(reg, live_prompts)
    findings += rule_bar_serves_two_beats(root, reg)
    findings += rule_unregistered_decisions(reg, cards, coverage_since)
    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--register", default=None)
    ap.add_argument("--coverage-since", default=None,
                    help="only report unregistered decisions resolved on/after this ISO date")
    ap.add_argument("--coverage", action="store_true",
                    help="list the resolved decisions no subject covers (they are always counted)")
    ap.add_argument("--quiet", action="store_true", help="FAIL lines only, no banner")
    a = ap.parse_args(argv)

    if yaml is None:
        print("check_canon_drift: pyyaml is not importable; abstaining rather than guessing")
        return 0

    findings = run(a.root, a.register, a.coverage_since)
    order = {FAIL: 0, ACK: 1, REVIEW: 2, UNKNOWN: 3}
    findings.sort(key=lambda f: (order[f.level], f.rule, f.where))
    counts = {lv: sum(1 for f in findings if f.level == lv) for lv in (FAIL, ACK, REVIEW, UNKNOWN)}

    uncovered = sum(1 for f in findings if f.rule == "unregistered_decision")
    if a.coverage and not a.quiet:
        print("REGISTER REACH — the resolved decisions below have NO subject, so no record was "
              "compared against them. They are not passes; they are the part of the inbox this "
              "check does not see.\n")
    for f in findings:
        if a.quiet and f.level != FAIL:
            continue
        if f.rule == "unregistered_decision" and not a.coverage:
            continue
        print(f.line())
    if not a.quiet:
        print()
        print(f"CANON-DRIFT: fail={counts[FAIL]} ack={counts[ACK]} "
              f"review={counts[REVIEW]} cannot-tell={counts[UNKNOWN]}")
        # THE REACH IS NOT A FOOTNOTE. `fail=0` on a register covering 1 of 75
        # resolved decisions is a statement about the register, not about the
        # repo, and printing the pass without the reach beside it is how a green
        # line starts meaning "nobody looked".
        if a.coverage_since:
            print(f"             REGISTER REACH: not computed — --coverage-since "
                  f"{a.coverage_since} hides every older decision, so the uncovered count "
                  "is a slice and a percentage of it would be a lie")
        else:
            resolved = len(_resolved_cards(a.root))
            covered = max(resolved - uncovered, 0)
            pct = (100.0 * covered / resolved) if resolved else 0.0
            print(f"             REGISTER REACH: {covered} of {resolved} resolved founder decisions "
                  f"are covered by a subject ({pct:.0f}%); {uncovered} are not"
                  + ("" if a.coverage else " — --coverage to list them"))
    return 1 if counts[FAIL] else 0


def _resolved_cards(root):
    p = Path(root) / "review" / "inbox.yaml"
    if not p.exists() or yaml is None:
        return []
    try:
        cards = yaml.safe_load(p.read_text(errors="replace"))
    except Exception:
        return []
    if not isinstance(cards, list):
        return []
    return [c for c in cards if isinstance(c, dict) and c.get("resolved")]


if __name__ == "__main__":
    sys.exit(main())
