#!/usr/bin/env python3
"""Collect what Elias wrote himself, so the voice guide is built from his words.

Sources: his messages in Claude Code session logs (dictated, typos kept) and
the notes of his Obsidian vaults. Agent-written text that reaches the log as a
user turn (thread briefs, handoffs, pasted documents, tool echoes, skill bodies)
is filtered out, because a voice learned from it would be the agent's.

The corpus is private: it is written outside Git, to the data folder the skill
names, and only the distilled guide enters the repository.

    voice_corpus.py --out ~/Documents/Personal/dev/social-presence/voice/corpus.jsonl
    voice_corpus.py --out FILE --since 2026-06-01 --vault ~/Documents/Personal/Life
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

HOME = pathlib.Path.home()
PROJECTS = HOME / ".claude/projects"

# Openings of user turns that a harness or an agent wrote, not him.
MACHINE_OPENINGS = (
    "<", "Caveat:", "[Request interrupted", "This session is being continued",
    "Base directory for this skill", "Continue from where you left off",
    "Stop hook feedback", "[Image", "API Error",
)
# A third-person mention of him, a Markdown heading or a fenced block means an
# agent wrote the brief; he dictates plain sentences.
AGENT_MARKS = re.compile(r"\bElias\b|^#{1,6} |^```|^\| .* \|$|^\s*- \[[ x]\]", re.M)
# Orchestration traffic between agents: commit hashes, tool names, watcher notices.
ORCHESTRATION = re.compile(r"\b[0-9a-f]{10,}\b|mcp__|T3 Code (is|keeps) watching|\bexit ?0\b|Responde solo con", re.I)
PASTED = re.compile(r"<pasted_content[^>]*>.*?</pasted_content[^>]*>", re.S)
TAGS = re.compile(r"<(system-reminder|command-[a-z]+|local-command-[a-z]+)>.*?</\1>", re.S)
SPANISH = re.compile(r"\b(que|de|la|el|los|las|para|con|pero|porque|esto|eso|hazme|quiero|tambien|también|necesito|ponle|dale|vaina|klk|ta)\b", re.I)
ENGLISH = re.compile(r"\b(the|and|with|this|that|want|make|should|please|because|it's|don't)\b", re.I)

MIN_CHARS, MAX_CHARS = 20, 1500


def language(text: str) -> str:
    es, en = len(SPANISH.findall(text)), len(ENGLISH.findall(text))
    if es and en and min(es, en) / max(es, en) > 0.4:
        return "mixed"
    return "es" if es >= en else "en"


def clean(text: str) -> str | None:
    """The message as he typed it, or None when it is not his."""
    text = TAGS.sub("", PASTED.sub("", text)).strip()
    if not (MIN_CHARS <= len(text) <= MAX_CHARS):
        return None
    if text.startswith(MACHINE_OPENINGS) or AGENT_MARKS.search(text) or ORCHESTRATION.search(text):
        return None
    lines = [ln for ln in text.splitlines() if ln.strip()]
    # Many bullet lines read as a plan an agent drafted; he dictates in prose.
    if sum(ln.lstrip().startswith(("- ", "* ", "1.", "2.")) for ln in lines) > 2:
        return None
    return text


def message_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        if any(isinstance(p, dict) and p.get("type") == "tool_result" for p in content):
            return ""
        return "\n".join(p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text")
    return ""


def from_sessions(since: str):
    """Yield (timestamp, text) for his turns, scanning the logs as text first so a
    17 GB tree is not parsed line by line in full."""
    for path in sorted(PROJECTS.glob("**/*.jsonl")):
        if "/subagents/" in str(path):
            continue
        try:
            handle = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with handle:
            for line in handle:
                if '"type":"user"' not in line or '"isSidechain":true' in line or '"tool_result"' in line:
                    continue
                if '"isMeta":true' in line or '"kind":"task-notification"' in line or '"promptSource":"system"' in line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                stamp = record.get("timestamp", "")
                if stamp[:10] < since:
                    continue
                text = clean(message_text(record.get("message", {}).get("content")))
                if text:
                    yield stamp, text


def from_vault(vault: pathlib.Path):
    """Yield (mtime date, paragraph) from his notes; templates and attachments are skipped."""
    for note in sorted(vault.glob("**/*.md")):
        if any(part.startswith(".") or part.lower().startswith(("plantilla", "template")) for part in note.parts):
            continue
        try:
            body = note.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        body = re.sub(r"^---\n.*?\n---\n", "", body, flags=re.S)
        stamp = str(note.stat().st_mtime)
        for paragraph in re.split(r"\n\s*\n", body):
            paragraph = paragraph.strip()
            if paragraph.startswith(("#", "|", "```", "![", "- [")) or "http" in paragraph[:12]:
                continue
            if MIN_CHARS * 2 <= len(paragraph) <= MAX_CHARS:
                yield stamp, paragraph


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, type=pathlib.Path)
    parser.add_argument("--since", default="2000-01-01", help="ISO date; older session turns are skipped")
    parser.add_argument("--vault", action="append", type=pathlib.Path, default=[])
    args = parser.parse_args()

    out = args.out.expanduser()
    if pathlib.Path(__file__).resolve().parents[3] in out.resolve().parents:
        print("refusing: the corpus is private and stays outside the repository", file=sys.stderr)
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    counts = {"session": 0, "vault": 0, "es": 0, "en": 0, "mixed": 0}
    with out.open("w", encoding="utf-8") as sink:
        sources = [("session", from_sessions(args.since))] + [("vault", from_vault(v.expanduser())) for v in args.vault]
        for source, rows in sources:
            for stamp, text in rows:
                key = hashlib.sha1(text.lower().encode()).hexdigest()
                if key in seen:
                    continue
                seen.add(key)
                lang = language(text)
                counts[source] += 1
                counts[lang] += 1
                sink.write(json.dumps({"source": source, "at": stamp, "lang": lang, "text": text}, ensure_ascii=False) + "\n")
    print(json.dumps({"out": str(out), **counts}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
