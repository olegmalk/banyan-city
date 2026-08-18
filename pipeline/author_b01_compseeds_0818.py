"""Clone the PROVEN composite recipe across fresh seeds — production, not a test.

WHY THIS IS NOT ANOTHER RUNG. The wording route to a two-leaf count is closed:
five prompt wordings scored 0-3 of 16 on beat 01's grid and the cells that
passed were the same reference-driven cells in every one of them
(review/ep2-picks/count-levers-0817-verdict.yaml). Composite-then-inpaint is
the route that works — with a composited init the thing you want is not a
sample from the model, and it returned exact two-leaf count 8 of 8 across two
independent inits with zero GPU spent on the count itself.

So this asks no question. It runs the SAME recipe, at the SAME settings, on the
SAME two committed composites, at seeds nobody has drawn yet, to produce
CANDIDATE PLATES. The consumer is the pick: beat 01 needs a frame somebody can
actually cut, choosing between takes is the steward's job under the founder's
own boundary, and a pick made from eight frames is a worse pick than one made
from thirty-two.

WHAT IS HELD IDENTICAL, because changing any of it would turn production back
into an experiment: the init and its sha256 pin, the ellipse, the prompt and
negative files, steps 40, cfg 7.5, strength 0.30, pad-crop 64, blur 8. ONLY the
seed and the output filename move. `--init-sha256` is the guarantee that matters
— if the composite on the box is not byte-for-byte the one these seeds were
authorised against, the step refuses rather than quietly restyling a different
picture.

NOT A BATCH OF AN UNAPPROVED RECIPE. The one-sample rule bites on a recipe
change; there is none here. The sample was 8 of 8 and it is already scored.

$0, local card, no provider. Beat 01 is a STILL PLATE on an approved node.
"""
import copy
import ntpath
import os
import sys

import yaml

SRC = "pipeline/jobs/ep2-b01-leafcomp-inpaint-0817.yaml"
# Two composites exist on the box and both are already pinned by sha in a
# committed spec. s1 is the one the source job ran; s3 is its independent twin,
# and running both is what keeps the candidate set from being one init's taste.
COMPS = {
    "s1": "ep2-b01-leafcomp-inpaint-0817.yaml",
    "s3": "ep2-b01-leafcomp-s3-0817.yaml",
}
# Fresh seeds, four to a job, none of them drawn before on this recipe. Grouped
# so a job is ~7 minutes: small enough that a crash costs one job, big enough
# that the queue is not mostly overhead.
# ROUND 2. Seeds 20260901-20260912 were drawn on 2026-08-17 and their 24 frames
# exist -- the jobs failed on a path bug, not on the render, and the frames were
# recovered out of C:\Windows\System32 into farm-out by hand. Re-running them
# would spend the card to redraw pictures we already have.
SEED_GROUPS = [
    [20260913, 20260914, 20260915, 20260916],
    [20260917, 20260918, 20260919, 20260920],
    [20260921, 20260922, 20260923, 20260924],
]
GROUP_OFFSET = 3   # so ids continue g4, g5, g6 rather than colliding with round 1


def seed_steps(src_steps):
    """The per-seed steps of the source job, and the non-seed ones around them."""
    seeds = [s for s in src_steps if s["name"].startswith("s2026")]
    if not seeds:
        sys.exit("!! no seed steps found in the source spec. Refusing.")
    return seeds[0]


