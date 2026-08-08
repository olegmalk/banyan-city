# Migrating banyan.city to its own Vercel account

**Who does what.** Roman does every step in §B — they are account, domain and
DNS steps, and those are founder-reserved human work. Dad watches the money and
owns the one decision marked **DECISION** (tier + cap). The steward does §C —
verification only, from the outside, $0, no account needed. Nothing in this file
requires a card, and no step here can bill anyone.

**What is already done (2026-08-08).** B2 (the new account) by the founder; B2b
(the Vercel project, created empty and pre-configured, git deliberately **not**
connected) by the steward. That turns B7 from five clicks into one look. **The
human work left is four steps:**

> **B1** find where the domain lives → **B4** move it to
> `olegmalkov2023-1685s-projects` → **B6** connect the git repo to the existing
> `banyan-city` project → **B8** attach the domain to it.
>
> With **B3** (tier — recommendation: change nothing, stay Hobby) as the one
> decision, and **B7** as a one-item verify in between. B5, B9 and B10 are
> confirm-only or no-ops on Hobby.

**Status when this was written (measured 2026-08-08 05:49Z, not assumed):**

| check | result |
|---|---|
| `curl -sI https://banyan.city` | **404**, `x-vercel-error: DEPLOYMENT_NOT_FOUND`, `server: Vercel` |
| `curl -sI https://www.banyan.city` | **404**, same |
| `curl -sI https://olegmlkvorg.github.io/banyan-city/` | **200** — the mirror is carrying the site |
| nameservers | `ns1.vercel-dns.com`, `ns2.vercel-dns.com` — **the DNS zone lives inside a Vercel account** |
| registrar | Name.com, Inc. Registered 2026-07-09, expires 2027-07-09, `clientTransferProhibited` |
| repo-side build guards on `main` | **present** — commits `eb16094`, `aeea1ac` |

The site is down right now. This is a repair, not a scheduled move.

---

## A. What happened

Between 2026-07-11 and 2026-08-08 the old Vercel project ran **2,982
deployments** — a number GitHub recorded independently of Vercel, as
`vercel[bot]` entries in the repo's deployments API — of which **2,303 (77.2%)
were Preview builds of branches nobody reads**. The cause was `farm_worker.py`
force-pushing a heartbeat commit to its `farm-results-*` branch every ~5 minutes
for the whole length of every render task (`telemetry.py PUBLISH_SECONDS = 300`;
of 613 measured inter-arrival gaps on rtx5090, 594 fell in the 4–6 minute band),
and Vercel building the entire site — full `pip install` plus `build_site.py`,
over a 1.9 GB clone — for each one. **The arithmetic closes:** >$100 at Vercel's
$0.0035 per CPU-minute is ~476 CPU-hours, which is the reported "500+ build
hours" figure; spread over 2,982 deployments that is 9.6 CPU-minutes each, or
~2.4 wall-minutes on the 4-vCPU Elastic machine that paid teams get by default.
So the 6× gap between that and our measured 100-second median build is the vCPU
multiplier, not a mystery. Dad removed the project on 2026-08-07 (last
`vercel[bot]` deployment 2026-08-08T00:55Z), which took the bill to zero and the
site with it. Nothing was overspent on rendering, models or storage — **this was
one unguarded git trigger, running on a timer, for 28 days.**

---

## B. The human steps, in order

Read the whole section before starting. Two orderings in it are load-bearing and
are called out where they occur.

### B0. The one thing that cannot be undone

**Do not delete the old Vercel account or team until the domain is out of it.**
The nameservers are Vercel's, so the DNS zone is an asset inside that account.
Deleting the account first is the one move here that can orphan the domain
mid-registration. Move first, delete second, and there is no hurry about the
second.

### B1. Find out where the domain actually lives (~2 minutes)

1. Log into the **old** Vercel account.
2. Team sidebar → **Domains**.
3. Is `banyan.city` listed?
   - **Listed, with a renewal date → it is Vercel-registered.** Take **path A**
     below. This is the expected case: Vercel resells registration through
     Name.com, the registration date (2026-07-09) is two days before the domain
     was attached, and the nameservers have been Vercel's from the start.
   - **Not listed → it was bought at Name.com directly**, probably on Roman's own
     login (`OPERATOR.md` V2 records it as "bought by founder"). Take **path B**.
     Ask before assuming a login is lost.

