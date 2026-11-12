---
name: tarea
description: Takes a university assignment from the PVA rubric to a submitted, defensible deliverable in the course folder. Use only when Elias asks to do an assignment, by /tarea or in words such as "hazme la tarea", "la asignacion de", "el informe de la materia", "lo que hay que entregar en el PVA", naming a course or an assignment. Not for a document outside a course (documents), a class transcript (class) or studying a topic (teach).
---

# Tarea

Elias asks for this, with `/tarea` or in words, and names a course or an assignment. It runs the whole
process a careful student follows, in order, so the first draft already meets
the rubric. The work helps him produce and understand his deliverable; it does
not hide the use of AI in graded work, and when a course or a professor asks
how the work was made, the answer is the true one.

Every step closes on something checkable. The university workspace contract
(`~/Documents/Universidad/CLAUDE.md`) owns the folder layout; the `class`
skill owns class digests; the `documents` skill owns how the file is built.

| # | Step | What closes it |
|---|---|---|
| 0 | Read the assignment, its **rubric or template**, the professor's instructions and any example in the PVA (mikampus MCP), plus the class digests for that topic and his previous submission in the course | The rubric criteria listed, each with its weight, and the template file saved locally |
| 1 | Confirm format, length, language, deadline (date and hour) and submission channel | One line in the chat with all five; a missing one is asked for once |
| 2 | Outline against the rubric: one section per criterion, in the order the rubric grades | The outline shown with each section mapped to its criterion |
| 3 | Gather real sources: the class material first, then primary sources, each one read | Every source cited in the format the course uses; nothing cited that was not opened |
| 4 | Draft through the documents skill (call the Skill tool with "documents"), on the template | The `.docx` in the course folder, the PDF rendered from it and looked at |
| 5 | Self-check item by item against the rubric, then the writing checklist in the documents skill | A table: criterion, where it is met, what is weak |
| 6 | Save in the course folder: drafts at the course root, the submitted file in `Entregas PVA/NN - <title>/`, which is append only | Paths in the chat; the course folder comes from the workspace's `## Facts` `course folder:` line when it exists |
| 7 | Record it in Kino (task done, link to the file) and remind him of the deadline if he submits | The Kino task updated |
| 8 | Prepare him to defend it: a short explanation of what was done and why, in his words, and for presentations the guion with `[show X]` cues | He can explain every section; a term he cannot explain is explained before he submits |

## Where the work lives

The workspace contract owns the folder layout; these rules govern the work
itself.

- The root of a course folder is a workbench for drafts and tool files.
  `Entregas PVA/NN - <title>/` is the record of a submission and is append
  only: a correction becomes a new numbered folder or a new file next to the
  old one, because the folder must match what the professor received.
  `_Revisado` or `_Revisada` marks the version that went up after a review
  pass, and that one is copied in.
- Code written for a class lives in that class's directory, never in
  `dev/projects`, because an assignment has a due date and then it is finished.
- An assignment has no branch model, no ticket, no ledger and no release. The
  coding preferences of development-workflow apply; its delivery states,
  distribution and review gate do not.
- No invented dates, weights, chapters or percentages: the professor said it,
  the PVA publishes it, or it is unknown and flagged as unknown.
- A notebook deliverable follows the notebook skill, not the informe rules.

## What went wrong before, so it does not again

| Date | What happened | Which step prevents it |
|---|---|---|
| 12 Oct 2026 | A thesis deck took 16 corrections; the first was "verifica si no hay una plantilla o rubrica de como tiene que verse la presentacion" | 0: the rubric is read before anything is built |
| 12 Oct 2026 | "Que significa MAE?" in his own deck | 8: every term defined, every slide explainable by him |
| 27 Sep 2026 | "Ese no es el directorio correcto, es en el directorio de la materia" | 6: the course folder from the contract or Facts |
| 16 and 17 Sep 2026 | "demasiado profesional", figure numbering he does not use | 4: his template and voice, through the documents skill |
| Sep 2026 | A report narrated the tooling (`tableau-prep-cli`) instead of the course tool | 4: the document describes the course's tools and method, the work he must be able to reproduce |

## Good practice the steps carry

- Start from the rubric the day the assignment appears; the deadline is
  recorded with its hour.
- Cite what was read, in the course's format; a number without a source is
  removed.
- Understand before submitting: if a part cannot be explained in two
  sentences, it is rewritten or studied (the teach skill, opened with `/teach`,
  does that).
- Proofread the rendered PDF, not the source file.
- Submit before the deadline, and keep the exact submitted file.

## Guion mode

For a presentation or an oral exam: one block per slide or section, with what
he says in short spoken sentences, `[show X]` where he points or switches,
and every acronym said in full the first time. Timed at about 130 words per
minute against the limit.
