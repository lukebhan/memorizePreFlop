# Changelog

## Unreleased

- Fixed range files that have no Raise hands (only calls, only all-ins, or any combo without a raise) failing to reopen. Such files start with `;` and the reader crashed on the empty raise section.

## 2026-07-08

- Added a "Raise All-In" category (color, range files, trainers, reports).
- UI auto-fits the window size and opens smaller.
- Ctrl + mouse wheel zooms the whole UI.
- Added `build.py` and a CI workflow that builds and releases Windows/macOS/Linux binaries.
