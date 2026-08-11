#!/usr/bin/env python3
"""The Mac is a CACHE of the render box, not a second archive of it.

    python3 pipeline/box_cache.py plan            # report only, deletes nothing
    python3 pipeline/box_cache.py reclaim --yes   # delete only what it proved
    python3 pipeline/box_cache.py fetch --page review/tonight/page.html
    python3 pipeline/box_cache.py fetch review/tonight/02-three-oh-seven.mp4
    python3 pipeline/box_cache.py disk            # refresh the /status tile

WHY THIS EXISTS. Roman, 2026-08-11: "fix the rendering storage issue in the
background" — the laptop was down to 9.6 GiB free while the render box sat on
217 GB. Nothing is rendered on the Mac. Every clip, candidate and contact sheet
under `review/` and `takes/` was MADE on the box and pulled here, and then kept
here forever, on the smallest disk in the system. One lane alone pulled 109
candidate files in a single afternoon. The box is the archive; this laptop only
ever needed the frames someone is actually looking at.

WHAT IT WILL NOT DO, and why each guard is here rather than assumed:

  * It never deletes a file that git tracks. Tracked media is the published
    work; its home is the repo, not the box.
  * It never deletes a file whose name appears in a committed page. A page that
    ships pointing at a file expects that file to be on disk; the ignore rules
    say nothing about that, so this is checked separately, over the text of the
    tracked tree.
  * It never deletes a file it could not find byte-identical on the box. Not
    same-name — same sha256. Filenames on the farm collide constantly (three
    tasks for the same beat all normalise to `01-the-keyboard.mp4`, which is the
    bug collect_farm.py exists to fix), so a name match here would mean deleting
    a good take because a stale one shares its title.
  * If the box cannot be reached at all, the whole run is a no-op. An unreachable
    archive proves nothing, and "prove nothing" must never round to "delete".
  * The sha is re-read immediately before the unlink. Lanes write into this tree
    while this runs; a file that changed between the plan and the act is no
    longer the file that was proven.

WHY A NAMED-SUBSET FETCH AND NOT AN SSH-BACKED SERVER. Serving review media
live off the box would make a review page's correctness depend on the box being
awake and reachable — it would fail exactly when the GPU is busiest, which is
exactly when someone is reviewing. `fetch --page` instead reads a page, takes
the media it actually embeds, and pulls back only those files. The review page
stays a plain static page over local files; the cost is one command, ~seconds
over the LAN, before reviewing something that was reclaimed.

The ledger of what was dropped is `ledger/reclaimed-media.tsv` — tracked, so
the repo remembers the pixels existed and where they went, the same bargain
`takes_backup.py` makes for the takes/ corpus.
"""

import argparse
import hashlib
import re
import shutil
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

DEFAULT_HOST = "rtx5090"
DEFAULT_ROOTS = ("C:\\banyan-farm",)
LEDGER = "ledger/reclaimed-media.tsv"
DISK_FILE = "pipeline/measured/local-disk.yaml"

# A file written in the last half hour is not a cache copy yet. This is a
# shared worktree: on 2026-08-11 one lane was rebuilding the cut in
# review/tonight/ while this was being written, and a file that is mid-arrival
# can be byte-identical to its box original and still be something a running
# job is about to read. Age is the cheapest way to stay out of a live lane's way.
MIN_AGE_S = 30 * 60

# 20 GiB. Not a cliff — the point at which the page should start saying so out
# loud. The 2026-08-11 fall was 19 -> 9.6 GiB in two hours, so a threshold below
# 20 would have lit up only after the useful window had already closed.
WARN_BELOW = 20 * 1024 ** 3

# The extensions the ignore rules already treat as "pixels, not provenance"
# (.gitignore, review/** and takes/** blocks). Sidecars are deliberately absent:
# a .meta.yaml is the record of what a render WAS and is a few hundred bytes.
MEDIA_EXT = {".mp4", ".mov", ".webm", ".png", ".jpg", ".jpeg", ".mp3", ".wav"}

