# PR bodies and proof

Read before writing a PR body, taking captures for one, or answering a red `agents proof`. The `body_template` gate covers the template and `proof` the checks (`SKILL.md`, Whose PR rules apply). An organization with `proof` on keeps `evidence` off unless it says otherwise: only the body-reading rules apply (no red-first logs, cites, suite counts, self-check or build receipts) and nothing is published.

## PR bodies
The PR is the delivery document, the one I read instead of the diff. It is written for someone who was not in the session: what was wrong, what caused it, what you did, what proves it. Every line is a fact with its anchor (`file.ext:line`, a command with its output, a URL); a section with nothing real in it is deleted, never filled. Left out and Door are optional for that reason; a one-way change (migration, shipped contract, data rewrite) always carries Door. Tables, `<details>` for anything long, tickets by title with their link.

The body opens with `## At a glance`, the only part Elias reads on every PR: four lines (`Changes:` what changes for the user, `Risk:` in one line, `Look at:` the screen, flow or file worth his eye, `Revert:` the commit or flag that undoes it), 120 words at most, because a 1,500 word body spends his attention on evidence a script already checked. Long evidence (mutation lists, benchmarks, dumps) goes inside `<details>` below. A PR that adds more than 800 product lines (tests, fixtures, goldens, generated code and lockfiles not counted) is split, or carries a `Size:` line there saying why it stays one, because a small PR is what keeps review, debugging and a revert cheap. `agents proof` checks both on every task PR.

```
## At a glance
- Changes: <what changes for the user, one line>
- Risk: <what could break, one line>
- Look at: <the screen, flow or file worth a look>
- Revert: <the commit or flag that undoes it>

## What was asked
<the request in one line, and the ticket by title with its link>
- R1 <each requirement, one line, from the ledger>

## The problem
<the symptom as it was observed: the screen or the command, what happened, what it cost whoever hit it. "X was missing" is not a problem statement>

## Root cause
<the mechanism, at `file.ext:line`: what the code did, why it did it, and why that was wrong. If a test or a check should have caught it, why it did not>

## The fix
<the approach and why this one. The alternatives discarded, each with its reason. Anything here I would want to argue with>

## What changed
| File or screen | Before | Now |
|---|---|---|
| `path` | what it did | what it does now |

## Proof
Proof at `<sha7>`: <the link: preview, build or evidence page>

| Req | What it proves | Channel | Evidence | Seen |
|---|---|---|---|---|
| R1 | <the property> | `render` | <the capture, inline> | <what the capture shows that matches R1, specifically> |
| R2 | <the property> | `test` | `<command>` → <literal output, with numbers> | |

Self-checked at `<sha7>`: [self-check-<sha7>.txt](<url>)   <!-- only for a PR opened before 12 Nov 2026 -->
Not verified: <what, and why nobody could>

## Risk
<what this could break, what to look at twice, what stays half done>

## Left out
<what was asked and not done, or deliberately excluded, each with its reason>

## Door: one-way or two-way
<how reversible this change is, and the revert path (the commit or flag to undo it, and what a revert would not undo)>
```

## No merge without proof

`agents proof <n>` judges the body and names each failure with its rule and body line. The rules live in `bin/proof.py`; the one date left, `VERIFY_FROM` (offline `--created <ISO date>`), keeps the self-check for PRs opened before it. What the code cannot decide is below.

- **Test rows.** A test that pins product behavior is a `test` row (`nonvisual` is for tooling). It links a red-first log of that test failing with the fix reverted or mutated, published with `agents evidence ... --dir datos`. A run that only failed to compile proves the symbol is new, not the behavior: mutate the fix instead. Without a failing run the test pins nothing.
- **Pending: batch.** In a task PR into `dev`, a `native`, `device-simulated` or `real-trip` row may say `Pending: batch` in its Evidence or Seen cell, needs no `proof:laptop`, and is refused in a PR into `main` or on any other channel. The device session that closes it runs once for the whole batch, on the laptop.
- **Release checklist.** A release PR (`dev` into `main`) lists every row its task PRs left `Pending: batch` under `## Release checklist` (columns PR, Req, Channel, Evidence), each with evidence taken at a commit that contains its task PR, the batch receipt for device captures, and, before `VERIFY_FROM`, a self-check verdict keyed `#<pr> R<n>` (after it, the capture rules apply to those rows). `agents proof` fails the release on a missing, pending, stale or re-channelled row.
- **Receipts.** `native` and `device-simulated` captures link `datos/recibo-<sha7>.txt`, from `agents evidence ... --receipt <package> --apk <installed APK> [--serial S]` right after the captures, from a clean worktree. A versionName carrying the sha7 ties the build and needs no `--apk`.

