# Extraction

How a class transcript is read and what comes out of it. The rule above all:
**a class is emptied whole**. What is not pulled out in this pass does not
exist, because nobody listens to the recording again.

Four products come out:

| Product | Digest key | What it is |
|---|---|---|
| The note | `summary`, `topics` | What was talked about and what he should have learned |
| What is actionable | `items` | Everything he has to do, with its bucket |
| What the professor said about the course | `from_professor` | Criteria, emphasis, rules, what shows up on the exam |
| The threads | `references` | What moves or closes from previous classes |

They are pulled out in the same pass because an assignment without its topic
next to it makes no sense three weeks later.

## What counts as an item

The test is a single one: **is there something Elias has to do, know or
resolve?** If the answer is no, it is content and it goes to the note.

| What was said | Bucket | Why |
|---|---|---|
| "La practica seis la suben a la PVA para el jueves" | `assignment` | There is a deliverable, a platform and a date |
| "Para la proxima vengan habiendo leido el capitulo 4" | `next_class` | There is required preparation |
| "El parcial es el 15 y cubre memoria compartida" | `month` | There is an evaluation with a date |
| "Los que no han subido la practica cinco, suban" | `pending` | A carryover that is still alive |
| "El lunes no hay clase, estoy en un congreso" | `notice` | It changes his calendar, it is not a deliverable |
| "A varios el codigo no les compilo y esa nota va en cero" | `problem` | He is stuck and it costs a grade |
| "Elias, tu te encargas del diagrama" | `assignment` with `personal` | They said his name |
| "Alguien pregunto si el informe era para el jueves, y no aclaro" | `question` | It was left open |
| "En el capitulo 4 esta la demostracion completa" | Not an item | It is a reference, it goes to the note |
| "Yo cuando estudiaba esto sufria" | Not an item | It adds neither concept nor assignment |
| "La practica cinco se las corro para el lunes" | **Reference**, not an item | The task already exists in Kino. See [threads](threads.md) |

The bucket is decided by **when it has to be acted on**, not by size. An
assignment that is also an evaluation of the month goes in `month`, not in both.

### `pending` against `updates`

It is the only border that produces duplicates, so it is decided with a fact,
not with judgment:

- `history` brings a `taskId` for that title, the task already lives in Kino.
  Then it is a **reference** of type `updates` and **nothing gets created**.
- `history` does not bring it (the previous class was not processed, or the
  task never went in). Then it is a **`pending`** item and it does get created.

Two practice fives in Kino is worse than none.

### `notice` against `assignment`

A `notice` changes the frame: day, room, deadline for the whole group, delivery
rules, way of grading. It has no deliverable of its own. If the notice forces
something to be done ("como no hay clase, me mandan el avance por correo"),
then there are two things: the `notice` and the `assignment` that comes out of
it.

### `problem`

What is stuck and costs him a grade or time if nobody touches it: a submission
that was uploaded wrong, a group that never showed up, a lab without access, a
grade that does not add up, material the PVA does not let him see. It carries
in `detail` **who has to solve it for him**: the professor, the PVA, the group or him.

A problem the professor solved at the whiteboard is not a `problem`: it is content, and
it goes to the `what_to_understand` of the topic.

### When they say his name

`personal: true` in any bucket. It is a separate boolean and not a bucket of
its own because "Elias, tu traes el caso" and "Elias, a ti te falto la
practica" are different things to do, and both carry his name.

The quote **has to contain the name or the direct pointing**. "Ustedes dos"
with a clear context that one of them is him counts, and the `detail` says why
it was read that way. A task for the whole group is not personal.

In the note these come out in their own section and in Kino they go up a step
of priority. It is what hurts most to lose from a class.

### The loose language of a professor

A professor almost never says "les asigno". They say "traten de", "seria bueno que",
"les recomiendo", "no se les olvide", "ya eso lo tienen en la plataforma".
Those sentences **do** generate an item, with two differences:

- The **priority** goes down (`medium` or `low`, see [kino](kino.md)).
- If no date was said, it is not invented: `certainty: unknown`, and closing it
  against the platform is attempted in the cross check
  ([mikampus](mikampus.md)).

### What a classmate said

A student question assigns nothing. What counts is **the professor's answer**.
If the answer changes a date or a scope, that is the item, and the quote is
hers. If the question was left unanswered, it is a `question` with the quote of
the question and `source: classmate`.

### The PVA

