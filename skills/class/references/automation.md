# The automatic runs around the class digests

Read this when a run touches Kino, the PVA or `Entregas PVA`. The class watcher
itself is in `SKILL.md` ("The timer that runs it alone").

## Who writes to Kino

Interactive sessions use the claude.ai Kino connector
(`mcp__claude_ai_Kino__*`). Automatic runs mount Kino directly (`mcp__kino__*`)
with the OAuth token Claude Code keeps on each machine. Only the machine that
holds that token writes to Kino, today the laptop: agentbox reads the class and
leaves its digest for the laptop to send, and its nightly check only logs. When
Kino fails, say so with the error instead of reasoning from the file tree.

A Kino write waits for his go ahead when he asked for the work. A run he did
not start does not wait, because the literal quote `class_session.py save`
demands of every item guards it.

Course folders created by this skill have `agentEditPolicy: direct`; older hand
written pages are `confirmation_required` and need his word before an edit.

## The 07:10 review run (laptop `class-review` timer)

In this order:

1. Merge each task the PVA sweep (`aula-a-kino`, hourly on agentbox) created
   with the class task for the same deliverable, keeping the PVA one with the
   class's context and linking it to the class note.
2. Close the University tasks the PVA records as submitted, only when the task
   is that very PVA activity and never because it merely cites its cmid. This
   lands before Kino's 08:00 digest.
3. Draft the forums due in the next seven days or asked by an open task.
4. Open the way on assignments due in two to twenty-one days: a plan page in
   Kino and a `.docx` skeleton at the course root.
5. Refresh each course's `Memoria:` page, its `Material:` page (the PVA course
   page organized by section, read only) and its study sessions.

The later steps can finish after 08:00.

## What the runs cannot touch

Claude Code denies every run its file-writing tools (Edit, Write) inside
`Entregas PVA` and refuses a LibreOffice command that names that folder,
because that folder is the record of what was submitted. The stale and forum
runs get no file-writing tool and no Bash, only Read, Glob and Grep. The class
run and the kickoff keep `python3`, which no deny rule can bound: there the
prompt is the guard, and the versions hook keeps a copy of whatever document
changes.

## Digest location and sync

Digests live in `~/Documents/Universidad/Aprendizaje/classes/`, not in
`~/Documents/Aprendizaje`. Corrections to an already saved class land in `classes/updates/`. Every pass, and a laptop timer every 30 minutes,
mirrors that folder both ways without deleting, so neither machine processes a
class the other already did.

## The timers and which machine runs them

The automatic class run belongs to agentbox because it stays on: `class-watch.timer` (Teams sweep plus digest), `class-watch-nightly.timer` (classes that left no trace) and `teams-session-check.timer` (daily, with `teams-session-alert.service` leaving a Kino task when the session dies). Install them by copying the units from `~/dev/class-pipeline/systemd/` (the private repo `eliasdlc/class-pipeline`, which also holds `class_watch.py` and `class_session.py`) into `~/.config/systemd/user/` and enabling the timers.

The laptop is the fallback: `class-watch-fallback.timer` runs the same `class-watch.service` twenty minutes after each agentbox pass and only does the work when agentbox is unreachable or failed. `class-digests-sync.timer` mirrors `Aprendizaje/classes/` with agentbox between passes.

The Teams session is `~/.local/share/mikampus/teams-state.json`. It is created and renewed on the laptop with `mikampus teams-login`, because its MFA needs a screen, whenever agentbox's Kino task asks for it. Copy the renewed file to agentbox with `scp -p` and keep the laptop's copy, since the fallback uses it. mikampus runs from `~/mikampus-better-solution` on its `dev` branch with the Node 26 under mise.
