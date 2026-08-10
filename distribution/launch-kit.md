# Distribution launch kit — drafts only

Steward-drafted copy for announcing the tree. **Posting is a founder-reserved
action** (CLAUDE.md operating rules): nothing here is published by the
pipeline or the steward, ever. Edit freely — these are candidates, not canon;
your voice wins. Every draft discloses AI authorship, matching the repo's
provenance rule (§7.2).

Suggested order: X + Reddit now; HN LATER — as of 2026-07-20 HN is
temporarily blocking Show HNs from new accounts (news.ycombinator.com/showlim).
Plan: the founder participates on HN normally for a few weeks (real comments,
no self-promo games — do NOT dodge the gate by dropping the 'Show HN' prefix),
then posts §1 with a living tree behind it. Each post links a different door
into the tree.

---

## 1 · Show HN

**Title:**
Show HN: A branching AI-animated series grown in a git repo – season 1 for $0

**Body (post as your first comment on the submission):**

Banyan City is a story "tree": an AI-animated micro-drama whose episodes branch
— rival sequels coexist, and viewers' reactions + one human's published
taste rules decide which line leads. The entire production is a public git
repo: scripts, render prompts, voice casting, governance, and a spend
ledger.

The part HN might find interesting:

- Season 1 (five voiced, subtitled episodes) rendered yesterday for $0
  billed: open Wan weights via a provider's free API quota, local Apache-2.0
  TTS (kokoro-82M) for the full cast, ffmpeg assembly. The public ledger
  records every generation at $0 with list prices noted (~$21 of video).
- Episodes are "leaves" — one render of a canonical script, never the final
  one. Anyone can re-render any episode better (there's a Kaggle notebook
  that does it on free GPUs) and submit it; screening + the taste file pick
  the leading leaf. Quality is designed to be crowdsourced; story and taste
  stay curated.
- Authorship as an auditable system: my taste is extracted into a versioned
  rules file; a model writes candidate episodes as delegated steward and
  must cite rule IDs in every commit. When it can't choose between two
  continuations it ships both as siblings — the tree's tip right now is a
  live fork.
- Reactions are GitHub issue emoji, harvested nightly into versioned YAML.
  Forking the whole project under a new name is explicitly encouraged; the
  one unamendable rule is that the right to branch can never be revoked.

Live tree: https://banyan.city
Repo: https://github.com/olegmalk/banyan-city

The renders are rough — first leaves, honestly labeled as such on the site.
The experiment is whether an open pipeline + right-to-branch can grow them
good. Happy to answer anything about the governance or the pipeline.

---

## 2 · X / Twitter thread

