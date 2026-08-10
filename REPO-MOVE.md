# Moving the repo to a new GitHub account — 2026-08-10

**Founder direction (Roman, 2026-08-10 ~01:20):** *"the repo should be moved to a
different github account"* / *"current account associated with other vercel
account"*.

`olegmlkvorg` — dad's nameplate, and the GitHub identity entangled with the OLD
Vercel account — stops owning `banyan-city`. A different account takes ownership
and pairs cleanly with the NEW Vercel account (`olegmalkov2023-1685`).

> ## ✅ ANSWERED AND DONE — `<NEW_OWNER>` = **`olegmalk`**, transfer already executed
>
> Measured 2026-08-10 16:30, not assumed: `gh api repos/olegmlkvorg/banyan-city`
> resolves to **`olegmalk/banyan-city`**, and the Pages site moved with it —
> `https://olegmalk.github.io/banyan-city/` serves 200, while the old
> `https://olegmlkvorg.github.io/banyan-city/` now **404s everywhere**, root
> included. Anyone still quoting the old mirror URL is handing out a dead link;
> `README.md`, `OPERATOR.md` and `pipeline/qa_local.py` were corrected.
>
> The old path still redirects, so this Mac's `gh`, the `origin` remote (which
> still reads `olegmlkvorg`) and the box's SSH pushes keep working untouched.
>
> **What this does NOT do:** it does not reconnect Vercel. Pushes to `main`
> still produce no deployment. Publishing goes through §A0 until someone
> completes §B3 in a browser.
>
> Original question, kept for the record: *which GitHub account owns the repo?*
> The steward did not get to pick it, and did not.

Times are local (+04). Every fact below was measured on 2026-08-10, not assumed;
GitHub's transfer semantics are quoted from
<https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository>.

---

## A0. The site does NOT have to stay frozen while the move is decided — 2026-08-10 16:20

**Publishing and git-integration are two different things, and only one of them
needs a browser.** This file and `DEPLOY-BROKEN-0810.md` both read as "nothing
can ship until Roman clicks" — true of *reconnecting the repo*, false of
*getting current content onto banyan.city*. The site sat 15.8 hours stale on
that misreading.

`vercel deploy --prebuilt --prod` uploads a locally-built site straight to the
existing project. It needs no GitHub connection, creates no project, spends
nothing, and does not touch the migration. The CLI on this Mac is already
authenticated as `olegmalkov2023-1685`, so it just works:

    python3 pipeline/build_site.py            # (+ build_sim.py, build_pulse.py)
    vercel build --prod --yes
    vercel deploy --prebuilt --prod --archive=tgz --yes

**`--archive=tgz` is load-bearing, not decoration.** Without it the CLI opens
many parallel uploads for ~530 files / 482 MB and dies partway with
`FetchError: … write EPIPE` (also seen as an `EPROTO … invalid session id` TLS
abort) against `api.vercel.com/v2/files`. Measured: plain and prebuilt uploads
failed four times, at 0 B and at 120 MB. The same endpoint accepts a single file
over `curl` without complaint, so it is the CLI's concurrent-socket behaviour on
Node 25, not the network and not a size cap. `--archive=tgz` sends one stream
and succeeded first try.

The first CLI deploy must push the whole 482 MB, because files built server-side
by earlier git deploys are not in the CLI's content-addressed upload store.
Later deploys dedupe and are fast.

**This is the standing unblock.** While the repo move is pending, a push to
`main` still publishes nothing — so anything that must be visible to the founder
gets deployed with the three commands above, and `pipeline/qa_local.py` now
fails if the public site falls behind (§A1).

## A1. The gate now catches a frozen site

A stuck deploy does not go down — it serves a correct page from the past, at
`200 OK`, which is why every check we had passed for 15.8 hours.
`pipeline/qa_local.py` grew a **PUBLIC DEPLOY FRESHNESS** section that fails on
two independent signals: the deployed page's `last-modified` trailing HEAD by
more than three hours, and the Pages mirror being materially newer than
banyan.city (the mirror builds from the same repo by a different mechanism, so
if it rebuilt and the primary did not, the primary is stuck). Unreachable is a
warn, not a fail — an offline laptop must not red a local run; `--no-public`
skips the section outright.

