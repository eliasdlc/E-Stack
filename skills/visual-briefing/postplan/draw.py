#!/usr/bin/env python3
"""Draw a Postplan page from data: the agent says what the page holds, this file owns how it looks.

  python3 draw.py page.json              check the data and write page.html beside it
  python3 draw.py page.json --check      check the data, write nothing
  python3 draw.py page.json --questions  print the question tool input for the same questions
  python3 draw.py --example decide       print a data file to start from (decide, understand, look)

Then `build.py page.html` probes the result in a browser and uploads it.

Why a program draws it. Measured over 122 published pages and 73 with
questions, 1 Sep to 11 Nov 2026: 111 shared one ground and 110 one face, and
the look only changed when an agent wrote the page by hand; the median round
asked 5 questions of 146 words and one asked 49; 43 of the 73 named a ticket,
a decision or an option by a code. So the data is checked before a pixel is
drawn: at most four questions, each read whole on a phone, each saying why it
is his, options named and never lettered, the recommended one first, what
happens if he does not answer, and no code standing where a title belongs.
The counts in the header are computed from the data, so they cannot drift.

Three page types, by what he has to do:
  decide      one to four questions first, then the evidence
  understand  the conclusion and the mechanism, no question
  look        something to look at first (a capture, a mock), questions optional

`--questions` prints the same questions for the question tool, so a name on
the page is the label he taps. When every question of the page is of a kind he
may answer from it (ANSWERABLE), each option also carries a link to the
service's confirmation page, and the page carries its round in
`<meta name="postplan-round">` for `build.py` to send. A redraw keeps the round
id while what he picks between is unchanged; `--new-round` makes a new one.
`agents postplan-await` hands his picks to the question in the thread.

The page carries `<meta name="postplan-drawn">`, a fingerprint of what was
drawn. `build.py` refuses a page without it (unless `--hand "reason"`) and a
page edited after it was drawn, so a change goes through the data.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html as htmllib
import json
import os
import re
import secrets
import sys
import unicodedata

TYPES = ("decide", "understand", "look")
MAX_QUESTIONS = 4
MAX_WORDS = 100
MAX_TITLE = 120
MAX_NAME = 48

# Why a question is his. The same closed list as hooks/question-reason.py, which
# warns on the question tool call; tests/test_postplan_draw.py pins the two together.
REASONS = {
    "taste": ("Gusto", "Taste"),
    "money": ("Dinero", "Money"),
    "production": ("Producción", "Production"),
    "irreversible": ("Irreversible", "Irreversible"),
    "rules": ("Tus reglas", "Your rules"),
    "plan": ("Un plan", "A plan"),
    "hands": ("Tus manos", "Your hands"),
    "eye": ("Tu ojo", "Your eye"),
}
# The reasons he may answer from the page (decided 11 Nov 2026). The others ask for his words
# in the chat, so a page that holds any of them carries no link and no round at all.
ANSWERABLE = {"taste", "plan"}
MAX_ROUND_TEXT = 500  # characters of a question text the service stores for a round
CODE =re.compile(r"(?<![\w#/.$-])(?:[A-Z]{1,4}-?\d{1,5}[A-Z]?|\d{1,2}[A-Z])(?![\w-])")
NOT_CODES = re.compile(
    r"^(?:T3|S3|C4|A[345]|H[1-6]|V\d+|Q[1-4]|M[1-4]|MP[34]|ES\d+|X11|E2E|B2[BC]|I18N|L10N|"
    r"UTF-?(?:8|16|32)|SHA-?(?:1|256|512)|GPT-?\d|HTTP-?[123]|[1-9]D|[1-9][GKX])$")
LETTERED = re.compile(r"^\s*(?:(?:option|opci[oó]n)\s+)?[A-Ha-h1-9]\s*$|^\s*[A-Ha-h1-9][.):]\s")

STR = {
    "es": {
        "waiting": "Te espero: ", "today": "Hoy:", "rec": "Recomendada", "costs": "Te cuesta: ",
        "silent": "Si no respondes: ", "evidence": "Ver la evidencia", "undo": "Para cambiarlo: ",
        "chip_q": ("te espera", "te esperan"), "chip_d": ("decidí yo", "decidí yo"),
        "chip_u": ("sin comprobar", "sin comprobar"),
        "h_q": ("{n} decisión es tuya", "{n} decisiones son tuyas"),
        "h_d": ("{n} cosa la decidí yo", "{n} cosas las decidí yo"),
        "h_u": ("{n} cosa sigue sin comprobar", "{n} cosas siguen sin comprobar"),
        "also": ("La pregunta está también en el hilo: contesta allá con un toque.",
                 "Las preguntas están también en el hilo: contesta allá con un toque."),
        "here": ("Toca una opción y confírmala, o contesta en el hilo.",
                 "Toca una opción en cada pregunta y confírmala, o contesta en el hilo."),
        "pick": "Elegir esta", "pick_label": "Elegir: ",
        "tool_rec": " (Recomendada)",
    },
    "en": {
        "waiting": "Waiting on you: ", "today": "Today:", "rec": "Recommended", "costs": "It costs you: ",
        "silent": "If you do not answer: ", "evidence": "See the evidence", "undo": "To change it: ",
        "chip_q": ("waits on you", "wait on you"), "chip_d": ("I decided", "I decided"),
        "chip_u": ("unverified", "unverified"),
        "h_q": ("{n} decision is yours", "{n} decisions are yours"),
        "h_d": ("I decided {n} thing myself", "I decided {n} things myself"),
        "h_u": ("{n} thing is still unverified", "{n} things are still unverified"),
        "also": ("The question is also in the thread: answer there with one tap.",
                 "The questions are also in the thread: answer there with one tap."),
        "here": ("Tap an option and confirm it, or answer in the thread.",
                 "Tap an option on each question and confirm it, or answer in the thread."),
        "pick": "Pick this", "pick_label": "Pick: ",
        "tool_rec": " (Recommended)",
    },
}

TOP_KEYS = {"type", "lang", "title", "kicker", "lede", "questions", "decided", "sections",
            "unverified", "sources"}
QUESTION_KEYS = {"reason", "question", "today", "options", "silent", "evidence"}
OPTION_KEYS = {"name", "does", "costs", "recommended", "show"}
BLOCKS = ("p", "list", "steps", "table", "figure", "figures", "code", "html")
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
               ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml"}

# The look of the proposal he approved on 11 Nov 2026 (plan.decruce.dev/d/dz5nwvwnldam),
# on the tokens every Postplan page has carried. /*FONTS*/ is filled by build.py.
CSS = """/*FONTS*/
:root{
  color-scheme:dark;
  --pg:#000;--pg-2:#0a0a0c;--pg-3:#121216;--ln:#1f1f25;--ln-2:#2b2b33;
  --tx:#f2f2f5;--tx-2:#a6a6b0;
  --warn:#f5a623;--warn-bg:rgba(245,166,35,.14);
  --brand:#5B8DEF;--brand-tx:#8fb1f5;
  --sans:"Figtree",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
  --display:"Bricolage Grotesque",var(--sans);
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
html{font-size:17px;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--pg);color:var(--tx-2);font:400 1rem/1.4 var(--sans)}
.wrap{max-width:40rem;margin:0 auto;padding:0 20px}
svg.i{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
strong{color:var(--tx);font-weight:700}
a{color:var(--brand-tx)}
:focus-visible{outline:2px solid var(--brand);outline-offset:2px}
code{font:500 .88em/1.3 var(--mono);color:var(--tx)}
p{margin:0 0 10px}
.top{padding:28px 0 4px}
.kick{font:600 .78rem/1.3 var(--sans);margin:0 0 10px}
h1{font:700 1.7rem/1.1 var(--display);letter-spacing:-.03em;color:var(--tx);margin:0 0 18px}
.turns{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:0 0 16px}
.turn{display:block;text-decoration:none;background:var(--pg-3);border-radius:14px;padding:12px 12px 11px;color:var(--tx-2)}
.turn b{display:block;font:700 1.7rem/1 var(--display);letter-spacing:-.03em;color:var(--tx)}
.turn span{display:block;font:600 .78rem/1.25 var(--sans);margin-top:6px}
.turn.you{background:var(--warn-bg)}
.turn.you b,.turn.you span{color:var(--warn)}
section{padding:26px 0 0}
h2{font:700 1.3rem/1.15 var(--display);letter-spacing:-.02em;color:var(--tx);margin:0 0 14px}
.qs{display:grid;gap:12px;align-items:start}
.q{background:var(--pg-3);border-radius:14px;padding:16px;container-type:inline-size}
.top > p,.sb > p,.sb > .list{max-width:44rem}
.pill{display:inline-flex;align-items:center;gap:6px;font:600 .78rem/1 var(--sans);border-radius:999px;padding:6px 10px 6px 8px;margin:0 0 12px;background:var(--warn-bg);color:var(--warn)}
.q h3{font:700 1.3rem/1.15 var(--display);letter-spacing:-.02em;color:var(--tx);margin:0 0 8px}
.hoy{margin:0 0 14px}
.hoy b{color:var(--tx)}
.opts{display:grid;gap:10px}
.opt{border:1px solid var(--ln-2);border-radius:10px;padding:13px 14px}
.opt.rec{border-color:var(--brand)}
.opt .tag{display:block;font:600 .76rem/1.2 var(--sans);color:var(--brand-tx);margin:0 0 5px}
.opt .nm{display:block;font:700 1.05rem/1.25 var(--sans);letter-spacing:-.01em;color:var(--tx)}
.opt .does{display:block;margin:5px 0 0;font-size:.94rem;line-height:1.38}
.opt .cost{display:block;margin:6px 0 0;font:600 .82rem/1.38 var(--sans)}
.opt img{display:block;max-width:100%;height:auto;border-radius:8px;margin:10px 0 0}
.ifno{display:flex;gap:8px;align-items:flex-start;font:600 .82rem/1.38 var(--sans);margin:14px 0 0}
.ifno svg{margin-top:.1em}
details{margin:12px 0 0;border-top:1px solid var(--ln);padding-top:12px}
summary{font:600 .88rem/1.3 var(--sans);color:var(--tx);cursor:pointer;min-height:32px}
details ul{margin:8px 0 0;padding-left:1.1em}
details li{font-size:.88rem;line-height:1.42;margin:0 0 6px}
.list{margin:0 0 12px;padding-left:1.1em}
.list li{margin:0 0 6px}
.steps{list-style:none;margin:0 0 12px;padding:0;counter-reset:s}
.steps li{counter-increment:s;display:grid;grid-template-columns:1.6rem 1fr;gap:0 10px;padding:13px 0}
.steps li + li{border-top:1px solid var(--ln)}
.steps li::before{content:counter(s);font:700 1.05rem/1.35 var(--display);color:var(--tx)}
.steps b{display:block;color:var(--tx);line-height:1.3}
.steps span{display:block;font-size:.88rem;line-height:1.4;margin-top:3px}
.steps em{display:block;font:600 .82rem/1.38 var(--sans);font-style:normal;margin-top:4px}
.rows{list-style:none;margin:0 0 12px;padding:0}
.rows li{display:grid;grid-template-columns:1.4rem 1fr;gap:0 10px;padding:13px 0}
.rows li + li{border-top:1px solid var(--ln)}
.rows svg{margin-top:.14em}
.rows b{display:block;color:var(--tx);font-weight:700;line-height:1.3}
.rows span{display:block;font-size:.88rem;line-height:1.4;margin-top:3px}
.rows em{display:block;font:600 .82rem/1.38 var(--sans);font-style:normal;margin-top:4px}
.tw{overflow-x:auto;margin:0 0 12px}
.tb{width:100%;border-collapse:collapse;font-size:.88rem;line-height:1.3}
.tb th{font:600 .76rem/1.25 var(--sans);text-align:left;padding:0 12px 8px 0;vertical-align:bottom}
.tb td{padding:10px 12px 10px 0;border-top:1px solid var(--ln);vertical-align:top}
.tb td:first-child{color:var(--tx);font-weight:600}
.tb th:last-child,.tb td:last-child{padding-right:0}
.fig{margin:0 0 12px}
.fig img{display:block;max-width:100%;height:auto;border-radius:10px}
.fig figcaption{font:600 .78rem/1.4 var(--sans);margin:8px 0 0}
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:0 0 12px}
.figs .fig{margin:0}
.code{margin:0 0 12px;padding:12px 14px;background:var(--pg-3);border-radius:10px;overflow-x:auto;font:500 .8rem/1.45 var(--mono);color:var(--tx)}
.foot{font:600 .76rem/1.45 var(--sans);padding:26px 0 40px}
/* A wide screen is filled, not centered on a phone column (his words, 11 Nov 2026):
   questions side by side, the options of a lone question in a row, titles in a rail. */
