# The note

The page that stays in Kino. It is written for the Elias of three weeks from
now, who does not remember the class and has an exam on Tuesday.

Clean markdown, no emojis, no decorative bold. Kino renders it.

## The shape

```markdown
# <Topic of the class>

<Course> - <long date> - <professor>

Comes from: [<date> - <topic>](<url of the previous page>)
You need first: [<date> - <topic>](<url>)

<One sentence: what it was about and what it is for inside the course.>

## What is on me

- [ ] <what they asked him for by name> - <date or "not confirmed">

## What has to be understood

### <Concept>

<The reasoning, two or three short paragraphs. What problem it solves, how it
works, and why it is done this way and not the other.>

Confused with: <the similar one, and the difference in one line.>
You know it when: <the concrete thing you would have to be able to do.>
The professor underlined: <only if there is a `from_professor` entry about this concept.>

> <literal quote from the professor>

## How the professor grades

- <criterion, required format, what gets penalized, what was repeated three times>

## Threads

- Revisits [<topic> (<date>)](<url>): <what today's class adds on top of that>
- Resolves [<question> (<date>)](<url>): <the answer, complete>
- Moves [<task> (<date>)](<url>): from <old date> to <new date>
- The class of <date> is not processed, <topic> was covered there

## What has to be done

- [ ] <title of the item> - due <date or "not confirmed">
- [ ] ...

## For the next class

- [ ] ...

## Of the month

- <evaluation> - <date> - <weight if it was said>

## Carryovers

- [ ] <what came from before and is still alive> - was due <old date>

## Notices

- <the change> - <from when it applies>

## Problems

- <what is stuck> - solved by <the professor | the PVA | the group | him>

## Not confirmed

- <what was left open and who has to be asked>

## To test yourself

1. <question>
2. ...

## Mentioned in class

- <chapter, paper, PVA document, tool>

---

Verified against the PVA on <date>. <what the platform corrected or added.>
```

Empty sections **are not written**. A class without evaluations of the month
does not carry an "Of the month: none", and the first class of a course does
not carry "Comes from" nor "Threads".

"What is on me" goes above everything, even before the concepts, and it only
exists if they said his name. It is the only thing from a class nobody else is
going to remind him of.

Every due line the PVA confirmed carries its date plain; one that only the
transcript holds up says "according to what was said in class"; a discrepancy
carries both and which one was used. The last line of the note says when it was
verified, or that mikampus did not answer.

The header lines (`Comes from`, `You need first`) are for the threads that
frame the whole class. The **Threads** section is for everything else, and it
goes after the concepts on purpose: first you understand what is from today,
then you see how it fits with what came before.

## What gets written in the old note

A thread also leaves a mark backward. Only add or strike through, never rewrite
the page, and always say where the change comes from:

```markdown
Continues in [<date> - <topic of today>](<url>)

~~Due Friday September 4~~ Moved to Monday the 8th, said in the
[class of September 4](<url>)

Resolved in the [class of September 4](<url>): <the answer>
```

The mechanics of that write (read first, `expectedUpdatedAt`, what to do on a
conflict) are in [threads](threads.md).

## The three lines of each concept

It is what separates a note from an index.

- **The reasoning.** Not the definition. "Reduce combines one piece of data
  from all the processes into a single one" is a definition. What is useful is
  why it exists: because joining partial results by hand forces every process
  to send its chunk to zero, and zero becomes the bottleneck.
- **Confused with.** Almost every concept of a class has a neighbor it gets
  mixed up with on the exam. Naming it now saves the mistake later.
- **You know it when.** An action, not a feeling. "You know it when you can
  decide which of the two to use by looking at the code", not "when you have it
  clear".

If the transcript does not give enough for the three, write the ones it does
and the hole turns into a `question`. Filling it in with your own knowledge of
the topic is the easiest way to make him study something his professor did not
teach.

## Self assessment

Between four and six questions, in the order the class went. They are exam
questions, not review questions:

- Bad: "What is broadcast?"
- Good: "Every process computed the sum of its chunk of the array. Which
  primitive do you use to have the total in all of them, and why not two
  calls?"

The answers **do not go in the page**. If he wants to work on them, that is
`/teach`, which probes before explaining.

## Title of the page

`YYYY-MM-DD - <topic of the class>`. The date first because in the list of
notes of the folder the chronological order is the one he looks for.
