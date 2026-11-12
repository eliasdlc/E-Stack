---
name: design-grammar
description: Design grammar (radius, spacing, type, color roles, elevation, touch), the DESIGN.md identity contract the design-identity hook enforces, and the per-project taste ledger. Load before building, mocking, redesigning or judging anything visible in Flutter, native or web UI, or a component in a visual brief: "design this", "how does it look", "the spacing", "the colors", "se ve muy AI", "arregla el diseno", "build the screen". On web, frontend-design loads with it. Not for backend, tooling or tests with no screen.
---

# Design skeleton

This file sets the feel: radius, spacing, type roles, color roles, elevation, touch, materials. The product decides the rest (screens, information architecture, navigation model, which components exist, layout, copy, motion, brand), so two products read as siblings, never as one app recolored; build no piece because it is listed here (no metrics, no metric tile). The repo's DESIGN.md and rules win over this file. When a rule makes a screen worse, the screen wins and the deviation carries a one-line comment saying why.

## Web

On web UI, read `references/web-checklist.md` before the first file and again before calling it done; frontend-design sets the direction, and the three-direction gate below wins over its single-plan process. The checklist overrides these parts; roles, spacing, touch, borders and the anti-patterns still apply:

| Part | On web |
|---|---|
| 1 Root | Tailwind `rem` on the browser root, unless DESIGN.md sets one |
| 2 Radius | one scale per page, written in DESIGN.md if it mixes; all-sharp is legal |
| 4 Type | checklist section 4 |
| 5 Color | one accent under 80% saturation, scoped by the DESIGN.md `Accent:` line; dark ground from the brand |
| 6 Elevation | cards only for real hierarchy, shadows tinted, no outer glow (so no accent glow), gradients per checklist |
| 8 Icons | one library from checklist section 2 |
| Thesis table, vocabulary glow pieces, floating nav | the checklist |

Postplan pages and pages in the T3 thread follow `visual-briefing`.

## The thesis

Apple-leaning, not Material:

| Dimension | Material tell (avoid) | This skeleton |
|---|---|---|
| Radius | 8 / 12 / 16 uniform on everything | 12 to 22, scaled to the element, never a sharp corner |
| Elevation in dark | drop shadow on a dark surface | surface tone steps, zero shadow |
| Elevation in light | layered ambient plus key shadow | one soft, wide, low opacity shadow |
| Accent | fills app bars, FABs, chips, headers | action and selection only, nothing else |
| Type | one family, hierarchy by weight | display face for titles and numerals, text face for the rest |
| Sizing | fixed px | `em` on a 17px root, scales with system type size |
| Navigation chrome | opaque bar pinned edge to edge | inset and floating, glass, never touching an edge |
| Buttons | rectangle, 8 to 20 radius, elevation | pill, 54 tall, accent glow instead of shadow |
| Borders | visible gray 1px lines everywhere | hairline at 6% only where separation is real |
| Icons | a filled third party set at 24 | one stroke set, active is the same glyph filled at 22% and stroke 2 |
| Color naming | brand names: coral, mango, mint | roles: `bg`, `sf`, `ink`, `ac`, `on` |
| Selection | checkbox, radio, ripple | the target itself becomes the accent |

# The grammar

## 1. Root and scale

Everything is `em` on a 17px root, so layout and touch targets follow the system type size. Fixed px only for hairlines and a mock's device frame.

## 2. Radius

Nothing has a sharp corner, and radius scales down with the element, so a chip
inside a card never looks like a smaller copy of the card.

| Size of thing | Radius |
|---|---|
| Large surface: card, sheet, tile, panel | 22 (`--r: 1.3em`) |
| Medium: a selectable or grouped block | 18 |
| Small control: segment, stepper, field | 16 |
| Chip sized: icon square, badge | 12 |
| Anything that reads as an action or a state | 999 |
| Round by nature: avatar, orb | 50% |

