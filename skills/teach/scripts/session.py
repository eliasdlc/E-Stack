#!/usr/bin/env python3
"""Memory of a learning session, and the gates the process cannot skip.

The pedagogy lives in SKILL.md. Here there is only what cannot depend on the
tutor remembering: where the session is saved, that an unapproved plan does not
get taught, and that a node is not closed because the learner recognized the
answer.

A session is a markdown file a person can open and correct by hand. The file is
the state: there is no database and no service behind it.

    # Topic
    > Learning session - v1 - <sessionId>
    ## Now          what to attend to
    ## Why          why this step matters
    ## Next         the next action, a single one
    ## Checkpoint   the state in JSON, which is what gets resumed
    ## Log          what happened, and it only grows

The first four sections are rewritten whole on save. The log only receives new
entries. The map, the plan and the checks live inside the log as marked
entries, so there is no extra section that can get lost.

Every command spits JSON on stdout. A failure goes out on stderr with code 1
and explains what is missing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path

LEVELS = ("knows", "shaky", "new")
CHECK_TYPES = ("recognize", "explain", "transfer")
CONFIDENCES = ("sure", "think-so", "no-idea")
VERDICTS = ("correct", "partial", "incorrect", "dont-know")
NODE_STATES = ("pending", "teaching", "mastered")
PLAN_STATES = ("proposed", "approved")
ENTRY_TYPES = ("probe", "teach", "note", "parked")

NOW, WHY, NEXT, CHECKPOINT, LOG = "Now", "Why", "Next", "Checkpoint", "Log"
MARK_MAP, MARK_PLAN, MARK_PARKED, MARK_CHECK = "**Map**", "**Plan**", "**Parked**", "**Check**"

JSON_BLOCK = re.compile(r"```json\s*\n([\s\S]*?)\n```")
HEADING = re.compile(r"^### (probe|teach|check|note) - (\S+)$")


class Failure(Exception):
    """What the tutor has to fix before going on."""


def root() -> Path:
    return Path(os.environ.get("TUTOR_SESSIONS", Path.home() / "Documents/Universidad/Aprendizaje/sessions"))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def slug(text: str) -> str:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    clean = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")
    return (clean or "session")[:60]


def files() -> list[Path]:
    return sorted(root().glob("*.md")) if root().exists() else []


def resolve(reference: str) -> Path:
    """Accepts a path, the file name, or the topic written any which way."""
    candidate = Path(reference).expanduser()
    if candidate.suffix == ".md" and candidate.exists():
        return candidate
    for option in (root() / f"{reference}.md", root() / f"{slug(reference)}.md"):
        if option.exists():
            return option
    target = slug(reference)
    partials = [p for p in files() if target in p.stem or p.stem in target]
    if len(partials) == 1:
        return partials[0]
    open_ones = ", ".join(p.stem for p in files()) or "none"
    raise Failure(f"I cannot find the session «{reference}». Open sessions: {open_ones}.")


# --- sections -----------------------------------------------------------------

def bounds(lines: list[str], heading: str) -> tuple[int, int]:
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == f"## {heading}")
    except StopIteration:
        raise Failure(f'This document is not a learning session: it is missing the "{heading}" section.')
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return start, end


def replace_section(markdown: str, heading: str, body: str) -> str:
    lines = markdown.split("\n")
    start, end = bounds(lines, heading)
    return "\n".join(lines[:start] + [f"## {heading}", "", body.strip(), ""] + lines[end:])


def block(value: object) -> str:
    return "```json\n" + json.dumps(value, indent=2, ensure_ascii=False) + "\n```"


# --- checkpoint ---------------------------------------------------------------

def build_checkpoint(session_id: str, args: argparse.Namespace) -> dict:
    minutes = int(args.minutes)
    if not 1 <= minutes <= 90:
        raise Failure("The minutes of the next block have to be between 1 and 90.")
    return {
        "schemaVersion": 1,
        "sessionId": session_id,
        "currentNodeId": args.node,
        "lastUnderstood": args.understood,
        "openQuestion": args.open_question or None,
        "nextAction": args.next,
        "suggestedMinutes": minutes,
        "learnerStateUpdatedAt": now_iso(),
    }


def read_checkpoint(markdown: str) -> dict:
    lines = markdown.split("\n")
    start, end = bounds(lines, CHECKPOINT)
    found = JSON_BLOCK.search("\n".join(lines[start:end]))
    if not found:
        raise Failure('The "Checkpoint" section has no JSON block: the session cannot be resumed.')
    try:
        value = json.loads(found.group(1))
    except json.JSONDecodeError:
        raise Failure("The checkpoint is not valid JSON. Open it and fix it by hand, or tell Elias what broke.")
    if value.get("schemaVersion") != 1:
        raise Failure("The checkpoint has a format version this tutor does not know.")
    return value


# --- document -----------------------------------------------------------------

def render(topic: str, now: str, why: str, checkpoint: dict) -> str:
    return "\n".join([
        f"# {topic.strip()}", "",
        f"> Learning session - v1 - {checkpoint['sessionId']}", "",
        f"## {NOW}", "", now.strip(), "",
        f"## {WHY}", "", why.strip(), "",
        f"## {NEXT}", "", checkpoint["nextAction"].strip(), "",
        f"## {CHECKPOINT}", "", block(checkpoint), "",
        f"## {LOG}", "",
    ])


def append_entry(markdown: str, kind: str, content: str, at: str) -> str:
    """Goes in at the end of the log, not of the file: whatever is written after that is still his."""
    lines = markdown.split("\n")
    _, end = bounds(lines, LOG)
    body, tail = lines[:end], lines[end:]
    while body and not body[-1].strip():
        body.pop()
    return "\n".join(body + ["", f"### {kind} - {at}", "", content.strip(), ""] + tail)


def entries(markdown: str) -> list[dict]:
    lines = markdown.split("\n")
    start, end = bounds(lines, LOG)
    log: list[dict] = []
    for line in lines[start + 1:end]:
        heading = HEADING.match(line.strip())
        if heading:
            log.append({"kind": heading.group(1), "at": heading.group(2), "content": []})
        elif log:
            log[-1]["content"].append(line)
    for entry in log:
        entry["content"] = "\n".join(entry["content"]).strip()
    return log


def last_block(log: list[dict], mark: str) -> dict | None:
    for entry in reversed(log):
        if entry["content"].startswith(mark):
            found = JSON_BLOCK.search(entry["content"])
            if found:
                return json.loads(found.group(1))
    return None


class Session:
    """The document already parsed. Everything the tutor needs to see at once."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.markdown = path.read_text(encoding="utf-8")
        self.entries = entries(self.markdown)
        self.checkpoint = read_checkpoint(self.markdown)
        self.topic = self.markdown.split("\n", 1)[0].lstrip("# ").strip()
        saved_map = last_block(self.entries, MARK_MAP)
        self.map: list[dict] = saved_map["concepts"] if saved_map else []
        self.plan = last_block(self.entries, MARK_PLAN)
        self.checks = [
            json.loads(JSON_BLOCK.search(e["content"]).group(1))  # type: ignore[union-attr]
            for e in self.entries
            if e["kind"] == "check" and e["content"].startswith(MARK_CHECK) and JSON_BLOCK.search(e["content"])
        ]
        self.parked = [
            e["content"][len(MARK_PARKED):].lstrip(" :\n")
            for e in self.entries
            if e["content"].startswith(MARK_PARKED)
        ]

    def save(self, markdown: str) -> None:
        self.path.write_text(markdown, encoding="utf-8")
        self.__init__(self.path)  # type: ignore[misc]

    def already_knows(self, concept_id: str) -> bool:
        return any(c["id"] == concept_id and c["state"] == "knows" for c in self.map)

    def next_node(self) -> dict | None:
        """The first pending node whose dependencies are mastered or were already known."""
        if not self.plan:
            return None
        mastered = {n["id"] for n in self.plan["nodes"] if n["state"] == "mastered"}
        ready = lambda i: i in mastered or self.already_knows(i)  # noqa: E731
        for node in self.plan["nodes"]:
            if node["state"] != "mastered" and all(ready(d) for d in node["dependsOn"]):
                return node
        return None

    def missing_to_master(self, node: str) -> list[dict]:
        """Recognizing well is not mastering. The log checks it, not the impression of the conversation."""
        own = [c for c in self.checks if c["node"] == node]
        missing = []
        for kind in ("explain", "transfer"):
            if any(c["type"] == kind and c["verdict"] == "correct" for c in own):
                continue
            attempts = len([c for c in own if c["type"] == kind])
            missing.append({
                "type": kind,
                "reason": f"there is no {kind} check at all" if attempts == 0
                else f"the {attempts} {kind} check(s) did not come out correct",
            })
        return missing

    def require_approved_plan(self, node: str) -> None:
        """The gate between Plan and Teaching."""
        if not self.plan or self.plan["state"] == "approved":
            return
        if not any(n["id"] == node for n in self.plan["nodes"]):
            return
        raise Failure(
            f"The plan is proposed, not approved, and «{node}» is one of its nodes. Show him the whole plan, "
            "ask him whether we start like this, and save his answer with `plan --state approved` before teaching."
        )

    def view(self) -> dict:
        return {
            "session": str(self.path),
            "topic": self.topic,
            "checkpoint": self.checkpoint,
            "map": self.map,
            "plan": self.plan,
            "nextNode": self.next_node(),
            "missingInThisNode": self.missing_to_master(self.checkpoint["currentNodeId"]),
            "parked": self.parked,
            "checks": len(self.checks),
        }


