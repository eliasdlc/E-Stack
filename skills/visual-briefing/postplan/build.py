#!/usr/bin/env python3
"""Prepare and upload a Postplan document.

  python3 build.py doc.html [--description "..."] [--check]
  python3 build.py doc.html --new --type decisions [--title "..."] [--lang es]
  python3 build.py doc.html --new --mode adaptive [--title "..."] [--lang es]

Two modes, declared in the head. `<meta name="postplan-mode" content="adaptive">`
publishes a page whose composition is its own: no bar, hero, kicker, stats,
index, sections, type or word ceiling is required. No meta, or content
"legacy", is the original recipe and keeps every check it always had. Any other
value is refused. Both modes keep the size limit, the blocked <link>, remote
assets and em dash, the accessibility of questions, the identity of components
and the browser probe for text size and overflow.

--new --type writes a legacy document with the chrome already in it (the bar, the hero,
the index, a section, the provenance) plus the style block and the script of
design.html, copied at run time so the two can never drift apart. Everything to
replace is marked [[like this]] and a leftover marker is a refusal.

What it does, in order:
  1. Re-encodes every embedded PNG and JPEG as WebP, keeping whichever is
     smaller. No fonts are injected: postplan.dev refuses them (see FONT_NOTE).
  2. Validates what Postplan rejects (<link>, <script src>, remote <img>, em
     dashes, 512 KB) and what this skill rejects: an embedded font, a missing
     postplan-type, a document over its type's word ceiling, a question that
     shows nothing, a broken option.
  3. Renders the document at 390 in headless Chromium and refuses text under
     11 px inside a component and anything clipped inside one.
  4. Uploads. If the HTML already has <meta name="postplan-draft" content="id">,
     it updates that draft (same URL). If not, it creates one, writes the meta
     into the file and uploads again so the remote copy carries the id too.
     A page with <meta name="postplan-round"> (draw.py writes it when he may
     answer from the page) is posted straight to the API with its round as
     metadata.round, because the npm CLI cannot send one; a refusal of the
     round is printed by name with what to do. Any other page goes through the
     CLI as before.

--check does 1 to 3 without uploading and WITHOUT writing the file.

Before any of that it asks who drew the page. A page comes from `draw.py`, which
stamps it with a fingerprint of what it drew; a page with no stamp, or one edited
after it was drawn, is refused. --hand "reason" publishes a page written by hand
(a source from before draw.py, or a shape draw.py cannot make) and writes the
reason into the document as <meta name="postplan-hand">. Another program that
draws its own page (the scorecard, the social pack) writes that meta itself.
"""
import argparse, base64, html as htmllib, importlib.util, json, os, re, subprocess, sys, urllib.error, urllib.request
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.join(HERE, "design.html")
MAX_BYTES = 8 * 1024 * 1024

# The documents are served by our own instance (eliasdlc/postplan on Vercel,
# Supabase behind it), whose CSP sends `font-src data:`. The hosted service does
# not, which is why every font embedded before 19 sep was refused by the browser
# and 138 documents rendered in the system stack without anyone noticing.
HOST = "https://plan.decruce.dev"
SECRETS = os.path.expanduser("~/.config/secrets/postplan.env")
FONTS_CSS = os.path.join(HERE, "fonts", "fonts.css")
WARN_BYTES = 6 * 1024 * 1024
IMG_DATA = re.compile(r"data:image/(png|jpeg|jpg);base64,([A-Za-z0-9+/=]+)")


def to_webp(html, quality=82):
    """Re-encode every embedded PNG and JPEG as WebP, keeping whichever is smaller.

    Measured on 19 sep: the two captures of tarjetas-ciclos.html went from
    176 KB to 59 KB, 67 % less, with no visible loss at reading size. Captures
    are the only way a document carries the project's real typeface, so their
    bytes are the ones worth buying back.
    """
    try:
        from PIL import Image
    except ImportError:
        return html, "Pillow is not installed: images stay as they are"
    import io
    before = after = 0
    count = 0

    def one(m):
        nonlocal before, after, count
        raw = base64.b64decode(m.group(2))
        before += len(raw)
        try:
            im = Image.open(io.BytesIO(raw))
            im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
            buf = io.BytesIO()
            im.save(buf, "WEBP", quality=quality, method=6)
            new = buf.getvalue()
        except Exception:
            after += len(raw)
            return m.group(0)
        if len(new) >= len(raw):
            after += len(raw)
            return m.group(0)
        after += len(new)
        count += 1
        return "data:image/webp;base64," + base64.b64encode(new).decode()

    out = IMG_DATA.sub(one, html)
    if not before:
        return html, None
    return out, f"{count} image(s) to webp: {before // 1024} KB to {after // 1024} KB"


def weight_report(html):
    """Where the bytes are, so a document over the ceiling is fixed at its cause."""
    fonts = sum(len(b) for b in re.findall(r"data:font/\w+;base64,([A-Za-z0-9+/=]+)", html))
    imgs = sum(len(b) for b in re.findall(r"data:image/\w+;base64,([A-Za-z0-9+/=]+)", html))
    svg = sum(len(m) for m in re.findall(r"<svg.*?</svg>", html, re.S))
    total = len(html.encode())
    # base64 is counted as it weighs in the file, not decoded, so the rows sum
    # to the total and the biggest one is really the biggest one.
    rows = [
        ("images, in base64", imgs),
        ("inline svg", svg),
        ("fonts, in base64", fonts),
        ("markup, css and js", max(0, total - fonts - imgs - svg)),
    ]
    return total, rows


CQ_UNIT = re.compile(r"\d\s*(cqw|cqh|cqi|cqb|cqmin|cqmax)\b", re.I)


def self_querying_containers(html):
    """A container does not query itself.

    If a rule declares container-type and also uses cq* units in that same
    rule, the unit does NOT resolve against that element: it climbs to the
    nearest ancestor container and, if there is none, falls back to the
    viewport. The classic symptom is a mock that looks perfect at 390px and
    gigantic on desktop, because at 390px the viewport and the container
    happen to measure almost the same.

    The fix is to move container-type to the wrapper and leave the cq* units
    on the child.
    """
    bad = []
    for css in re.findall(r"<style[^>]*>(.*?)</style>", html, re.S | re.I):
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
            sel, body = m.group(1).strip(), m.group(2)
            if sel.startswith("@"):
                continue
            establishes = re.search(r"container-type\s*:", body) or \
                re.search(r"(^|;)\s*container\s*:", body)
            if establishes and CQ_UNIT.search(body):
                bad.append(sel.splitlines()[-1].strip()[:70])
    return bad


FONT_SIZE_DECL = re.compile(r"font-size\s*:\s*([^;\"'}<]+)", re.I)


