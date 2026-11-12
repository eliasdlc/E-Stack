# Page rules

How a page is written: components, prose, decisions, where it lives and the
build. The purpose, the transport and the publish commands are in `SKILL.md`
and `transport.md`; the fields of a drawn page and what `draw.py` refuses are
in `recipes.md`; the incidents behind these rules are in `history.md`, read
only when a rule is being changed.

## Who draws the page

| Page | Made by | Checked by |
|---|---|---|
| Published | `draw.py page.json`, from data, in one of three types (`decide`, `understand`, `look`) | `draw.py` on the data (questions, names, words), then `build.py` in a browser |
| Published, written by hand | You, as an adaptive page (`<meta name="postplan-mode" content="adaptive">`), only for a shape `draw.py` cannot make | `build.py page.html --hand "the reason"`, which writes the reason into the page |
| In the thread | You, on the T3 theme variables (`SKILL.md`, Render inline) | `scripts/lint_page.py` |

`build.py` refuses a published page that carries no `postplan-drawn` stamp and
no reason, and one edited after it was drawn. The rules below are about what
you write, whoever draws it.

## The component is the implementation

Every visual page, a text-only one included, calls the Skill tool with
"design-grammar" and then "frontend-design" before drawing anything (anything
visible loads design-grammar, and visual documents also frontend-design). When
the page contains a component, the `design-identity` hook also refuses to write
a `.stage` until both are in the transcript, and a web product also follows the
web checklist `design-grammar` points to. A component is exactly one of:

1. **A capture of the real thing running**, mandatory when it already exists in
   code: Flutter and native through `app-testing`, web through a headless render
   of the real dev server.
2. **Implementation-ready markup in a `.stage`** (an `html` block of a drawn
   page), for something that does not exist yet: real px, real tokens, real
   strings, every state, written to be pasted into the repo.

A drawing from memory is neither, because the pick is made on something the
product will not look like.

### The component wears the product, not the page

The design comes from the product's `DESIGN.md` with `design-grammar` and
`frontend-design`. A drawn page is black, set in Bricolage and Figtree; the
product inside it wears its own face and ground.

- **The `.st` root declares `font-family`, `background` and `color` inline**
  with the product's values. `build.py` refuses a `.st` with text that declares
  none of the three, or whose font is the page's.
- **The typeface travels in the file**: `--font "Name=path.woff2"` (repeatable)
  embeds an `@font-face`. The serving CSP allows `font-src data:`; without it
  the browser falls back and the pick is made on the wrong face.
- **No `DESIGN.md` yet means the page decides it.** Each option is an identity,
  its own `.st` with its own face and neutrals, and the pick writes
  `DESIGN.md`. The `design-identity` hook (see `design-grammar`) blocks the
  repo's first UI file until it exists.

### The rules that make it real

- **Every value comes from the repo**: open the component or theme
  (`app_colors.dart`, `globals.css`, the tailwind config) and copy the literal
  hex, radius, padding and size; the mock's comment names the line. A value not
  in the repo yet is marked new, so a reader can tell a copy from an invention.
- **Every string comes from the string source**, as the user sees it, not
  retyped from the chat or an enum rendered as a label.
- **Every state**: grep the component for conditional classes, `@media` and
  `@supports`, and draw default, variants, dark, empty, error, disabled and one
  with ugly data (a name that never ends, a list with nothing in it), side by side.
- **A component is read at 350 px**: that is the column of a drawn page on his
  phone, and nothing scales it. A piece wider than that is captured at its real
  size and shown as a `figure`, because text under 11 px decides nothing and
  `build.py` refuses it.
- **A wide screen is filled**: from 700 px the page runs to 80rem, questions
  share a row and the options of a lone question do; from 1000 px each title
  sits in a rail beside its content and the counts beside the page title. Prose
  stays under 44rem a line. `draw.py` owns this, so look at a drawn page at 390
  and at 1440 before changing its stylesheet.
- **Prefix every class inside an `html` block**: the page's own classes (`q`,
  `opt`, `pill`, `tag`, `rows`, `steps`, `fig`, `tb`, `top`, `turn`, `foot`)
  style anything that reuses them.

## How it is written

Delete these four tics:

| The tic | What to write instead |
|---|---|
| "no es X, es Y" | Y, with its measurement next to it |
| Code that lies, breathes, eats, gives up | The producer, the consumer and the wrong value |
| A number-free slogan closing a factual paragraph | Nothing: the paragraph ends on its last fact |
| An option named after an obscure word, opened with its definition | What it does on screen, in his words |

The negation is allowed when X is a diagnosis Elias proposed in the message you
answer and the sentence names the `file.ext:line` that refutes it.

