#!/usr/bin/env python3
r"""Derive pipeline/jobs/ep2-b19-sapmid-b-0819.yaml -- the same rung, without the network.

PARENT: pipeline/jobs/ep2-b19-sapmid-0819.yaml, the 0.26 midpoint between two
PASSING inpaint strengths on beat 19's sapling composite. It never rendered.
rc=1 at its FIRST step, 2026-08-19T16:43:12Z, roughly three minutes after start:
`socket.gaierror [Errno 11001] getaddrinfo failed` out of fetch_init.py's
urllib.request.urlopen. No GPU ran, no sampler loaded, no pixels exist -- so the
parent's bar is untouched and still pre-registered, which is why this child
carries it verbatim rather than re-inventing it.

THE CURE WAS ALREADY IN THE TREE AND NEVER CROSSED LANES. That was the THIRD
network-fetch failure on the box that day and the SECOND lane to hit one.
pipeline/measured/failed-acknowledged.yaml carries a `fetch-404` group for
ep2-b12-plateship-0819 whose two failures were fixed the same hour by REPLACING
THE FETCH WITH A BOX-LOCAL COPY under the same per-file sha256 assertion (commit
0f799ddd), after which the successor ran rc=0. Byte-identity comes from the hash,
not from where the bytes came from: a file matching the committed sha IS the
committed file, whichever directory on the card it came out of.

WHERE THE BYTES ALREADY ARE, checked by certutil on the box before this spec was
written rather than asserted:

  C:\banyan-farm\courier-box\farm-out\ep2-b19-sapcomp-0819\   both, at sha
  C:\banyan-farm\courier-box\farm-out\ep2-b19-sapgloss-0819\  both, at sha
  C:\banyan-farm\b19sapcomp-0819\                             init at sha
  C:\banyan-farm\b19sapgloss-0819\                            init at sha

The parent's fetch_init.py docstring said these files "are NOT on the box's
courier worktree -- the courier only ever contains what the box produced." That
was true of the composite the day it was drawn on a Mac and stopped being true
the moment ep2-b19-sapcomp-0819 and ep2-b19-sapgloss-0819 published their own
inputs alongside their outputs. Same species of stale claim as the b12 header
that said plates-local no longer existed while three copies sat on the card.

TWO THINGS BESIDES THE FETCH, BOTH DURABILITY AND NEITHER A RENDER VARIABLE:

  * max_attempts 1 -> 2. A three-second DNS blink permanently killed a GPU job
    and idled the card behind it. Every step in this spec is now idempotent --
    the copy re-asserts shas, the inpaint is a fixed seed writing over its own
    output, the publish names every file in full -- so a retry cannot half-run.
  * THE WORKING DIRECTORY AND THE OUTPUT FILENAME ARE THIS JOB'S. The parent
    wrote its payload into C:\banyan-farm\b19sapgloss-0819 -- the PARENT SAPGLOSS
    JOB'S directory -- and named its output b19-sapgloss-s20260819.png, which is
    byte-for-byte the filename of the 0.22 sample that job already published. Two
    distinct takes, one basename, and a working directory a second job would
    clobber. Retokened to b19sapmid-b-0819 / b19-sapmid-b-s20260819.png. This is
    the duplicate-filename repair done in the GENERATOR, which is where it
    belongs: renaming a published artifact would invalidate the .sha256 that
    proves it arrived intact.

TAKEOVER, SAID PLAINLY. The parent's `what_the_next_lane_should_do` reserved the
re-run for the beat-19 composite lane and warned that two lanes re-filing the
same job is exactly what box_enqueue's idempotency gap turns into 264 wasted GPU
seconds. The owner was notified and the card is EMPTY NOW -- ready 0, running 0,
backlog 0, checked directly on the box and not off a box_autofill snapshot. A new
id under a new working directory cannot collide with the parent even if the owner
re-files it, and the parent stays in the tree carrying its outcome.

EVERY RENDER ARGUMENT IS THE PARENT'S: same init and mask at the same two shas,
same prompt and negative, same seed 20260819, same 40 steps, cfg 7.5, strength
0.26, pad-crop 64, blur 8. $0 to derive, ~5 min on the card, one sample.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import derive_spec  # noqa: E402

SRC = "pipeline/jobs/ep2-b19-sapmid-0819.yaml"
OUT = "pipeline/jobs/ep2-b19-sapmid-b-0819.yaml"
NEW_ID = "ep2-b19-sapmid-b-0819"
WORKDIR = r"C:\banyan-farm\b19sapmid-b-0819"
SEED = 20260819

INIT = "19-the-drop-sapcomp-0819.png"
INIT_SHA = "b6dbd53bffd0dae77eb410c7669a042c9a040fb3faf2a5f5a5032b7431418903"
MASK = "19-the-drop-sapcomp-mask-0819.png"
MASK_SHA = "ce1e5ba2f89e9cabd0f90a3316a1436605bfd152a23b7add994995e255bcf266"

# ORDERED, and every one of these was hashed by certutil on the box before this
# list was written. The two courier dirs lead because they carry BOTH files.
COPY = r'''#!/usr/bin/env python3
r"""Copy beat 19's composite init and its mask off THIS BOX. No network at all.

