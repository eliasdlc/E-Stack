---
name: rules-and-skills
description: How a rule, a skill, a subagent or a hook of Elias's gets written and corrected. Use it when touching anything inside ~/dev/agents, when creating or renaming a skill, when deciding whether something belongs in CLAUDE.md or in a skill, when writing a description, or when adding a hook.
---

# Rules and skills

The `~/dev/agents` repo is the configuration of Elias's agents. Its
maintenance contract lives in its `AGENTS.md` and rules over this skill. What
lives here is the judgment: what goes where, how it is written, and when a
lock is needed instead of a sentence.

## What stays in the core and what drops down to a skill

`rules/CLAUDE.md` loads on every turn of every session: a coding turn, a
design turn, a study turn and an accounting turn. A rule stays there only if
it governs all four. Everything else drops down.

Three tests, in order:

1. **The branch test.** If the rule only applies when there are pixels, or
   only when there is an APK, or only when there is a ticket, it is not core.
2. **The no-op test.** Read the sentence and ask what an agent does
   differently for having read it. If the answer is "nothing observable", it
   is surplus.
3. **The copy test.** If the concept is already written in another file, it
   does not get written again: pick an owner and have the rest point at it. A
   rule written twice is a contradiction waiting for its turn.

## The bar for a new skill

A skill needs a failure seen in a real session (the wrong output or the
repeated correction), named in the commit that adds it, because a skill written
from a guess pays its description in every turn for nothing. `agents usage`
shows which skills get called. When you remove one, add its name to `RETIRED_SKILLS`
in `bin/check.py` so it cannot come back unnoticed.

## The invocation axis

Every skill is one of two things, and it is declared in the frontmatter:

- **Model-invoked** (the default): the agent reaches it on its own. It pays
  for its `description` in the context of **every turn of every session**, so
  the description is written for routing: when it comes in, with which words,
  and when it does not, in the third person. Keep it under 1024 characters;
  past the listing budget Claude Code drops descriptions, starting with the
  least used skills.
- **User-invoked** (`disable-model-invocation: true`): only Elias opens it,
  with `/name`. It pays no context, and its description becomes one line for
  him, in his list of commands, not a list of triggers.

The cutoff rule: **model-invoked only if the agent, or another skill, has to
reach it without anybody asking for it.** If in practice he is always the one
who opens it, it is user-invoked.

What is vendored lives in `skills/vendor/` and is linked on no machine. It is
kept, it is consulted by reading it, and it does not get corrected. A skill
installed by hand (`npx skills add`) is not carried into the next generation:
it enters through the repo or not at all.

## How one skill calls another

Written as a tool instruction, never as a relative path:

    Call the Skill tool with "app-testing"

Two skills are two calls, and you say so. Never `../other-skill/FILE.md`: a
link between folders breaks the moment either of the two moves, and `agents
check` rejects it. If the dependency is a user-invoked skill, it does not get
called: Elias is told to open it.

## How it is written

- **Prompt the goal, not the prohibition.** Forbidding drags the forbidden
  behaviour into the context and makes it more available. "Headless, with a
  seeded account, always" works better than "never in the foreground". The
  prohibition survives only where there is a lock that really blocks it, and
  even there it travels with the positive version next to it.
- **Every rule carries its reason in one clause, and its story out of sight.**
  "Secrets are read with a tool that masks them, because a plain `sed -n`
  prints the key into the transcript" generalizes; the dated incident goes in
  the commit message or the skill's `references/history.md`. An HTML comment
  works only in `CLAUDE.md`, where Claude Code strips block comments before the
  model reads it; in a skill, comments reach the model, so a story left there
  is paid on every load. Keeping the story in a comment or a commit keeps the
  rule deletable the day its cause stops existing, without paying for the story
  on every turn.
- **Lead with the instruction.** The first words of a rule carry it, because
  the rest is skimmed: "Run `agents check` before committing", not "To keep
  the repo coherent, it helps to...". A description leads with its trigger.
- **The environment is a cache.** A path, version or count written in a file
  rots when the thing moves. Name the command that prints it and verify before
  relying on a copy.
- **Compose, don't add.** A new case first edits the rule or skill that owns the
  topic, because a second home for it contradicts the first.
- **Fight sediment.** Prose that only grows ends up as a paragraph per fix. A
  change that adds a line deletes the line it makes redundant.
- **American English, and technical terms stay in English.** Short sentences,
  imperative, with the consequence behind them.
- **No long dash**, in any file of the repo. When a sentence asks for one, it
  gets rewritten with a comma, a colon, a period or parentheses, whichever the
  sentence actually wanted. The character is never substituted blindly.
- **Tables for anything with fixed columns.** Prose only for a why or a
  tradeoff.

## Routing evals

The description is the only thing that routes a model-invoked skill, and a
description edited by feel can quietly stop loading, or start loading on
everything. So when such a skill is created or its description changes, the
evals are written next to it in `skills/<name>/evals/routing.json`, in the
shape of `skills/visual-briefing/evals/routing.json`: `skill`, and `cases`,
each with `id`, `message`, `situation`, `expect.loads` (true or false) and
`check` (what a reader of the transcript looks for). A user-invoked skill has
none, because nothing routes to it.

