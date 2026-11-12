# Strategy

What the evidence says about growing a developer and builder audience from
near zero in 2026, distilled from the research of 30 Oct 2026 (full notes and
every source in `<data>/research/2026-10-30-strategy.md`). Each claim is
labeled: **E** evidence (code, platform statement, measured study), **O**
opinion (creator advice, vendor blog), **I** our inference from them. Re-check
the X weights when X publishes a new version of its ranking code.

## The daily ceiling and the mix

Answering people who reply to him is uncapped and comes first. Beyond that:

| Week | X originals per day | X substantive replies per day | LinkedIn |
|---|---|---|---|
| 1 | 1 | 8 to 10 | 3 posts a week, 5 comments each weekday |
| 2 | 1 to 2 | 10 to 12 | same |
| 3 (launch week) | 2 | 12 | same, launch post on launch day |
| 4 | 1 to 2 | 12 to 15 | same |

Hard limits: never more than 3 originals or 15 replies a day, and no generic
reply ever (I, from the weights below). About one original per five to eight
replies. After week 2 the weekly review replaces these numbers with his own.

## What works, by strength of evidence

| Tactic | Label | Source |
|---|---|---|
| Replies carry the most weight in X ranking: a reply scores 5.0 against 0.66 for a like, and a reply between mutual followers adds 15 | E | X ranking code, github.com/xai-org/x-algorithm, read 30 Oct 2026 |
| Negative feedback is expensive: block -31.2, mute -58.8, report -234. A generic or off-topic reply risks it | E | same |
| Write things people send: copy-link share 20.0, DM share 5.0, quote 5.0 | E | same |
| Several originals in one day decay: each extra post by the same author is multiplied down | E | same |
| Consistency compounds: posting in 20 or more of 26 weeks showed 450% more engagement per post | E (observational, 100K+ users) | buffer.com/resources/creator-growth-playbook, 10 Jun 2026 |
| Answering every comment correlates with about 30% more engagement on LinkedIn and about 8% on X | E (correlational) | Buffer, same |
| LinkedIn infers a new member's interests from the headline and job title, so the headline decides who sees him | E | linkedin.com/blog/engineering, 12 Mar 2026 |
| Links are not penalized by rule on X; video weight is 0.0 at the defaults | E for the code and the statement, disputed by creators | X code; X product head statement, Aug 2026 |
| Threads, carousels and posting times | O | vendor blogs, see the research notes |

## Language

No platform publishes reach by language, so this is inference (I). Default to
English for developer content on X and LinkedIn, because the dev, AI and indie
audiences that follow builders read English. Use Spanish for ConoceRD, for
Dominican tech community moments and for local business content. One language
per post, never the same post in both. Test about 80/20 English to Spanish on
X and 60/40 on LinkedIn for three weeks, then let the review decide, using
the `lang` column of the ledger. **His decision**: the profile records it.

## Where his clients actually are

Dominican small businesses buy on Instagram and WhatsApp (73.4% and 71.1% of
SMEs, eldinero.com.do, 13 Jul 2023, dated, E). X and LinkedIn bring
credibility, global leads and offers more than local web clients. The
web-client campaign therefore needs a proof artifact he can send on WhatsApp
(a case page, a before and after), and the posts point at it.

## Launch playbook for a Play Store app

All vendor advice (O), arranged by us (I):

- **Before launch:** build-in-public screens and short screen recordings, one
  real detail each (the offline route, arrival with the diary, the map on an
  old phone). Show up at the community events in the calendar.
- **Launch day:** one post with a screen recording and the direct Play link,
  the story thread, a LinkedIn post, a Spanish post for the Dominican
  audience, and every reply answered the same day.
- **Week after:** a numbers post, a "what broke" post, a request for Play
  reviews, the best posts retold on LinkedIn.
- Product Hunt is low fit: a local tourism app for a global tech audience.

**Play gate (E):** a personal developer account created after 13 Nov 2023
needs a closed test with 12 testers for 14 days before production access
(support.google.com/googleplay/android-developer/answer/14151465). The launch
date in a campaign is only as real as that gate.

## Labeled estimates for goals

Vendor ranges (100 to 2,000 followers in month one) come from tools and
survivors, so they were discounted. For an account starting near zero, posting
daily and replying as above (all estimates):

| Day | X followers | LinkedIn new followers | Original post impressions | Qualified leads from social |
|---|---|---|---|---|
| 30 | 30 to 150 | 15 to 80 | 20 to 150 each | 0 to 1 |
| 60 | 80 to 400 | | | 0 to 1 |
| 90 | 150 to 800 | | | 0 to 2 |

The goals in `profile.json` sit inside these ranges and are replaced by
measured values after week 2.

## X API

Pay per use, no free tier (docs.x.com/x-api/getting-started/pricing, fetched
30 Oct 2026): post read $0.005, user read $0.010, own data $0.001, trends
$0.010 per request, cap 3M post reads a month. 100 post reads a day is about
$15 a month. It would add direct search for posts to reply to and real X
trends. It runs only when he asks for it (he chose not to buy it on 30 Oct).
