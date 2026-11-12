# Performance budget

Read when a product repo gets its budget, a metric is added, or a PR's budget table is red. The criterion "The budget holds" is in `SKILL.md`.

Every product repo whose PR policy has the `budget` gate (`SKILL.md`, Whose PR rules apply) measures its deterministic costs (bytes, counts, permissions) on every PR and on every push to `dev`, and posts one sticky table that updates in place (dev baseline, this PR, impact, ceiling, pass). A metric above its ceiling blocks the merge. A ceiling rises, and a guardrail (new permission, new package, new minSdk) passes, only in a PR whose body quotes my approval from the chat as `Ceiling raise approved: "<my words>"`. That quote counts as the one human review, so the PR merges on the criteria once it is there, and without it the PR waits for my words.

## What blocks and what only shows

Only a deterministic number blocks: bytes and counts come out the same for the same build, so they need no repeats and no tolerance. A timing moves with the runner, so it is shown with its median and spread and never blocks. A guardrail is a change of kind rather than size. `bin/budget.py` computes the verdicts (block, warn, show, the 5% growth warning); a warning on a deterministic metric makes the PR's Risk section say why. A measurement missing while the paths it measures changed blocks, enforced by the repo's gate script (the APK rows excepted: only the review build measures them).

## Metrics per stack

A metric enters a repo's table when the repo has the stack. Each repo's measure script owns the exact set; these are the ones that belong, by rule.

| Stack | Blocks | Guardrail | Warns or shows |
|---|---|---|---|
| Flutter app (the ConoceRD app) | APK arm64 release bytes and `libapp.so` bytes (review build and `dev` pushes only); assets bytes and the five largest files (every PR, no build) | Android permissions, minSdk and targetSdk, packages new in `pubspec.lock` | native libraries bytes, `flutter test` duration, cold start and frame build p90 (laptop only, posted as a PR comment); analyzer issues warn on +1, coverage on a 1 point drop |
| Web (Next.js, Vite: the web repos, dashboard, admin) | shared JS KB, total client JS KB, CSS KB, font KB, home page image KB | | home requests and HTML bytes, npm packages new in the lockfile, build time; Lighthouse performance, LCP and TBT (lab, median of 3) warn past +20%, CLS over 0.1, accessibility on any drop |
| API (conocerd-api) | Firestore reads, writes and response payload bytes per key endpoint, against the emulator fixture | | server bundle bytes, packages new in the lockfile; p50 and p95 latency (median of 20) warn past +50%; coverage on a 1 point drop |
| Every repo | | | CI minutes of the measuring run; baseline commit and whether it is the merge base |

## Mechanics

- **Measure** in the repo's own CI job, with a script the repo owns that prints JSON rows `{metric, unit, value, ceiling, rule}`. It runs on `pull_request` and on `push` to `dev`, and uploads the JSON as the artifact `perf-results` (90 days). Kino's `scripts/check-bundle.mjs` is the existing example of a blocking size script.
- **Report**: `bin/budget.py` of this repo does the rest: `baseline`, `report` (exits 1 on a blocking problem) and `post`. The baseline is the `perf-results` of the successful `dev` push run at the PR's merge base, else the latest successful one (the table says so), else the PR sets the first measurement.
- **Ceilings** live in the repo, in `perf/budget.json`, reviewed like code. A first ceiling is the first measurement plus 10%, rounded up for bytes and down for counts, because 10% of 4 reads is not a whole read and rounding up would allow one more read per call. Any ceiling that rose, and any guardrail diff against the baseline's `perf/budget.json`, needs the quote in the body.
- **How a repo gets the checks**: `.github/workflows/delivery-gates.yml` with two jobs, `proof` and `budget`, both required in the repo's rulesets for `dev` and `main`. They read `bin/proof.py` and `bin/budget.py` from this repo's `main` with a read-only deploy key, kept as the secret `AGENTS_KEY` in each repo; its private half lives in `~/.config/secrets/agents-ci-deploy-key` on the laptop, for the next repo. A body edit waits for the running pass instead of cancelling it, because a cancelled run on the same commit leaves the PR blocked.
- **Where it runs**: GitHub runners, never agentbox, because a blocking number has to come from the same toolchain as its baseline and agentbox cannot run a build next to the emulator. The APK is not built per PR: its sizes come from the review build (already paid when a PR gets `distribute`) and each `dev` push, so a PR without the label shows the APK row as not measured.
- Lighthouse runs only where a public page renders without secrets (kino answers 500 without its Clerk key; the dashboard and admin are behind their login). The per-repo measure scripts are listed in `history.md`.
