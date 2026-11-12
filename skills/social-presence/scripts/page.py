#!/usr/bin/env python3
"""Turn a week pack into the phone page Elias publishes from: Spanish UI, one tap per post.

Every X original gets "Abrir en X" (the composer opens with the text already in
it; for a quote post, with the quoted post attached) and every block gets
"Copiar". An X thread is split into its parts where lint.py splits it, numbered,
and only the first part opens the composer, because X takes the rest one by one
with its + button. An item whose heading is marked optional, "(optional)",
"(opcional ...)", ", optional" at the end or "Optional:" at the start, is folded
away. Context before the first `##` is the agent's provenance and stays off the
page; everything under a `##` is his, and a heading inside a draft's fence is
part of the draft.

    page.py <data>/packs/2026-11-09-week-2.md
    page.py PACK --out FILE

The page is written to `<data>/plans/<pack name>-phone.html`. When that file
already carries `<meta name="postplan-draft">` from an earlier upload, the new
page keeps it, so publishing again updates the same link instead of making a
new one. The pack is linted first, and a pack with findings builds no page;
nor does one the page would show differently from what the lint read (an
unclosed fence, a draft outside any `##`), a quote post without the link it
quotes, or an em dash or a middle dot anywhere on the page, which Postplan
refuses.

Exit 0 with the path printed, 1 when the lint has findings, 2 on a usage error.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import importlib.util
import json
import re
import sys
import urllib.parse
from pathlib import Path
from zoneinfo import ZoneInfo

DATA = Path.home() / "Documents/Personal/dev/social-presence"
ZONE = ZoneInfo("America/Santo_Domingo")
H = html.escape

_spec = importlib.util.spec_from_file_location("social_lint", Path(__file__).with_name("lint.py"))
lint = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lint  # dataclasses look their module up while the class is built
_spec.loader.exec_module(lint)

DAYS = {"Mon": "Lunes", "Tue": "Martes", "Wed": "Miércoles", "Thu": "Jueves", "Fri": "Viernes",
        "Sat": "Sábado", "Sun": "Domingo"}
MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
          "octubre", "noviembre", "diciembre"]
EN_MONTHS = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
                                          "Nov", "Dec"], 1)}
# The fixed words of a pack heading, in the order they are tried. Whatever follows
# them is shown as written, so a pack puts the rest of a heading in Spanish.
KINDS = [("LinkedIn post", "LinkedIn"), ("Quote post on", "Cita sobre"), ("Quote post", "Cita"),
         ("Reply on", "Respuesta en"), ("X replies", "Respuestas en X"), ("Comment on", "Comentario en"),
         ("Weekly review", "Revisión semanal"), ("Original", "Post"), ("Thread", "Hilo")]
# Note lines a pack writes in English; the Spanish form is accepted as is.
NOTES = [("Replying to:", "Responde aquí:"), ("Reply to:", "Responde aquí:"), ("Quote:", "Cita este post:"),
         ("Comment on:", "Comenta aquí:"), ("Link in the first comment:", "Enlace en el primer comentario:"),
         ("Link:", "Enlace:"), ("Why:", "Por qué:")]
OPTIONAL = re.compile(r"\s*[(\[](?:optional|opcional)(?:\s+(?:si|if)\b[^)\]]*)?[)\]]|,\s*(?:optional|opcional)\s*$"
                      r"|\s+-\s+(?:optional|opcional)\s*$|^(?:optional|opcional):\s*", re.I)
URL = re.compile(r"https?://[^\s<>\"]+")
BANNED = (lint.EM_DASH, lint.MIDDLE_DOT)


def intent(text: str, quoted: str = "") -> str:
    """The X composer link with `text` prefilled and, for a quote post, the quoted link; all encoded."""
    link = "https://x.com/intent/post?text=" + urllib.parse.quote(text, safe="")
    return link + ("&url=" + urllib.parse.quote(quoted, safe="") if quoted else "")


def is_x(info: str) -> bool:
    """Whether a fence holds an X draft, the way lint.py decides it."""
    return "x" in info.split()


def thread_parts(body: str, info: str = "x") -> list[str]:
    """The posts of a block: an X block splits where lint.py splits it, a line holding only `---`."""
    if not is_x(info):
        return [body.strip()]
    return [p.strip() for p in re.split(r"(?m)^---\s*$", body) if p.strip()]


def copy_button(text: str) -> str:
    return f'<button class="copy" data-t="{H(json.dumps(text))}">Copiar</button>'


def post_block(body: str, info: str, quoted: str = "") -> str:
    """One draft: each part in its own card, "Abrir en X" on the first part of an X original, quote or thread."""
    opens_x = is_x(info) and "reply" not in info.split()
    parts = thread_parts(body, info)
    out = []
    for i, part in enumerate(parts):
        seg = f'<span class="seg">{i + 1} de {len(parts)}</span>' if len(parts) > 1 else ""
        acts = copy_button(part)
        if opens_x and i == 0:
            acts = f'<a class="go" href="{H(intent(part, quoted))}" target="_blank" rel="noopener">Abrir en X</a>' + acts
        out.append(f'<div class="post">{seg}<p>{H(part)}</p><div class="acts">{acts}</div></div>')
    if len(parts) > 1:
        out.append('<p class="hint">Es un hilo: en el editor de X toca + para añadir el siguiente '
                   'y pega cada parte en orden.</p>')
    return "".join(out)


def clean_url(raw: str) -> str:
    """A link as written in prose: without the sentence's closing punctuation or an unbalanced `)`."""
    url = raw.rstrip(".,;:")
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1].rstrip(".,;:")
    return url


