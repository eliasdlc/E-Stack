# Kino

How a class lands in Kino. None of this runs before the go ahead.

## Where each thing goes

| Thing of the class | Thing of Kino |
|---|---|
| The semester | A system of archetype `academic` |
| The course | A folder inside that system, with `metadata` `{professor, schedule, semester}` |
| The note of the day | A page in that folder |
| Each actionable item | A task in that folder, linked to the page |
| What the professor said about the course | Text in the page. `from_professor` does not create tasks |

The academic archetype calls the folder "class" and the page "note", and its
view is a timeline. That is why the due date is what orders everything: a task
without a `dueDate` disappears from the main view, and hence the buckets below
push to `week` instead of to `backlog` when the date is missing but the urgency
is not.

## Recognize the ground

```
list_systems                      -> the one with systemType academic
list_folders     systemId         -> does the folder of the course exist?
list_folder_tasks folderId        -> what is already there, so as not to duplicate
```

- **A single academic system**: that one is used, nothing is asked.
- **Several** (one system per semester, for instance): ask which one, once, and
  remember it in the report for next time.
- **None**: ask before creating a system. Creating a system is structural, it
  is not part of the go ahead of one class.
- **The folder of the course does not exist**: it is created without asking,
  with `professor` and `semester` from whatever is known. It is reversible and
  it is the natural place of the note.

## The order of writing

First the page, then the tasks, the links at the end. That way, if something
fails halfway, what is left is a complete note without tasks (recoverable with
the digest) and not loose tasks with no origin.

1. `create_page` with `systemId`, `folderId`, `title` and `content` in
   markdown. The title is `YYYY-MM-DD - <topic of the class>`. The shape of the
   content is in [note](note.md). The URL ends up as
   `https://www.usekino.dev/systems/<systemId>/pages/<pageId>`, and it is the
   one used in the links between notes.
2. `bulk_create_tasks` with all the items at once (maximum 50, a class never
   gets close). Each task carries its `clientRequestId`.
3. `link_task_to_page` for each created task, against the page of step 1.
4. The backward effects of the threads, if there are any. They go after the
   class on purpose: today's class stays whole even if a write over an old page
   fails with a conflict.
5. The memory of the course (below), after `mark-sent`, so it already counts
   this class.
6. The study plan of every exam ahead (below).
7. A forum draft for every forum item, per [forums](forums.md).

### The memory of the course

One page per course folder, titled `Memoria: <course>`. It is the fichero de
recuerdos: every rule the professor gave, every deliverable with what moved
it, every contradiction between the class and the PVA, the questions still
open and every topic seen, each line with the date of its class. Any agent
that plans, drafts or reminds for the course reads this page first.

```bash
python3 ~/dev/class-pipeline/class_session.py memory --course "<course>" --output /tmp/.../memoria.md
```

It is compiled from the digests, never written by hand, so it is replaced
whole: `get_folder_children` to find it, then `update_page` with its
`updatedAt` as `expectedUpdatedAt`, or `create_page` when it does not exist.
A `CONFLICT` means another run wrote it a moment ago: read it again and
replace it again, the content comes from the same digests.

### The material of the course

One page per course folder, titled `Material: <course>`: the PVA course page,
organized for studying, so that a course taught in a room with no recording
still has its material in one place. Built from `get_pva_section` (every
section of the course, in its order) and, for what a file covers,
`search_pva_files` and `get_pva_file` when the file is indexed.

- At the top, `Nuevo desde <fecha de la versión anterior>`: what appeared in
  the PVA since the page was last written, or "nada nuevo".
- One heading per PVA section, with its name as the PVA has it.
- Under it, each resource as a line: its name as a link to the PVA, its type,
  and one line on what it covers, from the file itself; a file that is not
  indexed says "sin leer" instead of a guess. When a class digest mentions it,
  the date of that class.
- Each activity (assignment, forum, quiz): name, due date and time, and the
  link to its Kino task when one exists.

