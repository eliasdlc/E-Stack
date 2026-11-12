# What each machine is and does

Read this when choosing where work runs, handing work between machines, or checking what agentbox or a cloud session can do. The short identity of each machine is in `machines/<hostname>.md`, which loads on every turn and stays under 2 KB (`agents check` enforces it); everything longer lives here. What each machine can capture is in `app-testing`, `references/machines.md`.

Why the ssh timeout: on 23 Aug 2026 a hung ssh took 58 stop clicks and a second thread in T3 Code. Why CLI first: Elias, 27 Aug 2026, "I would rather handle everything through the CLI than through the console". Why the power warning: the laptop died three times in August 2026.

## The laptop (decruces-omarchy)

- Authenticated here: `gh` (eliasdlc), `firebase`, `gcloud` and `supabase` (<personal Google account>), `tailscale`, `flutter`, `adb`, `playwright`, `chromium`, `psql`, and Vercel through `npx vercel`. `doctl` and `xvfb-run` are not installed.
- Agentbox has no signing keys, device or display, so anything that needs them stays on the laptop. Where a thread runs and how it is launched is in `SKILL.md`.
- Before working in a shared repo, check whether agentbox claimed it: `git fetch`, `git ls-remote --heads origin` and the Zoho task status. Run `ab estado` with a short timeout only when those are ambiguous; no answer means it is not working.
- The laptop also holds the fallbacks for the class run (`class`, `references/automation.md`) and is the CI of the agents repo (`rules-and-skills`, `references/ci.md`).

## Agentbox

Ubuntu 26.04 LTS with XFCE, i5-6500 (4 cores), 7.1 GB RAM usable, mechanical disk, KVM, reached over Tailscale.

- One heavy job per resource (the emulator, a build or the full suite), run through `agents heavy`, which refuses a second one of the same kind and caps memory, plus capped light jobs. The 4 GB emulator and a Gradle build start together only when free memory after the 1 GiB reserve covers both caps. Flutter tasks take roughly 5x the laptop's time: say so up front when that makes a task a bad fit.
- Agents run in its T3 Code server, which survives disconnections and comes back after a reboot as a user service. A session on the laptop starts one here with `agents t3-launch --host agentbox`, never inside tmux.
- Its work: audits, research, scraping (use its own Playwright Chromium; the snap Firefox is for humans), Firestore seeding and security rules, long test runs, isolated refactors, dependency and migration work, and the web projects (conocerd-web, conocerd-dashboard, kino) where you can verify end to end without him.
- Hand the laptop anything that ends in a distributable, anything that needs the device or his judgment every few minutes, and anything on the critical path of a release. Agentbox never distributes, never creates a release commit or tag, and never bumps a version in a manifest.
- Finish by pushing the branch and opening the PR with every Proof row you can produce. A `native`, `device-simulated` or `real-trip` row that needs video, the phone, a login or the native map says `Pending: batch` and does not hold the merge into `dev`, so a green task PR merges on the merge criteria of `development-workflow`. The laptop's batch session and Elias's phone check happen at the release (`dev` into `main`), which waits for him. Hand off only through GitHub and Zoho Projects (the pushed branch, the PR body, the ticket comment), never through a file on the disk.
- The timers that run here: the class run (`class`, `references/automation.md`), the CI fallback (`rules-and-skills`, `references/ci.md`) and the daily PR triage below.

### The daily PR triage

The T3 scheduled task "Daily PR triage" runs every morning at 08:17 as a Haiku thread in the "PR triage" project: it reads every open PR and publishes a Postplan round of at most eight actions (merge, takeover, modernize, close, needs you). It reads GitHub and never writes to it, held there by the deny list in `~/.t3/pr-triage/.claude/settings.json`; the procedure is the "Daily triage" section of the `modernize` skill. Set it up once with `agents pr-triage --setup`, which prints the T3 steps.

### What it has, verified 5 Sep 2026

- Authenticated CLIs: `gh` (eliasdlc), `firebase` (<personal Google account>). `gcloud` and `supabase` are not installed; anything needing them goes to the laptop.
- Flutter 3.44.1 and Dart 3.12.1, and the Android SDK 36.0.0 with `adb` in `~/Android/Sdk/platform-tools`. It can compile and analyze Android, so a `flutter build apk --debug` is a legitimate compile check. No signing key: no release build, no distribution.
- Gradle is capped (verified 27 Sep 2026): `~/.gradle/gradle.properties` sets `-Xmx2560m`, overriding the `-Xmx8G` of ConoceRD's `android/gradle.properties`, which froze this machine for nine hours and corrupted the Gradle cache. Every build runs as `agents heavy --mem 5G -- <build>`.
- Also present: `node`, `pnpm`, `npx`, `psql`, `python3`, `tree-sitter`. Postplan uploads work (`python3 ~/.claude/skills/visual-briefing/postplan/build.py`, which shells out to `npx -y postplan`).
- Zoho MCP was installed and its dedicated configuration transferred over SSH on 13 Sep 2026. It uses `~/.config/secrets/zoho.env` with mode 600. Other credentials and signing keys remain on the laptop unless explicitly provisioned here.
- The emulator, `flutter doctor` gaps, T3's browser and device tools, Playwright and `xvfb-run`: `app-testing`, `references/machines.md`.

### Its configuration

The approved main branch of the agents repository is the shared source. Each enrolled host pulls, validates and activates its own generation. The laptop is not a configuration server. Edit a task worktree, push its PR and wait for the review gate; never edit the installed generation. Omarchy system skills remain host-owned on the laptop. Provider packages, credentials and private settings remain local unless explicitly provisioned.

## Cloud

A Claude Code cloud session (claude.ai/code or a scheduled routine): a fresh Linux VM that clones one repository, runs until the task ends and is then discarded.

- It has what the environment setup script installed: `git`, `gh` through the session's GitHub access, `node`, `python3`, and whatever the repository's own setup adds. It has no signing keys, no device or emulator, no display, no Tailscale, no `~/.config/secrets`, and no provider logins (`firebase`, `gcloud`, `supabase`, Vercel) unless the environment variables of the cloud environment provide them.
- Its work: code changes with tests, audits, research, refactors, dependency and migration work, and the web projects where a headless Playwright run can verify the change. It finishes like agentbox: push, PR with every Proof row it can produce, `Pending: batch` for the rest.
- It never distributes, deploys, creates a release commit or tag, bumps a version in a manifest, or touches production data: those belong to the laptop. It cannot reach the laptop or agentbox; hand off only through GitHub and Zoho.
- The environment setup script (canonical copy: `bin/cloud-bootstrap.sh`) installed its generation at session start from main, without an update timer; its log is `/tmp/agents-setup.log`. Edits to the configuration go through a PR in the agents repository like on any other host.
