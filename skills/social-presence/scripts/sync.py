#!/usr/bin/env python3
"""Mirror the social-presence working data between the laptop and agentbox, and nothing else.

Both machines write here: agentbox's scheduled runs write packs, pages, trends
and reviews, and Elias may paste his numbers in a session on either one. So the
mirror goes both ways and deletes nothing.

Only what the runs need crosses, named in MIRRORED: the profile, the tables,
the packs, the published phone pages, research, trends, reviews and the
harvest state. Everything else in the folder stays on the machine that wrote
it, because it can quote his own words: voice/ holds his raw texts, and a
plan such as a blind voice test shows them.

A conflict is settled per kind of file:

| File | When both sides changed it |
|---|---|
| ledger.csv, followers.csv | Every row either side has survives. A row both hold (ledger: date, platform, kind, url, first_line; followers: date, platform; a key repeated in one file pairs by its order) is merged field by field against the last merged copy, kept in `.sync-base/`: the side that changed a field since then wins it, so a correction sticks whichever file is newer. When both sides changed the same field, or there is no merged copy yet, the newer file wins it, except that a blank number there (empty, zero, or text `review.py` reads as zero) never erases a real one |
| leads.csv | No key: identical rows count up to the larger side |
| Everything else | The newer file wins whole (rsync `--update`) |

A table that does not parse (not UTF-8, or a row with more fields than its
header) is not merged and not mirrored; the run names it and the other files
still cross. A row removed on one side comes back from the other: remove it on
both. A file the mirror replaces with the other side's newer copy is kept next
to it as `<name>.replaced~`, which never crosses, so an overwritten edit can be
recovered on the machine where it was made.

    sync.py              # mirror with the other machine
    sync.py --dry-run    # print what would move, change nothing

Exit 0 when everything crossed, 1 when the other machine could not be reached,
rsync failed or a table was skipped (the local copy is always left usable).
"""
from __future__ import annotations

import argparse
import csv
import fcntl
import io
import os
import socket
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

DATA = Path.home() / "Documents/Personal/dev/social-presence"
PEERS = {"agentbox": "laptop", "decruces-omarchy": "agentbox"}
SSH = ["timeout", "120", "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10"]
LOCK = Path.home() / ".cache/social-presence-sync.lock"
KEYS: dict[str, tuple[str, ...] | None] = {
    "ledger.csv": ("date", "platform", "kind", "url", "first_line"),
    "followers.csv": ("date", "platform"),
    "leads.csv": None,
}
NUMBERS = {"impressions", "likes", "replies", "reposts", "profile_visits", "follows", "link_clicks", "followers"}
# rsync filter rules, first match wins: the allowlist, then everything else out.
MIRRORED = ["- *.replaced~", "- .*.sync-tmp", "+ /profile.json", *[f"+ /{name}" for name in KEYS], "+ /packs/", "+ /packs/*.md",
            "+ /plans/", "+ /plans/*-phone.html", "+ /research/", "+ /research/**", "+ /trends/",
            "+ /trends/**", "+ /reviews/", "+ /reviews/**", "+ /harvest/", "+ /harvest/**", "- *"]


BASE = ".sync-base"  # inside <data>, outside the allowlist: each machine's last merged copy of each table


