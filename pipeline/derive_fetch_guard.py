#!/usr/bin/env python3
r"""The retoken trap, as a guard a deriver can call instead of remembering.

WHAT WENT WRONG, ONCE, ON 2026-08-20. `derive_spec.derive()` retokens EVERY
string in a child -- payload keys, argv, embedded python -- so a child that
fetches an artifact its PARENT published gets its URL rewritten too:

    https://raw.githubusercontent.com/.../farm-out/ep2-b08-eraseonly-0820/
                                      -> .../farm-out/ep2-b08-nogoblin-0820/

`ep2-b08-nogoblin-0820` was filed against a directory nobody had written and
died on the card: rc=1, HTTP 404, three seconds into its first step. The sha
assertions were right, the filenames were right, the bytes were on main. Only
the address was invented, and nothing between the deriver and the GPU looked at
it.

WHY THE EXISTING REFUSAL DID NOT CATCH IT. The deriver DID try to override the
fetch script and `derive_spec` refused the override as byte-identical to the
parent's -- correctly, because the text offered WAS the parent's. That refusal
was then read as "the fetch inherits fine". It does not mean that. It only says
your replacement equalled the parent's original; it says nothing about what
retoken left in the child. A guard has to read the EMITTED file.

TWO WAYS TO BE RIGHT, and this module supports the one that costs nothing:

  publish_beside_the_child()  copy the parent's inputs under the child's own
                              name, so the retokened URL becomes true. Git
                              stores one blob for identical content, so N
                              copies of an init cost N tree entries and no
                              objects. This is also what every other job dir in
                              the tree looks like.
  assert_fetch_urls_resolve() re-read the EMITTED yaml and check every
                              raw.githubusercontent URL in it against the
                              filesystem, AFTER retoken has had its way.

    python3 pipeline/derive_fetch_guard.py --selftest

$0, no network, no GPU. The check is deliberately filesystem-only: a spec whose
URL names a directory that is not in this working tree cannot be trusted to be
on origin/main either, and the push is the deriver's own next step.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# `"...main/" "farm-out/x/"` -- the URL is built from two ADJACENT python
# literals split over a line break, so the concatenation is undone before
# matching. A regex that misses that reports "no URL found", which is the one
# answer this guard must never give.
_ADJACENT = re.compile(r'"\s*"')
_URL = re.compile(r"https://raw\.githubusercontent\.com/[^/]+/[^/]+/[^/]+/"
                  r"(farm-out/[A-Za-z0-9._-]+)/")


class FetchGuardError(RuntimeError):
    """Raised for every refusal. Callers are scripts; a traceback is fine."""


def _strings(v):
    if isinstance(v, str):
        yield v
    elif isinstance(v, dict):
        for k, x in v.items():
            yield k
            yield from _strings(x)
    elif isinstance(v, (list, tuple)):
        for x in v:
            yield from _strings(x)


def urls_in(spec: dict) -> set:
    """Every `farm-out/<dir>` a raw.githubusercontent URL in `spec` names."""
    blob = _ADJACENT.sub("", "\n".join(_strings(spec)))
    return set(_URL.findall(blob))


def publish_beside_the_child(src_dir: str, dst_dir: str, want: dict,
                             repo: str = REPO) -> str:
    """Copy `want` {filename: sha256} from src_dir to dst_dir, sha-checked.

    Both paths are repo-relative. Refuses on a mismatch: a file published under
    a new name with the wrong bytes is worse than a 404, because the job's own
    fetch assertion would then catch it ON THE CARD, after the queue has
    claimed it.
    """
    s_abs = os.path.join(repo, src_dir)
    d_abs = os.path.join(repo, dst_dir)
    os.makedirs(d_abs, exist_ok=True)
    for name, sha in sorted(want.items()):
        src = os.path.join(s_abs, name)
        if not os.path.isfile(src):
            raise FetchGuardError("!! %s is not in %s -- nothing to publish"
                                  % (name, src_dir))
        shutil.copy2(src, os.path.join(d_abs, name))
        with open(os.path.join(d_abs, name), "rb") as fh:
            have = hashlib.sha256(fh.read()).hexdigest()
        if have != sha:
            raise FetchGuardError(
                "!! %s published into %s with the wrong bytes\n   want %s\n"
                "   have %s" % (name, dst_dir, sha, have))
    return dst_dir


def assert_fetch_urls_resolve(spec_path: str, must_hold=(), repo: str = REPO,
                              log=print) -> set:
    """Re-read the EMITTED spec and check its fetch URLs against the tree.

    `must_hold` is the filenames each named directory must contain. Returns the
    set of directories checked. Refuses when the spec names no URL at all: a
    deriver that calls this is asserting there is one.
    """
    import yaml
    with open(spec_path, encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    found = urls_in(spec)
    if not found:
        raise FetchGuardError(
            "!! no farm-out fetch URL in %s -- this deriver asserts there is "
            "one, so finding none is a refusal and not a pass" % spec_path)
    for rel in sorted(found):
        d = os.path.join(repo, rel)
        missing = [n for n in must_hold
                   if not os.path.isfile(os.path.join(d, n))]
        if not os.path.isdir(d) or missing:
            raise FetchGuardError(
                "!! the emitted spec fetches from %s/ and that directory does "
                "not hold %s.\n   THIS IS THE RETOKEN TRAP: derive_spec "
                "rewrites every string in a child, published-artifact URLs "
                "included, and a 404 costs a queued job and a claimed card. "
                "Publish the files there (publish_beside_the_child) or "
                "override the payload, which lands AFTER retoken."
                % (rel, ", ".join(missing) or "anything"))
        log("  fetch URL OK: %s/ holds %d named file(s)" % (rel, len(must_hold)))
    return found


def selftest() -> int:
    """Asserts, not prints -- a selftest that only prints is a demo."""
    import tempfile
    import yaml

    split = {"payload": {"f.py": 'RAW = ("https://raw.githubusercontent.com/'
                                 'o/banyan-city/main/"\n       '
                                 '"farm-out/ep2-b08-child-0820/")'}}
    assert urls_in(split) == {"farm-out/ep2-b08-child-0820"}, \
        "the split-literal URL must be found -- this is the whole bug"
    joined = {"a": "https://raw.githubusercontent.com/o/r/main/"
                   "farm-out/ep2-x/f.png"}
    assert urls_in(joined) == {"farm-out/ep2-x"}
    assert urls_in({"a": "no url here"}) == set()
    assert urls_in({"a": ["https://raw.githubusercontent.com/o/r/main/"
                          "farm-out/ep2-deep/x"]}) == {"farm-out/ep2-deep"}

    with tempfile.TemporaryDirectory() as tmp:
        spec = os.path.join(tmp, "s.yaml")
        with open(spec, "w") as fh:
            yaml.safe_dump(split, fh)
        # the directory does not exist -> must refuse
        try:
            assert_fetch_urls_resolve(spec, ("init.png",), repo=tmp,
                                      log=lambda *a: None)
            raise AssertionError("guard did not fire on a missing directory")
        except FetchGuardError as e:
            assert "RETOKEN TRAP" in str(e)
        # publish the file -> must pass
        os.makedirs(os.path.join(tmp, "farm-out/ep2-b08-child-0820"))
        open(os.path.join(tmp, "farm-out/ep2-b08-child-0820/init.png"),
             "wb").write(b"x")
        got = assert_fetch_urls_resolve(spec, ("init.png",), repo=tmp,
                                        log=lambda *a: None)
        assert got == {"farm-out/ep2-b08-child-0820"}
        # a spec with no URL at all -> must refuse rather than pass silently
        empty = os.path.join(tmp, "e.yaml")
        with open(empty, "w") as fh:
            yaml.safe_dump({"payload": {"f.py": "print(1)"}}, fh)
        try:
            assert_fetch_urls_resolve(empty, (), repo=tmp, log=lambda *a: None)
            raise AssertionError("guard did not fire on a spec with no URL")
        except FetchGuardError as e:
            assert "no farm-out fetch URL" in str(e)

        # publish_beside_the_child: right bytes pass, wrong bytes refuse
        os.makedirs(os.path.join(tmp, "src"))
        open(os.path.join(tmp, "src/a.png"), "wb").write(b"hello")
        sha = hashlib.sha256(b"hello").hexdigest()
        publish_beside_the_child("src", "dst", {"a.png": sha}, repo=tmp)
        assert os.path.isfile(os.path.join(tmp, "dst/a.png"))
        try:
            publish_beside_the_child("src", "dst2", {"a.png": "0" * 64},
                                     repo=tmp)
            raise AssertionError("publish did not fire on a sha mismatch")
        except FetchGuardError as e:
            assert "wrong bytes" in str(e)
        try:
            publish_beside_the_child("src", "dst3", {"nope.png": sha},
                                     repo=tmp)
            raise AssertionError("publish did not fire on a missing source")
        except FetchGuardError as e:
            assert "nothing to publish" in str(e)

    print("✓ derive_fetch_guard selftest passed (8 assertions)")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(selftest() if "--selftest" in sys.argv else
                     print(__doc__.strip()) or 0)
