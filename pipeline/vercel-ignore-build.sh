#!/usr/bin/env bash
# The Vercel build guard — decides whether a push is worth a build at all.
#
# WHY THIS EXISTS. In under a month the old Vercel project billed >$100 across
# 500+ build hours, and almost none of it was the site changing. `farm_worker.py`
# force-pushes a heartbeat commit to its own `farm-results-*` branch every ~5
# minutes for the whole length of a render task; every one of those was a Vercel
# deployment, each running the full pip install + build_site.py. ~288 builds a day
# to publish nothing. Dad removed the project from his account on 2026-08-07. This
# file, plus the `git` block in vercel.json, is the repo-side half of making sure a
# future connection cannot repeat it — the guard lands BEFORE the project exists,
# so the first push to a new project is already governed.
#
# CONTRACT (Vercel "Ignored Build Step", and it is backwards on purpose):
#     exit 0  -> SKIP the build
#     exit 1  -> RUN the build
# https://vercel.com/docs/project-configuration/vercel-json#ignorecommand
#
# WHAT THIS CANNOT DO — read this before trusting it.
#   * A skipped build is still a *deployment event*. Vercel creates the record,
#     clones the repo (shallow, --depth=10) and runs this script before deciding.
#     That is seconds of a build slot, not the ~1-2 minutes of a real build, but it
#     is not zero and it is not invisible. Vercel's own docs are explicit that an
#     Ignored-Build-Step skip "still counts toward your concurrent build limits",
#     unlike its automatic monorepo skip.
#   * Therefore this is the SECOND line of defence. The first two are:
#       1. `git.deploymentEnabled` in vercel.json — evaluated by Vercel BEFORE a
#          deployment is created, so a matching branch produces no event at all.
#          That is what actually kills the farm-branch flood.
#       2. Project settings on Vercel's side: Production Branch = `main`, and
#          preview deployments OFF for all other branches. Settings win where they
#          disagree with intent, and they are the only layer that governs a branch
#          whose checked-out vercel.json is stale or missing. Those are clicks in
#          the dashboard, not code, and they belong to the human doing the move.
#     If all three are set, the farm branches cost nothing. If only this script is
#     set, they cost a few seconds each — better than $100/month, still not right.
#
# SELF-HEALING, which is why a wrong SKIP is survivable: build_site.py deletes
# _site/ and regenerates every page from the genomes on each run. There is no
# incremental state. A build this script wrongly skips is not lost work — the next
# build that does run publishes those changes too. Late, never missing. That is the
# reason the path list below can be strict without being dangerous.

set -u

SKIP=0   # named, because `exit 0` reads like success and here it means "don't"
BUILD=1

say()   { echo "[build-guard] $*"; }
skip()  { say "SKIP — $*"; exit "$SKIP"; }
build() { say "BUILD — $*"; exit "$BUILD"; }

# ---------------------------------------------------------------------------
# Gate 1 — environment. Only production deployments may build.
# ---------------------------------------------------------------------------
# Preview deployments should be OFF in project settings; this catches the case
# where they are not. Skipping a preview can never freeze banyan.city, because
# banyan.city is served by the production deployment only — so unlike the branch
# check below, this one is safe to fail closed.
if [ -n "${VERCEL_ENV:-}" ] && [ "${VERCEL_ENV}" != "production" ]; then
  skip "VERCEL_ENV=${VERCEL_ENV} — this project publishes production only"
fi

