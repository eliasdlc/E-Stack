---
name: full-send
description: Elias's "full send" mode: the agent owns the task PR to its merge. User-invoked as /full-send; the mode-keyword hook loads this text when he types the words.
disable-model-invocation: true
---

# Full send

Elias named the mode by typing "full send". It means: own the PR until it is merged, without him watching. Call the Skill tool with "development-workflow" first: the merge criteria, the needs-my-eye list and the PR body rules live there, and `references/review.md` of that skill owns the cycle below.

## What you do

1. Run the cycle of `references/review.md` (The cycle both modes run): verify on the channels the requirements need, run the review loop, mark the draft ready, watch the PR, fix what the watch brings.
2. When every merge criterion of development-workflow holds, merge it yourself (`gh pr merge <n> --merge`), then carry the release where the standing authorization covers it.
3. After the merge, follow what it set off (the deploy, the release build, the `dev` preview) to its end. Where the product reports crashes (Crashlytics in ConoceRD), read them for the release window. Message him only if something broke, with the run or the crash and the revert PR ready. Then `unwatch_pull_request`.

## When the list outranks the mode

A PR on the needs-my-eye list of development-workflow is never merged by you, whatever the keyword, because the list is about what Elias must see. Say in the first line of the PR and of your message that this full send runs as a full stop, name the row and what in the PR matches it, and finish as `~/.claude/skills/full-stop/SKILL.md` teaches (read it: the Skill tool refuses a user-invoked skill).