**Capture rules** (PRs opened on or after `VERIFY_FROM`, 12 Nov 2026, in `bin/proof.py`). No model reads the captures: three deterministic rules do, each failure starting with its code, and there is no `Self-checked at` line (one in a newer body is ignored with a note).

| Rule | It holds when |
|---|---|
| `CAPTURE_RECEIPT` | Every capture sits under an evidencia `<sha7>` folder, so a commit ties it (a `render` image from anywhere else fails), and a `native` or `device-simulated` capture links `datos/recibo-<sha7>.txt` with its fields, a clean worktree and a build line that ties the APK to that commit |
| `CAPTURE_STALE` | The capture's commit is in the head's history and no product file the row covers changed after it (the Row by row rule below; a capture is not required to be at the head, or one fix would discard every screen it never touched) |
| `CAPTURE_SCREEN` | The file is named `r<n>-<screen>[-<viewport>].<ext>` for its own row (`r1-settings-393.png`), a screen word appears in the row's What it proves or Seen cell, and Seen says what the frame shows in 4 words or more |

What stays judged is whether the pixels show the property (value, color, clipping, overlap, placeholder data): the author looks at its own frame before writing Seen (`app-testing`, verified capture), Elias looks at `Look at:` on a needs-my-eye PR, and a scoped review round (`references/review.md`) reads the risky rows of such a PR. The capture-mode self-check of `delivery-reviewer` (the `Self-checked at` line, `self-check-<sha7>.txt`, one verdict per capture) applies only to a PR opened before `VERIFY_FROM`, which keeps its earlier rules unchanged.

Publish the body once, when its proof is ready: draft it in a file, run `agents proof --body FILE --head <sha>` offline until it passes, then `gh pr edit <n> --body-file FILE` and `agents pr ready <n>`. A review round, where Review scope says one runs, happens while the PR is a draft, because every body edit on a ready PR reruns the proof and branch-model gates in CI. A budget ceiling quoted after the budget run needs `gh run rerun <run id> --failed`, because the budget gate runs once per commit.

**Row by row.** A row goes stale only when the fix touched files it covers. Coverage is derived (for a `test` row, the test file it names and its imports; for any row, the files its cells cite); where it cannot be, the row declares a `Covers` column of paths or globs, and a typo that matches no product file covers every one. Every row also covers manifests and lockfiles. The `Proof at <sha7>` line goes stale on any product change, so the full proof runs once on the final head.

**Generated Proof table.** Do not type the Proof table by hand. Write each row's Req, what it proves, channel and command or capture, then run `agents proof --draft BODY --base origin/dev --self-check FILE` (the flag only for a PR opened before `VERIFY_FROM`; on agentbox through `agents heavy -- agents proof --draft ...`, because it runs the tests). It runs the command at the head, reverts the covered files to the fork point (or applies the patch named `mutate: <file.patch>`), requires the red run to fail naming the test, publishes both logs and writes the table with its counts, shas, links and Covers cell. Copy its output into the body; `agents proof --body FILE --head <sha> --base origin/dev` has the last word.

**Shadow week** (decision 1A, 11 Nov 2026). Every `agents proof <n>`, and so every `agents pr ready` and `agents pr merge`, also runs the collapsed checker `bin/proof_gate.py` in a detached process and logs both verdicts to `~/.local/state/agents/proof-shadow.jsonl`; `bin/proof.py` still decides. A `ready` read against `.proof/<branch>.toml` is logged too, apart. The shadow judges the PR the old verdict saw: one merged since is read against its base just before the merge, and a moved head or a low GitHub rate limit leaves the row not compared. `agents proof --shadow [--log PATH ...]` summarizes one or both machines' logs: same verdicts, and each difference with the rules only one checker gave, explained (a rule the collapsed checker drops on purpose, or the self-check of a PR opened before `VERIFY_FROM`) or not. After 7 days the collapse PR switches to it once nothing stays unexplained.

`agents pr merge` refuses a red proof, with the red rows as its reason. A change with nothing to see proves itself with the command that pins its behavior (`test` or `nonvisual`), never with a picture of something else. What each kind of change needs is in `app-testing`, which also produces it.

