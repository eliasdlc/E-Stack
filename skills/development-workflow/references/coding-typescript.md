# TypeScript preferences

Read only for TypeScript code, after `references/coding.md`.

- `any` is the enemy. Inferred types are our friend. Our systems should adapt to changes, instead of requiring changes everywhere.
- If your TS code looks like a Python dev wrote it, it is bad TS code.
- Avoid one-line functions that are just casting wrappers.
- Write TS in ways that Matt Pocock and Theo would be proud of.
- If not already specified in project, I generally like to use the following tech: Convex or Neon, Tailwind, React, NextJS, Vite, Drizzle, pnpm.
- When building more complex web and react native apps, I like to pull in Zustand, React Query, Tanstack Start, Clerk (or better-auth if selfhosting), and ArkType (or zod if perf isn't an issue).