@container (min-width:44rem){.opts{grid-template-columns:repeat(auto-fit,minmax(13rem,1fr))}}
@media (min-width:700px){
  h1{font-size:2.2rem}
  .top{padding-top:48px}
  .wrap{max-width:80rem;padding:0 32px}
  .turns{max-width:30rem}
  .qs{grid-template-columns:repeat(auto-fit,minmax(22rem,1fr))}
}
@media (min-width:1000px){
  .top.counted{display:grid;grid-template-columns:minmax(0,1fr) 24rem;gap:0 40px}
  .top.counted > *{grid-column:1}
  .top.counted > .turns{grid-column:2;grid-row:1 / span 5;align-self:end;margin:0 0 18px}
  section.rail{display:grid;grid-template-columns:17rem minmax(0,1fr);gap:0 40px;margin-top:30px;border-top:1px solid var(--ln)}
  section.rail > h2{font-size:1.15rem;line-height:1.2}
  .sb > .rows{display:grid;grid-template-columns:1fr 1fr;gap:0 32px;align-items:start}
  .sb > .rows li:nth-child(2){border-top:0}
}
"""

# Only a page with a round carries these rules, so a page without one is drawn byte for byte as before.
# The action sits at the foot of its option, so options side by side line their actions up.
PICK_CSS = """.opts.can .opt{display:flex;flex-direction:column}
.pk{margin-top:auto;padding-top:14px}
.pick{display:flex;align-items:center;justify-content:center;min-height:48px;padding:0 20px;border-radius:999px;border:1px solid var(--ln-2);color:var(--tx);font:700 .94rem/1.2 var(--sans);text-decoration:none}
.opt.rec .pick{background:var(--brand);border-color:var(--brand);color:var(--pg)}
@media (min-width:700px){.pick{display:inline-flex;min-width:12rem}}
"""

ICONS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="i-check" viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></symbol>
  <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></symbol>
  <symbol id="i-hand" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="2.6" fill="currentColor" stroke="none"/></symbol>
</svg>"""