def inline(text: str) -> str:
    """Escape a line, drop code backticks and make its links tappable."""
    text = text.replace("`", "")
    out, last = [], 0
    for m in URL.finditer(text):
        url = clean_url(m.group(0))
        out.append(H(text[last:m.start()]))
        out.append(f'<a href="{H(url)}" target="_blank" rel="noopener">{H(url.split("//", 1)[1][:48])}</a>')
        last = m.start() + len(url)
    out.append(H(text[last:]))
    return "".join(out)


def note_line(line: str) -> str:
    for en, es in NOTES:
        if line.startswith(en):
            return es + line[len(en):]
    return line


def heading(text: str) -> tuple[str, bool]:
    """The Spanish label of an item heading and whether the item is optional."""
    optional = bool(OPTIONAL.search(text))
    text = OPTIONAL.sub("", text).strip()
    for en, es in KINDS:
        if text.startswith(en):
            text = es + text[len(en):]
            break
    return text, optional


def day_title(text: str) -> str:
    """`Mon 2 Nov: rest` (or Monday, November) becomes `Lunes 2 de noviembre: rest`; Spanish passes through."""
    m = re.match(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]* (\d{1,2}) ([A-Z][a-z]{2})[a-z]*\b(.*)", text)
    if m and m.group(3) in EN_MONTHS:
        return f"{DAYS[m.group(1)]} {m.group(2)} de {MONTHS[EN_MONTHS[m.group(3)] - 1]}{m.group(4)}"
    return text


def chip(title: str) -> str:
    """The short label of a day in the top bar: `Lun 2`, or the start of the title."""
    m = re.match(r"(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo) (\d{1,2})", title)
    if m:
        return f"{m.group(1)[:3]} {m.group(2)}"
    return re.split(r"[:,]", title)[0][:22]


class Refused(ValueError):
    pass


QUOTE_NOTE = ("Quote:", "Cita este post:", "Cita:")


def blocks(lines: list[str]) -> list[tuple[str, str, str]]:
    """("text", line, "") or ("post", body, info) pieces of a section, fences read before anything else."""
    out, i = [], 0
    while i < len(lines):
        m = re.match(r"^```post(.*)$", lines[i])
        if m:
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("```"):
                j += 1
            if j == len(lines) or lines[j].rstrip() != "```":
                raise Refused(f"line {i + 1}: a ```post fence that never closes with a bare ``` line")
            out.append(("post", "\n".join(lines[i + 1:j]), m.group(1)))
            i = j + 1
        elif lines[i].lstrip().startswith("```"):
            raise Refused(f"line {i + 1}: a fence the lint does not read (indented, four backticks or stray)")
        else:
            out.append(("text", lines[i], ""))
            i += 1
    return out


def render_blocks(pieces: list[tuple[str, str, str]], quote: bool = False) -> str:
    """Notes and drafts in order; a quote post's "Abrir en X" carries the link of its Quote note.

    A quote post (`quote`, a Quote or Cita note, or a fence marked quote) without that link is refused,
    because the button would publish it as a plain post.
    """
    notes = [t.strip() for kind, t, _ in pieces if kind == "text" and t.strip().startswith(QUOTE_NOTE)]
    links = [URL.search(t) for t in notes]
    quoted = next((clean_url(m.group(0)) for m in links if m), "")
    quote = quote or bool(notes) or any(kind == "post" and "quote" in info.split() for kind, _, info in pieces)
    if quote and not quoted:
        raise Refused("a quote post without a Quote: line carrying the link it quotes")
    out = []
    for kind, text, info in pieces:
        if kind == "post":
            out.append(post_block(text, info, quoted))
        elif text.strip():
            out.append(f'<p class="note">{inline(note_line(text.strip()))}</p>')
    return "".join(out)


