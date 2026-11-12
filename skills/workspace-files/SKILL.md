---
name: workspace-files
description: Decides where project documents, plans, audits, mocks, captures, receipts and other work artifacts live outside a repository: Documents paths, staging versus durable evidence, move proposals and publication boundaries. Use when creating, moving or publishing such files, or cleaning a project folder. Not for application-managed folders or credentials.
---

# Project documents and evidence

Every artifact has one home, and anything another machine or reviewer needs
has a shared record. The table decides both.

## Ownership

| Content | Home | Shared record |
|---|---|---|
| Product requirements and executable scope | Zoho | Task with full description and sources |
| Release evidence | The PR and its release receipt | Exact SHA and artifact |
| Code and durable product contracts | Product repository | PR and commit |
| Agent rules, skills, hooks and machine templates | agents repository | PR and approved main |
| Plans, audits and mocks | Documents/Proyectos/<Project>/dev | The page in the thread, or a Postplan link when it must outlive the thread |
| Source file of a visual brief | Documents/Proyectos/<Project>/dev/plans, outside every repo | Private by default; the thread attachment is a copy |
| Permanent references | Documents/Proyectos/<Project>/dev/references | Link from the record that uses it |
| Captures and receipts | Documents/Proyectos/<Project>/dev/evidence | Immutable external URL or private attachment |
| Private source assets | Project folder with verified private backup | Private by default |

Use `YYYY-MM-DD-topic.ext`. Canonical dev folders are `plans`, `audits`,
`mocks`, `references`, `evidence`. Personal agent-environment artifacts use
Personal/dev. Repo Markdown is limited by that repo's own contract; reports
and scratch projects live in Documents, outside the source tree.

## Existing folders

Propose the moves first, each with source, destination, SHA256 and collision
flag, and move nothing until the proposal is reviewed. Review links before
executing moves. Recheck checksums before
and after each move, refuse collisions, keep a reversible move log and fix
references in the same pass. Elias approves removal of old notes. A plan that
became tickets may leave staging only after its decisions have a durable
record. Evidence does not expire merely because its plan was implemented.

Application-managed folders (Tableau, BlackmagicDesign, Power BI), credential
files and unrelated personal documents are excluded. A credential-like name
is a review signal, not proof of its contents. Leave secrets closed and in
place during a general folder cleanup.

## Publication and backup

- `agents evidence <project>/<branch>/<sha7> <captures>` publishes only explicitly
  cleared, nonsecret artifacts (images, video, logs and data files), and it is the
  only road into `eliasdlc/evidencia`: never `gh api` or `git`. Public storage is
  permanent: seeded data only.
- A Postplan link publishes a page, under the standing line of the core rules.
  Showing the same page in the T3 thread or writing it to Documents does not
  publish it; `visual-briefing` chooses among them.
- Put private evidence and receipts in the private product delivery record or
  approved private artifact storage. Link the immutable object from the PR and
  Zoho, and keep Documents itself private rather than mirroring it publicly.
- A published capture does not back up its source assets. Report backup as
  unverified until a restore/checksum comparison has succeeded.
- Every new machine reads shared URLs. A local file path, SSH mount or matching
  directory name does not prove synchronization.

The decision behind this layout is in `references/history.md`; read it only
when changing it.