Nesting rule: an inner radius is the outer radius minus its own padding, never
larger. Two different radii of the same size class on one screen is a mistake.

## 3. Spacing

Base 4: `4 8 12 16 20 24 32 48`.

| Slot | Value |
|---|---|
| Screen margin | 20 |
| Between sibling blocks | 10 to 12 |
| Between sections | 20 |
| Padding inside a surface | 15 to 17 |
| Gap inside a row | 12 |

## 4. Type

Two families at most: a display face with character, a text face comfortable at 17. Display only on screen titles, numerals that carry meaning and the one figure a flow lands on; buttons, chips, tabs and labels always use the text face, which stops a UI reading like a poster.

| Style | Size / line | Face and weight |
|---|---|---|
| Display | 34 / 37 | display 700 |
| Title | 24 / 26 | display 700 |
| Heading | 20 / 23 | display 700 |
| Subhead | 18 / 22 | text 700 |
| Body | 17 / 23 | text 400 |
| Label | 15 / 20 | text 600 |
| Caption | 13 / 17 | text 600 |
| Micro | 10 / 12 | text 600 |

Tracking: `-0.03em` at Display, `-0.02em` at Title, `-0.01em` at Subhead, `0`
from Body down. Uppercase eyebrows carry `+0.06em` and never appear more than
once per screen region.

Variable display face: `opsz 48` in an app, `opsz 96` on a document cover.

## 5. Color: roles, not names

A project supplies one value per role per mode; `ac` survives a rebrand, `coral` does not.

| Token | Role |
|---|---|
| `--bg` | screen background |
| `--sf` | raised surface |
| `--sf2` | surface on top of a surface: icon chip, ghost button, counter |
| `--ink` | primary text, titles, values |
| `--body` | running text |
| `--mute` | metadata, labels, inactive states |
| `--ac` | accent: action and selection |
| `--on` | text and icon on top of the accent |
| `--ln` / `--ln2` | hairline 6%, strong hairline 16 to 18% |

Derived: `--glow` (accent at 55% dark, 35% light), `--glass`, `--glass-ln`,
`--glass-on`, `--shadow`.

Rules:
- The accent marks action and selection only: never decoration, a header fill or a section title.
- Meaning never rides on color alone: a category, severity or state carries a glyph or label next to its tint.
- Semantic and category colors are a tint pair, `color: X` on `X at 16%`, never a filled block.
- Red is for destruction and irreversible flows only.
- Text and icons on the accent use `--on`, never a hardcoded `#fff`, which breaks the day the accent goes light.

## 6. Elevation and materials

Four levels, and dark mode does not use shadow at all.

| Level | Dark | Light |
|---|---|---|
| e0 surface | `--sf` tone step, no shadow | `#fff` on tinted bg |
| e1 raised | tone step to `--sf2` | `0 10px 30px rgba(<ink>, .08)` |
| e2 accent | `0 8px 24px -6px <accent at 55%>` | same, accent at 35% |
| e3 glass | surface at 82%, `blur(24px) saturate(1.8)`, hairline at 9% | surface at 84%, hairline at 8% |

One shadow, never a stack of two. The glow on e2 is the accent's own color, not
black: that is what makes a primary action read as lit rather than lifted.

Gradients: one or two surfaces per product, always 140deg, three stops (brand light, brand, brand deep) plus one radial white sheen at 28% in a corner; never on a card, button, background or bar.

## 7. Touch

- Minimum 48 x 48 for anything tappable, 8 between adjacent targets.
- Primary action 54 tall; persistent chrome targets 56.

## 8. Icons

One stroke set per product, one glyph per icon with a controllable fill (Lucide and Phosphor qualify); never a set with a separate filled glyph per state.

`fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round;
stroke-linejoin: round`.

Active state is that same glyph: `fill: currentColor; fill-opacity: .22;
stroke-width: 2`. Never a second, filled glyph.

