# banyan.city stopped deploying — 2026-08-09 22:14:47 (+04)

**Status: the site is UP and serving, but frozen at the 21:52 build. It will not
un-freeze on its own. The first step is a browser action only the founder can do.**

Times are local (+04) unless marked Z.

## What happened

At **22:14:47 (18:14:47Z)** the Vercel project's GitHub repository was
disconnected. Vercel's own event log records it as:

    project-git-repository-disconnected
    "You disconnected GitHub repository olegmlkvorg/banyan-city from project banyan-city"
    principal: olegmalkov2023-1685 <olegmalkov2023@gmail.com>

That is the only non-deployment event in the project's whole event history. From
that moment pushes to `main` produce no deployment and no commit status — the
silence is correct behaviour for a project with no repo attached, not a failure.

It was **not** the Hobby deployment cap. Measured, not assumed: 56 deployments on
08-09 local, 44 on 08-09 UTC, 55 in the rolling 24h — against a 100/day cap. We
peaked at 56% and never came near it. That hypothesis is dead.

## What is actually broken

The disconnect went one level deeper than the project. The **GitHub Login
Connection on the Vercel account is gone**, not just the project link:

| Probe | Result |
|---|---|
| `GET /v9/projects/{id}` → `link` | `null` |
| `GET /v9/projects/{id}/link` | `404 Project Link not found` |
| `GET /v1/integrations/git-namespaces?provider=github` | `[]` |
| `GET /v1/integrations/configurations?view=account` | `[]` |
| `GET /v2/user` → `importFlowGitProvider` | `null` |

Attempting the repair from the CLI fails at validation, changing nothing:

    $ vercel git connect --yes
    > Connecting GitHub repository: https://github.com/olegmlkvorg/banyan-city
    Error: Failed to link olegmlkvorg/banyan-city. You need to add a Login
    Connection to your GitHub account first. (400)

This is exactly the state STATE.md §B6 describes as the thing that "cost the
morning" on 08-08 — the Vercel account must have GitHub login **`olegmlkvorg`**
(the repo owner) connected, because the repository picker enumerates only the
namespace of the connected identity. Collaborator access is not namespace
membership; connecting `olegmalk` will not make the repo appear.

## What is NOT broken — nothing else needs touching

- **Domains intact and `verified: true`**: `banyan.city`, `www.banyan.city`
  (redirecting to the apex), `banyan-city.vercel.app`.
- **Site live**, serving the `d395b88` build (21:52:14 READY) from CDN.
- **Project settings survived** the disconnect: `previewDeploymentsDisabled:
  true`, `commandForIgnoringBuildStep = bash pipeline/vercel-ignore-build.sh`,
  `gitForkProtection: true`, `gitProviderOptions.createDeployments: enabled`.
- **`vercel.json` untouched** — last modified by `6ddc5a2` at 15:40, seven hours
  before the disconnect. `git.deploymentEnabled.main: true` is still there.
- **GitHub Pages mirror is green and current** — the `mirror` workflow succeeded
  on every lost push, through `81a246a`. Content is publicly current there. This
  is the reason the outage is stale-site and not lost-work.
- **Vercel CLI auth is alive** (`vercel whoami` → `olegmalkov2023-1685`), but the
  stored token **expires 2026-08-10 08:30:12**.

## Cost so far

**9 pushes to `main` have produced no deployment**, from `4eb4c61` (22:54:13)
through `81a246a` (00:44:35). banyan.city is behind `main` by those 9 pushes.

## The fix — founder browser steps, in this order

1. **vercel.com → Account Settings → Authentication** → add a **GitHub Login
   Connection**, authorising as **`olegmlkvorg`** (repo owner — not `olegmalk`).
2. **Install the Vercel GitHub App** on that identity, scoped to **`banyan-city`
   only**, matching the 08-08 setup.
3. **Project `banyan-city` → Settings → Git → Connect Git Repository** → pick
   `olegmlkvorg/banyan-city`. Production branch must read **`main`**.
4. Confirm `previewDeploymentsDisabled` is still **true** before leaving the page.

After step 3 the next push to `main` deploys normally and the site catches up in
about a minute; no backlog replay is needed, since a deployment builds HEAD. If
no push is pending, the dashboard's **Redeploy** on the latest commit does it.

Do **not** add a payment card at any point — none of this needs one.

### Why the steward did not fix it

The GitHub OAuth flow is a browser step against the founder's credentials, and
`vercel git connect` refuses without it (proof above). A manual `vercel deploy
--prod` was considered and rejected: the working tree carries a large number of
untracked, unapproved media files (`AUDITION-*.wav`, `SAMPLES/`, contact sheets),
and a CLI deploy uploads the working tree rather than the committed state — it
would publish material the founder has not approved, which STEWARDSHIP §6
forbids. The Pages mirror already covers the content-availability gap.

## Backlog: push cadence on high-commit days

Independent of this outage, we burn a deployment event on **every** push to
`main`, and a skipped build is not free. Measured for 08-09:

| | |
|---|---|
| commits on `main` | 75 |
| pushes / deployment events | 56 (of a 100/day Hobby cap — 56% used) |
| peak hour | 15:00, **15 deployments** |
| skipped (`CANCELED`) builds | 10 — each still clones the 1.9 GB repo, ~53 s |
| total build wall time | 61.9 min |

At the 15:00 peak rate sustained, the cap is reachable in under 7 hours. Two
cheap disciplines, neither needing a platform change:

- **Batch lane pushes.** Lanes that commit several records in a row should push
  once at the end rather than per commit. Most of the 75→56 collapse already
  happens by accident; doing it deliberately would roughly halve the remainder.
- **Let the ignore script do its job earlier.** `git.deploymentEnabled` costs no
  event and no clone; `ignoreCommand` costs a 50 s clone before it can answer.
  Records-only pushes are the bulk of the traffic and the strongest argument for
  the repo-size work already noted in STATE.md.

Neither is urgent while we sit at 56%, and neither would have prevented tonight.
