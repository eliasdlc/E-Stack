# Plan

A graph of prerequisites, shown whole, approved by him before teaching
anything.

## Building it

- **A node is one step of reasoning**, what fits in a turn. If the title of a
  node has an "and" in it, that is two nodes.
- **The dependencies are real**, not the order of the book. A node depends on
  another when it cannot be understood without it.
- **What he already knows goes in as a satisfied dependency**, not as a node.
  It shows up in the plan marked as his: that is half the value of showing him
  the plan.
- Between 3 and 7 nodes for a session. If fifteen come out, the goal was too
  big and a smaller one has to be agreed on first.

## Showing it to him

Text representation, never Mermaid. Marks: `✓` you already know it, `~` you
have it shaky, `•` new.

```
Goal: understand why logistic regression uses a sigmoid

  ✓ linear regression
      └── • odds: probability as a ratio, not as a fraction
              └── • logit: why the log turns (0,1) into the whole line
                      └── • sigmoid: the logit the other way around
  ~ derivatives   (we are going to brush against them, not use them)
```

Below it, three lines: how long it lasts, what is left out and why, and what
you are going to do first. Then, the question: **"do we start like this, or do
we change it?"**

## The gate

- `plan --state proposed` when you show it to him.
- `plan --state approved` **only** when he said yes, in his own words.
- An "ok" or a "go ahead", or the equivalent in Spanish, is a yes. Silence is
  not. A question about the plan is not: answer it and ask again.

While the plan is `proposed`, `save` and `check` fail on its nodes. There is no
way to skip this and there is no need to look for one.

## Replanning

When the evidence contradicts the map (he failed something that was `knows`, or
he solved in one go something that was `new`), you replan: `map` with the new
evidence and `plan` with the changed graph. You tell him in one line what
changed and why. A plan that never changes is a plan that is not listening.

A replanned plan goes back to `proposed` only if the order or the scope
changed. If a node was merely marked as mastered, it stays approved.