Record which path in the `RESULT:` line of `OPERATOR.md` V6.

### B2. Create the new account — **DONE 2026-08-08, by the founder**

Kept as a step rather than deleted so the runbook stays honest about what was
done and by whom. **Nothing to do here.**

The account exists and the local Vercel CLI is logged into it. Measured
2026-08-08 by reading the API through that login, not assumed:

| fact | value |
|---|---|
| email | **olegmalkov2023@gmail.com** |
| user | `olegmalkov2023-1685` |
| **team slug** (this is what B4 asks for) | **`olegmalkov2023-1685s-projects`** |
| plan | `hobby` |
| payment method | **`null` — none attached** |

**Correction:** earlier drafts of this file, `OPERATOR.md` V7 and the `STATE.md`
entry for 2026-08-08 all named **`hellobanyancity@gmail.com`**. That plan was
dropped and no such account was made. Any doc still naming it is stale.

**The no-payment-method rule stands, and it is the whole spend guard.** Hobby
with `payment: null` is the only state in which this project cannot generate an
invoice (B3). Do not add a card to "unlock" anything. If a Vercel screen asks
for one, the answer is to not do that thing.

One thing the login also settles, read-only: the account can see two scopes,
`olegmalkov2023-1685s-projects` and a team `banyan-3318d224` ("banyan"). **Both
are empty — 0 projects and 0 domains each.** So the old account holding
`banyan.city` is *not* reachable from this login, and B1 is still a real step
that has to happen in the old account's own session.

### B2b. The project is created and pre-configured — **DONE 2026-08-08, by the steward**

**Nothing to do here either.** An empty, **git-disconnected** project named
`banyan-city` now exists in `olegmalkov2023-1685s-projects`, with the B7
settings already applied through the logged-in CLI. Creating an unlinked project
costs nothing, builds nothing and deploys nothing: `latestDeployments: []`,
`live: false`. **No deploy of any kind was run**, and the git repo was **not**
connected — that authorization is the founder's browser step (B6).

Project id `prj_EnxZWrmMb83d0Au5irzg5TAXmEoC`. Applied and then read back:

| setting | value | why |
|---|---|---|
| `framework` | `null` (= **Other**) | B6 step 3 |
| `previewDeploymentsDisabled` | **`true`** | B7 step 3 — see below |
| `commandForIgnoringBuildStep` | `bash pipeline/vercel-ignore-build.sh` | B7 step 2 |
| `gitForkProtection` | `true` | fork PRs need authorization |
| build/install/output/root | all `null` | Vercel reads them from `vercel.json` |

**`previewDeploymentsDisabled: true` is the one that matters**, and it is worth
saying why in full: it is a *project-level* setting, so it governs a push on a
branch whose checked-out `vercel.json` is stale — which, as §C1 measured, is all
five courier branches today. It is the layer `git.deploymentEnabled` cannot
reach. **It also closes the five-minute race window B6 used to warn about**: a
courier heartbeat landing between the git connect and the settings pass can no
longer create a preview build, because the setting is already on before the repo
is connected.

**Two settings could NOT be applied, and neither is a gap:**

- **Production branch.** Not settable before git is connected — it lives in the
  git link, not the project record, and it is absent from the `PATCH
  /v9/projects/{id}` schema entirely. It does not need setting: Vercel's docs say
  a new project's production branch is chosen as "the `main` branch" first, and
  ours is `main`. So it should come out right on its own. **Verify, don't set**
  (B7 step 1).
- **Build machine / on-demand concurrency.** The API refused: `Custom build
  machines are not available on your plan (400)`. That is Hobby working as
  intended — concurrency is 1, the machine is Standard, and
  `elasticConcurrencyEnabled` is already `false`. B7 steps 4 and 5 are **moot on
  Hobby**, not skipped. They become real again the day anyone upgrades to Pro,
  which is why they stay written down.

