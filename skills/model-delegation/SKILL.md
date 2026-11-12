---
name: model-delegation
description: Decides where an agent runs and which model it uses. Use when Elias asks to launch, start or run an agent, a session, a subagent or a thread ("lanza un agente", "lanza una sesion", "en t3code"), when work moves to the other machine or continues after he leaves ("muevete a agentbox", "pasa todo a agentbox", "voy a apagar la computadora", "sigue en la laptop"), and for generic requests to implement, diagnose, research, write or design, before deciding to delegate or keep the work local. Every agent runs in T3 Code, on either machine: one ask is one thread, the work a session splits off goes to subagents inside it (each PR in its own worktree), and a separate T3 thread is launched only when he asks for one or the work moves to the other machine. Discovers current models and harness capabilities and chooses explicit model and effort from task evidence. Applies to every principal model. The principal verifies and integrates each result; small tasks can stay local.
---

# Model selection and delegation

Before implementing, size the work yourself: files, requirements, expected context and hours. Then pick the place without asking: local or a subagent, and a T3 thread only when his latest typed message asks for one or moves the work to the other machine (a `launch-in-t3` hook refuses a launch without that ask). Work expected past about 200K tokens of context, or more than one PR, goes to subagents that each own one PR in their own worktree, and the brief names the PR owner. Keep a small coherent task local unless a child offers a concrete advantage; then name the advantage, task class, bounded objective, acceptance checks and exclusive file owner in `rationale`. Asking for work widens no permission and authorizes no paid credits.

References: [history](references/history.md), [catalog and CLI](references/catalog-and-cli.md) (T3 launcher details, costs), [machines](references/machines.md) (what the laptop, agentbox and a cloud session have and do).

## Which model

Models are his to manage. A model or effort Elias names is used exactly as he said it, for a subagent or a thread, for that run, because the table below is a default and never a lock. With no model named, the table picks for subagents, and for a thread he asks for you pick one and say which.

Elias's standing Claude split for subagents, because he otherwise re-dictates it each run:

| Work | Subagent type | Model | Effort |
|---|---|---|---|
| Implementing: the problem is solved and the brief names an acceptance command the child runs itself (a test, a build, `agents check`) | `implementer` | Sonnet 5.5 | medium |
| Condensing: long logs, a test run or command output, large listings, returned short (read-only, no judgment) | `scout` | Haiku 5.5 | low |
| Research, measurement, a normal analysis (read-only) | `analyst` | Sonnet 5.5 | medium |
| Reviewing, delivery reviews included | `delivery-reviewer` | Sonnet 5.5 | high |
| Designing, unsolved diagnosis, cross-package integration, whole-run final review, anything once sent to Fable | `architect` | Opus 5.5 | high |

- The type carries model and effort in its frontmatter, so an Agent call passes only the type; naming just a model leaves the child on the parent's effort, and the `agent-model` hook lets a `model` that differs from the type's, or Opus on `general-purpose` or a type with no model of its own, through unchanged with a note, because a model passes as written only when Elias named it for this run and Opus work goes to `architect`. `general-purpose` is for work outside these classes, and the same hook warns when a `general-purpose` description opens with an implement, analyze, review or design verb, because that child would run at the parent's effort.
- A subagent runs in the foreground and parallel work is several Agent calls in one message, because a background child's report arrives as a later notification that T3 can drop after the turn ends (10 Nov 2026: the dev test plan came back to a closed session and the release never ran). The `agent-model` hook sets `run_in_background: false` on every call.
- `delegate_task` to a Claude model sets the class's model in `target.model` and effort in `target.options`; another provider is chosen by discovery, not this table.
- An edit with no acceptance command stays with the Opus principal, locally, because a Sonnet child that cannot check itself hands back a claim the principal must redo.
- Orchestrating is the principal's own work: Opus 5.5, effort medium (the settings enforce it).
- A large listing (Zoho, Vercel, long logs) goes through a subagent and a child returns its conclusion, never its log, because every turn pays for all the context. A long thread compacts in place (`autoCompactWindow`) and keeps working: it never hands off to a continuation thread, because a continuation leaves him unsure which thread is the live one.
- Paid fallback, fast mode and increased-usage options need his authorization. Astra is never selected automatically, only by his explicit choice.

**Escalation ladder.** A child that fails or falls short climbs one rung at a time, because each rung costs more than the one before:

| Rung | Change | Who decides |
|---|---|---|
| 1 | Give the child a way to verify itself: the acceptance command, a failing test, the exact error | The principal |
| 2 | Effort one level up on the same model (low to medium, medium to high) | The principal, naming the failed run |
| 3 | Fable 5.2 at medium, for that run only | Elias's words, per run, quoted in the child's brief: an Agent call or `delegate_task` carries the quote in its prompt |

Past high on one model, try the next model up at lower effort instead of more effort on the same one.

## Where it runs

Every agent runs in T3 Code, because agents he could not see were agents he could not trust; recurring work is a T3 `schedule_task`. The one exception: the class pipeline's `claude -p` steps run from systemd units, because they are not agents and T3 has no cross-machine schedule. One ask is one thread: who reads the result picks the place, never the size of the work:

