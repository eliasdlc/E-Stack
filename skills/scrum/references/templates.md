# Templates

Verbatim shapes for the phase comment and the task description. Fill every
section; a section that does not apply says "none" so the
reader knows it was considered, not forgotten. The shapes are written here in
English; in Zoho they are written in Spanish, headings included (What it is:
Qué es; What exists today: Qué existe hoy; How it has to end up: Cómo tiene
que quedar; References: Referencias; How it is done: Cómo se hace; Acceptance
criteria: Criterios de aceptación; Surface: Superficie; Verification:
Verificación; Elias's hands: Manos de Elias; Source: Fuente). No emoji, no em
dashes.

Zoho phases and tasklists have no description field. What Linear kept in a
project description goes in the first comment of the phase
(`add_phase_comment`), and what a milestone description held goes in the first
comment of the tasklist (`add_tasklist_comment`). A task does have a
description, and it is the only place sources can live, because there is no
links field.

## Phase (the delivery stream)

First comment on the phase.

```
<One sentence: what is true when this phase ends.>

## What it is

<Two or three sentences: what exists today, what will exist when the phase ends, and why now.>

## Decisions made

* **<Decision>** (<date>). <One line with the reason.> <link to the section of the decisions document or to the published page or private source file>
* ...

## Not yet specified

* <What this phase needs and nobody has decided or defined yet; each item becomes a decision ticket or stays here on purpose. "None" if empty.>

## Out of scope

* <What someone could believe is included and is not, with the reason.>

## Repos and branches

| Repo | Base | Branch of the list | What it touches |
|---|---|---|---|
| `<folder or remote>` | `dev` | `<phase-n-topic>` | `<directories>` |

Rules of the repo: <link or path to the CLAUDE.md / AGENTS.md that rules>.

## Tasklists

1. **<Tasklist 1>**: <shared surface>, <n> tickets. Gate: <what gets reviewed>.
2. **<Tasklist 2>**: ...

Order derivable from the dependencies; if two lists can run in parallel it is said here.

## What stops the session

| Ticket | Why it stops | What it unblocks |
|---|---|---|
| <link> | Elias's hands: <what> | <tickets or list> |
| <link> | external wait: <what> | <tickets or list> |

None: <if there is nothing, say so>.

## How it is verified

* <Commands of the repo, test accounts, viewports, what capture is expected.>

## Sources

* [<title>](<published page url, or private source file path>)
* `<path of the decisions document>`
* [<audit>](<url>)
```

## Tasklist

First comment on the tasklist. Three lines, nothing more.

```
Branch: `<name>` from `dev`.
Surface: `<dir or file>`, `<dir or file>`.
Gate: <what gets reviewed and with which link it enters review>.
```

## Ticket

The task description, and the reason this skill exists. It is written for an
agent that never saw the conversation, never opened a link and does not know
Elias. If the brief has to be opened to know what is being built, the ticket is
not ready: **the ticket is the idea, the brief is where it came from**. A page
shown in the T3 thread is not a link anyone can open, so cite its published
link or the path of its private source file.

On 19 sep Elias said it whole: the descriptions "reference decisions, like
I said this, I said that, and that is not the idea; the idea is to explain in
depth what it is, what I want, how it is going to be done, and to reference with links,
photos or examples". His verbatim words do not disappear: they go down to "Source", which
is where the traceability lives. The thing itself goes on top.

```
Passes: 1

<Two or three sentences: what this is, who it is for, and what someone will be able to do when it exists that they cannot do today. It is understood without opening a single link.>

## What exists today

<The real state with real names: file, screen, collection, endpoint. What is missing or what is wrong, and why that matters. If nothing exists yet, it is said that way.>

## How it has to end up

<The thing described whole, at the detail whoever builds it needs.

If it is visible: the anatomy from top to bottom (which blocks, in which order, what each one carries), the tokens and sizes already decided, the states (empty, loading, error, ugly data, long text), what happens on touching each control, and what the layout does when the content grows.

If it is structural: the shape of the data with its fields and types, who produces it and who consumes it, the contract between the two ends, and what happens when it fails.

What is not decided yet is named here as an open question. It is not filled in with something made up.>

## References

| What to look at | Where | What is taken from it |
|---|---|---|
| <the approved mock> | <published page url or private source path> | <the anatomy and the spacing; not the color, that comes from the theme> |
| <the screen of another product> | <product and how that screen is reached, or url> | <only the drag gesture> |
| <a component that already exists> | `<path in the repo>` | <its API is copied, not its layout> |

None: <say so, and why it is not needed>.

## How it is done

1. <Buildable step with real names: endpoint, widget, collection, table.>
2. ...

Discarded: <the path someone is going to propose, and the line saying why not>.

## Acceptance criteria

- [ ] <Something a command or a capture checks.> [test | render | native | device-simulated | real-trip | nonvisual]
- [ ] ...

## Surface

* Repo: `<folder>`, base `dev`, branch of the list `<name>`
* Touches: `<dir or file>`, `<dir or file>`
* Shares with: <ticket that touches the same, or "none">

## Verification

* `<command>` to <what it has to say>
* Capture: <viewport and what has to be seen>, or "not visible"
* Channels this ticket demands and what produces them: <test | render | native | device-simulated | real-trip | nonvisual>, saying emulator or phone when it applies

## Elias's hands

<"none", or a console-guide guide: deep link, exact labels, value per input, what he brings back and where it goes.>

## Source

* [<title>](<url>)
* `<decisions document>`, section <n>
* What Elias asked for (<date>): "<his words, verbatim>"
```

### The references

A row without "what is taken from it" is decoration: whoever builds does not know whether
they have to copy the layout, the gesture or only the tone, and copies everything. Four
rules fix where each row comes from.

* **An image that matters does not live in a path of this machine.** What Elias
  pastes arrives at `~/.t3/userdata/attachments/` with a uuid name: it is temporary and
  agentbox does not open it. It is saved in
  `~/Documents/Proyectos/<Project>/dev/referencias/YYYY-MM-DD-<topic>.<ext>` and published
  inside a Postplan document (in base64, cap of 512 KB), which is the URL
  the ticket links. Zoho is no store: its MCP associates files that are already
  in the portal (`associate_attachments`), it uploads none.
* **An example from another product** is named with its screen and how it is reached.
  "Uber" is not a reference; "Uber's route sheet once the trip has already
  started, the one you drag up from the bottom" is.
* **A component that already exists in the repo** is cited with its path, and the row says
  whether its API or its look is copied, because they are almost never both.
* **What the agent found while searching** is marked as such, with its date, and
  never presented as something Elias asked for. The same for any filler data
  inside a mock.

### A visible ticket with no decided form is not a build ticket

If "How it has to end up" cannot describe the thing because nobody has decided
yet how it looks, the ticket is not created that way. Either it is a decision ticket with its
mocks inside, or its first pass is making the mocks and that is what its
description says. "Build component X" with the form blank is exactly
the ticket that comes back with questions mid-phase.

### The migrated tickets

A migrated task carries the block the migration wrote (Linear source,
original identifier, state history) above everything. Leave it where
it is and put `Passes: N` above it when repairing the ticket; that block is
history, not a section of this template. What does get repaired is the body: a
migrated description that only points to a decision is rewritten whole with the
sections above, from the repo and from the document that decided it.

## Decision ticket

For an open product decision. Same template, with "How it has to end up" and
"How it is done" replaced by the options, and "References" carrying what each
option imitates:

```
## Options

**A. <Title>** (recommended). <What it does differently.> Cost: <one line>.
**B. <Title>**. <What it does differently.> Cost: <one line>.
**C. <Title>**. ...

Answer with the letter and a note if you want to change something of the option. With the answer this ticket closes and the tickets it blocks unblock on their own.
```

Never two options. If only one path is real, the ticket is not a decision: it
is a fact in the phase comment.

## Comments

Every status change an agent makes that is not obvious from the status itself
gets a comment on the task (`add_task_comment`), one line each:

- Parked: `Parked: <reason>. I bring it at the gate of list <n>.`
- Cancelled: `Cancelled: <reason>. <What replaces it, if anything>.`
- Merged as duplicate: `Duplicate of <prefix>. <What was kept from this one>.`
- Invalid during execution: `Invalid: <reason with the path or the commit>. Recommendation: <cancel / rewrite as X>.`
- Build distributed that touches the ticket:
  `Build: <versionName> (<versionCode>) <exact release link> from <SHA>. This ticket: <Implemented | Verified [channel] | pending to see: what>.`
  One comment per build, never edited afterwards; the receipt format belongs
  to the `development-workflow` skill (its ledger reference).
- Closed: the PR link, the validation line (`typecheck 0, lint 0, 42 tests`)
  and the ledger of its acceptance criteria, each with its state and channel.
  A criterion at `native`, `device-simulated` or `real-trip` closes only with
  a capture or measurement that carries the receipt of the build it came from.

Zoho has no project status update object. The phase comment is where the state
of the stream lives: one comment at the start of each execution phase (the
phase map) and one at its end (what merged, what is parked, next list). Say
the health in the first line of that comment, in his words: `On track`,
`At risk: <what>` when a hands ticket sits unanswered on the critical path,
`Off track: <what>` when a gate has been open more than a week.
