# Web checklist

Web execution rules. They replace the grammar's web rows (the Web table in `SKILL.md`) and assume `DESIGN.md` exists. Run them before code and before done.

## 1. Read the brief first

- State the design read in one line before any code: "Reading this as: <page kind> for <audience>, with a <vibe> language, leaning toward <system or aesthetic>." The audience picks the aesthetic, not your taste.
- If the brief genuinely splits two ways, ask one question; otherwise declare the read and proceed.
- A redesign starts with an audit: brand tokens, information architecture, what works, what is filler, SEO baseline. Keep URLs, nav labels, form field names, logo and legal copy unless Elias approves the change.
- When the brief maps to a real design system (Fluent, Material 3, Carbon, Primer, Polaris, GOV.UK, USWDS, Radix Themes, shadcn/ui), install the official package instead of recreating it, one system per project. shadcn/ui ships customized, never in its default state.

## 2. Stack defaults

- Tailwind v4 (with `@tailwindcss/postcss` or the Vite plugin), React or Next.js with Server Components by default. Anything with motion, scroll listeners or pointer physics is an isolated `'use client'` leaf.
- Check `package.json` before importing a library and print the install command when it is missing.
- Fonts through `next/font` or self-hosted `@font-face` with `font-display: swap`, the faces `DESIGN.md` names.
- Icons from one family (`@phosphor-icons/react`, `hugeicons-react`, `@radix-ui/react-icons` or `@tabler/icons-react`; `lucide-react` only on request), `strokeWidth` fixed globally at 1.5 or 2. Glyphs come from the library, so a missing icon means a second library, not a hand-drawn path.
- Continuous values driven by input (scroll progress, pointer position) live in Motion's `useMotionValue`/`useScroll`, because `useState` re-renders the tree on every frame.

## 3. Layout that holds

- Breakpoints `sm 640`, `md 768`, `lg 1024`, `xl 1280`, `2xl 1536`; page containment `max-w-7xl mx-auto` or `max-w-[1400px]`; full-height sections use `min-h-[100dvh]` so the iOS address bar does not make them jump.
- CSS Grid for multi-column layouts, and every multi-column section declares its collapse under 768 px in the same component.
- The hero fits the first viewport: headline at most 2 lines, subtext at most 20 words, the primary CTA visible without scrolling, top padding at most `pt-24`. At most four text elements: one eyebrow or brand strip, headline, subtext, CTAs. Trust logos, taglines and pricing teasers go in the section below it.
- Plan headline size with the hero asset: `text-4xl md:text-5xl lg:text-6xl` by default, larger only for a 3 to 5 word headline.
- Navigation stays on one line at desktop and 64 to 72 px tall (80 at most), and condenses to a hamburger rather than wrapping; a full-bleed or edge-pinned bar is legal on web.
- Each section uses a different layout family from its neighbors; a page of eight sections uses at least four families, and no more than two image-and-text splits run in a row.
- A bento grid has exactly as many cells as items, with real variation (image, pattern, tint) in at least two of them.
- Section headers stack the headline over its body text; a small explainer floating beside a big headline reads as filler.
- One theme for the whole page (light, dark or system), and both modes designed and checked when the page follows the system.

## 4. Type, color, shape

- One accent, under 80% saturation, used identically across the page. Neutrals come from `DESIGN.md`, never stock Tailwind grays the file does not name.
- One radius system for the page, written down if it mixes (for example pill buttons, 16 px cards, 8 px inputs).
- Sans display by default; a serif only when the brand names one or the brand is genuinely editorial or heritage. `Inter` is discouraged; `Fraunces` and `Instrument Serif` are banned. No pure `#000000` or `#ffffff`. Emphasis inside a headline is italic or bold of the same family, and italic display words with descenders get `leading-[1.1]` and a little bottom reserve.
- Body text at most 65ch wide, WCAG AA contrast for body and every CTA, form label, placeholder and focus ring.
- Cards only where elevation means hierarchy; otherwise group with spacing or a single divider. A shadow, when used, is tinted to the background.

## 5. Content and copy

- Real images: a generation tool when one is available, otherwise `https://picsum.photos/seed/<descriptive-seed>/<w>/<h>` or the brand's own assets, and an explicit list of placeholder slots for Elias when neither exists. Product previews are real screenshots or real components, never rectangles made to look like one.
- Logo walls are logos only (Simple Icons or a simple generated mark), placed under the hero.
- Short sections: a headline of about 8 words, a paragraph of about 25, one visual or one CTA. Lists longer than five items become a grid, tabs, a carousel or grouped chunks.
- One label per intent across the page ("Contact" everywhere, not three phrasings) and CTA labels that fit on one line.
- Numbers are real or labeled as sample data. Names, brands and data read as believable and local.
- Re-read every visible string before shipping and replace anything cute, vague or grammatically odd with a plain functional sentence.
- Quotes run at most 3 lines with name, role and company.

## 6. Motion

- Every animation has a reason in one sentence (hierarchy, story, feedback, state change); otherwise it goes.
- Animate `transform` and `opacity` only, honor `prefers-reduced-motion` for everything above subtle, and clean up every effect.
- Scroll work goes through Motion `useScroll`, GSAP ScrollTrigger (pinned stacks start at `"top top"`), IntersectionObserver or CSS scroll-driven animations; a raw `scroll` listener janks.
- One marquee per page at most. Loading states follow what is loading and where: a skeleton shaped like the final layout when content loads in place, a thin progress bar for a page or flow transition, never a spinner; plus designed empty and error states.

## 7. Tells to remove before shipping

These are the patterns that make a page read as generated. Remove each one unless the brief asks for it:

- AI purple or blue glow, neon outer glows, gradient text on large headers, custom cursors.
- A centered hero over a dark mesh, three equal feature cards, cream background with a serif display and terracotta accent, or the beige, brass and espresso palette on a premium brief.
- An eyebrow above every section (at most one per three sections), numbered section labels (`01 / 04`, `006 How it works`), version badges in the hero, scroll cues.
- Decorative status dots, pills overlaid on photos, photo-credit captions on stock images, locale or weather strips, decorative hairline grids, rows with a border above and below each item.
- Filler copy: "Elevate", "Seamless", "Unleash", "Quietly trusted by", poetic section labels, micro sentences under eyebrows.

## 8. Before calling it done

Capture it headless at the viewports the `app-testing` skill lists, in both modes when the page follows the system, and check against this list: hero fits, nav on one line, no CTA wraps, contrast passes, eyebrow count, layout families vary, no tell from section 7, reduced motion works, empty and error states exist.
