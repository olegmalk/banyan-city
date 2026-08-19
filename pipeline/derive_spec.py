#!/usr/bin/env python3
r"""ONE shared derivation tool for box job specs: an ALLOW-LIST, not a deny-list.

WHY THIS EXISTS, AND IT IS A MEASURED FAILURE AND NOT A TIDINESS ARGUMENT.

Every spec-clone in this tree so far was hand-rolled and filtered its parent with
a DENY-LIST of key names. `derive_b12_stillmotion_0819.py` used

    REFUSE = re.compile(r"verdict|pick|sweep|plate_ack", re.I)

and it leaked, twice, six keys the filter's names do not match:

  * `cut_preference` -- beat 01's, two generations old, with THIS job's id
    substituted through it by the retokeniser, so it reads as a fresh
    recommendation for a clip that did not exist when it was written;
  * `pre_registered_fail_modes_as_fired`, `fail_mode_I_DID_NOT_PRE_REGISTER`,
    `what_the_next_rung_should_be`, `the_duplicate_run` -- another take's scored
    results, arriving in a spec whose own render had not happened;
  * `derivation.seed`, reading the PARENT's seed while the payload and the
    sidecar read the child's. A provenance block that disagrees with the bytes.

The repair attempted at the time was to RENAME the leaked keys
(`..._INHERITED_FROM_THE_S20260819_PARENT_NOT_THIS_JOB`). Naming a leak is not
closing it, and the renaming itself propagated to two more specs. The census
over all 1003 specs in pipeline/jobs/ finds ~180 distinct top-level key names,
most of them one-off prose written by whoever judged that job -- `verdict`,
`outcome`, `filed_0817`, `caveats_not_scored`, `THE_FINDING_THAT_OUTLIVES_BOTH_CLIPS`,
`the_crf_ruling_is_SOUND_and_beat_14_was_never_one_of_its_cases`. No regex over
names can enumerate that set, because the set is open: A VERDICT CAN ARRIVE
UNDER ANY KEY NAME. The only closed set is the one a runner and its guards
actually read, and that set is short. So the filter is inverted here: a child
carries what is on ALLOW, and everything else -- named, unnamed, renamed --
stops at the boundary.

WHAT A CHILD MAY CARRY (ALLOW), and every entry is justified by a reader:

  box_enqueue.to_job() copies these into the job the runner executes:
      id task node beat runner priority needs_gpu max_attempts env steps
      artifacts payload   (+ stamp_id, which controls to_job's id stamping)
  the queue and the scheduler read these:
      after needs sample est_minutes
  the guards and the human read these:
      owner consumer why success script_authority script_line
      goblin_def goblin_def_source

FOUR OF THOSE ARE ON ALLOW BUT ARE NEVER INHERITED (`FRESH`): why, consumer,
success, owner. They are the four sentences that say what THIS job asks, who
eats the answer, what landing looks like and who is accountable -- the four a
clone gets wrong by construction. The caller supplies them or the derivation
refuses; and for why/consumer/success a byte-identical copy of the parent's is
refused too, because passing the parent's sentence through your own hand is
still inheritance.

FOUR KEYS REFUSE THE WHOLE DERIVATION rather than being dropped: gate, gate_ref,
drafts_ack, recipe_slot. Dropping a verdict is safe -- the child simply has no
verdict. Dropping a BLOCK is not: box_enqueue refuses any spec carrying gate or
gate_ref precisely so that clearing one is a human deleting a key, and a
derivation that silently launders a blocked parent into an unblocked child would
be a hole in that guard. plate_ack is merely dropped (never carried): losing it
fails SAFE -- the plate check fires and a human looks.

WHAT THE CALLER AUTHORS (`extra`): bar, pre_registered_fail_modes,
init_provenance, failure_predicted_in_advance and the rest of a spec's written
thought. These are not on ALLOW and cannot be inherited; they are written by the
caller for this job. Two guards on them: a key whose NAME is findings-shaped
(verdict/pick/outcome/licence/fired/...) is refused outright, and a value that is
byte-identical to the parent's value under the same name is reported as CARRIED
VERBATIM so the spec can say so out loud instead of implying it was re-derived.

WHAT IT ALSO DOES, because these are the three things that went wrong at the
same time as the leak:

  RETOKEN   every string in the child -- payload dict KEYS (Windows paths),
            step argv, artifacts, embedded python and JSON -- is passed through
            an ordered substitution list that always includes
            (parent id -> child id). Then the parent id is asserted ABSENT from
            the serialised child. `derive_b12_stillmotion_0819.py` retargeted a
            spec's steps and left its payload keys on the parent's directory:
            scripts written to one place and read from another.
  OVERRIDES every change is declared as data and ASSERTED to have matched at
            least one site. A substitution that silently matched nothing is how
            a "one variable" rung becomes a re-run of its parent under a new
            name.
  SEEDS     `seed=N` patches the seed inside every jobs-render.json payload AND
            every `--seed` argv, then RE-PARSES the patched JSON and asserts
            each entry reads N. The b12 spec whose `derivation.seed` disagreed
            with its own payload is the reason this is a round-trip and not a
            regex.

Override vocabulary (a dict; every key is asserted to have matched):

    "seed": 20260871            -- jobs-render.json entries + --seed argv
    "argv:--strength": "0.26"   -- the value after that flag, every step
    "payload:<basename>": text  -- replace one payload file's contents (exactly
                                   one payload key must end with <basename>)
    "key:est_minutes": 8        -- set an ALLOW-listed top-level key

Usage as a library (the intended use -- one per-rung script per rung, tiny):

    import derive_spec
    child = derive_spec.derive(
        src="pipeline/jobs/parent.yaml", new_id="ep2-b12-noscav-0819",
        fresh={"why": ..., "consumer": ..., "success": ..., "owner": ...},
        overrides={"payload:b12-motion-prompt.txt": PROMPT},
        retoken=[("12-related-LTX-stillmotion-crf10", "12-related-LTX-noscav-crf10")],
        extra={"bar": {...}})
    derive_spec.write(child, "pipeline/jobs/ep2-b12-noscav-0819.yaml")

Selftest:  python3 pipeline/derive_spec.py --selftest
$0. No model, no network, no GPU.
"""

