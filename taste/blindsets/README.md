# Blind sets — soul as a test suite

A blind set validates the taste file (PRD §7.3): the author blind-scores a set of
candidates; the author-agent scores the same set seeing only the taste file. The
agreement percentage is the **taste fidelity** metric (PRD §12). Phase 4
acceptance: **≥ 90% agreement on a 20-candidate blind set**.

Every divergence is a bug in the taste file, not in the author: interrogate it,
diff a rule, bump the taste-file version, re-run.

## Format

```yaml
taste_file: taste/sapling.founder.v0.3.md
target_pct: 90
items:
  - id: bs-001
    candidates:
      - id: a
        text: |
          (candidate script/beat — any render tier; text is a render)
      - id: b
        text: |
          ...
    author_pick: a        # recorded BLIND, before any agent run
```

## Run

```sh
python3 pipeline/author_agent.py blindset taste/blindsets/<set>.yaml
# writes <set>.results.yaml — commit it; the diff history is the fidelity record
```

`example.yaml` demonstrates the format with two toy items. It is **not**
calibration data — real blind sets are built from candidates the author has
actually blind-scored (the extraction interview, PRD §7.3).