**Correction, 2026-08-10 17:22 — both of those signals were blind, and the
section now says so instead of printing `ok`.** Vercel sets `last-modified` to
the instant the CDN edge filled its cache, not to the build time. Measured:
`/city` and `/machine`, both cold (`x-vercel-cache: MISS`, `age: 0`), returned
`last-modified` equal to their own `date` header to the second; on a later HIT
the value froze there while `age` counted up from it. So the lag was never
"how far production trails HEAD", it was "how long ago an edge refilled" —
always seconds. The mirror cross-check failed the same way from the other
direction: Pages publishes a *genuine* build time, so the mirror is always the
older of the two and the drift is always negative. **A site frozen for a day
would have printed a green `0s behind HEAD`** — the precise false green this
section was added to prevent. `qa_local.is_cache_fill_clock()` now detects the
condition (`last-modified ≈ date - age`, which holds in both cache states) and
the section reports **BLIND** rather than passing.

**This leaves the gate with no automatic staleness signal — that is honest, not
fixed.** Until a build stamp exists, judge a deploy by building `origin/main`
and diffing the bytes against the served page, or by `vercel ls`. The durable
fix is for the builders to publish the commit they were built from (a
`<meta name="build-commit">` or a `/build.json`) so the gate can compare it to
HEAD directly; that needs `build_site.py`, and is not yet done.

## A. What happened tonight, re-framed

`DEPLOY-BROKEN-0810.md` is **superseded by this file.** Its diagnosis was right;
its repair plan is **withdrawn.**

At **22:14:47** the Vercel project's GitHub repository was disconnected. Vercel's
own event log names the actor and the act:

    project-git-repository-disconnected
    "You disconnected GitHub repository olegmlkvorg/banyan-city from project banyan-city"
    principal: olegmalkov2023-1685 <olegmalkov2023@gmail.com>

That was the only non-deployment event in the project's entire history. It read
as an outage because nobody had said why. It was **migration step one** — the old
owner being unhooked ahead of the move. Nine pushes to `main` produced no
deployment; the site froze at the 21:52 build (`d395b88`) and stayed up.

So `DEPLOY-BROKEN-0810.md`'s fix — *reconnect the GitHub login as `olegmlkvorg`,
install the app on that identity, re-link `olegmlkvorg/banyan-city`* — would
undo the migration. **Do not run those steps.** That file stays in the repo as
the evidence record (the measurements are good: the 100/day Hobby cap was never
near, the CLI failure mode is proven, the push-cadence backlog is still worth
reading) with a supersession banner pointing here.

**The silver lining:** we are already disconnected. The 08-08 reconnect cost a
morning partly because of an existing wrong link that had to be unpicked. This
time the project is a clean slate — there is **no unlink step**.

---

## B. The founder's browser steps, in order

Nothing here can be done by an agent: every step is an OAuth flow or an
ownership decision against Roman's credentials. Budget ~10 minutes.

### B1 — GitHub: transfer the repository

1. As **`olegmlkvorg`**: <https://github.com/olegmlkvorg/banyan-city> →
   **Settings** → scroll to **Danger Zone** → **Transfer**.
2. New owner: **`<NEW_OWNER>`**. Type `banyan-city` to confirm.
3. Sign in as **`<NEW_OWNER>`** and **accept** the emailed transfer invitation.
   **It expires in 24 hours** — accept in the same sitting.

What travels, per GitHub's docs: **issues, pull requests, wiki, stars, watchers,
all branches and tags, releases, full commit history, webhooks, deploy keys,
Actions secrets, and Actions data.** The 16 reaction issues (`#1`–`#16`, the
canonical sap channel) keep their numbers, so every `sap/reactions.yaml` URL
still resolves.

