#!/usr/bin/env python3
"""Flag the tells that make a draft read as written by an AI, before Elias sees it.

Deterministic: every rule is a pattern with a name, so a finding says which
rule fired and on what words. It checks English and Spanish, because he posts
in both. A draft that passes can still sound wrong; one that fails reads as AI
to anyone who has scrolled X in 2026.

    lint.py draft.txt                    # lint the whole file as one post
    lint.py --platform x draft.txt       # also enforce the 280 character limit
    lint.py pack.md                      # in Markdown, only ```post blocks are linted
    echo "text" | lint.py -

A Markdown file is linted block by block: a fenced block whose info string
starts with `post` is a draft (```post x, ```post linkedin, ```post reply x),
and everything outside those blocks (context, links, notes) is ignored. Inside
an X block a line with only `---` separates the posts of a thread.

Exit 0 when nothing fired, 1 when something did, 2 on a usage error.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EM_DASH, MIDDLE_DOT, EN_DASH = chr(0x2014), chr(0x00B7), chr(0x2013)
X_LIMIT = 280
X_URL_WEIGHT = 23  # X counts every link as 23 characters, whatever its length.
URL = re.compile(r"https?://\S+")
EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\U0001F900-\U0001F9FF⭐⭕‼⁉✅❌]"
)


@dataclass(frozen=True)
class Rule:
    id: str
    why: str
    pattern: re.Pattern


def words(*phrases: str) -> re.Pattern:
    """Case-insensitive alternation of whole phrases."""
    body = "|".join(re.escape(p).replace(r"\ ", r"\s+") for p in phrases)
    return re.compile(rf"(?<![\w-])(?:{body})(?![\w-])", re.I)


RULES: tuple[Rule, ...] = (
    Rule("em-dash", "Elias bans the em dash everywhere; rewrite with a comma, colon, period or parentheses",
         re.compile(EM_DASH)),
    Rule("middle-dot", "Elias bans the middle dot everywhere; use a comma or a new line",
         re.compile(MIDDLE_DOT)),
    Rule("dash-pause", "a spaced en dash is an em dash in disguise",
         re.compile(rf" {EN_DASH} ")),
    Rule("stock-phrase", "stock phrase of generated text",
         words("game changer", "game-changer", "delve", "delving", "dive into", "deep dive", "let's dive",
               "in today's fast-paced", "fast-paced world", "ever-evolving", "unlock", "unleash", "elevate",
               "seamless", "seamlessly", "robust", "leverage", "leveraging", "cutting-edge", "revolutionize",
               "harness the power", "the power of", "landscape", "tapestry", "testament to", "navigate the",
               "my journey", "the journey", "a journey", "embark", "realm", "supercharge", "empower", "empowering",
               "transformative", "pivotal", "foster", "synergy", "in conclusion", "at the end of the day",
               "moreover", "furthermore", "here's the thing", "let that sink in", "buckle up", "excited to announce",
               "thrilled to", "humbled to", "i'm excited to share", "proud to announce", "without further ado",
               "a must-have", "next level", "take it to the next level", "crucial", "meticulous", "intricate",
               "en el mundo actual", "en la era digital", "sin lugar a dudas", "cabe destacar",
               "es importante destacar", "revolucionar", "potenciar", "desbloquear", "sumérgete", "adentrémonos",
               "un viaje", "emocionado de anunciar", "me complace anunciar", "en conclusión", "transformador",
               "de vanguardia", "aprovechar al máximo", "llevar al siguiente nivel", "sinergia", "imprescindible",
               "fascinante mundo", "sin más preámbulos", "en resumen")),
    Rule("hype-word", "hype word: say what it does and let the reader decide it is good",
         words("revolutionary", "mind-blowing", "mind blowing", "insane", "incredible", "groundbreaking",
               "unbelievable", "game-changing", "10x", "jaw-dropping", "stunning", "epic",
               "revolucionario", "revolucionaria", "increíble", "impresionante", "épico", "épica", "brutalmente")),
    Rule("not-x-but-y", "the 'not X, but Y' contrast is the signature move of generated text",
         re.compile(
             r"\bnot\s+(?:just|only|merely)\b[^.!?\n]{1,60}\bbut\b"
             r"|\b(?:it's|it is|this is|that's|this isn't|it isn't)\s+not\s+[^.!?\n]{1,50}[.,;]\s*(?:it's|it is|this is|that's)\b"
             r"|\bisn't\s+(?:just\s+)?about\b[^.!?\n]{1,50}[,;]\s*it's\s+about\b"
             r"|\bno\s+(?:es|se\s+trata\s+de)\s+(?:solo|sólo|solamente)?\s*[^.!?\n]{1,50},\s*(?:sino|es)\b"
             r"|\bno\s+solo\b[^.!?\n]{1,60}\bsino\b", re.I)),
    Rule("rhetorical-triad", "three short parallel beats in one breath read as a slogan",
         re.compile(
             r"(?:^|[.!?]\s+)[\w'áéíóúñ]+(?:\s[\w'áéíóúñ]+)?,\s[\w'áéíóúñ]+(?:\s[\w'áéíóúñ]+)?,?\s(?:and|y|&)\s[\w'áéíóúñ]+(?:\s[\w'áéíóúñ]+)?[.!]"
             r"|(?:^|\n)\s*[\w'áéíóúñ]+\.\s+[\w'áéíóúñ]+\.\s+[\w'áéíóúñ]+\.(?:\s|$)", re.I | re.M)),
    Rule("reveal-question", "the 'The result? ...' self-answered question is a template",
         re.compile(r"\b(?:the result|the answer|the best part|the catch|the kicker|the secret|the twist|the outcome)\?"
                    r"|¿(?:el resultado|la respuesta|lo mejor|el truco|el secreto)\?", re.I)),
    Rule("template-opener", "a canned opener announces a post instead of starting it",
         re.compile(r"^\s*(?:here's (?:what|how|why)\b|hot take:|unpopular opinion:|psa:|a thread\b|thread:|"
                    r"lessons learned:|let's talk about|ever wondered|did you know|imagine this|"
                    r"hilo:|opinión impopular|¿sabías que|imagina esto)", re.I | re.M)),
    Rule("engagement-bait", "asking for engagement reads as a growth hack",
         re.compile(r"\b(?:thoughts\?|agree\?|what do you think\?|drop (?:a|your) comment|let me know in the comments|"
                    r"like and (?:share|repost)|follow for more|smash that|comment below|"
                    r"¿qué opinas\?|déjalo en los comentarios|comenta abajo|sígueme para más)", re.I)),
    Rule("hashtag-spam", "more than two hashtags reads as spam", re.compile(r"(?:#\w+[^#]*){3,}")),
    Rule("emoji-stack", "two emoji in a row, or more than three in a post, reads as generated",
         re.compile(rf"(?:{EMOJI.pattern}\s*){{2,}}")),
    Rule("exclamation-stack", "a double exclamation mark is hype",
         re.compile(r"!{2,}|¡[^!]*!.*¡[^!]*!.*¡[^!]*!", re.S)),
    Rule("pointing-emoji", "the pointing and rocket emoji are the clichés of growth posts",
         re.compile("[\U0001F447\U0001F449\U0001F680\U0001F9F5\U0001F525\U0001F4AF]")),
)


@dataclass(frozen=True)
class Finding:
    source: str
    line: int
    rule: str
    why: str
    excerpt: str

    def __str__(self) -> str:
        return f"{self.source}:{self.line}: {self.rule}: {self.why}: \"{self.excerpt}\""


@dataclass(frozen=True)
class Draft:
    text: str
    line: int  # 1-based line of the draft's first line in its file
    platform: str  # x, linkedin or any


def x_length(text: str) -> int:
    return len(URL.sub("x" * X_URL_WEIGHT, text.strip()))


def lint_draft(draft: Draft, source: str) -> list[Finding]:
    findings: list[Finding] = []
    for rule in RULES:
        for match in rule.pattern.finditer(draft.text):
            line = draft.line + draft.text.count("\n", 0, match.start())
            excerpt = match.group(0).strip().replace("\n", " ")[:60]
            findings.append(Finding(source, line, rule.id, rule.why, excerpt))
    emoji = EMOJI.findall(draft.text)
    if len(emoji) > 3:
        findings.append(Finding(source, draft.line, "emoji-stack", "more than three emoji in one post", "".join(emoji)))
    if draft.platform == "x":
        offset = draft.line
        for post in re.split(r"(?m)^---\s*$", draft.text):
            length = x_length(post)
            if length > X_LIMIT:
                findings.append(Finding(source, offset, "x-length", f"{length} characters, X allows {X_LIMIT}",
                                        post.strip()[:60].replace("\n", " ")))
            offset += post.count("\n")
    return findings


FENCE = re.compile(r"^```post(?P<info>[^\n]*)\n(?P<body>.*?)^```", re.M | re.S)


def drafts_of(text: str, markdown: bool, platform: str) -> list[Draft]:
    if not markdown:
        return [Draft(text, 1, platform)]
    found = []
    for block in FENCE.finditer(text):
        info = block.group("info").split()
        kind = "x" if "x" in info else "linkedin" if "linkedin" in info else platform
        found.append(Draft(block.group("body"), text.count("\n", 0, block.start("body")) + 1, kind))
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", help="text or Markdown files, or - for stdin")
    parser.add_argument("--platform", choices=("x", "linkedin", "any"), default="any",
                        help="platform of plain-text drafts; Markdown blocks name their own")
    args = parser.parse_args(argv)

    findings: list[Finding] = []
    count = 0
    for name in args.files:
        if name == "-":
            text, markdown = sys.stdin.read(), False
        else:
            path = Path(name)
            if not path.is_file():
                print(f"no such file: {name}", file=sys.stderr)
                return 2
            text, markdown = path.read_text(encoding="utf-8"), path.suffix == ".md"
        drafts = drafts_of(text, markdown, args.platform)
        if markdown and not drafts:
            print(f"{name}: no ```post blocks to lint", file=sys.stderr)
            return 2
        count += len(drafts)
        for draft in drafts:
            findings.extend(lint_draft(draft, name))

    for finding in findings:
        print(finding)
    print(f"{count} drafts, {len(findings)} findings", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
