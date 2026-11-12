# Writing DESIGN.md

Read this when a repo has no `DESIGN.md`, or when the `design-identity` hook reports a missing field.

The lock is a file. The hook refuses a `.tsx`, `.css` or `.html` write in a repo with a `package.json` until `DESIGN.md` exists and is complete. The lock does not reach a repo of another owner (an organization's, where `agents pr-policy` turns no gate on), because its design follows that owner's process, nor a React Native or Expo app (a nearest `package.json` that depends on `react-native` or `expo`), because its `.tsx` draws native views. The same hook blocks the line that imports a Google font the file does not name, and any stock Tailwind neutral (`slate`, `gray`, `zinc`, `neutral`, `stone`) by class or by hex, also in what a Bash heredoc or redirection writes.

One line per field, label then colon. Every one is required:

| Line | What goes there | What it prevents |
|---|---|---|
| `Picked:` | His literal words in quotes and the date | Building without a direction he chose |
| `Display face:` | The face for titles and numerals, and where it is self-hosted | Geist, Inter, whatever the scaffold shipped |
| `Body face:` | The text face, and where it lives | One family doing every job |
| `Brand hue:` | The hex the neutrals derive from | Brand as garnish on gray |
| `Neutrals:` | `--bg`, `--sf`, `--ink`, `--mute` as hexes, from the brand hue (the fusing steps in `SKILL.md`) | Tailwind slate under a product name |
| `Accent:` | The hex and the two places it is allowed: action and selection | Accent as decoration |
| `Radius:` | The scale, in px, per element class | `rounded-md` on everything |
| `Signature:` | The one element the page is remembered by | A page that violates nothing and contains nothing |
| `Borrowed from:` | The real product each structural idea comes from | Inventing from memory |
| `Rejected default:` | What the scaffold would have produced, named | Shipping it without noticing |
| `Imagery:` | Photography, illustration or none, with the reason | Logos in boxes for a business with a warehouse |

The file is written after the pick, from the mocks, and it is the source the
components in a visual brief copy their inline `font-family`, `background` and `color`
from. Stock `slate` stays legal only when the `Neutrals:` line names it on
purpose, with the reason next to it.
