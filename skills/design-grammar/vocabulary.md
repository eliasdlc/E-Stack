# Vocabulary

Native pieces; on web reference only, and the glow pieces are not portable.

Sizes in `em` at the 17px root.

## Primitives

Almost any product will need these, so their numbers are settled.

- **Surface** `background: --sf; border-radius: --r; padding: .9em 1em; border: 1px solid --ln; box-shadow: --shadow`.
- **Primary action** pill, `height: 3.2em`, `padding: 0 1.1em`, `background: --ac`, `color: --on`, weight 700, `box-shadow: 0 .5em 1.4em -.4em --glow`. Label in the text face.
- **Secondary action** same box, `background: --sf2`, `color: --ink`, no shadow.
- **Icon action** the same 3.2em, square.
- **Round action** 2.3em circle on `--sf` with a hairline. Badge dot 0.5em with a 0.13em ring in the surface color, so it reads as cut out.
- **Icon chip** 2.2em square, radius 0.7em, `background: --sf2`, `color: --ac`. Tinted variant: `color: X` on `background: X at 16%`.
- **List row** icon chip, text block, trailing affordance pushed right with `margin-left: auto` at 70% opacity.
- **Selectable target** `border: 1.5px solid --ln`, radius by size class. Selected: the whole target becomes `--ac`, its text becomes `--on`, e2 glow appears. No checkbox, no ripple.
- **Single choice row** equal flex pills, height 2.8em, `--sf2` at rest, `--ac` when chosen.

## Compositions

Borrow only if the product actually has this shape.

- **Feature surface** the one place a gradient is allowed: radius `--r`, title in the display face at 1.3em, body at 0.84em in `--on` at 82%, an action in `--bg` with `--ac` as its label color, e2 glow.
- **Metric tile** a surface with a colored header row at 0.8em bold, a display-face value at 1.55em with a text-face unit at 0.48em, a caption, and a sparkline bleeding to the tile edges via negative margins.
- **Segmented scale** equal columns, height 3.7em, radius 1em, display face for the number and text face for the caption under it. Selected fills with the accent.
- **Flow header** back affordance and action in the accent, title in `--ink` at weight 600, step counter in `--mute`. Height 2.4em. No app bar, no elevation, no background.

## Floating navigation

Only relevant when a product has persistent chrome (web: the checklist decides). When it does, this is the
shape, because it is the piece that carries the most personality and the one
Material gets most wrong.

- Floats: `position: absolute; left: .9em; right: .9em; bottom: 1.25em`. Inset
  on all four sides, never glued to an edge, never full bleed.
- Two objects side by side: the glass bar with the destinations, and a separate
  orb for the product's primary action. That action is not an extra tab and it
  is not a FAB dropped on top of the bar.
- Glass: `background: --glass; backdrop-filter: blur(1.4em) saturate(1.8);
  border: 1px solid --glass-ln; border-radius: 2.2em; padding: .3em;
  box-shadow: 0 .8em 2em -.8em rgba(0,0,0,.6)`.
- Destination: 4.4em tall, icon at 2em over a 0.58em label, both in the text
  face. Inactive is `--mute`. Active is `--ac` on a `--glass-on` pill inside the
  bar, and the icon switches to filled at 22% with stroke 2.
- Orb: 3.3em circle, the brand gradient, `--on` glyph, e2 glow.
- Content behind it reserves `padding-bottom: 5.4em`.
