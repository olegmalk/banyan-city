#!/usr/bin/env python3
"""Promote a chosen take into a node's canon `stills/` — WITH its record.

    python3 pipeline/promote_still.py sapling 001 14 \
        --take 14-worth-staying-in-r4-s3.png --address b14-r4-s3

THE STEP THIS REPLACES IS `cp`, AND THAT IS THE WHOLE BUG. Until today a canon
promotion was `cp takes/stills/<take>.png stills/<beat>-<slug>.png` and nothing
else, run by hand. The take's `.meta.yaml` stays behind in `takes/stills/`, so
the copy lands in canon carrying no provenance at all — and
`build_site.publishable()` reads an unprovenanced file as permitted
(build_site.py:535-536, deliberately: unprovenanced is the licence gate's
finding, not the build's). Promoting a frame is therefore the act that STRIPS
the record which would have refused it.

MEASURED, on a synthetic tree, 2026-08-10 — the four shapes a promotion can
land in, and only one of them is honest:

    promoted PNG, no sidecar          publishable=(True,  '')   gate: 0 findings
    sidecar with no `model:` key      publishable=(True,  '')   gate: 1 finding
    sidecar saying `model: see the take's sidecar`
                                      publishable=(True,  '')   gate: 1 finding
    sidecar naming the weights        publishable=(False, 'CreativeML Open
                                                           RAIL++-M')

The first row is what every promotion in this tree has done. Three of the four
publish silently, which is why this tool refuses all three by name rather than
trusting whoever runs it to write the fourth.

AND A FIFTH SHAPE, WHICH IS THIS TOOL'S OWN, found by measuring the first draft
of it rather than by reading it. When the take is a COMPOSITE — a frame drawn
from another frame, `model: wan` over `source_still_path: …/src-animagine.png` —
a sidecar naming only the take's own model reads:

    bare `cp`, no sidecar     asked directly   (True,  '')
                              asked as a frame (False, 'CreativeML Open RAIL++-M')
    sidecar naming only
      the take's own model    asked directly   (True,  '')
                              asked as a frame (True,  '')   ← LAUNDERED

Writing a PARTIAL record is strictly worse than writing none, and the mechanism
is `build_site.py:803`: `recorded_twin()` — the bytes-following recovery
4eb4c61 built — is consulted only when the promoted frame has NO sidecar. A
sidecar switches the recovery off and answers in its place, so it must answer
everything the take's record would have. That is why `carried()` below copies
the take's record forward key for key instead of restating one field, and why
`verify()` measures the two files against each other on every run rather than
trusting the key list to have stayed complete.

THE SAME MEASUREMENT CAUGHT THE FIELD SELECTION BACKWARDS. `model_value()` took
the first provenance key licence_gate could resolve; every sidecar in this
pipeline opens with `platform:`, and `local-gpu (rtx5090)` resolves to
`CC-BY-4.0 (our own output)`. On the real
`03-deploy-succeeded-fix-s0.png.meta.yaml` it returned the platform and dropped
`model: cagliostrolab/animagine-xl-3.1` — our own licence written over an
OpenRAIL++ frame, in the one file whose job is to say otherwise.

WHY A CONVENTION IN A README WAS NOT ENOUGH. `stills/README.md` has prescribed
the promotion sidecar since 2026-08-09 and every promotion since has skipped it,
because the convention is prose addressed to a person. This repo has already
written down what that costs, in `hold_still.sidecar()`'s own comment: "A label
that a person has to remember is a label that goes missing on the one run nobody
double-checks." The convention is now executable.

AND IT CLOSES THE HALF `4eb4c61` COULD NOT. That commit taught the read side to
chase a promoted frame's BYTES back to the take that still holds the record
(`build_site.recorded_twin()`), which answers for eight of the thirty frames in
`stills/`. It cannot answer when no copy of those bytes carries a record
anywhere — the take was cleaned up, the frame came from off-tree, or the
promotion moved instead of copied — and in that case `frame_publishable()`
counts the absence and returns `(True, "")` on purpose (build_site.py:833-837;
refusing there would have emptied the founder's review page over an absence).
Writing the record AT PROMOTION TIME is what stops that case from being created
in the first place, and it is the only place the information is still to hand.

WHAT THIS TOOL WILL NOT DECIDE. It never judges the picture and it never judges
the licence. `cagliostrolab/animagine-xl-3.1` drew every frame in this tree and
is CreativeML Open RAIL++-M, so an honest promotion sidecar REFUSES the frame it
documents and adds one line to the licence-debt count — that is D15, it is the
founder's, and this tool reports the number rather than pre-empting it. Nor does
it decide WHICH frame is canon: R4, taste is the author's, so `--address` is
required and is recorded verbatim as the thing he actually said.
"""

