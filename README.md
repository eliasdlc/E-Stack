# E-Stack

Elias Agent Stack: the general prompt (`CLAUDE.md`) and the skills his agents load, published from the latest `main` of his private agents configuration.

- `CLAUDE.md`: the rules every session loads.
- `skills/<name>/SKILL.md`: one skill per folder, loaded by its description.

## Skills

| Skill | What it does |
|---|---|
| `app-testing` | Launches, drives, captures and tests an app end to end headless, without taking over the real screen. |
| `class` | Turns a class recording or transcript into study notes and Kino tasks, with dates checked against the university portals. |
| `console-guide` | Writes the step by step guide for a web console task when no CLI or API can do it. |
| `council` | Has three models from different providers answer, cross-examine each other and return one synthesis. |
| `design-grammar` | Defines the design grammar (spacing, type, color, elevation), the DESIGN.md contract and the per-project taste ledger. |
| `development-workflow` | Owns the development lifecycle: branching, testing, PRs, merge criteria, builds and handoffs. |
| `dgii-accounting` | Acts as a Dominican tax accountant: records invoices, generates the 606 and 607, and computes ITBIS, ISR and deadlines. |
| `diagrams` | Makes, lints and exports draw.io diagrams (BPMN, C4, star and ER schemas) from a template. |
| `documents` | Produces delivered documents (docx, pptx, xlsx, pdf) from a template, in the author's voice, rendered and checked before handover. |
| `figma-assets` | Sets the order of work for Figma pieces (posts, flyers, cards, templates) with editable layers and exports. |
| `find-skills` | Searches the open skills ecosystem for a skill that covers a task and brings it in through a PR. |
| `frontend-design` | Guides distinctive, intentional visual design for new or reshaped web UI. |
| `full-send` | Mode where the agent owns the task PR all the way to its merge. |
| `full-stop` | Mode where the agent leaves the PR merge-ready, green and unmerged. |
| `grill-me` | Runs a relentless interview that settles every decision of a large task before work starts. |
| `handoff` | Writes the handoff a fresh session needs, or safely pauses unfinished work. |
| `ketchup` | Catches you up on where the current work stands in five bullets or fewer. |
| `media` | Does local audio, video and PDF work: transcription, frame sampling, re-encoding, compressing and merging. |
| `model-delegation` | Decides where an agent runs (laptop, agentbox, cloud) and which model and effort it uses. |
| `modernize` | Brings a stale PR or branch up to date, or closes it when something merged already covers it, and runs the daily PR triage. |
| `notebook` | Debugs Jupyter notebooks in a fresh kernel and teaches them cell by cell. |
| `provision-a-box` | Enrolls a new machine into the agents configuration and verifies it activates main. |
| `rules-and-skills` | Explains how rules, skills, subagents and hooks are written and corrected. |
| `scrum` | Moves work into and out of Zoho Projects as scrum master: phases, tickets, grooming and execution. |
| `social-presence` | Drafts posts, threads and replies for X, LinkedIn and GitHub in the owner's voice, from what shipped and what is trending. |
| `takeover` | Takes over unfinished work and carries it to a merged PR or a written disposition, keeping credit for whoever started it. |
| `tarea` | Takes a university assignment from its rubric to a submitted, defensible deliverable. |
| `teach` | Tutors a topic step by step, probes what is already known and checks understanding with evidence. |
| `troubleshoot` | Fixes a defect from a red reproduction, through falsifiable hypotheses, to a closing check. |
| `visual-briefing` | Chooses how to present a decision or explanation and builds a visual page when a page beats the chat. |
| `week` | Plans the week by crossing university, project work and energy windows, then writes the blocks to Kino. |
| `whatsapp` | Reads the owner's WhatsApp archive (read only) to answer what was said or agreed in a chat. |
| `workspace-files` | Decides where documents, plans, audits, mocks and captures live outside a repository. |

Hooks, installer, machine files and vendored skills are not included. Personal account and network identifiers are redacted.
