# What each machine captures

Read this when a Proof row depends on which machine runs it: video, frame rate, a login, the native map or a GUI that must render. The summary table is in `SKILL.md` ("Which machine captures what").

## The laptop records the video

Motion, transitions and flows on the phone go through `adb shell screenrecord`, and web through Playwright, both headless (recipes in `references/android.md` and `references/web.md`). Rows a task PR left as `Pending: batch` wait for one device session before the release: the laptop records them together, and the release PR lists them under `## Release checklist` with their receipts. The laptop has `playwright` and `chromium`; it does not have `xvfb-run`.

## Agentbox, verified

- **The emulator runs** (verified 27 Sep 2026): AVD `crd34`, Pixel 6, Android 14 x86_64, `-no-window -gpu swiftshader_indirect`. Cold boot took 243 s and froze system services for the first minute; after that a ConoceRD debug build launched in 8.5 s and answered taps driven by `adb` and `uiautomator dump`. It takes about 4 GB, so it never runs next to Gradle; the recipe is in `references/android.md`. It proves "it works" with screenshots. It cannot show frame rate (gfxinfo misses Impeller frames), anything behind a login (the test account secret is not provisioned there) or the native Mapbox map, and it records no video: its motion is swiftshader's, not the phone's.
- **`flutter doctor` gaps**: no `google-chrome` (use `-d web-server` plus Playwright, never `-d chrome`), and no Linux desktop toolchain (clang, cmake, ninja, pkg-config missing), so a Flutter Linux desktop build does not run there even with Xvfb.
- **T3's browser and device tools work** (enabled 18 Oct 2026): `t3 browser setup` allowed Chrome's sandbox, so `preview_open` and `html_preview` run; `enableDeviceSupport` and `enableAgentDeviceAccess` are on in `~/.t3/userdata/settings.json`, and `device_list` from a new thread lists `crd34` (Android only, no Xcode). A thread started before the change keeps "device access is turned off" until it is restarted, because the capability is set when the thread starts.
- **Playwright 1.62.1** with Chromium and Firefox already downloaded in `~/.cache/ms-playwright`. Scrape with its Chromium; the snap Firefox is for humans. It is not on `PATH`: drive it with `npx playwright` or from the repo's own dependency.
- **`xvfb-run` is installed** there and not on the laptop, so a GUI that must render belongs to agentbox, as long as it is not a Flutter Linux desktop build.
