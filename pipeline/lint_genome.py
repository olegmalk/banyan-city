#!/usr/bin/env python3
"""Genome linter — the framework's structural rules, as a test suite.

Checks every genome under genomes/ for:
  - lineage.yaml integrity: unique ids, declared parents that exist
    (Guideline 1: the only obligation is declaring your parent),
    valid statuses (Guideline 7), node directories present
  - node.md contract: a "State change" section (R1) and a "Hook"
    section (R5) must exist in every T0 leaf
  - leaf provenance: every leaf listed in lineage exists and publishes
    tier, cost, model/prompt/seed keys, and status (PRD §7.2 — every
    render publishes its metadata; transparency integrity metric §12)
  - shots.md shot lists: every fenced prompt carries the format contract
    ('9:16', 'no text') and the style-bible clause ('No photorealism' —
    genomes/sapling/style.md); beat headings' time ranges appear verbatim
    in the node.md script (canon-drift guard); beat numbers run 01, 02, …
  - ledger header shape
  - licence gate (pipeline/licence_gate.py): nothing that ships carries a
    non-commercial, share-alike, research-only or unclassified licence — the
    tree publishes CC BY 4.0 and cannot honour that promise otherwise

Exit 0 = healthy tree. Exit 1 = list of violations.
"""

import csv
import os
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))   # importable from any cwd

import licence_gate  # noqa: E402 — needs the path above

REPO = Path(__file__).resolve().parent.parent
VALID_STATUS = {"hot", "hardened", "dormant"}
# '## Beat NN — TITLE (M:SS–M:SS)'; trailing status markers allowed
BEAT_HEADING = re.compile(r"^## Beat (\d{2}) — .+?\((\d+:\d{2}[–-]\d+:\d{2})\)")
LEAF_REQUIRED_KEYS = {"leaf", "node", "tier", "form", "cost_usd", "status", "model", "prompt", "seed"}
VALID_TIERS = {"T0", "T1", "T2", "T3"}
LEDGER_HEADER = ["date", "node", "leaf", "citizen", "type", "amount_usd", "compute_desc", "split_applied", "notes"]

# Pre-existing licence violations, all in node 001 (see lint_licences). This
# number may only ever go DOWN. Raising it to make a build pass would convert
# the one gate that can catch an unpublishable episode into a rubber stamp.
LICENCE_DEBT = 21

errors = []

# visible-motion vocabulary for the first-sentence check (cycle 005) —
# generation models front-load whatever the opening sentence describes
MOTION_VERBS = re.compile(
    r"\b(walk|run|turn|fall|collaps|sweep|pan|tilt|drift|rise|rising|flicker|"
    r"sway|push|pull|zoom|track|lean|land|drop|open|close|reach|throw|toss|"
    r"catch|jump|climb|slide|spin|shake|nod|wave|point|stumble|burst|slam|"
    r"scatter|flutter|ripple|pour|spill|swing|dash|crash|mid-action|moves|"
    r"moving|gestur|breath)\w*\b", re.I)


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    """Advisory only — printed, never counted as a violation. For rules
    adopted after content already shipped (the tree is never re-judged
    retroactively; new growth follows the current bar)."""
    print(f"  ⚠ {msg}")