Like the memory, it is replaced whole (`update_page` with `expectedUpdatedAt`,
or `create_page` the first time). Nothing is downloaded on purpose, submitted
or posted: the PVA is only read. The daily refresh visits the courses that
have at least one class in Kino; a course with none yet gets its pages the
first time `class_watch.py --refresh "<course>"` names it.

### The study plan

For every exam or quiz in the course folder (`taskType: event` with
`metadata.eventSubtype` `exam` or `quiz`) whose `dueDate` is still ahead:

```bash
python3 ~/dev/class-pipeline/class_session.py study-plan --course "<course>" \
  --exam "<exam title as in Kino>" --exam-id <its Kino task id> --exam-date <local day of the exam> \
  --since <local day of the previous exam, if any> --busy <day> --busy <day>
```

`--busy` is every day between today and the exam with any class block, of
any course, overlapping 19:00: `get_schedule` with `from` today and `to` the
exam day, since it shows a week by default. A session never lands on top of a
class. Each session comes with a `key` that its description carries as
`Clave del plan: <key>`, and a `legacyKey`. With `list_folder_tasks`, a task
whose description carries either one is the same session: `update_task` its
`title`, `dueDate` and `description` in place when they changed, which also
writes the new key. The rest are created with
`status` derived from the date, `taskType: task`, `priority: high`,
`energyLevel: high` and the `estimatedTime` the plan gives. Their due time is
what makes Kino remind: hours before, at the hour, and again until it is
closed. A session the plan no longer returns (the exam moved closer) is left
as it is; Elias closes or deletes it.

### The threads, in Kino

| reference type | What gets executed |
|---|---|
| `revisits`, `depends` | Nothing. The links live in the markdown of both pages |
| `updates` | `update_task` on the `taskId` that `history` brought. It changes `dueDate`, `description` or whatever moved. **Never** `create_task` |
| `resolves` | `complete_task` on the task of the question, and the answer into the markdown of both pages |
| `no_record` | A normal `question` item: "Process the class of \<date\>" |

To write on an old page: `get_page` first, and its `updatedAt` back in
`update_page` as `expectedUpdatedAt`. If it answers `CONFLICT`, read it again
and apply the change on top of the new content, never force it. The rules about
what can be touched are in [threads](threads.md).

If the class referred to never went up to Kino (`status: pending`, without
`taskId`), there is nothing backward to update: it is said in the report and
uploading that class first is offered.

### clientRequestId

`clientRequestId` has a unique index per user in Kino: it is the idempotency
key. If `bulk_create_tasks` fails halfway and is retried, the ones that already
went in do not get duplicated.

```bash
python3 ~/dev/class-pipeline/class_session.py ids <digest.json>
```

It returns a stable key per item, derived from course, date and title. **Do not
invent UUIDs by hand**: they are not stable between turns and the index stops
being useful.

## From bucket to task

| Bucket and case | `status` | `taskType` | `dueDate` | `priority` |
|---|---|---|---|---|
| `assignment` with a date | derived from `dueDate` | `task` | yes | `high` if 3 days or less are left, `medium` otherwise |
| `assignment` without a date | `backlog` | `task` | no | `medium` |
| `next_class` with a date | derived | `task` | yes | `medium` |
| `next_class` without a date | `week` | `task` | no | `medium` |
| `month` exam or quiz | derived | `event` + `metadata.eventSubtype` (`exam` or `quiz`) | yes | `critical` |
| `month` graded practice | derived | `event` + `eventSubtype: practice` | yes | `high` |
| `month` submission or project | derived | `task` | yes | `high` |
| `pending` already submitted according to the PVA | not created | | | |
| `pending` alive | `today` if the date already passed, derived otherwise | `task` | if there is one | `high` |
| `notice` that moves a day | derived | `event` | yes | `medium` |
| `notice` about a rule or criterion | no task is created, it goes to the page | | | |
| `problem` | `week` | `task` | if there is one | `high` |
| `question` | `week` | `task` | no | `low` |

