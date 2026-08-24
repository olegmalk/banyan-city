"""Queue v2 -- durable records, idempotency, machine residency.

Implements upgrade-v2-design.md §3.2 (the four deltas on the maildir queue),
§2.2 verify-then-attest, §2.3 journal+sweep, and §2.4's sample_before_batch.
The directory queue itself is the v1 shape box_runner/box_enqueue already
drain and fill (backlog/ready/running/done/failed, claim = same-volume
rename); what v2 adds is a crash-proof attempt journal that is written BEFORE
work starts, dedupe by content fingerprint across live AND terminal states,
outputs in a content-addressed store outside the repo tree, and a founder
verdict gate between one sample and any batch.

    from queue2 import Queue2, queue2_sweep, record_sample_verdict
"""

from .journal import Journal, JournalCorrupt, ZombieAttempt
from .queue2 import (
    APPROVE_VERDICTS,
    DuplicateSpec,
    HoldActive,
    Queue2,
    Queue2Error,
    ResidencyError,
    SampleBeforeBatch,
    SpecInvalid,
    VerifyFailed,
    output_path_for,
    recipe_fingerprint,
    record_sample_verdict,
    spec_fingerprint,
)
from .sweep import compact_journal, pid_alive, queue2_sweep, startup_sweep

__all__ = [
    "APPROVE_VERDICTS", "DuplicateSpec", "HoldActive", "Journal",
    "JournalCorrupt", "Queue2", "Queue2Error", "ResidencyError",
    "SampleBeforeBatch", "SpecInvalid", "VerifyFailed", "ZombieAttempt",
    "compact_journal", "output_path_for", "pid_alive", "queue2_sweep",
    "recipe_fingerprint", "record_sample_verdict", "spec_fingerprint",
    "startup_sweep",
]