def plain(text):
    folded = unicodedata.normalize("NFKD", text.casefold())
    return " ".join("".join(c for c in folded if not unicodedata.combining(c)).split())


ACCEPTED = {plain(word): key for key, pair in REASONS.items() for word in pair}
ACCEPTED["plan"] = "plan"


def codes(text):
    """Codes standing where a title belongs. One in parentheses follows its title, so it passes."""
    bare = re.sub(r"\([^)]*\)|`[^`]*`", " ", text)
    return [c for c in CODE.findall(bare) if not NOT_CODES.match(c)]


def words(*texts):
    return sum(len(str(t).split()) for t in texts if t)


def question_words(q):
    opts = [o for o in q.get("options") or [] if isinstance(o, dict)]
    return words(q.get("question"), q.get("today"), q.get("silent"),
                 *[o.get(k) for o in opts for k in ("name", "does", "costs")])


def blocks_of(spec):
    for section in spec.get("sections") or []:
        if isinstance(section, dict):
            for block in section.get("blocks") or []:
                if isinstance(block, dict) and len(block) == 1:
                    yield next(iter(block.items()))


def figures_of(spec):
    """Every image the page shows: (where, path)."""
    for qi, q in enumerate(spec.get("questions") or [], 1):
        for o in (q.get("options") or []) if isinstance(q, dict) else []:
            if isinstance(o, dict) and o.get("show"):
                yield "question " + str(qi) + ", option `" + str(o.get("name")) + "`", o["show"]
    for kind, value in blocks_of(spec):
        for fig in ([value] if kind == "figure" else value if kind == "figures" else []):
            if isinstance(fig, dict):
                yield "figure `" + str(fig.get("alt") or fig.get("src")) + "`", fig.get("src")