import argparse
import hashlib
import shutil
import sys
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))

import licence_gate as lg          # noqa: E402
import plate_prep                  # noqa: E402
from hold_still import slug_for    # noqa: E402


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def refuse(what: str, fix: str = "") -> "SystemExit":
    """Every refusal names the field or the file, never just the verdict.

    A gate that says "not allowed" sends whoever hit it to read the source; a
    gate that says WHICH key is missing sends them to the record. The second is
    the only kind that gets fixed on the spot, and every branch below owes one.
    """
    return SystemExit(f"✗ REFUSED: {what}" + (f"\n  → {fix}" if fix else ""))


# --------------------------------------------------------------- the record
# The provenance keys a take's sidecar may legitimately carry the model under.
# Asked in licence_gate's own vocabulary rather than a local list, so a key that
# the gate learns to read is a key this reads too — two spellings of "where the
# model is written down" drifting apart is how a record becomes invisible to one
# tool and visible to the other (licence_gate's own META_EXT reader bug, and the
# `<name>.png.meta.yaml` miss it caused in build_site.publishable, are both that
# shape).
def model_value(data: dict) -> tuple:
    """(key, value) naming the model in a take's record, or (None, None).

    ASKED IN TIER ORDER — weights, then engine, and NEVER the platform — and
    that order is the difference between this tool working and laundering. Until
    it was measured on 2026-08-10 this took the FIRST provenance key whose value
    licence_gate could resolve, on the reasoning that a resolvable value is the
    one that answers the question. Every sidecar this pipeline writes opens with
    `platform:`, and `local-gpu (rtx5090)` resolves — to `CC-BY-4.0 (our own
    output)`. So on the real tree:

        03-deploy-succeeded-fix-s0.png.meta.yaml
          platform: local-gpu (rtx5090)              ← picked, CC-BY-4.0
          model: cagliostrolab/animagine-xl-3.1      ← dropped, OpenRAIL++

    which would have written OUR OWN licence over every animagine frame
    promoted to canon and cleared it — the exact inversion this file's docstring
    promises it refuses. A resolvable platform is not evidence about the
    weights; it is evidence about the machine, so it is not consulted here at
    all: a record carrying only `platform:` names no model, and that is the
    second of the three silent shapes, owed the refusal and not a substitute.
    The platform still travels into the canon record — `carried()` keeps every
    provenance key — it just cannot stand in for the thing that drew the frame.

    WITHIN A TIER, a resolvable value wins, but a tier that is PRESENT decides
    even when nothing in it resolves. `model: some-new-checkpoint` must reach
    check_take_record's "matches nothing in MODEL_LICENCES" refusal naming
    `model:`, not fall through to something that happens to classify — falling
    through is how an unclassified checkpoint would buy itself our licence.
    """
    for tier in (lg.MODEL_KEYS, lg.ENGINE_KEYS):
        present = [(k, str(v).strip()) for k, v in data.items()
                   if k.lower() in tier and str(v).strip()]
        if not present:
            continue
        for key, text in present:
            if lg.model_licences(text):
                return key, text
        return present[0]
    return None, None


