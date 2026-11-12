# Contract: ready to start

Definition of Ready for a delivery stream (a Zoho phase) and for a ticket (a
Zoho task). Both directions of the skill validate against this file. A ticket
that fails a line is not created until it passes, and a ticket found failing
during execution is repaired from the sources before work starts, never worked
around.

## The property map

What each Zoho task field means in Elias's portal. Nothing is decorative:
every field answers a question the executing agent would otherwise ask.

| Field | Answers | Rule |
|---|---|---|
| `name` | What becomes true | A sentence with the outcome or the problem. No verbs like "implement", no prefixes, no codes |
| `description` | The whole idea | The ticket template in `templates.md`, every section present or explicitly "none". It is not a pointer to where the idea was decided: it is the idea, at the detail whoever builds it needs, understandable without opening a link. The sources and Elias's words live at the end, under "Source", because a task has no links field |
| `milestone` | Which delivery stream | Always set. This is the Zoho phase. No orphan tickets |
| `tasklist` | Which execution phase, which branch | Always set. The tasklist is the phase; its first comment names the branch and the shared surface |
| `priority` | What goes first when two are unblocked | Only four values exist: `high` on the critical path of the stream or blocking a person, `medium` in scope and not on the path, `low` nice to have inside the stream, `none` only in a backlog phase. Linear's Urgent has no equivalent: an urgent ticket is `high` and first in the tasklist order |
| `Passes: N` | How many passes | First line of the description, above the paragraph. 1 = one PR with tests. 2 = the split is written inside. Never more than 2 on a leaf ticket. Zoho's `work` and `duration` are hours and stay untouched |
| `tags` | Type, surface, whose hands | Exactly one type, exactly one surface, plus `owner` or `external-blocker` when it applies. See taxonomy |
| dependency | What has to exist first | `add_task_dependency`, `dependency_type` `FS`, predecessor first. Only the three real kinds: a prior migration or schema, a value or data not yet produced, a decision of Elias. Ordering preference is not a dependency; it is `reorder_tasks` |
| `parental_info` | A pass inside a larger unit | Only when a ticket was split. The parent holds the why; the subtasks hold the work |
| `owners_and_work.owners` | Whose hands | Elias when the ticket needs his hands, accounts or a decision. Empty means an agent does it. Never assign agent work to Elias |
| `end_date` | An external deadline | Only when the world imposes it: store review windows, a meeting, a legal date. Never as a wish |
| `status` | Where it is | `Open` planned or next, `In Progress` an agent is on it, `Closed` merged into `dev` with its task PR's rows verified or `Pending: batch` (his phone check lives in the release checklist, not in the ticket), `Cancelled` with a comment saying why. Between the two there is no status: the ledger row of the ticket (Requested, Implemented, Verified, Distributed, Accepted, per the global rules) lives in its comments, one per build. Read the product's layout before using any other value. A duplicate is `Cancelled` with a comment `Duplicate of <prefix>`, because Zoho has no duplicate relation |
| sources | Where the claims come from | Inside the description, under "Source": the published page or private source file of the visual brief, the decisions file section, the audit, the PR once it exists |

A task link is `https://projects.zoho.com/portal/<portal>#zp/task-detail/<task_id>`: the task id alone, no portal id and no project id in the path. Build it from the id the API returns. Links to a phase, a tasklist or a project are copied from the browser, not composed.

Phase (delivery stream) fields:

| Field | Rule |
|---|---|
| `name` | Short, Elias's style; `Phase N: Title` when the plan is phased |
| `start_date` / `end_date` | From the plan. A stream with no dates stays `Active` with its tickets at `priority` `none` |
| `status_id` | `Active` planned, `In Progress` when the first execution phase starts, `Completed` when its last PR is merged and verified, `Cancelled` with a comment |
| `owner_zpuid` | Elias (`2716136000000103002`) |
| first comment | The phase template in `templates.md`: what it is, decisions made, not yet specified, out of scope, repos and branches, phases, what stops the session, how it is verified, sources. A phase has no description field, so this comment is the description |
| tasklists | One per execution phase; its first comment names branch, surface, gate |

## Tag taxonomy

Tags are flat in Zoho: there are no label groups, so the grouping is a
convention this file enforces. `get_project_tags` shows the current set per
product, and the two products differ. Never create a parallel tag for a
meaning that exists.