def item(head: str, pieces: list[tuple[str, str, str]]) -> str:
    """One `###` item: its heading, its notes and its drafts, folded when optional."""
    label, optional = heading(head.strip())
    inner = render_blocks(pieces, quote=bool(re.match(r"(?:Quote post|Cita)\b", OPTIONAL.sub("", head.strip()))))
    if optional:
        return (f'<details class="item opt"><summary><h3>{H(label)}</h3><span class="tagopt">opcional</span>'
                f'</summary>{inner}</details>')
    return f'<section class="item"><h3>{H(label)}</h3>{inner}</section>'


def sections(pack: str) -> list[tuple[str, str]]:
    """(title, html) for each `##` section; what comes before the first one stays off the page.

    Headings are read only outside a draft's fence, so a `## ` line inside a draft stays in it.
    """
    tree: list[list] = []  # [title, lead pieces, [(item head, pieces)]]
    for piece in blocks([line.rstrip("\r") for line in pack.split("\n")]):  # \n only, as the lint
        kind, text, _ = piece
        line = text.strip()
        if kind == "text" and re.match(r"##\s", line):
            tree.append([day_title(line[3:].strip()), [], []])
        elif not tree:
            continue  # provenance; a draft here is caught by the count in main()
        elif kind == "text" and re.match(r"###\s", line):
            tree[-1][2].append((line[4:].strip(), []))
        elif tree[-1][2]:
            tree[-1][2][-1][1].append(piece)
        else:
            tree[-1][1].append(piece)
    return [(title, render_blocks(lead) + "".join(item(h, p) for h, p in items)) for title, lead, items in tree]


def banned_lines(pack: str) -> list[str]:
    """Pack lines carrying a character Postplan refuses."""
    return [f"line {n}: {line.strip()[:60]}" for n, line in enumerate(pack.splitlines(), 1)
            if any(ch in line for ch in BANNED)]


def week_title(pack_path: Path, pack: str) -> str:
    """"Qué publicar en X, 9 al 15 de noviembre" from the Monday in the file name, else the pack's `#`."""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", pack_path.name)
    try:
        start = dt.date.fromisoformat(m.group(1)) if m else None
    except ValueError:
        start = None
    if start:
        end = start + dt.timedelta(days=6)
        if start.month == end.month:
            span = f"{start.day} al {end.day} de {MONTHS[end.month - 1]}"
        else:
            span = f"{start.day} de {MONTHS[start.month - 1]} al {end.day} de {MONTHS[end.month - 1]}"
        return f"Qué publicar en X, {span}"
    first = re.search(r"(?m)^# (.+)$", pack)
    return first.group(1).strip() if first else "Qué publicar en X"


def draft_meta(out: Path) -> str:
    """The postplan-draft meta of an earlier upload of this page, so the link stays the same."""
    if not out.is_file():
        return ""
    m = re.search(r'<meta name="postplan-draft" content="[^"]+">', out.read_text(encoding="utf-8"))
    return m.group(0) if m else ""


STYLE = """
:root{color-scheme:dark;--bg:#000;--sf:#111214;--sf2:#1c1d20;--ink:#f2f1ec;--body:#d6d4cc;--mute:#8f8c83;--ac:#7cc4ae;--on:#062a20;--ln:rgba(255,255,255,.08)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--body);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:620px;margin:0 auto;padding:22px 16px 60px}
h1{color:var(--ink);font-size:25px;line-height:1.2;margin:0 0 8px;letter-spacing:-.01em}
.lede{color:var(--mute);margin:0 0 18px}
nav{display:flex;gap:8px;overflow-x:auto;padding:0 0 14px 16px;margin:0 -16px 8px;scrollbar-width:none}
nav a{flex:none;color:var(--ink);text-decoration:none;background:var(--sf);border-radius:999px;padding:7px 13px;font-size:14px}
.day{margin:26px 0 0}h2{color:var(--ink);font-size:19px;margin:0 0 10px;border-top:1px solid var(--ln);padding-top:16px}
h3{color:var(--ink);font-size:15px;margin:0 0 8px;font-weight:650;display:inline}
.item{background:var(--sf);border-radius:18px;padding:14px;margin:0 0 10px}
section.item h3{display:block}
summary{cursor:pointer;list-style:none;display:flex;gap:8px;align-items:center;flex-wrap:wrap}summary::-webkit-details-marker{display:none}
summary::after{content:"ver";margin-left:auto;color:var(--mute);font-size:13px}details[open] summary::after{content:"ocultar"}
details[open] summary{margin-bottom:8px}
.tagopt{font-size:12px;color:var(--mute);background:var(--sf2);border-radius:999px;padding:2px 9px;margin-left:6px;font-weight:500}
.note{color:var(--mute);font-size:14px;margin:0 0 8px;overflow-wrap:anywhere}.note a{color:var(--body)}
.post{background:var(--sf2);border-radius:14px;padding:12px;margin:8px 0}
.post p{margin:0 0 10px;color:var(--ink);white-space:pre-wrap;user-select:all}
.seg{display:block;font-size:12px;color:var(--mute);margin-bottom:4px}
.acts{display:flex;gap:8px}
.go,.copy{font:600 15px system-ui,sans-serif;border-radius:999px;min-height:44px;padding:0 18px;display:inline-flex;align-items:center;justify-content:center;text-decoration:none;cursor:pointer;border:0}
.go{background:var(--ac);color:var(--on)}.copy{background:transparent;color:var(--ink);box-shadow:inset 0 0 0 1px rgba(255,255,255,.18)}
.copy.done{color:var(--ac);box-shadow:inset 0 0 0 1px var(--ac)}
.go:focus-visible,.copy:focus-visible,nav a:focus-visible,summary:focus-visible{outline:2px solid var(--ac);outline-offset:2px}
.hint{font-size:13px;color:var(--mute);margin:4px 0 0}
.foot{color:var(--mute);font-size:13px;margin-top:30px}
"""