def input_of(args: argparse.Namespace, field: str) -> str:
    value = getattr(args, field)
    return sys.stdin.read() if value == "-" else value


def respond(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


# --- commands -----------------------------------------------------------------

def cmd_list(_args: argparse.Namespace) -> None:
    sessions = []
    for path in files():
        try:
            s = Session(path)
        except Failure:
            continue  # a half written file does not block the list
        sessions.append({
            "session": path.stem,
            "topic": s.topic,
            "nextAction": s.checkpoint["nextAction"],
            "suggestedMinutes": s.checkpoint["suggestedMinutes"],
            "openQuestion": s.checkpoint["openQuestion"],
            "updatedAt": s.checkpoint["learnerStateUpdatedAt"],
        })
    sessions.sort(key=lambda s: s["updatedAt"], reverse=True)
    respond({"root": str(root()), "sessions": sessions})


def cmd_open(args: argparse.Namespace) -> None:
    root().mkdir(parents=True, exist_ok=True)
    path = root() / f"{slug(args.topic)}.md"
    if path.exists():
        raise Failure(f"There is already a session about this in {path}. Resume it with `read` instead of opening another one.")
    checkpoint = build_checkpoint(str(uuid.uuid4()), args)
    path.write_text(render(args.topic, args.now, args.why, checkpoint), encoding="utf-8")
    respond(Session(path).view())


def cmd_read(args: argparse.Namespace) -> None:
    s = Session(resolve(args.session))
    respond({**s.view(), "latest": s.entries[-args.entries:] if args.entries else []})


def cmd_save(args: argparse.Namespace) -> None:
    s = Session(resolve(args.session))
    s.require_approved_plan(args.node)
    checkpoint = build_checkpoint(s.checkpoint["sessionId"], args)
    output = replace_section(s.markdown, NOW, args.now)
    output = replace_section(output, WHY, args.why)
    output = replace_section(output, NEXT, checkpoint["nextAction"])
    s.save(replace_section(output, CHECKPOINT, block(checkpoint)))
    respond(s.view())


def cmd_record(args: argparse.Namespace) -> None:
    s = Session(resolve(args.session))
    content = input_of(args, "content")
    kind = "note" if args.type == "parked" else args.type
    body = f"{MARK_PARKED}: {content.strip()}" if args.type == "parked" else content
    s.save(append_entry(s.markdown, kind, body, now_iso()))
    extra = {"resumingAt": {"node": s.checkpoint["currentNodeId"], "next": s.checkpoint["nextAction"]}} if args.type == "parked" else {}
    respond({"recorded": args.type, **extra, "parked": s.parked})


def cmd_map(args: argparse.Namespace) -> None:
    s = Session(resolve(args.session))
    concepts = json.loads(input_of(args, "concepts"))
    if not concepts:
        raise Failure("An empty map says nothing. Classify at least one concept.")
    for concept in concepts:
        missing = {"id", "name", "state", "evidence"} - set(concept)
        if missing:
            raise Failure(f"Concept {concept.get('id', '?')} is missing fields: {', '.join(sorted(missing))}.")
        if concept["state"] not in LEVELS:
            raise Failure(f"State «{concept['state']}» is invalid. Use: {', '.join(LEVELS)}.")
        if not str(concept["evidence"]).strip():
            raise Failure(f"«{concept['id']}» has no evidence. Without evidence it is not a classification, it is a guess.")
    s.save(append_entry(s.markdown, "note", f"{MARK_MAP}\n\n{block({'concepts': concepts})}", now_iso()))
    respond({"map": s.map, "nextNode": s.next_node()})


def cmd_plan(args: argparse.Namespace) -> None:
    s = Session(resolve(args.session))
    nodes = json.loads(input_of(args, "nodes"))
    ids = {n["id"] for n in nodes}
    for node in nodes:
        if node.get("state") not in NODE_STATES:
            raise Failure(f"Node «{node.get('id', '?')}» needs a state: {', '.join(NODE_STATES)}.")
        for dependency in node["dependsOn"]:
            if dependency not in ids and not s.already_knows(dependency):
                raise Failure(
                    f"Node «{node['id']}» depends on «{dependency}», which is neither in the plan nor in the map "
                    "as something he already knows."
                )
    plan = {"goal": args.goal, "nodes": nodes, "state": args.state}
    s.save(append_entry(s.markdown, "note", f"{MARK_PLAN}\n\n{block(plan)}", now_iso()))
    respond({"plan": s.plan, "nextNode": s.next_node()})


def cmd_check(args: argparse.Namespace) -> None:
    s = Session(resolve(args.session))
    s.require_approved_plan(args.node)
    check = {
        "node": args.node,
        "type": args.type,
        "question": args.question,
        "answer": args.answer,
        "confidence": args.confidence,
        "verdict": args.verdict,
    }
    if args.note:
        check["note"] = args.note
    summary = f"{MARK_CHECK} node:{args.node} - {args.type} - {args.verdict} - confidence:{args.confidence}"
    s.save(append_entry(s.markdown, "check", f"{summary}\n\n{block(check)}", now_iso()))
    respond({"recorded": True, "missingInThisNode": s.missing_to_master(args.node)})


def cmd_master(args: argparse.Namespace) -> None:
    s = Session(resolve(args.session))
    if not s.plan:
        raise Failure("There is no plan yet: there is no node to close.")
    if s.plan["state"] != "approved":
        raise Failure("The plan is not approved. A node of a plan he did not approve does not get closed.")
    if not any(n["id"] == args.node for n in s.plan["nodes"]):
        raise Failure(f"«{args.node}» is not a node of the plan. Nodes: {', '.join(n['id'] for n in s.plan['nodes'])}.")
    missing = s.missing_to_master(args.node)
    if missing:
        detail = "; ".join(f"{f['type']} ({f['reason']})" for f in missing)
        raise Failure(f"«{args.node}» is not mastered yet: {detail}. Check that before moving on.")
    plan = {
        **s.plan,
        "nodes": [{**n, "state": "mastered"} if n["id"] == args.node else n for n in s.plan["nodes"]],
    }
    s.save(append_entry(s.markdown, "note", f"{MARK_PLAN}\n\n{block(plan)}", now_iso()))
    respond({"mastered": args.node, "nextNode": s.next_node(), "plan": s.plan})


def cmd_export(args: argparse.Namespace) -> None:
    sys.stdout.write(resolve(args.session).read_text(encoding="utf-8"))


def state_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--now", required=True, help="What the learner should attend to from now on")
    parser.add_argument("--why", required=True, help="Why that step matters")
    parser.add_argument("--node", required=True, help="Id of the plan node. Before the plan, a free id")
    parser.add_argument("--understood", required=True, help="The last thing he showed he understood, in his words")
    parser.add_argument("--next", required=True, help="A single concrete action to pick it back up")
    parser.add_argument("--minutes", required=True, type=int, help="Length of the next block, 1 to 90")
    parser.add_argument("--open-question", default=None, help="The question left open, if any was left")


def main() -> None:
    parser = argparse.ArgumentParser(description="Learning sessions of the tutor")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="The open sessions, the most recent one first").set_defaults(func=cmd_list)

    opened = sub.add_parser("open", help="Opens a new session, after the probe")
    opened.add_argument("--topic", required=True)
    state_args(opened)
    opened.set_defaults(func=cmd_open)

    read = sub.add_parser("read", help="Checkpoint, map, plan, next node and what is parked")
    read.add_argument("--session", required=True)
    read.add_argument("--entries", type=int, default=6)
    read.set_defaults(func=cmd_read)

    save = sub.add_parser("save", help="Saves where the session was left")
    save.add_argument("--session", required=True)
    state_args(save)
    save.set_defaults(func=cmd_save)

    record = sub.add_parser("record", help="Adds an entry to the log")
    record.add_argument("--session", required=True)
    record.add_argument("--type", required=True, choices=ENTRY_TYPES)
    record.add_argument("--content", default="-", help="Markdown, or - to read from stdin")
    record.set_defaults(func=cmd_record)

    concept_map = sub.add_parser("map", help="What he knows, what is shaky and what is new, with evidence")
    concept_map.add_argument("--session", required=True)
    concept_map.add_argument("--concepts", default="-", help="JSON [{id,name,state,evidence}], or - for stdin")
    concept_map.set_defaults(func=cmd_map)

    plan = sub.add_parser("plan", help="The prerequisite graph, proposed or approved")
    plan.add_argument("--session", required=True)
    plan.add_argument("--goal", required=True)
    plan.add_argument("--state", required=True, choices=PLAN_STATES)
    plan.add_argument("--nodes", default="-", help="JSON [{id,title,dependsOn,state}], or - for stdin")
    plan.set_defaults(func=cmd_plan)

    check = sub.add_parser("check", help="Records a check with his real answer")
    check.add_argument("--session", required=True)
    check.add_argument("--node", required=True)
    check.add_argument("--type", required=True, choices=CHECK_TYPES)
    check.add_argument("--question", required=True)
    check.add_argument("--answer", required=True, help="What he answered, literally")
    check.add_argument("--confidence", required=True, choices=CONFIDENCES)
    check.add_argument("--verdict", required=True, choices=VERDICTS)
    check.add_argument("--note", default=None, help="What the answer reveals: the missing premise, the confusion")
    check.set_defaults(func=cmd_check)

    master = sub.add_parser("master", help="Closes a node and returns the next unblocked one")
    master.add_argument("--session", required=True)
    master.add_argument("--node", required=True)
    master.set_defaults(func=cmd_master)

    export = sub.add_parser("export", help="Spits out the markdown as it is")
    export.add_argument("--session", required=True)
    export.set_defaults(func=cmd_export)

    args = parser.parse_args()
    try:
        args.func(args)
    except Failure as failure:
        print(str(failure), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