def prose_of(spec):
    """Every string he reads, with where it sits. Code and raw markup are not prose."""
    for key in ("title", "kicker", "lede", "sources"):
        if isinstance(spec.get(key), str):
            yield key, spec[key]
    for qi, q in enumerate(spec.get("questions") or [], 1):
        if not isinstance(q, dict):
            continue
        where = "question " + str(qi)
        for key in ("question", "today", "silent"):
            if isinstance(q.get(key), str):
                yield where, q[key]
        for text in q.get("evidence") or []:
            yield where + " evidence", str(text)
        for o in q.get("options") or []:
            if isinstance(o, dict):
                for key in ("name", "does", "costs"):
                    if isinstance(o.get(key), str):
                        yield where + " option", o[key]
    for key in ("decided", "unverified"):
        for item in spec.get(key) or []:
            for text in (item.values() if isinstance(item, dict) else [item]):
                yield key, str(text)
    for section in spec.get("sections") or []:
        if isinstance(section, dict) and isinstance(section.get("title"), str):
            yield "section title", section["title"]
    for kind, value in blocks_of(spec):
        if kind in ("code", "html"):
            continue
        stack = [value]
        while stack:
            item = stack.pop()
            if isinstance(item, str):
                if kind not in ("figure", "figures") or not os.path.splitext(item)[1].lower() in IMAGE_TYPES:
                    yield kind, item
            elif isinstance(item, dict):
                stack += list(item.values())
            elif isinstance(item, list):
                stack += item