Notes that are not obvious:

- **An exam, a quiz or a `next_class` on a day the course meets gets the
  start time of its class** from `get_schedule` (`2026-10-29T18:00:00-04:00`),
  not midnight. Kino counts its reminders to that moment; at midnight the
  last ones fall at night or after the class.
- **A `question` is a `task`, not a `reminder`.** Kino rejects a reminder
  without a due date, and a question almost never has one.
- **An `event` carries `startDate` too.** Kino rejects an event without it;
  for a one day notice it is the same instant as `dueDate`.
- **`next_class` without a date goes to `week`, not to `backlog`.** The day is
  not known but it is known to be before the next meeting, and in `backlog` he
  does not see it.
- **`personal: true` goes up a step**: `medium` becomes `high`, `high` becomes
  `critical`. What carries his name does not get lost among the group's, and
  the title still starts with the verb, without dressing it up.
- **A `pending` with an overdue date goes to `today`, not to the old date.** A
  late submission showing up with last month's date is seen by nobody.
- **A `notice` without a date creates nothing.** A change of criteria lives in
  the page, not in a task he is going to drag around forever.
- **`energyLevel`**: `high` for what demands reasoning (solving, programming,
  writing), `medium` for the rest. The academic archetype already uses `medium`
  by default, so it is only worth marking when it is `high`.
- **`estimatedTime`** only if the professor said how long it takes. It is not
  estimated for you.
- **`description`**: the `detail` of the item, below it the quote in quotation
  marks with the date of the class, and below that what the platform said. So
  that the task says on its own where it came from and against what it was
  verified:

  ```
  Answer the eight questions of chapter one.

  "El cuestionario lo suben a la plataforma para el lunes, en pdf"
  Class of September 9

  PVA cmid:3704379. Closes Monday the 14th at 10:00. No cutoff date.
  ```

  A `discrepancy` is written whole, with both versions and which one was used.
  An item with `verification.status: not_checked` says so, so that he knows
  that date is held up only by what was heard.

## Do not duplicate

Before creating, `list_folder_tasks` and compare. An existing task that matches
in title and `dueDate` **does not get created again**: it is reported as
already present. If the title matches but the date changed (the professor moved
the deliverable), `update_task` is done on the existing one and it is said in
the report.

A task Elias created by hand is never completed nor deleted.

## When Kino does not answer

It happens. A 404 with HTML instead of JSON means the connector is pointing at
routes the deployment no longer has; a 401 means the authorization expired and
the Kino connector has to be reconnected.

What gets done, in this order:

1. **One single retry**, no more. Do not hammer it.
2. The digest **stays at `pending`**. Nothing that was not created gets marked
   as sent.
3. Elias is told in one line that Kino did not answer and with what error, and
   the complete table is handed to him in the chat so he can decide.
4. When Kino comes back, `class_session.py list --pending` pulls out what was
   left hanging and it goes up without processing the transcript again.

What is not done: saving the note as an `.md` inside a repository, nor creating
a loose file "in the meantime". The digest is already that backup.

## The final report

A single batch, without a closing summary:

- How many tasks were created and how many already existed.
- **What carries his name**, apart, even if it already came out in the table.
- The discrepancies between what was heard and what the PVA publishes, with
  both dates.
- Which ones were left without a date, with the expression the professor said,
  so that he can set them.
- What was moved and what was closed from previous classes, with the old date
  and the new one.
- What has to be confirmed on the PVA or with the professor (the `question`
  items).
- The link of the page of the note.

And the record, so the thread stays auditable:

```bash
python3 ~/dev/class-pipeline/class_session.py mark-sent <digest> \
  --system <id> --folder <id> --page <id> \
  --task "<exact title of the item>=<uuid of the task>" \
  --updated <uuid> --completed <uuid>
```

The `title=uuid` pair is what lets the next class find this task with `history`
and move it instead of duplicating it. A title that is not in the digest makes
the command fail.
