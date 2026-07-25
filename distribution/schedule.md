# Season 1 drop schedule — one episode per day, 21:00 local

Posting is founder-only; this file is the run-sheet. **Rebased 2026-07-22:**
the original 12-hour plan didn't survive contact with real life (only eps
1–2 shipped), so the cadence is now one episode per evening. Drop files are
staged in `~/Desktop/banyan-drops/` (an auto-organizer sweeps ~/Downloads);
`genomes/*/leaves/`. Post the same clip to TikTok + YouTube Shorts +
Instagram Reels each slot; pin the comment from `launch-kit.md` §4.

**The reminder is local now:** a launchd agent
(`city.banyan.drop-reminder`, script at `distribution/reminder/remind.sh`)
fires daily at 21:00 — macOS notification, the tree's own voice announcing
the episode (kokoro bm_fable, $0), caption pre-copied to the clipboard,
the drops folder opened. After the last drop it announces the season complete and
unloads itself. The earlier cloud routines are dead (environment deleted).

| # | When (local, +04) | Episode | File (in ~/Desktop/banyan-drops) | Caption |
|---|---|---|---|---|
| ✅ | 2026-07-20 | 001 — Capability Inventory | `banyan-001-anime-v2.mp4` | A |
| ✅ | 2026-07-21 | 002b — The First Citizen | `banyan-002b-episode.mp4` | B |
| ✅ | 2026-07-22 (posted ~23:30) | 003b — One Leaf for Yes | `banyan-003b-episode.mp4` | C |
| ✅ | 2026-07-24 (recast voices, posted midday) | 004 — Shade | `banyan-004-episode.mp4` | D |
| 5 | 2026-07-24 21:00 | 005 — The Assessor | `banyan-005-episode.mp4` | E |
| 6 | 2026-07-25 21:00 | 006a — The Miracle Clause | `banyan-006a-episode.mp4` | F |
| 7 | 2026-07-26 21:00 | 007a — The Demo (finale) | `banyan-007a-episode.mp4` | G |

> **Open, and the founder's call (2026-07-25):** slots 5-7 are staged as
> **pre-molt cuts** — 4 to 6 shots each, which is the exact thing dad
> flagged ("the video is not matching the audio at all"). Cycle 007 rewrote
> all seven scripts to one shot per beat, but the footage for the new cuts
> does not exist yet (166 shots, rendering started on the free Kaggle
> floor). So the choice is: keep the daily cadence and post cuts we already
> know are the weak version, or pause the drops until the re-rendered
> episodes exist and lose the posting rhythm. Not a steward decision either
> way — posting is founder-only, and so is deciding to stop. The reminder
> agent keeps firing at 21:00 until told otherwise.

After #7: the season supercut (`banyan-sapling-season-1-COMPLETE.mp4`,
10:41) as a "binge the whole season" post, and the fork post — "the tree
chose A" runbook in `launch-kit.md` §5. Reschedule = edit this table +
the dates in `reminder/remind.sh`.

## Captions (per episode)

**A — 001:**
An engineer dies debugging production at 3am and wakes up as a tree.
Sapling, ep 1. An AI-animated series that branches — viewers pick which
sequel survives. Everything about it is public, even the budget ($0).
🌳 banyan.city
#anime #aianimation #isekai #webseries

**B — 002b:**
Day 2 as a tree: a fugitive goblin is hiding behind me. He's wanted for
eating one (1) apple. I have one fruit to my name and a decision to make.
Sapling ep 2 · full series free at banyan.city
#anime #aianimation #isekai

**C — 003b:**
He asked if I can hear him. One leaf for yes. Nothing for no.
"Did you MEAN to hit my head with that fig?" …long pause… one leaf.
Sapling ep 3 · banyan.city
#anime #aianimation #wholesome

**D — 004:**
Naming a town is hard when the founding committee is a goblin and a plant.
"Newhaven?" No leaf. "Greenrest?" Nothing. "…it's just shade." BOTH LEAVES.
Sapling ep 4 · banyan.city
#anime #aianimation #cozy

**E — 005:**
The tax man came to assess a town with one shack, three rocks, and a tree
that answers questions. He counted the rocks individually.
"Occupation?" …one leaf. "Noted."
Sapling ep 5 · banyan.city — and next, YOU pick what happens
#anime #aianimation #isekai

**F — 006a:**
The verdict: the talking tree is legally a SHRINE. The fugitive goblin is
now its official keeper. One catch — they owe the kingdom a verified
miracle by the full moon.
Sapling ep 6 · full season at banyan.city
#anime #aianimation #interactivefiction

**G — 007a:**
They rehearsed a miracle for two weeks. The wind ruined it in four seconds.
What happened next was not rehearsed.
Season finale · whole season free at banyan.city · the story branches —
you pick what happens next
#anime #aianimation #interactivefiction

## Standing rules (every post, every platform)

- **Always enable the platform's AI-generated content label** (TikTok's
  AIGC toggle, YouTube's altered-content disclosure, etc.) — honest per
  §7.2, required by platform policy, and unlabeled AI content gets
  suppressed. Adopted 2026-07-21 after the ep-1 repost.
- Post from the app on a warmed account, not the web uploader.
- Platforms (2026-07-21): TikTok @banyan.city + YouTube Shorts @banyancity
  ("Altered content: Yes") + Instagram Reels @banyan.city (Made-with-AI
  label) + Snapchat Spotlight (lowest priority). Mirror already-dropped
  episodes freely; NEW episodes follow the daily schedule on all platforms.
- X is suspended (appeal pending); Reddit waits for account age (~07-24+,
  playbook ready).

## Mechanics per slot (5 min)

1. 21:00 — the tree speaks; caption is already on the clipboard.
2. Post the file + caption on each platform (native upload, not links).
3. Pin the open-source comment (launch-kit §4).
4. Drop the episode link in the node's GitHub reactions issue.
5. That's it — reactions harvest into the repo nightly on their own.