from __future__ import annotations

import copy
import json
import os
import re
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --------------------------------------------------------------------------
# The allow-list. Order here is the order keys are written to the YAML, so a
# derived spec reads top-to-bottom the way a hand-written one does.
ALLOW = (
    "id", "task", "node", "beat", "runner", "priority", "needs_gpu",
    "max_attempts", "sample", "stamp_id", "after", "owner", "consumer",
    "success", "why", "est_minutes", "needs", "env", "payload", "steps",
    "artifacts", "script_authority", "script_line", "goblin_def",
    "goblin_def_source",
)

# On ALLOW, but never inherited -- the caller supplies them or this refuses.
FRESH = ("why", "consumer", "success", "owner")
# Of those, the three whose verbatim re-use is itself the defect.
FRESH_MUST_DIFFER = ("why", "consumer", "success")

# A parent carrying one of these refuses the derivation outright: these are
# BLOCKS, and a derivation that drops a block is a laundering path.
REFUSE_PARENT = ("gate", "gate_ref", "drafts_ack", "recipe_slot")

# Key names that may never be authored via `extra` either -- findings shaped.
FINDINGS_NAME = re.compile(
    r"verdict|pick|outcome|sweep|licen[cs]|fired|caveat|plate_ack|derivation|"
    r"settl|filed_|repick|finding|what_this|prior_verdict|cut_preference",
    re.I)

# Where a spec is allowed to keep an already-scored life: refuse to overwrite.
SCORED_NAME = re.compile(r"verdict|outcome|pick|sweep|filed_|fired", re.I)


class DeriveError(RuntimeError):
    """Raised for every refusal. Callers are scripts; a traceback is fine."""


# --------------------------------------------------------------------------
def _walk(value, fn):
    """Apply fn to every string in a nested structure, dict KEYS included."""
    if isinstance(value, str):
        return fn(value)
    if isinstance(value, list):
        return [_walk(v, fn) for v in value]
    if isinstance(value, tuple):
        return tuple(_walk(v, fn) for v in value)
    if isinstance(value, dict):
        return {_walk(k, fn): _walk(v, fn) for k, v in value.items()}
    return value


def _dump(value) -> str:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=False,
                          default_flow_style=False, width=100)