TEXT_EXT = {".md", ".yaml", ".yml", ".html", ".htm", ".py", ".json", ".jsonl",
            ".txt", ".csv", ".tsv", ".js", ".css"}

MEDIA_NAME = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._\-]*\.(?:mp4|mov|webm|png|jpe?g|mp3|wav)", re.I)


# ---------------------------------------------------------------- pure core


def is_candidate(rel: str) -> bool:
    """Is this path one of the box-made copies this tool is allowed to touch?

    Deliberately narrow. Only `review/` (media pulled off the farm for a look)
    and a node's `takes/` (pick-of-N candidates) qualify. Everything else on
    this disk — leaves, stills, cuts, the built site — is either tracked, or
    regenerable locally without the box, and is none of this tool's business.
    """
    if Path(rel).suffix.lower() not in MEDIA_EXT:
        return False
    if rel.startswith("review/"):
        return True
    return rel.startswith("genomes/") and "/takes/" in rel


def referenced_names(texts) -> set:
    """Every media filename mentioned anywhere in the committed text tree.

    Basenames, not paths, and that is on purpose: pages reference media by
    relative URL, by bare name in a markdown table, and by `src=` with a
    directory prefix that does not match the repo layout. Matching on the
    basename over-protects — a file is spared because something, somewhere,
    said its name. Over-protecting costs disk; under-protecting breaks a
    published page, so the asymmetry runs this way deliberately.
    """
    found = set()
    for t in texts:
        for m in MEDIA_NAME.finditer(t):
            found.add(m.group(0))
    return found


def page_media_refs(html: str) -> list:
    """The media a page actually embeds, in first-seen order.

    This is the "named subset" half of fetch-on-demand: a page declares what it
    needs, and only that comes back over the wire.
    """
    seen, out = set(), []
    for m in re.finditer(r'(?:src|href|poster)\s*=\s*["\']([^"\']+)["\']', html):
        ref = m.group(1).split("?")[0].split("#")[0]
        if Path(ref).suffix.lower() in MEDIA_EXT and ref not in seen:
            seen.add(ref)
            out.append(ref)
    return out


@dataclass(frozen=True)
class LocalFile:
    rel: str
    size: int
    sha: str
    age_s: float = 1e9


@dataclass(frozen=True)
class Verdict:
    rel: str
    size: int
    action: str          # "reclaim" | "keep"
    why: str
    box_path: str = ""


def classify(files, remote, tracked, referenced, min_age_s=MIN_AGE_S) -> list:
    """Decide each local file. Pure — this is the whole safety argument.

    `remote` maps lowercase sha256 -> list of box paths holding those exact
    bytes. The guards run most-conservative-first, so a file that is BOTH
    tracked and twinned is kept: having a copy on the box is never a reason to
    remove something whose home is the repo.
    """
    out = []
    for f in sorted(files, key=lambda x: x.rel):
        name = Path(f.rel).name
        if f.rel in tracked:
            out.append(Verdict(f.rel, f.size, "keep", "tracked in git"))
        elif name in referenced:
            out.append(Verdict(f.rel, f.size, "keep",
                               "named by a committed page"))
        elif f.age_s < min_age_s:
            out.append(Verdict(f.rel, f.size, "keep",
                               "written too recently — a lane may still be on it"))
        elif f.size == 0:
            out.append(Verdict(f.rel, f.size, "keep", "empty file"))
        elif f.sha.lower() not in remote:
            out.append(Verdict(f.rel, f.size, "keep",
                               "no byte-identical copy on the box"))
        else:
            out.append(Verdict(f.rel, f.size, "reclaim", "verified on the box",
                               remote[f.sha.lower()][0]))
    return out


