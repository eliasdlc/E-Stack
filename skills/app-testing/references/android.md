# Android and the phone

Read this for Flutter Android, the phone, and any `native` or `device-simulated` row.

## Launch

Emulator with `-no-window -no-audio -gpu swiftshader_indirect`, then `flutter run -d emulator-5554`. Drive with `adb shell input` for taps, `adb exec-out screencap -p` for captures, `integration_test/` for flows. A physical phone via `adb devices` serves measurements; a flow that signs in uses the seeded account, not Elias's.

## Preflight and receipt

Preflight before any `native` capture counts: the real `MapWidget` is mounted, the style finished loading, and `adb logcat` shows no swallowed native error (`addStyleImage`, `NullPointerException`, style errors). A capture taken while a native call failed silently is not evidence of that feature.

Publish `native` and `device-simulated` captures with `agents evidence ... --receipt <package> --apk <installed APK>` right after capturing, before any reinstall, from a clean worktree.

## Order of a physical gate

Fixed: `adb devices -l` first. No phone: build anyway, say "gate parked" and list what stays unverified. Phone present: install, `adb shell dumpsys package <pkg> | grep versionCode` and compare with the receipt before the first scenario. Scenarios then, one capture each.

## Actions on Elias's phone

Name these actions on Elias's phone in the message before they run: `pm clear` of any package, installing a package other than the review app, deleting app data or traces, changing system settings, granting or revoking permissions. Accounts on the device: the throwaway test account only.

## Video on the laptop

`adb shell screenrecord --bit-rate 8000000 --time-limit 30 /sdcard/r1.mp4`, then `adb pull` and `adb shell rm` it. Keep a clip under 30 s; publish it with `agents evidence ... --gif`, which adds the inline GIF preview next to the link.

## The emulator on agentbox runs once per batch

A task PR does not boot it: the implementer ships tests and renders, and the orchestrator starts one fixed emulator (`crd34`) for one session over the `device-simulated` rows (left as `Pending: batch`) of every merged task PR on the combined head (`dev` before the release), fixes failures in parallel, and runs a second session on the new head. In Kino the same batch runs with Playwright against one preview. Phone rows (`native`, `real-trip`) run in one laptop session for the batch.

## Heavy steps

Run the build and the emulator through `agents heavy` (one lock per resource inside a memory cap), never next to Gradle; the emulator takes about 4 GB. `agents heavy --status` shows holders; a wait that can pass 600 s runs with `run_in_background`, and `--wait-max SECONDS` ends a foreground wait earlier.

1. Build first: `agents heavy --mem 5G -- flutter build apk --debug`, then `./gradlew --stop` in `android/`.
2. Boot from the snapshot: `agents heavy --mem 4500M -- emulator -avd crd34 -no-window -no-audio -gpu swiftshader_indirect &` (the emulator lock is held while it runs, so stop it once the captures are done; the first cold boot takes about 4 minutes and saves the snapshot).
3. Wait for `adb shell getprop sys.boot_completed` to print 1, then 60 s more, and dismiss "not responding" dialogs before the first capture.
4. Install, drive through `uiautomator dump` and the Flutter semantics labels, capture with `adb exec-out screencap -p`.
5. Always end with `adb emu kill`, in a `trap` so a failure also ends it.
