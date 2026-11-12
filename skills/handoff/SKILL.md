---
name: handoff
description: Writes the handoff a fresh session needs, here or on agentbox. Use only when he asks for it, by /handoff or in words such as "hazme el handoff", "dame el handoff", "pasalo a otra sesion", "handoff para agentbox". Also owns the safe pause when a session must stop with work unfinished and nobody continues it now (the laptop shutting down): wip commit, push, resume note. Not when he pastes a handoff to execute (development-workflow runs that as the brief), not for an end-of-phase summary, and not for moving work to another machine yourself, which model-delegation launches.
---

# Handoff

Elias asks for this, with `/handoff` or in words, when work continues in another session, on
agentbox, or with a clean context. Call the Skill tool with
"development-workflow": its `references/ledger.md` owns the handoff template
(read first, his words, already decided, verified, not verified, hard
conditions, untouched, authority, how it closes). This skill only produces it.
Also read its `references/continuity.md`: the ledger and live run ids travel
with the handoff, and a render inspected is not a device verified.

1. Re-run the commands that prove the state now (`git status`, `git log -1`,
   the PR and run state, the ledger) and use their literal output; a fact
   from earlier in the chat is not verified until re-run.
2. Fill every field of the template from this session. His request is quoted
   from his messages, decisions carry their code or quote, links are absolute.
3. Name the receiving machine. For agentbox, push the branch first and say so
   in Read first; a document that lives only on the laptop travels as a path
   the receiver can reach or is not referenced.
4. When the handoff is for a session that continues the work now (another
   project, agentbox, the laptop he is about to close), it becomes that thread's
   first message: call the Skill tool with "model-delegation", which launches the
   thread itself, and give him its title. Otherwise hand it over as one fenced
   block in the chat, in the language he wrote in, with nothing after it but the
   closing paragraph.

The receiver executes it: a pasted handoff is the brief, not a document to
rewrite (development-workflow, Handoffs).

## Safe pause

When a session must stop with work unfinished (the laptop is shutting down, the
context is full), commit what exists and leave a note, because a stopped session
keeps nothing that is not in Git or on disk. The pause costs one commit and one
file; it is not a handoff, which Elias still asks for by name. When the work
continues now on agentbox, model-delegation launches that thread instead.

1. Commit the work in progress on the task branch, file by file so no other
   delivery's files ride along, as `wip: <what>`. The commit hook checks no
   subject type, so it accepts `wip:`. If its PR is ready, `gh pr ready --undo`
   first, because every push to a ready PR runs the paid gates. Then
   `git push -u origin HEAD`, so the other machine and the next session see it.
2. Write the note at the path this prints, so every reader finds the same file:

       echo ~/.cache/agents/pause/$(basename -s .git "$(git remote get-url origin)")-$(git branch --show-current | tr / -).md

   Create its folder with `mkdir -p` first, because a fresh machine has none.
   It holds done, next, the exact next command, and the ledger path and any
   live run id. Ten lines at most, because it is read before anything else.
3. A later session on that branch reads the note first and re-runs
   `git status` and `git log -3`, because the repo wins over the note when they
   disagree. It deletes the note once the work is picked up, so a stale note
   never steers a later resume.

A long thread is not a reason to pause or hand off: it compacts in place and
keeps working in the same thread, because a continuation thread leaves him
unsure which thread is the live one.

A handoff is for a clean context or the other machine. When he wants this same
conversation to go on in a new thread on this machine, fork it with
`t3_thread_fork` instead: it carries everything, with nothing to rewrite.
