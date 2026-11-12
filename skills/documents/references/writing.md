# Writing a document Elias delivers

## What he has already corrected

Each row happened in a real session; the fix is what the next draft does.

| Date | What he said | The fix |
|---|---|---|
| 15 Oct 2026 | "Necesito el texto editable en un docx, nunca en un html" | The editable source is the `.docx`, and the PDF is rendered from it with `soffice`; no HTML or Markdown is handed over as the text |
| 12 Oct 2026 | "los titulos son muy corny y muy cringy... no hay que ponerle un eslogan... es una tesis y punto" | Titles name the content: "Pregunta de investigacion", "Datos", "Resultados" |
| 16 and 17 Sep 2026 | "lo de Fig. # esas son cosas que yo no hago", "demasiado profesional" | No figure numbering or corporate tone unless the template or rubric asks for it |
| 18 Sep 2026 | "me creaste un documento de seis paginas... todo podria caber en dos simples paginas" | Length comes from the content and the limit, not from completeness |
| 12 Oct 2026 | "Que significa MAE?" | Every acronym spelled out the first time, in the document and in any script for speaking |
| 5 Nov and 12 Oct 2026 | "Eso esta muy confuso, explicalo mejor" (a sentence in a speaker script); a script declared spoken after a word count | Text meant to be spoken (script, speech, presentation notes) has no labels, colon headings, lists or parentheses inside its lines; before delivery each line is said through in full and any line that does not sound like speech is rewritten. No voice tool exists, so the duration estimate (about 130 words a minute) is only the length check |
| 18 Sep 2026 | "Literalmente acabas de mentir en el documento porque si tienen resenas" | Every claim about a business, a person or a number is checked against the source before it is written |
| 4 Oct 2026 | "son 540,000" (the draft said 537k) and "ese porcentaje de la ENTI 2025 en base a cuantas personas?" | Numbers are copied, not rounded; his own survey and a national survey are never mixed, each is cited as what it is |
| 12 Oct 2026 | "Los riesgos que muestras ahi no son muy reales" | Risks, limits and budgets are the project's real ones, or the section is left out |
| 12 Oct 2026 | "Rapidamente, explicame la pregunta de investigacion, porque no tiene sentido" | A research question says what it compares against what, measured how |
| 2 Oct 2026 | "cambiaste la tabla completamente... eso se tiene que quedar exactamente igual" | What he did not ask to change is not changed; `bin/docdiff` proves it |
| 4 and 5 Oct 2026 | "trabajaste encima de una version que no tenia unos cambios nuevos" | Re-read the current file before editing; his edits since your last read win |
| 16 Sep 2026 | "nadie manda un mensaje de whatsapp con titulos" | A message is not a document: no headings, short, in his voice |

## The checklist every draft is revised against

These patterns make prose generic and harder to trust, for any reader. Each one
is the choice that fits every subject, where a person writing for one reader
chooses something specific. The Spanish forms are examples of the same habit,
not a list to search for.