### B3. DECISION — tier and cap (dad + Roman together)

**Recommendation: stay on Hobby. Expected monthly cost $0.**

Hobby is not a compromise here, it is the strongest available spend guard: there
is no payment method attached, so there is nothing that can produce an invoice.
Exceed a limit and the feature pauses; it does not bill. Pro is $20/seat/month
**plus** metered usage.

Dad's "vercel does not have limit" is half right, and the half matters: Vercel's
**Spend Management is Pro-only** — the docs list it "N/A" for Hobby,
"Configurable" for Pro. So the tier that *can* charge you is the only tier with a
cap, and the tier with no cap is the one that cannot charge you at all.

**What Hobby costs us in exchange, stated honestly:**

- **100 deployments/day.** We averaged 106.5/day under the flood, so the guards
  in §D are what keep us under it. Exceeding it pauses deployments — which
  would take the site down, not bill us.
- 1 concurrent build. Fine for one site.
- **Non-commercial use only.** GitHub Pages carries the same class of
  restriction. Both hosts become a licensing question the same day banyan.city
  takes money — including donations. That is D5/§4 and Roman's call, not an
  infra decision, and it is not today.

**If dad chooses Pro anyway**, then step B9 is mandatory, not optional, and the
cap goes at **$5** with **Pause production deployment** switched on. Know before
choosing: Spend Management is checked "every few minutes", so it overshoots the
cap; and a paused project does **not** un-pause when the billing cycle rolls
over — someone resumes it by hand.

### B4. Move the domain — path A only (~2 minutes, instant)

A team-to-team move inside Vercel is **not** a registrar transfer, so the 60-day
ICANN lock (which runs to 2026-09-07) does not apply and there is no propagation
wait. The DNS zone moves with the domain.

1. Old account → **Domains** → the `⋯` menu next to `banyan.city` → **Move**.
2. Enter the **new** account's slug from B2. Confirm.
3. Verify it now appears under the new account's **Domains**.

**Path B instead:** there is nothing to do at this step. The domain gets verified
after the project exists, at B7.

**Why this comes before the import:** it takes the only irreversible risk in the
whole migration off the table while the old account is still open and healthy.

### B5. Confirm the guards are on `main` before connecting anything (~1 minute)

This is the step that makes the rest safe, and it is already done — confirm, do
not redo. On `main`:

- `vercel.json` carries `git.deploymentEnabled` denying `**`, `*`,
  `farm-results-*`, `farm-results-**`, `runpod-results`, and allowing `main`
  only. Vercel evaluates this **before creating a deployment**, so a matching
  push produces no event at all.
- `pipeline/vercel-ignore-build.sh` is wired as `ignoreCommand` and skips any
  push that touches no site input.

Commits **`eb16094`** and **`aeea1ac`**, both on `main`, CI green. The steward
re-verifies this on the day (§C1) and will say so before you import.

**An `ignoreCommand` alone would not have prevented this bill** — Vercel's docs
say a skipped build still counts as a full deployment and still takes a
concurrent build slot. `git.deploymentEnabled` plus the project settings in B6
are what stop the event existing.

### B6. Connect the repo to the project that already exists (~2 minutes)

**Do not use "Add New → Project".** That would create a *second* project and
leave the pre-configured one unused. The project exists (B2b); this step gives it
a git repo.

1. New account → project **`banyan-city`** → **Settings → Git**.
2. **Connect Git Repository** → GitHub. Install the Vercel GitHub app if
   prompted, granting access to **`olegmlkvorg/banyan-city` only**, not all
   repositories.
3. Select `olegmlkvorg/banyan-city` and connect.
4. Leave framework, build command, install command and output directory alone.
   They are already set (framework **Other**; the rest `null` so Vercel reads
   them from `vercel.json`).

**The old five-minute panic here no longer applies.** This step used to warn that
a courier heartbeat landing between the import and the settings pass would create
a preview build — because all five courier branches (`farm-results-rtx5090`,
`-msi`, `-m2`, `-m1pro`, `runpod-results`) still carry the **pre-guard**
`vercel.json`, and Vercel reads that file from the branch being pushed, so the
deny-list does not govern them until each branch turns over. That is still true
of the branches (§C1 re-checks it), but `previewDeploymentsDisabled` was set
**before** the repo was connected, so there is no window. Take B7 at a normal
pace.