def nocomments(text):
    """The text without CSS comments: a rule quoted in a comment is not a rule."""
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def uncapped_cq_samples(html):
    """A sample scaled with cqw and no ceiling.

    font-size:calc(100cqw/N) with N under 20 is an enlarged sample (a whole
    phone uses N around 23). When the grid collapses to one column, 100cqw
    starts measuring the whole screen and the sample comes out gigantic on
    mobile. The fix is the ceiling: font-size:min(calc(100cqw/N),17px).
    """
    bad = []
    for m in FONT_SIZE_DECL.finditer(nocomments(html)):
        val = m.group(1)
        cm = re.search(r"calc\(\s*100(?:cqw|cqi)\s*/\s*([\d.]+)\s*\)", val, re.I)
        if not cm or float(cm.group(1)) >= 20:
            continue
        if re.search(r"\b(?:min|clamp)\s*\(", val, re.I):
            continue
        bad.append(val.strip()[:60])
    return bad


# -- system classes that leak ------------------------------------------------

def bleeding_classes():
    """Classes of design.html that style without asking for an ancestor.

    A class like that applies anywhere in the document. If a mock reuses it
    for something else, the system paints over it silently: `.pill` adds
    uppercase and a ::before dot, `.tl` adds a grid and a top border on every
    child div. The symptom is a deformed mock nobody connects to the system
    CSS, because the guilty selector is not in the mock.

    It is computed from design.html itself so it cannot drift out of sync: a
    class enters if some selector starts with it and with it alone.
    """
    try:
        css = open(DESIGN, encoding="utf-8").read()
    except OSError:
        return set()
    style = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", css, re.S | re.I))
    style = re.sub(r"/\*.*?\*/", "", style, flags=re.S)
    out, ctx = set(), {}
    for m in re.finditer(r"([^{}]+)\{[^{}]*\}", style):
        sel = m.group(1).strip()
        if sel.startswith("@"):
            continue
        for part in sel.split(","):
            # (combinator, compound): the combinator matters because `>` only
            # reaches a direct child and a mock is always wrapped.
            toks = [t for t in re.split(r"\s*([>+~])\s*|\s+", part.strip()) if t]
            if not toks:
                continue
            first = toks[0]
            if not first.startswith("."):
                continue
            names = re.findall(r"\.([A-Za-z0-9_-]+)", first)
            if len(names) != 1:
                continue
            root = names[0]
            if len(toks) == 1:
                # `.C{...}` paints any element with that class, anywhere.
                out.add(root)
                continue
            i, child_only = 1, False
            while i < len(toks):
                t = toks[i]
                if t in (">", "+", "~"):
                    child_only = True
                    i += 1
                    continue
                if not child_only:
                    if t.startswith("."):
                        n = re.findall(r"\.([A-Za-z0-9_-]+)", t)
                        if len(n) == 1:
                            ctx.setdefault(root, set()).add(n[0])
                    elif re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", t):
                        # `.pick small`, `.tl div`: styles the TAG inside the
                        # block, so it reaches a mock nested there. A mixed
                        # compound (`b.l`) demands both things and does not count.
                        ctx.setdefault(root, set()).add("<" + t + ">")
                child_only = False
                i += 1
    return out, ctx


# Mock roots: inside them the document draws its own world and no system class
# has any business there.
MOCK_ROOTS = ("phone", "stage", "st")


class _Scan(HTMLParser):
    """Walks the HTML carrying the stack of ancestors.

    It collects four things: system classes used inside a mock, the
    structure of the questions, whether each question shows something, and
    the chrome of the page (the blocks the stylesheet is written for).
    """

    def __init__(self, reserved, ctx):
        super().__init__(convert_charrefs=True)
        self.reserved = reserved
        self.ctx = ctx
        self.stack = []
        self.bleed = []          # (class, mock root)
        self.questions = {}      # data-q -> dict
        self.qstack = []
        self.has_ans = False
        self.stages = []         # every .st: its inline style and the text it holds
        # Counted outside any mock: a .stat drawn inside a component is part of
        # the component, not of the header.
        self.chrome = dict.fromkeys(
            ("bar", "hero", "kick", "lede", "index", "prov", "stat", "section", "h1", "h1_hero",
             "route", "route_step"), 0)
        self.voids = {"br", "hr", "img", "input", "meta", "link", "source", "use", "path",
                      "circle", "rect", "line", "polyline", "polygon", "ellipse", "col",
                      "area", "base", "embed", "param", "track", "wbr"}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if a.get("id") == "ans":
            self.has_ans = True

        depth_roots = [c for fr in self.stack for c in fr["roots"]]
        if depth_roots:
            ancestors = {k for fr in self.stack for k in fr["cls"]}
            inherited = set()
            for anc in ancestors:
                # Mock roots expose their own children (.stage>.st,
                # .phone figcaption): that is the API, not a leak.
                if anc in MOCK_ROOTS:
                    continue
                inherited |= self.ctx.get(anc, set())
            if ("<" + tag + ">") in inherited:
                src = next(k for k in sorted(ancestors)
                           if k not in MOCK_ROOTS and ("<" + tag + ">") in self.ctx.get(k, set()))
                self.bleed.append(("<" + tag + ">", depth_roots[-1], src))
            for c in cls:
                if c in MOCK_ROOTS:
                    continue
                if c in self.reserved:
                    self.bleed.append((c, depth_roots[-1], None))
                elif c in inherited:
                    src = next(k for k in sorted(ancestors)
                               if k not in MOCK_ROOTS and c in self.ctx.get(k, set()))
                    self.bleed.append((c, depth_roots[-1], src))

        if not depth_roots:
            anc = {c for fr in self.stack for c in fr["cls"]}
            for c in ("bar", "hero", "kick", "lede", "index", "prov", "route"):
                if c in cls:
                    self.chrome[c] += 1
            if tag == "li" and "route" in anc:
                self.chrome["route_step"] += 1
            if "stat" in cls and "stats" in anc:
                self.chrome["stat"] += 1
            if tag == "section":
                self.chrome["section"] += 1
            if tag == "h1":
                self.chrome["h1"] += 1
                if "hero" in anc:
                    self.chrome["h1_hero"] += 1

        qid = a.get("data-q")
        if qid is not None:
            self.questions[qid] = self.questions.get(
                qid, {"count": 0, "opts": [], "visual": False, "single": False, "multi": False})
            self.questions[qid]["count"] += 1
            if "data-single" in a:
                self.questions[qid]["single"] = True
            if "data-multi" in a:
                self.questions[qid]["multi"] = True
            self.qstack.append(qid)

        cur = self.qstack[-1] if self.qstack else None
        if cur:
            if a.get("data-v") is not None:
                self.questions[cur]["opts"].append(
                    {"tag": tag, "v": a.get("data-v"), "pressed": "aria-pressed" in a})
            if tag == "svg" or "stage" in cls or "phone" in cls or tag == "img":
                self.questions[cur]["visual"] = True

        roots = [c for c in cls if c in MOCK_ROOTS]
        st = None
        if "st" in cls and any("stage" in fr["cls"] for fr in self.stack[-1:]):
            st = len(self.stages)
            self.stages.append({"style": a.get("style") or "", "text": "", "q": self.qstack[-1] if self.qstack else None})
        if tag not in self.voids:
            self.stack.append({"tag": tag, "roots": roots, "q": qid, "cls": cls, "st": st})

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        for fr in reversed(self.stack):
            if fr["tag"] in ("style", "script"):
                return
            if fr.get("st") is not None:
                self.stages[fr["st"]]["text"] += text + " "
                return

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                if self.stack[i]["q"] and self.qstack and self.qstack[-1] == self.stack[i]["q"]:
                    self.qstack.pop()
                del self.stack[i:]
                return