Two things worth knowing rather than discovering:

- **`olegmlkvorg` is auto-added as a collaborator.** GitHub does this on every
  personal→personal transfer. That is why this move is low-risk: **this Mac's
  `gh` auth and the box's SSH pushes keep working through the transfer without
  a single credential change.** `olegmalk` (the other existing collaborator)
  also survives — "other collaborators remain intact" — though it is worth a
  glance at Settings → Collaborators afterwards.
- **`olegmlkvorg` must never create a new repo named `banyan-city`.** Doing so
  *permanently deletes* the redirects that keep the couriers and raw URLs alive.

Keep the repo **public**. A private repo transferred to a free account loses
GitHub Pages, and the Pages mirror is our fallback layer.

### B2 — Vercel: connect the new identity

On the **new** Vercel account (`olegmalkov2023-1685`), which is already logged
in and holds the domains:

1. **Account Settings → Authentication** → add a **GitHub Login Connection**,
   authorising as **`<NEW_OWNER>`**. This is the step `vercel git connect`
   cannot do — it fails at validation with *"You need to add a Login Connection
   to your GitHub account first. (400)"*. The repository picker enumerates only
   the **namespace of the connected identity**; collaborator access is not
   namespace membership. That is why the identity must be the new *owner*.
2. **Install the Vercel GitHub App** on `<NEW_OWNER>`, scoped to
   **`banyan-city` only** — not "all repositories".
3. Project **`banyan-city` → Settings → Git → Connect Git Repository** → pick
   **`<NEW_OWNER>/banyan-city`**. Production branch must read **`main`**.
   *(No unlink first — the project is already disconnected. This is the part
   that is cleaner than 08-08.)*
4. Before leaving the page, confirm **`previewDeploymentsDisabled` is still
   `true`**.

**Do not add a payment card at any point.** None of this needs one, and the
cardless Hobby account is deliberate.

The next push to `main` deploys and the site catches up in about a minute — a
deployment builds HEAD, so there is no backlog to replay. If no push is pending,
**Redeploy** the latest commit from the dashboard.

### B3 — GitHub Pages: nothing to do, but know the URL moved

`pages.yml` hardcodes no owner and runs `actions/configure-pages` with
`enablement: true`, so Pages re-enables itself on the new owner at the first
push. The mirror simply reappears at a new address:

    OLD: https://olegmlkvorg.github.io/banyan-city/   ← dies, no redirect
    NEW: https://<NEW_OWNER>.github.io/banyan-city/

GitHub is explicit: *"we don't redirect GitHub Pages associated with the
repository."* This is the single surface with no safety net, which is why §C1
exists.

---

## C. The code-side fixes — run AFTER the transfer, not before

Editing these before the move would break links that currently work. The
checklist is ordered by how much it matters. **77 tracked files** (excluding this
one) mention `olegmlkvorg`; only the first two groups are urgent.

> **Re-grep before you start — this list drifts.** It is a snapshot, and lanes
> are committing all night. Between the first sweep and the commit after it,
> `pipeline/build_pulse.py` arrived carrying a fresh hardcoded
> `GH = "olegmlkvorg/banyan-city"` — a new builder written against the old
> constant, because that is what every sibling file still says. Expect more.
> Start the morning with `git grep -ln olegmlkvorg | wc -l` and treat any count
> above 77 as new arrivals to triage into the groups below. **Every new
> reference added between now and the transfer makes the C2 list longer**, so
> the sooner the account is named, the smaller this job is.

### C1 — The Pages mirror URL (no redirect — fix same day)

The only class of reference that hard-breaks. Nine occurrences across four
files:

| File | Lines |
|---|---|
| `README.md` | 72 (the public "free mirror" link) |
| `MIGRATION.md` | 39, 50, 510, 586, 592 |
| `OPERATOR.md` | 198, 208, 212 |
| `STATE.md` | 3316 (historical log line — annotate, do not rewrite) |

