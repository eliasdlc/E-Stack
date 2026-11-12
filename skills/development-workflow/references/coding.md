# Coding preferences and estimates

Read this before writing code, and before estimating or ordering work. The lifecycle is in `SKILL.md`; this file owns how code is written and how work is estimated.

## General
- Keep things simple. Don't build a capability now because we might need it later. It applies to presumptive features, not to things that are expensive to change later (schemas, auth boundaries, public API shapes, anything needing a migration). There, think ahead.
- Tests are good! Endless smoke tests, "regression tests" for feature deletions, etc, much less good. Tests should be focused, not slop.
- Comments are a great way to clarify functionality and how code is used. Don't comment every line, for every decision we make, but feel free to describe (concisely) how functions are used above function definitions, classes, etc. Don't add any reference to a decision we talked about or a ticket identifier, comments should only clarify functionality.
- Keep comments up to date! When making changes, it's important to keep things in sync.
- The lockfile is the source of truth for which package manager a repo uses. Never introduce npm or yarn into a repo using something else. Fresh project with no lockfile: pnpm.
- Ask for the real asset from day one; placeholder data is flagged, never presented as real.
- **Surgical changes: every changed line traces to the request.** Do not "improve" neighbouring code, copy, layout, tables, logos or formatting, and do not add what was not asked (a feature, a setting, a second screen). Remove only what your own change orphaned (imports, variables, files). Something else worth doing, or dead code that was already there: one line in the report, not an edit. Before committing, read the diff once asking of each hunk "which words of the request is this?". A hunk with no answer comes out.

## Visible changes
`design-grammar` owns the grammar, the `DESIGN.md` contract and the mocks. Two things it does not say:
- A non-trivial UI, layout or copy change stops at static mocks, each with a reason to be picked, presented with the `visual-briefing` skill, and waits for my pick before a real component is touched: the explicit exception to working autonomously. An audit or decision request authorizes preparing that comparison; external publication still needs my authorization.
- After constraining a layout to fix an overlap, verify the content still fits.

## Estimates
- Estimate in passes, gates and measured external waits, with the expected duration, where to watch and the result link afterward; never in developer-days, sprint capacity, story points or velocity, because I do not type the code: what industry math calls a two-week feature is usually one session.
- What actually costs time, and the only things worth flagging: blocking dependencies, product decisions only I can make, work needing my hands or accounts (device, store consoles, credentials, real data), external waits (CI, store review, API access), overlapping file surfaces, a PR that needs my eye.
- When something is slow, name it with its number: a test suite of twelve minutes, an agentbox Flutter job at roughly 5x, a store review in days. Never pad for typing.
- Asked to plan: order by blockers and shared surfaces, then by what gives me value first. Never cut scope or invent a "phase 2" to fit a calendar; trimming is my call.
