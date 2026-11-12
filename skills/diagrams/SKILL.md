---
name: diagrams
description: Makes and checks Elias's diagrams in draw.io: BPMN process flows with decisions, C4 architecture, star and ER schemas, from his template, linted before he sees them and exported to PNG or PDF without opening a window. Use for "diagrama", "draw.io", "drawio", "BPMN", "flujo", "flujograma", "rombo", "C4", "arquitectura", "modelo estrella", "diagrama de procesos", in English or Spanish, and before handing over any .drawio file. Not for Figma pieces (figma-assets) or charts of data (dataviz).
---

# Diagrams

The thesis diagrams went through several review rounds on 9 Oct for the same
three mistakes: a diamond with its question outside it, an empty diamond, and
a diamond wired straight to another diamond. Those are machine-checkable, so a
diagram is linted before anyone reviews it.

## 1. Start from his template

The template comes from the project's `## Facts` (`drawio template:`); if
there is none, ask once where it is and write the line there. Copy it, keep
its styles, colors and fonts, and build on the copy. A course that asks for
draw.io gets draw.io, not Mermaid.

## 2. The rules

| Kind | Rule |
|---|---|
| BPMN decision | The question goes inside the diamond and ends in "?"; every exit is labeled (Sí/No or the condition); at least two exits |
| BPMN flow | One start and at least one end event; every shape connected; no diamond straight into a diamond (an activity sits between two decisions) |
| BPMN lanes | One lane per actor, named as the course names them |
| C4 | One level per diagram (context, container or component); each box says what it is and its technology; each arrow says what it carries |
| Star or ER | Fact table in the center, dimensions around it, keys marked; names match the dataset |

## 3. Lint, export, look

```bash
python3 scripts/lint_drawio.py FILE.drawio      # rules above; exits 1 with one line per problem
bash scripts/export.sh FILE.drawio png          # inside headless gamescope, no window on his screen
bash scripts/export.sh FILE.drawio pdf
```

Fix every lint line, export, open the PNG and read it: labels fit their
shapes, nothing overlaps, arrows do not cross through boxes. Then hand over
the `.drawio`, the PNG and the PDF paths. The versions hook keeps the previous
file when it lives under Documents.
