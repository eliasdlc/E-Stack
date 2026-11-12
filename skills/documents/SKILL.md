---
name: documents
description: How a document Elias delivers is produced (docx, pptx, xlsx, pdf) for university, clients and his projects. Builds from his template or his previous document of the same kind, writes in his voice against the list of mistakes he has already corrected, sets him as the author with no library traces in the metadata, renders the result to look at it before handing it over, and keeps the previous version. Use for an informe, reporte, presentacion, deck, cotizacion, brochure text, carta, plantilla, "hazme el documento", "pasalo a Word", "el PDF", "la presentacion", or any file he will submit or send, in English or Spanish. Not for Postplan pages (visual-briefing), Figma pieces (figma-assets) or the 606/607 (dgii-accounting).
---

# Documents

A document goes to someone who judges it: a professor, a client, a jury. It
is built from what Elias already uses, written the way he writes, and looked
at before it leaves.

## 1. Start from his template, never from a blank default

| What is being made | The starting file |
|---|---|
| Another of something he has made before | His previous document of that kind: its styles, margins, header, cover and length |
| A university deliverable | The professor's template or rubric from the PVA first (`/tarea` owns that step), then `~/Documents/Universidad/Templates/` |
| A project or client document | That project's `Templates/` folder, else his last document for that client |
| Nothing exists yet | Ask once which past document it should look like; a python-docx default reads as generated |

Build with the template as the base file (`Document(template)`,
`Presentation(template)`), so styles come from it. A new template he approves
goes in the domain's `Templates/` folder (the workspace-files skill owns the
paths), named for what it is.

Work on the current version. Before editing a file he may have touched, check
its modification time against your last read; on 4 and 5 Oct a deck and a
document were edited on top of an older copy and his newer changes were lost.
The `versions` hook keeps the previous copy in a sibling `versiones/` folder,
and `bin/docdiff OLD NEW` lists what changed: paste that list when he asked
for parts to stay as they were.

## 2. Write it the way he writes it

`references/writing.md` lists every correction he has made to a document,
with the date, and the checklist every draft is revised against. The short
version:

- Titles say what the section is. No metaphors, no slogans, no "Fig. N" labels
  unless the template uses them.
- As long as it needs and no longer: a two page quote is two pages.
- Every number and fact comes from a source you read: his survey is his
  survey, a national statistic is cited as one. Unknown is written as unknown.
- Every acronym is spelled out the first time.
- Text meant to be spoken follows its own rule in `references/writing.md`.
- Spanish for a Spanish reader, Dominican register, his name with accents.

The checklist is about writing quality, because those patterns make a
document worse for any reader. This skill does not score text against AI
detectors, run evasion passes or insert deliberate errors.

## 3. Build it like a professional

The text is written into the `.docx` itself (or the `.pptx`, the `.xlsx`), on
his template, and every PDF is rendered from that file. He edits in Word or
LibreOffice and two sources drift apart, so the editable file he receives is
always the Office file, not an HTML page, a Markdown draft or a build script.

The mechanics belong to the official Anthropic skills (`anthropic-skills:docx`,
`:pptx`, `:xlsx`, `:pdf`, supplied by the Claude account, not by this repo):
call the Skill tool with the one for the format you are producing or editing. They know the file formats, tracked changes,
layouts, formulas and validation. `references/office.md` lists the settings a
professional checks in each program (styles and the table of contents in
Word, the slide master and native charts in PowerPoint, formulas and tables in
Excel, embedded fonts in a PDF); every file goes through its table before it
leaves.

A university deliverable also follows `references/university.md`: the voice, the
section structure, the default page and style settings and the file names.

## 4. Finalize the file

```bash
python3 scripts/finalize.py FILE.docx --title "Informe 2: ..."   # author Elías De La Cruz, no library traces
soffice --headless --convert-to pdf --outdir "$(dirname FILE.docx)" FILE.docx   # the PDF comes from the docx
```

`finalize.py` edits only `docProps`: creator and last modified by become him,
the title is set, and any field naming the generating library is removed. A
value that came from his own template stays; nothing is invented.

## 5. Look at it, then hand it over

Render to PDF and read the pages: page count against the limit, nothing cut,
tables intact, images present, no placeholder left. A deck gets its slides
rendered too. Then hand over the path (or attach the file) of the `.docx`,
`.pptx` or `.xlsx` he will edit or submit, plus the PDF rendered from it when he
will upload a PDF.
