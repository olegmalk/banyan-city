#!/usr/bin/env python3
"""The write-ahead attempt journal: SQLite, WAL, synchronous=FULL.

WHY IT EXISTS. Attempt counters were blind to BSODs ("any failure mode that
takes down the OS is invisible to the attempt counter" -- the animegen
post-mortem), window-CLOSE killed workers and removed its own evidence, and
attempt history was reconstructed by grepping heartbeat prose. This file
inverts that: the STARTED row {job_id, attempt_n, machine, pid, ts} is
committed and fsync'd BEFORE any work is spawned -- the Brandur/Stripe
idempotency-key pattern, insert the intent record in its own transaction
before doing the work -- so a crash cannot erase its own evidence. Heartbeat
prose is a projection of this journal, never the source.

THE PRAGMA FINE PRINT IS LOAD-BEARING. WAL + synchronous=NORMAL survives app
crashes but can lose a committed transaction on OS crash or power loss -- and
a BSOD is an OS crash -- so this journal runs synchronous=FULL. The design
doc names it (§2.3); do not "optimize" it back to NORMAL.

CORRUPTION IS LOUD, NEVER ZERO. A truncated or corrupt journal raises
JournalCorrupt at open (integrity_check runs every time -- the db is tiny),
because a corrupt db answering "0 attempts" is exactly the silent-failure
class this whole layer exists to kill. Recovery is an explicit, recorded act:
Journal.recover() quarantines the corrupt file beside itself and starts a
fresh journal that carries a `recovered_from` meta row -- history loss is a
fact in the record, not an absence.

ZOMBIE GUARD (litequeue's claim_id pattern). Completion presents the attempt
row id it holds; DONE/FAILED transitions only fire on a row still in STARTED.
A resurrected process cannot mark DONE a job that was swept and re-run --
its row was already retired to INTERRUPTED and the UPDATE matches nothing.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import time


class JournalCorrupt(Exception):
    """The journal db cannot be trusted. rc 6. Recover with Journal.recover()."""
    rc = 6


class ZombieAttempt(Exception):
    """A terminal record presented a stale attempt token. rc 7."""
    rc = 7


SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id      TEXT PRIMARY KEY,
    spec_fp     TEXT NOT NULL,
    recipe_fp   TEXT NOT NULL,
    fanout      INTEGER NOT NULL DEFAULT 1,
    enqueued_ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS jobs_spec_fp   ON jobs (spec_fp);
CREATE INDEX IF NOT EXISTS jobs_recipe_fp ON jobs (recipe_fp);

CREATE TABLE IF NOT EXISTS attempts (
    attempt_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          TEXT NOT NULL,
    attempt_n       INTEGER NOT NULL,
    machine         TEXT NOT NULL,
    pid             INTEGER,
    state           TEXT NOT NULL,
    reason          TEXT,
    started_ts      TEXT NOT NULL,
    started_epoch   REAL NOT NULL,
    ended_ts        TEXT,
    output_path     TEXT,
    readback_sha256 TEXT,
    readback_bytes  INTEGER,
    readback_ts     TEXT,
    boot_id         TEXT
);
CREATE INDEX IF NOT EXISTS attempts_job   ON attempts (job_id);
CREATE INDEX IF NOT EXISTS attempts_state ON attempts (state);

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT NOT NULL,
    value TEXT NOT NULL,
    ts    TEXT NOT NULL
);
"""

STATES = ("STARTED", "DONE", "FAILED", "INTERRUPTED")


def utcnow() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---- boot identity ---------------------------------------------------------
# WHY: a pid is only meaningful within one boot. After a reboot the OS hands
# the same numbers out again, so a STARTED row from the previous boot can
# point at a pid that is alive TODAY doing something else -- and pid_alive()
# would call the dead attempt live forever. The journal therefore records
# which boot an attempt belongs to; the sweep treats a row from another boot
# as dead no matter what its pid looks like now.

_BOOT_ID_CACHE = None
BOOT_TOLERANCE_S = 5.0  # two epochs this close are the same boot (a real
                        # reboot on the box takes ~90s; method jitter is <2s)


