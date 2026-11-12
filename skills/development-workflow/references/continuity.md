# Handoffs and resumed sessions

Read this at the end of a phase or delivery unit, when a handoff is received, after a context compaction or a resumed session, and when you must stop.

- End of a phase or delivery unit: completion percentage and exactly what is missing from the rest, delivered by the closing rule (chat or readable HTML, never local Markdown alone).
- Writing a handoff: call the Skill tool with "handoff"; the template is in `references/ledger.md`. The Verified and Not verified blocks say which of render and device ran.
- A handoff pasted as Elias's message is the brief for this session: execute it; do not rewrite it, summarize it back or hand it on.
- Receiving a handoff: re-run its commands before acting, report any mismatch first. The repo or the hosting dashboard wins over the handoff.
- Memory (MEMORY.md, rollout summaries, session digests) is an index of sources, never the state of a delivery. Delivery state is read from git, the PR, the run list and the ledger.
- After a context compaction, a "continue from where you left off", or a resumed session: re-run the commands that `hooks/after-compaction.sh` prints in that same moment, and re-read the ledger, before affirming anything. A monitor from before the compaction is dead until proven alive.
- If you must stop: finish everything that does not depend on my answer, then close as `rules/CLAUDE.md` says (the state as it is, and what needs me asked with the question tool), never "can I continue?". When the stop is the session itself (the context full, the laptop shutting down), run the handoff skill's Safe pause first.
- A product run uses the rules it started with, as `VERIFY_FROM` does for proof. A fix to the agents repo goes in its own thread and activates between runs, so product work never pauses for it.
