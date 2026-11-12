# When Elias wants to watch: T3's browser and device panel

In a T3 session, T3 drives a browser and a simulator itself and shows them to him, so use its tools when he wants to see the app working or a recording of it. Batches of captures at every viewport stay on Playwright and `adb`.

| He wants | T3 tool | Notes |
|---|---|---|
| To watch the web app, or a capture of one state | `preview_open` with the dev server (`target: {kind: "environment-port", port}`), `preview_resize` with a preset (`iphone-12-pro`, `pixel-7`) or the viewport, `preview_set_appearance`, `preview_snapshot` with `save: true` | The preview opens inline in his thread; `open: false` keeps it in the background. Sign in with the seeded account, as everywhere |
| A recording of a web flow | `preview_recording_start`, the flow with `preview_act` and `preview_wait_for`, then `preview_recording_stop` | It returns a local file; show it in the thread. Proof video for a PR stays a laptop row |
| To watch the Android emulator | `device_list`, `device_open` (boots it and streams it to his Device panel), `device_screenshot`, then `device_close` with `shutdown: true` | On agentbox it is the same 4 GB emulator: open it only when `agents heavy` holds no job and Gradle is stopped |

Both need the host prepared once. The browser fails with "AppArmor ... blocks the sandbox" until `sudo env "PATH=$PATH" t3 browser setup` runs on that host. The device tools answer "device access is turned off" until device access is enabled in T3's settings (`enableDeviceSupport` and `enableAgentDeviceAccess`); a thread started before that keeps the old answer until it restarts. Say which one is missing and fall back to the headless recipe in `references/web.md` or `references/android.md`.