**1/**
Yesterday this was a text project. Today it's a five-episode animated season —
rendered, voiced, subtitled — for $0 billed, with the entire production
trail public in a git repo.

Banyan City: an AI-animated series that branches. banyan.city 🌳
(attach: 20-30s clip from ep 1)

**2/**
The story: an engineer dies debugging prod at 3am and reincarnates as a
banyan sapling. Can't move, can't fight. Can only sense, grow, and make the
space around him worth staying in.

By episode 5 he has a town, a tax problem, and a legal category.

**3/**
The structure is the experiment: when a plot point has two honest
continuations, both get rendered as sibling branches. The tip is a live fork
RIGHT NOW — same cliffhanger, two rival payoffs. Viewers react; taste
decides; neither is ever deleted.

**4/**
Every episode is a "leaf" — one render of the script, never the last word.
The renders are rough, on purpose and honestly labeled. Anyone can re-render
any episode better on free GPUs (the notebook is in the repo) and submit it.
Quality is crowdsourced; the story is curated.

**5/**
The authorship experiment: my taste lives in a versioned rules file. An AI
steward writes under it and cites rule IDs in every commit. When I wince, I
don't override the commit — I amend the rules, publicly. A legal system for
narrative.

**6/**
Season 1 is free, unwalled, and forkable — the one unamendable rule is that
the right to branch can never be cut.

Start here: banyan.city 💧

---

## 3 · Reddit (adapt per community)

**Suggested communities & angle:**
- r/InternetIsBeautiful → the explorable tree site
- r/WritingWithAI / r/ArtificialInteligence → the taste-file + steward model
- r/rational → the governance/promise design (right-to-branch as constitution)
- video-gen communities (r/aivideo etc.) → the T3 trials, model bake-off in the open

**Title (general):**
I'm growing a branching AI micro-drama in a public git repo — every script, render decision, and dollar is auditable, and anyone can branch the story

**Body:**

The premise: an engineer dies at 3am debugging production and reincarnates in
a fantasy world as a banyan sapling — immobile, tiny, and very much still an
engineer about it.

The structure is the experiment. Instead of one linear plot:

- Episodes form a lineage tree. Anyone may write a continuation of any
  episode; the only obligation is declaring your parent. Nothing is ever
  deleted — rejected branches just wait for readers to water them.
- The author's taste is extracted into a public rules file, and an AI steward
  writes candidate episodes under it, citing which rules drove each choice in
  the git log. Disagree with a call? The fix is a public diff to the rules
  file, not a quiet edit.
- The current tip is a live fork: one cliffhanger, two competing payoffs
  (a civic-comedy one and a mythology one). Reactions decide which leads.
- Season 1 (five voiced, animated episodes) rendered for $0 billed on provider
  free quotas + local open models — the public ledger records every
  generation. Episodes are "leaves": anyone can re-render one better on free
  GPUs (notebook included) and submit it. The renders are rough and labeled
  as such; regrowing them is the point.

Site (no git needed): https://banyan.city
Repo: https://github.com/olegmalk/banyan-city

Full disclosure: episodes past the root are model-written (labeled in each
episode's provenance metadata), curated by a human taste file. Feedback on
the governance design is as welcome as feedback on the story.

---

## Post-launch follow-up stock (use as replies or later posts)

- "The nightly 'sap harvest' cron reads emoji reactions off GitHub issues and
  commits them as YAML — the tree's vital signs are version-controlled."
- "Every AI-video candidate model runs the same three shots, scored in the
  open: banyan.city/trials"
- "The founding promise is one paragraph, and one clause is unamendable: the
  right to branch may never be cut."

---

## 4 · Episode drop copy (001 anime release, added 2026-07-19)

The file to post everywhere: `banyan-001-anime-v2.mp4` (Desktop) — 72s,
9:16, watermark-free, subtitled. Platforms: TikTok / YouTube Shorts /
Instagram Reels / X. Posting is founder-only; paste-and-go drafts:

**TikTok / Shorts / Reels caption:**
An engineer dies debugging production at 3am and wakes up as a tree.
Episode 1 of Sapling — an AI-animated series that BRANCHES: every episode
has rival sequels, and viewers decide which one leads. Whole show + all
its source is public. 🌳 banyan.city
#anime #aianimation #isekai #webseries #interactivefiction

**X post:**
Episode 1 of Sapling is live — an engineer reincarnates as a tree, rendered
in anime, voiced, subtitled, $0 in generation costs, every prompt and
decision public in git.

The story branches. You pick what survives. banyan.city

**Pinned-comment / reply (all platforms):**
Every episode's script, render prompts, costs, and even the editorial
rulebook are public: github.com/olegmalk/banyan-city — you can write a
rival next episode yourself. Declaring the parent episode is the only rule.

---

## 5 · Fork day runbook (Mon 2026-07-27 target, after the Sun finale)

UPDATE 2026-07-22: the trunk call is MADE — 006a "The Miracle Clause" is
canon (edl.md, steward under founder delegation). Reframe the posts: not
"you decide" but "the tree chose Ending A — Ending B lives on as a branch;
water it if you'd have chosen differently." Same two videos, stronger story:
the governance actually ran.
Files: `banyan-006a-THE-MIRACLE-CLAUSE.mp4` + `banyan-006b-RECONCILIATION.mp4`
(Desktop/Downloads). Post A first, B ~2h later, all platforms, AI labels on.

**TikTok/IG caption (video A):**
Episode 6 has two endings. You pick which becomes canon 🌳
This is Ending A: the tree is now legally a shrine. Miracle due by full moon.
Ending B + how to vote: banyan.city
#anime #aianimation #interactivefiction

**TikTok/IG caption (video B, ~2h later):**
Ending B, for the undecided: the kingdom has been reading the sky's debug
overlay for centuries — and the sky says this town doesn't add up.
Both endings + voting: banyan.city 🌳
#anime #aianimation #interactivefiction

**YouTube title A (≤100):** Sapling ep 6, Ending A: the tree is now legally a shrine — you pick which ending becomes canon
**YouTube title B (≤100):** Sapling ep 6, Ending B: the kingdom has been reading the sky — you pick which ending becomes canon
(descriptions: reuse the caption + banyan.city/watch + banyan.city/create links)

**Reddit (account should clear the age gate ~today):** r/generativeAI post
from §the playbook first; r/ClaudeAI retry with the steward angle;
r/interactivefiction with the mechanism angle. One sub per day, comments
answered same-day.

**Mechanics honesty (for replies):** the call was made by the AI steward
under the founder's published taste rules, cited line-by-line in the public
editorial log (genomes/sapling/edl.md, 2026-07-22). Ending B is not dead:
branches never die here — react on issue #14 and it keeps growing.
