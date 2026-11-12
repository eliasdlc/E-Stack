---
name: visual-briefing
description: Chooses how to put what Elias has to decide, understand or read in front of him, and builds a visual page when a page beats the chat. Use when the result is a choice between options, a comparison, findings, a mock or component to look at, an explanation of how something works, or material long enough to need navigation, even if he never says "HTML". Also use for "show me the options", "bring me the HTML" and "put it in a postplan", and when a standing instruction asks for decisions that way. A decision is asked with the question tool, with a page only when there is something to look at; mocks to compare, phone reading and long material go out as a published Postplan link; a verdict or two options render inline in the T3 thread. A short answer stays in the chat. Not for messages to other people, tickets, commit or PR text, university deliverables, or deciding where files live.
---

# Visual briefing

Elias decides by looking and reads on a phone. Pick the form that gets him to
the answer or the pick fastest: the chat, or a page. He never opens generated
Markdown, so a result, a decision or an explanation lives in the chat or in a
page he can read, with the options, the recommendation and what each choice
costs visible there.

## Pick the purpose

| He has to | The first screen carries | The rest carries |
|---|---|---|
| Decide | The question, or the options with what each one costs and the recommended one | The evidence for each option, and what the pick sets off |
| Understand | The conclusion and the mechanism | The evidence: measurements, a trace, a diagram, before and after |
| Read | What it is, why it is worth the time, and a way to move through it | The material, in the order he will use it |

Use the chat when it carries the content as fast as a page would: a verdict,
a few options in a sentence each, a number with its source. Then answer there,
in the closing paragraph. Reach for a page when layout does work the chat
cannot: side by side comparison, a component or capture to look at, a diagram,
a table he scans, long material he navigates.

A decision goes through the question tool, asked last (core rules, Closing a
turn): at most four questions in a round, each one read whole on a phone
screen, and a fifth means one of them was yours to decide. A page goes with
the question only when there is something to look at (mocks, captures, a
comparison he scans), and the question carries its link. A new round shows
only what is new and one line pointing at the last page. A round he answered
stays answered in the thread.

## Compose from what the content needs

A published page is drawn from data by `postplan/draw.py`: you write what the
page holds (the questions, what you decided alone, the evidence, what is
unverified) and the program owns the look, because the look Elias reads
comfortably only changed when an agent wrote a page by hand. It has three
types, by what he has to do: `decide`, `understand` (reading material
included) and `look`. A page in the thread has no template. Whether such a page
has a title, a header, a bar, an index, metrics, a hero, which colors it uses,
and how long it runs, is decided by this content and this reader. A yes or no
with a consequence can be a few lines and two options. An audit can be a
headline number, a chart and a table. Study material can be an indexed set of
sections. Four things hold on every page:

1. The first screen carries the answer, the ask or the thing to look at.
2. A decision is only what Elias alone can settle: taste, money, production,
   something irreversible, his rules or a plan. A fact the code, the repo, the
   tracker or a command can answer is looked up and written as a fact, and a
   fork that can be undone is decided and reported, because a question he has
   to research, or never needed to see, costs him a round.
   Options are worded so that a plain "sí" accepts the recommended one: the
   recommendation comes first and says what "sí" sets off. Each option is
   named by what it does, the same name on the page and in the question, and
   the question says what happens if he does not answer.
   The pick is made in the question tool. A page's buttons and toggles are for
   looking at options and never submit, save or record approval: the frame has
   no channel back to the agent, and nothing counts as chosen until he answers.
   The one exception is the link `draw.py` puts on each option when every
   question is of taste or a plan: he confirms it on the service's own page,
   and that pick answers the question tool for him (Published links, step 5).
3. Every title says what the content establishes. Every claim is useful and
   grounded in something that was read, run or measured, with the evidence
   close to the claim when he needs it to trust or decide. Sentences that
   carry nothing go. Plain punctuation, no emoji, no em dash.
4. A component is a capture of the real thing or markup ready to paste, built
   from the repo's own values and strings, with every state. Call the Skill tool
   with "design-grammar" and then "frontend-design" before drawing one.

Say what was not verified wherever it changes what he would decide.

## Choose the transport from what the session offers

| Situation | Transport |
|---|---|
| Options shown as mocks or captures, anything he reads on his phone, reader material longer than one screen, or anything to share, cite from Zoho or a PR, or keep past the thread | A published Postplan link, drawn from data |
| A verdict, or up to two options with one visual, and `html_render` exists (T3) | Inline in the thread |
| The upload fails (no network, instance down) | A standalone HTML file, its path in the chat, and the failure named |
| The chat carries it | The chat |

A local file path is a source, never the delivery: since 8 Oct, 6 of 38 rounds
went out as paths he never opened and 0 as links. Choosing a transport needs
no permission. A page for Elias publishes under his standing authorization in
the core rules. A page carrying client or customer data publishes only when he
asks for it; until then it is inline. A page that decides or proves something is written as a
source file first, so the inline render, a later upload and the record share one origin.
Limits, the preview loop and the publish commands are in
`references/transport.md`.

## Render inline

If `html_preview` and `html_render` are deferred, load them with ToolSearch by
those two names: the harness decides their prefix.

1. Write the page to its file. Match the thread: use the theme variables T3
   injects (`--background`, `--foreground`, `--border` and the rest), zero
   margin on the outermost element, fluid width, no outer card, border or
   banner title, fixed pixel heights for charts, no `100vh`. The `scripts/lint_page.py`
   script checks the parts a machine can decide.
2. `html_preview` at about 390 and at 728, dark and light. Read the console
   and `missingImages`, and take `contentHeight` as the frame height.
3. One `html_render` with that height. If `contentHeight` passes 2000, the
   content scrolls inside the frame with its scrollbar hidden: publish a link
   for it instead.
4. Write only what the page does not say, in the closing paragraph.

## Who renders

Only the agent talking to Elias renders, because `html_render` shows in the
caller's own thread. A delegated child writes the page as a file and returns
its path and what it checked; the principal previews and renders. Call the
Skill tool with "model-delegation" when composing the page is worth a child.

## Published links

This skill owns the whole path, from its own `postplan/` folder: `draw.py`
draws the page and `build.py` probes it in a browser and uploads it.

1. `draw.py --example decide` (or `understand`, `look`) prints a data file to
   start from; `references/recipes.md` has every field and what is refused.
2. `draw.py page.json` checks the data and writes `page.html`. It refuses a
   fifth question, a question that does not fit a phone screen or does not say
   why it is his, a lettered option, and a code where a title belongs.
3. `draw.py page.json --questions` prints the same questions as input for the
   question tool, so the name on the page is the label he taps.
4. `build.py page.html` uploads. It refuses a page `draw.py` did not draw, or
   one edited afterward: a change goes through the data.
5. When every question is of taste or a plan, the page gets a button on each
   option and `build.py` uploads its round. Then, before calling the question
   tool, start `agents postplan-await page.json` in the background: once he has
   confirmed a pick for every question on the page, it answers the question
   tool with them. Answering in the thread still works; the first answer wins,
   and the poller then exits 0 saying it was answered in the thread. It waits
   up to 7 days (24 hours when T3's database cannot be read), and it ends
   non-zero when the relay failed. One round answers one question, once: a
   second poller on the same round exits naming the first, and asking again
   on an answered round exits saying so, because the service keeps its first
   picks and would post the old ones. To ask again run `draw.py page.json
   --new-round`, `build.py`, then the poller.

Read `references/page-rules.md` before writing the data: components, prose,
decisions and the build refusals. `/postplan` no longer exists; "put it in a
postplan" routes here.