def load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    if not isinstance(spec, dict):
        raise DeriveError("!! %s is not a mapping" % path)
    return spec


# --------------------------------------------------------------------------
def _apply_seed(child: dict, seed) -> list:
    """Patch the seed in jobs-render.json payloads and in --seed argv.

    Round-trips the JSON: the value is asserted by re-parsing the patched text,
    not by trusting that a regex fired. The b12 spec whose derivation.seed read
    one number while its payload read another is what this is for.
    """
    seed = int(seed)
    sites = []
    for key, val in (child.get("payload") or {}).items():
        if not isinstance(val, str) or '"seed"' not in val:
            continue
        try:
            before = json.loads(val)
        except ValueError:
            continue
        patched = re.sub(r'"seed"\s*:\s*\d+', '"seed": %d' % seed, val)
        after = json.loads(patched)          # refuses to write invalid JSON
        found = [e for e in (after if isinstance(after, list) else [after])
                 if isinstance(e, dict) and "seed" in e]
        if not found:
            continue
        bad = [e["seed"] for e in found if int(e["seed"]) != seed]
        if bad:
            raise DeriveError("!! seed patch did not take in %s: still %s"
                              % (key, bad))
        child["payload"][key] = patched
        old = sorted({int(e["seed"]) for e in
                      (before if isinstance(before, list) else [before])
                      if isinstance(e, dict) and "seed" in e})
        sites.append("payload %s (%s -> %d, re-parsed)"
                     % (os.path.basename(key.replace("\\", "/")),
                        ",".join(str(o) for o in old), seed))
    for step in child.get("steps") or []:
        argv = [str(a) for a in (step.get("argv") or [])]
        for i, tok in enumerate(argv):
            if tok == "--seed" and i + 1 < len(argv):
                sites.append("step %s --seed (%s -> %d)"
                             % (step.get("name"), argv[i + 1], seed))
                argv[i + 1] = str(seed)
        step["argv"] = argv
    return sites


def _apply_argv(child: dict, flag: str, value) -> list:
    sites = []
    for step in child.get("steps") or []:
        argv = [str(a) for a in (step.get("argv") or [])]
        for i, tok in enumerate(argv):
            if tok == flag and i + 1 < len(argv):
                sites.append("step %s %s (%s -> %s)"
                             % (step.get("name"), flag, argv[i + 1], value))
                argv[i + 1] = str(value)
        step["argv"] = argv
    return sites


def _apply_payload(child: dict, basename: str, text: str) -> list:
    keys = [k for k in (child.get("payload") or {})
            if k.replace("\\", "/").rsplit("/", 1)[-1] == basename]
    if len(keys) != 1:
        raise DeriveError("!! payload override %r matched %d payload keys "
                          "(want exactly 1): %s"
                          % (basename, len(keys), ", ".join(sorted(keys)) or "-"))
    old = child["payload"][keys[0]]
    child["payload"][keys[0]] = text
    if old == text:
        raise DeriveError("!! payload override %r is byte-identical to the "
                          "parent's -- that is not an override." % basename)
    return ["payload %s (%d -> %d chars)" % (basename, len(old), len(text))]