- **Every title is a fact**, not just the `h1`: write the heading last, read the
  first sentence of its block and promote it. A heading is a subject, a verb and
  a consequence ("El retroceso es real y se puede medir: hasta 4,73 m hacia
  atras en 0,30 s", not "El chevron que tiembla"). A title that is only
  `Lo que ...`, `Qué ...`, `Cómo ...`, `Dónde ...`, `Por qué ...` or a number
  and a noun gets rewritten.
- **Delete the sentences that carry no grounded claim.** If deleting one loses
  meaning, it hid a mechanism you never wrote: write the mechanism there.
- Tables for anything that repeats more than three times, same columns every
  time. `<details>` only for what changes a decision, 120 words at most. Say
  what a result came from and what was not verified, next to it. Every section carries something the reader can use. Plain
  punctuation, no emoji; `build.py` rejects em dashes. Spanish when Elias writes
  in Spanish, technical terms in English.

## Decisions, when a page asks for a pick

- A question carries the question as he would say it, `today` (what is wrong
  now, with its number or path), then each option: its name, what it does, its
  cost and, when there is something to see, its capture.
- **The cost is a consequence with a unit**: minutes of his time, a scenario
  that breaks, a file that stops being editable. Effort words (easy, hard,
  quick) give him nothing to weigh.
- **Every option is one he could pick.** "Keep as is" appears only when it is a
  real candidate, with its reason. Two options is a smell: look for the third
  that dissolves the tradeoff. If only one path is real, it is not a question:
  take it and list it under `decided`, with the way back.
- An answer in his own words designs the option: build what it says without
  asking again. A note on a picked option modifies it; it does not reject it.
- The pick is asked with the question tool, each option under the name it has
  on the page (`draw.py page.json --questions` prints them). The page collects
  an answer only through the link `draw.py` puts on each option when every
  question is of taste or a plan (`ANSWERABLE` in `draw.py`): he confirms on the
  service's page and `agents postplan-await` hands the picks to the question
  tool. Money, production, the irreversible, his rules, his hands and his eye
  stay in the thread, and one of them on a page leaves every option without a
  link, so a round is answered in one place. A question with its options stays
  under 100 words: the median was 146, and he answered those with a note three
  times out of four.

## Where the file lives

`~/Documents/Proyectos/<Project>/dev/plans/YYYY-MM-DD-<topic>.json`, with the
`.html` drawn beside it, outside every repo; audits in `audits/`; his own setup
in `~/Documents/Personal/dev/`.

**A closed round stays closed**: his answer in the thread is the record.
Apply the decisions, write each where it lives (the Zoho comment, the repo
file) and reply with what you do next, not a rebuilt page. A **new** round is a
new page with its own URL and one line linking the last; settled items stay in
the old one. Touch an old page only to fix a defect (a wrong number, a
superseded component): fix that block, note the superseding commit, say so in
the chat.

## What a finding looks like

A title that **is** the measurement (value, unit and window; no number in the
title means measuring is unfinished), one sentence on what it was measured
**on**, evidence as `command` then its literal output in a `code` block (run
every count you report), the `app-testing` channel named before the first
sentence (a render never certifies a native layer), and a chart for a series or
distribution: parse the real log and plot it, with a caption naming each color.
A before and after is one subtree captured twice with one named difference
(`figures`). Findings go in a three-column table; at most three get a section
of their own, only those whose severity changes what happens next.

## Shipping

```
python3 ~/.claude/skills/visual-briefing/postplan/draw.py --example decide > page.json
python3 ~/.claude/skills/visual-briefing/postplan/draw.py page.json [--check] [--questions]
python3 ~/.claude/skills/visual-briefing/postplan/build.py page.html --check
python3 ~/.claude/skills/visual-briefing/postplan/build.py page.html [--description "..."] [--font "Name=path.woff2"]
```

`draw.py` checks the data and writes the page; what it refuses is in
`recipes.md`. Redrawing keeps the page's link. `build.py` re-encodes embedded
images to WebP, validates, renders at 390 in headless Chromium and uploads. The
first upload writes `<meta name="postplan-draft">` so later uploads keep the
URL. `--check` validates without uploading or touching the file.

`build.py` refuses: a page `draw.py` did not draw and that gives no reason, a
page edited after it was drawn, `<link>`, remote scripts or images, em dashes,
over 8 MB, an unknown `postplan-mode`, a `.st` with text and no inline
`font-family`, `background` and `color`, a `.st` in the page's font, text under
11 px inside a component, anything clipped inside one, and a page wider than
390 px.

**Fonts render only on our instance**: `eliasdlc/postplan` at `plan.decruce.dev`
sends `font-src data:`; hosted postplan.dev does not and refuses embedded fonts.
`build.py` fills `/*FONTS*/` with Bricolage Grotesque and Figtree, and the
system stack stays behind them.

**Captures travel inside the file**: the CSP allows a remote image, but a page
that needs the network dies the day that host does, so the remote `<img>`
refusal stays.

**If it does not fit, the components win.** The refusal prints where the bytes
are. Fix in this order: re-encode captures, replace repeated SVG with `<symbol>`
and `<use>`, cut prose, split by subject. Still too big: keep the file local,
hand Elias the path and say the 8 MB limit stopped it; raising it is one
environment variable in `eliasdlc/postplan`. Keep every component at full
fidelity.

### Look at it before uploading

```
cat > /tmp/f390.html <<'EOF'
<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#000}
iframe{width:390px;height:26000px;border:0;display:block}</style></head>
<body><iframe src="doc.html"></iframe></body></html>
EOF
chromium --headless=new --force-prefers-reduced-motion --hide-scrollbars \
  --screenshot=/tmp/pp390.png  --window-size=420,26000 file:///tmp/f390.html
chromium --headless=new --force-prefers-reduced-motion --hide-scrollbars \
  --screenshot=/tmp/pp1440.png --window-size=1440,16000 file://.../doc.html
```

`--window-size=390` does not give a 390 px viewport (Chromium lays out at about
500 and crops, so everything past x=390 looks like overflow that is not there);
the iframe does, and it sits beside the document so the relative `src`
resolves. The window must be taller than the page or the screenshot is silently
truncated. Read the crops for the components and option names, not the page
shape: 390 is how he reads it, 1440 is where anything sized against the
viewport instead of its container breaks.

Reply with the URL, the version and one line on what to look at; the page stays at its URL and the chat carries the link.
