# The AGENTS.md template

Read when creating or migrating a repo contract. Every line is something the code does not show.

`CLAUDE.md` in the repo is one line: `@AGENTS.md`. There is one truth, and Claude Code and the other agents both load it.

**Size guidance.** A line earns its place only if an agent could not learn it by reading the code or running a command: intent, a trap, a command that is not obvious, a decision with its reason. What the code shows stays out: no file trees, no per-function summaries, no list of dependencies. A section with nothing true to say stays one line, not padding. Where a rule can be a lint rule, a test or a hook, make it one and keep a single line here that names it.

## Sections, in this order

The headings below are exact: `agents check` looks for them.

| Heading | Holds | Rule |
|---|---|---|
| `## What it is` | What the product is for, who uses it, and its non-negotiables (what must never break, never ship, never be built) | Five to ten lines. A non-negotiable carries its reason |
| `## Owner's note` | Elias's own words on taste and scope: what he wants this repo to be and not to be | His words, not yours. If none exists, leave the heading with `To fill in by Elias.` and invent nothing |
| `## Glossary` | `term: one-line definition` for the repo's own words, each with an `_Avoid_:` line of synonyms not to use | `references/facts.md` owns the format and why |
| `## Facts` | `key: value`: production URL and branch, preview, deploy, distribution, figma, devices | `references/facts.md` owns the keys |
| `## Ways to hurt yourself` | The numbered traps specific to this repo: the migration that runs on production, the secret file, the test that passes while the app is broken | Each trap says what goes wrong and what to do instead. Fewer than ten |
| `## Surfaces` | The checklist of every place one change must land (client, server, rules, seeds, docs, types, both platforms) | A change touching one surface asks which others it needs |
| `## Run and verify` | Exact commands: dev servers, seeded test accounts, the checks that must pass before a PR, what only a device or a human can show | Copy-paste commands. `skills/app-testing` owns the method, this section owns the repo's facts |
| `## Pull requests` | What differs from `skills/development-workflow`: the base branch if unusual, required checks, CI quirks, release notes format | Repo-specific only. Do not restate the workflow |
| `## Map` | `area: path, and the command that tests it`, at most 25 lines | `references/facts.md` owns how it is written and kept true |
| `## Taste` | Code and product style the linter cannot see: naming, where logic lives, what a good change looks like here | Examples beat adjectives. Point at a file that is right |

A repo may add sections after these (evals, a plan index). It may not reorder or rename them.

## Migrating a repo

An existing AGENTS.md or CLAUDE.md is reshaped, not rewritten: every line that is true and not visible in the code moves under the heading it belongs to, and a line that fails the size guidance is dropped and named in the PR body. Content that fits nowhere goes under the closest section, not into a new one. Nothing is invented: a section with no source stays a single line, and the owner's note stays for Elias. A repo with a CLAUDE.md that is not `@AGENTS.md` gets its content merged into AGENTS.md first.

## Run and verify seeds, as known on 1 Sep 2026

Moved here from the former "Per project" section of `skills/app-testing`, which now sends each repo to its own `## Run and verify`. A line moves into the repo's `## Run and verify` when that repo migrates (verify before relying on it), and this list then loses it. Kino and ConoceRD migrated and left on 6 Nov 2026.

- **salud_dental_clinic_management**: local stack `supabase start`, reset with
  `supabase db reset`; seeds in `supabase/tests/` include certified users per
  role (`hfx_clin_006_seed_certificacion.sql`) and a login overlay; harness in
  `tool/e2e/jornada_ui.sh` and `integration_test/`. `dart_define.json` points
  to production: pass `--dart-define` for the local stack instead.
- **ConoceRD admin**: `pnpm emuladores` (needs `JAVA_HOME` from mise temurin-21)
  plus `pnpm dev`; `pnpm verificar` and `pnpm probar:*` against emulators.
- **conocerd-web**: `pnpm build && pnpm start`; `?medir=1` exposes the in-page
  probe on the measurement branch.
- **mikampus**: needs a real PUCMM session; scraping runs only with Elias's
  explicit go and against his own account, and stays out of automated tests.
