---
name: figma-assets
description: The order of work for anything Elias wants made or changed in Figma: social posts and stories, flyers, brochures, print cards, badges, speaker and sponsor posts, templates, handoff files. Covers the MCP login and which account, finding the file in the project's Facts, matching the template and the taste ledger, editable layers (never a flat image), variants and earlier versions in their own sections, PNG or print PDF with bleed, and the contact sheet. Use on "en Figma", "hazlo en figma", "figma link", "publicaciones", "posts", "flyer", "brochure", "tarjeta", "gafete", "plantilla", "stories", "guarda las versiones", "editable", "make a post in Figma", before the first Figma tool call. Not for UI code, Miro or Canva.
---

# Figma assets

Elias's posts, print pieces and badges are Figma files he edits afterwards, so
the deliverable is editable layers in the right file, in the project's style,
with nothing lost. `design-grammar` owns taste and the taste ledger,
`development-workflow` owns the Facts convention; this skill is the order of
work. Call the Skill tool with "design-grammar" before the first pixel.

## 1. Connection and account, before any other work

```
timeout 60 claude mcp list 2>&1 | grep -i figma
```

The Figma plugin (figma@claude-plugins-official) is off everywhere by the
agents repo's lean start, so there is one server per login. The route is the
`claude.ai Figma` account connector, which keeps its own login and loads only
in the design directories `workspaces/registry.json` grants it (`claude mcp
list` does not show it; ToolSearch does). Use the one that is Connected, load its tools with ToolSearch
(search "figma whoami"), call `whoami`, and state the account, plan and seat
in one line. Compare it with the account in the project's Facts: `exdj0002`
edits the CICC and ConoceRD files, the personal account is read-only on CICC.

| Signal | Meaning | Tell Elias, once |
|---|---|---|
| `Needs authentication` | no login yet | the steps below |
| The plugin is Connected, but this T3 session has no Figma tools | T3 does not load plugin servers; a new T3 thread hits the same wall | the connector steps below, then a new T3 thread with the full handoff and the real URL, never a `<link>` placeholder. For work already blocked, a headless `claude -p` with `--mcp-config '{"mcpServers":{"figma":{"type":"http","url":"https://mcp.figma.com/mcp"}}}'` reuses the stored login, on his words |
| `claude.ai Figma` is `needs-auth` | the connector was never connected, or with another Figma account | the connector steps below |
| `Can't call "createSection" in read-only mode` | the account is not an editor in the team that owns the file; a "can view" share or a share to his other email does not count | the email `whoami` returned and the file name: invite that exact email as editor (team member), or reconnect the MCP with the account that owns the file |
| `whoami` differs from the Facts account | wrong login | reconnect with the Facts account |

Connector (T3): first make sure figma.com in the browser is signed in as the
Facts account, because the authorization takes whichever Figma account is
open there; then https://claude.ai/customize/connectors, **Figma**,
**Disconnect** if it shows an error, **Connect**, check the email on Figma's
page, **Allow access**. A new session sees it. Plugin (terminal): `cd
<project> && claude`, `/mcp`, the plugin's **figma** server, **Authenticate**,
sign in with the Facts account, **Allow access**, `/exit`. The `authenticate` tool
cannot start that login. While blocked, say so and prepare assets; a render
from HTML or from the repo is not the Figma deliverable ("no te conectaste a
figma", 21 Sep). Miro is also connected, and "en Figma" never means Miro.

## 2. Find the file

1. The `figma:` lines in the project's `## Facts` (the SessionStart hook prints them).
2. `agents session "figma <project words>"`, or stream the transcripts: `grep -rlE 'figma\.com/design' ~/.claude/projects/<project dir>`, then read only the hits.
3. Ask only when two files fit, naming both and what each holds. A link is never the first question: on 14 Oct a handoff went out with a `<link>` placeholder and Elias answered "go look for the link, its in past sessions".

Confirm before editing: `get_metadata` with no `nodeId` lists the pages, then
look at one screenshot. On 5 Oct the first hit was a discarded file
(`ARCHIVO DESCARTADO / Primera propuesta`).

In the same turn, write the file into the project's Facts, one line per file:

```
figma: https://www.figma.com/design/<key> (<account>; <file name>, page <page>: Plantillas <node>, Finales <node>, Archivo <node>)
```

The map comes from `use_figma` listing `figma.currentPage.children` (id, name,
type, size). `get_metadata` on a whole page of a big file returns millions of
characters and errors; call it on one section.

## 3. Style: three sources, in this order

1. The `## Taste ledger` in the project's `DESIGN.md` (`design-grammar` defines it). A correction from Elias goes there in the same turn.
2. The template already in the file. Measure its fonts, fills, sizes and logo components with `use_figma`; do not assume the repo's fonts (on 21 Sep the posts used the site's Bricolage and Geist while the club kit used Amaranth Bold and Inter, and the feed stopped matching).
3. Last year's pieces in the same file (for Barcamp, the 2025 reference section).

