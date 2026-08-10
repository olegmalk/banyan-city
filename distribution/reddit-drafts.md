# Reddit drafts — project-first (2026-07-23)

Founder call 2026-07-23: the videos won't carry attention on their own — the
*project* is the hook. These drafts lead with the mechanism and the radical
transparency, own the roughness, and invite forking. Posting is founder-only;
paste-and-go. Cadence per playbook: max 1–2 posts/day across all subs,
answer every comment same-day. Account: banyan.city (warming; first post
attempt ~Fri 07-25+).

---

## 1 · r/generativeAI — flair "How I Made This" (first post)

**Title:**
I made a 7-episode AI-animated series for $0 — and the whole show is a git
repo: every prompt, every editorial decision, even the budget ledger is public

**Body:**
For the past two weeks I've been building Sapling — a short anime-style
series about an engineer who dies debugging production and reincarnates as
a tree. The videos are rough (first renders, free-quota models), but that's
not really the point. The point is the format:

**The show is a git repository.** Every episode is a folder: script,
storyboard, render prompts, voice casting, and a provenance file naming the
exact model and cost of every clip. The budget ledger is public — the whole
season billed $0 (Alibaba Model Studio free video quota + kokoro-82M running
locally for all the voices + ffmpeg for assembly).

**The story branches like code.** Episodes have rival sequels — sibling
branches — and there's a public rulebook (the founder's "taste file") that
decides which branch leads the canon. Every one of those decisions is
logged with reasoning in the repo. Losing branches are never deleted;
they stay alive and can take the lead later.

**Anyone can write a rival episode.** Declare which episode yours continues
— that's the only rule. There's a no-git submission form, and the pipeline
renders contributor episodes the same way it renders mine.

Site (all 7 episodes free): banyan.city
Repo: github.com/olegmalk/banyan-city

Happy to answer anything about the pipeline — the $0 constraint forced some
fun decisions (local TTS casting per character, keyframe→i2v to hold the
anime style, a designed "slate" system for beats I couldn't afford to
render).

---

## 2 · r/interactivefiction — text post (day 2+)

**Title:**
A branching serial where the audience orders the branches and the author's
taste rules are a public document — Sapling, an experiment in open canon

**Body:**
I've been running an experiment I think this community might find
interesting *as a format*, separate from how it's produced (it's
AI-animated — disclosed up front, and every generation prompt is public).

The story is a tree. Episodes have rival continuations — when a cliffhanger
genuinely splits ("does the tree answer Y or N?"), both branches get made.
Readers react on each episode's page; that reaction data plus a public
taste rulebook (six rules, versioned like a spec) decides which branch
becomes canon. The editorial log citing which rule drove each call is
public. Branches that lose are never deleted — they stay readable and can
be revived.

Anyone can submit a rival episode for any point in the tree; declaring the
parent is the only requirement. The whole thing — scripts, rules, decision
log — lives in a public git repo.

Season 1 is 7 short episodes: banyan.city — and the first real fork (two
incompatible episode 6s, both fully produced) is live now.

Curious what this community thinks of reader-ordered canon vs. classic
CYOA choice — is a "tree you can watch being pruned in public" interactive
fiction, or something else?

---

## 3 · r/webfiction — flair [Serial] (day 3+)

**Title:**
[Serial] Sapling — a branching web serial where readers water the branches
and the pruning log is public (AI-animated, 7 episodes, free)

**Body:**
Premise: an engineer dies debugging production at 3am and wakes up as a
tree. A fugitive goblin who ate one (1) apple becomes his first citizen.
Bureaucracy escalates until the law classifies him as a shrine and demands
a verified miracle by the full moon.

Format is the experiment: episodes have rival sequels, readers' reactions
order them, and a public taste rulebook decides canon — every call logged
with reasoning. Nothing is ever deleted; unloved branches stay alive.
It's AI-animated (all prompts and costs public — the season billed $0)
and yes, the renders are rough; the writing and the mechanism are the
product. You can submit a rival episode for any point in the tree.

banyan.city — all episodes free, no signup, ~90s each.

---

## 4 · r/WritingWithAI — Weekly Tool Thread comment (zero-risk, anytime)

Been building "Sapling," a branching AI-animated serial where the whole
show is a public git repo — scripts, render prompts, a versioned taste
rulebook that picks canon between rival episodes, and a $0 budget ledger.
The interesting writing problem turned out to be the rulebook: extracting
taste into six citable rules that an AI steward can apply between sibling
episodes without me in the loop. banyan.city if anyone wants to poke at it
or write a rival episode.

---

## X thread (when the appeal resolves — project-first reframe)

1/ I made a 7-episode animated series for $0. The videos are rough. The
interesting part is that the show is a git repo — every prompt, every
editorial decision, the whole budget ledger, public.

2/ The story branches like code: rival sequels per episode, a public taste
rulebook picks canon, losing branches never die. Season 1's first real
fork (two incompatible episode 6s, both produced) is live.

3/ Anyone can write a rival episode — declaring the parent is the only
rule. Pipeline renders yours like mine. banyan.city

---

## Rules for all of these (standing)

- AI disclosure up front, always (§7.2 + platform policy).
- Own the roughness — never oversell the renders (founder correction,
  twice). The transparency and the mechanism are the sell.
- Links in body text, not link-posts, until the account has karma.
- Answer every comment same-day; no posting on the dad's account, ever.
