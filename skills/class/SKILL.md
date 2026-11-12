---
name: class
description: Turns the recording or the transcript of a class into study notes and tasks in Kino, with every date cross checked against MiCampus and the PVA.
disable-model-invocation: true
---

# From the class to the note and to the tasks

Three rules carry the skill.

1. **Extract only what was said.** If the professor said "traten de darle una
   mirada al capitulo cuatro", Kino gets exactly that, not "Read chapter 4,
   due Thursday, 10%". A date nobody said is worse than no date at all,
   because it gets believed.
2. **Empty the class whole, in this pass.** Nobody listens to the recording
   again, so the carryover she named in passing, the notice that there is no
   class on Monday and the time the professor said his name all come out now.
3. **Write a note for studying.** A list of topics ("we covered MPI, we
   covered broadcast") is not a note. The note carries the reasoning: what
   problem each thing solves, what it gets confused with, and what he would
   have to be able to do to say he understood it.

The flow has eight steps: place the class, normalize, extract, resolve dates,
verify against mikampus, save and show the table, the gate, Kino.

The student is Elias. Dominican Spanish, technical terms in English, plain and
direct: no emojis, no empty cheering.

## The evidence contract

**Every extracted thing carries the literal quote from the transcript.** Not a
paraphrase: the words that were said. No quote, no item, no topic, no thread.

This does not depend on your good will. `class_session.py save --transcript`
folds the quote and the transcript (no accents, no punctuation, no double
spaces) and checks that the quote is inside. If it is not, the command fails
and names the item. A digest with an invented assignment does not get saved.

There is **one single exception**: an assignment the PVA publishes that nobody
mentioned in class. That one comes in with `origin: platform` and pays its
evidence with the id mikampus returned, not with a quote.

What is on you: the quote has to be the sentence that **assigns**, not one that
mentions the topic. "El parcial cubre memoria compartida" assigns nothing.

## The seven buckets

Everything actionable in a class falls into one. The `type` of each item.

| type | What it is | Signal in the transcript |
|---|---|---|
| `assignment` | A new deliverable, almost always through the PVA | "suben a la PVA", "me entregan", "para el jueves" |
| `next_class` | What has to be known or brought to the next meeting | "para la proxima clase", "vengan habiendo leido" |
| `month` | Big evaluations and deliverables of the period | "el parcial es", "el proyecto final", "la exposicion" |
| `pending` | Something from before that is still alive and the professor named again | "recuerden que", "los que no han subido" |
| `notice` | Changes his calendar or the rules, without being a deliverable | "el lunes no hay clase", "cambiamos de aula", "les corri todo" |
| `problem` | Something stuck that costs him a grade or time | "eso no se subio", "el grupo no entrego", "no tengo acceso" |
| `question` | Left open and has to be confirmed | an unanswered question, a date the professor will confirm |

Crossing the seven, a boolean: **`personal: true` when they said his name**.
"Elias, tu traes el caso" and "Elias, a ti te falto la practica" are different
things to do, and both have to be seen apart from the rest.

The bucket is decided by **when it has to be acted on**, not by size. An
assignment that is also an evaluation of the month goes in `month`, not in both.

And two things that are not items: the **topics** (the note) and **what the professor
said about the course** (criteria, what shows up on the exam, how it is graded),
which go to `from_professor` and live in the page.

## The flow

Eight steps. The seventh is a gate he opens.

### 1. Place the class and open the thread

Three pieces of data are needed: **course**, **date of the class** and
**professor**. They almost never have to be asked:

```
get_overview        -> the degree, the cycle, the enrolled courses
get_schedule        -> day, time, room and professor of each course
get_pva_courses     -> the same course from the Moodle side
```

With the date and time of the recording, `get_schedule` says which class it
was. Ask whatever mikampus does not return **in a single message**, all
together. The bridge between the MiCampus code (`ICC-321`) and the PVA
shortname (`CSTI-1930-5227`) is in [mikampus](references/mikampus.md), and it
is not obvious.

The date of the class is the anchor of every relative date. If it is today's,
say so and move on; if the class was last Tuesday, "para el jueves" means
something else.

```bash
S=~/dev/class-pipeline/class_session.py
python3 $S list                                          # already processed?
python3 $S history --course "<course>" --before <date>   # the thread of the course
```

`history` brings what was covered in previous classes, with the Kino `taskId`s,
and the `open` list with the questions, the carryovers and the problems that
were never closed. **It is loaded before reading the transcript**, because
without it "acuerdense de lo de la semana pasada" is noise. The full doctrine
is in [threads](references/threads.md).

### 2. Normalize

```bash
python3 $S normalize <file> --output /tmp/.../clean-class.txt
```

It reads `.vtt`, `.srt`, `.txt`, `.md`, `.json` (Whisper exports), `.docx` and
`.pdf`. It strips timestamps, cue numbers and the repeated lines of rolling
subtitles, and joins each speaking turn into a paragraph. A one hour VTT loses
close to half its weight here.

If what there is is **audio or video**, this skill does not transcribe: say it
in one line and ask for the text. If he pasted the transcript in the chat,
write it to a file in the scratchpad and normalize that one.

Read the clean text **whole**. An hour and a half class is about 12 thousand
words: it fits. What is actionable is almost always in the last five minutes
and in the first minute, but the reasoning of the note, the notices and the
times they said his name are spread through the middle.

### 3. Extract everything

Four things come out: the **topics** (the note), the **items** (what is
actionable, in their seven buckets), **`from_professor`** (criteria and
emphasis) and the **references** (the threads backward).

The detail is in [extraction](references/extraction.md): what falls into each
bucket, the border between a carryover and an update, what to do with what a
classmate said, when to mark `personal`, and the bar for the summary. For the
references, [threads](references/threads.md).

With the `open` list from `history` in front of you, the question in every
stretch is triple: does this assign something new?, does this close or move
something old?, does this carry his name?

### 4. Resolve dates

Compute every date with the script:

```bash
python3 $S dates --anchor <date-of-the-class> "para el jueves" "en dos semanas"
```

It returns `iso` and `certainty`:

| certainty | What it means |
|---|---|
| `explicit` | The professor said the date or the day |
| `derived` | The professor said it in relative terms, or it came from the schedule, and the script counted |
| `pva` | The date is published by the platform, which is what gets graded |
| `unknown` | It depends on something nobody said. It shows up in the list of what has to be confirmed |

"Para la proxima clase" comes out `unknown` from this step and almost always
stops being so in the next one.

### 5. Verify against mikampus

**Run this step every time.** What was heard is one version; what the
platform publishes is what gets graded. Every item leaves here with its `verification`
set, even when it says `not_checked`.

```
get_pva_assignment  -> the real closing date, the weight, whether it is submitted
get_pva_due         -> what is due and nobody mentioned in class
get_pva_section     -> the material the professor said was uploaded
get_pva_file        -> what that material says, to close a question
get_schedule        -> turns "la proxima clase" into a date
get_pva_grades      -> the classroom grade, which is not the transcript one
```

The rules needed before touching a tool are in
[mikampus](references/mikampus.md): the `freshness` / `warnings` / `unknown`
envelope and what to do with each one, the bridge between the two platforms,
the precedence table, and the detail that dates come in UTC.

That last one bites: a close at `02:00Z` on Tuesday is due **Monday at ten at
night** here.

```bash
python3 $S pva-date "2026-09-15T02:00:00.000Z"
```

A disagreement between what was heard and what the PVA publishes is **always
shown**: the PVA wins, `verification.status` stays at
`discrepancy`, and both versions come out in the table. If mikampus does not
answer, the flow goes on with what was heard and it is said in one line.

### 6. Save and show the table

```bash
python3 $S save --json <digest.json> --transcript <original-file>
```

The format of the digest is in [extraction](references/extraction.md). If the
command fails, fix the digest and run it again.

After that, **a single table in the chat**, grouped by bucket, with columns:
title, course, date (or "not confirmed" with the expression that was said),
where the date came from, evaluation, and weight if it was mentioned. Below it,
and in this order:

1. **What carries his name**, apart, even if it is already in the table.
2. **The discrepancies**, with both dates and which one was used.
3. How many items were left without a date and what has to be confirmed.
4. If there are references, the **Threads** section: one line per thread,
   saying which task moves and from which date to which date, which question
   closes. Format in [threads](references/threads.md).

The threads go **before** the gate: moving a deliverable and closing a question
are writes over what already exists, and he has to see them before authorizing.

### 7. The gate, when he is there

**He asked for it and is reading: write to Kino only after his go ahead**,
the page and every task alike. The table is shown and you wait. "Go
ahead", "all good", "green", "upload that", or the equivalent in Spanish, is the
authorization.

If he corrects an item (a date, a title, one that does not belong), the digest
is corrected, `save` is run again and the table is shown again. The correction
does not open a new digest.

**An automatic run has no gate.** The prompt that starts it says so, and it
comes from `class_watch.py`, the timer that picks up a transcript nobody
asked about. Write the page and the tasks, and close with a short paragraph
instead of the table, because nobody is reading a chat.

The automatic run keeps every other rule, and that is the whole reason it can
be left alone: the guard against an invented date lives in
`class_session.py save`, not in his attention. A class where nothing was
assigned writes no task, and a date nobody said leaves the task in `backlog`.

### 8. Kino

With the green light, the order and the exact mapping are in
[kino](references/kino.md): academic system, folder of the class, page of the
note, tasks per bucket, the priority step up for the ones that carry his name,
the link of each task with the page, the backward effects of each thread, the
memory page of the course, its material page from the PVA, and the study plan
of every exam ahead.
When done:

```bash
python3 $S mark-sent <digest> --system <id> --folder <id> --page <id> \
  --task "<title>=<uuid>" --updated <uuid> --completed <uuid>
```

And the report in the chat: how many tasks, what carries his name, the
discrepancies, which ones were left in `backlog` for lack of a date, what was
moved and what was closed from previous classes, and the link of the page.

## What gets asked and what does not

- **Gets asked**, in a single message: whatever mikampus does not return and
  cannot be deduced; which of two courses of the cycle it is, if the name
  matches both; and which Kino system the class goes to if more than one is
  possible.
- **Does not get asked**: the course, the professor or the schedule before
  calling mikampus; how to word a title; whether a reading is an assignment or
  preparation (the bucket decides that); nor permission to go on after the gate.
  Decide those yourself.
- **Gets flagged and you move on**: anything left as a `question`. A question
  does not block the rest of the flow.

## The rules

- Every date rests on a said expression or a platform record. Without one the
  task goes to `backlog`, which beats an invented date.
- Every percentage, chapter, page and platform name comes from the transcript
  or from the mikampus response.
- Every PVA date goes through `pva-date`, since the platform returns UTC.
- Every discrepancy is shown, and mikampus data that falls into `unknown` stays
  unknown.
- Write to Kino after the gate, when there is a gate. An automatic run does not
  have one; everything else on this list still holds. The PVA stays read only:
  uploading a submission is on his hands.
- Process each class once: `list` first. If it really has to be redone, update
  the existing page and tasks in place.
- The note lives in Kino, and the digest in
  `~/Documents/Universidad/Aprendizaje/classes/`, outside every repository.
- Summarize only stretches that contribute a concept, an assignment or a
  notice; what the professor told about their weekend stays out.
- Open a backward thread only from a sentence of hers, and that sentence is the
  quote; topical resemblance opens nothing.
- A deliverable that moved gets **updated** in place. Two practice fives in
  Kino is worse than none.
- A carryover the PVA considers submitted stays out of the tasks.

## The timer that runs it alone

`~/dev/class-pipeline/class_watch.py` looks at `~/Downloads` and at where the mikampus sweep
leaves what it takes from Teams, at 13:45, 16:45, 21:45 and 23:30. Each sweep
asks Teams for the last three days, because Teams can publish a transcript a
day or more after the class. A transcript that is under twelve hours old on
disk and has no copy next to a digest is handed to a headless agent with this
skill and no gate.

Two things the watcher cannot do, and how each one is covered. It cannot see a
class that left no transcript: `class_watch.py --nightly` runs at 23:41 and names
the blocks of the day that produced nothing. The day is named: from 23:00 on
it is today, earlier it is yesterday, so a closed laptop that catches the run
up the next morning or afternoon checks the day it missed and never today's
unfinished blocks. On the machine with the Kino token each such block becomes a
task, «Clase sin grabación: <materia>, <AAAA-MM-DD>», in the course folder,
saying where to drop a recording or how to note the class; a same-title task
already done is not recreated, and a block the course memory calls
asynchronous gets none. The in-person classes (Móviles, Gestión de Proyectos)
are what it catches. Every run finds `claude` by its install path when the unit
has no PATH, which is the case for a Persistent timer at session boot. And it cannot tell a broken
transcript from a hard one, so a file whose run failed is not retried until the
file itself changes, or one broken file becomes a hundred agent runs in a day.

The watcher, `class_session.py` and the units live in the private repository
`eliasdlc/class-pipeline`, cloned at `~/dev/class-pipeline/` on both machines;
the units are copied from its `systemd/` by hand, once per machine, and its
README says how. The agents installer owns none of them.
agentbox runs the pass, because it stays on and sweeps Teams itself; the
laptop's timer fires twenty minutes later and only works when agentbox could
not. Whichever machine holds the Kino token sends the digests still pending,
so a class agentbox read but could not write reaches Kino from the laptop.

## Resources

- [`references/extraction.md`](references/extraction.md) the seven buckets, the
  `personal` mark, `from_professor`, the bar for the summary and the format of
  the digest.
- [`references/mikampus.md`](references/mikampus.md) the cross check with
  MiCampus and the PVA: which tool answers what, the envelope of each response,
  the bridge between the two platforms, the precedence and the dates in UTC.
- [`references/threads.md`](references/threads.md) the crossings between classes
  of one course: how they are recognized, what each type does, and how to write
  backward without breaking the old page.
- [`references/kino.md`](references/kino.md) the mapping to Kino, the order of
  writing and what to do when the MCP does not answer.
- [`references/note.md`](references/note.md) the shape of the study page.
- [`references/automation.md`](references/automation.md) who writes to Kino,
  the 07:10 review run and what automatic runs cannot touch.
- [`references/forums.md`](references/forums.md) the forum draft: what is read, what the page carries, and that nothing is posted.
- `~/dev/class-pipeline/class_session.py` `normalize`, `dates`,
  `pva-date`, `save`, `history`, `ids`, `list`, `read`, `mark-sent`, and the two
  that feed Kino after each class: `memory` (the page of the course) and
  `study-plan` (the sessions before each exam).
- [`references/history.md`](references/history.md) the decisions behind the
  automatic run; read it only when changing the skill.
