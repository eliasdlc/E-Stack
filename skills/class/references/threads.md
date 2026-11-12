# Threads between classes

A course is not twelve loose notes, it is one thing being built. The professor
knows it and that is why the professor talks as if you remembered: "acuerdense de lo de
la semana pasada", "eso que les deje ya lo pueden entregar el lunes", "esto
necesita que tengan claro lo otro".

Each of those sentences is a thread. If it is not picked up, today's note
starts in midair and last week's is left lying.

## Open the thread before reading

The history is loaded **before** reading the new transcript, not after. It is
what makes it possible to recognize a reference: without knowing that last
class talked about race conditions, "acuerdense de eso" is noise.

```bash
python3 ~/dev/class-pipeline/class_session.py history --course "<course>" --before <date>
```

It returns, per previous class: date, summary, topics, items with their Kino
`taskId`, whether they carry his name, and the ids of the page. Apart from
that, `open`: the questions, the carryovers, the problems and the undated items
of the whole course. That list is the one to keep in mind while reading:
**today's class is the one most likely to close them**.

Titles and ids, not content. For the detail of an old class, `read`.

## The language of a reference

| What is heard | Almost always is |
|---|---|
| "acuerdense de", "como vimos", "lo que dimos la semana pasada", "volviendo a" | `revisits` |
| "se los corro para", "mejor entreguenlo el", "les extiendo", "ya no es necesario que" | `updates` |
| "ya subi lo que les prometi", "les confirmo que", "sobre lo que preguntaron" | `resolves` |
| "esto necesita que ya tengan claro", "si no entendieron lo anterior esto no va a cuadrar" | `depends` |
| a class that is named and has not been processed | `no_record` |

Watch out for the most common false positive: **repeating a topic is not
revisiting it**. If today the professor explains race conditions from scratch again
because nobody understood, that is a topic of today, not a thread. The thread
exists when the professor **leans on** what came before, not when the professor repeats it.

## The five types

| type | In today's note | In the old note | In Kino |
|---|---|---|---|
| `revisits` | A "Comes from" line linking to the old page, and the `effect` explaining what it adds today | A "Continues in" line at the end of the section of the topic | Nothing. The notes are already linked |
| `updates` | Goes into the Threads section with the old date and the new one | The old date is struck through and it is said that it moved, with the date of the class that moved it | `update_task` on the existing task. **Never** a new task |
| `resolves` | The answer, complete, in the section it belongs to | The question is marked as resolved, with the answer and the link to today's page | `complete_task` on the reminder of the question |
| `depends` | A "You need first" line with a link | Nothing | Nothing. A dependency is not a subtask |
| `no_record` | A line saying that class is not processed | There is no old page | A `question` item: "Process the class of \<date\>" |

### Why `updates` never creates a task

It is the mistake that ruins a task system. The professor moved practice five
from Friday to Monday: if that comes in as a new task, there are two practice
fives in Kino, one overdue and one alive, and in two weeks neither of them is
believed. `history` brings the `taskId` exactly for this.

If the old task has no `taskId` (that class never went up to Kino), there is
nothing to update: it stops being a reference and becomes a `pending` item,
which does get created. That border is what avoids the duplicates and it is
written in [extraction](extraction.md).

### What the platform closes is not a thread

A question about "downloading the document from the PVA" is closed in the cross
check with mikampus, not with a sentence of hers. That is not a `resolves`
reference: there is no quote to hold it up and the validator will reject it,
rightly. It is resolved in the cross check, it is said in the report, and that
is it.

### `resolves` is the one that gives the most value

A question that stays open for three weeks is a grade that comes out wrong.
When the professor answers something that was asked in another class, closing
that reminder in Kino and writing the answer in both notes is what makes the
system worth more than taking notes.

## Writing backward without breaking anything

Touching the old page is the delicate part. Three rules:

1. **Read before writing.** `get_page` returns the content in markdown and an
   `updatedAt`. That value is sent back in `update_page` as
   `expectedUpdatedAt`: if somebody edited the page since then, the write fails
   with `CONFLICT` instead of stepping on it. On a conflict it is read again
   and the change is applied on top of the new content.
2. **Only add or mark, never rewrite.** A new line, a struck through text with
   its explanation. What he wrote by hand on that page stays intact.
3. **A backward note says where it comes from.** "Moved to September 8 in the
   class of the 4th" with a link, not "Moved to September 8".

The links between pages are plain markdown, and the URL of a Kino page is
`https://www.usekino.dev/systems/<systemId>/pages/<pageId>`.

## In the chat

The table of items does not change. Below it goes a separate section,
**Threads**, with one line per reference:

```
Threads with previous classes
- Revisits: Race condition (Aug 28), MPI avoids the race because there is no shared memory
- Updates: Upload practice 5 to the PVA, Friday Sep 4 moves to Monday Sep 8
- Resolves: Confirm whether there is a template for the report (Aug 28), there is, it is on the PVA
- No record: the class of Aug 13 is not processed, Amdahl's law was covered there
```

And what changes backward is said **before** the gate, not after. Moving a due
date and closing a question are writes over what already exists: he has to see
them before giving the go ahead, not find out in the report.

## The lock

`class_session.py save` validates every reference the same way it validates an
item, and on top of that:

- The quote has to exist literally in today's transcript.
- `to_class` has to have a saved digest, of that course, with an earlier date.
  If it does not exist, the correct type is `no_record`.
- `to_topic` or `to_item` has to resolve against something real of that class.
  The title is copied from `history`, not rewritten from memory.
- `resolves` only points at an item of type `question`. `updates` never points
  at a topic nor at a question.

A thread toward a topic nobody wrote down is an invented thread, and it does
not get saved.

## What is not done

- Linking by topical resemblance. Two classes talking about MPI is not a
  thread. The thread is opened by the professor with a sentence, and that sentence is the
  quote.
- Chaining backward more than what was said. "Acuerdense de la clase pasada"
  points at the previous class, not at the four before it.
- Reopening a question that was already closed. If the topic comes up again, it
  is a new item.
- Touching the old page of a class that is still `pending`: if it never went up
  to Kino, there is nothing backward to update.