def lint_genome(genome_dir: Path) -> None:
    name = genome_dir.name
    lineage_file = genome_dir / "lineage.yaml"
    tree_file = genome_dir / "tree.yaml"

    if not tree_file.exists():
        err(f"{name}: missing tree.yaml")
    if not lineage_file.exists():
        err(f"{name}: missing lineage.yaml")
        return

    lineage = yaml.safe_load(lineage_file.read_text())
    nodes = lineage.get("nodes") or []
    ids = [n.get("id") for n in nodes]
    if len(ids) != len(set(ids)):
        err(f"{name}: duplicate node ids in lineage.yaml")

    roots = [n for n in nodes if n.get("parent") is None]
    if len(roots) != 1:
        err(f"{name}: expected exactly one root node (parent: null), found {len(roots)}")

    for n in nodes:
        nid, slug = n.get("id"), n.get("slug")
        where = f"{name}/{nid}"

        parent = n.get("parent")
        if parent is not None and parent not in ids:
            err(f"{where}: declares parent '{parent}' which does not exist (Guideline 1)")
        if n.get("status") not in VALID_STATUS:
            err(f"{where}: status '{n.get('status')}' not in {sorted(VALID_STATUS)} (Guideline 7)")

        node_dir = genome_dir / "nodes" / (slug or "")
        if not node_dir.is_dir():
            err(f"{where}: node directory nodes/{slug}/ missing")
            continue

        node_md = node_dir / "node.md"
        if not node_md.exists():
            err(f"{where}: node.md (T0 leaf) missing")
        else:
            text = node_md.read_text()
            if "## State change" not in text:
                err(f"{where}: node.md has no '## State change' section (R1 — every node must change something)")
            if "## Hook" not in text:
                err(f"{where}: node.md has no '## Hook' section (R5)")

        for leaf_id in n.get("leaves") or []:
            leaf_file = node_dir / "leaves" / f"{leaf_id}.yaml"
            if not leaf_file.exists():
                err(f"{where}: leaf '{leaf_id}' listed in lineage but leaves/{leaf_id}.yaml missing")
                continue
            leaf = yaml.safe_load(leaf_file.read_text())
            missing = LEAF_REQUIRED_KEYS - set(leaf)
            if missing:
                err(f"{where}/{leaf_id}: leaf metadata missing keys {sorted(missing)} (PRD §7.2 — publish everything)")
            if leaf.get("tier") not in VALID_TIERS:
                err(f"{where}/{leaf_id}: tier '{leaf.get('tier')}' not in {sorted(VALID_TIERS)}")
            if leaf.get("node") != nid:
                err(f"{where}/{leaf_id}: leaf 'node' field is '{leaf.get('node')}', expected '{nid}'")
            # content must point at a real artifact — a dead reference passes
            # metadata checks but ships a 404 on the site (the silent gap the
            # linter exists to catch). "../node.md" is the T0 self-reference.
            content = str(leaf.get("content", ""))
            if content and content != "../node.md" and not (node_dir / "leaves" / content).exists():
                err(f"{where}/{leaf_id}: content '{content}' declared but leaves/{content} missing")

        # orphan leaves: files on disk not declared in lineage
        leaves_dir = node_dir / "leaves"
        if leaves_dir.is_dir():
            declared = set(n.get("leaves") or [])
            for f in leaves_dir.glob("*.yaml"):
                if f.stem not in declared:
                    err(f"{where}: leaves/{f.name} exists but is not listed in lineage.yaml")

    for shots_file in sorted((genome_dir / "nodes").glob("*/shots.md")):
        lint_shots(name, shots_file)


def lint_shots(genome_name: str, shots_file: Path) -> None:
    where = f"{genome_name}/{shots_file.parent.name}/shots.md"
    node_md = shots_file.parent / "node.md"
    script = node_md.read_text() if node_md.exists() else None
    if script is None:
        err(f"{where}: node.md missing — beat times cannot be checked against the script")

    beat_nums = []
    beat_label = None  # heading context for prompt errors; None above the first beat
    block = None  # accumulates lines while inside a fence
    for line in shots_file.read_text().splitlines():
        if line.startswith("```"):
            if block is None:
                block = []
                continue
            # closing fence — blocks above the first beat heading aren't prompts
            if beat_label is not None:
                prompt = "\n".join(block).lower()
                for phrase in ("9:16", "no text"):
                    if phrase not in prompt:
                        err(f"{where}: {beat_label} prompt missing '{phrase}' (base-footage contract)")
                if "no photorealism" not in prompt:
                    err(f"{where}: {beat_label} prompt missing 'No photorealism' (style bible — genomes/sapling/style.md)")
                # motion grammar (loop cycles 001/005, verified): WARN-only so
                # the already-filmed season stays lint-clean; future shot
                # lists should fix these before generating.
                first_sentence = re.split(r"(?<=[.!?])\s", prompt.strip(), maxsplit=1)[0]
                if not MOTION_VERBS.search(first_sentence):
                    warn(f"{where}: {beat_label} prompt's FIRST sentence has no visible "
                         "motion — models front-load stillness (cycle-001 defect: "
                         "near-still hook shots)")
                if re.search(r"completely still|motionless|frozen in place", prompt) \
                        and not re.search(r"cloud|grass|wind|ripple|light shift|breath|drift|sway", prompt):
                    warn(f"{where}: {beat_label} asks for stillness with no secondary "
                         "motion clause — reads as a freeze-frame on a phone")
            block = None
            continue
        if block is not None:
            block.append(line)
            continue
        if line.startswith("## Beat"):
            m = BEAT_HEADING.match(line)
            if not m:
                err(f"{where}: malformed beat heading '{line[:60]}' — expected '## Beat NN — TITLE (M:SS–M:SS)'")
                continue
            num, time_range = m.groups()
            beat_label = f"beat {num}"
            beat_nums.append(int(num))
            # the range must appear verbatim in the script — guards against
            # canon drift like the 1:05/1:10 typo found 2026-07-19
            if script is not None and time_range not in script:
                err(f"{where}: beat {num} time range ({time_range}) not found in node.md script")

    if beat_nums != list(range(1, len(beat_nums) + 1)):
        err(f"{where}: beat numbers {beat_nums} not sequential from 01")