**On whether connecting produces a deployment:** the old import flow always did,
by design — its last button was "Deploy". Connecting a repo to an existing
project may or may not; Vercel's docs do not say, so this file does not claim
either. It does not matter much: previews are off, so anything it produces is a
production build of `main`, which is the build we want. If nothing appears,
push to `main` or use **Deployments → Create Deployment** with branch `main`.

### B7. The settings — now a VERIFY pass, ~1 minute

Steps 2–5 were applied in B2b or are unavailable on Hobby. **Only step 1 is
still an action, and it is a look, not a change.** Check the rest against the
dashboard; if any disagrees with the table below, that is worth knowing before
the domain goes on.

1. **Production branch = `main` — verify.** **Settings → Environments →
   **Production** → Branch Tracking.** (Not "Settings → Git" — Vercel moved it;
   older notes in this repo, including `OPERATOR.md` V8, still say Git.) It
   should already read `main` because Vercel picks `main` first for a new
   project. If it says anything else, change it here and save.
2. Ignored Build Step — **already set** to `bash pipeline/vercel-ignore-build.sh`
   (B2b). `vercel.json`'s `ignoreCommand` carries the identical string, so the
   two layers cannot disagree whichever takes precedence.
3. Preview deployments — **already disabled** project-wide (B2b).
4. On-Demand Concurrent Builds — **not available on Hobby**, and already `false`.
5. Build machine → Standard — **not selectable on Hobby**; the API returns
   `Custom build machines are not available on your plan`. Standard is the
   default and the un-metered one.

Steps 4 and 5 stay written down because they stop being moot the moment anyone
upgrades to Pro. That upgrade is exactly when the meter that caused §A turns back
on, so whoever does it reads this step first.

These settings are the only layer that governs a branch whose checked-out
`vercel.json` is stale — which every courier branch is today (§C1).

### B8. Attach the domain (~2 minutes)

Moving a domain does **not** carry project assignments with it. This is a real
step, not a formality.

1. Project → **Settings → Domains → Add Domain** → `banyan.city`.
2. Accept the `www` prompt and let `www` redirect to the apex, as it was before.
3. **Path B only:** Vercel will report the domain is in use by another account
   and issue a **TXT record**. Add that record at Name.com. Per Vercel's docs
   this verifies *use*, not ownership — which is all the project needs.

### B9. DNS (~0 minutes on path A)

**Path A: there is nothing to do.** The nameservers are already
`ns1/ns2.vercel-dns.com` and the zone travelled with the domain in B4. The A
records resolve as soon as B8 is saved. Do not touch DNS to "make sure" — the
apex A values rotate (measured `216.150.16.65 / .16.193` early on 2026-08-08 and
`216.150.1.1 / .1.193` a few hours later, both Vercel edge), so a hardcoded
record copied from a screenshot will rot. The nameservers are the load-bearing
fact, not the IPs.

**Path B:** either leave the nameservers pointing at the old account's Vercel DNS
(works, but keeps a dependency on an account we are leaving), or — cleaner —
point Name.com's nameservers at the **new** account's Vercel DNS and let Vercel
recreate the records. Do this only after B8 shows the domain verified.

### B10. Spend Management — Pro only (~2 minutes)

**On Hobby, skip this. It does not exist, and it does not need to: there is no
payment method to charge.**

**On Pro:** Account → **Settings → Billing → Spend Management** → set the amount
to **$5**, and separately switch on **Pause production deployment**. The pause is
not automatic without that second switch. Then read B3's caveats again — the cap
overshoots and the un-pause is manual.

---

## C. Verification after each step — steward side, $0, no account needed

Every check below runs from this repo with no Vercel access at all. That is
deliberate: an audit that depends on the dashboard is an audit dad cannot ask a
second party to reproduce.

### C1. Before B6 — the guards are on `main`

```sh
git fetch origin
git show origin/main:vercel.json | grep -A8 deploymentEnabled
git branch -r --contains eb16094 --contains aeea1ac
```

