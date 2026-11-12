# Reading the merge criteria, entering review, after a merge

Read before a merge, before entering review, and after a merge into `dev`. The criteria and the needs-my-eye list stay in `SKILL.md`; this file says how each is read and what follows.

Record no acceptance step: the PR, its checks and its proof are the record.

## How each criterion is read

`agents pr merge` reads the route, the checks, `CLEAN`, the proof and a needs-my-eye first line in its own call (`--approved "<his words>"` carries his approval); the rest are yours, read in the same turn as the merge.

| Criterion | How it is read |
|---|---|
| The route is right | Task branch into `dev`, or `dev` into `main` for a release; `branch-model` green where the repo has it |
| Every required check is green on the current head | `gh pr checks <n>` and `gh pr view <n> --json headRefOid,mergeStateStatus` show the same SHA and `CLEAN`. A gate reads `pass`, never `skipping`: a run skipped while the PR was a draft can land after the real one and stand in for it, and `gh run rerun <run id>` of the real run puts it back on top |
| The repo's own checks ran and pass | The commands of `references/verification.md`, with their numbers in the PR body |
| Every requirement is Verified on its channel | `agents proof <n>` passes (where CI proves the rows, it reads the `proof-rows` and `proof-body` checks at the head). A `native`, `device-simulated` or `real-trip` row only the phone can produce says `Pending: batch` in a task PR into `dev` (`references/proof.md`) |
| The budget holds | The budget table of the head SHA shows no red row; a raised ceiling carries Elias's quote (`references/budget.md`) |
| The diff is only what was asked | You read the final diff end to end: no stray files, no debug code, no work from another delivery |
| Nothing is left open | No unanswered review comment, no question to Elias in the PR, no conflict with the base |

## Entering review and after the merge
- A visible change enters review with its preview URL or build first, the login it needs and the data it points at, found with the CLI, never asked of Elias.
- After a merge into `dev`: close its tickets idempotently (a failed write stays visible and retriable), leave the worktree on the parent branch and verify it (`main` for releases), report merge hash, PR and proof link.
- A problem Elias reports on merged work is a new PR on the same ticket; on an open PR it belongs to that PR: same branch, revalidate, merge again on the criteria.
