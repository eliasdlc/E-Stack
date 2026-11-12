# The professional settings, per format

The `docx`, `pptx`, `xlsx` and `pdf` skills (`anthropic-skills:*`) own
the mechanics: how to read, write and validate each file. This page owns what a
professional checks before a file leaves, so the result looks made by someone
who knows the program, not by a library.

## Word (docx)

| Setting | The professional default | Why it shows |
|---|---|---|
| Styles | Every heading and paragraph uses a named style from the template (Title, Heading 1-3, Normal); no direct bold-and-size headings | The navigation pane and the table of contents only see styles |
| Table of contents | A real TOC field built from Heading 1-3, updated before export | A typed index breaks the moment a page moves |
| Page setup | Letter (8.5 x 11 in) for PUCMM and Dominican clients unless the template says A4; margins from the template (university deliverables default to A4, see `university.md`) | A4 in a Letter printer cuts the footer |
| Sections | Cover in its own section with no page number; numbering starts on the first content page | A numbered cover reads as careless |
| Headers and footers | Different first page; the course or project name and page X of Y from fields | Hand-typed numbers go stale |
| Language | Proofing language es-DO (or en-US) on Normal and every style | Spell check in the wrong language flags every word |
| Tables | Header row repeats across pages, rows do not break across pages, widths fixed to the text column | Tables that break mid row were a correction he made |
| Images | Inline with text, alt text set, sized to the column, 150 to 300 dpi | Floating images jump on edit |
| Citations | The course's style (APA 7 unless told), references list as a styled list | A pasted bibliography breaks the format |
| Captions | Only when the template or rubric uses them ("lo de Fig. # esas son cosas que yo no hago") | |

## PowerPoint (pptx)

| Setting | The professional default | Why it shows |
|---|---|---|
| Slide master and layouts | Every slide uses a layout from the template's master; text lives in placeholders | Text boxes placed by hand do not follow theme changes |
| Size | 16:9 (13.333 x 7.5 in) unless the template is 4:3 | Mixed sizes letterbox in the room |
| Fonts | Theme fonts from the template; if a font is not standard, embed it or use a safe one | A missing font reflows every slide on the jury's laptop |
| Editable content | Charts as native charts with their data, diagrams as shapes, tables as tables; never a screenshot of a slide or a chart ("Lo que hiciste fue muy perezoso", 3 Sep 2026) | He edits after delivery |
| Video | Embedded mp4 (H.264), poster frame set, plays on click; not frames pasted as images | |
| Speaker notes | What each presenter says, in the notes pane, when he asked for a script | The script travels with the deck |
| Animations | Native entrance and transitions only, few and consistent | Imitated motion breaks in Google Slides |
| Accessibility | Every image with alt text, reading order checked, contrast readable | |
| Count | At most what the rubric or he asked ("no quiero mas de 10 slides") | |

## Excel (xlsx)

| Setting | The professional default | Why it shows |
|---|---|---|
| Data as tables | Ranges formatted as Excel tables with headers; one table per sheet purpose | Filters, totals and formulas follow the table |
| Formulas | Computed values are formulas referencing cells, not pasted numbers; no hard-coded totals | A changed input must change the result |
| Number formats | Currency RD$ with two decimals, dates dd/mm/yyyy, percentages as % | Raw floats look unfinished |
| Layout | Header row frozen, columns sized to content, sheet names that say what they hold | |
| Validation | Data validation lists for categorical inputs he types | Typos break pivots |
| Charts | Native charts tied to the table | A pasted chart image cannot be updated |
| Print | Print area set, fit to one page wide, landscape for wide sheets | |
| Sheets he asked for | Exactly the sheets requested (for example two sheets: pending tasks and explanation) | |

## PDF

| Setting | The professional default | Why it shows |
|---|---|---|
| Export | From the Office file that is the source (`soffice --headless --convert-to pdf` on the `.docx`), with fonts embedded and text selectable; never a PDF of screenshots (on 5 Oct a brochure PDF came out as images of text) | Printers and graders select text |
| Bookmarks | From Word headings | Long reports are navigable |
| Size | Under the platform limit; compress with the media skill when needed | The PVA rejects large uploads |
| Print pieces | Bleed and crop marks as figma-assets describes | |
| Metadata | Title and author set; no library traces | |
