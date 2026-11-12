# Forum drafts

A forum contribution is graded work that Elias publishes himself. What the
pipeline leaves him is a page he can read on the phone and turn into his post in
a few minutes: what the prompt asks, what classmates already said, an angle
nobody took, and a draft in his voice. Nothing is ever posted from here.

## When a draft is made

- A class item asks for a forum contribution ("respondan el foro", "participen
  en el foro de", "aporten en el foro"), or `get_pva_due` lists a forum with a
  due date, and the task is still open.
- The discussion the prompt points to has no post with `isMine`. A
  discussion he already answered gets no draft. `answeredByMe` is true when he
  posted in any discussion of the forum, so a new discussion in a forum he has
  used before still needs its own check.

## What is read first

| Source | Tool | What it gives |
|---|---|---|
| The forum | `get_pva_forum` by name or `cmid` | The prompt (`intro` and the professor's opening post), every classmate post, and when it was read (`freshness`) |
| The course memory | `get_page` on `Memoria: <course>` | The professor's rules: length, sources, AI limit, how he grades participation |
| The class where the topic was seen | `class_session.py history`, then the class note; the automatic run has no Bash and greps the digests in `Aprendizaje/classes` instead | What was said in class, so the draft builds on it |
| Course material | `search_pva_files`, `get_pva_file` | A source the course already uses, when the prompt asks for one |

If `get_pva_forum` returns an `unknown` of kind `pva_mensajes_de_foro`, or the
tool is not there, the posts were never read: the page says so in its first
line, and the draft is written from the prompt alone.

## What the page carries

One Kino page in the course folder, titled `Borrador foro: <forum name>`, linked
to the forum task with `link_task_to_page`. In this order:

1. **Aviso.** One line: it is a draft written by an agent for him to rewrite in
   his words; the post he publishes is his. When the memory carries an AI limit
   from the professor, it is quoted here with its date.
2. **Lo que pide la consigna.** The prompt in two or three lines, with its due
   date and any length or source the professor asked for. When the class note
   and the written prompt disagree, both are shown and the written one wins.
3. **Lo que ya dijeron.** One line per classmate: author and the angle they
   took. This is what the draft must not repeat.
4. **Tu ángulo.** The angle nobody took, in one sentence, and why it answers the
   prompt.
5. **Borrador.** In Spanish, first person, plain, the length the prompt asks
   (150 to 250 words when it does not say). No headings, no lists unless the
   prompt asks for them, no phrase a classmate already wrote.
6. **Fuentes.** Only what was opened, in the format the course uses.

The task description gets one line at the end: `Borrador listo: <page URL>`.

## When the forum changes

A later run that finds new classmate posts rewrites sections 3 to 5 of the same
page (`get_page`, then `update_page` with its `expectedUpdatedAt`), and the
draft moves away from whatever a classmate has posted since. Once that
discussion has a post with `isMine`, the page stays as it is.
