---
name: scrum
description: Moves work into and out of Zoho Projects as scrum master with full authority to create, edit, merge, cancel and reorder. Into Zoho: plans, decision rounds, audits and ticket documents become a phase of ready tasks ("put this in Zoho", "create the tickets", "make the roadmap"). Out of Zoho: a project or task URL, "start", "execute", "keep going with". Also grooming ("clean the backlog"), and Spanish equivalents. Not for agent environment changes.
---

# Scrum master for Zoho Projects

The goal is one sentence: **a project link is a complete instruction.** An agent
that receives it starts working with nothing else, and the only things that stop
it are Elias's hands and product decisions, which are marked in advance so they
never surprise anyone mid-phase.

Authority: full. Create, edit, retag, merge, cancel, reorder, move between
phases. Every destructive action (cancel, merge into a duplicate, drop a
dependency) leaves a comment saying why, and the closing message lists all of
them. Elias reads the changelog, not a permission prompt.

Linear is closed: read, write and link only Zoho. What the migration kept from
Linear lives inside each task description.

## Two directions, one contract

Both directions are governed by `references/contract.md`, the definition of
"ready to start" for a delivery stream and for a ticket. Read it first,
every time.

| Direction | Trigger | What happens | Reference |
|---|---|---|---|
| Plan to Zoho | A plan, decisions round, audit, tickets document or chat agreement becomes work | Inventory the portal, build the phase, tasklists per delivery phase, tasks with every property, dependencies, tags, dates; then validate against the contract and report | `references/templates.md` |
| Zoho to work | A link arrives, or "start", "execute", "keep going" | Read everything, repair what is not ready from the sources, post the phase map, execute phase by phase, keep Zoho live, park hands tickets, close at the gate | `references/execution.md` |

Grooming ("clean up", "review the backlog") is the first direction applied to
what already exists: same contract, same changelog.

## Before touching Zoho

1. **Inventory the portal.** `get_portals`, `get_projects_list`,
   `get_all_users_in_a_portal`, `get_project_tags` for the product,
   `get_project_phases` (it rejects the call without `page`),
   `get_all_project_task_lists`. Read every tag, status and phase before using
   it; the two products have different tag sets.
2. **Statuses are read, not guessed.** The four in use on tasks are `Open`,
   `In Progress`, `Closed`, `Cancelled`; phases carry `Active`, `In Progress`,
   `Completed`, `Cancelled`. Each product has its own task layout
   (`get_layout_list` with `module` `tasks`), so read the layout before
   writing a status that is not one of the four.
3. **Read the sources, not the summary.** The visual brief source HTML (or
   published Postplan) in
   `~/Documents/Proyectos/<Project>/dev/plans/` (older projects keep theirs in
   `dev/planes/`), the decisions file (`<Project>-DECISIONS.md`), the tickets
   document if one exists, the repo's `CLAUDE.md` or `AGENTS.md` for branch
   rules, commands and test accounts. Every claim in a ticket carries where it
   came from.
4. **Check the repo state.** `git fetch`, `git ls-remote --heads origin`, open
   PRs. A ticket that describes work already merged is closed, not created.

## The portal, and the noun collision

Zoho's nouns and Elias's collide. This table is the whole translation; use it
instead of re-deriving it.

| Elias says | Zoho object | MCP identifier |
|---|---|---|
| the portal | portal | `<portal id>` (`<portal>`) |
| the product | project | Kino `2716136000000108080`, ConoceRD `2716136000000108003` |
| a project, a delivery stream | phase (the API also calls it milestone) | `milestone` on a task, `*_phase*` tools |
| a phase: tickets sharing a file surface, one branch, one gate | tasklist | `tasklist` on a task |
| a ticket | task | `prefix` `KI1-T16`, `CO1-T4` |
| a label | tag | flat, no groups |
| a sub-ticket | subtask | `parental_info` on the task |

A phase and a milestone are the same object in the API; `create_task_list`
attaches one through its `milestone` field, and there is no separate phase
parameter. When Elias says "phase", he means the tasklist.

Both products live in one portal, so there is no second connection to ask
for: `zoho_projects` reaches Kino and ConoceRD equally.

## The description is the whole idea

Explain the thing itself in the description. A description that only
references decisions ("I said this, I said that") tells the reader where the
idea came from and not what to build, so they invent or they ask.

The description is written for someone who did not see the conversation, does not open
the links and does not know Elias. Four things in order: what it is, what exists today, how
it has to end up and how it is done. If it is visible, "how it has to end up" describes
the whole component (anatomy, states, ugly data, what happens on touch) and
"References" carries the mock, the screen of another product or the component that
already exists in the repo, each row with what is taken from it. Elias's verbatim words
and the documents go down to "Source": they are the traceability, not the body.

A visible ticket whose form nobody has decided is created as a decision
ticket, carrying its mocks or making the mocks its first pass. The exact shape
is in `references/templates.md`.

## Building a roadmap (Plan to Zoho)

- **One phase per delivery stream**, named as Elias names them: a short title,
  optionally `Phase N: Title` when the plan is phased. `create_phase` takes
  `name`, `start_date`, `end_date`, `owner_zpuid`, `status_id`. Everything a
  Linear project description used to hold (summary, decisions, sources) has no
  field here: a phase has no description. It goes as the first phase comment
  (`add_phase_comment`) and is linked from every ticket of the phase. Every
  phase comment carries "Not yet specified" and "Out of scope" sections, so
  nobody builds on a gap or inflates the phase.