`MIGRATION.md:586` and `OPERATOR.md:208` are the DNS fallback plan: *"point `www`
at a CNAME → `olegmlkvorg.github.io`"*. That instruction becomes **actively
wrong** — following it after the transfer would point the domain at an account
that no longer hosts the site. Highest-priority edit in this file.

### C2 — Hardcoded repo slugs in build code (redirect covers us briefly)

These emit `github.com/olegmlkvorg/...` links into the **published site**. Web
links redirect, so nothing 404s — but the product would be publicly advertising
an account that no longer owns it. Same-day.

| File | Line | Constant |
|---|---|---|
| `pipeline/build_sim.py` | 78 | `GH = "olegmlkvorg/banyan-city"` — feeds `API`, and `RAW` at line 80, which becomes `RAW_BASE` in the browser (`LIVE_JS`, lines 1649 & 1683: heartbeat + telemetry fetches) |
| `pipeline/build_pulse.py` | 58 | `GH` → `RAW` → `TELEMETRY_URL` (reads the **`farm-results-rtx5090` courier branch**) and `QUEUE_URL`. Landed after the first sweep of this inventory — see the drift note below |
| `pipeline/build_shotboard.py` | 54 | `GH_REPO` → `REPO_URL` |
| `pipeline/build_status.py` | 25 | `GH_URL` → issue links, render-request label query, and `DEPLOY_API` (line 247) |
| `pipeline/ops_board.py` | 188, 189 | inline issue links |
| `pipeline/render_t1.py` | 169 | the footer stamped into **every T1 leaf** — fix before the next T1 render or new leaves inherit the old name |
| `pipeline/build_site.py` | 43, 2150 | see the trap below |
| `pipeline/harvest_sap.py` | 27 | `os.environ.get("GITHUB_REPOSITORY", …)` — runs in Actions, self-heals |
| `pipeline/test_pipeline.py` | 5301 | asserts the deployments API URL — **update in the same commit as `build_status.py:25` or CI goes red** |