def scan(html):
    reserved, ctx = bleeding_classes()
    s = _Scan(reserved, ctx)
    s.crashed = None
    try:
        s.feed(html)
    except Exception as e:  # a silent failure here lets the whole document through
        s.crashed = repr(e)
    return s


DOC_FONTS = re.compile(r"bricolage|figtree|var\(--(sans|display|mono)\)", re.I)


def identity_problems(sc):
    """A component wears the product's identity, never the document's.

    Measured 20 sep: every .st in the corpus inherited the document's Figtree
    and its true black ground, so the options Elias picked between all wore
    the same face whatever the product was. A .st that holds text declares
    its own font-family, background and color on its root, from the repo's
    DESIGN.md, and --font embeds the product's faces so they render."""
    out = []
    for i, st in enumerate(sc.stages, 1):
        if not st["text"].strip():
            continue  # a capture, an svg with no text
        style = st["style"]
        where = "component " + str(i) + (" (question " + st["q"] + ")" if st["q"] else "") + \
            " `" + st["text"].strip()[:40] + "`"
        missing = [k for k, rx in (("font-family", r"font-family\s*:"),
                                   ("background", r"(^|;)\s*background(-color)?\s*:"),
                                   ("color", r"(^|;)\s*color\s*:")) if not re.search(rx, style)]
        if missing:
            out.append(where + " declares no " + ", ".join(missing) + " on its .st root, so it "
                       "inherits the document's: the product's face, ground and ink go there, from "
                       "its DESIGN.md, and --font embeds the face")
            continue
        fam = re.search(r"font-family\s*:\s*([^;]+)", style).group(1)
        if DOC_FONTS.search(fam):
            out.append(where + " wears the document's font (`" + fam.strip() + "`): the product's "
                       "face goes there, embedded with --font Name=path.woff2")
    return out


def structure_problems(sc, composer=True):
    """What breaks a decision without it showing when you look at the page."""
    out = []
    if getattr(sc, "crashed", None):
        out.append("the HTML could not be walked all the way through (" + sc.crashed +
                   "): the structure validation did not cover the document")
    seen = set()
    for qid, q in sorted(sc.questions.items()):
        if q["count"] > 1:
            out.append("data-q=\"" + qid + "\" repeated " + str(q["count"]) +
                       " times: the composer stores a single answer per number")
        if len(q["opts"]) < 2 and not q["single"]:
            out.append("question " + qid + " has " + str(len(q["opts"])) +
                       " options with data-v: a decision needs at least two real ones; "
                       "if there is only one path, mark the block with data-single and present it as taken")
        if q["single"] and len(q["opts"]) != 1:
            out.append("question " + qid + " carries data-single and " + str(len(q["opts"])) +
                       " options: data-single is for a single real path")
        for o in q["opts"]:
            if o["v"] == "X":
                out.append("option " + qid + "X in the markup: the X is Elias's own answer "
                           "and the script adds it; use another letter")
            if o["tag"] != "button":
                out.append("option " + qid + o["v"] + " in <" + o["tag"] +
                           ">: it has to be a <button> or it cannot be touched, not even with a keyboard")
            if not o["pressed"]:
                out.append("option " + qid + o["v"] +
                           " with no aria-pressed: the script cannot mark it")
        letters = [o["v"] for o in q["opts"]]
        if len(set(letters)) != len(letters):
            out.append("question " + qid + " repeats an option letter: " + " ".join(letters))
        seen.add(qid)
    if composer and seen and not sc.has_ans:
        out.append("there are questions and the answers composer is missing (element with id=\"ans\")")
    return out


START_HERE = ("\n  Start the file with `python3 build.py <file.html> --new --type " +
              "<type>`: it writes the chrome the stylesheet is written for.")


def chrome_problems(sc, html):
    """The shape of the page, which nothing used to check.

    Measured on 19 sep over two documents of the same type built by two agents
    from this same skill: one carried the bar, the hero and 9 <section>, the
    other none of them. The stylesheet only sizes an h1 inside .hero, so the
    second one rendered its headline at 32 px on a 1440 screen against 60, with
    its title flush against the top edge and every block in one flat column.
    """
    t = doc_type(html) or ""
    c = sc.chrome
    out = []
    if not c["h1"]:
        out.append("no h1: the conclusion, with its number, is the first thing in the document")
    if not c["hero"]:
        out.append('no .hero: the header is <div class="hero"><div class="wrap">, and it '
                   "holds the kicker, the h1, the lede and the stats. Outside it the h1 has "
                   "no size rule of its own and the browser renders it at 32 px at any width" + START_HERE)
    elif c["h1"] and not c["h1_hero"]:
        out.append("the h1 sits outside the .hero: only `.hero h1` carries the "
                   "clamp(32px,5.5vw,60px), and only .hero carries the top padding that keeps "
                   "the title off the edge of the screen")
    if not c["kick"]:
        out.append("no .kick: one line above the h1 with the project, the type and the date")
    if not c["lede"]:
        out.append("no .lede: two lines under the h1 with at least three numbers or paths in them. "
                   "`.sub` is the subtitle of a section, not the lede")
    if not c["prov"]:
        out.append("no .prov: every document closes with the line that says which files, commits "
                   "and dates the data came from, and what was estimated")
    if t != "note":
        if not 3 <= c["stat"] <= 4:
            out.append(str(c["stat"]) + " .stat in the header: three or four, and the fourth "
                       "counts what is NOT verified")
        if not c["section"]:
            out.append("no <section>: the body goes in sections, which is what gives each block "
                       "its 56 px and its separating line. Without them the whole document is one "
                       "column with nothing between one subject and the next" + START_HERE)
        if c["section"] + len(sc.questions) >= 3 and not c["index"]:
            out.append("no .index with " + str(c["section"] + len(sc.questions)) +
                       " blocks to reach: every finding and every question, by title, as a link")
        if c["section"] >= 3 and not c["bar"]:
            out.append("no sticky .bar with " + str(c["section"]) + " sections: the bar is what "
                       "says where he is in a document he reads on a phone")
    # A document that asks for a pick sets work off, and until 19 sep it never
    # said what work. Measured over 167 documents: 18 carried a heading that
    # said what followed, and none of the six types had a place for it.
    if t in ASKS:
        if not c["route"]:
            out.append('no <ol class="route">: a document that asks for a pick sets work off, '
                       "and the route is what says what it goes through. One <li> per step, each "
                       "with what it touches, what closes it, and .you on the one that needs him")
        elif c["route_step"] < 2:
            out.append(str(c["route_step"]) + " step(s) in the .route: a route of one step is a "
                       "sentence. Write the steps, in order, or say in the lede that the pick "
                       "changes nothing yet")
    return out


