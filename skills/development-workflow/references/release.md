# Releases and distribution

Read this before opening or merging a release PR (`dev` into `main`), and before any build or distribution. The merge criteria in `SKILL.md` still decide the merge; this file owns what a release settles and what makes a build Distributed.

## The release
- A release (`dev` into `main`, and every distribution to users) is where my phone check and the `Pending: batch` rows its task PRs left, listed in its `## Release checklist`, are settled. A release PR follows the same criteria and carries a needs-my-eye change only if one of its task PRs did, and then it waits for me. After merging it, verify production the way the repo defines it and report the result; in `~/dev/agents` that is `agents update --all`, which activates the new main on both machines at once and prints each one's result.
- A `dev` into `main` PR that meets the criteria and carries nothing from the needs-my-eye list merges like a task PR, in the turn it is green, without asking for an explicit order. The merge is not the deploy: only a production deploy, a tag or a store distribution needs my words or the standing authorization below. Where the hosting deploys `main` by itself, say so before merging, because that merge is then also the deploy.
- The standing authorization of `rules/CLAUDE.md` covers a green release with nothing from the needs-my-eye list: Kino `dev` into `main` plus its production deploy, and a ConoceRD review build to my tester group. ConoceRD to users outside the group needs my words.
- What the release checklist must carry, row by row, is in `references/proof.md` (Release checklist).
- Before aligning an existing `dev` with `main`, inventory both sides and preserve unique work. A release PR contains only merged task work; unrelated pending work does not ride along inside a workflow correction.

## Distribution
- Vercel (deploy, logs, env, domains, inspect) is managed by agents with `npx vercel`, already signed in on the laptop, never with the claude.ai Vercel connector, which is denied everywhere because it cost about 15K tokens per session. Elias does not have to do it by hand.
- The build number is never edited by hand. CI owns it (run number or commit count) and passes it into the build.
- Two build classes. Review builds: CI builds the task branch and sends it to my tester group, which the standing authorization covers for ConoceRD. Release builds: a train from `dev`, several tickets per distribution, preferred over one per ticket.
- No CI distribution workflow yet: manual, from `dev`, from the laptop only. Merge to `dev` on the criteria; a distribution to users outside the tester group waits for my words, and I test my release checklist on that build.
- Release notes exist so I can test: what changed, the steps that exercise it in the order I would do them, what was not verified.
- **The receipt, and this is the only list of it.** A build is Distributed when every one of these exists: SHA, run id and URL, versionName, versionCode, package name, the exact App Distribution release (never the generic console: if the link could not be read from the log, say so), group, time in UTC and local, and the message or standing line that authorized it. A field missing is a build not distributed. Installed needs `dumpsys package` on the phone. A bridge failure gets bounded diagnostics before asking me to reconnect.
- A second build for a new defect is allowed without waiting for the previous gate. The pending rows of the previous gate carry over in the ledger; they never disappear.
- Device before build, when the gate is physical: without a phone, build anyway and say "gate parked" with what is missing. The order of commands is in `app-testing`.
- A successful upload is not a merge. Work distributed from a task branch stays pending until it is merged or its PR is closed with the disposition of its commits written down.
- Project mechanics (scripts, version scheme, tester lists) live in that repo's `AGENTS.md` and win over this file.
