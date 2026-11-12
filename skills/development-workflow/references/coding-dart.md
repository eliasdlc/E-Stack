# Dart and Flutter preferences

Read only for Dart or Flutter code, after `references/coding.md`.

- `dynamic` is the `any` of Dart. Same enemy. Prefer sealed classes and pattern matching over runtime type checks.
- Widgets stay small and named. A `build` method that scrolls is a refactor you skipped, not a style choice.
- Extract widgets into classes, not into methods that return a `Widget`: methods break `const`, rebuild scope, and hot reload.
- `const` constructors wherever they are legal. They are the cheapest performance win in the framework.
- State management follows the repo. Do not introduce a second solution alongside the one already there.
- Anything async that touches a `BuildContext` guards with `context.mounted` first.