## 4. Work

| Rule | Reason |
|---|---|
| Call the Skill tool with "figma-use" before every `use_figma` (Figma marks it mandatory), with "figma-generate-design" for full designs from the file's system, and with "figma-create-new-file" before `create_new_file`; they come with the plugin. This skill is the order of work on top of them | figma-use carries the Plugin API rules that prevent the hard-to-debug failures |
| Duplicate the template or its component instance, then edit text and fills | the new piece inherits the family |
| Text is text layers with the real font, shapes are vectors, logos are the file's components or the project's SVG; images only for photos and generated backgrounds | "son imagenes y ya, no elementos de figma editables" (21 Sep), "totalmente editable todo" (23 Sep) |
| A soft or blurry raster logo gets replaced by the project's SVG; with no SVG, say so once | Elias: Figma can make it sharp and resizable |
| Imports from HTML (html.to.design) come as flat pictures and layers named `figure` or `div.flat`; they go to a section marked `Archivo (no usar)`, not into a deliverable | LIORA, 26 Sep: 140 frames named `figure` |
| N variants, each in its own labeled section or row with a code (`1A`, `2C`), structurally different (layout, type scale, background idea), not recolors; a series of posts must not read alike | "los tres posts se ven iguales" (9 Oct); he chooses by code |
| Before changing an existing piece, clone it into the file's `Archivo` section named with the date and what it was, then edit the live one. Never delete or overwrite | "guarda las versiones anteriores" (21 Sep); instances and links keep pointing at the live piece |
| `generate_image` spends paid credits: only on Elias's words in the last message | 19 Sep: 26 credits on unrequested images |

Check each piece with `use_figma` before sending it:

- Every text fits its frame. Test the longest title in the set (Batista and Morales on 14 Oct), because `resize()` resets text auto-resize.
- No placeholder is left: `FOTO`, `Lorem`, `XX`, `TODO`, `<link>`, the template's sample name.
- No foreign script that is not in the copy. The Chinese in a speaker's title was replaced by its Spanish translation at his request, and the swap was reported.
- Logos sit where the ledger says (for CICC and PUCMM: bottom right, equal padding from both edges). With no ledger line, copy the template's placement. No `@handle` inside an Instagram post.
- A carousel is laid out in swipe order, left to right, so a continuous background connects.

| Gotcha | Fix |
|---|---|
| WebP is accepted but not drawn | convert to PNG and upload again |
| Photos into frames | `upload_assets` with the target rectangle ids returns one URL per node; `curl -F file=@photo.png "<url>"` each, scale mode FILL |
| `set_vectorPaths` fails with `Invalid command at H` | write paths with `M L C Z` only |
| Rate limit or plan error | read `file://figma/docs/rate-limits-access.md` through the MCP; Starter seats have monthly call limits |

## 5. Export and deliver

| Output | How | Check |
|---|---|---|
| Social PNG | feed 1080x1350 (4:5), story and reel 1080x1920, at 1x; `get_screenshot` or `download_assets` per frame; `https://www.figma.com/api/mcp/asset/<id>.png` is the file URL, save it with `curl -sL` | pixel size equals the platform size; open each PNG |
| Print PDF | frame at real size, 1 px = 1 pt, 3 mm bleed inside the frame, guides in a hidden layer `Guías (no imprimen)`; `download_assets` with `defaultFormat: pdf` per face; then trim and bleed boxes, plus a crop-marks copy (`references/print-pdf.md`) | `pdfinfo` page size = trim + bleed, `pdffonts` shows embedded fonts, every QR scans, render every page |
| Contact sheet | one screenshot of the whole section, plus one per piece; for a long set, a PDF with several pieces per page, reference codes and sections | look at each capture against step 4 before sending |

Print PDFs come from Figma's PDF export so text stays vector; a PNG-to-PDF
build carried the 5 Oct brochure's text as 504 ppp images. Where the files are
saved follows `workspace-files`. Close with the Figma node links, the contact
sheet embedded in the answer, the export paths, and the updated Facts map if
sections changed.
