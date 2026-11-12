# Incidents as evals

Two texts decide merges: the merge criteria and the needs-my-eye list in
`skills/development-workflow/SKILL.md`, and the brief in
`subagents/delivery-reviewer.md`. Each confirmed incident that went wrong on
one of them becomes a small case in `tests/fixtures/incidents/<id>.json`, so a
change to the text, the scripts or the model is scored against what already
happened.

## A fixture

| Field | Meaning |
|---|---|
| `id` | The file name without `.json` |
| `kind` | `diff` (changed files against the needs-my-eye row), `proof` (a PR body for `agents proof`), `judged` (needs a model: a closing that parks, his approval words) |
| `judged_by` | `script` or `model`; a `judged` kind is always `model` |
| `basis` | `recorded` when the input is what the incident produced, `reconstructed` when it is rebuilt from the rule or test the incident led to (say so in `note`) |
| `source` | `commit` and/or `pr`, `date`, `note` where the incident is recorded |
| `input` | What the kind needs: `closing`; `messages`, `closing`, `commands`; `changed_files`; `body`, `created`, `files`, `logs`; or `pr` (a PR body and diff summary written out) |
| `expected` | `verdict`: `merge`, `park` (with `rule` naming the row for a model case) or `block` (with `rule` naming what it caught) |

An incident goes in as it happened: the real closing, body or file list, with
the source that recorded it. A case reduced from a long story says so in
`note`.

## Deterministic part

`python3 -m unittest discover -s tests -p test_incident_evals.py` reads every
fixture. For `judged_by: script` it asks the code that enforces the rule, with
no model: the needs-my-eye row read from the skill, and `bin/proof.py`. For
`model` cases (a park without a row, approval words that must merge) it checks
the shape, that the cited commit exists and that the gating text still names
the expected row or criterion.

Add a fixture for a new incident the three-step way: it passes against the
repo, flipping its `expected.verdict` makes the test fail naming the fixture,
and restoring it passes.

## Rerun the model-judged cases by hand

Rerun when the gating text, the reviewer brief or the model changes, like the
routing evals. A run spends model calls, so it does not run on every commit.

1. List them: `grep -l '"judged_by": "model"' tests/fixtures/incidents/*.json`.
2. For each, start a fresh session of the model under test with only the
   gating text and the case input. Example:

       claude -p "You apply the merge criteria and the needs-my-eye list below.
       Answer with one line: merge, park with the row, or block with the
       criterion.

       $(sed -n '/^# Merging/,$p' skills/development-workflow/SKILL.md)

       Case: $(jq -r .input.pr tests/fixtures/incidents/<id>.json)"

   For the reviewer brief, give the case as the PR body and diff summary and
   read whether `subagents/delivery-reviewer.md` would report the row as a
   counterexample.
3. Run each case three times. It passes when two of three runs give the
   expected verdict (and name the expected row or criterion for a `park` or
   `block`).
4. Put the table of results in the PR, not in the file.

A case that fails after a text change means the text lost the incident's
lesson: fix the text, not the fixture. A case that fails only on a new model
goes to the next weekly `agents scorecard` page.