SCRIPT = """
document.querySelectorAll(".copy").forEach(b=>b.addEventListener("click",async()=>{const t=JSON.parse(b.dataset.t);try{await navigator.clipboard.writeText(t)}catch(e){const a=document.createElement("textarea");a.value=t;document.body.appendChild(a);a.select();document.execCommand("copy");a.remove()}b.textContent="Copiado";b.classList.add("done");setTimeout(()=>{b.textContent="Copiar";b.classList.remove("done")},1600)}));
"""


def render(pack_path: Path, pack: str, drafts: int, meta: str, now: dt.datetime) -> str:
    title = week_title(pack_path, pack)
    days = sections(pack)
    nav = "".join(f'<a href="#d{i}">{H(chip(t))}</a>' for i, (t, _) in enumerate(days))
    body = "".join(f'<article class="day" id="d{i}"><h2>{H(t)}</h2>{b}</article>' for i, (t, b) in enumerate(days))
    stamp = f"{now.day} de {MONTHS[now.month - 1]}, {now:%H:%M}"
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="postplan-mode" content="adaptive"><meta name="postplan-hand" content="drawn by social-presence page.py from the pack">{meta}<title>{H(title)}</title>
<style>{STYLE}</style></head><body><main>
<h1>{H(title)}</h1>
<p class="lede">"Abrir en X" abre el editor con el texto puesto: revisas, adjuntas la foto o el video si dice, y publicas tú. "Copiar" copia el bloque para pegarlo donde dice.</p>
<nav>{nav}</nav>
{body}
<p class="foot">Todo pasó el lint de señales de IA ({drafts} borradores, 0 hallazgos). Actualizado el {stamp}.</p>
</main><script>{SCRIPT}</script></body></html>'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pack", type=Path)
    parser.add_argument("--out", type=Path, help="default: <data>/plans/<pack name>-phone.html")
    parser.add_argument("--data", type=Path, default=DATA)
    args = parser.parse_args(argv)
    if not args.pack.is_file():
        print(f"no such pack: {args.pack}", file=sys.stderr)
        return 2
    pack = args.pack.read_text(encoding="utf-8")
    drafts = lint.drafts_of(pack, True, "any")
    if not drafts:
        print(f"{args.pack}: no ```post blocks", file=sys.stderr)
        return 2
    findings = [f for d in drafts for f in lint.lint_draft(d, str(args.pack))]
    if findings:
        for finding in findings:
            print(finding, file=sys.stderr)
        print(f"{len(findings)} lint findings: fix the pack, then build the page", file=sys.stderr)
        return 1
    out = args.out or args.data / "plans" / f"{args.pack.stem}-phone.html"
    try:
        page = render(args.pack, pack, len(drafts), draft_meta(out), dt.datetime.now(ZONE))
    except Refused as err:
        print(f"{args.pack}: {err}; fix the pack, then build the page", file=sys.stderr)
        return 1
    shown = page.count('<div class="post">') - page.count('<span class="seg">') + page.count('<span class="seg">1 de ')
    if shown != len(drafts):
        print(f"{args.pack}: the lint read {len(drafts)} drafts and the page would show {shown}; "
              "every draft goes inside a closed fence under a `## ` day", file=sys.stderr)
        return 1
    if any(ch in page for ch in BANNED):
        for line in banned_lines(pack):
            print(f"{args.pack}: {line}: an em dash or middle dot, which Postplan refuses", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