## Proof in CI

A repo whose CI runs the proof action (decision 1A, 9 Nov 2026) has no Proof table, no self-check and nothing published to evidencia: CI runs each row and reports what it saw. `agents proof <n>` tells the two apart by the `proof-rows` check at the PR head (`agents pr ready` reads the body against the spec, because the rows run only once the PR is ready); where it is missing the legacy rules of this file apply unchanged. A release PR (`dev` into `main`) keeps the legacy gate until release mode lands.

Write `.proof/<branch>.toml` in the branch (a slash in the branch name is a folder), one row per R of What was asked, and commit it with the tests it names. `validate.py ledger.json --render toml` prints a start whose empty `run` keeps it red until filled.

```toml
[[row]]
req = "R1"
proves = "one claim per owner per month"
run = "pnpm exec vitest run test/monthly-report-run.test.ts"   # repo-relative, names its test file
red = "revert"     # default: the covered product files go back to the merge base. Or "mutate:R1.patch" in .proof/<branch>/
covers = ["src/lib/monthly-report/run.ts"]   # optional; default every product file the PR changed

[[row]]
req = "R2"
proves = "the Hoy card shows the closed month"
channel = "render"   # a Playwright spec; its screenshots go to the artifact, To look at. red = "none" lists it unproven
run = "pnpm exec playwright test e2e/hoy.spec.ts"

[[row]]
req = "R3"
proves = "the route sheet follows the real map"
channel = "device"
pending = "batch"    # into dev only; the laptop's batch session owes it

[[row]]
req = "R4"
proves = "the Resend email arrives"
channel = "manual"
reason = "no real send from CI"   # replaces the body's Not verified line
```

In the repo's CI job, after its install, `bin/proof_ci.py` runs each distinct row at the head and again without its fix, resets the checkout after every run, and reports the `proof-rows` check, a sticky comment and the artifact `proof-<sha7>` (every log, Playwright screenshots, `results.json`). The red run must exit non-zero, fail on an assertion rather than only a missing symbol, and name the row's test failing. A separate short job, `bin/pr_body.py`, reports `proof-body`: every R under What was asked has a row, and the At a glance and size rules above hold. Each failure names its rule, listed in `RULES` of both scripts. A body edit reruns only `proof-body`; a push reruns the rows, so fix a red row with a commit, never with words.

Merging: where the head has `proof-rows`, `agents proof <n>` (and so `agents pr merge`) is red while either check is pending or red, `proof-body` has not reported, or a check judged another body or base than the PR has now (`STALE_INPUT`: each check records them, because a body edit or a retarget makes no commit); a head with no `proof-rows` gets the legacy gate. Wait on them with `watch_pull_request`, never a loop; the job takes about as long as the tests it names, and nothing runs on your machine.

Opting a repo in, under the deploy key (agents' Actions access stays `none`, so a private repo cannot call `.github/workflows/proof-body.yml` yet): the CI job that installs gets `fetch-depth: 0`, `checks: write`, `pull-requests: write`, the `edited` event with `if: github.event.action != 'edited' || github.event.changes.base` (a retarget reruns the rows, a body edit does not), and as its last steps

```yaml
      - uses: actions/checkout@v4
        with: {repository: eliasdlc/agents, ref: main, path: .agents, ssh-key: "${{ secrets.AGENTS_KEY }}"}
      - uses: ./.agents/.github/actions/proof
        with:
          wrap: firebase emulators:exec --only auth,firestore --project demo-conocerd   # empty without emulators
```

and `proof.yml` keeps its trigger and draft skip, with a job named `body` (never `proof-body`, the check's own name) holding the same checkout and the action `with: {mode: body}`, and permissions `contents: read`, `checks: write`, `pull-requests: read` (an explicit block sets every other one to none). Then the ruleset of `dev` requires `proof-rows` and `proof-body` instead of `proof`; the ruleset of `main` keeps `proof` until release mode.

Captures stay on the machine that took them, under `Documents/Proyectos/<Project>/dev/evidence/<branch>/<sha7>/`. A PR renders an image only from a public URL, so `agents evidence <project>/<branch>/<sha7> <files>` keeps the original there and publishes a scanned copy to `eliasdlc/evidencia`, printing the Markdown for the body. Images, video and text files all go through it and nothing reaches that repo any other way, because a push with `gh api` or `git` skips the scan and that host is world readable forever. The command's refusals are in `bin/evidence.py`.