def remote_hash_script(sizes, roots) -> str:
    """PowerShell that hashes ONLY the box files whose length we care about.

    The box holds 35,416 files and 86 GB; hashing all of it to answer a
    question about 900 files would take longer than the renders it interrupts.
    Length is a free prefilter — `dir` already knows it — and sha256 still
    decides, so the shortcut costs no certainty. Hashtable keys are strings
    because a PowerShell literal integer is Int32 and a FileInfo.Length is
    Int64, and ContainsKey across those two types silently never matches.
    """
    keys = "; ".join(f'"{int(s)}"=1' for s in sorted(set(sizes)))
    paths = ", ".join('"' + r.replace('"', '') + '"' for r in roots)
    # ONE STATEMENT PER LINE, no trailing-pipe continuations. `powershell
    # -Command -` consumes stdin as if it were typed, so a pipeline broken
    # across lines is an incomplete command, and with the whole run wrapped in
    # SilentlyContinue it fails by printing NOTHING. That reads identically to
    # "the box holds none of your files" — the most dangerous possible way for
    # this script to break, and the way it did break first (2026-08-11).
    return "\n".join([
        "$d = Get-PSDrive -Name C",
        '"#FREE`t" + $d.Free',
        "$s = @{ " + keys + " }",
        f"Get-ChildItem -Path {paths} -Recurse -File -ErrorAction SilentlyContinue"
        " | Where-Object { $s.ContainsKey($_.Length.ToString()) }"
        " | ForEach-Object { $h = (Get-FileHash -Algorithm SHA256"
        ' -LiteralPath $_.FullName).Hash; "$h`t$($_.Length)`t$($_.FullName)" }',
        "",
    ])


def parse_remote(text: str):
    """(sha -> [box paths], free bytes or None) from the script's output."""
    remote, free = {}, None
    for line in text.splitlines():
        line = line.rstrip("\r")
        if line.startswith("#FREE\t"):
            try:
                free = int(line.split("\t", 1)[1])
            except ValueError:
                free = None
            continue
        parts = line.split("\t")
        if len(parts) != 3 or len(parts[0]) != 64:
            continue
        remote.setdefault(parts[0].lower(), []).append(parts[2])
    return remote, free


def win_to_scp(path: str) -> str:
    """A Windows path in the form scp will carry over the wire."""
    return path.replace("\\", "/")


def words(n: int) -> str:
    for unit, div in (("GiB", 2 ** 30), ("MiB", 2 ** 20), ("KiB", 2 ** 10)):
        if n >= div:
            return f"{n / div:.1f} {unit}"
    return f"{n} B"


# ------------------------------------------------------------ impure edges


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def tracked_paths() -> set:
    return {p for p in git("ls-files", "-z").split("\0") if p}


def local_candidates(hash_files=True) -> list:
    """Every gitignored media file under review/ and takes/, hashed.

    Enumerated through git rather than by walking, so "is this ignored" is
    answered by the same rules git uses. A file git does not consider ignored
    is either tracked or brand new, and neither is ours to remove.
    """
    out = []
    listing = git("ls-files", "-o", "-i", "--exclude-standard", "-z")
    for rel in listing.split("\0"):
        if not rel or not is_candidate(rel):
            continue
        p = REPO / rel
        if not p.is_file() or p.is_symlink():
            continue
        st = p.stat()
        # `disk` only needs the byte total, and hashing 620 MB to print one
        # number would make the reading too slow to take often — which is the
        # whole failure this is meant to fix.
        out.append(LocalFile(rel, st.st_size, sha256(p) if hash_files else "",
                             max(0.0, time.time() - st.st_mtime)))
    return out