def every_string(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from every_string(value)
    elif isinstance(node, list):
        for value in node:
            yield from every_string(value)


def lint(spec, base="."):
    """What is wrong with the data, each line naming its rule. Empty means it can be drawn."""
    out = []
    if not isinstance(spec, dict):
        return ["data: the file holds a JSON object"]
    for key in sorted(set(spec) - TOP_KEYS):
        out.append("unknown-key: `" + key + "` is not a field of a page (" + ", ".join(sorted(TOP_KEYS)) + ")")
    kind = spec.get("type")
    if kind not in TYPES:
        out.append("type: `" + str(kind) + "` is not a page type. decide when he has to answer, "
                   "understand when he has to follow an explanation, look when there is something to see")
    if spec.get("lang") not in STR:
        out.append("lang: say `es` or `en`, the language he reads this page in")
    title = spec.get("title")
    if not isinstance(title, str) or not title.strip():
        out.append("title: missing. The title is the conclusion, in one sentence")
    elif len(title) > MAX_TITLE:
        out.append("title: " + str(len(title)) + " characters, over " + str(MAX_TITLE) +
                   ". It is read at a glance; move the detail to the lede")
    if not isinstance(spec.get("kicker"), str) or not spec["kicker"].strip():
        out.append("kicker: missing. One line saying what this page is and its date")

    questions = spec.get("questions") or []
    if not isinstance(questions, list):
        questions = []
        out.append("questions: a list of questions")
    if len(questions) > MAX_QUESTIONS:
        out.append("question-count: " + str(len(questions)) + " questions, over " + str(MAX_QUESTIONS) +
                   " in a round. The extra ones were yours to decide: decide them and list them under `decided`")
    if kind == "decide" and not questions:
        out.append("question-count: a decide page asks at least one question. With none, it is an understand page")
    if kind == "understand" and questions:
        out.append("question-count: an understand page asks nothing. A page that ends in a question is a decide page")
    for qi, q in enumerate(questions, 1):
        where = "question " + str(qi)
        if not isinstance(q, dict):
            out.append(where + ": an object with reason, question, options and silent")
            continue
        for key in sorted(set(q) - QUESTION_KEYS):
            out.append("unknown-key: " + where + " has `" + key + "` (" + ", ".join(sorted(QUESTION_KEYS)) + ")")
        if plain(str(q.get("reason") or "")) not in ACCEPTED:
            out.append("reason: " + where + " says `" + str(q.get("reason")) + "`, which is not a reason a "
                       "question is his. Use one of " + ", ".join(es for es, _ in REASONS.values()) +
                       ". A fork with none of those that can be undone is yours: decide it and list it under `decided`")
        if not isinstance(q.get("question"), str) or not q["question"].rstrip().endswith("?"):
            out.append("question: " + where + " is not written as a question ending in `?`")
        if not isinstance(q.get("silent"), str) or not q["silent"].strip():
            out.append("silent: " + where + " does not say what happens if he does not answer")
        options = q.get("options")
        if not isinstance(options, list) or not 2 <= len(options) <= 4 or not all(isinstance(o, dict) for o in options):
            out.append("options: " + where + " needs two to four options, which is what the question tool shows")
            continue
        names = []
        for oi, o in enumerate(options):
            for key in sorted(set(o) - OPTION_KEYS):
                out.append("unknown-key: " + where + " has an option with `" + key + "` (" +
                           ", ".join(sorted(OPTION_KEYS)) + ")")
            name = o.get("name")
            if not isinstance(name, str) or not name.strip():
                out.append("option-name: " + where + " has an option with no name")
                continue
            names.append(plain(name))
            if LETTERED.search(name):
                out.append("option-name: " + where + " names an option `" + name.strip() + "`, a letter. "
                           "Name it by what it does")
            if len(name) > MAX_NAME:
                out.append("option-name: `" + name[:30] + "...` is " + str(len(name)) + " characters, over " +
                           str(MAX_NAME) + ". The name is the label he taps; the rest goes in `does`")
            if not isinstance(o.get("does"), str) or not o["does"].strip():
                out.append("option-does: " + where + ", `" + name + "` does not say what it does")
            if o.get("recommended") and oi:
                out.append("recommended-first: " + where + " recommends `" + name + "`, which is not the first "
                           "option. The recommended one goes first, so a plain yes accepts it")
        if len(set(names)) != len(names):
            out.append("option-name: " + where + " repeats an option name")
        count = question_words(q)
        if count > MAX_WORDS:
            out.append("question-words: " + where + " runs " + str(count) + " words, over " + str(MAX_WORDS) +
                       ". The question, what happens today, the options and the silence are read whole on a "
                       "phone; move the rest to `evidence`, which is folded")

    for key, need in (("decided", ("what", "why")), ("unverified", ("what",))):
        items = spec.get(key)
        if items is None and key == "unverified":
            out.append("unverified: missing. List what was not run or seen, or write [] when everything was")
            continue
        for item in items or []:
            if isinstance(item, str) and key == "unverified":
                continue
            if not isinstance(item, dict) or any(not item.get(k) for k in need):
                out.append(key + ": every entry carries " + " and ".join("`" + k + "`" for k in need) +
                           (", plus `undo` when there is a way back" if key == "decided" else ""))
                break

    sections = spec.get("sections") or []
    for si, section in enumerate(sections, 1):
        if not isinstance(section, dict) or not section.get("title") or not isinstance(section.get("blocks"), list):
            out.append("section: section " + str(si) + " carries a `title` and a list of `blocks`")
            continue
        for block in section["blocks"]:
            if not isinstance(block, dict) or len(block) != 1 or next(iter(block)) not in BLOCKS:
                out.append("block: section " + str(si) + " has a block that is not one of " + ", ".join(BLOCKS))
                continue
            name, value = next(iter(block.items()))
            if name == "table":
                head = value.get("head") if isinstance(value, dict) else None
                rows = value.get("rows") if isinstance(value, dict) else None
                if not isinstance(head, list) or not isinstance(rows, list) or \
                        any(not isinstance(r, list) or len(r) != len(head) for r in rows):
                    out.append("block: a table in section " + str(si) + " needs `head` and `rows` of the same width")
            elif name in ("list", "steps", "figures") and not isinstance(value, list):
                out.append("block: `" + name + "` in section " + str(si) + " is a list")
    if kind == "understand":
        if not isinstance(spec.get("lede"), str) or not spec["lede"].strip():
            out.append("lede: an understand page opens with the conclusion and the mechanism in `lede`")
        if not sections:
            out.append("section: an understand page carries its evidence in at least one section")
    shown = list(figures_of(spec))
    if kind == "look" and not shown and not any(k == "html" for k, _ in blocks_of(spec)):
        out.append("nothing-to-look-at: a look page shows a capture, a mock or a component "
                   "(`show` on an option, a `figure`, `figures` or `html` block)")
    for where, src in shown:
        path = os.path.join(base, str(src or ""))
        if os.path.splitext(path)[1].lower() not in IMAGE_TYPES:
            out.append("image: " + where + " points at `" + str(src) + "`, which is not one of " +
                       ", ".join(sorted(IMAGE_TYPES)))
        elif not os.path.isfile(path):
            out.append("image: " + where + " points at `" + str(src) + "`, which does not exist")

    for where, text in prose_of(spec):
        for code in codes(text):
            out.append("code-for-a-name: `" + code + "` in " + where + " stands where a title belongs. Write the "
                       "title and, if the code helps, put it after it in parentheses")
    for text in every_string(spec):
        if chr(0x2014) in text or chr(0xB7) in text:
            out.append("punctuation: an em dash or a middle dot in `" + text[:40] + "`. Use a comma, a colon, "
                       "a period or parentheses")
    try:
        asks = round_questions(spec) and tool_questions(spec)["questions"]
    except (KeyError, TypeError, AttributeError):
        asks = None  # a malformed question is already named above
    if asks:
        # The service stores this exact text and refuses over MAX_ROUND_TEXT or a control character.
        for qi, asked in enumerate(asks, 1):
            if len(asked["question"]) > MAX_ROUND_TEXT:
                out.append("round-text: question " + str(qi) + " reaches the question tool as " +
                           str(len(asked["question"])) + " characters with its silence sentence, over " +
                           str(MAX_ROUND_TEXT) + " that the service stores for a round. Shorten the question "
                           "or `silent`, or make it a reason he answers in the chat")
            if re.search(r"[\x00-\x1f\x7f]", asked["question"]):
                out.append("round-text: question " + str(qi) + " carries a control character that the "
                           "service refuses in a round")
    return list(dict.fromkeys(out))


def esc(text):
    return htmllib.escape(str(text), quote=True)


INLINE = re.compile(r"\*\*(.+?)\*\*|`([^`]+)`|\[([^\]]+)\]\((https?://[^\s)]+)\)")


def inline(text):
    """Escaped text with **strong**, `code` and [links](https://...)."""
    text, out, pos = str(text), [], 0
    for m in INLINE.finditer(text):
        out.append(esc(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append("<strong>" + esc(m.group(1)) + "</strong>")
        elif m.group(2) is not None:
            out.append("<code>" + esc(m.group(2)) + "</code>")
        else:
            out.append('<a href="' + esc(m.group(4)) + '">' + esc(m.group(3)) + "</a>")
        pos = m.end()
    return "".join(out) + esc(text[pos:])


def icon(name):
    return '<svg class="i" aria-hidden="true"><use href="#i-' + name + '"/></svg>'


def data_uri(base, src):
    path = os.path.join(base, src)
    kind = IMAGE_TYPES[os.path.splitext(path)[1].lower()]
    with open(path, "rb") as image:
        return "data:" + kind + ";base64," + base64.b64encode(image.read()).decode()


def figure(base, fig):
    caption = "<figcaption>" + inline(fig["caption"]) + "</figcaption>" if fig.get("caption") else ""
    return ('<figure class="fig"><img src="' + data_uri(base, fig["src"]) + '" alt="' +
            esc(fig.get("alt") or fig.get("caption") or "") + '">' + caption + "</figure>")


def block(base, kind, value):
    if kind == "p":
        return "<p>" + inline(value) + "</p>"
    if kind == "list":
        if value and all(isinstance(v, dict) for v in value):
            return '<ul class="rows">' + "".join(
                "<li>" + icon("check") + "<div><b>" + inline(v.get("title", "")) + "</b>" +
                ("<span>" + inline(v["text"]) + "</span>" if v.get("text") else "") + "</div></li>"
                for v in value) + "</ul>"
        return '<ul class="list">' + "".join("<li>" + inline(v) + "</li>" for v in value) + "</ul>"
    if kind == "steps":
        return '<ol class="steps">' + "".join(
            "<li><div><b>" + inline(v.get("title", "")) + "</b>" +
            ("<span>" + inline(v["text"]) + "</span>" if v.get("text") else "") +
            ("<em>" + inline(v["note"]) + "</em>" if v.get("note") else "") + "</div></li>"
            for v in value) + "</ol>"
    if kind == "table":
        head = "".join("<th>" + inline(h) + "</th>" for h in value["head"])
        rows = "".join("<tr>" + "".join("<td>" + inline(c) + "</td>" for c in row) + "</tr>"
                       for row in value["rows"])
        return ('<div class="tw"><table class="tb"><thead><tr>' + head + "</tr></thead><tbody>" +
                rows + "</tbody></table></div>")
    if kind == "figure":
        return figure(base, value)
    if kind == "figures":
        return '<div class="figs">' + "".join(figure(base, fig) for fig in value) + "</div>"
    if kind == "code":
        return '<pre class="code">' + esc(value) + "</pre>"
    return str(value)  # html: a component as markup, his to look at, never a control that submits


def plural(strings, key, n):
    return strings[key][0 if n == 1 else 1].format(n=n)


def question(base, strings, lang, q, links=None):
    """One question. `links` holds the confirmation link of each option, when the page has a round."""
    reason = REASONS[ACCEPTED[plain(q["reason"])]][0 if lang == "es" else 1]
    out = ['<div class="q">',
           '<span class="pill">' + icon("hand") + esc(strings["waiting"] + reason.lower()) + "</span>",
           "<h3>" + inline(q["question"]) + "</h3>"]
    if q.get("today"):
        out.append('<p class="hoy"><b>' + strings["today"] + "</b> " + inline(q["today"]) + "</p>")
    out.append('<div class="opts can">' if links else '<div class="opts">')
    for oi, o in enumerate(q["options"]):
        rec = bool(o.get("recommended"))
        # A plain link is the only channel a drawn page has: the service serves it with no script,
        # no form and no network, and the pick is confirmed and recorded on the service's own page.
        pick = ('<span class="pk"><a class="pick" href="' + esc(links[oi]) + '" aria-label="' +
                esc(strings["pick_label"] + o["name"].strip()) + '">' + strings["pick"] + "</a></span>"
                if links else "")
        out.append('<div class="opt' + (" rec" if rec else "") + '">' +
                   ('<span class="tag">' + strings["rec"] + "</span>" if rec else "") +
                   '<span class="nm">' + inline(o["name"]) + "</span>" +
                   '<span class="does">' + inline(o["does"]) + "</span>" +
                   ('<span class="cost">' + strings["costs"] + inline(o["costs"]) + "</span>" if o.get("costs") else "") +
                   ('<img src="' + data_uri(base, o["show"]) + '" alt="' + esc(o["name"]) + '">' if o.get("show") else "") +
                   pick + "</div>")
    out.append("</div>")
    out.append('<p class="ifno">' + icon("clock") + "<span>" + strings["silent"] + inline(q["silent"]) + "</span></p>")
    if q.get("evidence"):
        out.append("<details><summary>" + strings["evidence"] + "</summary><ul>" +
                   "".join("<li>" + inline(e) + "</li>" for e in q["evidence"]) + "</ul></details>")
    out.append("</div>")
    return "\n".join(out)


def rows(strings, items, mark):
    out = ['<ul class="rows">']
    for item in items:
        item = {"what": item} if isinstance(item, str) else item
        out.append("<li>" + icon(mark) + "<div><b>" + inline(item["what"]) + "</b>" +
                   ("<span>" + inline(item["why"]) + "</span>" if item.get("why") else "") +
                   ("<em>" + strings["undo"] + inline(item["undo"]) + "</em>" if item.get("undo") else "") +
                   "</div></li>")
    return "\n".join(out + ["</ul>"])


def draw(spec, base=".", round_id=None):
    """The page for data that passed lint(), stamped with its fingerprint. When every question is
    answerable the page carries its round, under `round_id` or a new one."""
    lang = spec["lang"]
    strings = STR[lang]
    questions, decided = spec.get("questions") or [], spec.get("decided") or []
    unverified, sections = spec.get("unverified") or [], spec.get("sections") or []
    asks = round_questions(spec)
    rid = (round_id or new_round_id()) if asks else None

    chips = [(len(questions), "chip_q", "tuyas", " you"), (len(decided), "chip_d", "decidi", ""),
             (len(unverified), "chip_u", "dudas", "")]
    counted = any(n for n, *_ in chips)
    top = ['<header class="top' + (" counted" if counted else "") + '">',
           '<p class="kick">' + inline(spec["kicker"]) + "</p>", "<h1>" + inline(spec["title"]) + "</h1>"]
    if counted:
        top.append('<div class="turns">' + "".join(
            '<a class="turn' + cls + '" href="#' + anchor + '"><b>' + str(n) + "</b><span>" +
            strings[key][0 if n == 1 else 1] + "</span></a>"
            for n, key, anchor, cls in chips if n) + "</div>")
    if spec.get("lede"):
        top.append("<p>" + inline(spec["lede"]) + "</p>")
    if questions:
        top.append("<p>" + strings["here" if rid else "also"][0 if len(questions) == 1 else 1] + "</p>")
    top.append("</header>")

    def links(qi, q):
        return ["/a/" + rid + "/" + str(qi) + "/" + str(oi) for oi in range(len(q["options"]))] if rid else None

    asked = []
    if questions:
        asked = ['<section id="tuyas">', "<h2>" + plural(strings, "h_q", len(questions)) + "</h2>",
                 '<div class="qs">', *[question(base, strings, lang, q, links(qi, q))
                                       for qi, q in enumerate(questions)], "</div>",
                 "</section>"]

    def railed(anchor, title, *inner):
        # The title and its content are two cells, so a wide screen can set them side by side.
        return ['<section id="' + anchor + '" class="rail">', "<h2>" + title + "</h2>",
                '<div class="sb">', *inner, "</div>", "</section>"]

    body = []
    for si, section in enumerate(sections, 1):
        body += railed("s" + str(si), inline(section["title"]),
                       *[block(base, *next(iter(b.items()))) for b in section["blocks"]])
    tail = []
    if decided:
        tail += railed("decidi", plural(strings, "h_d", len(decided)), rows(strings, decided, "check"))
    if unverified:
        tail += railed("dudas", plural(strings, "h_u", len(unverified)), rows(strings, unverified, "clock"))
    foot = ['<p class="foot">' + inline(spec["sources"]) + "</p>"] if spec.get("sources") else \
        ['<div class="foot"></div>']
    # A look page opens on the thing to look at; the other two on the ask or the conclusion.
    middle = body + asked + tail if spec["type"] == "look" else asked + body + tail

    # The round sits inside what the stamp covers, so a hand edit of it or of a link is refused.
    head_round = ['<meta name="postplan-round" content="' +
                  esc(json.dumps({"id": rid, "questions": asks}, ensure_ascii=False, separators=(",", ":"))) +
                  '">'] if rid else []
    page = "\n".join([
        "<!doctype html>", '<html lang="' + lang + '">', "<head>", '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="postplan-mode" content="adaptive">', *head_round, STAMP_SLOT,
        "<title>" + esc(spec["title"]) + "</title>", "<style>", CSS + (PICK_CSS if rid else "") + "</style>",
        "</head>", "", "<body>", ICONS, '<div class="wrap">', *top, *middle, *foot, "</div>", "</body>", "</html>", ""])
    return page.replace(STAMP_SLOT, '<meta name="postplan-drawn" content="' + fingerprint(page) + '">', 1)


STAMP_SLOT = '<meta name="postplan-drawn" content="">'
STAMP = re.compile(r'<meta name="postplan-drawn" content="([0-9a-f]*)">')
DRAFT = re.compile(r'<meta name="postplan-draft" content="([^"]+)">')
ROUND = re.compile(r'<meta name="postplan-round" content="([^"]*)">')


def round_questions(spec):
    """What the service stores for the round: each question as it reads on the page and its option
    names. None unless every question is answerable, because a round is answered in one place."""
    questions = spec.get("questions") or []
    if not questions or any(ACCEPTED[plain(q["reason"])] not in ANSWERABLE for q in questions):
        return None
    # `text` is what the question tool is given (draw.py --questions), silence sentence included,
    # because his tap in the thread is keyed by it: a change to the silence is a new round.
    asked = tool_questions(spec)["questions"]
    return [{"text": a["question"], "options": [o["name"].strip() for o in q["options"]],
             "answerable": True} for a, q in zip(asked, questions)]


def new_round_id():
    """16 random bytes, base64url: the service takes 22 to 64 URL-safe characters."""
    return secrets.token_urlsafe(16)


def round_of(page):
    """The round a page carries, {id, questions}, or None."""
    m = ROUND.search(page)
    if not m:
        return None
    try:
        found = json.loads(htmllib.unescape(m.group(1)))
    except ValueError:
        return None
    return found if isinstance(found, dict) and found.get("id") and found.get("questions") else None


def fingerprint(page):
    """A hash of what was drawn, blind to what build.py adds on the way up: the
    fonts, the WebP re-encode of the images and the draft id."""
    text = re.sub(r'<meta name="postplan-(?:draft|drawn)" content="[^"]*">', "", page)
    text = re.sub(r"@font-face\s*\{[^}]*\}", "", text).replace("/*FONTS*/", "")
    text = re.sub(r"data:[\w.+-]+/[\w.+-]+;base64,[A-Za-z0-9+/=]+", "data:", text)
    return hashlib.sha256(" ".join(text.split()).encode()).hexdigest()[:16]


def stamp_of(page):
    """The fingerprint a page claims, or None when no program drew it."""
    m = STAMP.search(page)
    return m.group(1) if m else None


def tool_questions(spec):
    """The same questions as input for the question tool: each name is the label he taps."""
    lang = spec["lang"]
    strings = STR[lang]
    out = []
    for q in spec.get("questions") or []:
        options = []
        for o in q["options"]:
            description = o["does"] + (" " + strings["costs"] + o["costs"] if o.get("costs") else "")
            options.append({"label": o["name"] + (strings["tool_rec"] if o.get("recommended") else ""),
                            "description": description})
        out.append({"question": q["question"].rstrip() + " " + strings["silent"] + q["silent"],
                    "header": REASONS[ACCEPTED[plain(q["reason"])]][0 if lang == "es" else 1],
                    "multiSelect": False, "options": options})
    return {"questions": out}


EXAMPLES = {
    "decide": {
        "type": "decide", "lang": "es",
        "title": "La conclusión en una oración: qué pasa y qué te toca",
        "kicker": "Qué es esta página y su fecha",
        "questions": [{
            "reason": "Gusto",
            "question": "¿La pregunta, como él la diría?",
            "today": "Qué pasa hoy, con su número.",
            "options": [
                {"name": "El nombre de la primera", "does": "Qué hace.", "costs": "qué le cuesta.",
                 "recommended": True},
                {"name": "El nombre de la segunda", "does": "Qué hace."}],
            "silent": "qué pasa si no contesta.",
            "evidence": ["Un dato medido, con su fuente."]}],
        "decided": [{"what": "Lo que decidí yo", "why": "Por qué era mío.", "undo": "cómo se cambia."}],
        "sections": [{"title": "Un título que es un hecho, con su número", "blocks": [{"p": "La evidencia."}]}],
        "unverified": ["Lo que no corrí ni vi."],
        "sources": "De dónde sale lo medido.",
    },
    "understand": {
        "type": "understand", "lang": "es",
        "title": "La conclusión en una oración",
        "kicker": "Qué es esta página y su fecha",
        "lede": "El mecanismo en dos oraciones.",
        "sections": [{"title": "Un título que es un hecho, con su número", "blocks": [
            {"steps": [{"title": "Primer paso", "text": "Qué pasa."}]},
            {"table": {"head": ["Qué", "Antes", "Ahora"], "rows": [["Una fila", "un valor", "otro"]]}}]}],
        "unverified": [],
    },
    "look": {
        "type": "look", "lang": "es",
        "title": "Qué se ve y qué cambia",
        "kicker": "Qué es esta página y su fecha",
        "sections": [{"title": "Un título que dice qué cambió entre las capturas", "blocks": [
            {"figures": [{"src": "antes.png", "caption": "Antes"}, {"src": "ahora.png", "caption": "Ahora"}]}]}],
        "unverified": [],
    },
}


def main():
    ap = argparse.ArgumentParser(description="Draw a Postplan page from data.")
    ap.add_argument("data", nargs="?", help="the page as JSON")
    ap.add_argument("--out", help="where the page is written (default: beside the data, .html)")
    ap.add_argument("--check", action="store_true", help="check the data and write nothing")
    ap.add_argument("--questions", action="store_true", help="print the question tool input")
    ap.add_argument("--example", choices=TYPES, help="print a data file to start from")
    ap.add_argument("--new-round", action="store_true",
                    help="give the page's round a new id even when its questions did not change")
    a = ap.parse_args()
    if a.example:
        print(json.dumps(EXAMPLES[a.example], ensure_ascii=False, indent=2))
        return 0
    if not a.data:
        ap.error("the data file is missing")
    path = os.path.abspath(a.data)
    try:
        spec = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as err:
        sys.exit("not drawing: " + path + " is not readable JSON (" + str(err) + ")")
    base = os.path.dirname(path)
    problems = lint(spec, base)
    if problems:
        sys.exit("not drawing:\n- " + "\n- ".join(problems))
    if a.questions:
        print(json.dumps(tool_questions(spec), ensure_ascii=False, indent=2))
        return 0
    asked = len(spec.get("questions") or [])
    note = spec["type"] + ", " + str(asked) + " question(s)" + \
        "".join(", " + str(question_words(q)) + " words" for q in spec.get("questions") or [])
    if a.check:
        print("ok, " + note)
        return 0
    out = os.path.abspath(a.out or os.path.splitext(path)[0] + ".html")
    old = open(out, encoding="utf-8").read() if os.path.exists(out) else None
    if old is not None and stamp_of(old) is None:
        sys.exit("not drawing: " + out + " exists and was not drawn by this program. Pick another --out")
    # The round keeps its id while what he picks between is unchanged, so a link he already
    # opened still answers; a changed question or option is a new round.
    before = round_of(old) if old and not a.new_round else None
    kept = before["id"] if before and before.get("questions") == round_questions(spec) else None
    page = draw(spec, base, kept)
    if old is not None:
        draft = DRAFT.search(old)
        if draft:  # the same link keeps its address across redraws
            page = page.replace("<head>", "<head>\n" + draft.group(0), 1)
    open(out, "w", encoding="utf-8").write(page)
    drawn = round_of(page)
    if drawn:
        note += ", answerable from the page (round " + drawn["id"] + (", kept" if kept else ", new") + ")"
    print(out + "  " + note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
