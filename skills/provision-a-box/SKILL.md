---
name: provision-a-box
description: Enroll a new machine (laptop, server, VM, cloud environment) into the agents configuration, verify it pulls and activates main, and record what the run taught. Elias opens it with /provision-a-box.
disable-model-invocation: true
---

# Provision a box

Hosts pull; nothing is pushed to them. A new box needs three things, in this
order: its machine file approved on `main`, enrollment, and proof that the update
loop runs. Every run ends by appending to
"Fixes learned", so the next run starts from what this one found.

Everything below comes from `README.md`, `bin/configuration.py`,
`bin/cloud-bootstrap.sh`, `dependencies.json` and `systemd/`. When a step here
disagrees with the code, the code wins: fix the step in the same PR.

## What only Elias does

Write each of these as a handoff naming the exact command and the host it runs
on, and never attempt it. A credential stays on the host that holds it, because
a machine file or a copied token turns one host's breach into all of them.

| Handoff | Why it is his |
|---|---|
| `gh auth login`, `firebase login`, `gcloud`, `supabase` and any provider login | Provider accounts are host-owned and need his browser |
| `~/.config/secrets/zoho.env` with `ZOHO_MCP_URL` (mode 600), then `zoho-projects-mcp` and the OAuth once | The URL and the session never enter Git or move between hosts unless he provisions them |
| `mikampus teams-login` on the laptop, then `scp -p` of the session file to the host that runs the class pipeline | The MFA needs a screen |
| Signing keys, device, release builds, distribution | Laptop only. Agentbox and cloud never distribute, tag or bump a version |
| `loginctl enable-linger "$USER"` on an always-on host, if preflight shows `Linger=no` | The repo does not set it and it changes the host's session policy |

## 1. Preflight: facts to gather on the new host

Run these in the host's own login shell. A non-interactive `ssh host cmd` has a
shorter `PATH` and reports installed tools as missing (see Fixes learned).
Every fact becomes a line in the machine file, so record the command's output,
not what you expect.

| Fact | Command | Why |
|---|---|---|
| Hostname | `hostname` | It names `machines/<hostname>.md`; the installer refuses a host with no file |
| Python 3.12 or newer | `python3 --version` | `dependencies.json` minimum, for safe tar extraction |
| Git and its access to the private repo | `git --version`, `gh auth status` | The host clones and fetches with its own credentials |
| User systemd | `systemctl --user show-environment >/dev/null && echo ok` | The update timer is a user unit |
| Linger | `loginctl show-user "$USER" -p Linger` | Without it, user timers can stop when nobody is logged in |
| Node and npm | `command -v node npm` | `mcp-remote@0.14.2` installs through npm |
| OS, CPU, memory, disk | `. /etc/os-release; echo "$PRETTY_NAME"`, `lscpu \| grep 'Model name'`, `free -h`, `lsblk -d -e7 -o NAME,ROTA,SIZE` | Specs for the machine file |
| Capabilities | `command -v gh firebase gcloud supabase flutter adb playwright xvfb-run psql tailscale` plus each tool's own auth status | "Authenticated" is seen, not assumed |
| Reach | The Tailscale name, or how a session starts (cloud) | The `reach` lines of the inventory |
| Reliability | Sleeps? Loses power? Runs unattended? | Decides what work belongs here |

## 2. Write the machine identity (in a task worktree, never the installed generation)

1. Branch from current `dev` in the editing checkout (`~/dev/agents` by default).
2. `./bin/agents prepare-host` creates `machines/<hostname>.md` from
   `machines/template.md`, and refuses to overwrite an existing file.
3. Replace every `{{TODO...}}`, in the prose and in the `<!-- inventory` block.
   The prose is written for the agent (what the host is, what belongs here, what
   moves elsewhere); the block is facts for the page. Model it on
   `machines/agentbox.md` (unattended worker), `machines/decruces-omarchy.md`
   (keys and device) or `machines/cloud.md` (disposable). The block never holds
   a credential or its location: state that one exists.
