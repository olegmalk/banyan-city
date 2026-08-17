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
SEED_GROUPS = [
    [20260901, 20260902, 20260903, 20260904],
    [20260905, 20260906, 20260907, 20260908],
    [20260909, 20260910, 20260911, 20260912],
]


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

        for gi, group in enumerate(SEED_GROUPS, 1):
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
                    return obj.replace(r"C:\banyan-farm\leafcount-0817", workdir)
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
                        argv[i + 1] = argv[i + 1].replace(
                            os.path.basename(argv[i + 1]),
                            "b01-compseed-%s-s%d.png" % (comp_tag, seed))
                    elif a == "--note":
                        argv[i + 1] = (
                            "PRODUCTION, not a rung. Proven composite recipe "
                            "(8 of 8 exact two-leaf count) at a fresh seed, to widen "
                            "the candidate set beat 01's pick is made from. No setting "
                            "differs from ep2-b01-leafcomp-inpaint-0817 except the seed.")
                steps.append(st)
            if pub:
                p = copy.deepcopy(pub[0])
                # Publish under this job's own id or the manifest names files it
                # never copied — a step that has already lied once in this repo.
                for i, a in enumerate(p.get("argv", [])):
                    if isinstance(a, str) and "leafcomp-inpaint-0817" in a:
                        p["argv"][i] = a.replace("ep2-b01-leafcomp-inpaint-0817", job_id)
                # The frame-count assertion keeps its teeth.
                p.pop("allow_fail", None)
                steps.append(p)

            job = copy.deepcopy(src)
            job["id"] = job_id
            job["task"] = job_id
            job["steps"] = relocate(steps)
            job["payload"] = relocate(src.get("payload") or {})
            job["artifacts"] = relocate(src.get("artifacts") or [])
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
