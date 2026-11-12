# Probe

Find out what he really knows, not what he thinks he knows. What comes out of
here is a map with one piece of evidence per concept.

## Rules

- **Between 3 and 6 questions.** More than that is an exam, and he came to
  learn.
- **Start wide, then adapt.** The first question opens the whole topic ("tell
  me what happens when..."). The next ones depend on what he answered.
- **Never ask whether he knows something.** Self reporting is not evidence.
  Instead of "do you know what an index is?", ask him to use it: "you have a
  table with a million rows and a query that drags, what do you look at
  first?".
- **No yes or no.** A closed question leaves no evidence.
- **Ask for the confidence.** "are you saying that for sure, or is it a
  think-so?". A right answer with a "think-so" is a `shaky`, not a `knows`.
- **"No idea" is a valid answer** and it ends that branch without penalty. You
  thank him and move on.

## Classifying

Every concept falls into one of three states, and none of them exists without
the evidence that justifies it:

| State | When | Evidence that has to be saved |
|---|---|---|
| `knows` | He used it right in a case he had not seen | What he answered, in his words |
| `shaky` | He got it right while doubting, or got the definition right and failed the use | Where exactly it broke |
| `new` | It did not come up, or he said he does not know | That it did not come up in the probe |

Save every question with its answer using `record --type probe` and the
complete map with `map`. The map is rewritten whole every time it changes; it
is a snapshot, not a history.

## What a prerequisite branch is

Split the goal into the chains of things that have to be known first. Probe the
root of each chain, not the leaves: if he does not know what a probability is,
do not spend a question on the sigmoid.

When an answer reveals that something is missing much further down than you
expected, say it without dramatizing and go down there: that is the probe
working, not a problem.

## Output

- `map` with all the concepts you touched.
- One sentence for him with what you found, in the positive and without a long
  list: "you have the X part solid, what is missing is the bridge between X and
  Y".
