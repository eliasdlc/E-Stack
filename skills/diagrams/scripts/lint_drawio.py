#!/usr/bin/env python3
"""lint_drawio.py FILE.drawio

Checks the BPMN rules the thesis diagrams kept breaking (9 Oct 2026: diamonds
with the question outside them, empty diamonds, a diamond wired to another
diamond), on every page of a draw.io file, plain or compressed:

- gateway-question: a diamond (rhombus) carries its question in its own text,
  ending in "?" ;
- gateway-branches: every edge leaving a diamond is labeled (Si/No, Yes/No or
  the condition), and there are at least two;
- gateway-chain: a diamond does not connect straight to another diamond;
- edge-ends: every edge has a source and a target;
- orphan: no shape is left unconnected (text labels and containers excepted).

Prints one line per problem with the rule, the page and the cell id, and exits
1 when there is any, 0 when the diagram is clean.
"""
from __future__ import annotations

import base64
import html
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib


def pages(path: str) -> list[tuple[str, ET.Element]]:
    root = ET.parse(path).getroot()
    out = []
    diagrams = root.findall("diagram") if root.tag == "mxfile" else []
    if root.tag == "mxGraphModel":
        return [("page 1", root)]
    for i, d in enumerate(diagrams, 1):
        name = d.get("name") or f"page {i}"
        model = d.find("mxGraphModel")
        if model is None and (d.text or "").strip():
            raw = base64.b64decode(d.text.strip())
            xml = urllib.parse.unquote(zlib.decompress(raw, -15).decode("utf-8"))
            model = ET.fromstring(xml)
        if model is not None:
            out.append((name, model))
    return out


def text(value: str | None) -> str:
    value = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return " ".join(value.split())


def style(cell: ET.Element) -> dict[str, str]:
    out = {}
    for part in (cell.get("style") or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
        elif part.strip():
            out[part.strip()] = "1"
    return out


def is_diamond(cell: ET.Element) -> bool:
    s = style(cell)
    return s.get("shape") == "rhombus" or "rhombus" in s or "gateway" in (s.get("shape") or "")


def lint(path: str) -> list[str]:
    problems = []
    for page, model in pages(path):
        cells = {c.get("id"): c for c in model.iter("mxCell")}
        vertices = {i: c for i, c in cells.items() if c.get("vertex") == "1"}
        edges = [c for c in cells.values() if c.get("edge") == "1"]
        touched = set()
        for e in edges:
            src, tgt = e.get("source"), e.get("target")
            if not src or not tgt:
                problems.append(f"edge-ends [{page}] edge {e.get('id')}: needs both a source and a target")
            touched.update(x for x in (src, tgt) if x)
        for vid, v in vertices.items():
            if not is_diamond(v):
                continue
            q = text(v.get("value"))
            if not q:
                problems.append(f"gateway-question [{page}] diamond {vid}: empty; the question goes inside it")
            elif not q.endswith("?"):
                problems.append(f"gateway-question [{page}] diamond {vid}: '{q}' is not a question ending in '?'")
            out = [e for e in edges if e.get("source") == vid]
            if len(out) < 2:
                problems.append(f"gateway-branches [{page}] diamond {vid}: {len(out)} outgoing edge(s); a decision needs two or more")
            for e in out:
                label = text(e.get("value"))
                if not label:
                    kids = [c for c in cells.values() if c.get("parent") == e.get("id") and text(c.get("value"))]
                    label = text(kids[0].get("value")) if kids else ""
                if not label:
                    problems.append(f"gateway-branches [{page}] edge {e.get('id')} from diamond {vid}: unlabeled; write Si/No or the condition")
                tgt = cells.get(e.get("target") or "")
                if tgt is not None and is_diamond(tgt):
                    problems.append(f"gateway-chain [{page}] diamond {vid} -> diamond {tgt.get('id')}: put an activity between two decisions")
        for vid, v in vertices.items():
            s = style(v)
            if vid in touched or "text" in s or s.get("container") == "1" or "swimlane" in s or "group" in s:
                continue
            parent = cells.get(v.get("parent") or "")
            if parent is not None and parent.get("vertex") == "1":
                if parent.get("id") in touched or "swimlane" in style(parent) or parent.get("vertex") == "1":
                    continue
            if parent is not None and parent.get("edge") == "1":
                continue
            if any(c.get("parent") == vid for c in vertices.values()) and any(
                    c.get("id") in touched for c in vertices.values() if c.get("parent") == vid):
                continue
            problems.append(f"orphan [{page}] shape {vid} '{text(v.get('value'))[:40]}': not connected to anything")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: lint_drawio.py FILE.drawio", file=sys.stderr)
        return 2
    problems = lint(argv[0])
    for p in problems:
        print(p)
    print("clean" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
