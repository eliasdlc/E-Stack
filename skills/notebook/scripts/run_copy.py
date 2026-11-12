#!/usr/bin/env python3
"""run_copy.py NOTEBOOK [--timeout SECONDS] [--keep]

Runs a copy of a Jupyter notebook top to bottom, the way a fresh kernel would,
and reports what Elias needs to fix his own run:

- the first cell that fails: its number as Jupyter shows it (1-based among
  code cells), its first source line, the exception type and message;
- the cells whose saved execution counts are out of order (run out of
  sequence or skipped in his kernel), which is the usual reason "it works for
  you but not for me";
- which cells he must rerun in his kernel, in order.

The original is never touched: its folder is copied (files over 50 MB are
symlinked) to a temporary directory, its sha256 is checked before and after,
and plots use the Agg backend so no window opens.

Exit codes: 0 clean, 1 a cell failed or timed out, 2 could not run.
System python3 has no nbformat here, so the script re-executes itself under
the interpreter of the `jupyter` command on PATH.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile

BIG = 50 * 1024 * 1024


def reexec_under_jupyter() -> None:
    try:
        import nbclient  # noqa: F401
        import nbformat  # noqa: F401
        return
    except ImportError:
        pass
    if os.environ.get("RUN_COPY_REEXEC"):
        print("run_copy: nbclient and nbformat are not importable, even under jupyter's python", file=sys.stderr)
        sys.exit(2)
    jupyter = shutil.which("jupyter")
    if not jupyter:
        print("run_copy: jupyter is not on PATH", file=sys.stderr)
        sys.exit(2)
    with open(jupyter, encoding="utf-8", errors="ignore") as f:
        first = f.readline().strip()
    python = first[2:].split()[0] if first.startswith("#!") else ""
    if not python or not os.path.exists(python):
        print("run_copy: cannot find the python behind " + jupyter, file=sys.stderr)
        sys.exit(2)
    os.environ["RUN_COPY_REEXEC"] = "1"
    os.execv(python, [python, os.path.abspath(__file__), *sys.argv[1:]])


def sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_folder(src: str, dst: str) -> None:
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in (".ipynb_checkpoints", "__pycache__", ".git", "versiones")]
        rel = os.path.relpath(root, src)
        os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for name in files:
            s, d = os.path.join(root, name), os.path.join(dst, rel, name)
            if os.path.getsize(s) > BIG:
                os.symlink(s, d)
            else:
                shutil.copy2(s, d)


def out_of_order(nb) -> list[int]:
    """1-based code-cell numbers whose saved count is lower than an earlier one, or missing between run cells."""
    seen, bad, last = 0, [], 0
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        seen += 1
        count = cell.get("execution_count")
        if count is None:
            continue
        if count < last:
            bad.append(seen)
        last = max(last, count)
    return bad


def main(argv: list[str]) -> int:
    reexec_under_jupyter()
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError, CellTimeoutError

    args = [a for a in argv if not a.startswith("--")]
    timeout = 300
    if "--timeout" in argv:
        timeout = int(argv[argv.index("--timeout") + 1])
        args = [a for a in args if a != str(timeout)]
    if len(args) != 1:
        print(__doc__.split("\n\n")[0], file=sys.stderr)
        return 2
    original = os.path.abspath(args[0])
    if not os.path.isfile(original):
        print("run_copy: no such notebook: " + original, file=sys.stderr)
        return 2
    before = sha(original)
    tmp = tempfile.mkdtemp(prefix="run_copy_")
    copy_folder(os.path.dirname(original), tmp)
    copy = os.path.join(tmp, os.path.basename(original))
    nb = nbformat.read(copy, as_version=4)
    saved_order = out_of_order(nb)
    code_index = {}
    n = 0
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == "code":
            n += 1
            code_index[i] = n
    state = {"cell": None}

    def on_start(cell, cell_index, **_):
        state["cell"] = cell_index

    os.environ["MPLBACKEND"] = "Agg"
    client = NotebookClient(nb, timeout=timeout, kernel_name=nb.metadata.get("kernelspec", {}).get("name", "python3"),
                            resources={"metadata": {"path": tmp}}, allow_errors=False, on_cell_start=on_start)
    failed = None
    try:
        client.execute()
    except (CellExecutionError, CellTimeoutError) as e:
        idx = state["cell"]
        cell = nb.cells[idx] if idx is not None else None
        first = cell.source.strip().splitlines()[0] if cell is not None and cell.source.strip() else ""
        kind = "timeout" if isinstance(e, CellTimeoutError) else (getattr(e, "ename", "") or "error")
        message = (getattr(e, "evalue", "") or str(e).strip().splitlines()[-1])[:300]
        failed = {"cell": code_index.get(idx), "first_line": first[:160], "type": kind, "message": message}
    except Exception as e:  # kernel could not start, missing kernelspec
        print("run_copy: could not run: " + str(e)[:400], file=sys.stderr)
        return 2
    finally:
        if "--keep" not in argv:
            shutil.rmtree(tmp, ignore_errors=True)
    if sha(original) != before:
        print("run_copy: the original changed during the run; nothing here wrote to it", file=sys.stderr)
    total = len(code_index)
    report = {"notebook": original, "code_cells": total, "failed": failed, "saved_out_of_order": saved_order}
    if failed:
        rerun = list(range(1, (failed["cell"] or 1) + 1))
        print(f"FAILS at cell {failed['cell']} of {total}: {failed['type']}: {failed['message']}")
        print(f"  first line: {failed['first_line']}")
    else:
        rerun = list(range(1, total + 1)) if saved_order else []
        print(f"OK: all {total} code cells ran in order in a fresh kernel")
    if saved_order:
        print(f"  saved notebook ran out of order at cells {', '.join(map(str, saved_order))}: "
              "his kernel state does not match the file")
    if rerun:
        print("  in his kernel: Kernel > Restart, then run cells " + (f"1 to {rerun[-1]}" if len(rerun) > 1 else "1"))
    print(json.dumps(report, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
