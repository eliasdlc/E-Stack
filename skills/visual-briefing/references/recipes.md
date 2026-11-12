# The data of a drawn page

`postplan/draw.py` turns one JSON file into the page. You write what the page
holds; the layout, the colors, the type and the counts in the header are the
program's. `draw.py --example decide` (or `understand`, `look`) prints a file to
start from, and `draw.py page.json --check` says what is wrong without writing.

## Three types

| `type` | He has to | Opens on | Must carry |
|---|---|---|---|
| `decide` | Answer | The questions | One to four `questions` |
| `understand` | Follow an explanation, or read material | The conclusion | A `lede` (the mechanism), at least one section, no question |
| `look` | See something | The sections, with the capture or mock | A `figure`, `figures`, an `html` component or an option with `show`; questions are optional |

## Fields

| Field | What it is |
|---|---|
| `type`, `lang` | The type above; `es` or `en`, the language he reads the page in |
| `title` | The conclusion in one sentence |
| `kicker` | One line: what this page is and its date |
| `lede` | The mechanism in two sentences, under the header |
| `questions` | Each one: `reason`, `question`, `today`, `options`, `silent`, `evidence` |
| `decided` | What you decided alone: `what`, `why` it was yours, and `undo`, the way back |
| `sections` | Each one a `title` that says what its content establishes, and `blocks` |
| `unverified` | What was not run or seen, as a line or as `what` and `why`. Required; `[]` when everything was |
| `sources` | One closing line: where the measurements come from |

A question:

| Field | What it is |
|---|---|
| `reason` | Why it is his: Gusto, Dinero, Producción, Irreversible, Tus reglas, Un plan (or Tus manos, Tu ojo for what is not a decision). The list is the one the `question-reason` hook warns on |
| `question` | As he would say it, ending in `?` |
| `today` | What happens now, with its number |
| `options` | Two to four. `name` (what it does, the label he taps), `does`, `costs`, `recommended` (first option only), `show` (a capture) |
| `silent` | What happens if he does not answer |
| `evidence` | Lines folded under the question; they do not count against its words |

When every `reason` is Gusto or Un plan, each option gets a button that
answers from the page, and the page carries its round (`transport.md`,
Published link). One question of any other reason draws the page with no
button at all.

Blocks, one key each: `p`, `list` (lines, or `title` and `text` pairs), `steps`
(`title`, `text`, `note`), `table` (`head`, `rows`), `figure` (`src`,
`caption`, `alt`), `figures` (a row of them, for a before and after), `code`,
and `html` for a component as markup. Text takes `**strong**`, `` `code` `` and
`[links](https://...)`. An image path is read from beside the data file and
travels inside the page.

## What is refused, by name

| Rule | Refused |
|---|---|
| `question-count` | A fifth question; a `decide` page with none; an `understand` page with one |
| `question-words` | A question over 100 words of question, `today`, options and `silent` |
| `reason` | A `reason` outside the list: a fork with none of them that can be undone is yours, and goes under `decided` |
| `silent`, `question`, `options`, `option-does` | A question missing one of its parts |
| `option-name` | An option named by a letter or a number, a repeated name, a name too long to tap |
| `recommended-first` | A recommended option that is not the first |
| `code-for-a-name` | A ticket, decision or option code in prose. After its title, in parentheses, it passes: "the offline map (T737)" |
| `punctuation` | An em dash or a middle dot |
| `nothing-to-look-at`, `image` | A `look` page with nothing to see; an image that does not exist |
| `unknown-key`, `block`, `section`, `type`, `lang`, `title`, `kicker`, `lede`, `unverified`, `decided` | A field the page does not have, or one it needs |

## Sources from before `draw.py`

Pages published before 11 Nov 2026 were written by hand in six typed recipes
(`decisions`, `findings`, `draft`, `briefing`, `comparison`, `note`) and keep
opening at their links. Fixing a defect in one republishes its source with
`build.py page.html --hand "the reason"`, which still applies that recipe's
checks; its markup is in `postplan/design.html`. A new page is never started
that way.
