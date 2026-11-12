---
name: ketchup
description: Catches Elias up on where the current work stands, in five bullets or fewer.
disable-model-invocation: true
---

# Ketchup

Elias opens this with `/ketchup` when he comes back to a thread and has lost the
thread of it. Answer "where did we leave off" from evidence, not from memory.

1. Read the state now: this conversation, `git branch --show-current`,
   `git log --oneline -5`, `git status --short`, and, when a PR exists,
   `gh pr view --json number,state,isDraft,url` with `gh pr checks`. Also read
   the pause note a stopped session left, if it exists, because it holds the
   next command; its path is
   `~/.cache/agents/pause/$(basename -s .git "$(git remote get-url origin)")-$(git branch --show-current | tr / -).md`.
   Where the note and the repo disagree, the repo wins, because the note is
   only as current as the moment it was written. A fact from earlier in
   the chat is not current until re-run.
2. Answer in five bullets or fewer, in the language he wrote in, because he
   reads this to re-enter the work in seconds. Order: where the work is
   (branch, PR, checks); what was done; what is running or blocked; the last
   thing he decided; what is pending. Several pending decisions share the
   fifth bullet, one short question each, so the cap holds.
3. Phrase each pending decision as a question a bare "yes" answers, with your
   recommendation inside it, so one word from him moves the work: "Merge #12
   into dev (checks green)? Yes accepts."
   A decision with no recommendation you can defend is stated as two options,
   because a "yes" to a question with no recommendation accepts nothing.
4. Add no plan, no history and no offer to continue, because each one pushes
   the state past five bullets. A fact you could not read says so in its
   bullet, so a gap never reads as a fact.
