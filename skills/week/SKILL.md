---
name: week
description: Plans Elias's week by crossing what the university asks (MiCampus and the PVA) with what the projects need (Zoho) and his real energy windows (Kino), then writes the approved blocks to Kino.
disable-model-invocation: true
---

# The week

Build the week from the hours Elias really has, not from an ideal schedule.
Steps: bring the three sides (1), allocate by the rule (2), show the table (3),
and write to Kino only after his word (4).

## 1. Bring the three sides

**University**, with `mikampus`, in this order:

- `get_overview` first, always.
- `get_upcoming` and `get_pva_due` for what is due.
- `get_blockers` for what cannot be started.
- `get_schedule` for the hours already taken by class.
- `suggest_load` as a reference, not as a decision.

**Hard rule of the MCP:** what comes in `unknown` is unknown. Write it as "no
confirmed date" and ask Elias, or verify it on the platform, because an
invented date in a study plan is worse than having no plan. Look at
`freshness` too before affirming anything.

**Energy and tasks**, with the Kino MCP:

- `get_energy_windows` and `get_energy_distribution`: when he really performs.
- `get_today_plan` and `list_tasks` for what is already committed.
- `find_stale_systems` once a month, not every week.

**Product**: the open phases in Zoho, with `scrum`. Only what is in
progress or is next, not the whole backlog.

## 2. The allocation rule

- **What is due before next Monday wins**, always, even if it is boring.
- **The heavy thing goes in his best window.** Studying something new and
  designing compete for the same energy; reviewing a PR and answering email do
  not.
- **One block, one thing.** If a block has two topics, they are two blocks.
- **Plan below 100%.** A full day breaks with the first surprise; the margin is
  part of the plan, not what is left over.
- **What needs his hands or his accounts** (a console, the phone, a signature)
  is grouped into a single block of the week.

## 3. What gets delivered

A table per day, with the window, the block and where it came from:

| Day | Window | Block | Where it comes from | Due |
|---|---|---|---|---|

Below, three short lists:

- **What does not fit**, with what it would cost to fit it in (what leaves the
  plan in exchange). Name everything that was cut.
- **What is blocked** and by whom.
- **What is not known**: unconfirmed dates, assignments with no statement, what
  arrived in `unknown`.

## 4. The gate

Show the table and **wait for his word** before writing anything in Kino.
With his go-ahead: `schedule_task_block` or `propose_day_blocks` for the
blocks, and tell him how many were placed.

On Friday, the short loop back: which blocks were met, which were not and why.
That, and not Monday's intention, is what adjusts the following week.
