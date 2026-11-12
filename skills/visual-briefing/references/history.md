# Why the Postplan rules exist

The incidents, measurements and quotes behind the rules in `SKILL.md`,
`page-rules.md` and `recipes.md`. The skill does not need this file to be followed; read it when a
rule is being changed or questioned.

## The document is the part he needs

Measured on 19 sep over the 138 documents this skill had produced: median 2,498
words, 12.5 minutes of reading. The part he needs (the h1, the lede, the
numbers, the titles of the findings and the questions) was a median of 224
words, 11 % of each document. The other 89 % is what made him stop at line 15.
So the document is not a shorter report: it is those 224 words, on the first
screen, with the components attached.

## Step 0: only when he asks

Measured on 19 sep over the 167 documents built in 29 days, 5.8 a day: 112
carried no component and no capture, so a chat message could have carried them
whole, and 120 asked him nothing at all. Nothing recorded whether he had wanted
any of them. He said it on 19 sep: "only when I ask it to, the agent is gonna
generate an html". The row "he asked for nothing: work finished" was the one
being got wrong.

## The first screen

In the 35 documents that asked Elias something, the first question sat at word
1,557, screen 8.8 of a phone. He had to read for eight screens to reach the
thing he was summoned for.

Two documents of the same type, both built from this skill on 19 sep, came out
as two different products: one with the bar, the hero and 9 `<section>`, the
other with an `h1` naked at the top of the page and no section at all. The
stylesheet only sizes an `h1` inside `.hero`, so that one rendered its headline
at 32 px on a 1440 screen against the 60 it should have. `build.py` refuses it
now, and the chrome check is what keeps two documents looking like one product.

## The route

He said it on 19 sep: "the html never shows the workflow or the roadmap that is
gonna be followed, therefore I never know what is it gonna go thru". Measured
over the same 167 documents: 18 carried a heading that said what followed, and
none of the six types had a place for one.

## What you decided alone

He asked for it in his own words: "tell me the decisions, the things that you
decided yourself, because the decisions were obvious and you didn't need me to
take a vote into that decision". Of 138 documents, 2 had such a section. A
fourth column for how to reverse each decision left each cell at 80 px on the
phone, which is why the table has three.

## The component is the implementation

"It shouldn't be a mockup. It shouldn't be a half-made component. It should be
the exact component that is going to be implemented into the app or the
website." Measured against the repos on 19 sep: the mocks invented their own
hexes, radii and type sizes, drew one state where the code had five, and
rendered text at 3.8 to 8.3 px on the phone he reads on. The skill drew every
pixel Elias approved and had never once opened the design grammar.

Elias, 20 sep: "it's not the design, it's the place where we show the design".
Measured on 20 sep: every `.st` in the corpus inherited the document's Figtree
and its true black ground, so the options Elias picked between all wore the
same face whatever the product was, and three demos built that week came out
as one page.

## How it is written

The complaint was "words are tiring, are so AI, like do a lot of similes,
metaphors". Measured: only 17 similes in 138 documents. What was actually there
was four tics:

| The tic | Times |
|---|---|
| "no es X, es Y" | 147, in 42 % of documents |
| Code that lies, breathes, eats, gives up | 66, in 33 documents |
| A number-free slogan closing a factual paragraph | 451, in 115 documents |
| An option named after an obscure word, opened with its definition | 11, in 7 documents |

In the corpus 92 % of h1s stated a fact and 24 % of h2s did; in 79 of 88 cases
the fact that should have been the heading was already written one block below
it. Running prose carried 9.1 % load-bearing words.

## Findings

The finding block described in the skill is the best block in the corpus and
the one he pointed at. Median finding was 68 words; the same fact as a table
row was 17.

## Closed rounds

42 of 138 documents were rebuilds that showed him decisions he had already
made, and none of them asked him for anything. A rebuild reprinted 43 % of its
own prose; a fresh document reprinted 0 %.

## Fonts

Every font this skill embedded before 19 sep was refused by the browser on the
hosted postplan.dev: both families reported `status: "error"` and
`document.fonts.check` came back false, and 138 documents rendered in the
system stack without anyone noticing. That is why documents are served by our
own instance.

## Recipes

The old set had eleven types, four of which were never used once in 138
documents, while the shape Elias asks for most (work he has to understand, with
what you decided alone) had no recipe at all. The six current types replaced
them.

## Adaptive mode (8 Oct 2026)

The chrome, the six types and the word ceilings came from measuring 138
documents on 19 sep, and they fit documents shaped like those. Elias approved
fully adaptive composition on 8 Oct, so `build.py` gained a declared mode:
`postplan-mode` adaptive skips the layout and ceiling checks and keeps the
quote, the size and asset limits, option accessibility, component identity and
the browser probes, and adds a probe for a page wider than the screen. A page
with no mode stays legacy, unchanged. `/postplan` became a manual command (since removed, folded into this skill) that
opens `visual-briefing` first, because the automatic route now belongs to that
skill. Nothing here was measured on readers yet: the rules that remain are the
ones that protect the reader, the host and the upload.

## Drawn from data (11 Nov 2026)

Elias asked for the decision pages to be rethought from zero: readable at a
glance, names instead of codes, a design that stops changing. Measured over
1,635 transcripts, 122 published pages and 73 with questions, 1 Sep to 11 Nov:
111 pages shared one ground and 110 one face, so the look was stable and only
moved when an agent wrote a page by hand; the median round asked 5 questions
of 146 words and one asked 49; 43 of 73 named a ticket, a decision or an
option by a code; 73 percent of his lettered answers carried a written note
anyway. The six typed recipes and their word ceilings were prose and a check
on finished HTML, which an agent met by composing around them. So the checks
moved to the data (`draw.py`) and the layout left the agent's hands: three
types, four questions, 100 words each, named options, the recommended one
first. The proposal he approved is plan.decruce.dev/d/dz5nwvwnldam; a council
of two models left it at 8.5 of 10. The legacy scaffold and its checks stay in
`build.py` only to republish an old source with `--hand`.

The first drawn page kept the phone column (40rem) on every screen, and on his
laptop he wrote: "La pagina esta muy estrecha es incomod de leer asi, hay
demasiado espacio gastado en nada a los lados" (11 Nov 2026). The approved look
had only been checked at 390 px. So the stylesheet fills a wide screen and the
phone column stays as it was.

## The answer button (11 Nov 2026)

He asked for a link where he places his decisions and they reach the agent,
and after a spike he picked "Constrúyelo ahora". A drawn page whose questions
are all of taste or a plan carries a link on each option; he confirms on the
service's page (eliasdlc/postplan), and `agents postplan-await` hands the picks
to the question pending in the thread through a T3 webhook relay. The other
reasons ask for his words in the chat, so a page holding one of them keeps no
button, and the thread answer keeps working either way.