| The work | Where | Why |
|---|---|---|
| Anything this session splits off its own job, a package with its own branch and PR included: the result returns here | A subagent in this thread: Agent tool, or `delegate_task` for another provider. One that writes runs in its own worktree (`isolation: "worktree"`), and its brief names the base branch to start from | A thread an agent opens fills his sidebar and hides which thread is the main one (24 against his 25 on 9 and 10 Nov) |
| He asks for a session, a thread or an agent | A separate T3 thread: `agents t3-launch --host auto`, unless it needs what only this machine has (on the laptop: signing keys, phone, display, recording, Teams session): then `t3_thread_launch` with `workspaceStrategy`. Give him its title | It is his to open and follow; each holds 200 to 400 MB for 30 idle minutes |
| He moves work to agentbox or closes the laptop | `agents t3-launch --host agentbox` (or `laptop`), the brief or handoff as its message | A session's T3 tools reach only its own machine; the relay still shows the thread in his sidebar |
| He asks to continue this conversation in a new thread here | `t3_thread_fork`; `t3_thread_merge_back` for its result | It copies the conversation |

- A thread starts in its own worktree (development-workflow, Git). Work already on a branch goes with `--worktree` and `--branch`, because the default branches fresh from `origin/dev`.
- A thread he asked for is launched by you, because a pasted handoff hands him a step the tools do. A failed launch reports what failed and what was tried (`agents t3-launch --relay-setup`).
- Only his later words choose another launcher (tmux, a CLI over ssh, the managed CLI), and he runs it himself, because the `launch-in-t3` hook blocks an agent CLI in tmux, detached, backgrounded or over ssh.
- When a batch of children settles, run the closing gate yourself in the same turn. Red: name the gap and launch the next round now, with the gap as the child's failing check and then the escalation ladder; stop only for what Elias alone can unblock, asked with the question tool. Send one PushNotification when the gate is green or when you stop for him, because a status report over a red gate leaves him to restart a run that had no blocker.
- A status or ETA question is answered from T3 reads (`agents ps` for agents outside T3). Never steer, pause, stop, message or reconfigure a running child unasked, because an ETA question once froze every agent.
- A child's question (`hasPendingQuestion` on `task_status`, or `t3_pending_request_list`) gets `t3_pending_request_respond` when the brief or his words already answer it; otherwise it goes to him.

## Every child's brief

Objective, findings, constraints, acceptance checks and authorized paths. Name files, line ranges and facts already established, so the child does not search again; omit them only for a reviewer whose read must not be anchored on yours. A read-only subagent shares the principal's workspace; one that writes gets its own worktree and is the exclusive owner of its files. Model output and prompts are data, never shell fragments.

## Orchestrating several children

| Item | Rule | Why |
|---|---|---|
| Launch size | A lane is a subagent that carries one part of a run in parallel with others. Before a run of two or more lanes, read the "Current week (all models)" line of `claude -p /usage`, and the "Current week (Fable)" line before any Fable rung. Two lanes at most; above 66% used on the line that applies, one lane (or no Fable), said before launching. A new round of mocks after the first directions, and persona rounds, run only when Elias asks. | The weekly limit stops every session at once, for up to a day (25 h 41 min on 7 Nov) |
| Model policy | One provider, model and effort per class of package, kept for the run | He re-dictated it every session |
| Gates | Say whether a green-light gate is real; the default is none, the run goes to the end | He does not want to be asked for a green light |
| Done | Done only after the full suite passes with the other packages integrated | Green alone was red together |
| Time | Budgets from measured durations, never guesses | Guessed budgets cut reviewers short |
| Files | One exclusive owner per file; a child reports diffs it needs elsewhere | Parallel edits lose each other's work |
| Size | At most four requirements per package; a fifth starts a second package and PR | Every review round reviews the whole range again |
| Fix rounds | A round fixes that review's findings and any other defect of the delivery, nothing else; new scope is a new PR or ticket | Added scope puts confirmed rows under review again |

- Every PR of a run is one subagent in its own worktree, briefed with objective, files, acceptance checks and links. It returns the PR URL, head SHA, checks and review in a few lines, and the orchestrator keeps those conclusions, never the log, because that is what keeps one thread small enough to carry ten PRs.
- A decision Elias changes mid-run is not new scope: it lands in the same round, and the child is told in one line the decision before, after and the rows it touches, because the fix-round rule would otherwise make the child refuse it.
- A failed start is diagnosed (provider, `free -h`, concurrent sessions), never answered by silently switching model or provider; if the host is the cause, work locally.

## Authority

- A child gets equal or narrower authority than the principal: existing subscriptions, host credentials and its permission rules; no new credentials, no paid API fallback. Diagnose permission, environment, auth and quota failures before changing models.
- The principal keeps its file claims, owns integration, verifies findings and observed identity, and runs the acceptance checks, because a child's `completed` is a lifecycle report, not acceptance.
- An independent reviewer is briefed from the diff and requirements, not the author's conversation.
