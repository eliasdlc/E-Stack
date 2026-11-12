---
name: full-stop
description: Elias's "full stop" mode: the agent leaves the PR merge-ready and unmerged. User-invoked as /full-stop; the mode-keyword hook loads this text when he types the words.
disable-model-invocation: true
---

# Full stop

Elias named the mode by typing "full stop". It means: leave everything ready so he only presses the merge button, without thinking, and give him a way to try what you just did. You never merge, even a task PR that meets every criterion, because this mode exists so the last decision stays in his hand.

Call the Skill tool with "development-workflow" first: the merge criteria and the PR body rules live there, and `references/review.md` of that skill owns the cycle below.

## What you do

1. Run the cycle of `references/review.md` (The cycle both modes run): verify, run the review loop, mark the draft ready, watch the PR, fix what the watch brings.
2. Stop at merge-ready, and read all of this in the same turn as your message:

   | Condition | How it is read |
   |---|---|
   | Ready for review | The PR is not a draft (`gh pr view <n> --json isDraft`) |
   | Every check green on the head | `gh pr checks <n>` and `gh pr view <n> --json headRefOid,mergeStateStatus` show the same SHA and `CLEAN`; a gate reads `pass`, never `skipping` |
   | Proof done | `agents proof <n>` passes, or in a repo with the proof action its checks pass at the head |
   | Nothing open | No unanswered comment, no conflict with the base |

3. Put the one-step test in the first lines of the PR body and of your message, before anything else: one of the preview URL of the branch (with the login it needs and the data it points at), the review APK link or its install command, or one command to run. Then one or two lines on what to look at and why. Find it with the CLI; he never asks for it.
4. Send one message: the PR link, the test, what to look at. If a needs-my-eye row applies (or a full send fell back to this mode), add which row and what in the PR matches it. A release PR is left the same way, and its production deploy, tag or distribution waits for his words as `references/release.md` says.

Call `unwatch_pull_request` when the PR is merge-ready and you hand it back.