# ---------------------------------------------------------------------------
# Gate 2 — branch. Only `main` is the site.
# ---------------------------------------------------------------------------
# Belt to git.deploymentEnabled's braces. Named branch families first so the log
# line says WHY, then the catch-all.
REF="${VERCEL_GIT_COMMIT_REF:-}"
case "$REF" in
  farm-results-*)
    # the courier branches: farm_worker.py's heartbeat/telemetry, force-pushed
    # every ~5 min. Never site content — the worker syncs its files FROM main.
    skip "branch '$REF' is a render-farm courier branch, never site content" ;;
  runpod-results|rescue-diag-history|tmp/*|claude/*)
    skip "branch '$REF' is a working branch, not the site" ;;
  main)
    : ;;
  "")
    # VERCEL_GIT_COMMIT_REF is empty when "Automatically expose System
    # Environment Variables" is off, or on a CLI/hook deploy with no branch.
    # Fail OPEN: git.deploymentEnabled already refuses non-main pushes at the
    # event layer, so the cost case is covered without this check, and a silent
    # skip here would freeze the live site with nothing in the log to explain it.
    say "warn: VERCEL_GIT_COMMIT_REF is empty — cannot confirm the branch" ;;
  *)
    skip "branch '$REF' is not main" ;;
esac

# ---------------------------------------------------------------------------
# Gate 3 — did this push actually change anything the site is built from?
# ---------------------------------------------------------------------------
# Every path below is a real input of `python3 pipeline/build_site.py`, read out
# of the code rather than guessed. Line references are to the files as of
# 2026-08-08. If you add an input, add it here — and test_pipeline.py's
# test_vercel_build_guard_covers_every_site_input() fails the build if a path in
# this list stops existing, which is the rename that would otherwise silently
# un-guard a directory.
SITE_INPUTS=(
  # --- the content ---------------------------------------------------------
  # build_site.load_genome() walks every genome: tree.yaml, lineage.yaml,
  # node.md, leaves/*.yaml (+ the .html/.mp4 they name), sap/{reactions,
  # summary,screening}.yaml, stills/, takes/{stills,clips}/, clips/, shots.md,
  # motion.yaml. One directory covers all of it and there is no sub-path worth
  # excluding: everything under genomes/ reaches a page.
  genomes
  # cuts/cuts.yaml builds the unlisted /review/ area (D17); the mp4s beside it
  # are the one place media is committed. build_site.py:1676.
  cuts
  # review/<name>/index.html — hand-authored pages published into the same
  # unlisted area (build_site.review_page_dirs). The approvals page lives here,
  # and on 2026-08-10 it 404'd for a whole afternoon; a guard that skipped the
  # push which fixes that would put the same 404 on banyan.city instead.
  #
  # IT IS THE WHOLE DIRECTORY AND THAT COSTS BUILDS, deliberately, same trade as
  # pulse-series.json below. review/ is also the render lanes' scratch yard, so
  # a commit of round-N contact frames now triggers a site build that publishes
  # nothing. Two things keep it small: only TRACKED files can trigger anything
  # (.gitignore:57 swallows every mp4 under review/, which is the bulk of it),
  # and a handful of pushes a day is not the 288 this guard was written against.
  # A narrower pathspec cannot be written here: the builder discovers pages by
  # scanning the directory, so the directory is the input.
  review
  # copied wholesale into _site/lab/ when present. build_site.py:2077-2079.
  lab
  # assets/og.png is the social-share image every page's <meta> points at.
  # build_site.py:2084. Directory, not the file, so a second asset is covered.
  assets
  # the spend figures on the status page. build_status.py:212.
  ledger/render-spend.csv

  # --- the generator -------------------------------------------------------
  # build_site.py is the whole static-site generator; the rest are what it
  # imports or delegates to, directly or transitively:
  #   build_status  (2073)  status-page data from repo files
  #   build_sim     (2075)  composes the status page
  #   build_shotboard (2110) the per-node shot boards, D11
  #   site_theme           the one palette, imported by all four
  #   licence_gate         publishable()/public_licence() — the licence gate
  #   generate_shots       parse_shots(), used by build_status + build_shotboard
  #   sd_prompt            imported by build_shotboard for prompt display
  pipeline/build_site.py
  pipeline/build_status.py
  pipeline/build_sim.py
  pipeline/build_shotboard.py
  # build_pulse (build_site.py:3065) draws /pulse — the queue and the render
  # box's vitals over time — from the cache below.
  pipeline/build_pulse.py
  # build_queue (build_site.py:3255-3256) draws /queue — every render as a
  # browsable gallery, plus queue-data.json and queue-detail.json. MISSING FROM
  # THIS LIST UNTIL 2026-08-18, and missing for the same reason episode_eta.py
  # was: build_site imports it INSIDE the function that calls it, so the
  # column-0 sibling-import walk in test_pipeline never demanded it and nothing
  # noticed. A push that changed only this file would skip the build and leave
  # banyan.city serving a stale /queue — which is exactly what it is: one of the
  # four builders qa_local.py runs.
  pipeline/build_queue.py
  pipeline/site_theme.py
  # the /status page's inline-SVG charts — the sapling tree and the render
  # box's per-day work bars — and the ONE definition of what each beat state
  # is coloured, which build_sim's ETA bars read too. Change it and the page's
  # pictures change with no other file touched, exactly like site_theme.py.
  pipeline/charts.py
  # the per-beat receipts behind /status's episode strip: which take is in the
  # cut, its sha256 recomputed at build time, the verdict quoted out of its job
  # spec, and the mid-frame beside it. build_sim imports it at column 0, so this
  # would have been demanded anyway — listed with a reason because change it and
  # twenty-one folds on the founder's own progress panel change with no other
  # file touched, which is the same argument site_theme.py and charts.py carry.
  pipeline/proof_receipts.py
  pipeline/licence_gate.py
  # every github.com / raw.githubusercontent link the site emits is built from
  # the slug this resolves. It is a build input in the strictest sense: change
  # it and every one of those hrefs changes, with no other file touched.
  pipeline/repo_slug.py
  # the `<meta name="build-commit">` every page carries, so the deploy can state
  # which commit it is. Listed for the same reason as repo_slug.py above: change
  # it and every page's bytes change with no other file touched — and a guard
  # that skipped that push would leave banyan.city stamped with a stale commit,
  # which is the exact lie the stamp exists to prevent.
  pipeline/build_commit.py
  # the /status ETA cards and their glance cell. build_sim imports episode_eta
  # INSIDE the function that reads it, so the sibling-import walk in
  # test_pipeline (which only follows column-0 imports, to stay out of the paid
  # render path) does not demand these two — and would not have noticed them
  # missing. They are listed by hand for the reason the measured/ directory is:
  # a push that changed only these would skip the build, and banyan.city would
  # keep publishing yesterday's hours from a file that had already moved.
  # box_job_minutes comes with it — episode_eta imports it for the job KINDS
  # table, so the two are one input.
  pipeline/episode_eta.py
  pipeline/box_job_minutes.py
  pipeline/generate_shots.py
  pipeline/sd_prompt.py
  # read at build time for the founder's inbox on the status page.
  # build_status.py:227.
  pipeline/pending-founder.yaml
  # the dated measurements the status page's footprint section prints
  # (render-bandwidth.yaml, local-disk.yaml — build_sim.render_bandwidth() /
  # local_disk()). Found missing by the 2026-08-11 status audit: a push that
  # only refreshed these never rebuilt the live page, so "measurements with
  # dates" aged invisibly in production while claiming freshness.
  pipeline/measured
  # the render queue the status page reports. build_sim.py:282.
  pipeline/farm-queue.yaml
  # the only history the /pulse graphs have. build_pulse.py:CACHE.
  #
  # THIS ONE COSTS A BUILD EVERY TIME IT IS REFRESHED, and that is the point of
  # listing it rather than an oversight: it is a genuine input, so a guard that
  # omitted it would leave banyan.city serving yesterday's graphs while claiming
  # today's. The control is cadence, not the allowlist — `pulse_series.py` says
  # so at its top. Do not put it on a five-minute timer; that is the shape of
  # the spend this whole guard exists to prevent.
  pipeline/pulse-series.json
  # /trials/ — README.md, prompts.md, scores.yaml and outputs/*/*.mp4.
  # build_site.py:1547, 1623-1624, 2095.
  pipeline/t3-trials

  # --- prose the site renders verbatim ------------------------------------
  # city.html inlines these three (build_site.py:1505); machine.html inlines
  # MACHINE.md (1526). Every OTHER root .md — README, STATE, CLAUDE, DECISIONS,
  # SITE, PROMISE's neighbours — is repo documentation that no page reads, and
  # deliberately NOT listed: STATE.md alone is appended to several times a day.
  PROMISE.md
  GUIDELINES.md
  VOCABULARY.md
  MACHINE.md

  # --- the build configuration itself -------------------------------------
  # so that changing the build command, or this guard, can still deploy.
  vercel.json
  pipeline/vercel-ignore-build.sh
)