def bleed_problems(sc):
    out = []
    seen = set()
    for cls, root, src in sc.bleed:
        if (cls, root, src) in seen:
            continue
        seen.add((cls, root, src))
        sel = cls if cls.startswith("<") else "." + cls
        where = "the system's `." + src + " " + (sel[1:-1] if cls.startswith("<") else sel) + \
                "` reaches this mock" if src else \
                "the Postplan CSS styles `" + sel + "` anywhere"
        out.append(
            ("tag " if cls.startswith("<") else "class ") + "`" + cls.strip("<>") +
            "` used inside a ." + root + ": " + where + ", so it paints "
            "over it (uppercase, ::before, grid, borders) and the mock comes out deformed without "
            "the guilty selector being in sight. Rename it in the mock")
    return out


FILLER = re.compile(
    r"(as today|as it is\b|as[- ]is\b|as now|as until now|leave (it|them) ?(as is|alone|the same|unchanged)|"
    r"\bkeep\b|do nothing|no change|without changes|stay the same|status quo|\bfree\b|"
    r"como hoy|como est[aá]|como ahora|como hasta ahora|dejar(lo|la)? (as[ií]|igual)|"
    r"mantener(lo|la)?\b|no hacer nada|no cambiar|sin cambios|seguir (igual|como)|"
    r"\blibre\b)", re.I)


def option_titles(html):
    """Visible title of every option, per question: {qid: [(letter, title)]}."""
    out = {}
    blocks = re.split(r'(?=<div class="q[^"]*"[^>]*data-q=)', html)
    for b in blocks:
        # The last block runs to the end of the file: cut it at whatever is no
        # longer a question, or the composer and the footer come in as options.
        b = re.split(r'<div class="answers|<p class="prov', b)[0]
        m = re.match(r'<div class="q[^"]*"[^>]*data-q="([^"]+)"', b)
        if not m:
            continue
        qid = m.group(1)
        for v, inner in re.findall(r'data-v="([A-Z])"[^>]*>(.*?)</button>', b, re.S):
            t = re.sub(r"<small>.*?</small>", "", inner, flags=re.S)
            t = re.sub(r"<span class=\"(rec|pk-st)\">.*?</span>", "", t, flags=re.S)
            t = re.sub(r"<(svg|span class=\"stage)[^>]*>.*", "", t, flags=re.S)
            t = htmllib.unescape(re.sub(r"<[^>]+>", " ", t))
            t = re.sub(r"\s+", " ", t).strip()
            out.setdefault(qid, []).append((v, t[:90]))
    return out


def undecidable(sc):
    """Questions that do not show what they decide. A machine can see it:
    either there is a .stage, a phone frame, an SVG or an image inside the block,
    or there is not."""
    out = []
    for qid, q in sorted(sc.questions.items()):
        if not q["visual"]:
            out.append("question " + qid + " does not show what it decides: with no .stage, no phone "
                       "frame, no SVG and no image, you have to scroll up to find the "
                       "component, and a decision is taken looking at what it decides. If there "
                       "really is nothing to draw, draw the consequence: two states "
                       "of the same row, a before and an after")
    return out


PROGRESS_PERCENT = re.compile(
    r"(\d{1,3})\s*%[^<.]{0,60}?(implement|verif|complet|cubiert|cover|listo|done|avance|progres|de la entrega|of the delivery)"
    r"|(implement|verif|complet|cubiert|cover|listo|done|avance|progres|of the delivery)[^<.]{0,60}?(\d{1,3})\s*%",
    re.I)


def invented_progress(html):
    """A progress percentage with no table it comes from. The totals of a
    delivery are counted over rows; a percentage that does not come from rows is
    invented. It does not look at any percentage: only the one claiming progress."""
    m = PROGRESS_PERCENT.search(nocomments(html))
    if not m:
        return []
    rows = len(re.findall(r"<tr\b", html, re.I))
    if rows >= 3:
        return []
    return ["progress percentage (\"" + m.group(0).strip()[:60] + "\") with no table it comes "
            "from: the totals are counted over rows, one per requirement, and a percentage that "
            "does not come from rows is invented. Put the table in or take the percentage out"]


def warnings_for(html, sc):
    out = []
    titles = option_titles(html)
    for qid, q in sorted(sc.questions.items()):
        for v, t in titles.get(qid, []):
            if FILLER.search(t):
                out.append("option " + qid + v + " sounds like filler (\"" + t[:50] + "\"): "
                           "an option is something Elias could really pick. If keeping is "
                           "real, say why; if it is not, drop it and find one that is")
        if len(q["opts"]) == 2 and not q["multi"]:
            out.append("question " + qid + " is binary: before uploading, look for the third "
                       "option that dissolves the tradeoff, or the version of A that absorbs what "
                       "B protects")
    for m in FONT_SIZE_DECL.finditer(nocomments(html)):
        val = m.group(1)
        if re.search(r"100(?:cqw|cqi)", val, re.I) and re.search(r"\bmin\s*\(", val):
            out.append("font-size with a ceiling `" + val.strip()[:50] + "`: if the box carries no "
                       "max-width, the type stops growing and the box keeps going, and the component "
                       "reflows differently on desktop. The component is authored at its real size in a .stage")
            break
    return out


def validate(html):
    problems = []
    mode = doc_mode(html)
    if mode not in MODES:
        problems.append('unknown postplan-mode "' + mode + '": use ' + " or ".join(MODES) +
                        ", or no meta for the legacy recipe")
    adaptive = mode == "adaptive"
    if re.search(r"<link\s[^>]*href=", html, re.I):
        problems.append("<link> present: Postplan blocks it; embed the font with --font NAME=PATH.woff2")
    if re.search(r"<script[^>]+src=", html, re.I):
        problems.append("<script src> present: inline JS only")
    if re.search(r"""(src|href)=["']https?://fonts\.""", html, re.I):
        problems.append("reference to fonts.googleapis/gstatic: it has to be embedded")
    if re.search(r"""<img[^>]+src=["']https?://""", html, re.I):
        problems.append("remote <img>: embed the image in base64 or remove it")
    if "—" in html:
        problems.append("em dash (U+2014) in the document")
    if "/*FONTS*/" in html:
        problems.append("the /*FONTS*/ marker is still unfilled")
    left = re.findall(r"\[\[([^\]]{0,60})\]\]", html)
    if left:
        problems.append(str(len(left)) + " placeholder(s) from --new still in the document: [[" +
                        "]], [[".join(dict.fromkeys(left[:4])) + "]]")

    for sel in self_querying_containers(html):
        problems.append(
            "container that queries itself in `" + sel + "`: it declares "
            "container-type and uses cq* units in the same rule, so they "
            "resolve against the viewport. Move container-type to the wrapper "
            "and leave the cq* on the child. It looks fine at 390px and broken on desktop")
    sc = scan(html)
    if not adaptive:
        # The system stylesheet and its chrome exist only in a legacy document,
        # so the reserved-class and layout rules have nothing to protect here.
        problems += bleed_problems(sc)
        problems += chrome_problems(sc, html)
    problems += structure_problems(sc, composer=not adaptive)
    problems += identity_problems(sc)
    if not adaptive:
        problems += undecidable(sc)
    problems += invented_progress(html)
    for val in uncapped_cq_samples(html):
        problems.append(
            "uncapped cqw sample `font-size:" + val + "`: when the grid "
            "collapses to one column, 100cqw is the whole screen and the sample "
            "comes out gigantic on mobile. Use font-size:min(calc(100cqw/N),17px)")
    size = len(html.encode())
    if size > MAX_BYTES:
        problems.append(f"{size} bytes, over the {MAX_BYTES} Postplan accepts")
    problems = list(dict.fromkeys(problems))
    return problems, size, list(dict.fromkeys(warnings_for(html, sc)))