# --------------------------------------------------------------------------
def derive(src: str, new_id: str, fresh: dict, overrides: dict = None,
           retoken=None, extra: dict = None, by: str = None) -> dict:
    """Derive a child spec from `src`, carrying ONLY ALLOW-listed structure."""
    src_path = src if os.path.isabs(src) else os.path.join(REPO, src)
    parent = load(src_path)
    parent_id = parent.get("id")
    if not parent_id:
        raise DeriveError("!! parent %s has no id" % src)
    if not new_id or new_id == parent_id:
        raise DeriveError("!! new_id must be given and must differ from %r"
                          % parent_id)

    blocked = [k for k in REFUSE_PARENT if parent.get(k)]
    if blocked:
        raise DeriveError(
            "!! parent %s carries %s -- a BLOCK, not a verdict. Deriving off it "
            "would launder the block away. Clear it on the parent (a human "
            "deleting a key) or file the child by hand and say why."
            % (os.path.basename(src_path), ", ".join(blocked)))

    # ---- the allow-list is the whole filter.
    carried, dropped = [], []
    child = {}
    for key in ALLOW:
        if key in FRESH or key not in parent:
            continue
        child[key] = copy.deepcopy(parent[key])
        carried.append(key)
    for key in sorted(parent):
        if key not in ALLOW:
            dropped.append(key)

    # ---- the four sentences the caller owns.
    fresh = dict(fresh or {})
    missing = [k for k in FRESH if not str(fresh.get(k) or "").strip()]
    if missing:
        raise DeriveError(
            "!! %s must be supplied fresh by the caller and %s %s missing. A "
            "clone inherits the parent's question, and the parent's question is "
            "answered." % ("/".join(FRESH), ", ".join(missing),
                           "is" if len(missing) == 1 else "are"))
    for key in FRESH_MUST_DIFFER:
        if str(fresh[key]).strip() == str(parent.get(key) or "").strip():
            raise DeriveError(
                "!! fresh[%r] is byte-identical to the parent's -- passing the "
                "parent's sentence through your own hand is still inheritance."
                % key)
    unknown = [k for k in fresh if k not in FRESH]
    if unknown:
        raise DeriveError("!! fresh carries non-fresh keys %s -- use overrides "
                          "(key:<name>) or extra" % ", ".join(sorted(unknown)))
    child.update(fresh)

    # ---- ids first, so retokening sees the new one nowhere and the old one
    # ---- everywhere it still hides.
    child["id"] = new_id
    child["task"] = new_id

    # ---- retoken: ordered, longest-first inside each caller pair is the
    # ---- caller's business; the id pair always runs last so a more specific
    # ---- filename rule gets first refusal on the same substring.
    pairs = [tuple(p) for p in (retoken or [])] + [(parent_id, new_id)]
    for old, new in pairs:
        if not old:
            raise DeriveError("!! empty retoken source")
    def _sub(text: str) -> str:
        for old, new in pairs:
            text = text.replace(old, new)
        return text
    child = _walk(child, _sub)

    blob = _dump(child)
    if parent_id in blob:
        stuck = [ln.strip() for ln in blob.splitlines() if parent_id in ln]
        raise DeriveError("!! the parent id %r survives retokening in %d line(s): "
                          "%s" % (parent_id, len(stuck), stuck[0][:160]))

    # ---- overrides, each asserted to have matched something.
    applied = {}
    for spec_key, value in sorted((overrides or {}).items()):
        if spec_key == "seed":
            sites = _apply_seed(child, value)
        elif spec_key.startswith("argv:"):
            sites = _apply_argv(child, spec_key[5:], value)
        elif spec_key.startswith("payload:"):
            sites = _apply_payload(child, spec_key[8:], value)
        elif spec_key.startswith("key:"):
            name = spec_key[4:]
            if name not in ALLOW:
                raise DeriveError("!! key override %r is not on the allow-list"
                                  % name)
            if name in ("id", "task"):
                raise DeriveError("!! id/task come from new_id, not an override")
            child[name] = value
            sites = ["key %s = %r" % (name, value)]
        else:
            raise DeriveError(
                "!! unknown override %r. Vocabulary: seed, argv:<flag>, "
                "payload:<basename>, key:<allow-listed name>." % spec_key)
        if not sites:
            raise DeriveError(
                "!! override %r matched NOTHING. A substitution that silently "
                "matched nothing is how a 'one variable' rung becomes a re-run "
                "of its parent under a new name." % spec_key)
        applied[spec_key] = sites

    # ---- what the caller authored for this job.
    verbatim = []
    for key in sorted(extra or {}):
        if key in ALLOW:
            raise DeriveError("!! %r is on the allow-list -- pass it as "
                              "key:%s in overrides, not as extra" % (key, key))
        if FINDINGS_NAME.search(key):
            raise DeriveError(
                "!! extra[%r] is findings-shaped. A spec earns those AFTER its "
                "pixels exist; authoring one now is pre-writing a verdict." % key)
        child[key] = copy.deepcopy(extra[key])
        if key in parent and _dump(parent[key]) == _dump(extra[key]):
            verbatim.append(key)

    # ---- the provenance block, written here and never inherited.
    derivation = {
        "parent": os.path.relpath(src_path, REPO).replace("\\", "/"),
        "by": by or "pipeline/derive_spec.py",
        "method": ("ALLOW-LIST, not a deny-list. Only the keys pipeline/derive_spec.py "
                   "names as structural cross from the parent; every other key -- "
                   "verdicts, picks, sweeps, fired fail-modes, cut preferences, "
                   "notes, however named or renamed -- stops at the boundary by "
                   "construction. A verdict can arrive under any key name, so the "
                   "closed set is what a runner and its guards read, not what a "
                   "regex can enumerate."),
        "carried_structural_keys": sorted(carried),
        "authored_fresh_by_the_caller": sorted(list(fresh) + list(extra or {})),
        "keys_the_parent_had_that_did_NOT_cross": sorted(dropped) or "none",
        "retokened": ["%s -> %s" % (o, n) for o, n in pairs],
        "overrides_applied_and_asserted": applied or "none",
    }
    if verbatim:
        derivation["carried_verbatim_by_the_callers_own_hand"] = (
            "%s -- authored as `extra` but byte-identical to the parent's value "
            "under the same name. Recorded rather than implied: a pre-registered "
            "bar carried unchanged is legitimate, and it should say so."
            % ", ".join(verbatim))
    if "seed" in applied:
        derivation["seed"] = int(overrides["seed"])
    child["derivation"] = derivation

    stray = [k for k in child if k not in ALLOW and k != "derivation"
             and k not in (extra or {})]
    if stray:
        raise DeriveError("!! child grew keys nobody authored: %s"
                          % ", ".join(sorted(stray)))
    return child


