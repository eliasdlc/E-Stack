#!/usr/bin/env python3
"""Lints a visual-briefing page for what the T3 frame cannot do.

    python3 lint_page.py page.html [--standalone]

It reads the file and reports rules it can decide by looking at text: storage
and dialogs that fail inside the sandboxed frame, controls that claim to submit
or save a decision, viewport heights that make the frame grow without end, and
a page that ignores the host theme. It does not judge composition, copy or
whether the page was worth building. A clean run proves none of that.

--standalone is for a page opened outside T3: it needs its own light and dark
variables instead of the host's.
"""
from __future__ import annotations

import re
import sys

THEME_VARS = ("--background", "--foreground", "--border", "--muted", "--card", "--accent")

RULES = [
    ("viewport-height",
     re.compile(r"(?:min-|max-)?height\s*:\s*[^;}]*\d\s*(?:d|s|l)?vh|(?:html|body)\s*\{[^}]*height\s*:\s*100%", re.I),
     "viewport based height: the frame grows to fit the page, so it grows again and again"),
    ("storage",
     re.compile(r"\b(?:localStorage|sessionStorage|indexedDB)\b|document\.cookie"),
     "storage throws SecurityError inside the sandboxed frame"),
    ("dialog",
     re.compile(r"\b(?:alert|confirm|prompt)\s*\(|window\.open\s*\("),
     "dialogs and popups are blocked inside the frame"),
    ("submit-control",
     re.compile(r"<form\b|type\s*=\s*[\"']?submit", re.I),
     "a form or submit button sends nothing: the frame has no channel back to the agent"),
    ("saved-claim",
     re.compile(
         r"\b(?:saved|submitted|recorded|stored|guardad[oa]s?|enviad[oa]s?|registrad[oa]s?)\b"
         r"[^<>]{0,40}\b(?:choice|selection|decision|answer|approval|elecci[oó]n|respuesta|decisi[oó]n)"
         r"|\b(?:choice|selection|decision|answer|approval|elecci[oó]n|respuesta|decisi[oó]n)\w*\b"
         r"[^<>]{0,20}\b(?:saved|submitted|recorded|stored|guardad[oa]s?|enviad[oa]s?|registrad[oa]s?)\b",
         re.I),
     "the page says a decision was saved: nothing counts as chosen until he types it in the chat"),
    ("em-dash", re.compile(chr(0x2014)), "em dash: use a comma, colon, period or parentheses"),
]


def lint(html: str, standalone: bool = False) -> list[tuple[str, int, str]]:
    found = []
    for rule, pattern, message in RULES:
        for hit in pattern.finditer(html):
            found.append((rule, html.count("\n", 0, hit.start()) + 1, message))
    if standalone:
        if "prefers-color-scheme" not in html:
            found.append(("standalone-theme", 1, "a standalone page needs light and dark behind prefers-color-scheme"))
    elif not any(f"var({name}" in html for name in THEME_VARS):
        found.append(("theme-variables", 1, "no host theme variable is used: the page will not follow light and dark in the thread"))
    return sorted(found, key=lambda f: f[1])


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    with open(args[0], encoding="utf-8") as handle:
        problems = lint(handle.read(), standalone="--standalone" in sys.argv)
    for rule, line, message in problems:
        print(f"{args[0]}:{line}: {rule}: {message}")
    print("clean" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