Sizes: 1.3em inline, 1.15em next to a small label, 1.55em inside a round
primary action, 2em in persistent chrome.

## 9. Borders

A hairline only where two things need separating: 6% in the common case, 16 to 18% when it does real work (the resting outline of a selectable target). One divider weight per screen. In a list, a top hairline on rows after the first, never a full-width rule to the screen edge.

# Identity: DESIGN.md

**Every web product of Elias's own carries `DESIGN.md` at its repo root before its first UI file.** The `design-identity` hook blocks the write until it is complete, and blocks a Google font or a stock Tailwind neutral the file does not name. Writing one: read `references/design-md.md` first.

A scaffold default ("Tailwind + Geist + restrained motion") is not a direction, and the checklist's tells are a floor: a page that clears every one and has no signature has not been designed.

Three directions before one line of code, differing in structure and identity (face, neutral derivation, signature, the real product each borrows from). Three recolors of one layout is one option.

## Taste ledger

Every project keeps a `## Taste ledger` in its `DESIGN.md` (repo root for code, `~/Documents/Proyectos/<Project>/DESIGN.md` for a Documents project), posts, decks, print and video included. Read it before producing anything visible for that project. A taste correction goes there the same turn, one line, his words and the date: `- No shadows on cards or logos ("No agregues sombras", 2 Oct 2026)`. A project without `DESIGN.md` gets one holding only this section.

# Fusing a brand onto the grammar

1. Brand primary becomes `--ac`; if it fails 4.5:1 on the dark `--bg`, lighten it for dark mode only. Two values, one role.
2. Dark `--bg`: brand hue, saturation about 6%, lightness about 7%, never `#000` or neutral gray. `--sf` lifts it about 8 points of lightness, `--sf2` another 8.
3. Light `--bg`: brand hue, saturation about 4%, lightness about 96%; `--sf` is white.
4. Secondary brand colors become category tints, never surfaces or roles.
5. A brand brings hue, typeface and voice, never geometry.

# Vocabulary

`vocabulary.md` holds settled numbers for primitives, compositions and the floating navigation. Read it when the product needs one of those pieces; it is not an inventory.

# Platform notes

- **Flutter**: roles become a `ThemeExtension`, the `em` root becomes `MediaQuery.textScaler` over a base of 17, radii and spacing live in their own const classes.
- One token system per product; two parallel scales make it look assembled.

# Mocks and verification

- **Flutter mocks are Dart.** A CSS mock never throws a RenderFlex overflow and
  its paddings lie. A proposal for a Flutter screen or component is a sibling
  widget nobody mounts yet, rendered by a golden test into a PNG gallery
  outside the repo (`test/render/*.dart`, output dir from an env var, files
  not ending in `_test.dart` so the suite ignores them). The PNGs go into the
  visual brief as the option. The real screen is not touched until the
  pick. HTML mocks are for web products only.
- **Anything visible is verified by looking**: a headless capture at the `app-testing` viewports, defects marked on it (overlap, clipped control, text past its frame, element under the nav). A requested fix is done only when the capture shows it fixed.
- **Fidelity is exact when a reference was given.** If the ask is "like this
  screenshot", shadow, size, padding, radius and hierarchy are copied, not
  adapted. Adaptation is a separate option, offered next to the copy.

# Before calling it done

A screen that reads generic almost always has a shadow in dark mode, the accent as decoration, a rectangle where a pill belongs, or chrome glued to an edge. Everywhere: one divider weight; no small-radius rectangle beside a pill without a rule; no color-only category; no hardcoded `#fff` or `#000`; no control that does nothing; no spinner; the loading treatment follows what is loading and where (a skeleton shaped like the content when content loads in place, a thin progress bar for a page or flow transition). Native only: no gradient on a card, button, bar or background; no display face on a button, chip or tab; no continuously repainting animation (pulse, shimmer, animated blur), which rules out a shimmering skeleton too.

Why each rule exists: `references/history.md`, read only when changing one.