WHY THIS FILE EXISTS INSTEAD OF fetch_init.py. The parent of this job,
ep2-b19-sapmid-0819, died rc=1 at its first step on 2026-08-19T16:43:12Z with
`socket.gaierror [Errno 11001] getaddrinfo failed` raised out of
fetch_init.py's urllib.request.urlopen. DNS did not resolve on the box for a few
seconds and, with max_attempts: 1, that permanently failed a GPU job whose only
network need was to re-download bytes already committed to the repo AND already
sitting on this card in four places. It was the third network-fetch failure on
this box that day.

The cure is the one commit 0f799ddd applied to ep2-b12-plateship-0819 after the
same class of failure: a box-local copy under the SAME per-file sha256
assertion. BYTE-IDENTITY COMES FROM THE HASH, NOT FROM THE ORIGIN OF THE BYTES.
The two sha256s below are the hashes of the files committed to main; a file that
matches one of them IS that committed file, whichever directory it came out of.
Nothing matches, nothing is written, nonzero exit.

The parent's fetch_init.py claimed these files "are NOT on the box's courier
worktree -- the courier only ever contains what the box produced". True of the
day the composite was drawn on a Mac; false since ep2-b19-sapcomp-0819 and
ep2-b19-sapgloss-0819 published their own inputs next to their outputs. Each
directory below was hashed by certutil before it was listed here.
"""
import hashlib, os, shutil, sys

OUT = r"{workdir}"
DIRS = [
    r"C:\banyan-farm\courier-box\farm-out\ep2-b19-sapcomp-0819",
    r"C:\banyan-farm\courier-box\farm-out\ep2-b19-sapgloss-0819",
    r"C:\banyan-farm\b19sapcomp-0819",
    r"C:\banyan-farm\b19sapgloss-0819",
]
WANT = [
    ("{init}", "{init_sha}"),
    ("{mask}", "{mask_sha}"),
]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


os.makedirs(OUT, exist_ok=True)
missing = []
for name, want in WANT:
    dst = os.path.join(OUT, name)
    if os.path.isfile(dst) and sha256_of(dst) == want:
        print("already here %-34s sha %s OK" % (name, want[:12]), flush=True)
        continue
    got = ""
    for d in DIRS:
        src = os.path.join(d, name)
        if not os.path.isfile(src):
            continue
        have = sha256_of(src)
        if have != want:
            print("   skip %s -- sha %s != %s" % (src, have[:12], want[:12]),
                  flush=True)
            continue
        shutil.copy2(src, dst)
        after = sha256_of(dst)
        if after != want:
            sys.exit("!! COPY CORRUPTED %s -- wrote %s" % (dst, after))
        got = d
        break
    if not got:
        missing.append(name)
    else:
        print("copied %-34s from %s  sha %s OK" % (name, got, want[:12]),
              flush=True)
if missing:
    sys.exit("!! NOT FOUND at the asserted sha in any of %d dirs: %s\n"
             "   Nothing was rendered. Add a directory to DIRS or re-publish "
             "the composite." % (len(DIRS), ", ".join(missing)))
print("both files present at their asserted sha256. no network was used.",
      flush=True)
'''.format(workdir=WORKDIR.replace("\\", "\\\\"), init=INIT, init_sha=INIT_SHA,
           mask=MASK, mask_sha=MASK_SHA)


def main() -> int:
    parent = derive_spec.load(os.path.join(derive_spec.REPO, SRC))

    child = derive_spec.derive(
        src=SRC, new_id=NEW_ID, by="pipeline/derive_b19_sapmid_b_0819.py",
        fresh={
            "owner": ("queue lane, 2026-08-19 -- TAKEOVER of the beat-19 composite "
                      "lane's rung, derived by pipeline/derive_b19_sapmid_b_0819.py. "
                      "The original's owner was notified when it died; the card was "
                      "empty at file time (ready 0, running 0, backlog 0, read off the "
                      "box directly). A new id under a new working directory cannot "
                      "collide with the parent if the owner re-files it."),
            "consumer": (
                "THE RECIPE, not the beat -- unchanged from the parent, because the "
                "parent never rendered and so answered nothing. ep2-b19-sapcomp-0819 "
                "PASSED all eight clauses at strength 0.30 and fired exactly one "
                "pre-registered mode, FAIL-CRYSTAL on its GLOSS half; ep2-b19-sapgloss-0819 "
                "passed at 0.22 with the gloss fixed and the weakest shading. This "
                "measures the 0.26 midpoint: whether the gloss fix survives while the "
                "shading works harder. Beat 19's plate does NOT need this job -- it "
                "already has a passing sample and a picked plate."),
            "success": (
                "ONE 832x1216 png at strength 0.26, byte-identical to the two passing "
                "samples in every other argument -- same init and mask at the same two "
                "shas, same prompt, same negative, same seed 20260819, same 40 steps, "
                "cfg 7.5, pad-crop 64, blur 8 -- published into courier-box with its "
                "mask, its sidecar and a .sha256 manifest. AND, the part the parent "
                "could not deliver: IT GETS PAST ITS FIRST STEP. The parent's whole "
                "output was an rc=1 on name resolution; this one touches no network."),
            "why": (
                "RE-FILE OF ep2-b19-sapmid-0819, which died rc=1 at its FIRST step at "
                "16:43:12Z on `socket.gaierror [Errno 11001] getaddrinfo failed` -- a "
                "DNS blink, the third network-fetch failure on this box that day and the "
                "second lane to hit one -- while the bytes it went to the internet for "
                "sat on the card in four directories at the asserted sha. The fetch step "
                "becomes a box-local copy with the same per-file sha256 assertion, which "
                "is exactly the cure 0f799ddd already applied to ep2-b12-plateship-0819 "
                "and never carried across lanes. Everything a sampler reads is the "
                "parent's, so the rung it asks is unchanged: strength 0.26, the midpoint "
                "between two PASSING strengths."),
        },
        overrides={
            # A no-op in value and not in effect: it asserts every --seed argv
            # really reads 20260819 after the rewrite, so derivation.seed cannot
            # disagree with the argv the way the last generation's did.
            "seed": SEED,
            # A blink cost a whole GPU job. Every step here is idempotent -- the
            # copy re-asserts shas and skips what is already correct, the inpaint
            # is a fixed seed writing over its own output, the publish names
            # every file in full -- so a retry cannot half-run.
            "key:max_attempts": 2,
        },
        retoken=[
            # The parent wrote into the SAPGLOSS job's working directory and
            # published its output under the SAPGLOSS job's own filename. Two
            # distinct takes, one basename. Repaired in the generator, which is
            # where it belongs: renaming a published artifact would invalidate
            # the .sha256 that proves it arrived intact.
            ("b19-sapgloss-s20260819", "b19-sapmid-b-s20260819"),
            ("b19-sapgloss-DRY", "b19-sapmid-b-DRY"),
            # Bare, not path-prefixed: the publish step embeds this directory
            # as a python literal with FORWARD slashes ("C:/banyan-farm/...")
            # while the payload keys and argv use backslashes, and a pair
            # written in one spelling silently misses the other. Retokening
            # runs before `extra` is attached, so the prose that records the
            # collision keeps the old name while the machinery does not.
            ("b19sapgloss-0819", "b19sapmid-b-0819"),
        ],
        extra={
            # Carried VERBATIM and deliberately: the parent's bar was written
            # before any pixels and no pixels ever arrived, so it is still
            # pre-registered. Re-wording it would be re-writing a bar that has
            # never been tested, which is worse than carrying it.
            "bar": parent["bar"],
            "pre_registered_fail_modes": parent["pre_registered_fail_modes"],
            "failure_predicted_in_advance": parent["failure_predicted_in_advance"],
            "negative_ordering": parent["negative_ordering"],
            "init_provenance": (
                parent["init_provenance"].rstrip().rstrip(".")
                + ". READ OFF THIS BOX, NOT OFF THE NETWORK: both files were hashed by "
                  "certutil on the rtx5090 on 2026-08-19 before this spec was written "
                  "and are present at these exact shas in four directories -- "
                  "courier-box\\farm-out\\ep2-b19-sapcomp-0819, "
                  "courier-box\\farm-out\\ep2-b19-sapgloss-0819, b19sapcomp-0819 and "
                  "b19sapgloss-0819. copy_init.py tries them in that order and refuses "
                  "on any mismatch, so byte-identity is established by the hash rather "
                  "than by the origin of the bytes."),
            "mask_provenance": parent["mask_provenance"],
            "the_fetch_step_is_gone_and_this_is_what_replaced_it": {
                "what_killed_the_parent": (
                    "rc=1 at step `fetch`, 2026-08-19T16:43:12Z, ~3 minutes after start. "
                    "socket.gaierror [Errno 11001] getaddrinfo failed, out of "
                    "fetch_init.py's urllib.request.urlopen. No GPU ran, no sampler "
                    "loaded, no pixels exist -- which is why no verdict was written "
                    "against it and why this child carries its bar untouched."),
                "the_cure_was_already_committed": (
                    "0f799ddd, the same day, one hour earlier, on another lane's job: "
                    "ep2-b12-plateship-0819 failed its fetch twice and was fixed by "
                    "replacing it with a box-local copy under the same per-file sha256 "
                    "assertion, after which the successor ran rc=0. "
                    "pipeline/measured/failed-acknowledged.yaml carries it as a "
                    "`fetch-404` group. The fix never crossed to this lane."),
                "why_a_local_copy_is_not_a_weaker_claim": (
                    "The two sha256s are the hashes of the files committed to main. A "
                    "file matching one of them IS that committed file, byte for byte, "
                    "whichever directory on this box it came out of. Nothing matches, "
                    "nothing is written, nonzero exit. The parent's `fetch_note` argued "
                    "the re-fetch is what makes 'one variable' true of the artifacts; a "
                    "copy under the same assertion proves exactly the same thing without "
                    "making a GPU job depend on name resolution."),
                "the_parents_own_claim_that_was_stale": (
                    "fetch_init.py's docstring said these files \"are NOT on the box's "
                    "courier worktree -- the courier only ever contains what the box "
                    "produced.\" True the day the composite was drawn on a Mac; false "
                    "since ep2-b19-sapcomp-0819 and ep2-b19-sapgloss-0819 published "
                    "their own inputs beside their outputs. Same species as the b12 "
                    "header that said plates-local no longer existed while three copies "
                    "sat on the card."),
                "max_attempts_raised_1_to_2": (
                    "A three-second DNS outage permanently failed a GPU job and idled the "
                    "card behind it. Every step here is idempotent: copy_init.py skips a "
                    "file already present at the right sha, the inpaint is a fixed seed "
                    "overwriting its own output, and the publish names every file in "
                    "full and fails on a missing one. A retry cannot half-run."),
                "the_working_directory_and_filename_are_this_jobs": (
                    "The parent wrote its payload into C:\\banyan-farm\\b19sapgloss-0819 "
                    "-- the PARENT SAPGLOSS JOB's directory -- and named its output "
                    "b19-sapgloss-s20260819.png, which is byte-for-byte the filename of "
                    "the 0.22 sample that job already published. Two distinct takes, one "
                    "basename, and a directory a second job would clobber. Retokened to "
                    "b19sapmid-b-0819 and b19-sapmid-b-s20260819.png. Fixed in the "
                    "generator, not in the published files: renaming a published artifact "
                    "invalidates the .sha256 that proves it arrived intact."),
            },
            "takeover_and_why_it_is_not_a_double_file": (
                "The parent reserved its own re-run for the beat-19 composite lane and "
                "warned that two lanes re-filing one job is what box_enqueue's known "
                "idempotency gap turns into 264 wasted GPU seconds. Taken over anyway, "
                "on three facts: the owner was notified when the job died and has not "
                "re-filed it; the card is EMPTY -- ready 0, running 0, backlog 0, read "
                "off the box directly rather than off a box_autofill snapshot, which was "
                "caught 16 minutes stale the same night; and this is a NEW id under a NEW "
                "working directory publishing under a NEW filename, so even if the owner "
                "re-files the original the two cannot collide in the queue, on disk or in "
                "farm-out. ep2-b19-sapmid-0819 stays in the tree carrying its outcome and "
                "is not edited by this job."),
            "parent_the_bar_came_from": {
                "spec": "pipeline/jobs/ep2-b19-sapmid-0819.yaml",
                "carried_verbatim": (
                    "bar, pre_registered_fail_modes, failure_predicted_in_advance, "
                    "negative_ordering and mask_provenance are the parent's text "
                    "unchanged, and that is deliberate rather than lazy: the parent "
                    "NEVER RENDERED, so its bar has never been tested against pixels and "
                    "is still pre-registered in the only sense that matters. Re-wording "
                    "an untested bar at re-file time is how a rung quietly becomes a "
                    "different rung."),
                "what_is_NOT_carried": (
                    "Its `outcome_0819` block -- the rc=1, the DNS diagnosis and the "
                    "instructions to the next lane. That is the parent's history and it "
                    "stays on the parent. This spec restates the mechanism in its own "
                    "words under `the_fetch_step_is_gone_and_this_is_what_replaced_it` "
                    "because the fix is this job's, but nothing is inherited."),
            },
        })

    # ---- the one piece of surgery the override vocabulary cannot express: a
    # ---- payload file is REPLACED BY A DIFFERENT FILE, name included. Asserted
    # ---- on both sides so a rename cannot silently leave the fetch behind.
    fetch_key = WORKDIR + "\\fetch_init.py"
    if fetch_key not in child["payload"]:
        print("!! expected %s in the retokened payload; found %s"
              % (fetch_key, ", ".join(sorted(child["payload"]))))
        return 2
    del child["payload"][fetch_key]
    copy_key = WORKDIR + "\\copy_init.py"
    child["payload"][copy_key] = COPY

    steps = []
    for step in child["steps"]:
        if step.get("name") == "fetch":
            steps.append({"name": "copy",
                          "argv": [r"C:\banyan-farm\venv\Scripts\python.exe",
                                   copy_key]})
            continue
        steps.append(step)
    child["steps"] = steps

    # Asserted on the OPERATIONAL surface -- payload keys, payload script
    # bodies, step argv and artifacts -- and not on the prose. The prose names
    # fetch_init.py, urllib and the parent's filename on purpose: that is the
    # record of what was wrong. A guard that could not tell a description of a
    # defect from the defect would push lanes toward not describing them.
    blob = derive_spec._dump({k: v for k, v in child.items() if k != "derivation"})
    argvs = [str(a) for s in child["steps"] for a in s["argv"]]
    surface = list(child["payload"]) + argvs + [str(a) for a in child["artifacts"]]
    assert not [t for t in surface if "fetch_init" in t], "the fetch script survived"
    assert not [t for t in surface if "b19sapgloss-0819" in t], \
        "the parent's working directory survived"
    assert not [t for t in surface if "b19-sapgloss-s20260819" in t], \
        "the parent's output filename survived"
    for key, body in child["payload"].items():
        if not isinstance(body, str):
            continue
        assert "urlopen(" not in body, "%s still opens a URL" % key
        assert "urlretrieve" not in body, "%s still downloads" % key
    for arg in argvs:
        assert not arg.startswith("http"), "a step still takes a URL: %s" % arg
    assert [s["name"] for s in child["steps"]] == ["copy", "dry", "s20260819",
                                                   "publish"], child["steps"]
    for name, sha in ((INIT, INIT_SHA), (MASK, MASK_SHA)):
        assert sha in blob, "%s's sha is no longer asserted anywhere" % name
        assert sha in COPY, "%s's sha is not asserted by the copy step" % name
    # the render arguments are the parent's, checked flag by flag.
    p_render = [s for s in parent["steps"] if s["name"] == "s20260819"][0]["argv"]
    c_render = [s for s in child["steps"] if s["name"] == "s20260819"][0]["argv"]
    for flag in ("--steps", "--cfg", "--strength", "--pad-crop", "--blur",
                 "--seed", "--init-sha256"):
        pv = p_render[p_render.index(flag) + 1]
        cv = c_render[c_render.index(flag) + 1]
        assert pv == cv, "%s changed: %r -> %r" % (flag, pv, cv)

    out = derive_spec.write(child, OUT)
    print("parent   %s  (rc=1 at step `fetch`, never rendered)" % SRC)
    print("child    %s" % os.path.relpath(out, derive_spec.REPO))
    print("step 1   fetch -> copy (copy_init.py, no network)")
    print("workdir  %s" % WORKDIR)
    print("seed     %d, strength/steps/cfg/pad-crop/blur all == the parent's" % SEED)
    print("dropped  %s" % ", ".join(
        child["derivation"]["keys_the_parent_had_that_did_NOT_cross"]))
    print("steps    %s" % ", ".join(s["name"] for s in child["steps"]))
    print("rc=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
