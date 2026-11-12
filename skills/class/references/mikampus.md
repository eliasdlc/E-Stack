# The cross check with mikampus

The transcript knows what was said out loud. The platform knows what was left
written. Until the two are crossed, half of what comes out of a class is a half
finished date.

Verified on 11 sep 2026 by calling the tools: **this already exists and
answers**. The step is not optional, and it is only skipped when the server
does not reply.

## Two platforms, two truths

| Server | What it is | Tools |
|---|---|---|
| MiCampus | The PeopleSoft of PUCMM: transcript, enrollment, schedule, official grades | `get_overview`, `get_cycle`, `get_schedule`, `get_academics`, `get_upcoming`, `find_courses` |
| PVA | The Moodle of the classroom: assignments, submissions, material, announcements, the professor's gradebook | `get_pva_courses`, `get_pva_due`, `get_pva_assignment`, `get_pva_section`, `get_pva_announcements`, `search_pva_files`, `get_pva_file`, `get_pva_grades` |

The classroom grade and the transcript grade **are not the same**, and mixing
them is the classic mistake. `get_pva_grades` is what the professor keeps in
Moodle; `get_academics` is what counts toward the GPA.

mikampus is **read only**. It changes nothing in the portal, it does not upload
a submission, it does not mark anything as done.

## The envelope of each response

Every response carries `asOf`, `data`, `freshness`, `warnings` and `unknown`.
Before asserting anything with it, look at the last three:

- **`unknown`** is what is not known. It is not estimated, not filled in, not
  interpreted. It comes out in the report as what has to be confirmed.
- **`freshness`** says when each thing was synced. With `stale: true` or
  `neverSynced: true`, the data **does not win over the transcript**: what was
  heard is used and it is said in one line that the platform is old, with the
  minutes.
- **`warnings`** changes the reading. Two real ones that show up often:
  `pva_modulos_sin_acceso` (there is material the PVA declares and this user
  cannot see, so "it does not show up" does not mean "it does not exist") and
  `pva_eventos_ausentes` (something stopped coming in the feed, and that does
  not prove it was submitted).

## The bridge between the two

MiCampus and the PVA **do not share an identifier**, and that is the real
friction of the cross check:

| MiCampus | PVA |
|---|---|
| `courseCode` `ICC-321`, `title` "Inteligencia de Negocios" | `shortname` `CSTI-1930-5227`, `fullname` "CSTI-1930-5227 - Inteligencia de Negocios" |

The bridge is built in two steps:

1. **The cycle**, which is the middle segment of the shortname. The `term` that
   `get_schedule` returns (`1930`) is the same `1930` of `CSTI-1930-5227`. That
   immediately rules out the courses of old cycles, which keep showing up in
   `get_pva_courses`.