Every time the platform is named ("esta en la PVA", "lo suben por la
plataforma", "ahi les deje el documento"), the item carries `source: pva`. That
is what sends it to the cross check with mikampus, where it stops depending on
what was heard.

The documents the professor mentions having uploaded go in as a `question` with the title
"Download from the PVA: <whatever it is>", and the cross check almost always
resolves them by itself.

### Weights and percentages

A percentage is only recorded if it was said, exactly as it was said ("20%",
"un tercio de la nota"). It is never computed nor split. The cross check can
replace it with the published `gradeMax`, and then where it came from is said.

## What the professor said about the course

`from_professor` is the bucket for what is neither concept nor assignment, and
it is the first thing that gets lost from a class:

- What shows up on the exam and what does not.
- How the professor grades, what gets penalized, what format is required.
- Rules: lateness, groups, copying, late submissions.
- What the professor repeated three times, which is how a professor says it matters.

Each entry is `{what, quote}`. `what` states the rule and why it matters;
`quote` is the professor's sentence. If the entry points at a concept of the note, the note
marks it under that concept.

An emphasis is not an assignment. "Esto cae en el examen" does not create an
item: it creates an entry here, and the note raises it when he studies.

## The bar for the summary

A note that only lists topics is useless. Each topic of the digest carries:

| Field | What goes in | Bar |
|---|---|---|
| `topic` | The short name | How he would search for it in three weeks |
| `what_to_understand` | The reasoning, not the definition | What problem it solves and why it is done this way |
| `confused_with` | The neighbor it gets mixed up with | The difference in one line |
| `you_know_it_when` | The action that proves he understood | An action, not a feeling |
| `quote` | Where the professor explained it | The sentence that carries the idea |

`what_to_understand` is where the note is won or lost. The difference:

- Weak: "Broadcast and reduce in MPI were covered."
- Good: "Broadcast sends the same piece of data from one process to all of
  them; reduce takes one piece of data from all of them and combines it into
  one. They get confused because both touch the whole communicator. The proof
  that you understand it is knowing which of the two you need when every
  process has already computed its chunk of a sum."

`topic` and `what_to_understand` are mandatory and the validator requires them.
The other two are written when the class gives enough for them, and when it
does not, the hole turns into a `question`.

**It does not get filled in with what you know about the topic.** The note
belongs to that class, and if it carries things the professor did not say, he studies for
an exam that does not exist. That rule has a lock: the validator requires a
literal quote in every topic.

## The format of the digest

JSON, written to a temporary file and passed to `class_session.py save`.

```json
{
  "course": "Inteligencia de Negocios",
  "date": "2026-09-09",
  "professor": "Name or N/D",
  "summary": "Two or three lines: what the class was about and where it goes.",
  "topics": [
    {
      "topic": "Dato, informacion y conocimiento",
      "what_to_understand": "...",
      "confused_with": "...",
      "you_know_it_when": "...",
      "quote": "literal sentence from the transcript"
    }
  ],
  "from_professor": [
    { "what": "What the professor requires, penalizes or underlines", "quote": "literal sentence" }
  ],
  "items": [
    {
      "type": "assignment | next_class | month | pending | notice | problem | question",
      "title": "Verb and object. Short.",
      "detail": "What is needed to do it without going back to the class.",
      "personal": false,
      "origin": "class | platform",
      "due": {
        "iso": "2026-09-14 or null",
        "certainty": "explicit | derived | pva | unknown",
        "expression": "the words the professor used",
        "reason": "what it was derived from, when the certainty is derived"
      },
      "source": "pva | micampus | professor | classmate | syllabus",
      "assessment": "exam | quiz | practice | submission | reading | project | presentation",
      "weight": "20% or null",
      "verification": {
        "source": "pva | micampus | none",
        "status": "confirmed | discrepancy | not_found | not_checked",
        "ref": "cmid:3704379",
        "note": "what the platform said"
      },
      "quote": "literal sentence that assigns the task"
    }
  ],
  "references": [
    {
      "type": "revisits | updates | resolves | depends | no_record",
      "to_class": "2026-09-02",
      "to_course": "only if the thread goes to another course",
      "to_topic": "title of the topic, copied from history",
      "to_item": "title of the item, copied from history",
      "quote": "literal sentence with which the professor leans on the previous class",
      "effect": "what changes: the new date, the answer, what it adds today"
    }
  ]
}
```

`from_professor` and `references` may be missing or come in empty. `items` can
also come in empty (a class with nothing to do exists), but the key is written
all the same: the empty list is the proof that somebody looked.

Each reference carries `to_topic` **or** `to_item`, not both, and the title is
copied exactly from `history`. The five types are in [threads](threads.md).

Rules the validator applies and that are not worth fighting:

- `quote` between 15 and 400 characters, literal in the normalized transcript,
  in every item, every topic, every `from_professor` entry and every reference.
- The only exception is `origin: platform`: it was not heard in class, and it
  pays its evidence with `source` `pva` or `micampus` and `verification.ref`.
- `personal` does not fit with `origin: platform`: his name is said in a
  classroom.
- Without `due.iso`, the `certainty` has to be `unknown`.
- `certainty: pva` requires `verification.source: pva`. `certainty: derived`
  requires `reason` or `expression`.
- A `discrepancy` requires `verification.note`.
- `type`, `source`, `origin`, `assessment`, `certainty` and the fields of
  `verification` are closed lists.

### Titles

The title is the only thing he is going to see in the Action View of Kino at
seven in the morning. A verb, a concrete object, without the name of the course
(that is already the folder) and without codes.

- Bad: "Practica 6", "ICC303 T06", "Tarea de la profe"
- Good: "Upload practice 6 of MPI to the PVA", "Read chapter 4 of Pacheco"

If two items from different classes end up with the same title, disambiguate
with the object, never with the date.