| Group | Tags | Meaning |
|---|---|---|
| Type (exactly one) | `Feature`, `Improvement`, `Bug`, `Chore` | What kind of change. `Chore` is repo hygiene, CI, dependencies, docs |
| Surface (exactly one) | ConoceRD: `app`, `infra`, `web`, `dashboard`, `map`, `navigation`, `content`, `legal`. Kino: `app`, `convex`, `docs`, and what the product adds | Which repo or module the branch lives in. Create a new one only for a new repo, named after its folder in the workspace `CLAUDE.md` |
| Flag (zero or more) | `owner`: needs Elias's hands (external account, product decision). A device check is a release checklist row and does not keep a ticket open. `external-blocker`: a third party controls the clock (store review, lawyer, testers, data that has to accumulate). `post-v1`: out of the launch scope. `tos-risk`: legal exposure with a provider | Whose hands, or a warning |
| Migration | `migrated-from-linear` | Set by the migration. Read-only history: never add it to a new ticket, never remove it from an old one |

`owner` tickets are owned by Elias and written as a guide he can run.
`external-blocker` tickets say what unblocks them and how to check whether it
arrived. Neither sits on the critical path of an execution phase without being
listed in the phase comment under "What stops the session".

The tag `awaiting-decision` exists in Kino from the migration and is redundant
with `owner` on a decision ticket. Do not use it on anything new.

## Checklist per ticket

Every line has to be true before the ticket exists or before work on it starts.
The test that covers most of them at once: cover the chat, cover the links, and
ask whether what is left builds the right thing. If not, it is not
ready.

1. The title states an outcome or a problem, not an action.
2. `Passes: 1` or `Passes: 2` is the first line of the description.
3. The first sentences say what the thing is, who it is for, and what someone
   will be able to do with it. No section has a decision as its subject ("Elias
   said", "it was decided on 12 sep"): that is traceability and it lives in "Source".
4. "What exists today" names the real state with real names (file, screen,
   collection, endpoint), or says that nothing exists yet.
5. "How it has to end up" describes the whole thing. Visible: anatomy, tokens
   decided, states (empty, loading, error, ugly data, long text),
   behavior on touch, and what the layout does when the content grows.
   Structural: shape of the data, producer, consumer, contract and what happens
   when it fails. What is not decided appears as an open question, never filler.
6. A visible ticket whose form nobody has decided is not a build ticket: it is
   a decision ticket with its mocks, or its first pass is the mocks.
7. "References" has at least one row for everything visible and for everything that
   imitates something that already exists, and each row says what is taken from it. An image
   lives in the visual brief source and in `~/Documents/Proyectos/<Project>/dev/referencias/`,
   never in a temporary path of a machine. "None" only when there really is
   none, with the reason.
8. "How it is done" is a numbered list an agent can build from, with the real
   names of files, collections, endpoints, screens, and it names the discarded
   path so nobody reopens it.
9. "Acceptance criteria" is checkable by a command or a capture, never "that it
   works well", and every line ends with its evidence channel: `test`
   (unit or widget test), `render` (golden of a widget, including any mock
   that replaces the map engine), `native` (the real map on emulator or
   device), `device-simulated` (the phone with simulated GPS), `real-trip` (a real
   trip), `nonvisual` (tooling, rules). A ticket that touches native map layers (ModelLayer and its shadows,
   `line-width`, `line-trim-offset`, sprites, traffic segments, refresh rate,
   map density, night mode, arrival at low speed) needs at least one line at
   `native`, `device-simulated` or `real-trip`; `test` and `render` alone do
   not close it. `nonvisual` is for tooling and rules with no screen. The
   channels are not a ladder: each proves a class of properties, and the
   criterion names the one that can show its property.
10. "Surface" names the repo, the base branch, the directories or files
    touched, and any file another ticket also touches.
11. "Verification" lists the commands the repo defines (from its `CLAUDE.md`,
    `package.json`, Makefile) and what a capture has to show if the change is
    visible.
12. "Elias's hands" is either "none" or a `console-guide` guide.
13. "Source" links every document the claims come from, and carries Elias's
    words verbatim with their date when the ticket was born from a message of his.
14. `milestone`, `tasklist`, `priority`, type tag and surface tag are set.
15. Every dependency is one of the three real kinds and the predecessor exists
    in the same product.
16. Nothing in the ticket is already merged in the repo (checked against
    `git log` and open PRs).

## Checklist per phase

1. The first comment follows the template: what it is, decisions made, out of
   scope, repos and branches, phases, what stops the session, how it is verified,
   sources, opening with the one sentence that says what is true when the
   stream completes.
2. Every execution phase is a tasklist whose first comment names its branch.
3. Every ticket belongs to a tasklist and to the phase.
4. The critical path is derivable from the dependencies alone: an agent
   reading them and the tasklist order gets the order the plan intended.
5. Every hands or wait ticket is listed under "What stops the session" with
   what it unblocks.
6. No two tickets share a surface inside the same tasklist without saying
   which goes first.
7. Every source document is linked.
8. Owner, dates and status set.
