# Web stacks

Read this for Next.js, Vite and Flutter web.

| Stack | Launch | Drive | Notes |
|---|---|---|---|
| Flutter web | `flutter run -d web-server --web-port 8080 --dart-define-from-file=dart_define.json` | `flutter drive` with `chromedriver --port=4444` and `--headless`, or Playwright against `localhost:8080` | Each login needs a fresh browser context: the Supabase or Firebase session persists in the profile |
| Next.js / Vite | `pnpm dev` on a port that is free (`ss -ltn`) | Playwright headless (`npx playwright`, or the repo's own dependency) at the real viewports | Run against the repo's emulators when it has them (`pnpm emuladores`), not the shared Neon or Firestore |

Video of a web flow: Playwright with `recordVideo: { dir, size }` at the viewport of the capture. Keep a clip under 30 s; publish it with `agents evidence ... --gif`.

Drawing defects on a capture (overlap, clipped control, text outside its frame): the ConoceRD web repo has the pattern in `.artifacts/senal.mjs`; reuse the idea, not the file.