# ------------------------------------------------- what the canon copy inherits
# EVERY KEY build_site ASKS A FRAME, enumerated from its readers rather than
# invented here, because a promotion sidecar is only honest if it answers the
# same questions the take's record answers:
#
#   publishable()          routes the provenance keys through licence_gate
#   composite_publishable  walks `ingredients:`
#   source_frame() /       follows the three frame-reference dialects and the
#     record_still_claim   two path hints to the picture underneath
#
# THE COST OF RESTATING INSTEAD OF CARRYING, measured on a synthetic tree the
# same day. A take drawn from an animagine frame (`model: wan`,
# `source_still_path: …/src-animagine.png`) answers (False, OpenRAIL++). Promote
# it with a sidecar naming only its own model and the canon copy answers:
#
#     asked directly            (True, '')     — as it always did
#     asked as a source frame   (True, '')     ← LAUNDERED
#
# where the bare `cp` this tool replaces answered (False, OpenRAIL++) on the
# second line. That is not a smaller improvement, it is a REGRESSION, and the
# mechanism is build_site.py:803: recorded_twin() is consulted only when the
# promoted frame has NO sidecar. Writing a partial record is therefore strictly
# worse than writing none — it switches off the recovery path 4eb4c61 built and
# puts nothing in its place. A promotion sidecar must carry the whole question
# forward or it must not exist.
CLAIM_KEYS = {
    "init_still", "init_still_sha256", "init_still_path",
    "source_still", "source_still_sha256", "source_still_path",
    "init_frame",
    # render_b01r8's img2img dialect (render_b01r8.py:267-268). build_site
    # cannot read this one YET — record_still_claim knows three dialects and
    # this is a fourth — which is the reason to carry it and not a reason to
    # drop it: the day the gate learns the key, the canon records that were
    # written today already answer. Dropping it now would make that day a
    # backfill nobody knows they owe.
    "init_image", "init_sha256",
}
CARRY = ({k.lower() for k in lg.PROVENANCE_KEYS} | set(lg.LICENCE_KEYS)
         | {"model_licence", "model_license", "ingredients"} | CLAIM_KEYS)


def carried(data: dict) -> dict:
    """The take's record reduced to what the gate will ask the canon copy.

    An ALLOWLIST, so the prompt, the negative, the wall time and the render's
    own `approved: false` stay behind: they describe the take's making, not the
    canon frame's provenance, and `approved: false` sitting beside the
    `approved_by:` this tool writes would be one record answering one question
    twice. Everything the gate reads travels; nothing else does.
    """
    return {k: v for k, v in data.items()
            if k.lower() in CARRY and v is not None and str(v).strip() != ""}


