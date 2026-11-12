---
name: council
description: Convenes three models from different providers to answer, cross-examine each other and hand you one synthesis of what you asked for.
disable-model-invocation: true
---

# Council

Elias opens `/council <what he wants>`: a decision, a review, a design
critique, a plan, a diagnosis. The council does that thing, and only that
thing. Three members answer on their own, then each reads the others and
objects, then this thread writes one synthesis in the shape he asked for, with
the dissent left visible.

The council is advice he chose to pay for. It is not a gate: nothing else
calls it, and it never stands in for `delivery-reviewer`, the proof gate or
the review loop of development-workflow.

<!-- Adapted from Theo Browne's `council` skill in t3dotgg/tstack (MIT, published 24 Oct 2026, file read at commit 7de017b): three providers, flagship models at high effort, resolved with orchestrator_capabilities and run with delegate_task, no substitution of a missing member, read-only members for review or feedback, a score out of 10 for code review in a "Council review" table in the PR body, and the orchestrator fighting scope creep. Added from Karpathy's karpathy/llm-council (Nov 2025): the second stage where each member reads the others anonymized. Changed on purpose: Theo loops until every delegate is satisfied; here the rounds are capped so a council costs minutes, and disagreement that survives the cap is reported instead of argued away. Elias, 26 Oct 2026 (decision 11X): "Esto no es algo que deberia ser una regla sino que es algo que yo decisi si pasa o no, la idea seria crear una skill llamada council parecuda a la de theo en su t3stack y si llamo la skill pues llega el council a hacer li que realmente quiero que haga" (verbatim, dictated). It replaces the Kino Rework 2 habit of five-judge panels on every wave: 8 of 8 first panels failed by design, 75 judge runs, 30% of the rework's tokens. -->

## 1. Read the request

Before seating anyone, pin down four things from his words, and state them in
one line to him as the council starts:

| Field | What it holds | Default |
|---|---|---|
| Kind | decision, review, design critique, plan or diagnosis | the closest reading of his words |
| Object | what the council looks at: a PR number, a diff range, files, a Postplan page, a question | what the conversation is about |
| Shape | what he gets back | the shape of its kind in section 4 |
| Action | what happens after the synthesis | nothing: the synthesis is the result |

The action is only what he asked. "Council on this PR" ends in the synthesis.
"Council on this PR and fix what they agree on" goes on to fix it, under
development-workflow. A council that edits when he asked for an opinion has
done something he did not decide.

## 2. Seat the members

Call `orchestrator_capabilities` in the same turn; the catalog decides, not
this file.

| Seat | Default | Effort |
|---|---|---|
| Claude | Sonnet 5.5 for a review; Opus 5.5 for a decision, design critique, plan or diagnosis | class `architect` or `delivery-reviewer` (both high) |
| Codex | the newest flagship the Codex instance lists | `reasoningEffort: high` |
| Third | the flagship of a third runnable provider; with only Claude and Codex runnable, the Claude model the first seat did not take | high |

Three seats, because two members who disagree leave the tie to this thread,
and a fourth seat adds a run per round for little new judgment. The Claude
seat follows Elias's model policy: reviews on Sonnet 5.5, design and diagnosis
on Opus 5.5. High is the ceiling, and xhigh, max or fast mode run only when he
names them.

A Claude seat that runs as an in-thread subagent (Agent tool) uses a typed
class, never `general-purpose` with an `effort`: `architect` (Opus 5.5 high)
for a decision, design critique, plan or diagnosis, `delivery-reviewer`
(Sonnet 5.5 high) for a review. Through `delegate_task`, put that class's model
and effort in `target.model` and `target.options`.

What he names wins: models ("council con opus y luna"), size ("council de
5"), rounds. A named member the catalog cannot run is reported, not replaced
by a lookalike. If fewer than two members can run, say which ones failed and
why (provider, auth, memory, per model-delegation) and stop.

## 3. Run the rounds

Codex and third-provider members run through `delegate_task`; a Claude seat runs
through it too or, in-thread, as a typed Agent subagent (section 2). Each
`delegate_task` call uses `mode: "wait"` with `timeoutMs: 900000`, all seats of a round in one message so they run and wait in
parallel, `isolation` shared, `role` `review` for a review and `design`
otherwise, `clientRequestId` `council-<slug>-r<round>-<seat>`. A seat that
returns without a result (`waitTimedOut`, a pending question or approval)
gets `task_cancel` with its `taskId` and counts as no answer. Waiting is what
enforces the cap: an async member that hangs never wakes this thread, so
nothing would cancel it. The members are read-only:
they read files, `git` and `gh`, and they never edit, commit, push, publish,
comment on a PR or start their own children. Every member brief says so.

**Round 1, independent.** Each member gets the same brief, written for a
reader with no context:

- his request, verbatim, and the kind and shape from section 1;
- where the object lives (paths, PR number, commit range, page URL), so the
  member reads it itself instead of a pasted dump;
- the constraints that bind the answer (repo contract, decisions already made);
- what to return, in at most 600 words: a position, the evidence for it with
  anchors (`path:line`, a command and its output, a URL), a confidence, and
  what would change its mind. For a code review, also a score out of 10.

**Round 2, cross-examination.** Each member gets a new task with the round 1
brief, its own answer marked as its own, and the other answers as "Member A"
and "Member B", without model names, so no one defers to a brand. It returns,
in at most 300 words: what each other answer gets wrong, with evidence; what
it saw that this member missed; and its final position, held or changed, with
the reason. A member that changes its mind says from what to what.

**Limits.** Two rounds, then the synthesis. When he asked for fixes, this
thread applies the ones the synthesis keeps and runs one confirmation round on
the diff of those fixes, and no more. A round waits 15 minutes for its
members (the `timeoutMs` above), the late ones are cancelled, and they count
as no answer for that round. Fifteen minutes is a starting value, not a measurement: report the
real durations each time so the next council has one. Findings that ask for
work outside his request are listed under "Out of scope" and not acted on.

## 4. Write the synthesis

Weigh evidence, not votes. Before a finding or a fact about code or data goes
into the synthesis, read it at its anchor: three members agreeing on a line
that says something else are three members wrong. One member with a
reproducible counterexample outweighs two without one.

| Kind | Shape |
|---|---|
| Decision | The recommendation in one line; each viable option with what it decides and what it costs; where each seat landed |
| Review | Findings by severity, each with its anchor, who raised it, who objected, and whether this thread verified it; the score of each member per round |
| Design critique | Agreed problems first, each with where, why and the fix; then the contested ones |
| Plan | Steps ordered by blockers, contested steps marked with the objection |
| Diagnosis | The most likely cause with its evidence, the alternatives still alive, and the one probe that separates them |

Every synthesis ends with two blocks:

- **Dissent.** Each disagreement that survived round 2: the positions, now
  with model names, the strongest evidence for each, and this thread's call
  with its reason. "None" only when every member converged.
- **Council.** Seats with model and effort, rounds run, wall time per round,
  child runs (three members and two rounds are six), any member that failed or
  was cancelled, and token use when `task_status` reports it, otherwise
  "not reported".

He reads it in the language he wrote in. Options he has to look at to
choose, or a synthesis too long for the chat: call the Skill tool with
"visual-briefing". When the object is an open PR and he asked for the result
on the PR, the score table goes into its body under `## Council review`
(rounds as columns, `no score` where a member gave none), drafted in a file
and published the way development-workflow publishes a body, never as a
comment. Without that ask the PR is not touched.

## 5. Then

Do the action from section 1, if there is one, under the skill that owns it.
Then stop. Another council happens when he opens one.
