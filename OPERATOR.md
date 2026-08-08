# Operator work orders

This file is the handoff channel between the **steward** (the agent tending this
repo remotely — no browser, no accounts, no money) and the **operator** (an
agent or human on the founder's machine, with browser access and, when the
founder grants it, payment ability).

**Protocol:** the steward writes bounded work orders here. The operator
executes them, then edits this file — filling in the `RESULT` line and checking
the box — and commits with message `operator: <task-id> done`. The steward
verifies outcomes independently (DNS, HTTP, ledger) on its next tending pass.

## Rules for the operator (read first)

1. **Standing grant (founder, 2026-07-11, stated non-negotiable):** the
   operator has **full access on the founder's machine and the founder's
   payment card**. Work-order budget lines are the steward's cost *estimates*
   and scope signals, not caps — the operator may exceed them at its own
   judgment under this grant.
2. **Transparency is not waived:** every spend, whatever its size, gets
   recorded in `ledger/expenses.csv` (date, item, amount, task-id). This city
   publishes its costs — that's the framework's constitution, not a leash.
3. **Card and credentials never enter this repo or any commit.** This
   repository is PUBLIC: a card number, token, or password committed here is
   scraped by strangers within minutes. The card lives on the founder's
   machine and in payment forms only. Secrets that services need go in their
   own dashboards (e.g. GitHub repo secrets), referenced here by name only.
4. **This repo's story/governance files are not the operator's surface.**
   Operators touch this file, `ledger/expenses.csv`, and service dashboards —
   nothing else without a work order saying so.

---

## OPEN WORK ORDERS

### V6 — banyan.city is DOWN: decide the domain's route home
- [ ] Status: **open — the live site is 404 right now**, dad, ~10 minutes
- **Measured 2026-08-08, not assumed** (`dig`, `whois`/RDAP, `curl`):
  - `https://banyan.city` → **HTTP 404, `x-vercel-error: DEPLOYMENT_NOT_FOUND`,
    `server: Vercel`**. Same for `www`. The site is off the air.
  - Nameservers: **`ns1.vercel-dns.com` / `ns2.vercel-dns.com`** — the domain is
    on **Vercel DNS**, not merely pointed at Vercel with an A record. So the zone
    itself lives inside a Vercel account, and *whoever holds that account holds
    the DNS*. This is the fact that decides everything below.
  - Apex A → `216.150.16.65`, `216.150.16.193`; `www` A → `216.150.1.1`,
    `216.150.16.193` (Vercel edge). No `_vercel` TXT present.
  - Registrar: **Name.com, Inc.** Registered **2026-07-09**, expires
    **2027-07-09**, status `clientTransferProhibited`.
- **What this adds up to:** Vercel resells registration **through Name.com**
  (their own legal terms name Name.com and Tucows as the registrars they use),
  the registration date is two days before work order V2 attached the domain, and
  the nameservers have been Vercel's from the start. Read together that says
  **banyan.city was almost certainly bought through Vercel and is an asset sitting
  inside the old account** — not an independent registrar entry that merely points
  at Vercel. And `DEPLOYMENT_NOT_FOUND` (rather than NXDOMAIN or a dead TCP
  connect) means Vercel's router still recognises the hostname: the domain record
  is still there, the *project* behind it is what dad removed.
- **Do this first — one look settles it.** Log into the **old** Vercel account →
  **Domains** in the team sidebar. Is `banyan.city` listed?
  - **Listed, with a renewal date → it is Vercel-registered.** Go to V7 path A.
    Fastest route back online, and it moves the DNS zone with it.
  - **Not listed → it was bought at Name.com directly** (probably by Roman —
    V2 says "bought by founder"). Then dad needs the Name.com login, and V7 path B
    applies. **Ask Roman before assuming the account is lost.**
- **Do NOT delete the old Vercel account/team until the domain is out of it.**
  Deleting the account that holds a Vercel-registered domain is how a domain gets
  orphaned mid-registration. Move first, delete second, in that order.