def committed_references() -> set:
    """Media names mentioned by tracked text. Read once, not grepped per file."""
    texts = []
    for rel in tracked_paths():
        if Path(rel).suffix.lower() not in TEXT_EXT:
            continue
        p = REPO / rel
        try:
            if p.is_file() and p.stat().st_size < 4 * 1024 * 1024:
                texts.append(p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    return referenced_names(texts)


def ssh_powershell(host: str, script: str, timeout: int = 900):
    """Run a PowerShell script on the box. Returns (ok, stdout, why-not).

    Fails soft in every direction — an unreachable box is a normal Tuesday
    (asleep, mid-bugcheck, waiting on a human login) and must produce a no-op,
    not a traceback and not an empty index that reads as "nothing is backed up".
    """
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", host,
           "powershell -NoProfile -ExecutionPolicy Bypass -Command -"]
    try:
        r = subprocess.run(cmd, input=script, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except FileNotFoundError:
        return False, "", "ssh is not installed on this machine"
    except subprocess.TimeoutExpired:
        return False, "", f"{host} did not answer within {timeout}s"
    if r.returncode != 0:
        why = (r.stderr or "").strip().splitlines()
        return False, "", f"ssh to {host} failed: {why[-1] if why else 'no reason given'}"
    return True, r.stdout, ""


def previous_reading() -> dict:
    """The last reading, as flat key -> string. No yaml dependency: this file
    is written by the function below and is flat by construction."""
    p = REPO / DISK_FILE
    out = {}
    if not p.is_file():
        return out
    for line in p.read_text().splitlines():
        if line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    return out


def disk_reading(box_free=None, cached=0, reclaimable=0,
                 box_checked_on=None) -> str:
    """The yaml the /status tile reads. A measurement with a date on it."""
    usage = shutil.disk_usage(str(REPO))
    lines = [
        "# How much room is left on the laptop that reviews the renders.",
        "#",
        "# Roman, 2026-08-11, after the Mac hit 9.6 GiB free while the render box",
        "# sat on 217 GB: \"fix the rendering storage issue in the background\". It",
        "# had fallen 19 -> 9.6 GiB in two hours and nobody noticed until a",
        "# supervisor tick happened to look. A number nobody can see is a number",
        "# nobody watches, so it goes on the page next to the other measurements.",
        "#",
        "# WHY A FILE AND NOT A LIVE READ, same as render-bandwidth.yaml beside it:",
        "# the deploy server has its own disk and reading THAT would publish a",
        "# confident, meaningless number. This is written by",
        "# `python3 pipeline/box_cache.py disk` (and by every plan/reclaim run) on",
        "# the machine it describes, and the page prints the date so it ages in",
        "# public rather than pretending to be current.",
        f"measured_on: {time.strftime('%Y-%m-%dT%H:%M:%S')}",
        f"host: {socket.gethostname()}",
        f"free_bytes: {usage.free}",
        f"total_bytes: {usage.total}",
        f"warn_below_bytes: {WARN_BELOW}",
        f"cached_media_bytes: {cached}",
    ]
    # The box figures cost an ssh round trip and a hash pass, so `disk` carries
    # the last ones forward rather than dropping them — but under their OWN
    # date. A reclaimable total from this morning printed under this minute's
    # timestamp would be the page inventing a measurement it did not take.
    if box_free is not None:
        lines.append(f"box: {DEFAULT_HOST}")
        lines.append(f"box_free_bytes: {box_free}")
        lines.append(f"reclaimable_bytes: {reclaimable}")
        lines.append(f"box_checked_on: {box_checked_on or time.strftime('%Y-%m-%dT%H:%M:%S')}")
    return "\n".join(lines) + "\n"


def write_disk_reading(**kw) -> None:
    p = REPO / DISK_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(disk_reading(**kw))


def ledger_rows() -> list:
    p = REPO / LEDGER
    if not p.is_file():
        return []
    rows = []
    for line in p.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) == 5:
            rows.append(dict(zip(("when", "rel", "size", "sha", "box"), parts)))
    return rows


def ledger_append(rows) -> None:
    p = REPO / LEDGER
    p.parent.mkdir(parents=True, exist_ok=True)
    new = not p.is_file()
    with p.open("a", encoding="utf-8") as fh:
        if new:
            fh.write(
                "# Local copies removed by pipeline/box_cache.py because the same\n"
                "# bytes were verified present on the render box. Tracked on purpose:\n"
                "# without it the repo would hold no record that these frames ever\n"
                "# existed. Bring one back with `box_cache.py fetch <path>`.\n"
                "# when\trepo path\tbytes\tsha256\tbox path\n")
        for r in rows:
            fh.write("\t".join(str(r[k]) for k in
                               ("when", "rel", "size", "sha", "box")) + "\n")


