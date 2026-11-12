# Facts and Glossary

Read this when writing or correcting a repo or project contract, and before a deploy reads its target.

Every product repo's contract (AGENTS.md, or CLAUDE.md when the repo has none)
and every Documents project's contract carries three sections the agent reads
before acting (writing a correction into them is a global rule):

| Section | Lines | Why |
|---|---|---|
| `## Facts` | `key: value`: `production` (URL), `production branch` (main), `preview`, `deploy`, `distribution` (lanes, package ids), `figma` (file URL and what it holds), `devices` (name and adb serial), `course folder` | A wrong production URL, a production branch set to dev and the wrong phone all came from facts that lived only in chat |
| `## Glossary` | `term: one-line definition` for the repo's own words, names and concepts | The dictation map: an unrecognized word resolves to the closest term here. An `_Avoid_:` line under a term lists the synonyms not to use, so one concept keeps one name; no implementation detail |
| `## Map` | `area: path, and the command that tests it`, one line per area, at most 25 lines | Searching and reading took a quarter of agent time in Oct 2026; a line here is one search no later session repeats |

A Glossary entry, with its `_Avoid_` line:

```
- review build: an APK built from a task branch for Elias's phone.
  _Avoid_: beta, preview, release
```

The SessionStart hook prints at most 40 Glossary lines, so add an `_Avoid_`
line only where a synonym has actually been used for the wrong thing.

The Map is written by the session that paid for the search: when finding where
something lives took more than a few searches, or a path in the Map turned out
wrong, that session adds or fixes the line in the same commit as its work. It
holds where things are and how they are tested, never how they work, so it
stays true while the code changes.

These three sections sit inside the repo contract template, whose sections and
order are in `references/agents-md.md`.

The SessionStart hook prints both from an AGENTS.md that Claude would not load on its own. A production deploy reads its target from `production:`, and the `delivery` hook refuses one in a repo whose Facts do not name it.
