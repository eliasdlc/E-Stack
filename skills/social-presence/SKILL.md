---
name: social-presence
description: Grows Elias's audience on X, LinkedIn and GitHub in his own voice. Finds what he shipped (harvest) and what developers, AI builders and the Dominican tech scene discuss this week (trend radar), then drafts posts, threads, replies, quote posts and LinkedIn posts and comments that he publishes himself, linted for AI tells. Also owns his profile audit (X bio, pinned post, LinkedIn, GitHub README, decruce.dev), the campaign calendar (ConoceRD launch, build in public, web clients) and the weekly review of his numbers. Use for "hazme un tweet", "post para LinkedIn", "que publico hoy", "un thread de esto", "a quien le respondo", "como vamos con los seguidores", when he pastes his weekly numbers, and after a release or launch worth announcing, in English or Spanish. Not for post graphics in Figma (figma-assets), a message to one person, release notes, or code changes to his site.
---

# Social presence

The goal is always the same: more followers, and his work in front of people
who can use, hire or fund it. Followers are the score; inbound leads (web
clients, ConoceRD users, offers) are the money. Every draft serves one of the
two, and the weekly review says which moves do.

**Drafts only.** Elias publishes everything himself, because a post speaks for
him. The skill hands him ready-to-paste text and, for a reply or a quote, the
link to the post it answers. It never logs in, posts, follows or likes.

## Where things live

| What | Where | Why there |
|---|---|---|
| Procedure, scripts, distilled voice guide, strategy | this skill (`scripts/`, `references/`) | Versioned, reviewed, read on every draft |
| Profile: facts with dates, accounts, goals, campaigns, harvest boundaries | `~/Documents/Personal/dev/social-presence/profile.json` | Changes weekly; facts he corrects are written here the same turn |
| Raw voice corpus, blind test key | `<data>/voice/` | His private words stay out of Git |
| Accounts worth engaging | `<data>/research/` (latest dated file) | Accounts go stale; re-verify monthly |
| Ledger, follower snapshots, leads | `<data>/ledger.csv`, `followers.csv`, `leads.csv` | His numbers, outside the agents repo |
| Week packs, reviews, trend digests, audits | `<data>/packs/`, `reviews/`, `trends/`, `audits/` | Dated, one per run |

`<data>` is that folder, at the same path on the laptop and on agentbox.
`python3 scripts/sync.py` mirrors the working data between the two, both
ways, deleting nothing: `profile.json`, the three CSVs, `packs/`, the
published `plans/*-phone.html`, `research/`, `trends/`, `reviews/` and
`harvest/`. Nothing else crosses, in either direction: `voice/`, `audits/`,
`evidence/` and every other plan stay on the machine that wrote them, because
they can quote his own words. The CSVs merge row by row, so numbers pasted on
either machine all survive; in a row both sides hold, the side that changed a
field since the last mirror wins it, so a correction sticks. Any other file goes to the newer copy, and the copy it replaces stays
next to it as `<name>.replaced~` on that machine only. Run it before reading `<data>`
and after writing it; on the laptop `social-presence-sync.timer` (in `systemd/`,
copied into `~/.config/systemd/user/` by hand like the class mirror) runs it
every 30 minutes.

## Before writing anything

1. Read `references/voice.md`. Every draft is written to it, not to a generic
   developer voice.
2. Read `<data>/profile.json`: the facts, the goals, the active campaign and
   his decisions (language, demo businesses, paid sources), which bind every
   draft.
3. Read `references/strategy.md` for the daily ceiling, the mix and what the
   evidence says works.

## The daily menu

Run when he asks what to post, and when something big ships.

1. `python3 scripts/harvest.py`: what he shipped since the last run, ranked,
   each story with its evidence link. A private repository gives the outcome
   only (what a user can now do), never its internals or a link.
2. `python3 scripts/trends.py`: this week's conversation per group (ai,
   flutter, web, indie, dr-latam, general) with links. Add `--group` to narrow.
3. Choose moves up to the ceiling in `references/strategy.md`, in its mix:
   most of the volume in the first weeks is replies, because a reply on a
   bigger account is seen by its audience and an original post from a small
   account is seen by almost nobody.
