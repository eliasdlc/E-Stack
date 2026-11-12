---
name: modernize
description: Brings a stale PR or branch up to date with its base and decides whether it is still needed, closing it with a written disposition when something merged since already covers it. Also runs the daily PR triage on agentbox. Use only when Elias asks to modernize, poner al dia, actualizar or revisar si sigue haciendo falta a PR or branch, chained or not with "takeover", "full send" or "full stop", or when the triage timer runs. Not for resolving a conflict in work this session owns, and not for branch cleanup.
---

# Modernize

A branch more than three days outside its base is a defect (development-workflow,
Git). This skill is what resolves one: up to date and alive, or closed with its
reason. Call the Skill tool with "development-workflow" first.

## One PR or branch

1. **Is it free?** `git fetch`, then `git ls-remote --heads origin` and the
   ticket's claim. A branch another live session holds is left alone, and the
   report says who holds it.
2. **Is it still needed?** List what merged into the base since the branch
   left it (`git log --oneline <merge-base>..origin/dev`) and read those PRs
   against this one's goal and files. Then answer one of:

   | Finding | Then |
   |---|---|
   | A merged PR does the same thing | Close it: a comment naming the PR that covers it, then `gh pr close`. The branch stays, as Git says |
   | Part of it is covered | Keep only what is not; say which commits became redundant |
   | Nothing covers it | Bring it up to date (step 3) |
   | It contradicts what merged since | Stop and report the conflict of intents; that choice is Elias's |

3. **Bring it up to date** by merging the base into the branch
   (`git merge origin/dev`) and integrating both intents in any conflict.
   Never rebase or force-push: another machine may hold the branch. Then run
   the repo's checks and redo the Proof rows the merge invalidated.
4. **Hand it on.** With "full send" or "full stop" in the message, run that
   mode. Otherwise leave it ready and say so.

Report per PR: the finding, the merged PR that decided it, and the checks with
their numbers.

## Daily triage

The T3 scheduled task "Daily PR triage" runs this section on agentbox once a
day with Haiku, as a thread in Elias's sidebar, because the scan is wide and
cheap and he decides from the report, not from the model. Nobody is in front of
it, so it reads and reports only: it merges, closes, pushes and comments
nothing, and the deny list of its project (`agents pr-triage --setup`) holds it
to that.

1. List the open PRs of every repo Elias owns
   (`gh search prs --owner eliasdlc --state open`) and the open PRs of the
   team repos in his workspace contracts. Only this triage reads across
   repos: a request to modernize one PR or branch, or a question about open
   PRs, stays in the repo it names or the current one.
2. For each one older than three days, or with new activity in the last
   24 hours, apply step 2 above by reading only (`gh pr view`, `gh pr diff`,
   the merged PRs since its base).
3. Keep at most 8, the ones where an action moves something, and give each its
   action: **merge** (criteria likely met), **takeover**, **modernize**,
   **close** (name the PR that covers it) or **needs you** (a decision only he
   makes). The rest go in one line with their count.
4. Publish it as a Postplan `decisions` round in Spanish, because Elias reads
   it, one question per PR, options
   being the actions with the recommended one marked, under the standing
   authorization. Call the Skill tool with "visual-briefing"
   for the recipe. If the upload fails, save the round as a
   dated HTML file in `~/Documents/Personal/dev/triage`, and say so in the
   thread.
5. When nothing qualifies, publish nothing and log "triage: nothing to act on".

His answer comes back in a normal session as a decision code, and each action
then runs there: "3 takeover, full stop".

<!-- Adapted from Theo Browne's "modernize" skill (rebase on main, check whether something merged covers it, close it if so), described in his live of 14 Oct 2026; his file was not public. Rebase became merge because Elias's Git rules forbid rebasing a branch another machine may hold. The daily triage is Theo's nightly scheduled PR triage (cheap models scan, at most 8 PRs reported); Elias picked it daily and with Haiku (7B, note "Pero con Haiku") on 15 Oct 2026, when one of his two Max accounts sat at 93 percent of its weekly limit. -->