Expected: the deny-list block, and `origin/main` in the contains list.

Also reports, per courier branch, whether it has turned over yet:

```sh
for b in farm-results-rtx5090 farm-results-msi farm-results-m2 \
         farm-results-m1pro runpod-results; do
  printf '%-24s ' "$b"
  git show "origin/$b:vercel.json" 2>/dev/null | grep -q deploymentEnabled \
    && echo 'guard present' || echo 'PRE-GUARD — relies on B7 settings'
done
```

All five printed `PRE-GUARD` on 2026-08-08. They self-heal only when each box
starts its next task (`farm_worker.py:573` runs `git checkout origin/main -- .`),
so this is re-run rather than assumed.

### C2. After B7 — a courier push does NOT trigger a build

GitHub records every Vercel deployment as a `vercel[bot]` entry, so this is
answerable without logging into Vercel. This is the same signal that measured the
2,303 preview builds in §A.

```sh
gh api "repos/olegmlkvorg/banyan-city/deployments?per_page=100" \
  --jq '.[] | select(.creator.login=="vercel[bot]")
        | [.created_at, .environment, .ref[0:8]] | @tsv'
```

Wait for the next heartbeat (≤5 minutes; confirm one landed with
`git log -1 --format=%cI origin/farm-results-rtx5090`), then re-run. **Pass: no
new `Preview` row.** A new `Preview` row means B7 step 2 or 3 did not take, and
it is worth catching within the hour rather than at month end.

### C3. After B8/B9 — banyan.city serves the new deployment

```sh
curl -sI https://banyan.city | head -8
curl -sI https://www.banyan.city | head -3
curl -s https://banyan.city | grep -c 'banyan'
```

Pass: **200** with an `x-vercel-id` header and **no** `x-vercel-error`; `www`
returns a 30x to the apex; the body is the real site, not a placeholder. The
steward also diffs a handful of live pages against a local `build_site.py` run to
confirm the deployment is current rather than a stale cached edge response.

### C4. Continuously — the mirror still works as fallback

```sh
curl -sI https://olegmlkvorg.github.io/banyan-city/ | head -3
```

Pass: **200**. The mirror is what has been carrying banyan.city through this
outage, and it stays live as the fallback. It must keep answering on its own
`github.io` URL — which is exactly what the optional interim in §E would give up.

### C5. Ongoing — the deployment count is the spend meter

```sh
gh api "repos/olegmlkvorg/banyan-city/deployments?per_page=100" --paginate \
  --jq '.[] | select(.creator.login=="vercel[bot]") | .created_at[0:10]' \
  | sort | uniq -c
```

Healthy looks like single digits per day, all Production. Two thresholds worth
alarming on: **any** Preview row, and **>50/day** (half of Hobby's 100/day
allowance). This query is the honest, $0 data source for the status-board spend
tile queued as `infra-spend-tile-1786166880` — it counts *build triggers*, which
we can measure, and does not pretend to know dollars, which we cannot until an
invoice exists.

---

## D. Standing rules from here

1. **Only `main` builds.** In code (`vercel.json` `git.deploymentEnabled`) and in
   the dashboard (B7). Both, always — the code layer does not govern a branch
   whose checked-out copy is stale, and the dashboard layer is not diffable by a
   reader of this repo. Neither is sufficient alone.
2. **A build must be justified by a changed site input.**
   `pipeline/vercel-ignore-build.sh` holds the path list, derived from the
   builders' source rather than guessed, and
   `test_vercel_build_guard_covers_every_site_input()` in `pipeline/test_pipeline.py`
   fails if a new input escapes it. If you add a module that `build_site.py`
   reads, that test tells you before Vercel does.
3. **The spend tile ships on the status board** (`infra-spend-tile-1786166880`),
   sourced from C5. A metered service with no visible meter is how this happened.
4. **No metered service gets connected without a code-side guard and a $0 meter
   first** — D18, resolved 2026-08-08. `budget.yaml` only ever guarded priced,
   discrete, human-initiated jobs; infra is none of those, so the guard sat
   waiting to be asked while a machine spent on a timer. A dashboard toggle does
   not satisfy this rule, because nobody can diff a toggle.
