# Delivery states and verification

Read before testing, and before calling anything done, committed or ready for review.

## Delivery states
Each requirement is a ledger row in one of five states; totals and percentages come from rows (format: `references/ledger.md`).

| State | Minimum evidence | Does not imply |
|---|---|---|
| Requested | My message or the decision, with its notes | anything was built |
| Implemented | The chain producer → consumer → effect, tied to a SHA. A value that is computed and nobody consumes is not implemented | it works at runtime |
| Verified | The scenario of the requirement, on the channel the requirement needs, with artifact and result. For something I will open myself, the closing claim ("ready", "fixed", "works") names the surface I will use (my live instance, my laptop UI, my phone, the document I will read aloud) and either shows a result read from it or says "not reached: <surface>" plus the one step I take to see it; read only where that is read-only and allowed (a deployed preview, a status page, my live instance when the project's Facts allow it), never acting on my live data or my screen | distributed or accepted. It is what a merge needs |
| Distributed | The receipt of the APK of that exact SHA, with every field listed under "The receipt" in `references/release.md` | installed on my phone: that needs `dumpsys` |
| Accepted | My green light on that delivery, when I give one. Never required to merge | measurements that were never made |

Channels of evidence are not a ladder: each proves a class of properties and no other, and none is a cheaper version of the next. A test cannot show a shadow; a trip cannot show that every branch of a formula holds. So every acceptance criterion names the channel that can show its property; what only exists in a native layer is never Verified from `test` or `render`; and a capture or run proves only the build whose receipt it carries, so one of an earlier build never proves a later fix: rerun after the final edit.

The six channels live once in the `app-testing` skill, which also produces them.

## Verification
- Nothing is done, committed or handed to review until the repo's own checks are clean. Find them: `package.json` scripts, Makefile, justfile, CI config, the repo's `CLAUDE.md`. None configured: say so.
- TypeScript / JS: typecheck, lint, tests when behavior changed. Dart / Flutter: `flutter analyze` and `flutter test`; report the warning count and whether it moved. Anything else: what the language gives for free, and say what you ran.
- No production build unless the task needs it or I ask.
- Exercise what the user touches, per role, including interactive states (sheets, overlays), headless so my screen stays mine; commands per stack are in `app-testing`.
- Anything visible gets a headless capture before "done" (`app-testing` lists the viewports); a fix I asked for is not done until the capture shows it.
- Report what you ran and what it said, with numbers. "Tests pass" is not a report.
- During a round run the targeted tests of what you touched, by path. Run the full suite before requesting review and again after the final change (one run when nothing changed after it), because each full run costs minutes plus its wait for the build lock. Run a full suite or a build as `agents heavy -- <cmd>` (`--wait` queues it; rules in `bin/heavy.sh`).
- Walk the edge cases of `app-testing` for every change a user can reach.
- Device rows (`native`, `device-simulated`, `real-trip`) leave a task PR as `Pending: batch`; the orchestrator verifies them once per batch (`app-testing`).
- Scratch work (mutation copies, downloaded captures, review notes, logs) goes under `~/.cache/<project>/<branch>/` for an implementer and `~/.cache/<project>/review-<pr>-<round>/` for a reviewer, a new directory each reviewer round, because `/tmp` is shared by every session and emptied by the system.
- End a turn only on a wake the harness keeps: `watch_pull_request` for a PR's checks, a running subagent, the completion notice of an async `delegate_task`, or a background shell or Monitor marked with `t3_background_wait` the moment it starts, because T3 kills an unmarked background shell when the turn ends, and the `turn-close` Stop hook holds the turn (up to 3 blocks per task ID) while a running job is unmarked. A wait goes to `run_in_background` plus `t3_background_wait`, or a PR watch, never to a foreground polling loop. A job under ten minutes is simplest as the foreground command itself, with its `timeout` set. While a job runs, do the independent work and say which wake you registered. A detached process (`setsid`, `nohup`, `systemd-run`) and `ScheduleWakeup` outside `/loop` never wake you.
- The state of a CI run or a build comes from a command in the same turn (the repo's build-state script where it has one, `app/scripts/estado-build.sh` in ConoceRD, else `gh run view --json createdAt,status,conclusion,jobs` next to `date -u`), never from memory and never from `updatedAt` alone. Durations are computed from parsed timestamps with their zone; UTC and local are both printed. A run is never "hung": it is "above the reference" with its steps listed.
- A confirmed defect stays open until a test or a capture refutes it after the change. Re-read that list before auditing anything else. A conclusion inherited from a previous session ("the shadow is already gone") is re-verified at the one line that matters before it is repeated.
- A test written for a fix has been seen failing without it: run it on the old code (or with the fix reverted), then restore the fix and run it green. A test that never failed pins nothing. A test that asserts on a mock proves the mock, so what only exists in a native layer is not covered by it.
- A subagent's "done" is a claim, not a result: read its diff and rerun its command before repeating it as yours.

**Excuses that end in an untested "done".** Each preceded a claim Elias later found false:

- The emulator is not the phone: say which device ran it, and for a physical gate wait for the receipt of that build on the phone.
- Size decides how much you run, never whether: a color, a copy line or a logo is visible, so it gets its capture.
- Analysis, build and behavior are three claims: state which ran.
- "Should", "probably" and "seems to" in a status line mean a command was not run: run it this turn and quote the number.