def main() -> None:
    written = []
    for comp_tag, src_name in COMPS.items():
        path = os.path.join("pipeline/jobs", src_name)
        if not os.path.exists(path):
            sys.exit("!! source spec missing: %s" % path)
        src = yaml.safe_load(open(path, encoding="utf-8"))
        template = seed_steps(src["steps"])
        pub = [s for s in src["steps"] if s["name"] == "publish"]
        comp = [s for s in src["steps"] if s["name"] == "comp"]

        for gi, group in enumerate(SEED_GROUPS, 1 + GROUP_OFFSET):
            job_id = "ep2-b01-compseed-%s-g%d-0818" % (comp_tag, gi)
            out_path = "pipeline/jobs/%s.yaml" % job_id
            if os.path.exists(out_path):
                print("skip (exists):", out_path)
                continue

            # EACH JOB GETS ITS OWN DIRECTORY, and this is not tidiness.
            # `payload:` maps absolute box paths to file CONTENTS and box_enqueue
            # writes them at ENQUEUE time, not at run time. Six queued jobs all
            # naming C:\banyan-farm\leafcount-0817\inpaint_fruit.py would each
            # overwrite the previous one's inputs before any of them ran, and the
            # box would render one thing under six names. The enqueue guard
            # refuses exactly this, and it refused these six on the first attempt
            # -- the fix is a private directory per job, not a louder guard.
            workdir = r"C:\banyan-farm\leafcount-0818-%s-g%d" % (comp_tag, gi)

            def relocate(obj):
                """Move every leafcount-0817 path onto this job's own directory.

                Deliberately narrow: it rewrites that one directory token and
                nothing else, so the comp step's --init, which reads a published
                frame out of courier-box\\farm-out, is left pointing where it
                belongs. A blanket path rewrite here would silently repoint the
                source image and the job would composite the wrong picture.
                """
                if isinstance(obj, str):
                    # BOTH SPELLINGS. The steps use backslashes, but the publish
                    # step is an inline python program whose paths are written
                    # with forward slashes. Rewriting only the backslash form
                    # left publish pointing at the SOURCE job's directory, so it
                    # copied that job's frames into this job's farm-out folder,
                    # printed "published 14 of 14" and exited 0. It published a
                    # different job's work under this job's name.
                    return (obj.replace(r"C:\banyan-farm\leafcount-0817", workdir)
                               .replace("C:/banyan-farm/leafcount-0817",
                                        workdir.replace("\\", "/")))
                if isinstance(obj, list):
                    return [relocate(v) for v in obj]
                if isinstance(obj, dict):
                    return {relocate(k): relocate(v) for k, v in obj.items()}
                return obj

            steps = []
            # The comp step is carried so the composite is REBUILT and re-pinned
            # rather than assumed present. A job that depends on a file another
            # job happened to leave behind is a job that passes until the day
            # somebody cleans the directory.
            if comp:
                steps.append(copy.deepcopy(comp[0]))
            for seed in group:
                st = copy.deepcopy(template)
                st["name"] = "s%d" % seed
                argv = st["argv"]
                for i, a in enumerate(argv):
                    if a == "--seed":
                        argv[i + 1] = str(seed)
                    elif a == "--out":
                        # ntpath, NOT os.path. These are WINDOWS paths and this
                        # script runs on a Mac, where os.path.basename() finds no
                        # "/" separator and returns THE WHOLE STRING. The old line
                        # therefore replaced the entire absolute path with a bare
                        # filename, and the box wrote 24 renders into the runner
                        # service's working directory -- C:\Windows\System32 --
                        # where the artifact check could not find them and the job
                        # failed rc=92 with every render actually complete.
                        argv[i + 1] = ntpath.join(
                            ntpath.dirname(argv[i + 1]),
                            "b01-compseed-%s-s%d.png" % (comp_tag, seed))
                    elif a == "--note":
                        argv[i + 1] = (
                            "PRODUCTION, not a rung. Proven composite recipe "
                            "(8 of 8 exact two-leaf count) at a fresh seed, to widen "
                            "the candidate set beat 01's pick is made from. No setting "
                            "differs from ep2-b01-leafcomp-inpaint-0817 except the seed.")
                steps.append(st)
            # THE PUBLISH STEP IS REGENERATED, NOT PATCHED. The source job's
            # version carries a hardcoded `names = [...]` listing ITS OWN
            # filenames (b01-leafcomp-s2026081x.png). Rewriting the directory
            # inside it is not enough: the step would look for the other job's
            # frames in this job's folder, find none, and -- because it only
            # asserts on one specific old filename -- report success over an
            # empty copy. This builds the list from the seeds actually rendered
            # and asserts on the count, so it cannot pass while publishing
            # nothing.
            names = []
            for seed in group:
                base = "b01-compseed-%s-s%d" % (comp_tag, seed)
                names += [base + ".png", base + ".png.meta.yaml", base + "-mask.png"]
            wd_fwd = workdir.replace("\\", "/")
            dst_fwd = "C:/banyan-farm/courier-box/farm-out/" + job_id
            prog = (
                "import hashlib, os, shutil\n"
                "src = %r\n" % wd_fwd +
                "dst = %r\n" % dst_fwd +
                "os.makedirs(dst, exist_ok=True)\n"
                "names = %r\n" % (names,) +
                "got = []\n"
                "for n in names:\n"
                "    p = os.path.join(src, n)\n"
                "    if os.path.isfile(p):\n"
                "        shutil.copy2(p, os.path.join(dst, n)); got.append(n)\n"
                "with open(os.path.join(dst, 'SHA256SUMS.txt'), 'w', newline='\\n') as fh:\n"
                "    for n in got:\n"
                "        h = hashlib.sha256(open(os.path.join(dst, n), 'rb').read()).hexdigest()\n"
                "        fh.write('%s  %s\\n' % (h, n))\n"
                "print('published', len(got), 'of', len(names))\n"
                "raise SystemExit(0 if len(got) == len(names) else 1)\n")
            steps.append({"name": "publish",
                          "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", prog]})

            job = copy.deepcopy(src)
            job["id"] = job_id
            job["task"] = job_id
            job["steps"] = relocate(steps)
            job["payload"] = relocate(src.get("payload") or {})
            # The runner fails a job whose declared artifacts are missing, and
            # that check is the only reason last night's breakage was caught at
            # all. It is worth nothing if it names another job's files.
            job["artifacts"] = [ntpath.join(workdir, "b01-compseed-%s-s%d.png"
                                            % (comp_tag, seed)) for seed in group]
            job["est_minutes"] = 7
            job["priority"] = 40
            job["owner"] = ("count-control lane, 2026-08-18 -- production seeds off a "
                            "closed question, filed to backlog")
            job["consumer"] = (
                "The PICK for beat 01. The wording route to an exact two-leaf count is "
                "closed by evidence (five wordings, 0-3 of 16, same ref-driven cells in "
                "every one), and composite-then-inpaint already returns 8 of 8. This job "
                "asks nothing and tests nothing: it draws four more candidates at seeds "
                "nobody has run, so the frame that ships is chosen from a wide set rather "
                "than from the first eight. Choosing between takes is the steward's under "
                "the founder's own boundary; whether any of them is good enough is his.")
            job["why"] = (
                "NOTHING MOVES EXCEPT THE SEED. Init and its sha256 pin, ellipse, prompt "
                "and negative files, steps 40, cfg 7.5, strength 0.30, pad-crop 64 and "
                "blur 8 are carried from ep2-b01-leafcomp-inpaint-0817 by "
                "pipeline/author_b01_compseeds_0818.py rather than retyped. The "
                "`--init-sha256` pin is the load-bearing part: if the composite on the box "
                "is not byte-for-byte the one these settings were authorised against, the "
                "step refuses instead of restyling a different picture. The one-sample rule "
                "is not in tension with this -- it bites on a recipe CHANGE, and the recipe "
                "here is unchanged and already scored 8 of 8. $0, local card, no provider.")
            job["success"] = (
                "NOT A MEASUREMENT AND IT DECLARES SO. This job has no bar because it is "
                "not asking a question: it is drawing candidates from a recipe whose bar was "
                "already met (8 of 8 exact two-leaf count, recorded before these seeds "
                "existed). It PASSES when four PNGs and four sidecars land and the publish "
                "step's frame-count assertion holds -- that assertion keeps its teeth here, "
                "with no allow_fail over it. "
                "WHAT WOULD MAKE IT A FAILURE WORTH READING: if the composited two-leaf "
                "structure does NOT survive at these seeds, that contradicts the 8 of 8 and "
                "the recipe stops being trusted -- so the frames are still read, just not "
                "against a count bar. "
                "NOT A PICK and NOT A TASTE CALL: which frame ships is R4's; that a frame "
                "exists to choose from is what this job buys.")
            with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
                yaml.safe_dump(job, fh, sort_keys=False, allow_unicode=True, width=110)
            back = yaml.safe_load(open(out_path, encoding="utf-8"))
            if back != job:
                sys.exit("!! %s does not round-trip. Refusing." % out_path)
            seeds_in = [s["name"] for s in back["steps"] if s["name"].startswith("s2026")]
            print("wrote %s  seeds=%s  steps=%d"
                  % (out_path, ",".join(x[1:] for x in seeds_in), len(back["steps"])))
            written.append(out_path)
    print("\n%d job(s) written, %d minutes of card time"
          % (len(written), 7 * len(written)))


if __name__ == "__main__":
    main()