Eight to twelve cases:

- **Should load**, half of them: the same intent in different words, one formal
  and one casual with a typo, at least one in Spanish as he dictates it, one
  that never names the skill, one where another skill competes and this one
  should win.
- **Should not load**, the other half: near misses that share a word with the
  skill but belong to another skill or to none ("how do hooks work in general"
  against "add a hook"). An obviously unrelated message tests nothing.
- Messages as he would really type them, with a path or a bit of backstory. A
  request the agent can do with basic tools alone loads no skill whatever the
  description says, so a trivial message is a bad case.

To run them by hand, after the description is final: for each case, start a
fresh `claude -p "<message>" --effort low` session (with `--output-format
stream-json --verbose` the tool calls are in the output) and look for a Skill
tool call naming the skill. Loading is not deterministic, so run each case three
times; a should-load case passes at two of three, a should-not case at zero or
one. Re-run only the failed cases with `--effort high`, and a case passes if
either pass does, because low then retry costs less than all high. Put
the table of results in the PR, not in the file. A run spends model calls, so it
happens when a description changes, not on every commit.

To improve a description that fails: for a missed should-load, add the words he
actually uses for it; for a should-not that loaded, add the exclusion ("Not
for ..."), not another keyword. Tune against about 60 percent of the cases and
check against the rest, and keep the version that does better on the held-out
ones, so the description does not memorize its examples. Three rounds at most;
it stays under 1024 characters.

`tests/test_external_practices.py` checks that every `routing.json` is well
formed (unique ids, boolean `expect.loads`, cases in both directions, the skill
named as its folder). It reads files and runs no model, so it cannot show that
an agent routes as the file expects; only the hand run can.

## The cause before the lock

**An incident is a symptom. Find what keeps producing it and fix that; a rule
or a hook over a cause that is still there is tape on a bowl that keeps
falling.**

Before writing any new line or hook, trace the incident to its producer and
write it down: the rule, skill, tool or hook of this repo that made the agent
do it, the harness behavior it ran into (Claude Code, T3 Code), or the way the
work was asked for. Then pick the fix by where the cause lives:

| The cause lives in | The fix |
|---|---|
| A rule, skill or tool of this repo | Change or delete that producer. Do not add a second text that counters the first |
| Another hook | Fix that hook; a hook that forces a workaround is the defect |
| Work that runs in the wrong place (long jobs on the agent's machine, evidence the agent asserts) | Move the work to where it is observed (CI, a tool that returns the result) |
| The harness, and nothing here can change it | A lock, sized to the harness behavior, and an upstream report |
| The model's defaults | A lock or a validator, only where breaking it is costly |
| How Elias asked | Tell him, with the evidence, next to the weekly `agents scorecard` |

**A change to how Elias works shows him the day before it ships.** Its PR or
decision page carries a before and after of one real session: threads opened,
calls denied, times it stops for him. A cost table alone approved a ceiling
that cut his threads into continuations.

**One in, one out.** A new hook that denies, or a new rule in the core, names
the one it replaces and deletes it in the same PR.

**A hook denies only what cannot be undone or what is his taste**: `secrets`,
`delivery`, `evidencia-road`, `launch-in-t3`, `design-identity`, and the look
at visible work that `turn-close` asks for. Anything else
fixes the call silently (`updatedInput`), runs in CI, or warns.

A lock is still the fix only for the last three rows, and then by kind:
`PreToolUse` for a pattern in a command, a check in `bin/check.py` for files
incoherent with each other, a validator in the tool for a malformed document,
prose for a judgment. Every hook declares in `hooks/registry.json` its `cause`
and its `remove_when` (the condition that retires it, or `never: <reason>` only
when the cause is outside the repo and permanent: an irreversible act, a model
default, a cost), and `agents check` refuses one without them,
so the hook leaves the day its cause is fixed. A lock never parses prose to
guess intent: from 1 to 9 Nov 2026, 45 of 66 `turn-close` blocks came from
such guesses, about 17 were false, and each one buried the answer under a
correction.

## The ceremony

A validator or a hook **is not done** until its three step run has been seen,
pasted in the message:

1. It passes with the repo as it is.
2. It **fails** against a violation fabricated on purpose, and the message
   names the rule that fired.
3. It passes again once the violation is undone.

A check that was never seen failing checks nothing.

## When you finish

- `agents check` green. Whatever comes out red gets fixed or gets named in the
  commit with the phase that closes it.
- A hook is registered in `hooks/registry.json`, never by hand editing a
  machine's `settings.json`. One that lives outside the repo is declared with
  its whole `command` and with a guard, so a machine without that file does
  not fail.
- Commit and push the task branch in the same session, open the PR and merge it
  on the development-workflow merge criteria; authority rules, gating hooks and
  the installer wait for Elias. After the merge reaches main, enrolled machines
  pull it automatically. Do not
  install a task branch into the live configuration.
- A machine file (`machines/<hostname>.md`) loads on every turn of its machine,
  so it holds identity, what the machine owns, the screen rule and the ssh
  wrapper in 2,048 bytes at most (`agents check`); the rest goes to the skill
  that uses it. The CI of this repo, while GitHub blocks its Actions, is in
  `references/ci.md`.
