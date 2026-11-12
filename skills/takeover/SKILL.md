---
name: takeover
description: Takes over unfinished work and carries it to a PR that lands or a written disposition, keeping credit for whoever started it. Use only when Elias asks to take over, retomar, rescatar or terminar a PR, a branch, a worktree, a failed or abandoned agent thread or delegated task, or a teammate's work, alone or chained with "full send", "full stop" or "modernize". Not for continuing work this session already owns, and not for a pasted handoff, which development-workflow executes as the brief.
---

# Takeover

The work arrives as a PR link, a branch, a worktree path, a T3 thread id or a
failed delegated task. Its author may be a teammate, a contributor or one of
Elias's own agents that died mid-task. This session becomes its owner: the
original goal is finished here, or the work is closed with the reason written
down. Call the Skill tool with "development-workflow" first; its Git, proof and
merging rules govern everything below.

## 1. Recover the intent

Read, in this order, until the goal is clear: the ticket it links, the PR body
and its comments, the thread or task transcript (`t3_thread_read`, or
`task_status` for a delegated task), the commits (`git log base..branch`) and
the diff. Write the original goal in one line and the requirements as ledger
rows. The goal is what the work was for, not what its diff happens to do.

## 2. Check that it is free

A branch another live session or machine holds is not taken: `git fetch`,
`git ls-remote --heads origin`, the ticket's claim and, for agentbox,
`ab estado` with a short timeout. Claimed and live: stop and say who holds it.

## 3. Decide: continue or rebuild

| The work | Then |
|---|---|
| Sound and on the current base | Continue on its branch |
| Sound but stale | Call the Skill tool with "modernize", then continue |
| Right idea, unreliable code (failing checks nobody fixed, a half rewrite, a design that fights the repo) | A new task branch from current `dev`; the old branch is the reference |
| Already done by something merged since | Close it, as modernize says |

Say which one and why in a line before acting. Continuing on someone else's
branch means pushing to it, so on a teammate's branch, or one another machine
might have, prefer the new branch: rebasing or force-pushing it is never yours
to do.

## 4. Keep the credit

Whoever started the work keeps visible credit, because closing someone's PR
and shipping their idea under another name is how contributors stop
contributing.

- A teammate or contributor: every commit built on their work carries
  `Co-authored-by: Name <email>` with the identity from their commits, and the
  new PR body opens with "Takes over #<n> by @<author>" and what was kept.
- The old PR, once the new one exists: a comment linking it, then close it.
- Elias's own agents: no trailer (the commit rules forbid AI co-authors); the
  PR body names the thread or task it continues, with its link.

## 5. Finish it

From here it is an ordinary delivery: implement what is missing, verify on
each requirement's channel, fill the Proof section, and merge or hand it over
per development-workflow. With "full send" or "full stop" in the message, run
that mode to its end.

Report what was taken over, the decision of step 3, the PR or the closing
disposition, and what the original work got wrong, if anything did.

<!-- Adapted from Theo Browne's "takeover" skill, described in his live of 14 Oct 2026 ("I'm a maintainer and I have bullshit to deal with"); his file was not public. Changed for Elias: most of his abandoned work comes from his own agents (81 Booga worktrees, 37 unmerged ConoceRD app branches and more than 10 failed delegated tasks on 15 Oct 2026), so threads, worktrees and tasks are inputs too. Picked 3A on 15 Oct 2026. -->