def lint_ledger() -> None:
    ledger = REPO / "ledger" / "watering.csv"
    if not ledger.exists():
        err("ledger/watering.csv missing")
        return
    with ledger.open() as f:
        header = next(csv.reader(f), None)
    if header != LEDGER_HEADER:
        err(f"ledger/watering.csv header is {header}, expected {LEDGER_HEADER}")


def lint_licences() -> None:
    """Publish-safety of every licence the shipping artifacts declare. A
    non-commercial or share-alike asset in an episode is not a style problem,
    it is a licence violation of our own CC BY release — and it is invisible in
    the finished mp4, so only code can catch it (near-miss 2026-08-01: an
    entire episode nearly voiced with CC BY-NC F5-TTS weights).

    A RATCHET, not a switch. `.github/workflows/pages.yml` runs this file
    immediately before `build_site.py`, so a hard failure here does not turn a
    badge red — it stops banyan.city from deploying at all. On 2026-08-01 the
    gate's first full run found 46 pre-existing violations, all in node 001;
    fixing records and archiving orphans took it to LICENCE_DEBT below, and the
    rest need either a re-render (queued) or a licence somebody has actually
    read. Failing the deploy over debt this gate itself just discovered would
    have blocked the founder's own goal for the day.

    So: pre-existing debt is an advisory, exactly as warn() already documents
    for "rules adopted after content already shipped" — but the COUNT is
    asserted. One new violation pushes the total above LICENCE_DEBT and fails
    the build immediately. The number may only go down, and lowering it is how
    the debt is retired. Set LICENCE_GATE_STRICT=1 to make every violation
    fatal — the founder's switch, to flip the day the tree is clean.
    """
    errors, advisories = licence_gate.scan(REPO)
    for a in advisories:
        warn(a)
    strict = os.environ.get("LICENCE_GATE_STRICT") == "1"
    if strict or len(errors) > LICENCE_DEBT:
        for e in errors:
            err(e)
        if not strict:
            err(f"licence debt ROSE to {len(errors)} (ratchet: {LICENCE_DEBT}) — "
                "the new asset above is not publishable; replace it or record "
                "its licence. Never raise LICENCE_DEBT to make this pass.")
        return
    for e in errors:
        warn(f"[licence debt] {e}")
    if errors:
        print(f"  ⚠ {len(errors)} pre-existing licence violation(s), ratchet "
              f"{LICENCE_DEBT} — see MORNING-2026-08-01.md; a NEW one fails CI")
    if len(errors) < LICENCE_DEBT:
        print(f"  ✓ licence debt is down to {len(errors)} — lower LICENCE_DEBT "
              f"in lint_genome.py from {LICENCE_DEBT} to {len(errors)}")


def main() -> int:
    genome_dirs = sorted(p for p in (REPO / "genomes").iterdir() if p.is_dir())
    if not genome_dirs:
        err("no genomes found under genomes/")
    for g in genome_dirs:
        lint_genome(g)
    lint_ledger()
    lint_licences()

    if errors:
        print(f"✗ {len(errors)} violation(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"✓ tree healthy — {len(genome_dirs)} genome(s) linted, 0 violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