def oversize_help(html, size):
    """What to say when the document does not fit.

    The ceiling is Postplan's, not the document's: it is never a reason to
    lower the fidelity of a component. Fonts and images are the cause in
    practice, and both have a cheaper form. When neither is left, the document
    goes out as a local file and Elias opens it from disk.
    """
    if size <= MAX_BYTES:
        return ""
    total, rows = weight_report(html)
    lines = ["", f"where the {total // 1024} KB are:"]
    for name, b in sorted(rows, key=lambda r: -r[1]):
        lines.append(f"  {b // 1024:>5} KB  {name}")
    lines += [
        "",
        "in this order, and none of them touches the components:",
        "  1. the fonts are already subset; drop a family the document does not use",
        "  2. re-encode the captures smaller (the webp pass already ran)",
        "  3. cut prose and repeated sections, which is free",
        "  4. split it in two documents by subject, each with its own decisions",
        "",
        "if the components are what does not fit, they win: build the file, do not",
        "upload it, and hand over the local path saying the limit is what stopped it.",
    ]
    return "\n".join(lines)


# Every document declares its type in <meta name="postplan-type">. The ceiling
# is the type's frame plus what each decision or finding is allowed to cost.
# Measured on 19 sep over 138 documents: median 2,498 words, 12.5 minutes of
# reading, of which the part Elias needs (h1, lede, stats, titles) was a median
# of 224. The ceiling is what stops the other 2,274 from being written.
# The ceiling is the type's frame plus what each unit of content is allowed to
# cost: a question, a finding, and a table row. Measured on 19 sep over 138
# documents: median 2,498 words of which Elias needed 224; median finding 68
# words, median table row 17. The first version of this table counted only
# findings, so an audit that also asked four questions was born condemned.
#                frame  per finding  per question  per table row
TYPES = {
    "note":       (250,   0,   0,  20),
    "decisions":  (200,   0, 150,  20),
    "findings":   (250, 120, 150,  20),
    "draft":      (250, 120, 150,  20),
    "briefing":   (600,   0, 150,  20),
    "comparison": (350,   0,  80,  20),
}

PLAYWRIGHT_MISSING = (
    "the render check did not run (playwright not found), so nothing measured "
    "the components at 390: no floor on text size, no clipping check, no word count")


ASKS = {"decisions", "draft", "comparison"}  # the types that end in an answer from Elias


