---
name: development-workflow
description: Owns the development lifecycle for product code and agent tooling. Use before implementing, testing, branching, committing, opening or reviewing a PR, merging, building or distributing; when Elias says "full send" or "full stop" (their own skills carry the mode, this one carries the merge criteria); and when a delivery has several requirements or a handoff is written or received. Load alongside the repository contract, and scrum for product scope. Not for read-only questions.
---

# Development workflow

Repository mechanics live in the repo contract. Read each step's reference when the step arrives, unless already read this session.

| When | Read |
|---|---|
| Code, a visible change, an estimate | `references/coding.md` |
| TypeScript or Dart code | `references/coding-typescript.md` or `references/coding-dart.md`, only the stack you touch |
| Branching, committing, a worktree, a long process | `references/git.md` |
| Testing, committing, or calling anything done | `references/verification.md` (delivery states) |
| Several requirements, a handoff | `references/ledger.md` |
| A PR body, its captures, a red `agents proof` | `references/proof.md` |
| A reviewer, review feedback, the cycle of a mode | `references/review.md` |
| A merge, entering review, after a merge | `references/merging.md` |
| A budget table or ceiling | `references/budget.md` |
| An incident that went wrong on a gating text, or a fixture of one | `references/incident-evals.md` |
| A release PR, a build, a distribution | `references/release.md` |
| Phase end, a handoff, a compaction or resume | `references/continuity.md` |
| A contract's Facts or Glossary, a deploy target | `references/facts.md` |
| A repo whose AGENTS.md lacks the template headings or whose CLAUDE.md is not `@AGENTS.md`: migrate it in its own small PR into `dev`, never inside the task; never sweep a repo you are not working in | `references/agents-md.md` |
| Changing a rule of this skill | `references/history.md` |

## Whose PR rules apply

Gates apply per repo owner: run `agents pr-policy` (or `--repo owner/name`). Gates: `proof`, `draft_pr`, `branch_model`, `review`, `budget`, `body_template`, `merge_criteria`. Where a gate is off, the repository's own process rules; with none on, write the PR in its format and publish nothing from it.

## Scope before mutation

State the objective, affected surfaces and closing gate in one sentence before the first change, because that sentence is where Elias catches a wrong scope. For a generic multi-step task, call the Skill tool with "model-delegation" to assess bounded child work; follow the active harness authority and keep small tasks direct. Expose material limits, costs and owner decisions when they affect the next action. Scope approval authorizes building, not acceptance or activation.

# Git

- **Maintained code projects use `main` → `dev` → task branch:** task branches start from current `dev`, task PRs merge into `dev`, a release is a `dev` → `main` PR. Never propose dropping `dev`, because large task groups collect there before one release PR.
- Push a task branch the moment it is created, before the first line of code: active file surfaces are exclusive across sessions and hosts, and the pushed branch and the ticket are the claim another machine reads before overlapping work.
- **A PR goes through one door, `agents pr`** (the `pr-door` hook runs `gh pr create` and `gh pr merge` through it). `agents pr open` opens the PR as a draft against its declared base; `agents pr ready <n>` after the review of `references/review.md` is clean, and only on a green proof, because ready runs the paid gates; `agents pr merge <n>` merges only when the criteria below hold, else prints the one reason and next step. Then fast-forward the local base and report merge hash and PR URL.
- Never delete a branch, merged or not. Never rebase or force-push a branch another machine might have.
- Every session works in its own worktree and stops only its own processes (`references/git.md`).

## No merge without proof

Where the policy has the `proof` gate, every PR proves each requirement it claims, on its channel, at the commit being merged. `agents proof <n>` judges it (in a repo whose CI runs the proof action, from the `proof-rows` and `proof-body` checks), and `agents pr merge` refuses a red proof. Read `references/proof.md` before writing the body or answering a red run.

# Merging (`merge_criteria` gate; where off, the repository's process decides, and full send and full stop end there)

**There is no default mode.** "Full send" and "full stop" are keywords: when one appears in my message, the `mode-keyword` hook prints that mode's text (or I type `/full-send` or `/full-stop`): `full-send` owns the PR to its merge, `full-stop` leaves it merge-ready and unmerged. With neither, verify what was asked and decide on the criteria: merge when they hold and no row of the list applies; otherwise leave the PR ready with its one-step test in the first lines and the row that applies.

**Merge criteria**, all of them, read in the same turn as the merge (how each is read: `references/merging.md`): The route is right. Every required check is green on the current head (a gate reads `pass`, never `skipping`). The repo's own checks ran and pass. Every requirement is Verified on its channel. The budget holds. The diff is only what was asked. Nothing is left open.

**Needs my eye.** Open the PR with its row in the first line and enter review; I merge it with the button or my approval words (last bullet).

| It changes | Because |
|---|---|
| A database schema, a migration, security rules, or real data (delete, rewrite, backfill) | It is hard to undo and it touches users |
| Auth, permissions or a trust boundary | A mistake here is a breach, not a bug |
| Money, billing, payments or credentials | It costs money or leaks access |
| A contract another released thing depends on (public API, app store config, package id, permissions) | A shipped client cannot follow it |
| A product or design decision I have not made (a screen not picked from a mock, removed features, copy I did not approve) | The decision is mine, not the code |
| How agents are governed, in `~/dev/agents`: the `# Authority` section of `rules/CLAUDE.md`; the installer and activation (`bin/agents` install, update and exec, `bin/configuration.py`); a hook that guards an irreversible action (`secrets`, `delivery`, `evidencia-road`: each `hooks/<name>.sh`, its `.py` where it has one, and `hooks/common.sh`, which they source). Every other hook, the registries, skills, references, tests and the README merge on the criteria | It changes what every future session is allowed to do, or guards what cannot be undone |
| A performance ceiling raised, or a guardrail passed (new permission, package, minSdk) | My chat quote in the PR is the review |
| Anything I said I want to see | I asked |

The list is the whole list: a PR not on it that meets the criteria gets merged, not parked out of caution. A release PR (`dev` into `main`) merges on the same criteria; only a production deploy, a tag or a store distribution needs my words (`references/release.md`).

- Entering review is one message: ready; the link first (PR, preview, build, file); the row and what in this PR matches it; what to check and why. "Your rule says" without the row and the match is not a reason.
- "Everything good", "green", "continue", or the equivalent in Spanish ("apruebo todo", "todo bien", "dale"), is my merge for a task PR that needed my eye: merge it in that turn on the criteria. A release PR is the same; its deploy follows `references/release.md`. If I approved something else, say in one sentence what I have not seen yet.