def _boot_epoch_windows():
    # Preferred: WMI's LastBootUpTime, a string FIXED at boot -- stable
    # across every process that asks. CIM datetime: yyyymmddHHMMSS.ffffff+UUU
    # where UUU is minutes ahead of UTC.
    try:
        out = subprocess.run(
            ["wmic", "os", "get", "lastbootuptime", "/value"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=15).stdout
        for line in out.splitlines():
            if "=" in line and "lastbootuptime" in line.lower():
                stamp = line.split("=", 1)[1].strip()
                base, rest = stamp[:14], stamp[14:]
                offset_min = 0
                for sign in ("+", "-"):
                    if sign in rest:
                        offset_min = int(rest[rest.index(sign):])
                        break
                import calendar
                st = time.strptime(base, "%Y%m%d%H%M%S")
                return float(calendar.timegm(st) - offset_min * 60)
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    # wmic is deprecated and ABSENT on this farm's Win11 box (measured
    # 2026-08-24). Same source via PowerShell CIM: LastBootUpTime is a value
    # FIXED at boot, stable across every process that asks -- unlike the
    # tick fallback below, which drifts by however long the machine spent
    # powered off or suspended inside one fast-startup kernel session
    # (measured 9.2h apart on the box). Slow (~1s) but cached per process.
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "[long](((Get-CimInstance Win32_OperatingSystem).LastBootUpTime"
             ".ToUniversalTime() - [datetime]'1970-01-01T00:00:00Z')"
             ".TotalSeconds)"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=30).stdout.strip()
        if out:
            return float(int(out))
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    # Last resort: boot epoch derived from the monotonic-since-boot tick
    # counter. Jitters ~1s between processes (BOOT_TOLERANCE_S absorbs
    # that) and shifts across suspend -- acceptable only when both stable
    # sources are gone.
    try:
        import ctypes
        ticks_ms = ctypes.windll.kernel32.GetTickCount64()
        return time.time() - ticks_ms / 1000.0
    except (OSError, AttributeError):
        return None


def _boot_epoch_posix():
    if sys.platform == "darwin":
        try:
            out = subprocess.run(["sysctl", "-n", "kern.boottime"],
                                 capture_output=True, text=True,
                                 timeout=15).stdout
            # "{ sec = 1756020000, usec = 123456 } Mon Aug 24 ..."
            sec = out.split("sec =", 1)[1].split(",", 1)[0].strip()
            return float(int(sec))
        except (OSError, ValueError, IndexError, subprocess.SubprocessError):
            return None
    try:
        with open("/proc/stat", encoding="utf-8") as fh:  # linux
            for line in fh:
                if line.startswith("btime "):
                    return float(int(line.split()[1]))
    except (OSError, ValueError, IndexError):
        pass
    return None


def boot_id() -> str:
    """This boot's identity: the boot epoch as a whole-second string.
    Empty string when the platform gives no answer -- UNKNOWN, never a lie;
    the sweep falls back to pid-liveness alone for unknown rows."""
    global _BOOT_ID_CACHE
    if _BOOT_ID_CACHE is None:
        epoch = (_boot_epoch_windows() if sys.platform == "win32"
                 else _boot_epoch_posix())
        _BOOT_ID_CACHE = "%.0f" % epoch if epoch is not None else ""
    return _BOOT_ID_CACHE


def same_boot(recorded, current) -> bool:
    """True only when BOTH ids are known and name the same boot (within
    tolerance -- wmic and the tick fallback may disagree by a second or two).
    Either side unknown/legacy-NULL -> None: no boot verdict, pid decides."""
    if not recorded or not current:
        return None
    try:
        return abs(float(recorded) - float(current)) <= BOOT_TOLERANCE_S
    except ValueError:
        return recorded == current