- **A prefactor task comes first** when the phase needs one: a ticket that
  reshapes existing code so the rest lands cleanly, first in the tasklist
  order (`reorder_tasks`), because ordering is not one of the three real
  dependency kinds below.
- **One tasklist per execution phase**, in order, attached to the phase through
  `create_task_list`'s `milestone` field. A phase is a group of tickets sharing
  a file surface: one branch, one PR, one review gate. Derive phases from the
  surfaces, not from the calendar. A tasklist has no description either, so
  its branch, shared surface and gate go in its first comment
  (`add_tasklist_comment`); the name stays short: `P2: The identity, one`.
- **One ticket per pass.** A pass is one PR with its tests. Anything clearly
  over two passes is split into subtasks (`parental_info`) that each fit one;
  two tickets that are half a pass each are merged. State the cut inside the
  parent.
- **Every acceptance criterion names its channel**, from the six that
  `app-testing` lists and nowhere else; the contract says which tickets cannot
  stop at `test` or `render`. The ledger that tracks each criterion through
  Requested, Implemented, Verified, Distributed and Accepted belongs to the
  `development-workflow` skill (its ledger reference); this skill only
  requires it.
- **Every ticket carries the full property set** from the contract: title that
  states the outcome, description from the template with the idea whole and the
  sources last, `milestone` (phase),
  `tasklist`, `priority`, `Passes: N` as the first description line, tags
  (type, surface, and the hands or wait marker when it applies),
  `add_task_dependency` for real dependencies, `owners_and_work` only when the
  hands are Elias's, `end_date` only for an external deadline, source links
  inside the description.
- **Dependencies are of three kinds and only three:** a migration or schema
  step that has to exist first, a value or data that has not been produced
  yet, a decision Elias has to make. Anything else is ordering, not blocking,
  and goes into the tasklist order (`reorder_tasks`) instead of a dependency.
  `add_task_dependency` takes `predecessor_task`, `successor_task` and
  `dependency_type` `FS`; it returns no id, so a dependency is identified by
  its task pair when updating or deleting it.
- **Hands tickets are written as `console-guide` guides**, deep link, exact
  labels, value per input, what he brings back and where it goes. They are
  owned by Elias and tagged `owner`. If the wait is external (a store review,
  an API approval, data that has to accumulate) the tag is `external-blocker`
  and the ticket says what unblocks it and how to check.
- **Decisions already made are stated as facts in that phase comment**, with
  the date and the link. Open decisions become one ticket each, tagged
  `owner`, with the options written as a visual brief decision would write them:
  recommendation first, cost per option, and real alternatives rather than a
  bare binary.
- **Create in dependency order** so `add_task_dependency` can reference real
  ids. Batch creations, then a second pass for dependencies and tags, then
  validation.
- **Passes, not estimates.** Zoho's `work` and `duration` are hours, which is
  the unit Elias does not use. `Passes: 1` or `Passes: 2` is the first line
  of every description; leave `work` alone.

## Validation before reporting

Run the contract checklist against every ticket you created or touched, by
reading them back (`get_tasks_by_project` with `page` and `per_page`, then
`get_task_details` for anything with a dependency or a subtask). Fix what
fails. Then report:

- the phase link in the first line
- a table: tasklist, tickets, surface, what blocks it
- the hands list: every `owner` and `external-blocker` ticket with its link and
  what it unblocks
- the changelog: created, edited, merged, canceled, with the reason for each
  destructive one
- what was inferred and what is still open

Report tickets by title and link; the bodies stay in Zoho.

## Language and style

Everything written in Zoho is Spanish, because Elias reads it there: phase and
tasklist names, ticket titles, comments and new tickets, with technical terms
in English. An old body in English is translated when someone works the
ticket, not in bulk. GitHub stays English (PRs, commits, release notes).
<!-- Decided 2026-09-23, answer 1A of the Zoho grooming round
(plan.decruce.dev/d/65r7y679ke2k): the portal mixed two languages. -->

Write plain text: commas, colons and parentheses where an em dash would go,
and no emoji. Ticket codes live in the task prefix, and prose
names tickets by title. Titles are sentences that state the outcome or the
problem, in the style of the existing ones: "The mode belongs to the leg, not
to the trip: the app works out on its own where you drive and where you walk",
rather than "Implement X" or a prefix like `[app]`.

## Unplanned requests

Record unplanned requests immediately and triage them by impact. A weekly plan
does not veto new requests. Record independent product work before coding,
preserving the owner's exact words under Source. A defect in the delivery
currently under review extends that task and branch instead.

- Urgent independent failures take the next safe slot. Nonurgent work queues.
- Overlapping file surfaces serialize across sessions and machines. Record
  the dependency before either begins.
- A scope change names the interrupted work and branch, then waits for the
  owner's switching decision. Preserve valid local changes.
- Machine, skill, hook and rule changes belong in agents Git history, not Zoho.
- Read-only questions and audits do not create implementation tickets.

GitHub owns delivery events tied to the reviewed SHA. Zoho owns scope and
receives linked status and evidence. A failed projection is pending work, not
a reason to mark a task Closed. Before a new execution phase, reconcile
accepted-but-unmerged work and incomplete writes in the previous phase.

The incidents behind these rules are in `references/history.md`; read it only
when changing a rule.
