# Transport reference

Measured on T3 Code 0.0.46-nightly.20261006.2735 (nightly channel) in an
audit on 8 Oct 2026. Nothing here comes from T3 documentation: re-check it when
the version changes.

## Inline in the thread (`html_preview`, then `html_render`)

| Fact | Value |
|---|---|
| Input | One document, 512,000 characters at most |
| Local images | Absolute path in `src`, `url()` or a JS string; png, jpg, gif, webp, avif, svg, bmp, ico; 10 MiB each, 25 MiB per page after inlining |
| Video | Not inlined |
| Frame | Borderless, 728 px on desktop, about 360 px on phones, height 80 to 2000; content past the height scrolls inside the frame |
| Theme | CSS variables on `:root` that follow light and dark live; base 14 px; scrollbar hidden |
| Sandbox | `allow-scripts allow-forms`, origin `null` |
| Fails inside the frame | `localStorage`, `sessionStorage`, `document.cookie`, `indexedDB` (SecurityError), `alert`, `window.open` |
| Page to host | Height changes and `http(s)` link clicks only |
| Persistence | None: a choice lives in the frame and reaches the agent only when he types it |
| Link | None to share; the attachment belongs to the thread |
| Scope | `html_render` shows in the caller's own thread, so a delegated child's render does not reach Elias |

`html_preview` runs the page as a top-level document with storage available and
a system sans-serif. It measures height, console output and missing images. It
cannot show the sandbox, the host messages, the hidden scrollbar or the real
font, so a passing preview is not proof of the reader's view. The first preview
on a machine can report that T3 is still installing its browser: call again a
minute later.

Copying: the frame does not delegate clipboard access, so never depend on a
copy button.

Accessibility the audit did not verify in the real frame: keyboard focus
between chat and page, screen reader behavior, the 14 px base. Check that the
page reflows at 320 px without two dimensional scrolling.

## Standalone HTML file (outside T3)

Write it under `~/Documents/Proyectos/<Project>/dev/plans/YYYY-MM-DD-topic.html`
(`~/Documents/Personal/dev/` for his own setup), outside every repo, and report
the path. Do not open a window on his screen. With no host theme the page
carries its own light and dark variables behind `prefers-color-scheme`.

## Published link (Postplan)

The default for pages with something to look at, phone reading and anything
past one screen. Both programs are in this skill's `postplan/` folder: `draw.py`
draws the page from data, `build.py` uploads it.

```
python3 ~/.claude/skills/visual-briefing/postplan/draw.py --example decide > page.json
python3 ~/.claude/skills/visual-briefing/postplan/draw.py page.json
python3 ~/.claude/skills/visual-briefing/postplan/build.py page.html --check
python3 ~/.claude/skills/visual-briefing/postplan/build.py page.html
```

The fields of the data and what `draw.py` refuses are in `recipes.md`. The
drawn page declares `<meta name="postplan-mode" content="adaptive">` and the
`postplan-drawn` stamp `build.py` asks for; an unknown mode is refused.

Authorization: the standing line in the core rules covers pages for Elias. A
page carrying client or customer data waits until he asks for it.

`build.py` keeps what protects the reader and the host: the 8 MB limit, no
`<link>`, remote scripts or remote images, no em dash, a component that
declares its own font, ground and ink, and a browser probe at 390 for text
under 11 px inside a component, clipping, and the page running wider than the
screen.

A page whose questions are all of taste or a plan carries its round in
`<meta name="postplan-round">` and a link on each option to
`/a/<round>/<question>/<option>`, the service's confirmation page. `build.py`
posts such a page straight to `/api/uploads` with `metadata.round`, because the
npm CLI cannot send one, and prints the round's status (`created`, `updated`,
`unchanged`) or its refusal by name with what to do. A service that predates
the button stores no round, and `build.py` says so: the buttons lead nowhere,
so skip the wait and he answers in the thread. Otherwise:

```
agents postplan-await page.json        # in the background, before the question tool
```

It polls `/api/rounds/<round>/picks` with the upload key and, once every
question is picked, posts `{threadId, round, answers}` to the "Postplan answer
relay" webhook task of this machine's T3 Code (`--relay-setup` prints its
one-time setup), which answers the pending question of the thread in
`T3CODE_THREAD_ID`. A question waits as long as he needs: the poller reads the
thread's pending question from T3's state database
(`orchestration_v2_projection_runtime_requests`, `kind = 'user_input'`), exits 0
with "answered in the thread" when it is no longer pending, and caps the wait at
7 days (24 hours when the database cannot be read). It polls every 10 seconds
for 10 minutes, then every 30. After posting it waits up to two minutes for the
question to leave pending and exits 1 when the relay failed or the question is
still pending. It also exits 1 naming the cause on a missing relay, a refusal,
a redirect (never followed, so the key stays put) or the cap.

One round answers one question, once. The service keeps the first pick of each
question forever, so the poller keeps per round state in
`~/.cache/agents/postplan-await`: a lock while it runs (a second poller on that
round exits naming the first) and a marker once picks were posted or the
question was answered in the thread (a later poller exits saying these picks
already answered a question). To ask again run `draw.py page.json --new-round`,
upload with `build.py`, and start the poller on the new round. The round's
question `text` is the exact text the question tool is given (`draw.py page.json
--questions`), silence sentence included, so changing only the silence is a new
round too; `draw.py` refuses an answerable page whose tool text passes 500
characters, the service's limit. A redraw otherwise keeps the round id while
that text and the option names are unchanged; `--new-round` gives a fresh one
after a `round_conflict` or `round_frozen`.

A published page needs the network and the `plan.decruce.dev` instance, so
captures travel inside the file as data URIs: `draw.py` reads each image path
from beside the data file and `build.py` re-encodes it to WebP.

## Source file

A page that decides or proves something keeps its source file in the plans
folder above, private by default because it holds captures and sometimes client
data. The thread attachment is a copy bound to that thread. The record of a
closed round is his answer in the chat plus the place where it was applied.
A one-off explanation needs no source file.

## Not measured

The mobile app frame, a copy button under a real tap, downloads, video in
either transport, and a page's state after the thread reloads.