# ------------------------------------------------------------- the commands


def survey(host, roots, min_age_s=MIN_AGE_S):
    """Everything both machines know, or an honest reason we do not know it."""
    files = local_candidates()
    cached = sum(f.size for f in files)
    if not files:
        return [], [], None, cached, ""
    ok, out, why = ssh_powershell(
        host, remote_hash_script([f.size for f in files], roots))
    if not ok:
        return files, [], None, cached, why
    remote, free = parse_remote(out)
    verdicts = classify(files, remote, tracked_paths(), committed_references(),
                        min_age_s)
    return files, verdicts, free, cached, ""


def report(verdicts, cached, free, why) -> int:
    kept = {}
    gain = 0
    for v in verdicts:
        if v.action == "reclaim":
            gain += v.size
        else:
            k = kept.setdefault(v.why, [0, 0])
            k[0] += 1
            k[1] += v.size
    usage = shutil.disk_usage(str(REPO))
    print(f"laptop free      {words(usage.free)}"
          + ("  ⚠ below the warn line" if usage.free < WARN_BELOW else ""))
    if free is not None:
        print(f"box free         {words(free)}")
    print(f"cached media     {words(cached)} in review/ and takes/")
    if why:
        print(f"\nNO-OP: {why}.")
        print("Nothing was removed. An archive that cannot be reached proves "
              "nothing,\nand proving nothing must never round to deleting.")
        return 0
    for reason, (n, b) in sorted(kept.items(), key=lambda x: -x[1][1]):
        print(f"  keep {n:4d} files  {words(b):>10}   {reason}")
    n = sum(1 for v in verdicts if v.action == "reclaim")
    print(f"  DROP {n:4d} files  {words(gain):>10}   verified byte-identical on the box")
    return 0


def takes_note(verdicts) -> str:
    """One line, printed only when it applies. `takes_backup.py verify` with no
    --dir checks THIS disk, so reclaiming candidates makes it report them
    missing — which is true, and is the state the manifest was written to
    describe. Say so rather than letting someone meet it as a mystery."""
    n = sum(1 for v in verdicts if v.action == "reclaim" and "/takes/" in v.rel)
    if not n:
        return ""
    return (f"\nNote: {n} of these are takes/ candidates. `takes_backup.py verify`\n"
            "without --dir will now report them missing on this disk — that is the\n"
            "manifest doing its job. Verify the box copy, or fetch them back first.")


def cmd_plan(a) -> int:
    files, verdicts, free, cached, why = survey(a.host, a.root, a.min_age * 60)
    gain = sum(v.size for v in verdicts if v.action == "reclaim")
    write_disk_reading(box_free=free, cached=cached, reclaimable=gain)
    rc = report(verdicts, cached, free, why)
    if not why:
        print(f"\nDry run. `box_cache.py reclaim --yes` would free {words(gain)}.")
        note = takes_note(verdicts)
        if note:
            print(note)
    return rc


def cmd_reclaim(a) -> int:
    files, verdicts, free, cached, why = survey(a.host, a.root, a.min_age * 60)
    gain = sum(v.size for v in verdicts if v.action == "reclaim")
    write_disk_reading(box_free=free, cached=cached, reclaimable=gain)
    report(verdicts, cached, free, why)
    if why:
        return 0
    note = takes_note(verdicts)
    if note:
        print(note)
    if not a.yes:
        print(f"\nWould free {words(gain)}. Re-run with --yes to actually remove.")
        return 0
    when = time.strftime("%Y-%m-%d")
    rows, freed, skipped = [], 0, 0
    for v in verdicts:
        if v.action != "reclaim":
            continue
        p = REPO / v.rel
        if not p.is_file():
            continue
        # Re-prove immediately before the unlink. Lanes write into review/ while
        # this runs; a file that changed since the plan is not the proven file.
        want = next(f.sha for f in files if f.rel == v.rel)
        if sha256(p) != want or p.stat().st_size != v.size:
            print(f"  skip {v.rel} — changed since it was proven")
            skipped += 1
            continue
        rows.append({"when": when, "rel": v.rel, "size": v.size,
                     "sha": want, "box": v.box_path})
        p.unlink()
        freed += v.size
    if rows:
        ledger_append(rows)
    write_disk_reading(box_free=free, cached=cached - freed, reclaimable=0)
    print(f"\nRemoved {len(rows)} files, freed {words(freed)}"
          + (f" ({skipped} skipped as changed)" if skipped else "") + ".")
    print(f"Recorded in {LEDGER}; bring any of them back with "
          "`box_cache.py fetch <path>`.")
    return 0


