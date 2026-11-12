# Execution from a link

The protocol when a Zoho link arrives (a project, a phase, a tasklist or a
task), alone or with "start", "execute", "keep going with", "what is missing". The
promise: no question to Elias before the first line of code, except the ones
the phase already marked as his.

Any link resolves to a delivery stream. A task link is read as its phase: the
whole phase is read the same way, and execution starts at that task only if
its predecessors are closed. `get_project_id_from_entity_id` turns a bare id
into its product when the link does not say which.

## 1. Read everything, then decide

- `get_project_detail` for the product, `get_project_phases` with `page` (the
  call fails without it) to place the stream, `get_all_project_task_lists` for
  its execution phases.
- `get_tasks_by_project` with `page` and `per_page` up to 200, paging until
  `has_next_page` is false, then `get_task_details` for every task whose
  status is not `Closed` or `Cancelled`, to pull dependencies, subtasks and
  the full description.
- `get_task_comments` on anything parked: the reason is there, not in the
  status.
- The phase's first comment (`get_phase_comments`) and the documents it links:
  Postplan, decisions file, and the repo's `CLAUDE.md` or `AGENTS.md`.
- The repo: `git fetch`, `git ls-remote --heads origin`, `gh pr list`. A
  branch named after a tasklist or a task already on the remote means another
  session or agentbox claimed it: read its state before touching it.

## 2. Repair before starting

Run the ticket checklist from `contract.md` over every open ticket. What fails
is repaired from the sources, not asked about:

| Missing | Repair from |
|---|---|
| The idea: the description points at a decision instead of explaining the thing | The Postplan, the audit or the decisions document that originated it. The whole body is rewritten with the sections of `templates.md` and the verbatim goes down to "Source" |
| "How it has to end up" blank on something visible | The approved mock. If nobody decided the form, the ticket is not a build ticket: it becomes a decision ticket with its mocks, or its first pass is the mocks, with a comment saying which of the two |
| "References" empty, or rows without "what is taken from it" | The document that brought them. An image that only exists in a temporary path of a machine is republished inside a Postplan and saved in `referencias/`; the row nobody can open is removed |
| Surface, files, branch | The repo: grep the names the ticket mentions, read the workspace `CLAUDE.md` for the base branch |
| Acceptance criteria | The plan or audit the ticket links; the existing tests in the repo for the shape |
| Verification commands | `package.json`, Makefile, `CLAUDE.md` of the repo |
| Tasklist | The surface: put it with the tickets that touch the same files (`move_task` keeps it in the product) |
| Type or surface tag | The repo it touches and the kind of change (`associate_tags_to_entity`) |
| `Passes: N` | The size of the pass: one PR with tests is 1 |
| A dependency that is not one of the three real kinds | `delete_task_dependency` on the task pair, comment why, keep the order through `reorder_tasks` |
| A ticket already merged | `git log --grep`, open PRs: set `Closed` with the PR link and a comment |
| Two tickets that are the same | Keep the older one, set the other `Cancelled` with the comment `Duplicate of <prefix>. <what was kept>`, move anything unique into the survivor first |

A migrated ticket whose description still describes a Linear reality (a state
that no longer exists, an attachment that was a Linear upload) is repaired
against the repo, not against Linear. The `migrated-from-linear` block at the top
of the description is history: it is never edited, never trusted over the repo.

Only a missing product decision stops here, and it stops as a hands ticket:
create it from the decision template, make what depends on it a successor,
keep going with everything it does not block.

## 3. The phase map, once

One message and one comment on the phase, same content:

- tasklist order with branch per tasklist and what each waits on
- the tickets of the first phase in execution order with their links
- the hands list: every `owner` and `external-blocker` ticket, what it
  unblocks, and in which gate it comes up
- what was repaired in step 2, as a changelog

Then start. The map is a checkpoint, not a stopping point.

## 4. During a phase

- One branch from `dev`, named after the tasklist, pushed before the first
  line of code. Task prefixes stay in branch names and commit trailers only.
- "No pauses" or "complete all the phases" lifts the wait at the gate, not
  the branch per tasklist. Folding tasklists into one PR, or any other
  deviation from the map, is named in one line before it happens, with its
  cost (one review for four surfaces), in the chat and as a phase comment.
- A task link inside the message that starts the work is read, set
  `In Progress` and commented before the first edit; the 13 sep session that
  rewrote the tracker rules never touched the task it was given.
- Each ticket: `In Progress` the moment work starts, `Closed` when its part is
  merged into `dev` with its rows verified or `Pending: batch` (his phone check
  lives in the release checklist), with the validation line and the ledger of
  its criteria as a task comment. Every distributed
  build that touches the ticket leaves the `Build:` comment from
  `templates.md`, so anyone can tell which version carried what. A ticket
  that turns invalid mid-phase: comment, park, bring it to the gate with a
  recommendation. It is not cancelled during execution; cancelling is Elias's
  call at the gate.
- Hands tickets stay parked. Everything they do not block gets finished. They
  come as one batched list at the gate, each with its guide ready to run.
- Two tickets sharing a file inside the phase run in the order the map says,
  never in parallel agents.
- A decision made while working that was not in the plan goes as a comment on
  the task and as a line in
  `~/Documents/Proyectos/<Project>/dev/<Project>-DECISIONS.md`.

## 5. The gate

Each PR is merged on the merge criteria of `development-workflow`, or enters
review when it needs Elias's eye: link first (the preview, the build, or the PR
for code-only work), which item of the list it is, what to check, the batched
hands list. A comment on the phase mirrors it.

After the merge (his or yours): set the tickets `Closed`, the tasklist
completed (`update_task_list`), the phase `In Progress` if it was `Active` and
`Completed` after the last execution phase, fast-forward `dev`, and post the
next phase map in the same message.

## 6. When the session has to stop

Finish everything that does not depend on Elias. Then: percentage done, what
is unfinished as a numbered list, what was tried, and the one question that
unblocks. Zoho already holds the state, so the handoff is short: the phase
link, the branch, and `git status` output.