5. **Couriers commit with explicit pathspecs.** `farm_worker.py:155` is correctly
   scoped but `:156` is a bare `git commit`, which sweeps whatever another
   process staged in that shared checkout into an `hb:` commit and force-pushes
   it. Queued as `courier-commit-pathspec-1786167000`.
6. **Reducing heartbeat cadence is not a money fix.** Queued as a proposal only
   (`telemetry-idle-cadence-proposal-1786166940`) and argued on its real merit —
   the monitoring blind spot — because once the allowlist is on, slower
   heartbeats save exactly $0.
7. **Read the first invoice**, whatever the tier says. Vercel's docs stop short
   of promising that a prebuilt deploy is never billed, and ">$100" may have
   included CDN bandwidth for 86 mp4s in a 482 MB `_site` rather than being all
   build compute. Only the invoice splits that, and until one exists we say so
   instead of guessing.
8. **Record what the domain cost** in `ledger/expenses.csv` (`OPERATOR.md` V5).
   This city publishes its costs; the one line we are missing is the domain.

---

## E. Optional interim — park the apex on the Pages mirror today

**Take this only if B1 shows the domain is not reachable today** — if path A is
available, it is faster and cleaner than this and this section should be skipped
entirely. Path A is instant; this trades a clean 404 for hours of TLS warning.

**The order is load-bearing. DNS first.**

1. **DNS first.** In whichever zone is authoritative, replace the apex `A`
   records with GitHub's four: `185.199.108.153`, `185.199.109.153`,
   `185.199.110.153`, `185.199.111.153`. Optional AAAA: `2606:50c0:8000::153`
   through `:8003::153`. Point `www` at a **CNAME → `olegmlkvorg.github.io`**.
2. **Then** repo → **Settings → Pages → Custom domain** → `banyan.city` → Save.
3. Wait for the certificate to issue, **then** tick **Enforce HTTPS**.

**Every caveat:**

- Setting the custom domain makes `olegmlkvorg.github.io/banyan-city` **redirect**
  to `banyan.city`. Do it before DNS resolves and you take down the one URL that
  currently works. That is why DNS is step 1.
- HTTPS is not instant — GitHub says Enforce HTTPS can take **up to 24 hours** to
  become available. Until then the apex serves a certificate warning.
- Pages here is workflow-built, so the 10-builds/hour soft limit does not apply;
  the 100 GB/month bandwidth and 1 GB site limits do, and `_site` is 482 MB.
- The generator emits **only relative links** (checked, zero root-relative paths)
  and `CANONICAL` is already `https://banyan.city`, so every page works unchanged
  at the apex root. Nothing in the repo needs editing for this.
- Reverting to Vercel later means restoring the A records and clearing the custom
  domain. Cheap, but it is a second cutover, and cutovers are where domains get
  hurt.

---

## Provenance

Assembled 2026-08-08 by the steward from three prep passes: the build-guard
implementation (`eb16094`, `aeea1ac`), the migration research recorded as
`OPERATOR.md` V6–V9 (`51dc76e`), and the spend forensics recorded in `STATE.md`
and `DECISIONS.md` D18 (`8f8a00f`). Every number in §A and every DNS, HTTP and
branch fact in this file was measured on 2026-08-08, not carried over.

Revised later the same day, after the founder created the account and logged the
Vercel CLI into it. B2, B2b, B6 and B7 were rewritten against **measured API
state**, not docs: every value in B2 and B2b was read back from
`GET /v9/projects/banyan-city` after being written, and the two refusals in B7
are the API's own 400. The click-path correction in B7 step 1 (Environments →
Branch Tracking, not Git) comes from Vercel's current `/docs/git`.

**What an agent did and did not do.** Did: create one empty Vercel project and
PATCH its settings, through the founder's already-logged-in CLI. Did not: run any
deploy, connect the git repo, touch DNS or a domain, add a payment method, delete
anything, or mint a token. Domain and git-authorization steps are human work by
design, and the account remains Hobby with no payment method.