4. Write each move in his voice, one ```post block per move (format below).
5. `python3 scripts/lint.py <pack>.md` until it prints `0 findings`. Fix a
   finding by rewriting the sentence the way he would say it, never by
   weakening the rule.
6. Hand him the menu: in a chat he is reading, each block ready to paste with
   the link it answers and one line on why it is worth posting today; for a
   week pack, the phone page (below).

## Hand-over: the phone page

He publishes from his phone, so a week pack reaches him as one page: Spanish
UI, "Abrir en X" on every X original and on the first part of a thread (the
composer opens with the text in it), "Copiar" on every block, threads split
into numbered parts, optional items folded.

1. `python3 scripts/page.py <data>/packs/<monday>-week-<n>.md` writes
   `<data>/plans/<pack name>-phone.html`. It lints the pack first and builds
   nothing while a finding is left.
2. `python3 ~/.claude/skills/visual-briefing/postplan/build.py <page> --check`, then publish it
   with `BY=standing` (his standing authorization for reader pages; nothing
   about clients goes on it). The first upload writes the page's
   `postplan-draft` id into the file, and `page.py` carries it into every
   rebuild, so republishing keeps the same link all week.
3. Give him the link: in the chat, or as the last line of a scheduled run's
   thread.

The page shows only what sits under a `##`; what comes before it is the
agent's provenance. It translates the fixed words of a pack (weekday and
month in a `##`, the move in a `###` such as Original, Thread, Reply on,
Quote post, LinkedIn post, "optional", and note prefixes such as Reply to,
Quote, Link, Why) and shows everything else as written, so the rest of each
heading and every note under it is written in Spanish, for him.

### The moves

| Move | When | Shape |
|---|---|---|
| Original post | Something shipped, learned or decided | One idea, under 280 characters, a concrete detail a reader can check |
| Thread | A story with steps: a launch, how the agent system works, a bug hunt | 4 to 7 posts, the first one stands alone, the last one links the thing |
| Reply | A post from an account in the list, under 3 hours old, where he has real experience | Adds a fact, a number or a counterexample from his own work; never "great post" |
| Quote post | A trend item he can add an angle to | His angle in the first line, the link quoted |
| Repost with comment | Something from the DR or LatAm scene worth amplifying | One line of why it matters to him |
| LinkedIn post | The week's best story, retold for clients and recruiters | 600 to 1,300 characters, first two lines carry the hook, link in the first comment |
| Comment on another's post | LinkedIn posts by Dominican founders, communities, potential clients | Two to four sentences, a specific point |

### Pack format

A pack is Markdown. Only fenced blocks whose info string starts with `post`
are drafts, so context and links can sit around them:

    ## Tue 4 Nov, reply
    Replying to: https://x.com/<account>/status/<id> (why: they asked about offline maps in Flutter)

    ```post reply x
    the draft text
    ```

Inside an X block, a line with only `---` separates the posts of a thread;
the lint measures each one against 280 characters, counting a link as 23.

## Scheduled runs on agentbox

Two T3 scheduled tasks on agentbox (America/Santo_Domingo) run this skill
without him, each run a thread he can open. Their prompts only point here, so
the procedure changes by PR. Both start the same way:

1. `git -C ~/dev/wt/agents/social-presence-runner fetch -q origin` and
   `git -C ~/dev/wt/agents/social-presence-runner checkout -q --detach origin/dev`.
   `$SKILL` below is `~/dev/wt/agents/social-presence-runner/skills/social-presence`,
   and every script named in this section is `python3 $SKILL/scripts/<name>`;
   `build.py` is `~/.claude/skills/visual-briefing/postplan/build.py`. The installed
   generation lags behind `dev`, and a run that read it would miss these
   scripts.
2. `python3 $SKILL/scripts/sync.py`. If the laptop is asleep it fails; go on
   with the local copy and say so in the run's last message.
3. Read `$SKILL/SKILL.md`, `$SKILL/references/voice.md`,
   `$SKILL/references/strategy.md` and `<data>/profile.json`, as for any
   draft.

A script that fails gets one retry, then the run goes on without it. Give
`trends.py` up to ten minutes; it fetches many feeds. The run's last message
names every step that failed or came back thin (the mirror, a trend source
refusing, a harvest with nothing new), so a quiet degradation shows up in the
thread. Facts follow the same rule as in a session: every claim is in the harvest, a
public page or his own words; nothing posts anywhere; no client names.

### Sunday 18:00: next week's page

1. If `ledger.csv` or `followers.csv` has rows dated from this week's Monday
   (six days ago) to today, run `python3 $SKILL/scripts/review.py --week <that Monday>`
   and steps 3 and 4 of Weekly review, and keep its one change for the
   message.
2. `harvest.py --since <this week's Monday>` (an explicit window, so a retry
   cannot narrow the next one) and `trends.py`, then write
   next week's pack. If a `<data>/packs/<next monday>-week-*.md` already
   exists, that is the pack: it may carry his edits, so build on it, never
   over it. Otherwise it is `<next monday>-week-<n>.md`, `<n>` the latest
   pack's plus one. One `##` per day, Monday to Sunday. An X original only on
   the days the active campaign has a beat, within that week's daily ceiling
   in `references/strategy.md`;
   the other days are left for the 07:30 run. Each post in the language
   `decisions.language` gives its topic; at most one optional LinkedIn post;
   a `### X replies` item on Monday telling him to paste the posts he wants to
   answer, because replies need a post under three hours old and the X API is
   not used. Provenance above the first `##`, Spanish headings below it.