class Journal:
    def __init__(self, path: str):
        self.path = path
        try:
            self.db = sqlite3.connect(path)
            self.db.row_factory = sqlite3.Row
            # WAL for concurrent readers (the sweeper and a status page can
            # read while the worker writes); FULL so the pre-work record
            # survives the OS itself dying one second later.
            self.db.execute("PRAGMA journal_mode=WAL")
            self.db.execute("PRAGMA synchronous=FULL")
            verdict = self.db.execute("PRAGMA integrity_check").fetchone()[0]
            if verdict != "ok":
                raise sqlite3.DatabaseError("integrity_check: %s" % verdict)
            self.db.executescript(SCHEMA)
            # Migration for journals created before boot_id existed (the
            # box's live journal.db): CREATE IF NOT EXISTS will not add a
            # column, ALTER does. Old rows stay NULL = boot unknown.
            cols = [r[1] for r in
                    self.db.execute("PRAGMA table_info(attempts)").fetchall()]
            if "boot_id" not in cols:
                self.db.execute("ALTER TABLE attempts ADD COLUMN boot_id TEXT")
            self.db.commit()
        except sqlite3.DatabaseError as exc:
            # Release the OS handle before raising. CPython's sqlite3 keeps a
            # prepared-statement LRU cache whose Statements point back at the
            # Connection -- a reference CYCLE, so a dropped connection is
            # freed only by the cyclic GC, never by refcounting. On POSIX that
            # is invisible (an open file can still be unlinked); on Windows
            # the file stays LOCKED -- and the very next thing a caller does
            # after this raise is Journal.recover(), which RENAMES this file.
            # Leaking here would make recovery, the one path that runs when
            # things are already bad, fail with WinError 32.
            try:
                self.db.close()
            except (sqlite3.Error, AttributeError):
                pass
            raise JournalCorrupt(
                "!! journal %s is corrupt (%s) -- refusing to answer from it; "
                "quarantine + restart with Journal.recover(%r)"
                % (path, exc, path)) from exc

    def _exec(self, sql: str, args: tuple = ()):
        # Every later query gets the same loudness the open-time check gives:
        # a db that decays mid-session raises, it does not return few rows.
        try:
            return self.db.execute(sql, args)
        except sqlite3.DatabaseError as exc:
            raise JournalCorrupt(
                "!! journal %s failed mid-query (%s) -- recover, do not trust"
                % (self.path, exc)) from exc

    @classmethod
    def recover(cls, path: str):
        """Quarantine a corrupt journal and start fresh, ON THE RECORD.

        Returns (journal, quarantine_path). The fresh journal carries a
        `recovered_from` meta row so no reader can mistake "recovered
        yesterday" for "never had an attempt" -- dedupe falls back to the
        done/failed directories, which are the other half of the evidence.
        """
        quarantine = "%s.corrupt-%d" % (path, int(time.time()))
        os.replace(path, quarantine)
        for tail in ("-wal", "-shm"):
            side = path + tail
            if os.path.exists(side):
                os.replace(side, quarantine + tail)
        journal = cls(path)
        journal._exec("INSERT INTO meta (key, value, ts) VALUES (?, ?, ?)",
                      ("recovered_from", quarantine, utcnow()))
        journal.db.commit()
        return journal, quarantine

    def recovered_from(self):
        row = self._exec(
            "SELECT value FROM meta WHERE key='recovered_from' "
            "ORDER BY ts DESC LIMIT 1").fetchone()
        return row["value"] if row else None

    # ---- enqueue-time records ------------------------------------------

    def record_enqueued(self, job_id: str, spec_fp: str, recipe_fp: str,
                        fanout: int = 1) -> None:
        self._exec("INSERT INTO jobs (job_id, spec_fp, recipe_fp, fanout, "
                   "enqueued_ts) VALUES (?, ?, ?, ?, ?)",
                   (job_id, spec_fp, recipe_fp, int(fanout), utcnow()))
        self.db.commit()

    def spec_fp_known(self, spec_fp: str) -> bool:
        return self._exec("SELECT 1 FROM jobs WHERE spec_fp=? LIMIT 1",
                          (spec_fp,)).fetchone() is not None

    def recipe_count(self, recipe_fp: str, exclude_spec_fp: str = "") -> int:
        """How many outputs this recipe already fans across, counting
        DISTINCT spec contents -- a byte-identical re-file (--again) is the
        same sample run twice, not a wider batch."""
        return self._exec(
            "SELECT COALESCE(SUM(f), 0) AS n FROM (SELECT MAX(fanout) AS f "
            "FROM jobs WHERE recipe_fp=? AND spec_fp<>? GROUP BY spec_fp)",
            (recipe_fp, exclude_spec_fp)).fetchone()["n"]

    # ---- attempt lifecycle ---------------------------------------------

    def record_started(self, job_id: str, attempt_n: int, machine: str,
                       pid: int, boot: str = None) -> int:
        """THE write-ahead record. Committed (and, at synchronous=FULL,
        fsync'd) before the caller spawns anything. Returns the attempt
        token every terminal transition must present. The row carries this
        boot's id: a pid is only a name within one boot, and the sweep must
        be able to see that a row belongs to a boot that is over."""
        cur = self._exec(
            "INSERT INTO attempts (job_id, attempt_n, machine, pid, state, "
            "started_ts, started_epoch, boot_id) "
            "VALUES (?, ?, ?, ?, 'STARTED', ?, ?, ?)",
            (job_id, attempt_n, machine, int(pid), utcnow(), time.time(),
             boot_id() if boot is None else boot))
        self.db.commit()
        return cur.lastrowid

    def attest_done(self, attempt_id: int, output_path: str, sha256: str,
                    nbytes: int) -> None:
        """DONE only lands on a row still STARTED -- the zombie guard."""
        cur = self._exec(
            "UPDATE attempts SET state='DONE', ended_ts=?, output_path=?, "
            "readback_sha256=?, readback_bytes=?, readback_ts=? "
            "WHERE attempt_id=? AND state='STARTED'",
            (utcnow(), output_path, sha256, int(nbytes), utcnow(),
             int(attempt_id)))
        self.db.commit()
        if cur.rowcount != 1:
            raise ZombieAttempt(
                "!! attempt %s is not live -- this process was swept and its "
                "job re-owned; a resurrected worker may not attest DONE"
                % attempt_id)

    def record_failed(self, attempt_id: int, reason: str) -> None:
        cur = self._exec(
            "UPDATE attempts SET state='FAILED', ended_ts=?, reason=? "
            "WHERE attempt_id=? AND state='STARTED'",
            (utcnow(), reason, int(attempt_id)))
        self.db.commit()
        if cur.rowcount != 1:
            raise ZombieAttempt(
                "!! attempt %s is not live -- stale token, FAILED not recorded"
                % attempt_id)

    def mark_interrupted(self, attempt_id: int, reason: str) -> bool:
        """Sweep-only transition; returns False (does not raise) when the
        row already reached a terminal state between listing and marking."""
        cur = self._exec(
            "UPDATE attempts SET state='INTERRUPTED', ended_ts=?, reason=? "
            "WHERE attempt_id=? AND state='STARTED'",
            (utcnow(), reason, int(attempt_id)))
        self.db.commit()
        return cur.rowcount == 1

    # ---- reads -----------------------------------------------------------

    def attempt_count(self, job_id: str) -> int:
        """Every attempt counts, whatever ended it. A job that takes down its
        own host CONSUMES budget (design §2.3, the b4 WDDM ban in code):
        INTERRUPTED rows are spent attempts, not free retries."""
        return self._exec("SELECT COUNT(*) AS n FROM attempts WHERE job_id=?",
                          (job_id,)).fetchone()["n"]

    def attempts_for(self, job_id: str) -> list:
        return [dict(r) for r in self._exec(
            "SELECT * FROM attempts WHERE job_id=? ORDER BY attempt_id",
            (job_id,)).fetchall()]

    def started_rows(self, machine: str = None) -> list:
        if machine is None:
            cur = self._exec("SELECT * FROM attempts WHERE state='STARTED' "
                             "ORDER BY attempt_id")
        else:
            cur = self._exec("SELECT * FROM attempts WHERE state='STARTED' "
                             "AND machine=? ORDER BY attempt_id", (machine,))
        return [dict(r) for r in cur.fetchall()]

    # ---- compaction ------------------------------------------------------

    def compact(self, export_path: str, keep_days: float = 14.0) -> int:
        """Export-then-delete terminal attempt rows older than keep_days.

        Write-ahead applies to compaction too: the ndjson export is written
        and fsync'd BEFORE any row is deleted, so compaction can crash at any
        line without losing history. The export is a small text record --
        the one artifact class §2.1 allows back into the repo. The jobs
        table is never compacted: it is the idempotency memory and it is
        tiny. Returns the number of rows retired."""
        cutoff = time.time() - keep_days * 86400.0
        # `<=`, not `<`: on Windows time.time() is GetSystemTimeAsFileTime,
        # which ticks every 15.625 ms -- an attempt started and finished
        # inside one tick has started_epoch EXACTLY equal to a keep_days=0
        # cutoff, and a strict `<` would silently retire nothing. Measured on
        # the rtx5090 box 2026-08-24: 200 tight time.time() samples, ONE
        # distinct value. At keep_days=14 the boundary case cannot matter.
        rows = [dict(r) for r in self._exec(
            "SELECT * FROM attempts WHERE state IN "
            "('DONE','FAILED','INTERRUPTED') AND started_epoch <= ?",
            (cutoff,)).fetchall()]
        if not rows:
            return 0
        os.makedirs(os.path.dirname(export_path) or ".", exist_ok=True)
        with open(export_path, "a", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        self._exec("DELETE FROM attempts WHERE attempt_id IN (%s)"
                   % ",".join(str(r["attempt_id"]) for r in rows))
        self.db.commit()
        self._exec("PRAGMA wal_checkpoint(TRUNCATE)")
        return len(rows)

    def close(self) -> None:
        self.db.close()
