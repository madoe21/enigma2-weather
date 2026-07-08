# Codebase map (onboarding 2026-07-08)

**enigma2-weather** — Enigma2 (OpenATV 7.6) plugin: current weather + forecast
on the TV. Python. ~1400 LOC.

## Layout
- `src/Weather/plugin.py` (~134 LOC) — entry.
- `src/Weather/core/service.py` (~221) — weather provider client + model.
  **`core/` = platform-agnostic data layer.**
- `src/Weather/screens.py` (~636) — enigma2 GUI.
- `res/`, `control/`, `build/` (gitignored ipk).

## Conventions
- Enigma2 Py3; timeouts on provider calls (main reactor thread).
- Location/units are user config — keep out of `core/` (inject).

## Kodi portability: **already split**
`core/service.py` separated from the enigma2 GUI. Verify `core/` is
enigma2-free (config injected), then a Kodi port only needs `platform/kodi/`.
Reference-shaped (with lotto, stocks).
