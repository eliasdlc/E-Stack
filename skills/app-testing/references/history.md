# Why the app-testing rules exist

The incidents behind the rules in `SKILL.md`. Read this only when a rule
is being changed or questioned. Stories live here and not in HTML comments
inside the skill, because a comment in a SKILL.md reaches the model (measured).

## Headless, with a seeded account

In August, Elias wrote "in the background" eighteen times and "I already signed
in" eleven times. Every one came from an app launched in the foreground of his
screen or a flow driven through his own login. The skill exists to make the
headless path, with a seeded account, the cheap one.

## Edge cases

Elias's list of 21 Oct 2026. The ConoceRD v0.17 review audit of the same day
backs most lines: 150 % text scale in 10 of 43 rounds, shared or global state
in 6, clocks in 3, a pill cut at 430x748 (#220), offline and slow-link errors
(#224, #225), a draft back on cold start (#223), a GPS trace after sign-out
(#224), a FAB in loading and error states (#234). Light and dark has no audit
finding; it is on the list because every state is captured in both themes.
Most lines are defect classes reviewers kept finding after the author had
called the work done.

## Batched device sessions

Speed round, 26 Oct 2026, decision 5A: the emulator held the machine lock for
8 h straight while implementers sat at 68% waiting. One session per batch
keeps the machine free.

## Games and gamescope

Booga twice ran but never showed on his Hyprland session: Godot fell to
XWayland and llvmpipe, which Xvfb could not reveal because it proves only the
X11 path.

## Evidence road

A raw logcat pushed with `gh api` skipped every scan and put a Firebase App
Check debug token in the public evidence repo. Camo, GitHub's image proxy,
caches by URL, which is why the sha7 is part of the path.
