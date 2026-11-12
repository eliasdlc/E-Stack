---
name: app-testing
description: Launches, drives, screenshots, records and tests an app end to end on the laptop or agentbox without taking Elias's screen, for Flutter web or Android, Next.js, Vite and desktop GUIs. Owns headless launch per stack, seeded test accounts, the evidence channels, what proves each kind of change, which machine captures what, and what a verified capture is. Use for "test the app", "launch the app", "take some captures", "run the whole flow", "use vision", "computer use", the Spanish equivalent, or any request to see a change working.
---


# Testing an app headless

Run every app headless and signed in with a seeded test account, so Elias's screen and his accounts stay his: no window on his display, no computer use, no session of his.

## The steps

1. Read the repo's AGENTS.md `## Run and verify` and the reference for your stack (table below).
2. Get the seeded account for the role. If a repo has none for the role you need, creating it is the first step of the test, on the task branch, and it goes into the PR.
3. Launch headless and drive the flow as that role, through the control the user touches next.
4. Capture every screen the change touches at its viewports (the list below), walk the edge cases, run the data check behind it.
5. Publish with `agents evidence` and report what ran and what could not.

| Stack | Read before launching |
|---|---|
| Flutter Android, the phone, any `native` or `device-simulated` row | `references/android.md` |
| Next.js, Vite, Flutter web | `references/web.md` |
| Desktop GUI or a game (Flutter Linux, Electron, Godot) | `references/desktop.md` |
| Elias wants to watch it live, or a recording, in his T3 thread | `references/t3-watch.md` |

- Real keys: `set -a; . ~/.config/secrets/<project>.env; set +a`, values never printed.
- A seeded password is test data: fine in the seed and harness, never in a Postplan page or a handoff.

Viewports to capture, listed here and nowhere else: an app (Flutter, Android) at one standard phone, 393x852; web at one phone, 430x748 (Safari with its bars, which shows the defects he reports), and one laptop, 1440x900. Skip 430x932: it hides most of the defects he reports.

## What verified means

A run is verified when all four hold:

1. The flow ran as the role that uses it: doctor, assistant, admin, traveler, business. Say which account.
2. A capture per screen the change touches, at its viewports, with defects drawn on the capture (overlap, clipped control, text outside its frame, element under the nav).
3. The data check behind the screen: the row in the database, the request in the log, the file on disk. A green screen with a missing row is a failure.
4. The report lists what ran, with numbers, and what could not be exercised and why. "It looks fine" is not a report.

Write the action, expected effect and observed effect before promoting a requirement to Verified. Exercise the actual role and consumer of the change, including the controls used next. A step that succeeded (an import, an upload, a page arriving, a diagnostic passing) proves that step, not the outcome the user asked for.

## Evidence channels

Every capture is evidence on one channel, and a claim never rises above the channel that produced it. Channels are not a ladder: each proves its own class of properties. This table is the only catalog.

| Channel | What it is | Proves | Does not prove |
|---|---|---|---|
| `test` | Unit or widget test | logic, every branch of a computation, contracts between classes | anything drawn or timed at runtime |
| `render` | Golden of a widget (ConoceRD: `test/render/mocks/nav_mock_kit.dart` stands in for the Mapbox `MapWidget`) | Dart layout, copy, sizes, overflow | anything a native view draws: map layers and shadows, line styling, sprites, traffic, refresh rate, density, night mode |
| `native` | The real native view on a GPU emulator (`-gpu swiftshader_indirect` at least) or the phone, driven by `adb`; the evidence says which | layers, sprites, shadows, colors, trim, banner at a given distance | timing under real GPS, thermal behavior, refresh rate (a still capture never certifies it) |
| `device-simulated` | Phone or emulator fed a recorded trace or mock locations; the evidence says which, and an emulator is always called an emulator | maneuvers, reroutes, arrival, refresh mode measured as frames over a moving sequence, pill and banner in motion | signal loss, thermal throttling, real sensor noise |
| `real-trip` | Elias driving the review build with the trace recorder on | only the scenarios that occurred, with the trace as data; a trip with no reroute proves nothing about rerouting | anything the trip did not exercise |
| `nonvisual` | Tooling, scripts, rules, CI | its own tests and dry runs | any behavior on a screen |

## What proves each kind of change

Any change a user can see needs a capture of this build: a screen, a component, a color, a font, a size, spacing, copy, an icon, a state (empty, error, disabled, dark). However small.

| Change | The proof | Channel |
|---|---|---|
| New screen or component | Each state (default, empty, error, disabled, dark) at its viewports, plus the data check | `render`; `native` when it draws on the map |
| Color, font, size, spacing, icon, copy | Before and after at the same viewport, cropped to the change, plus one full screen | `render` |
| Changed flow | One capture per step, plus a video of the flow | `render` or `device-simulated` |
| Animation, transition, gesture, scroll | A video with its GIF preview (phone: `adb`; web: Playwright), recorded on the laptop | `device-simulated` |
| Backend, rules, data | Emulator or rules tests, and the query that shows the row, both with literal output | `test` |
| Tooling, CI, scripts, hooks | Passes, fails on a fabricated violation naming its rule, passes | `nonvisual` |
| Refactor with nothing visible | The tests that pin the behavior; for UI code a render diff of 0 pixels against the base | `test` or `render` |
| Performance | The PR's budget table (`development-workflow`, `references/budget.md`) | `nonvisual` |

## Edge cases every change walks

A case the change can reach gets a test or a capture in its row.

| Case | What to check |
|---|---|
| Text scale 150 % | No clipped control, label crossing its edge or unreachable button |
| Every viewport, light and dark | Every state above in both themes; insets paid once (a pill cut at the shorter viewport) |
| Time zone and clock | Device day versus the place's day, overnight hours, AM and PM, a clock the test injects (an open bar shown closed after midnight) |
| Shared or global state | Two trips, screens or accounts over one SDK, singleton or file (per-trip gates over a global map SDK) |
| Offline and slow network | Airplane mode, a timeout on a slow link reported as what it is, retry offered only where it can work |
| Cold start and relaunch | State that survives a kill, a draft that should not come back |
| Signed out and account switch | Nothing of the previous account left on disk or on screen (a GPS trace after sign-out) |
| Loading and error states | Controls that only belong to the loaded state stay hidden (a FAB drawn in the loading and error states) |

## Which machine captures what

The machine running the session does the work. Agentbox gives backend and data proof and Playwright or emulator screenshots; it cannot give video, frame rate, a login (no `conocerd.env`) or the native Mapbox map, so those rows say `Pending: batch` for the laptop's batch session. The laptop records the video (`adb shell screenrecord`, headless Playwright). What each machine has verified, emulator numbers included, is in `references/machines.md`.

## Publishing evidence

**Every file reaches `eliasdlc/evidencia` through `agents evidence`, and only through it**. That repo is public and its history is permanent, so captures come from a seeded account. `agents evidence <project>/<branch>/<sha7> <files> [--gif] [--dir datos]` keeps the original, checks the sha7 is HEAD, scans, and prints the Markdown for Proof.

When it refuses a file, fix the file (crop, redact, a seeded account); never push around it.

Look at each capture yourself: the scan does not see a face, a real place name or a business that is not a test fixture.

The incidents behind these rules are in `references/history.md`; read it only when changing a rule.