- **Budget:** $0. Renewal is already paid to 2027-07-09.
- RESULT:

### V7 — Move banyan.city to the new account and put the site back up
- [ ] Status: **open** (blocked on V6's one look), dad
- **Path A — the domain is in the old Vercel account (expected case).**
  A team-to-team move inside Vercel is **not** a registrar transfer, so the
  60-day ICANN lock does **not** apply to it. It is instant.
  1. Create the new account on **hellobanyancity@gmail.com**. Keep it on
     **Hobby** — see V8 for why that is the correct tier, not a compromise.
  2. Old account → **Domains** (team sidebar) → context menu next to
     `banyan.city` → **Move** → enter the receiving team's **slug**
     (Settings → the slug field, on both profiles) → **Move**.
  3. Receiving account: **Add New → Project** → import `olegmlkvorg/banyan-city`.
     Vercel reads `vercel.json`, so the build command and output dir come across
     on their own. Framework preset: **Other**.
  4. New project → **Settings → Domains → Add Domain** → `banyan.city`. Accept
     the `www` prompt and let it redirect to the apex, as V2 had it.
  5. Because the nameservers are already Vercel's and the zone came with the
     move, the A records resolve without a registrar step. **No DNS change, no
     propagation wait.**
  - Caveat from Vercel's own docs, so it is not a surprise on the day: moving a
    domain does **not** carry project-domain assignments with it — step 4 is a
    real step, not a formality.
- **Path B — the domain is at Name.com under someone's personal login.**
  1. Get into Name.com (dad's or Roman's — V6 establishes whose).
  2. New Vercel account → new project (as A.3) → **Settings → Domains → Add
     Domain** → `banyan.city`. Vercel will report the domain is **in use by
     another account** and issue a **TXT record** to verify access. Add that TXT
     at Name.com. Vercel's docs are explicit that this **verifies use, it does
     not move ownership** — which is fine and is all the project needs.
  3. Then either leave the nameservers on Vercel (if the old account still serves
     the zone) or, cleaner, point Name.com's nameservers at the **new** account's
     Vercel DNS and re-add the records.
  - **Registrar transfers are locked until 2026-09-07** (registered 2026-07-09 +
    60 days, ICANN). Nothing above needs one — flagging it so nobody tries.
- **Done when:** `curl -sI https://banyan.city` returns `200`, not
  `DEPLOYMENT_NOT_FOUND`.
- **Budget:** $0.
- RESULT:

### V8 — Set the new account up so it cannot bill us again
- [ ] Status: **open**, dad — do this *before* the first push, not after
- **Tier: stay on Hobby. It is not a downgrade, it is the actual spend guard.**
  Hobby has **no payment method and no overage billing at all** — exceed a limit
  and the feature pauses for 30 days; it cannot produce an invoice. Pro is
  $20/seat/month *plus metered usage*, and **Vercel Spend Management does not
  exist on Hobby (the docs list it "N/A" for Hobby, "Configurable" for Pro)**.
  So dad's "vercel does not have limit" is **half right, and the half matters**:
  on the tier that can charge you there IS a cap (Pro Spend Management can
  auto-**pause production deployments** at a dollar amount), and on Hobby there
  is no cap because there is nothing to cap. **The safest tier is the free one.**
  - Spend Management caveats if we are ever on Pro: Vercel checks spend "every
    few minutes", so it is a **soft cap that overshoots** — set it below the real
    limit. Pausing is not automatic; the **Pause production deployment** switch
    has to be turned on separately. Paused projects **do not un-pause** when the
    cycle rolls over; each one is resumed by hand.
- **What would force Pro later** — honest list, none of it true today:
  taking money (Hobby's fair-use terms restrict it to **non-commercial, personal
  use**, and name payment processing, ads, affiliate links and **asking for
  donations** as commercial), more than 100 deployments/day, >1 concurrent build,
  or needing a team seat for a second person. **Opening a money rail is the
  trigger — and that is D5/§4, Roman's call, not an infra decision.** Note the
  same restriction applies to the Pages mirror: GitHub forbids Pages "as a free
  web-hosting service to run your online business". Both hosts are fine while
  banyan.city earns nothing; **both become a licensing problem the same day**.
- **Where the >$100 actually came from, so the settings below are aimed right.**
  Not bandwidth — build compute. Vercel bills builds at **$0.0035 per CPU-minute,
  rounded UP to the whole minute and multiplied by every vCPU on the machine**,
  and new paid teams default to **Elastic** machines (4–30 vCPU) with **on-demand
  concurrency on by default, up to 500 parallel builds**. Four farm boxes ×
  ~288 heartbeats/day ≈ **1,150 deployments a day**, each a full pip install +
  `build_site.py`, all allowed to run at once. 500 build hours on a 4-vCPU
  machine is 500 × 60 × 4 × $0.0035 ≈ **$420** of theoretical burn; >$100 is that
  meter running for part of a month.
- **Clicks, in order, on the new project:**
  1. **Settings → Build and Deployment → Ignored Build Step → Only build
     production.** (`vercel.json` already carries `git.deploymentEnabled` and an
     `ignoreCommand`; this is the layer that still governs a branch whose
     checked-out `vercel.json` is stale, which force-pushed farm branches are.)
  2. **Settings → Git → Production Branch = `main`.**
  3. **Settings → Build and Deployment → On-Demand Concurrent Builds → off.**
     On Hobby concurrency is 1 anyway; set it so an accidental upgrade cannot
     silently re-enable the thing that cost the money.
  4. Leave the build machine at **Standard**. Vercel's pricing page: builds on
     Standard are billed **only** when on-demand concurrency is enabled or
     Elastic is selected. Standard + no on-demand = the build meter never starts.
- **One thing that is NOT a fix, so nobody reaches for it:** an
  `ignoreCommand` alone would not have prevented this bill. Vercel's docs say a
  skipped build is still **"counted as a full deployment"** and still consumes
  **deployment quota and a concurrent build slot** — and billing rounds up to a
  whole CPU-minute, so ~1,150 no-op skips a day still meters. Only
  `git.deploymentEnabled` (evaluated *before* a deployment is created) and the
  project settings above stop the event happening at all.
- **Cheapest possible shape, if dad wants belt-and-braces:** set
  `git.deploymentEnabled: false` and deploy only through the existing `vercel`
  GitHub Actions workflow, which already does `vercel build` +
  `deploy --prebuilt` (that is how V1 shipped). The build then runs on a **free
  public-repo GitHub runner** and Vercel only hosts. Vercel's docs stop short of
  stating outright that a prebuilt deploy is never billed, so **check the first
  invoice rather than take that on trust** — but it moves the compute off the
  meter by construction. Costs nothing to adopt; needs V4's token.
- **Budget:** $0, and that is the point.
- RESULT:

### V9 — Stopgap: park banyan.city on the free Pages mirror (only if V7 stalls)
- [ ] Status: **open — use only if V6 shows the domain is not reachable today**
- **Why it is a real option:** `https://olegmlkvorg.github.io/banyan-city/`
  answers **200** right now, and the generator emits **only relative links**
  (`href="city.html"`, zero root-relative `/…` paths — checked, not assumed), so
  every page works unchanged when the site moves from `/banyan-city/` to the apex
  root. `build_site.py` already sets `CANONICAL = "https://banyan.city"`.
- **Steps, and the order is load-bearing:**
  1. **DNS first.** Wherever the zone is (Vercel DNS in the old account, or
     Name.com), replace the apex A records with GitHub's four:
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
     (AAAA, optional: `2606:50c0:8000::153` … `:8003::153`). Point `www` at a
     **CNAME → `olegmlkvorg.github.io`**.
  2. **Then** repo → **Settings → Pages → Custom domain** → `banyan.city` → Save.
  3. Wait for the cert, **then** tick **Enforce HTTPS**.
- **Caveats, all of them:**
  - **Setting the custom domain makes `olegmlkvorg.github.io/banyan-city`
    redirect to `banyan.city`.** Do it before DNS resolves and you take down the
    one URL that currently works. Hence DNS first.
  - **HTTPS is not instant** — GitHub says the Enforce HTTPS option can take
    **up to 24 hours** to become available while the certificate issues. Between
    the DNS cut and the cert, the apex serves a TLS warning. This stopgap trades
    a clean 404 for a few hours of cert warning; if V7 path A is available, **V7
    is both faster and cleaner and this order should be skipped entirely.**
  - Pages deploys here are **workflow**-built, so the 10-builds/hour Pages soft
    limit does not apply; the 100 GB/month bandwidth and 1 GB site soft limits do.
  - Reverting to Vercel later means putting the A records back and clearing the
    custom domain — cheap, but it is a second cutover.
- **Budget:** $0.
- RESULT:

### V4 — Add the VERCEL_TOKEN repository secret (enables auto-deploy from CI)
- [ ] Status: **open** — founder or operator, ~30 seconds
- **What:** GitHub repo → Settings → Secrets and variables → Actions → New
  repository secret. Name: `VERCEL_TOKEN`. Value: the Vercel token the founder
  issued to the steward (founder has it; steward holds it only in its ephemeral
  session). Then re-run the `vercel` workflow once (Actions → vercel → Run
  workflow) or push anything to `main`.
- **Why:** the steward's session proxy blocks writing GitHub secrets, and the
  steward's own copy of the token dies with its container. Until this is set,
  banyan.city updates only when the steward manually redeploys on a tending pass.
- **STALE AFTER THE MOVE — read before setting the token.**
  `.github/workflows/vercel.yml` hardcodes the **old** account's
  `VERCEL_ORG_ID: team_a9sPzfYauUVeVMTAsO8hWXaH` and
  `VERCEL_PROJECT_ID: prj_LfrxgwzJFYqW2OEa5TL63RePlmbD`. Both die with the old
  project. Setting a **new** account's `VERCEL_TOKEN` while those stay put makes
  the workflow fail against IDs the token cannot see. Take the new pair from the
  new project's `.vercel/project.json` (or Settings → General) and update the
  workflow **in the same change** as the secret. The workflow is a no-op without
  the token, so today it is harmless — it stops being harmless the moment V4 is
  done.
- **Budget:** $0.
- **Done when:** the `vercel` workflow runs green and banyan.city reflects a new push.
- RESULT:

### V5 — Record the banyan.city purchase price
- [ ] Status: **open**
- **What:** add a row to `ledger/expenses.csv` with the actual price the founder
  paid for banyan.city (registrar receipt) and commit.
- **Budget:** $0 (retroactive bookkeeping).
- RESULT:

### V3 — Report rails available for Phase 3 (no purchase)
- [ ] Status: **open** (anytime)
- **What:** check whether the founder's GitHub account is eligible for GitHub
  Sponsors, and note which of Ko-fi / Patreon the founder prefers to open when
  Phase 3 starts. **Do not create any account or accept any money** — this is
  reconnaissance only; opening a rail requires the founder's explicit go
  (STEWARDSHIP.md §4).
- **Budget:** $0.
- RESULT:

---

## COMPLETED WORK ORDERS

### V1 — Deploy the site to Vercel — **done 2026-07-11 by the steward**
- Founder issued a full-access Vercel token directly to the steward, making the
  browser path unnecessary. Project `banyan-city` created via CLI; prebuilt
  static deploys (local `vercel build` → `deploy --prebuilt --prod`).
- RESULT: production live; remote pip build intentionally bypassed (prebuilt flow).

### V2 — Attach banyan.city — **done 2026-07-11 by the steward**
- Domain was already on Vercel nameservers (bought by founder); apex attached to
  the project, `www` added with redirect to apex; certificates issued.
- RESULT: <https://banyan.city> serves the full site (8 nodes), valid TLS.