def check_take_record(take: Path) -> tuple:
    """(key, value, record) for the model that drew this take — or refuse, saying which.

    THE THREE SILENT SHAPES, refused here in the order they were measured. Each
    one publishes today and each one gets its own sentence, because "this take
    has no usable record" would leave the operator guessing which of the three
    they are looking at.
    """
    side = lg.sidecar_for(take, lg.RECORD_SIDECAR_EXT)
    if side is None:
        raise refuse(
            f"{rel(take)} has no provenance record beside it — expected "
            f"{take.name}.meta.yaml",
            "a take with no record cannot be promoted: nothing in the tree says "
            "what drew it, and the copy would inherit that silence as permission. "
            "Write the render's sidecar first, or promote the take that has one.")
    try:
        data = yaml.safe_load(side.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        raise refuse(f"{rel(side)} is not readable yaml ({e.__class__.__name__})",
                     "an unparseable record is an absent record — fix it, then promote.")
    if not isinstance(data, dict):
        raise refuse(f"{rel(side)} does not parse to a mapping",
                     "the sidecar must be a yaml mapping with a `model:` key.")

    key, value = model_value(data)
    if key is None:
        raise refuse(
            f"{rel(side)} names no model — missing field: `model:`",
            "the promotion sidecar's whole job is to say what drew the frame. "
            "Add `model:` naming the weights to the take's record first.")

    # A POINTER IS THE ONE WAY TO GET THIS EXACTLY BACKWARDS, and it is worth its
    # own refusal because it LOOKS like diligence. `model: see the take's
    # sidecar` names no model, so lg.model_licences() returns nothing,
    # publishable() finds no licence question and CLEARS the frame — a sidecar
    # written to account for a frame would be the thing that launders it.
    # stills/README.md states the rule as "name the weights or write nothing";
    # this is that rule with teeth.
    norm = lg.normalise(value)
    if lg.POINTER.search(norm):
        raise refuse(
            f"{rel(side)} points instead of naming: `{key}: {value}`",
            "a pointer resolves to no model, so publishable() reads it as 'no "
            "licence question' and CLEARS the frame — the opposite of what the "
            "sidecar is for. Name the weights (stills/README.md).")
    if not lg.model_licences(value) and norm not in lg.SENTINELS:
        raise refuse(
            f"{rel(side)} names `{key}: {value}`, which matches nothing in "
            "licence_gate.MODEL_LICENCES",
            "an unclassified model is not a safe model. Add it to "
            "pipeline/licence_gate.py with the licence you actually read, then "
            "promote — otherwise the canon frame states terms nobody has read.")
    return key, value, data


def rel(p: Path) -> str:
    return plate_prep.posix(plate_prep.rel_to_repo(p))


# --------------------------------------------------------------------- main
def resolve_node(genome: str, node: str) -> Path:
    nodes = REPO / "genomes" / genome / "nodes"
    match = [x for x in sorted(nodes.iterdir())
             if x.is_dir() and x.name.startswith(node)]
    if not match:
        raise refuse(f"no node under {rel(nodes)} starting with {node!r}")
    if len(match) > 1:
        raise refuse(f"{node!r} matches {len(match)} nodes: "
                     f"{', '.join(m.name for m in match)}",
                     "give enough of the directory name to pick one.")
    return match[0]


def resolve_take(node_dir: Path, take: str) -> Path:
    """The take, named however the operator had it to hand."""
    p = Path(take)
    for cand in (p, REPO / p, node_dir / "takes" / "stills" / p.name):
        if cand.is_file():
            return cand.resolve()
    raise refuse(f"no such take: {take}",
                 f"looked in {rel(node_dir / 'takes' / 'stills')}/ and as a "
                 "path from the repo root.")


def canon_name(node_dir: Path, beat: int) -> str:
    slug = slug_for(node_dir, beat)
    if not slug:
        raise refuse(f"{node_dir.name}/shots.md has no beat {beat:02d}",
                     "the canon filename is derived from the beat's slug in "
                     "shots.md, so a beat that is not in the script cannot be "
                     "promoted to.")
    return f"{beat:02d}-{slug}.png"


def promote(node_dir: Path, beat: int, take: Path, address: str,
            approved_by: str, dry_run: bool) -> Path:
    stills = node_dir / "stills"
    dest = stills / canon_name(node_dir, beat)

    # NEVER OVERWRITE A CANON NAME. Revocations STACK in this tree: a refused
    # frame is `git mv`-ed to `NN-<slug>-REVOKED-<why>.png` and kept as the
    # record of what was refused (stills/README.md, R6). Clobbering the canon
    # name would destroy that record and would do it silently, since the bytes
    # are the only thing that distinguishes the two.
    if dest.exists():
        raise refuse(
            f"{rel(dest)} already exists",
            "a canon name is freed by recording the refusal, never by "
            "overwriting: `git mv` the current frame to "
            f"{dest.stem}-REVOKED-<why>.png first. Revocations stack; a "
            "-REVOKED- name is one refusal with its reason in it, not a slot.")

    key, value, record = check_take_record(take)
    take_sha = sha256(take)
    inherit = carried(record)

    if dry_run:
        print(f"  would copy  {rel(take)}\n"
              f"          →   {rel(dest)}\n"
              f"  would record {key}: {value}")
        for k in inherit:
            if k != key:
                print(f"  would carry  {k}: "
                      f"{str(inherit[k])[:60].splitlines()[0] if str(inherit[k]) else ''}")
        return dest

    stills.mkdir(parents=True, exist_ok=True)
    shutil.copy(take, dest)

    # A PROMOTION IS BYTE-FOR-BYTE OR IT IS NOT A PROMOTION. Every table in
    # stills/README.md records "copied: byte-for-byte", and the whole recovery
    # path 4eb4c61 built (recorded_twin follows BYTES, never names) is only
    # sound while that is true. Asserted rather than assumed, because a partial
    # copy would produce a canon frame whose record describes a different
    # picture — the exact failure the record exists to prevent.
    dest_sha = sha256(dest)
    if dest_sha != take_sha:
        dest.unlink(missing_ok=True)
        raise refuse(f"the copy does not match the take ({dest_sha[:12]}… != "
                     f"{take_sha[:12]}…) — nothing was promoted")
    # The take STAYS. recorded_twin() reaches a promoted frame's provenance by
    # finding the take still in the tree holding the same bytes, so moving it
    # would break the recovery path for every clip already drawn from it.
    if not take.is_file():
        raise refuse(f"{rel(take)} is gone after the copy — promotion COPIES, "
                     "it never moves")

    # FROM HERE THE PNG EXISTS AND ITS RECORD DOES NOT, which is the very state
    # this tool was written to make unreachable. Any failure below — an
    # unwritable sidecar, a dialect we failed to carry — takes the frame back
    # out with it, because a half-finished promotion left on disk is the bare
    # `cp` again, arrived at by a longer route.
    side = Path(str(dest) + ".meta.yaml")
    try:
        side.write_text(
            "# Canon promotion — provenance preserved (stills/README.md).\n"
            "# Written by pipeline/promote_still.py, never by hand: a promotion\n"
            "# that copies only the pixels strips the record that refuses them.\n"
            "#\n"
            "# The block below is the TAKE'S OWN record, carried forward key for\n"
            "# key — its model, its licence, and whatever frame or ingredients it\n"
            "# was made from. Carried and not restated: two sentences about one\n"
            "# picture are two chances to disagree, and a promotion sidecar that\n"
            "# answers fewer questions than the take's is worse than no sidecar\n"
            "# at all, because build_site only reaches for the take's record\n"
            "# (recorded_twin) while the canon copy has none.\n"
            + yaml.safe_dump(inherit, sort_keys=False, allow_unicode=True,
                             default_flow_style=False)
            + f"promoted_from: {rel(take)}\n"
              f"promoted_from_sha256: {take_sha}\n"
              f"sha256: {dest_sha}\n"
              f"promoted_on: {date.today().isoformat()}\n"
            # R4. Taste is the author's, so the record says whose pick this was
            # and in whose words — an address he typed, never a steward's
            # reading of it.
              f"approved_by: {approved_by}\n"
              f"his_address: {address}\n", encoding="utf-8")
        verify(dest, take, record)
    except BaseException:
        dest.unlink(missing_ok=True)
        side.unlink(missing_ok=True)
        raise
    return dest


def verify(dest: Path, take: Path, record: dict) -> None:
    """The canon copy must answer publishable() exactly as the take does.

    CARRY IS A LIST, AND A LIST GOES STALE. It was already stale when it was
    written — `init_image` is a fourth frame-reference dialect that
    record_still_claim does not know, and it was found by reading render_b01r8
    rather than by anything failing. The next dialect will arrive the same way
    and nobody will remember this file. So the guarantee is not "the list is
    complete"; the guarantee is measured here, on the two files, every run: if
    the copy is more publishable than the picture it was copied from, the
    promotion moved a licence question and the promotion does not happen.

    Only the permissive direction refuses. A canon copy that answers MORE
    strictly than its take has told no lie about the frame, and refusing it
    would be this tool making the licence call that D15 reserves to the founder.
    """
    import build_site as bs

    # still_dirs()/frame_dirs() cache on first use and `dest` is younger than
    # any of it — a stale cache would answer about a tree that predates the file
    # being judged, which is the one file the answer is about.
    bs._STILL_DIRS = []
    bs._FRAME_DIRS = []
    ok_take, why_take = bs.publishable(take)
    ok_dest, _why_dest = bs.publishable(dest)
    if ok_dest and not ok_take:
        side = lg.sidecar_for(dest, lg.RECORD_SIDECAR_EXT)
        written = yaml.safe_load(side.read_text(encoding="utf-8")) or {}
        dropped = sorted(set(record) - set(written))
        raise refuse(
            f"the promoted copy is MORE publishable than {rel(take)} — the take "
            f"answers ({ok_take}, {why_take!r}) and the copy answers "
            f"({ok_dest}, '') — missing field(s): "
            + (", ".join(f"`{k}:`" for k in dropped) or "none identified"),
            "the copy inherited fewer provenance keys than the take carries, so "
            "a licence question that the take answers has gone missing in the "
            "promotion. Nothing was written. Add the dropped key(s) to "
            "promote_still.CARRY (they are what build_site would have followed) "
            "and promote again.")


def report(dest: Path) -> None:
    """What the tree now says about the frame — measured, not predicted.

    Printed after every promotion because the two consequences land in different
    places: publishable() decides whether the frame reaches banyan.city, and the
    licence-debt count decides whether CI goes red. Both are consequences of
    telling the truth about the frame, and neither is this tool's to soften.
    """
    import build_site as bs

    ok, why = bs.publishable(dest)
    print(f"  publishable: {ok}" + (f" — {why}" if why else ""))

    errors, _advisories, _candidates = lg.scan_all(REPO)
    import lint_genome
    ceiling = lint_genome.LICENCE_DEBT
    print(f"  licence debt: {len(errors)} (ratchet {ceiling})")
    if len(errors) > ceiling:
        # FIXME(founder-owed, D15): an honest promotion sidecar names
        # cagliostrolab/animagine-xl-3.1 and so adds one CreativeML Open
        # RAIL++-M line to the debt. Fourteen canon frames would RE-report
        # liability `001-t3-d.yaml` already counts once, which is precisely what
        # licence_gate's ltx-video comment refuses to raise a ceiling for; eight
        # more are counted nowhere today. Whether the number should
        # de-duplicate, and whether the ratchet moves, is D15 and it is the
        # founder's call. Nothing here may raise LICENCE_DEBT to make CI pass —
        # lint_genome says so in as many words — and nothing here may drop the
        # sidecar to keep the count down, which is the hole this file closes.
        print("\n  ⚠ THE RATCHET IS NOW BREACHED, and the sidecar is not the\n"
              "    thing to delete. The frame's licence was always this; the\n"
              "    record is what made it countable. Raising LICENCE_DEBT is\n"
              "    explicitly forbidden (lint_genome.py). This is D15 and it is\n"
              "    the founder's to settle — report it, do not resolve it.")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("genome")
    ap.add_argument("node", help="node dir, or enough of its start to be unique")
    ap.add_argument("beat", type=int)
    ap.add_argument("--take", required=True,
                    help="the chosen frame: a filename in takes/stills/, or a path")
    # R4 IS WHY THIS IS REQUIRED AND HAS NO DEFAULT. A promotion is a taste act,
    # and taste belongs to the author. `--address` is the thing he actually
    # typed (`b14-r4-s3`), recorded verbatim so the record shows his pick rather
    # than a steward's reading of it. A tool that let this default would let a
    # steward promote on their own judgment and leave no trace that they had.
    ap.add_argument("--address", required=True,
                    help="the founder's own address for this frame, verbatim "
                         "(e.g. b14-r4-s3) — R4, recorded as given")
    ap.add_argument("--approved-by", default="founder")
    ap.add_argument("--dry-run", action="store_true",
                    help="run every check and print the plan, write nothing")
    a = ap.parse_args()

    node_dir = resolve_node(a.genome, a.node)
    take = resolve_take(node_dir, a.take)
    dest = promote(node_dir, a.beat, take, a.address, a.approved_by, a.dry_run)
    if a.dry_run:
        print("✓ dry run — nothing written")
        return 0
    print(f"✓ {rel(dest)}\n✓ {rel(dest)}.meta.yaml — provenance preserved")
    report(dest)
    print("next: git add the PNG AND its .meta.yaml together — a promotion "
          "committed without its record is the bug this tool exists to prevent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