def cmd_fetch(a) -> int:
    wanted = list(a.paths)
    if a.page:
        page = Path(a.page)
        page = page if page.is_absolute() else REPO / page
        if not page.is_file():
            print(f"no such page: {a.page}")
            return 1
        base = page.parent
        for ref in page_media_refs(page.read_text(encoding="utf-8",
                                                  errors="replace")):
            if ref.startswith(("http://", "https://", "data:", "//")):
                continue
            try:
                wanted.append(str((base / ref).resolve().relative_to(REPO)))
            except ValueError:
                continue
    if not wanted:
        print("nothing named to fetch (pass paths, or --page)")
        return 1
    known = {r["rel"]: r for r in ledger_rows()}
    got = miss = 0
    for rel in dict.fromkeys(wanted):
        dest = REPO / rel
        if dest.is_file():
            continue                      # already local; fetch is idempotent
        row = known.get(rel)
        if not row:
            print(f"  ? {rel} — not in {LEDGER}, so the box copy is unknown")
            miss += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(
            ["scp", "-q", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
             f'{a.host}:{win_to_scp(row["box"])}', str(dest)],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0 or not dest.is_file():
            print(f"  ! {rel} — scp failed: {(r.stderr or '').strip()[:120]}")
            miss += 1
            continue
        if sha256(dest) != row["sha"]:
            dest.unlink()
            print(f"  ! {rel} — arrived with the wrong sha256, discarded")
            miss += 1
            continue
        print(f"  + {rel} ({words(int(row['size']))})")
        got += 1
    print(f"\nfetched {got}, unavailable {miss}")
    return 1 if miss else 0


def cmd_disk(a) -> int:
    """Free space only — no ssh, no hashing, fast enough to run on every tick."""
    prev = previous_reading()
    files = local_candidates(hash_files=False)
    try:
        box_free = int(prev["box_free_bytes"])
        recl = int(prev.get("reclaimable_bytes") or 0)
        checked = prev.get("box_checked_on") or prev.get("measured_on")
    except (KeyError, ValueError):
        box_free = recl = checked = None
    write_disk_reading(box_free=box_free, cached=sum(f.size for f in files),
                       reclaimable=recl or 0, box_checked_on=checked)
    usage = shutil.disk_usage(str(REPO))
    print(f"free {words(usage.free)} of {words(usage.total)} — wrote {DISK_FILE}"
          + ("  ⚠ below the warn line" if usage.free < WARN_BELOW else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--root", action="append", default=None,
                    help="box directory to search (repeatable)")
    ap.add_argument("--min-age", type=float, default=MIN_AGE_S / 60,
                    dest="min_age", metavar="MIN",
                    help="never touch a file written this recently "
                         f"(default {MIN_AGE_S // 60:.0f} min)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    rec = sub.add_parser("reclaim")
    rec.add_argument("--yes", action="store_true")
    fet = sub.add_parser("fetch")
    fet.add_argument("paths", nargs="*")
    fet.add_argument("--page", help="pull back only the media this page embeds")
    sub.add_parser("disk")
    a = ap.parse_args()
    a.root = a.root or list(DEFAULT_ROOTS)
    return {"plan": cmd_plan, "reclaim": cmd_reclaim,
            "fetch": cmd_fetch, "disk": cmd_disk}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
