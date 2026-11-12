# Git and worktrees

Read before branching, committing, starting a long process. `SKILL.md` keeps the branch model, the push-at-creation claim, the one door for a PR and the no-rebase rule; this file holds the rest. Branch model and drafts follow the `branch_model` and `draft_pr` gates; the rest holds everywhere.

## Branches
- **Demos and non-code projects are exempt** from `main` → `dev` → task branch. The project's contract says it is a demo (PetHospital and Repuestos Santiago are, by Elias's classification), never inferred from a web preview.
- In maintained projects, no implementation commits on `main` or `dev` unless Elias says so. Verify branch, worktree and ancestry before editing.
- **Every finished, green task PR merges into `dev`; what must not show yet goes behind a feature flag.** A rework is small PRs into `dev`; branch off another task branch only when Elias names it as base, because work parked outside `dev` never reached anyone.
- **A branch outside its base for more than three days is a defect, not a state.** It gets merged, or its PR gets closed with the disposition of its commits written down.
- Production deploys from `main`, always; `dev` produces previews. Never set a hosting project's production branch to `dev`.
- Never suggest branch cleanup. `git worktree prune` is allowed; `git branch -d` never.
- Lifting a wait ("no pausing", "complete every phase") lifts the wait, not "one branch per phase" or any other rule of the plan. Any deviation from the plan is named in one line before it happens, with what it costs.
- Conflicts: integrate both intents. If they cannot coexist, stop and explain the decision required.
- SSH push fails (`Permission denied (publickey)`, `ssh-askpass`): `gh auth setup-git`, push over HTTPS, mention the fallback.

## Commits
- Conventional Commits unless the repo defines another; atomic; titles in repo style. No AI attribution trailers, co-author lines, "Generated with" lines, session links or em dashes (`clean-commit` hook).
- Files dirty from another delivery never enter a commit; in a worktree of your own there are none.
- Commit after validation passes and report hash and message, plus anything left uncommitted.
- A run is cancelled only when it is your own duplicate for a replaced SHA, or when Elias asks for it.

## Worktrees and processes
**Every session works in its own worktree and stops only its own processes**, because two sessions in one checkout commit and undo each other's files, and a stop by name reaches another session's job. A T3 thread gets its worktree from `workspaceStrategy` `worktree` (`agents t3-launch` sets it for a git project; `--shared-root` only for read-only work); let T3 create it under `~/.t3/worktrees/<project>/`. One you create yourself lives in `~/dev/wt/<repo>/<branch>`, never beside the repo or in `/tmp`, which the system empties. A long process (dev server, emulator, watcher) starts with `agents run [--name N] -- <command>` and stops with `agents run --stop N` (or `--all`), which reaches only that worktree's groups.
