# Desktop GUIs and games

Read this for Flutter Linux, Electron, Godot and any app Elias runs himself.

Which session applies:

| App | Session |
|---|---|
| A GUI web cannot cover, where the X11 path is enough | A nested Wayland session, or agentbox with Xvfb (`xvfb-run` is not installed on the laptop). Screenshots come from that session, never the laptop display |
| A game or app his Hyprland session runs on Wayland | `gamescope`, below. Xvfb proves only the X11 path |

Launch inside gamescope: `gamescope --backend headless --expose-wayland -W 1280 -H 720 -- <launcher>`. It gives a real Wayland socket and no window. Check the launcher's log (driver, renderer, surface) and capture from inside that session. The launcher itself carries `--display-driver wayland` so his run takes the verified path.

Without gamescope, the first run he makes is the check: ask for the one log line naming the display driver and renderer.