> **The `build_site.py` trap — the non-obvious one.**
> Line 43 reads `os.environ.get("GITHUB_REPOSITORY", "olegmlkvorg/banyan-city")`.
> In **GitHub Actions** `GITHUB_REPOSITORY` is set, so the Pages mirror
> self-heals to the new owner with no edit at all. On **Vercel** — which is
> where banyan.city actually ships, via `buildCommand: python3
> pipeline/build_site.py` — there is **no `GITHUB_REPOSITORY` variable**
> (Vercel's git vars are `VERCEL_GIT_REPO_OWNER` / `VERCEL_GIT_REPO_SLUG`;
> confirmed against Vercel's system-environment-variables reference). So the
> **production site silently keeps the hardcoded old owner while the mirror
> quietly corrects itself** — the two surfaces disagree and neither errors.
> The fix is one line: default from `VERCEL_GIT_REPO_OWNER`/`_SLUG` when
> present, then `GITHUB_REPOSITORY`, then a literal. Line 2150 is a separate
> hardcoded `<a href>` inside an HTML string and needs its own edit.

### C3 — Clone/remote instructions for humans and fresh machines

Redirects keep existing clones working, but a *new* clone should not be taught
the old name.

`pipeline/ONBOARD-WINDOWS.md` (76, 100) · `pipeline/farm-join.md` (30, 34) ·
`pipeline/runpod_boot.sh` (34) · `pipeline/runpod_lane.py` (85) ·
`pipeline/kaggle/render-kaggle.ipynb` (112, `REPO_URL`) ·
`pipeline/telemetry.py` (83, `REMOTE = "git@github.com:olegmlkvorg/banyan-city.git"`).

### C4 — Published prose and node data (cosmetic; redirects hold indefinitely)

`.github/ISSUE_TEMPLATE/config.yml` (4, 7) · `MACHINE.md` (39) ·
`distribution/launch-kit.md` (52, 138, 179) · `distribution/reddit-drafts.md`
(41) · `lab/*.html` (10 across four files) · `pipeline/pending-founder.yaml`
(99, 105) · **48 files under `genomes/sapling/nodes/`** — 16 × `leaves/*-t1-a.html`
footers, 16 × `sap/reactions.yaml`, 16 × `sap/summary.yaml`.

The genome files are generated output; the cleanest fix is C2's `render_t1.py`
plus a scripted sweep, done as one commit so the lint diff is legible. The
issue **numbers** are correct and must not change.

`MIGRATION.md`, `STATE.md` and `DEPLOY-BROKEN-0810.md` are historical records —
the old name is *true* in them. Annotate, never rewrite.

### C5 — Off-repo surfaces (no commit; verify by hand)

| Surface | State now | After transfer |
|---|---|---|
| This Mac's `origin` | `https://github.com/olegmlkvorg/banyan-city` | Redirects. Run `git remote set-url origin https://github.com/<NEW_OWNER>/banyan-city` |
| `gh` CLI auth | account `olegmlkvorg`, scopes `gist, read:org, repo, workflow` | Still works — old owner is auto-collaborator. Re-auth as `<NEW_OWNER>` only if admin-level API calls start 403ing |
| Box: `C:\banyan-farm\banyan-city` | `git@github.com:olegmlkvorg/banyan-city.git` | SSH pushes redirect. Update at leisure; **needs a human login on the box**, so batch it with other box work |
| Box: `C:\banyan-farm\telemetry-git` | same SSH remote | Same — this is the courier that pushes `farm-results-*` |
| Actions secret `TRAFFIC_TOKEN` | present | Secrets transfer with the repo. **But if it is a fine-grained PAT scoped to `olegmlkvorg`'s resources, it stops covering the repo.** Verify at the next nightly `harvest-sap` (04:17) — a traffic fetch that silently skips is the symptom |
| Repo forks | **none** | No fork-network collision blocks the transfer |
| `<NEW_OWNER>` name collision | `olegmalk` has **no** `banyan-city` repo | Transfer to `olegmalk` would succeed today |

---

## D. What breaks in the gap, and for how long

| Surface | During the gap | Duration |
|---|---|---|
| **Couriers pushing from the box** (`telemetry.py`, `farm_worker.py`) | **Fine.** Git push redirects at the old SSH URL | Indefinite — until someone creates a repo at the old name |
| **`LIVE_JS` browser fetches** (`raw.githubusercontent.com/olegmlkvorg/...` → heartbeat, telemetry) | **Fine, but on borrowed time.** Raw redirects follow the repo | Works now; treat as same-day (C2). A CDN that caches a redirect badly is the failure we would not see coming |
| **GitHub Pages mirror** | **BREAKS.** Old URL dead, no redirect, new URL live at `<NEW_OWNER>.github.io/banyan-city` | Immediate and permanent. The C1 edits are the fix |
| **banyan.city (Vercel)** | Frozen at `d395b88` (21:52, 08-09) until §B2 step 3 | Ends the moment the project is reconnected |
| **Reaction issues `#1`–`#16`** | **Fine.** Numbers preserved, links redirect | Indefinite |
| **CI (lint, pages, sap, mirror)** | **Fine.** No workflow hardcodes the owner; Actions data transfers | No gap |
| **`gh` API calls by old name** | Redirect, but GitHub advises updating | Same-day for anything scripted |

The honest summary: **the only thing that truly breaks is the Pages mirror URL.**
Everything else is a redirect we should retire deliberately rather than lean on.

---

## E. Sequence

1. **Roman answers §0: which account.**
2. Transfer (§B1) → Vercel reconnect (§B2). One sitting, ~10 min.
3. Confirm a push to `main` deploys, and that
   `https://<NEW_OWNER>.github.io/banyan-city/` returns 200.
4. Agents run C1 + C2 in one commit (with the `test_pipeline.py:5301` update),
   then C3, then the C4 sweep.
5. Update `STATE.md` and append the supersession to `MIGRATION.md`.

Nothing in §C runs before step 2. Tonight's commit adds this file and the
supersession banner and touches nothing else.
