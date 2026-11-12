---
name: grill-me
description: Relentless interview that settles every decision of a large task before work starts.
disable-model-invocation: true
---

<!-- Trial of decision 3A, one week, review on 2026-11-13: keep it, change it or delete it by what the week showed. Based on Matt Pocock's `grilling` and `grill-me` (github.com/mattpocock/skills, skills/productivity), MIT. One change, by Elias's note of 6 Nov 2026: questions go through the AskUserQuestion tool, which T3 Code renders as a picker, because it is faster and more comfortable than typed answers. -->

Interview Elias until you both hold the same picture of the task. Map it as a
**design tree**: every decision branches into the decisions that hang off it.

## Facts are yours, decisions are his

A fact the environment holds (a file, a tool, a log, a measurement, the state of
a repo) is yours to find, never his to answer. Read it yourself, or hand it to
a subagent with a fresh context, and do not block on it: only the questions
downstream of a running lookup wait, so ask the rest of the frontier now. A
decision (scope, taste, cost, risk, priority) is his: put it to him and wait.

## Rounds

The **frontier** is every decision whose prerequisites are settled: what you
can ask now without guessing at answers you have not heard. Ask the whole
frontier in one round. A question whose answer depends on another still open in
this round belongs to a later round. His answers reshape the tree, so recompute
the frontier after each round and ask the next one.

## How a round is asked

Use the AskUserQuestion tool, at most 4 questions per call. A frontier larger
than 4 goes out as consecutive calls of the same round, with no lookup or
reasoning for him to wait on in between.

- The recommended option comes first and ends with "(Recommended)". Word each
  question so accepting it is the shortest path.
- Each option says what it decides and what it costs, in a clause.
- "Other" is always open, and a free-text answer counts as fully as a pick.
  Pickers push toward multiple choice, which is the failure to avoid: when a
  question has no sensible options (a name, a number, a story, a constraint
  only he knows), ask it open, in plain text, and not as a forced choice.
- A choice that is not exclusive uses `multiSelect`.

## Done

The session is done when the frontier is empty: every branch visited, nothing
assumed in silence. He ends it by saying enough, and until then you keep
asking. Then write the settled decisions as a short list in the chat (one line
each: the decision and its answer), and go into the normal workflow: call the
Skill tool with "development-workflow" and start from the decisions, with no
further questions about what he already settled.