| Pattern | Rewrite |
|---|---|
| Intensifiers and stock vocabulary: "crucial", "pivotal", "robust", "delve", "landscape", "tapestry", "showcase", "underscore"; "crucial", "fundamental", "robusto", "panorama", "un abanico de", "cabe destacar", "es importante destacar que" | Delete, or replace with the fact that makes it important. One such word alone is not a tell; a cluster is |
| Inflated significance: "marks a pivotal moment", "stands as a testament", "plays a key role"; "marca un hito", "es un testimonio de", "juega un papel clave", "deja una huella imborrable" | Keep the fact (what happened, when, who) and drop the claim about its importance |
| Promotional language: "nestled in the heart of", "rich heritage", "breathtaking", "renowned"; "vibrante", "rico patrimonio", "ubicado en el corazón de", "de renombre" | Say what the thing is and what it does. A client document is not an advertisement for the client |
| Superficial -ing analysis: a participle tacked onto a fact to give it depth ("..., highlighting its importance", "..., reflecting the community's commitment"); "..., lo que subraya...", "..., reflejando el compromiso de..." | Keep the fact. Keep the tail only when the source says it |
| Vague attributions: "experts argue", "studies show", "it is considered"; "los expertos coinciden", "diversos estudios", "se considera que" | Name who said it and where, or cut the claim |
| Vague connection: "associated with", "linked to"; "vinculado a", "relacionado con" | Name the relationship (founded, funds, is a client of), or keep the vague word only when the source is vague |
| Avoiding "is" and "has": "serves as", "stands as", "boasts", "features"; "funge como", "se erige como", "cuenta con", "ofrece" | "Es", "tiene", "hay" |
| Lists of three by habit ("rapido, seguro y escalable"), and three parallel examples followed by a lesson | Keep only the items that are true and specific; keep three when the content has three |
| Negative parallelisms: "No es X, es Y", "no solo X, sino tambien Y", "more than X, it is Y", and the split form "This does not mean X. It means Y." | State Y with its evidence. Keep the contrast only when the X half corrects something the reader actually believes |
| Arguing with no one: "I am not saying", "to be clear", "una opcion tentadora seria"; an objection or alternative that appears nowhere else | State the point; keep an alternative only when the reader would really weigh it |
| Hedging stacks ("podria potencialmente ayudar a") | Say what it does, or say it is not known |
| Staged run-ups and sayings that sound deep: "let's dive in", "vamos a sumergirnos", "the real question is", "en el fondo", "at its core" | Start with the point |
| A guess where the source is silent: "likely", "probablemente se formo en", "based on available information" | Write "not documented in the sources", or cut the sentence |
| Every sentence the same length and shape; the same sentence opening three times in a row | Vary it the way the content varies; short for a fact, longer for a reason |
| A closing paragraph that restates the section, a one-line paragraph that repeats the one above, or a send-off ("el futuro luce prometedor", "a pesar de los desafios, continua prosperando", "exciting times ahead") | End on the last fact. A section called challenges and outlook is written only when the project has real ones, with their numbers |
| Describing the document instead of its subject: "la tabla a continuacion compara", "este apartado se organiza en", "anything unconfirmed is flagged" | Say the content. Keep a note about the document only when it changes what the reader does |
| Metaphor titles and slogans; Title Case On Every Heading; a heading repeated by the first sentence under it | A sentence-case title that names the content, with the first sentence adding something |
| Bold on words that need none, a bold label before every list item, emojis or arrows as bullets | Plain text; turn a labeled list into a sentence when the labels carry nothing |
| Chat residue inside a deliverable: "espero que esto te ayude", "claro!", "dime si quieres que lo amplie" | Delete the wrapper and keep the content |
| Abstract nouns where a person did something ("se realizo la implementacion") | Who did what: "implementamos el modelo bayesiano" |
| Promises without a number ("mejora significativa") | The number, or no claim |

**How to revise.** Mark every pattern first, then rewrite the paragraph around its
point instead of patching phrases one by one. The rewrite adds no fact, name,
number, date, quote or claim that the source or Elias did not give, and loses
none: compare the numbers before and after. Read it aloud. When he gives a
writing sample or the text is his, his voice and his punctuation win over this
table, and text he wrote is edited only where he asked.

**What this is for.** A reader trusting the text, and nothing else. These are
habits, not proof of who wrote a thing: people write this way too, the words
change with each model release, and a pattern alone in a passage is not a tell.
It is never used to dodge a detector or to pass a text off as written by hand;
the line that forbids that is in the documents skill.

<!-- Sources: Wikipedia "Signs of AI writing" (WikiProject AI Cleanup), for the pattern families and the warning that they are symptoms and not proof; blader/humanizer (structural patterns first, no added facts in the rewrite, the voice sample wins, leave quotations, titles and proper names alone, the heading and document-description patterns). Spanish forms are examples written for this repo. Left out: the humanizer rule against curly quotes and hyphenation, and its dash rule, because a check in this repo already bans the long dash. -->

Spanish documents are written in Dominican Spanish as he speaks it in an
academic or professional register, with accents correct and his name as
"Elías De La Cruz Jiménez" on a cover.