2. **The name**, folded and abbreviated. The PVA truncates ("Seg. en Tecnologia
   Informacion" against "Seguridad Tecnologias Informacion", "Desarrollo de
   Aplicac. Moviles" against "Desarrollo de Aplicaciones Moviles"). Compare by
   words, not by equality.

If two courses of the cycle tie, **ask which one it is**, once, and note it in
the report. A cross check against the wrong course puts another class's
deliverable in this one's folder.

## The cross check, item by item

It goes between resolving dates and saving. Every item comes out with its
`verification` set, including `not_checked` when there was nothing to check.

| Bucket | What gets called | What is done with the answer |
|---|---|---|
| `assignment`, `month` with `source: pva` | `get_pva_assignment` by `query` with the title | `dueAt` to `certainty: pva`; `intro` to the `detail`; `gradeMax` to the `weight` if it is greater than zero; `submission.status` says whether it is already done |
| `pending` | `get_pva_assignment` | If `submission.status` is not `new`, **it was already submitted**: no task is created, it is reported as closed |
| `next_class` without a date | `get_schedule` from the date of the class | The next occurrence of that course is the date. `certainty: derived`, `reason` "schedule of the course according to mikampus" |
| `question` about downloading material | `get_pva_section` or `search_pva_files` | If the file exists, the question closes and a task to read it is left, with the real name |
| `question` about content | `get_pva_file` | What the document says closes the question. The text comes out in parts: while it carries `nextOffset`, keep going |
| `notice` | `get_pva_announcements` | Confirms that it was left written. The content of the announcement **cannot be read yet**: that goes to `unknown` |
| `problem` about grades | `get_pva_grades` of the course, and `get_academics` if it is from the transcript | The real number, saying which of the two is being looked at |
| Any | `get_pva_due --days 30` | What is due and was **not** mentioned in class comes in as a new item with `origin: platform` |

### The dates come in UTC

`dueAt` and `opensAt` are UTC. The Dominican Republic is UTC-4 all year, so a
close at `02:00Z` on Tuesday is due **Monday at ten at night**. Copying the UTC
day into Kino moves the submission a whole day.

```bash
python3 ~/dev/class-pipeline/class_session.py pva-date "2026-09-15T02:00:00.000Z"
```

`get_pva_due` already brings `localDay` resolved; `get_pva_assignment` does
not, and that is where the error slips in.

### What the PVA publishes and is not what it looks like

- **`gradeMax: 0`** is not "it is worth zero": it is that the weight was not
  published. The `weight` keeps what was said in class, or null.
- **`cutoffAt: null`** means it accepts late submissions indefinitely, and it
  comes out in the warning `pva_sin_corte`. It does not make the date optional,
  but it changes what gets done if it already passed.
- **The calendar only publishes what is pending.** A submission already done
  disappears from the `get_pva_due` feed. Something not being there does not
  prove it was submitted: the assignment says that, with `submission`.
- **`matches`** with several options means the title was ambiguous. Look at the
  list and pick by course, never grab the first one.

## The precedence rule

They do not compete: each source wins in its own domain.

| Data | Wins |
|---|---|
| Due date, closing time, published weight, submission status | **The PVA**. It is written and it is what gets graded |
| What has to be done, with what criteria, what the professor wants | **The transcript**. In class what is not written is said |
| Schedule, room, professor, cycle | **MiCampus** |
| Official grade | **MiCampus**. The classroom one is the professor's and does not have to match |
| Existence of the assignment | Either. If it is in one and not in the other, it exists, and where it came from is marked |

The precedence falls apart when the source that wins is `stale` or inside
`unknown`. There the other one wins, and it is said.

## A disagreement is never resolved in silence

If the professor said Thursday and the PVA says Friday, the task goes with the
PVA date, `verification.status: discrepancy` and a `note` with both versions.
The validator requires that note. In the gate table it comes out with both
dates visible, because sometimes the PVA is the one that is out of date and he
is the one who decides.

## What the cross check unblocks

- "Para la proxima clase" stops being `unknown`.
- The course, the professor and the cycle are not asked: they come from
  `get_schedule` and `get_cycle`, and the Kino folder is created complete
  instead of with N/D.
- Assignments that exist and were never named in class show up all the same.
- A carryover that was already submitted does not turn into a phantom task.

## When mikampus does not answer

It is not assumed to be running. It is checked with `get_overview` and, if it
fails:

1. One single retry.
2. The flow **goes on** with what was heard. Every item stays at
   `verification.status: not_checked`.
3. It is said in one line, before the table, that the verification did not run
   and against what the dates were left.

A cross check that could not be done is information. An invented cross check is
a false date with a platform stamp, which is worse than having no date.

## What is not done

- Credentials through the chat. They go to the mikampus vault, and if one is
  needed, ask him to put it in `~/.config/secrets/mikampus.env`.
- Writing to the PVA. Uploading a submission is on his hands, always.
- Marking something as submitted because it disappeared from the calendar.
- Treating the classroom grade as the transcript grade.
