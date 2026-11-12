# Requirement ledger

Read when a delivery has several requirements or a handoff is written or received. States are in `references/verification.md`, channels in `app-testing`; this file owns the row format, the validator and the handoff template.

## Rows

Before implementing, break what was asked into observable, atomic criteria. Keep later corrections and pending items from earlier builds. A value that is computed with no consumer does not implement a requirement.

For product work, the shared source is the current description or comment of the ticket in Zoho, through the `scrum` skill. For agent environment work, Git history and the agents PR own the scope, per scrum. Set `work_kind: agent-environment` only for that case, with an agents GitHub issue, PR or task branch as `ticket`. A local JSON validates or transports the same scope and is never a second source. Publish product ledger updates in Zoho when a state changes; keep reports out of the repo.

Each row carries `requirement`, `decision`, `ticket` (scope URL), `channel`, `sha`, `state` and `evidence` (a list). For configuration without Git, `channel: nonvisual` allows `identity_type: sha256` with the SHA256 of a snapshot or manifest of the files; keep the command and the manifest, and do not invent a commit. Tooling with no binary goes from Verified to Accepted; distribution is not required.

What each state requires of a row:

- Implemented: `sha` present and a `code` evidence with the real path connected.
- Verified: an evidence of the row's `channel`, with the `sha` that produced it.
- Distributed: a `receipt` evidence whose SHA matches the row's. Pending evidence of other rows stays pending.
- Accepted: an `acceptance` evidence with the owner's literal message, never inferred from tests or an upload.

An evidence has `kind` (`code`, `command`, `capture`, `receipt`, `acceptance`), `sha` and `reference` (a command with its literal result, or a link). Captures add `channel`, `receipt` (`sha`, `versionName`, `versionCode` of the observed build) and `inspected: true` only after looking at them. A receipt evidence carries the full JSON from `release_evidence.py` (`releaseUrl`, `runUrl` or `receiptPath`, SHA and versions). The approval adds the literal `message`. Percentages come from the rows.

## Consumer verification

Create new ledgers with `schema_version: 2`. Each Implemented or later row
carries `implementation: {"producer":"...","consumer":"...","effect":"..."}`.
Each Verified or later row also carries `verification: {"action":"...",
"expected":"...","observed":"...","reference":"..."}`. Its reference must
match evidence for that row at its SHA and channel. A finished worker, a
private import, an early camera arrival or an upload proves only that action;
record the requested consumer effect separately.

For figures, retain sources for the actual value and period. For a performance
comparison, retain build, host, URL, locale, cache policy and the readiness
condition being compared. Unknowns remain pending, never invented facts.
Version 1 ledgers stay readable without the new structural guarantees.

## Validator

Root format for new work: `{"schema_version": 2, "work_kind": "product", "inventory": ["original requirement", ...], "requirements": [...]}`. The inventory keeps the full agreed list, so the validator detects rows omitted or added against it; it cannot discover a requirement nobody put in the inventory. Include the original notes in `decision`.

```bash
python3 ~/.claude/skills/development-workflow/scripts/validate.py ledger.json
python3 ~/.claude/skills/development-workflow/scripts/validate.py ledger.json --render handoff
```

`--render pr` prints the What was asked list and the Proof table in the format `agents proof` reads (a row not yet Verified prints as Pending, which keeps the PR red; a capture's `seen` string becomes the Seen cell). `--render toml` prints the rows of `.proof/<branch>.toml` for a repo whose CI proves them (`references/proof.md`, Proof in CI), with `run` empty so the spec stays red until each command is written in. `--render handoff` keeps every row and separates evidence from pending items. The validator checks structure and correspondence, not that a capture was looked at, a command ran or a consumer worked.

## Handoff template

One block a fresh session receives as its first message (the launch is the agent's, through model-delegation), in his language, in this order:

1. **Read first:** the documents, PRs, Zoho phase and decision pages the receiver opens before anything, as links or absolute paths.
2. **What I asked, in my words:** his request quoted, not paraphrased.
3. **Already decided:** each decision with its answer code or quote and where it lives; the receiver does not reopen them.
4. **Verified:** requirement, SHA, exact command and its literal output, links to PR, run, receipt and Zoho. Percentage derived from the ledger, pending items listed.
5. **Not verified:** hypotheses, pending items per channel, blockers and next commands.
6. **Hard conditions:** the non-negotiables (channels of proof, devices, models, no paid credits, what runs headless).
7. **Untouched:** files, branches, services and sessions the receiver leaves alone, and claims another machine holds.
8. **Authority:** whether the receiver may merge, distribute or deploy, with the message of mine that allows it.
9. **How it closes:** the gate that ends the work and what the receiver reports.

Receiving one is in `references/continuity.md`.