class Malformed(ValueError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as err:
        raise Malformed(f"not UTF-8 (byte {err.start})") from None


def read_csv(text: str) -> tuple[list[str], list[dict]]:
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
    try:
        rows = list(reader)
    except csv.Error as err:
        raise Malformed(str(err)) from None
    for number, row in enumerate(rows, 2):
        if None in row:
            raise Malformed(f"line {number} has more fields than the header")
    return list(reader.fieldnames or []), rows


def keyed(rows: list[dict], key: tuple[str, ...] | None) -> list[tuple]:
    """The merge key of each row plus how many times that key was seen; without a key, the whole row."""
    seen: Counter = Counter()
    out = []
    for row in rows:
        k = tuple(row.get(c, "") for c in key) if key else tuple(sorted(row.items()))
        seen[k] += 1
        out.append((k, seen[k]))
    return out


def blank(value: str) -> bool:
    """Zero as review.py reads it: empty, 0, or anything that is not a plain number (n/a, -, 1.2k)."""
    try:
        return float((value or "0").replace(",", "")) == 0
    except ValueError:
        return True


def pick(newer: str, older: str) -> str:
    return older if blank(newer) and not blank(older) else newer


def merge_csv(newer: str, older: str, key: tuple[str, ...] | None, base: str | None = None) -> str:
    """Every row of both files, ordered by date; a row both hold is merged field by field.

    With `base` (the last merged copy) the side that changed a field since then wins it.
    Otherwise, or when both changed it, the newer file wins, except that its blank number
    never erases a real one.
    """
    new_head, new_rows = read_csv(newer)
    old_head, old_rows = read_csv(older)
    base_rows = read_csv(base)[1] if base else []
    head = new_head + [c for c in old_head if c not in new_head]
    new_index = dict(zip(keyed(new_rows, key), new_rows))
    old_index = dict(zip(keyed(old_rows, key), old_rows))
    base_index = dict(zip(keyed(base_rows, key), base_rows))
    rows = []
    for k in list(new_index) + [k for k in old_index if k not in new_index]:
        mine, theirs, before = new_index.get(k), old_index.get(k), base_index.get(k)
        if mine is None or theirs is None:
            rows.append(mine or theirs)
            continue
        row = {}
        for column in head:
            a, b = mine.get(column, ""), theirs.get(column, "")
            was = before.get(column, "") if before else None
            if a == b or (was is not None and b == was):
                row[column] = a
            elif was is not None and a == was:
                row[column] = b
            else:
                row[column] = pick(a, b) if column in NUMBERS else a
        rows.append(row)
    rows.sort(key=lambda r: r.get("date", ""))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=head, restval="", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def write_atomic(path: Path, text: str) -> None:
    tmp = path.with_name(f".{path.name}.sync-tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def ensure_remote(remote: str) -> bool:
    """Create the other side's folder, so the first mirror to a machine that never had it works."""
    host, sep, path = remote.partition(":")
    if not sep:
        Path(remote).mkdir(parents=True, exist_ok=True)
        return True
    return subprocess.run([*SSH, host, "mkdir", "-p", path], capture_output=True).returncode == 0


def merge_tables(local: Path, remote: str, dry_run: bool) -> tuple[bool, list[str], dict[str, str]]:
    """Fetch the other side's tables and write the merge here, so the push that follows carries it.

    Returns whether the fetch worked, the tables left out of this run, and the text each table
    will hold on both sides once the push lands (saved as the next base only then).
    """
    skipped, settled = [], {}
    with tempfile.TemporaryDirectory() as tmp:
        done = subprocess.run(["rsync", "-t", "--ignore-missing-args", *[remote + name for name in KEYS], tmp + "/"],
                              capture_output=True, text=True, env={**os.environ, "RSYNC_RSH": " ".join(SSH)})
        if done.returncode != 0:
            print(f"sync: could not read the other side's tables: {done.stderr.strip()[:200]}", file=sys.stderr)
            return False, skipped, settled
        for name, key in KEYS.items():
            theirs, mine, base = Path(tmp) / name, local / name, local / BASE / name
            if not theirs.exists() or not mine.exists():
                continue  # one side only: the rsync passes copy it untouched
            newer_mine = mine.stat().st_mtime >= theirs.stat().st_mtime
            try:
                their_text, my_text = read_text(theirs), read_text(mine)
                if their_text == my_text:
                    settled[name] = my_text
                    continue
                before = read_text(base) if base.exists() else None
                merged = merge_csv(*((my_text, their_text) if newer_mine else (their_text, my_text)), key, before)
            except Malformed as err:
                print(f"sync: {name} not merged, {err} on one side; fix it, it stays out of this run", file=sys.stderr)
                skipped.append(name)
                continue
            print(f"sync: merged {name}")
            settled[name] = merged
            if not dry_run:
                write_atomic(mine, merged)  # now the newest copy, so the push carries it
    return True, skipped, settled


def rsync(source: str, target: str, skipped: list[str], dry_run: bool) -> subprocess.CompletedProcess:
    rules = [f"- /{name}" for name in skipped] + MIRRORED
    flags = ["-a", "--update", "--mkpath", "--backup", "--suffix=.replaced~", *[f"--filter={rule}" for rule in rules],
             *(["--dry-run", "-v"] if dry_run else [])]
    return subprocess.run(["rsync", *flags, source, target], capture_output=True, text=True,
                          env={**os.environ, "RSYNC_RSH": " ".join(SSH)})


def sync(local: Path, remote: str, dry_run: bool = False) -> bool:
    """Merge the tables, then push and pull the allowlist; `remote` is an rsync spec ending in /."""
    if not dry_run:
        local.mkdir(parents=True, exist_ok=True)
    if not dry_run and not ensure_remote(remote):
        print("sync: the other machine could not be reached", file=sys.stderr)
        return False
    fetched, skipped, settled = merge_tables(local, remote, dry_run)
    if not fetched:
        return False
    ok = not skipped
    for source, target in [(f"{local}/", remote), (remote, f"{local}/")]:
        done = rsync(source, target, skipped, dry_run)
        if dry_run:
            print(done.stdout.strip())
        if done.returncode != 0:
            print(f"sync: rsync {source} -> {target} failed: {done.stderr.strip()[:200]}", file=sys.stderr)
            ok = False
    if ok and not dry_run:
        (local / BASE).mkdir(exist_ok=True)
        for name, text in settled.items():
            write_atomic(local / BASE / name, text)  # both sides now hold it
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--peer", default=PEERS.get(socket.gethostname()),
                        help="ssh host of the other machine (default from this host's name)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if not args.peer:
        print(f"sync: no peer known for {socket.gethostname()}; pass --peer", file=sys.stderr)
        return 2
    try:
        relative = args.data.resolve().relative_to(Path.home().resolve())
    except ValueError:
        print(f"sync: {args.data} is outside the home folder, the same path cannot exist on both", file=sys.stderr)
        return 2
    remote = f"{args.peer}:{relative}/"
    if args.dry_run:
        ok = sync(args.data, remote, dry_run=True)
    else:
        LOCK.parent.mkdir(parents=True, exist_ok=True)
        with LOCK.open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)  # the laptop timer and a session never mirror at once
            ok = sync(args.data, remote)
    print(f"sync with {args.peer}: {'done' if ok else 'incomplete, working from the local copy'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
