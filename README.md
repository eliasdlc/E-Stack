# E-Stack

Elias Agent Stack: the general prompt (`CLAUDE.md`) and the skills his agents load, published from the latest `main` of his private agents configuration.

- `CLAUDE.md`: the rules every session loads.
- `skills/<name>/SKILL.md`: one skill per folder, loaded by its description.

## Core skills

The ones that carry the work, ordered by how often they loaded in the last 60 days.

| Skill | What it does | Uses |
|---|---|---|
| **`development-workflow`** | **Owns the development lifecycle: branching, testing, PRs, merge criteria, builds and handoffs.** | 377 |
| **`design-grammar`** | **Defines the design grammar (spacing, type, color, elevation), the DESIGN.md contract and the per-project taste ledger.** | 321 |
| **`class`** | **Turns a class recording or transcript into study notes and Kino tasks, with dates checked against the university portals.** | 282 |
| **`frontend-design`** | **Guides distinctive, intentional visual design for new or reshaped web UI.** | 155 |
| **`app-testing`** | **Launches, drives, captures and tests an app end to end headless, without taking over the real screen.** | 153 |
| **`model-delegation`** | **Decides where an agent runs (laptop, agentbox, cloud) and which model and effort it uses.** | 121 |
| **`rules-and-skills`** | **Explains how rules, skills, subagents and hooks are written and corrected.** | 83 |
| **`visual-briefing`** | **Chooses how to present a decision or explanation and builds a visual page when a page beats the chat.** | 73 |
| **`scrum`** | **Moves work into and out of Zoho Projects as scrum master: phases, tickets, grooming and execution.** | 70 |
| **`figma-assets`** | **Sets the order of work for Figma pieces (posts, flyers, cards, templates) with editable layers and exports.** | 39 |
| **`tarea`** | **Takes a university assignment from its rubric to a submitted, defensible deliverable.** | 37 |

## Other skills

| Skill | What it does | Uses |
|---|---|---|
| `documents` | Produces delivered documents (docx, pptx, xlsx, pdf) from a template, in the author's voice, rendered and checked before handover. | 32 |
| `workspace-files` | Decides where documents, plans, audits, mocks and captures live outside a repository. | 28 |
| `full-send` | Mode where the agent owns the task PR all the way to its merge. | 24 |
| `social-presence` | Drafts posts, threads and replies for X, LinkedIn and GitHub in the owner's voice, from what shipped and what is trending. | 19 |
| `handoff` | Writes the handoff a fresh session needs, or safely pauses unfinished work. | 17 |
| `console-guide` | Writes the step by step guide for a web console task when no CLI or API can do it. | 16 |
| `find-skills` | Searches the open skills ecosystem for a skill that covers a task and brings it in through a PR. | 13 |
| `troubleshoot` | Fixes a defect from a red reproduction, through falsifiable hypotheses, to a closing check. | 12 |
| `takeover` | Takes over unfinished work and carries it to a merged PR or a written disposition, keeping credit for whoever started it. | 10 |
| `dgii-accounting` | Acts as a Dominican tax accountant: records invoices, generates the 606 and 607, and computes ITBIS, ISR and deadlines. | 6 |
| `whatsapp` | Reads the owner's WhatsApp archive (read only) to answer what was said or agreed in a chat. | 6 |
| `modernize` | Brings a stale PR or branch up to date, or closes it when something merged already covers it, and runs the daily PR triage. | 3 |
| `notebook` | Debugs Jupyter notebooks in a fresh kernel and teaches them cell by cell. | 2 |
| `diagrams` | Makes, lints and exports draw.io diagrams (BPMN, C4, star and ER schemas) from a template. | 1 |
| `media` | Does local audio, video and PDF work: transcription, frame sampling, re-encoding, compressing and merging. | 1 |
| `teach` | Tutors a topic step by step, probes what is already known and checks understanding with evidence. | 1 |
| `council` | Has three models from different providers answer, cross-examine each other and return one synthesis. | 0 |
| `full-stop` | Mode where the agent leaves the PR merge-ready, green and unmerged. | 0 |
| `grill-me` | Runs a relentless interview that settles every decision of a large task before work starts. | 0 |
| `ketchup` | Catches you up on where the current work stands in five bullets or fewer. | 0 |
| `provision-a-box` | Enrolls a new machine into the agents configuration and verifies it activates main. | 0 |
| `week` | Plans the week by crossing university, project work and energy windows, then writes the blocks to Kino. | 0 |

Uses count model loads plus slash invocations from 13 Sep to 12 Nov 2026 (`agents usage --days 60`).

Hooks, installer, machine files and vendored skills are not included. Personal account and network identifiers are redacted.