3. `lint.py` on the pack until `0 findings`, then the hand-over: `page.py`,
   `build.py --check`, publish with `BY=standing`.
4. `sync.py`. The run's last message carries the new link, the number of
   posts and the review's one change when step 1 ran.

### Daily 07:30: the post of the day

1. Find this week's pack: the `<monday>-week-<n>.md` whose Monday is today or
   up to six days before. None: say so in the thread and stop. If today's
   `##` already has an `Original del día` and the published page already
   shows it (`curl` the link, look for its first words), today's run already
   happened: say so and stop. If the pack has it and the page does not, an
   earlier run failed after writing it: go on from step 3.
2. `harvest.py --since <yesterday>` and `trends.py`. Write one new X original
   for today on what shipped in the last day, or else on today's best trend
   item he has a real angle on, never repeating a post already in the pack.
   Add it as the first item under today's `##` (a missing `##` goes in date
   order), headed `### Original del día: <tema>`. When today already holds
   as many originals as this week's daily ceiling in `references/strategy.md`
   allows, head it `### Original del día, en vez del de abajo (opcional): <tema>`,
   so it folds and he picks one.
3. `lint.py` until `0 findings`, `page.py`, `build.py --check`, publish with
   `BY=standing`: the same link, since the page keeps its draft id.
4. `sync.py`. The run's last message carries the link and the new post.

## Boundaries

| Shown | Never shown |
|---|---|
| Public repositories, releases, live sites, his own projects (ConoceRD, Kino, the agent system as a story, Barcamp RD work) | Anything from ~/Documents/Finanzas, Personal content beyond his writing style |
| The outcome of private work: what users can now do | Private-repo internals, code, tickets, client data, secrets |
| Public events and communities | MEK Technologies work, university assignments (unless he says so) |
| Demo sites for real businesses, only in the form `profile.json` decisions allow | Names and logos of businesses he built unsolicited demos for, unless the owner said yes |

The harvester enforces the repository side from `profile.json`
(`harvest.exclude_owners`, `exclude_repos`, `doc_projects`). A story that
would need a boundary crossed is dropped, not softened.

## Profile audit

Re-run when something big ships (a launch, a public repo, a new client site)
and monthly. Check each surface against one test: a stranger understands who
he is, what he builds and why to follow, in five seconds.

| Surface | What to check |
|---|---|
| X | Display name, bio (what he builds, for whom, one proof), pinned post (the best current proof), banner (a real screen of his work), link |
| LinkedIn | Headline (role plus proof, not "student"), About (three short paragraphs: who, what he ships, how to hire him), Featured (ConoceRD, a client site, the agent write-up) |
| GitHub | Profile README (who, three projects with links, how to reach him), pinned repositories (public, with READMEs and screenshots), bio |
| decruce.dev | Above the fold says the same thing as the X bio; contact path for a business is one click |

Write the audit to `<data>/audits/<date>-profile-audit.md` with the current
text quoted and the proposed text ready to paste.

## Campaigns and goals

Goals and campaigns live in `profile.json` (`goals`, `campaigns`), each number
labeled `estimate` until a review replaces it with a measured one. A campaign
has dated beats; the daily menu fills the active beat before anything else.
Proposing a new campaign: name its goal metric, its beats with dates, and what
the review will look at to call it working.

## Weekly review

Every Sunday, or when he pastes numbers:

1. Put his numbers in `<data>/ledger.csv` (one row per post, `lang` en or es), `followers.csv`
   (one snapshot per platform) and `leads.csv` (no names: channel, kind,
   status). `python3 scripts/review.py --init` creates them.
2. `python3 scripts/review.py --week <monday>` writes the report to
   `<data>/reviews/` and compares followers, impressions and leads with pace.
3. Change the plan on what it shows: more of the move with the best follows
   per post, less of the worst, the ceiling down if replies stop converting.
   After three weeks, move the language split by the "By language" section.
   Write the change into `profile.json` with the date and the number behind it.
4. Tell him in the chat: where he is against pace, the one change, and the
   next week's beats.

## Voice upkeep

Rebuild the corpus when the guide starts to drift, or every couple of months:

    python3 scripts/voice_corpus.py --out <data>/voice/corpus.jsonl \
      --vault ~/Documents/Personal/Life --vault "$HOME/Documents/Personal/Segundo Cerebro"

The guide changes only from evidence in the corpus or from his correction,
and a changed guide earns a new blind test: five of his real texts and five
generated on the same topics and lengths, unlabeled, and his guess recorded in
`<data>/voice/`. Where he can still tell, the guide says why.

## Paid sources

The X API is the only way to read X directly (search, a timeline, the posts to
reply to). It costs money, so it runs only when he asks for it; until then,
propose it with its current price and what it would add. Free sources stay
the default.
