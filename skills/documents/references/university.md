# University documents

Read this when the document is a deliverable for a course. The `tarea` skill
owns the assignment process; this page owns how the file looks and is named.
Everything here yields to the professor's template or rubric.

## Language and voice

Spanish, Dominican, formal academic register. Technical terms stay in English
and are not translated (`dataset`, `room`, `ETL`, `SIEM`, `commit`; `flujo`
for a Tableau flow is fine). English only when the course itself is in English.

Write full paragraphs that reason, not bullet fragments. A section says what
was done, what came out and what it means, in that order. First person singular
for what he did (`ejecuté dirb`, `completé los cuatro rooms`), third person for
what a source says (`Sherman divide esta justificación en dos partes`). No
emojis, no cheering (`¡Excelente!`) and no closing summary that repeats the
document.

Say the concrete thing: `De las 4,610 peticiones quedaron dos rutas` beats `se
encontraron varios resultados`. When something matters, give the number, the
date, the account, the command.

## Structure

```
Título del documento
Subtítulo o sesión, cuando aplica

Asignatura: <nombre> (<código>, Grupo <n>)
Estudiante: Elías De La Cruz Jiménez
Profesor: <nombre>
Fecha: <día> de <mes> de <año>

1. Introducción          qué se hizo, cuándo y con qué cuenta
2. <Primer bloque>
   2.1 Qué hice
   2.2 Qué encontré
   2.3 Análisis
3. <Siguiente bloque>
...
N. Conclusión            opcional, y solo si aporta algo que no está arriba
Referencias              IEEE, numeradas (the course's own style wins)
```

Sections are numbered. Terminal output goes in a monospaced block exactly as it
printed, uncut. Screenshots go in a figure, when the template or rubric uses figures, with a
caption that says what is being looked at and where it came from, not `Figura 3`.

## Format and toolchain

The editable source is always `<Nombre_Del_Documento>.docx`, built on the
professor's template or the cover in `~/Documents/Universidad/Templates/`. The
PDF that gets uploaded is rendered from it, because he edits in Word or
LibreOffice and a second source drifts from the first:

```bash
soffice --headless --convert-to pdf --outdir . Nombre_Del_Documento.docx
```

A correction goes into the `.docx` and the PDF is rendered again. Shorter work
with no code or captures can be typed straight in LibreOffice Writer and saved
as `.docx`. An older submission that has an `informe.html` keeps it as a
record.

The format lives in the document's named styles, so an edit in Word keeps it
(the default when the template says nothing):

- A4, 22mm top and 20mm on the other sides.
- Body (Normal) in Liberation Serif 11pt, justified, line height 1.45.
- Headings in Liberation Sans.
- Code and terminal output in a code paragraph style: Liberation Mono 8.5pt,
  light grey shading, left border.
- The identification block sits between two horizontal rules under the title.

File names use `Palabras_Con_Guion_Bajo`: the same base name for the `.docx`
and its `.pdf`, descriptive, no dates inside the name, no spaces. The student's
name goes in the file name only when the professor asked for it.

## Before it counts as done

The `.docx` and the PDF rendered from it exist, the PDF has been read once end
to end, and its numbers match the evidence next to it. Handing it in is his
action, not an agent's: report both paths and what is left to do, and stop
there.

<!-- 15 Oct 2026, Elias: "Necesito el texto editable en un docx, nunca en un html". Until then deliverables were authored as informe.html with print CSS, printed with chromium, and a docx came out only when a professor asked. Submissions before that date keep their informe.html. -->