# --------------------------------------------------------------------------
def write(child: dict, out: str, force: bool = False) -> str:
    out_path = out if os.path.isabs(out) else os.path.join(REPO, out)
    if os.path.isfile(out_path) and not force:
        existing = load(out_path)
        scored = sorted(k for k in existing if SCORED_NAME.search(k))
        if scored:
            raise DeriveError(
                "!! %s already carries %s -- refusing to overwrite a SCORED "
                "spec. Pass force=True if that is genuinely what you want."
                % (os.path.relpath(out_path, REPO), ", ".join(scored)))
    ordered = {k: child[k] for k in ALLOW if k in child}
    ordered.update({k: v for k, v in child.items() if k not in ordered})
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(ordered, fh, sort_keys=False, width=100,
                       default_flow_style=False, allow_unicode=False)
    return out_path


# --------------------------------------------------------------------------
# Selftest. Asserts, not prints -- a selftest that only prints is a demo.
_PARENT_FIXTURE = {
    "id": "ep2-bxx-parent-0819",
    "task": "ep2-bxx-parent-0819",
    "node": "002b-first-citizen",
    "beat": 12,
    "runner": "box",
    "priority": 30,
    "needs_gpu": True,
    "max_attempts": 1,
    "sample": True,
    "est_minutes": 8,
    "needs": ["cuda", "vram20"],
    "env": {"PYTHONUTF8": "1"},
    "owner": "some other lane",
    "consumer": "the parent's consumer",
    "success": "the parent's success",
    "why": "the parent's why",
    "script_authority": "Node 002b-first-citizen, approved_by: founder.",
    "payload": {
        r"C:\banyan-farm\ep2-bxx-parent-0819\prompt.txt": "a leaf, and a scavenger behind it",
        r"C:\banyan-farm\ep2-bxx-parent-0819\jobs-render.json":
            '[\n {\n  "beat": 12,\n  "seed": 20260819,\n  "out": '
            '"C:\\\\banyan-farm\\\\ep2-bxx-parent-0819-out\\\\12-parentclip.mp4"\n }\n]',
    },
    "steps": [
        {"name": "render",
         "argv": ["py", r"C:\banyan-farm\ep2-bxx-parent-0819\go.py",
                  "--seed", "20260819", "--strength", "0.30",
                  "--out", r"C:\banyan-farm\ep2-bxx-parent-0819-out\12-parentclip.mp4"]},
    ],
    "artifacts": [r"C:\banyan-farm\ep2-bxx-parent-0819-out\12-parentclip.mp4"],
    # ---- everything below is what must NOT cross, in the shapes it really
    # ---- arrived in on 2026-08-19.
    "verdict_this_job": "PASS-HOLD",
    "verdict_this_job_measured": {"whole_frame": "f000 125.68"},
    "cut_preference": "CUT-PREFERRED: ep2-bxx-parent-0819. It clears the bar.",
    "cut_preference_INHERITED_FROM_THE_B01_GRANDPARENT_NOT_THIS_JOB": "renamed, still a leak",
    "pre_registered_fail_modes_as_fired": {"FAIL-DEAD": "FIRED"},
    "fail_mode_I_DID_NOT_PRE_REGISTER": "DUSK COLLAPSE",
    "the_duplicate_run": "ran twice",
    "what_the_next_rung_should_be": "a shorter frame count",
    "THE_FINDING_THAT_OUTLIVES_BOTH_CLIPS": "prose nobody can regex for",
    "plate_ack": "the plate was looked at on 2026-08-13",
    "bar": {"the_number_that_decides": "|drift| >= 20"},
    "pre_registered_fail_modes": {"FAIL-DEAD": "no movement"},
}