# Pick the baseline to diff against.
#
# VERCEL_GIT_PREVIOUS_SHA is the commit of the last *successful* deployment on
# this branch, and Vercel exposes it only when an Ignored Build Step exists. It
# is the correct baseline for two reasons a plain HEAD^ gets wrong:
#   - a push carrying several commits (HEAD^ would see only the last one), and
#   - a run of skipped builds (the baseline does not advance past a skip, so the
#     changes accumulate instead of being stranded behind one).
# It is empty on the first deployment, and it has a standing report of being
# empty for other reasons, so both fallbacks below are load-bearing.
BASE=""
PREV="${VERCEL_GIT_PREVIOUS_SHA:-}"
if [ -n "$PREV" ]; then
  if git cat-file -e "${PREV}^{commit}" 2>/dev/null; then
    BASE="$PREV"
    say "baseline: last deployed commit ${PREV:0:12}"
  else
    # Vercel shallow-clones with --depth=10. An unreachable baseline means ten
    # or more commits since the last successful deploy — we cannot see the range,
    # so we cannot prove nothing changed. Build.
    build "last deployed commit ${PREV:0:12} is outside the shallow clone (>10 commits behind)"
  fi
elif git rev-parse --verify --quiet "HEAD^" >/dev/null 2>&1; then
  # No baseline from Vercel. HEAD^ is the next best window: it is correct for a
  # single-commit push, which is what a farm heartbeat always is and what most
  # pushes to main are. It can under-detect a multi-commit push — survivable,
  # per the self-healing note at the top of this file.
  BASE="HEAD^"
  say "warn: VERCEL_GIT_PREVIOUS_SHA empty — falling back to HEAD^ (one-commit window)"
else
  build "no parent commit reachable — first deployment, or the bottom of the clone"
fi

if git diff --quiet "$BASE" HEAD -- "${SITE_INPUTS[@]}"; then
  skip "no site input changed between $BASE and HEAD"
fi

say "changed site inputs:"
git diff --name-only "$BASE" HEAD -- "${SITE_INPUTS[@]}" | sed 's/^/[build-guard]   /'
build "site inputs changed"