def scaffold(path, dtype, title, lang):
    """Write the chrome of a new document, with the style and the script of
    design.html copied verbatim so the two can never drift apart.

    Everything the agent has to replace is marked [[like this]], and validate()
    refuses a document that still carries one.
    """
    if dtype not in TYPES:
        sys.exit("unknown type '" + str(dtype) + "': " + ", ".join(sorted(TYPES)))
    if os.path.exists(path):
        sys.exit(path + " already exists: --new never overwrites a document")
    design = open(DESIGN, encoding="utf-8").read()
    style = re.search(r"<style>.*?</style>", design, re.S).group(0)
    script = re.search(r"<script>.*?</script>", design, re.S).group(0)
    title = title or "[[the conclusion, with its number]]"
    note = dtype == "note"

    head = ['<!doctype html>', '<html lang="' + lang + '">', '<head>',
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<meta name="postplan-type" content="' + dtype + '">',
            '<title>' + title + '</title>', style, '</head>', '<body>', '']
    body = []
    if not note:
        body += ['<header class="bar"><div class="wrap">',
                 '  <a class="logo" href="#top"><i></i>[[project]]</a>',
                 '  <nav id="nav"><a href="#s1">[[section]]</a></nav>',
                 '</div></header>', '']
    body += ['<main id="top">', '',
             '<div class="hero"><div class="wrap">',
             '  <p class="kick">[[project]], ' + dtype + ', [[date]]</p>',
             '  <h1>' + title + '</h1>',
             '  <p class="lede">[[two lines, three numbers or paths between them]]</p>']
    if not note:
        body += ['  <div class="stats">',
                 '    <div class="stat"><div class="big">[[n]]</div><span>[[what it counts]]</span></div>',
                 '    <div class="stat"><div class="big">[[n]]</div><span>[[what it counts]]</span></div>',
                 '    <div class="stat"><div class="big">[[n]]</div><span>[[what is NOT verified]]</span></div>',
                 '  </div>']
    if dtype in ASKS:
        body += ['  <div class="ask">',
                 '    <svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"/>'
                 '<path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 2-3 4"/><path d="M12 17h.01"/></svg>',
                 '    <div><b>[[what I need from you]]</b>[[n decisions, below, answer with the code]]</div>',
                 '  </div>']
    if not note:
        body += ['  <nav class="index"><a href="#s1"><i>01</i>[[the section, by its title]]</a></nav>']
    body += ['</div></div>', '']
    if dtype in ASKS:
        body += ['<div class="wrap">',
                 '  <h3 class="rv">What happens after you pick</h3>',
                 '  <ol class="route rv">',
                 '    <li><b>[[what the step does]]</b><span>[[what it touches: the files]]</span>'
                 '<i>[[what closes it]]</i></li>',
                 '    <li class="you"><b>[[the step that needs him]]</b>'
                 '<span>[[what it touches]]</span><i>[[what closes it]]</i></li>',
                 '  </ol>',
                 '</div>', '']
        body += ['<!-- The questions go HERE, before the sections, which are their evidence.',
                 '     The block, whole, is in design.html, beside this file. Each one ends in the composer:',
                 '     <div class="answers rv"><span class="hint">Your answer</span>'
                 '<code id="ans">no answer yet</code><button id="copy" type="button">Copy</button></div> -->', '']
    if not note:
        body += ['<section id="s1"><div class="wrap">',
                 '  <div class="sh rv"><span class="n">01</span><h2>[[a heading that is a fact: subject, verb, consequence]]</h2></div>',
                 '  <!-- The body of this type is in design.html, beside this file -->',
                 '</div></section>', '']
    body += ['<p class="prov wrap"><b>Provenance.</b> [[files, commits, dates, and what was estimated]]</p>',
             '', '</main>', '', script, '</body>', '</html>', '']
    open(path, "w", encoding="utf-8").write("\n".join(head + body))
    print(path + "  " + dtype + ", " + str(len("\n".join(head + body).encode()) // 1024) +
          " KB. Replace every [[marker]]; the recipe for the body is in design.html, beside this file")


def scaffold_adaptive(path, title, lang):
    """A bare adaptive page: the head, a neutral light and dark theme, nothing else.

    No chrome is written because none is required. The body is whatever the
    content needs, composed by whoever fills it.
    """
    if os.path.exists(path):
        sys.exit(path + " already exists: --new never overwrites a document")
    title = title or "[[title]]"
    text = "\n".join([
        '<!doctype html>', '<html lang="' + lang + '">', '<head>', '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="postplan-mode" content="adaptive">',
        '<title>' + title + '</title>',
        '<style>',
        ':root{color-scheme:light dark;--background:#fff;--foreground:#111;--muted:#666;--border:#ddd}',
        '@media (prefers-color-scheme:dark){:root{--background:#0b0b0b;--foreground:#eee;--muted:#999;--border:#2a2a2a}}',
        'body{margin:0;background:var(--background);color:var(--foreground);font:17px/1.5 system-ui,sans-serif}',
        '</style>', '</head>', '<body>', '<!-- Compose from what the content needs. -->', '</body>', '</html>', ''])
    open(path, "w", encoding="utf-8").write(text)
    print(path + "  adaptive, " + str(len(text.encode())) + " bytes. No chrome is required; replace [[markers]]")


def embed_font(html, spec):
    """NAME=PATH.woff2 becomes an @font-face with the file inline, once: a
    document uploaded twice keeps one copy. The serving CSP allows font-src
    data:, which is what makes the product's face render inside a .st."""
    if "=" not in spec:
        sys.exit("--font takes NAME=PATH.woff2, got " + spec)
    name, path = spec.split("=", 1)
    name = name.strip().strip("\"'")
    if re.search(r"font-family\s*:\s*['\"]?" + re.escape(name) + r"['\"]?\s*;[^}]*src\s*:\s*url\(data:", html, re.I):
        return html, ""
    if not os.path.isfile(path):
        sys.exit("--font " + name + ": " + path + " does not exist")
    data = base64.b64encode(open(path, "rb").read()).decode()
    kind = "woff2" if path.lower().endswith(".woff2") else "woff" if path.lower().endswith(".woff") else "truetype"
    face = ("@font-face{font-family:'" + name + "';font-weight:100 900;font-display:swap;"
            "src:url(data:font/" + kind + ";base64," + data + ") format('" + kind + "')}\n")
    if "</style>" not in html:
        sys.exit("--font: the document has no <style> to embed into")
    return html.replace("</style>", face + "</style>", 1), "embedded " + name + " (" + str(len(data) // 1024) + " KB)"


def doc_type(html):
    m = re.search(r'<meta\s+name="postplan-type"\s+content="([a-z-]+)"', html)
    return m.group(1) if m else None


MODES = ("legacy", "adaptive")


def doc_mode(html):
    """The publication mode a page declares: "legacy" when it declares none.

    Anything else is returned as written so the caller can refuse it by name:
    an unknown mode must never fall back to the lenient one.
    """
    m = re.search(r'<meta\s+name="postplan-mode"\s+content="([^"]*)"', html)
    return m.group(1).strip() if m else "legacy"


def render_report(path):
    """What only a browser knows: rendered sizes, clipping, words, screens."""
    script = os.path.join(HERE, "render_check.mjs")
    try:
        r = subprocess.run(["node", script, path, "390"],
                           capture_output=True, text=True, timeout=180)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    line = (r.stdout or "").strip().splitlines()
    if not line:
        return None
    try:
        rep = json.loads(line[-1])
    except json.JSONDecodeError:
        return None
    return None if rep.get("error") else rep


def over_note(html, reason, words, ceiling):
    """Write the exception into the document, where Elias reads it.

    The ceiling blocks; --over is the way past it, and its price is that the
    reason stops being something only the agent knows.
    """
    es = re.search(r'<html[^>]*\blang="es', html, re.I) is not None
    text = (f'<b>Techo excedido.</b> {words} palabras contra {ceiling}: "{reason}"'
            if es else
            f'<b>Over the ceiling.</b> {words} words against {ceiling}: "{reason}"')
    note = f'<p class="prov over">{text}</p>'
    if "</main>" in html:
        return html.replace("</main>", note + "\n</main>", 1)
    return html.replace("</body>", note + "\n</body>", 1)


def render_problems(rep, html, over=None):
    """The refusals a browser can justify and a regex cannot."""
    out, notes = [], []
    if rep is None:
        return [], [PLAYWRIGHT_MISSING]

    if rep["tinyCount"]:
        worst = ", ".join(f'{t["cls"] or "?"} "{t["text"]}" at {t["px"]} px' for t in rep["tiny"][:4])
        out.append(
            f'{rep["tinyCount"]} text node(s) inside a component render under 11 px at 390: '
            f'{worst}. The stage already refuses to scale past the floor, so this is the '
            f'component itself: either its own type is too small (read the token from the '
            f'repo again) or it is a frame where a row would do')
    if rep["clippedCount"]:
        worst = ", ".join(f'{c["cls"] or "?"} ({c["scrollWidth"]} in {c["clientWidth"]})'
                          for c in rep["clipped"][:4])
        out.append(
            f'{rep["clippedCount"]} element(s) clipped inside a component: {worst}. '
            f'Part of what Elias has to choose is off screen. Mark it data-bleeds if '
            f'it really is meant to run past the edge')

    for t in rep.get("wideTables", []):
        out.append(
            f'a table is {t["w"]} px wide in {t["room"]} px of room ("{t["head"][:30]}"), so its '
            f'last column falls off the right edge at 390. Wrap it in <div class="tw"> to let it '
            f'scroll, or drop a column')

    if doc_mode(html) == "adaptive":
        # Length is the page's own business. What a browser can still refuse is
        # the page running past the screen it is read on.
        if rep.get("pageOverflowPx", 0) > 2:
            out.append(
                f'the page is {rep["pageOverflowPx"]} px wider than the 390 px screen it is read on: '
                f'something runs off the right edge (a table, a code block, a fixed width). '
                f'Let it wrap or scroll inside its own box')
        notes.append(f'{rep["words"]} words, {rep["screens"]} screens at 390, no word ceiling in adaptive mode')
        return out, notes

    if doc_mode(html) not in MODES:
        return out, notes  # validate() already refused the mode by name

    kind = doc_type(html)
    if not kind:
        out.append('no <meta name="postplan-type">: declare one of ' + ", ".join(TYPES))
    elif kind not in TYPES:
        out.append(f'unknown postplan-type "{kind}": use one of ' + ", ".join(TYPES))
    else:
        frame, per_f, per_q, per_r = TYPES[kind]
        findings, questions = rep["findings"], rep["questions"]
        rows = rep.get("tableRows", 0)
        ceiling = frame + per_f * findings + per_q * questions + per_r * rows
        parts = [f"{frame} of frame"]
        if per_f * findings:
            parts.append(f"{per_f * findings} for {findings} finding(s)")
        if per_q * questions:
            parts.append(f"{per_q * questions} for {questions} question(s)")
        if per_r * rows:
            parts.append(f"{per_r * rows} for {rows} table row(s)")
        if rep["words"] > ceiling and over:
            notes.append(
                f'{rep["words"]} words against a ceiling of {ceiling}, published with the '
                f'reason "{over}", which is now written at the end of the document')
        elif rep["words"] > ceiling:
            out.append(
                f'{rep["words"]} words, over the {ceiling} a "{kind}" document gets '
                f'({", ".join(parts)}). Cut prose, not components: the sentence that '
                f'carries no grounded claim is the first to go. If the document '
                f'really needs them, say why with --over "the reason", which writes it '
                f'into the document')
        else:
            notes.append(f'{rep["words"]} of {ceiling} words, {rep["screens"]} screens at 390')

    # Three screens, not two: the table of what the agent decided alone is
    # required to sit before anything the document asks for, and it plus the
    # index take about one screen on their own. The pathology this catches is
    # the corpus median, which was screen 8.8.
    if rep["questions"] and rep["firstQuestionAtPx"] and rep["firstQuestionAtPx"] > 2532:
        notes.append(
            f'the first question sits at {rep["firstQuestionAtPx"]} px, screen '
            f'{round(rep["firstQuestionAtPx"] / 844, 1)}: it belongs right after the stats')
    return out, notes


def _draw():
    spec = importlib.util.spec_from_file_location("postplan_draw", os.path.join(HERE, "draw.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def drawn_problem(html, hand=None):
    """Why this page may not go up as it is, or None.

    Measured 1 Sep to 11 Nov 2026: the look of a page only changed when an
    agent wrote it by hand, and the rules on names, counts and words were prose
    nobody ran. draw.py runs them on the data, so the page that goes up is the
    one it drew."""
    draw = _draw()
    stamp = draw.stamp_of(html)
    if stamp is None:
        declared = HAND.search(html)
        if (hand and hand.strip()) or (declared and declared.group(1).strip()):
            return None
        return ("this page was not drawn from data. Write what it holds as JSON "
                "(`draw.py --example decide`, understand or look) and run `draw.py page.json`, which checks "
                "the questions, the names and the words and writes the page. A page that has to be "
                "written by hand goes up with --hand \"the reason\"; another program that draws its own "
                "page declares itself with <meta name=\"postplan-hand\" content=\"drawn by ...\">")
    if stamp != draw.fingerprint(html):
        return ("this page was edited after draw.py drew it, so its checks no longer cover it. "
                "Change the data and run `draw.py page.json` again")
    return None


HAND = re.compile(r'<meta\s+name="postplan-hand"\s+content="([^"]*)">')


def hand_note(html, reason):
    """The reason a page was written by hand travels in it, once."""
    if HAND.search(html) or "<head>" not in html:
        return html
    return html.replace("<head>", '<head>\n<meta name="postplan-hand" content="' +
                        htmllib.escape(reason.strip(), quote=True) + '">', 1)


def draft_id(html):
    m = re.search(r'<meta\s+name="postplan-draft"\s+content="([a-z0-9]+)"', html)
    return m.group(1) if m else None


def upload_env():
    """Our instance, with the key from ~/.config/secrets/postplan.env."""
    env = dict(os.environ)
    env.setdefault("POSTPLAN_API_URL", HOST)
    if "POSTPLAN_API_KEY" not in env and os.path.exists(SECRETS):
        for line in open(SECRETS, encoding="utf-8"):
            k, _, v = line.strip().partition("=")
            if k == "POSTPLAN_BOOTSTRAP_API_KEY":
                env["POSTPLAN_API_KEY"] = v
    return env


def known_draft(path):
    """The draft this file already has on OUR host, if there is one.

    The CLI keeps a map of file path to draft id in ~/.postplan and never
    records which host the draft belongs to, so a document uploaded to
    postplan.dev before 19 sep asked our instance for a draft it never had. A
    HEAD against the host settles it, and it also covers the case the meta
    cannot: a file regenerated from a script, which comes back with no meta at
    all and would otherwise publish a duplicate every run.
    """
    reg = os.path.expanduser("~/.postplan/drafts.json")
    if not os.path.exists(reg):
        return None
    try:
        entry = json.load(open(reg, encoding="utf-8")).get("files", {}).get(path)
    except (json.JSONDecodeError, OSError):
        return None
    did = entry.get("draftId") if isinstance(entry, dict) else entry
    if not did:
        return None
    req = urllib.request.Request(f"{HOST}/d/{did}", method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return did if r.status == 200 else None
    except Exception:
        return None


def upload(path, draft, description):
    cmd = ["npx", "-y", "postplan", "upload", path]
    draft = draft or known_draft(path)
    if draft:
        cmd += ["--draft", draft]
    else:
        cmd += ["--new"]
    if description:
        cmd += ["--description", description]
    r = subprocess.run(cmd, capture_output=True, text=True, env=upload_env())
    out = r.stdout + r.stderr
    m = re.search(r"Draft ID:\s*([a-z0-9]+)", out)
    if r.returncode != 0 or not m:
        sys.exit("the upload failed:\n" + out.strip())
    url = re.search(r"URL:\s*(\S+)", out).group(1)
    ver = re.search(r"Version:\s*(\d+)", out)
    return m.group(1), url, ver.group(1) if ver else "?"


# What each refusal of a round means and what to do about it. The service names them in
# eliasdlc/postplan, src/api.js; a refused round rolls the whole upload back.
ROUND_REFUSALS = {
    "round_requires_key": "the upload carried no key, and only a key may open a round. Put "
                          "POSTPLAN_BOOTSTRAP_API_KEY in ~/.config/secrets/postplan.env",
    "invalid_round": "the service refused the shape of the round. Redraw the page with draw.py; if it is "
                     "refused again, draw.py and the service disagree on the round",
    "round_conflict": "this round id belongs to another draft or account (a copied page, or a changed "
                      "postplan-draft meta). Run `draw.py page.json --new-round`, then build.py again",
    "round_frozen": "he already picked in this round and its questions changed since. Run `draw.py page.json "
                    "--new-round` and build.py again; he answers the new round from the start",
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """The upload key rides on the request, and urllib would forward it to wherever a redirect points."""
    def redirect_request(self, *args, **kwargs):
        return None


def upload_round(path, draft, description, round_):
    """POST the page with its round to our instance, which the npm CLI cannot do. Returns the draft
    id, URL, version and the round's status, or exits naming the refusal."""
    env = upload_env()
    key = env.get("POSTPLAN_API_KEY")
    if not key:
        sys.exit("not uploading: round_requires_key: " + ROUND_REFUSALS["round_requires_key"])
    # No known_draft() here: a drawn page keeps its postplan-draft meta across redraws, so the
    # draft is in the page, and that probe asks the production host whatever the environment says.
    payload ={"html": open(path, encoding="utf-8").read(), "filename": os.path.basename(path),
               "draftId": draft, "description": description,
               "metadata": {"round": round_, "cliVersion": "build.py"}}
    req = urllib.request.Request(env["POSTPLAN_API_URL"].rstrip("/") + "/api/uploads", method="POST",
                                 data=json.dumps(payload).encode(),
                                 headers={"content-type": "application/json", "authorization": "Bearer " + key,
                                          "user-agent": "postplan-build"})
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=60) as r:
            body = json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        with e:
            if 300 <= e.code < 400:
                sys.exit("the upload failed: redirected (HTTP " + str(e.code) + ") and not followed, because the "
                         "upload key would go with it. Point POSTPLAN_API_URL at the host that serves the API")
            try:
                body = json.loads(e.read() or b"{}")
            except ValueError:
                body = {}
        code = body.get("code")
        if code in ROUND_REFUSALS:
            sys.exit("not uploading: " + code + ": " + ROUND_REFUSALS[code])
        detail = "; ".join(body.get("errors") or []) or body.get("error") or ""
        sys.exit("the upload failed: HTTP " + str(e.code) + (": " + detail if detail else ""))
    except OSError as e:
        sys.exit("the upload failed: " + str(e))
    # A service from before the answer button stores the metadata and answers no round.
    status = (body.get("round") or {}).get("status")
    return body["draftId"], body["publicUrl"], str(body.get("versionNumber", "?")), status


def publish(path, html, description):
    """Upload the page as written to `path`, giving it a draft meta the first time. A page with a
    round sends it with the upload; any other page goes through the CLI as it always has.
    Returns the URL, the version and a line about the round (empty without one)."""
    round_ = _draw().round_of(html)
    existing = draft_id(html)

    def send(draft, desc):
        if round_:
            return upload_round(path, draft, desc, round_)
        return (*upload(path, draft, desc), None)

    did, url, ver, status = send(existing, description)
    if not existing:
        html = html.replace("<head>", f'<head>\n<meta name="postplan-draft" content="{did}">', 1)
        open(path, "w", encoding="utf-8").write(html)
        did, url, ver, again = send(did, None)
        status = status if again == "unchanged" else again
    said = ""
    if round_ and status:
        said = "round " + round_["id"] + " " + status + ": each option links to its confirmation page"
    elif round_:
        said = ("round " + round_["id"] + " not stored: this service predates the answer button, so the "
                "page's buttons lead nowhere and he answers in the thread")
    return url, ver, said


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--description")
    ap.add_argument("--check", action="store_true", help="validate without uploading")
    ap.add_argument("--over", metavar="REASON",
                    help="publish over the type's word ceiling, writing REASON into the document")
    ap.add_argument("--no-webp", action="store_true",
                    help="leave embedded images as they are (a capture that has to stay lossless)")
    ap.add_argument("--new", action="store_true",
                    help="write a new document with the chrome already in it, and stop")
    ap.add_argument("--type", help="with --new: " + ", ".join(sorted(TYPES)))
    ap.add_argument("--mode", choices=MODES, default=None,
                    help="with --new: adaptive writes a bare page with no required chrome; "
                         "legacy (the default with --type) writes the recipe")
    ap.add_argument("--title", help="with --new: the h1, which is the conclusion")
    ap.add_argument("--lang", default="en", help="with --new: es when Elias wrote in Spanish")
    ap.add_argument("--hand", metavar="REASON",
                    help="publish a page draw.py did not draw, writing REASON into the document")
    ap.add_argument("--font", action="append", default=[], metavar="NAME=PATH.woff2",
                    help="embed the product's typeface so its components render in it; repeatable")
    a = ap.parse_args()

    path = os.path.abspath(a.file)
    if a.new:
        if not (a.hand and a.hand.strip()):
            sys.exit("--new writes a page to fill by hand, and a page is drawn from data: start from "
                     "`draw.py --example decide` (or understand, look). When the page has to be written "
                     "by hand, say why: --new --hand \"the reason\"")
        if a.mode == "adaptive":
            if a.type:
                sys.exit("--type belongs to the legacy recipe: an adaptive page declares none")
            scaffold_adaptive(path, a.title, a.lang)
        else:
            scaffold(path, a.type, a.title, a.lang)
        made = open(path, encoding="utf-8").read()
        open(path, "w", encoding="utf-8").write(hand_note(made, a.hand))
        return
    html = open(path, encoding="utf-8").read()

    refusal = drawn_problem(html, a.hand)
    if refusal:
        sys.exit("not uploading:\n- " + refusal)
    if a.hand and _draw().stamp_of(html) is None:
        html = hand_note(html, a.hand)

    savings = []
    if "/*FONTS*/" in html:
        html = html.replace("/*FONTS*/", open(FONTS_CSS, encoding="utf-8").read(), 1)
        savings.append("fonts embedded (they render on our instance, not on postplan.dev)")

    for spec in a.font:
        html, how = embed_font(html, spec)
        if how:
            savings.append(how)

    if not a.no_webp:
        html, how = to_webp(html)
        if how:
            savings.append(how)

    problems, size, warns = validate(html)

    # The browser pass runs on the document as it will be published, so the
    # webp re-encode and anything the script draws are already in it.
    probe = path + ".probe.html"
    open(probe, "w", encoding="utf-8").write(html)
    try:
        rep = render_report(probe)
    finally:
        os.remove(probe)
    rproblems, rnotes = render_problems(rep, html, a.over)
    if a.over and rep and not rproblems and doc_mode(html) != "adaptive":
        frame, per_f, per_q, per_r = TYPES.get(doc_type(html), (0, 0, 0, 0))
        ceiling = (frame + per_f * rep["findings"] + per_q * rep["questions"]
                   + per_r * rep.get("tableRows", 0))
        if rep["words"] > ceiling:
            html = over_note(html, a.over, rep["words"], ceiling)
    problems += rproblems
    warns += rnotes

    if problems:
        sys.exit("not uploading:\n- " + "\n- ".join(problems) + oversize_help(html, size))
    note = f"{size // 1024} KB" + (" (close to the limit)" if size > WARN_BYTES else "")
    if savings:
        note += " [" + "; ".join(savings) + "]"

    def notices():
        """At the end, not at the start: a notice up top gets eaten by the URL."""
        if not warns:
            return
        print("\n" + str(len(warns)) + " judgment notice(s), which the machine cannot decide:")
        for i, w in enumerate(warns, 1):
            print(f"  {i}. {w}")

    if a.check:
        # --check does not touch the file: if it wrote, it would eat the
        # /*FONTS*/ marker and the next run with --font would inject the
        # family a second time.
        print("ok,", note)
        notices()
        return
    open(path, "w", encoding="utf-8").write(html)

    url, ver, said = publish(path, html, a.description)
    print(f"{url}  v{ver}  {note}")
    if said:
        print(said)
    notices()


if __name__ == "__main__":
    main()