_FRESH_OK = {
    "why": "a child's why",
    "consumer": "a child's consumer",
    "success": "a child's success",
    "owner": "the selftest",
}


def _raises(fn, needle):
    try:
        fn()
    except DeriveError as exc:
        assert needle in str(exc), "wrong refusal: %s (want %r)" % (exc, needle)
        return str(exc)
    raise AssertionError("expected a DeriveError containing %r" % needle)


def selftest() -> int:
    import tempfile
    tmp = tempfile.mkdtemp(prefix="derive-spec-selftest-")
    src = os.path.join(tmp, "parent.yaml")
    with open(src, "w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(_PARENT_FIXTURE, fh, sort_keys=False, allow_unicode=False)

    def go(**kw):
        kw.setdefault("fresh", _FRESH_OK)
        return derive(src, kw.pop("new_id", "ep2-bxx-child-0819"), **kw)

    # 1. the allow-list holds: not one findings key crosses, renamed or not.
    child = go(overrides={"seed": 20260871})
    leaked = [k for k in child if k not in ALLOW and k != "derivation"]
    assert leaked == [], "leaked: %s" % leaked
    for key in ("verdict_this_job", "cut_preference", "plate_ack", "bar",
                "cut_preference_INHERITED_FROM_THE_B01_GRANDPARENT_NOT_THIS_JOB",
                "pre_registered_fail_modes_as_fired", "the_duplicate_run",
                "THE_FINDING_THAT_OUTLIVES_BOTH_CLIPS"):
        assert key not in child, "%s crossed" % key
    blob = _dump(child)
    for corpse in ("PASS-HOLD", "CUT-PREFERRED", "DUSK COLLAPSE",
                   "prose nobody can regex for", "ran twice"):
        assert corpse not in blob, "%r survived in the child's text" % corpse
    assert child["derivation"]["keys_the_parent_had_that_did_NOT_cross"].count(
        "cut_preference") == 1
    assert "THE_FINDING_THAT_OUTLIVES_BOTH_CLIPS" in \
        child["derivation"]["keys_the_parent_had_that_did_NOT_cross"]

    # 2. structure DID cross.
    for key in ("node", "beat", "runner", "priority", "needs_gpu", "env",
                "needs", "payload", "steps", "artifacts", "script_authority"):
        assert key in child, "%s did not cross" % key
    assert child["beat"] == 12 and child["needs"] == ["cuda", "vram20"]

    # 3. the seed patch took, and it took in the JSON as PARSED not as matched.
    rj = [v for k, v in child["payload"].items() if k.endswith("jobs-render.json")][0]
    assert json.loads(rj)[0]["seed"] == 20260871, "seed not patched in json"
    argv = child["steps"][0]["argv"]
    assert argv[argv.index("--seed") + 1] == "20260871", "--seed not patched"
    assert child["derivation"]["seed"] == 20260871
    assert "re-parsed" in " ".join(
        child["derivation"]["overrides_applied_and_asserted"]["seed"])

    # 4. ids are retokened through every path, key and embedded blob. Measured
    #    on the job body only: `derivation` NAMES the parent on purpose, and a
    #    check that could not tell those apart would forbid provenance.
    body = _dump({k: v for k, v in child.items() if k != "derivation"})
    assert "ep2-bxx-parent-0819" not in body
    assert any("ep2-bxx-child-0819" in k for k in child["payload"])
    assert child["artifacts"][0] == \
        r"C:\banyan-farm\ep2-bxx-child-0819-out\12-parentclip.mp4"
    assert "ep2-bxx-parent-0819" in child["derivation"]["retokened"][0]

    # 5. an extra retoken reaches a published filename (the duplicate-filename
    #    trap: three distinct takes publishing one basename).
    child2 = go(retoken=[("12-parentclip", "12-childclip")])
    assert "12-parentclip" not in _dump(
        {k: v for k, v in child2.items() if k != "derivation"})
    assert child2["artifacts"][0].endswith("12-childclip.mp4")

    # 6. fresh is mandatory, and a copy of the parent's is not fresh.
    _raises(lambda: go(fresh={"why": "x", "consumer": "y", "success": "z"}),
            "owner")
    _raises(lambda: go(fresh=dict(_FRESH_OK, why="the parent's why")),
            "byte-identical to the parent's")
    _raises(lambda: go(fresh=dict(_FRESH_OK, beat=13)), "non-fresh keys")

    # 7. every override must match something.
    _raises(lambda: go(overrides={"argv:--nosuchflag": "1"}), "matched NOTHING")
    _raises(lambda: go(overrides={"payload:nope.txt": "x"}), "matched 0 payload keys")
    _raises(lambda: go(overrides={"nonsense": 1}), "unknown override")
    _raises(lambda: go(overrides={"key:verdict": "PASS"}), "not on the allow-list")
    ch = go(overrides={"argv:--strength": "0.26",
                       "payload:prompt.txt": "a leaf, and nothing behind it",
                       "key:est_minutes": 5})
    a = ch["steps"][0]["argv"]
    assert a[a.index("--strength") + 1] == "0.26" and ch["est_minutes"] == 5
    assert "scavenger" not in _dump(ch)
    _raises(lambda: go(overrides={"payload:prompt.txt":
                                  "a leaf, and a scavenger behind it"}),
            "byte-identical")

    # 8. `extra` is authored, never laundered.
    _raises(lambda: go(extra={"verdict_0819": "PASS"}), "findings-shaped")
    _raises(lambda: go(extra={"beat": 13}), "on the allow-list")
    ch = go(extra={"bar": _PARENT_FIXTURE["bar"], "init_provenance": "sha ..."})
    assert ch["bar"] == _PARENT_FIXTURE["bar"]
    assert "bar" in ch["derivation"]["carried_verbatim_by_the_callers_own_hand"]
    assert "init_provenance" not in \
        ch["derivation"]["carried_verbatim_by_the_callers_own_hand"]

    # 9. a BLOCK refuses the whole derivation instead of being dropped.
    for block in REFUSE_PARENT:
        blocked_src = os.path.join(tmp, "blocked-%s.yaml" % block)
        with open(blocked_src, "w", encoding="utf-8", newline="\n") as fh:
            yaml.safe_dump(dict(_PARENT_FIXTURE, **{block: "held"}), fh,
                           sort_keys=False, allow_unicode=False)
        _raises(lambda s=blocked_src: derive(s, "ep2-bxx-child-0819", _FRESH_OK),
                "a BLOCK, not a verdict")

    # 10. id hygiene.
    _raises(lambda: go(new_id="ep2-bxx-parent-0819"), "must differ")

    # 11. write() refuses to clobber a spec that has been scored.
    out = os.path.join(tmp, "out.yaml")
    write(child, out)
    assert yaml.safe_load(open(out, encoding="utf-8"))["id"] == "ep2-bxx-child-0819"
    write(child, out)                       # unscored -> overwrite is fine
    scored = yaml.safe_load(open(out, encoding="utf-8"))
    scored["verdict_0819"] = "PASS"
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(scored, fh, sort_keys=False, allow_unicode=False)
    _raises(lambda: write(child, out), "refusing to overwrite a SCORED spec")
    write(child, out, force=True)

    # 12. the written file round-trips through yaml and keeps ALLOW order.
    back = load(out)
    assert list(back)[:4] == ["id", "task", "node", "beat"], list(back)[:4]
    assert back["payload"] and back["steps"] and back["artifacts"]

    print("derive_spec selftest: 12 groups, all asserts passed. rc=0")
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    print(__doc__)
    print("nothing to do -- this is a library. --selftest runs the asserts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
