---
name: notebook
description: Debugs and teaches Jupyter notebooks for Elias's data classes without seeing his kernel. Runs a copy of the .ipynb top to bottom in a fresh kernel, names the first failing cell with its error, detects cells he ran out of order, and tells him exactly which cells to rerun; or guides him cell by cell so he writes and runs the code himself. Use for "el notebook me da error", "me da error al final", "revisa el notebook", "celda", "kernel", ".ipynb", "Jupyter", "paso por paso en el notebook", "explicamelo como a un nino", scikit-learn or pandas exercises in a notebook, in English or Spanish. Not for plain Python scripts.
---

# Notebook

The agent cannot see his kernel: only the saved `.ipynb`. On 14 Oct a failure
took three turns because the fix was tested in a copy while his kernel still
carried a skipped cell. So the first move is always to run a copy the way a
fresh kernel would, and to tell him what to rerun in his.

## Debug: run a copy first

```bash
python3 scripts/run_copy.py "/path/to/notebook.ipynb" [--timeout 300]
```

It copies the notebook's folder (data files resolve the same way), runs every
code cell in a fresh kernel with plots off-screen, never touches the original,
and prints:

| Line | What to tell him |
|---|---|
| `FAILS at cell N of M: <Error>: <message>` | The real bug, with the cell number as Jupyter counts code cells. Fix it in his file, then rerun it in a copy until `OK` |
| `OK: all M code cells ran in order` | The code is fine; his kernel state is the problem |
| `saved notebook ran out of order at cells ...` | He ran or re-ran cells out of sequence; values in his kernel are not what the file says |
| `in his kernel: Kernel > Restart, then run cells 1 to N` | The exact instruction to give him, in one line |

Edit the notebook with the notebook tools, keep his cell order and outputs,
and run `run_copy.py` again after the fix. A fix that only passed in your copy
is not done until he reruns the cells it names.

## Learn: one cell at a time

When he asks to learn ("paso por paso lo que tengo que hacer en el notebook en
blanco", "explicamelo como que soy un nino"):

1. One cell per step, in the order the class uses: imports, load, explore,
   split, model, evaluate.
2. For each: the code, what each line does in plain words, and the output he
   should see. He types it and runs it.
3. Name the function's documentation page when it helps (`help(...)` or the
   scikit-learn page), and define every term the first time (cross validation,
   MAE, precision).
4. Stop after each step only when its output matters to the next; otherwise
   keep going.

For deeper study he can open `/teach`.

## A notebook handed in as the deliverable

A notebook that is the graded deliverable is not an informe, so it carries no
references and no academic register, because the rubric grades the analysis and
not the prose. Write a short note after each result, enough for the analysis
the rubric grades, and code comments only where they help. The code takes the
correct, simple route. Tools beyond what was seen in class are fine, and the
closing message names which ones were used, because he has to explain every
line.
<!-- 25 Oct 2026, BI Practica 2: "tampoco tienes que citar nada en el notebook, esto no es un informe". -->