4. `agents check` and `python3 -m unittest discover -s tests -v`. Expected: the
   check ends `everything coherent` and the tests end `OK`. A host without
   Elias's Documents folders reports check 5 red for unrelated skills;
   `python3 bin/check.py --repository-only` (what CI runs) must be green.
5. Commit, push, open the PR into `dev` (task PRs never target `main`), merge it
   on the development-workflow criteria, then release `dev` into `main` the same
   way. Enrollment reads only approved `main`, so a machine file still on `dev`
   fails with `enrollment requires machines/<hostname>.md`.

## 3. Enroll

Cloud sessions are different: paste `bin/cloud-bootstrap.sh` as the
environment's setup script, with a fine-grained `GH_TOKEN` (Contents read on
this repository only) that Elias provides, and read `/tmp/agents-setup.log`.
There is no timer there. Everything else:

```sh
git -C ~/dev/agents switch main && git -C ~/dev/agents pull --ff-only
~/dev/agents/bin/agents install
agents tools-update
```

`install` writes `~/.config/agents/config.json`, fetches `main`, runs the
candidate's `check.py --repository-only` (CI ran the suite before main could
change), activates the generation, then copies `agents-update.service` and
`agents-update.timer` into `~/.config/systemd/user/` and enables the timer
(every minute).
`--no-timer` is for sandbox verification only, not an enrollment. The installer
links `agents` into `~/.local/bin`, so that directory must be on `PATH`.

Optional, only when the machine file says the host runs it: the class units.
Clone the private `eliasdlc/class-pipeline` into `~/dev/class-pipeline/`, copy
the `class-*` and `teams-session-*` units from its `systemd/` into
`~/.config/systemd/user/`, `systemctl --user daemon-reload`, and enable the
timers. The Teams session is the handoff above. A Flutter host with 8 GB of
RAM or less caps the Gradle heap and runs builds through `agents heavy`; the
reason and numbers are in `machines/agentbox.md`.

## 4. Verify

| Command | Expected |
|---|---|
| `agents status` | `"enrolled": true`; `active.host` is the hostname; `active.sha` equals `git ls-remote origin refs/heads/main`; `last_update.status` is `activated` or `current`, never `failed`; every `external_dependencies` entry is `matched` |
| `systemctl --user is-active agents-update.timer` | `active` |
| `systemctl --user list-timers agents-update.timer --no-pager` | A time in the NEXT column within a minute. A `-` there means the timer is not firing |
| `readlink ~/.claude/machine.md` | `.../.local/share/agents/current/source/machines/<hostname>.md` |
| `agents update` | `Current configuration: <sha> (<hostname>)` |

A row that does not match is a failure to report with its output, not to
explain away. Skills and hooks arrive with the generation: confirm with
`agents status` that the `skills` list includes this one.

## 5. Close the run

1. Append every defect this run hit to "Fixes learned". When the fix belongs to
   a step above, edit that step in the same PR and say so in the last column.
2. Report the handoffs still open, each with its command and host.

## Fixes learned

One row per defect, newest last. Say what was observed; mark a cause you did not
establish as unknown.

| Date | Host | Symptom | Fix or rule | Folded into |
|---|---|---|---|---|
| 2026-10-14 | decruces-omarchy, over `ssh` | `command -v adb playwright gcloud` printed nothing for tools its machine file lists | Preflight in the host's own login shell, not a bare `ssh host cmd`: non-interactive `PATH` skips mise shims and user paths | Step 1 |
| 2026-10-14 | agentbox | `agents-update.timer` was `active (elapsed)` with `Trigger: n/a` and LAST 2026-10-06, so nothing pulled automatically; `last-update.json` read `failed`, `BUDGET_RUNTIME: no free slot`. Cause unknown | Check the NEXT column, not only `is-active`. The unit belongs to the installer, so report it to Elias instead of editing it | Step 4 |
