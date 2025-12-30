# Architecture Overview

This document explains the high-level architecture of the piPipBoy project and the responsibilities of each module boundary.

## High-level components

- src/pipboy/
  - interface/ — UI and hardware interface abstraction (Tk dev UI, display drivers, input mapping, AppManager)
  - driver/ — Hardware access drivers (I2C, SPI, UART, sensors, specific hardware profiles like Freenove)
  - app/ — Modular apps (FileManager, Map, Environment, Clock, Radio, Update, Debug)
  - data/ — Data providers (map tile provider stubs, IP/geolocation stubs)
  - resources/ — Fonts, images, theme assets
  - main.py — Entry point that selects dev vs hardware mode and wires the AppManager

## Responsibilities

- Interface layer: Provide stable rendering and input hooks for apps. Implement display backends and an AppManager that runs apps and coordinates inputs. Keep hardware-specific initialization out of apps.
- Driver layer: Small, testable wrappers around hardware interfaces (I2C, SPI, serial) with graceful degradation when hardware is absent.
- App layer: UI logic and per-app rendering. Apps should expose `render(ctx)` and `handle_input(event)` and avoid direct hardware calls — they get sensors/peripherals injected.
- Data layer: Non-networked stubs and extension points for tile providers and other external data. No direct network calls in core; use environment/config to point to caches or offline providers.

## Boot flow
1. main.py loads config (generating defaults if missing)
2. Detect platform (Raspberry Pi vs dev). In dev: run TkInterface. On Pi: initialize drivers and hardware interfaces, then start HardwareInterface loop.
3. AppManager drives rendering loop and delegates inputs and updates to apps.

## Testing and CI
- Unit tests mock hardware layers and assert app behavior via `tests/*`.
- Linting/formatting enforced via `pyproject.toml` (black, ruff).

## Extensibility
- Add new display drivers by implementing `display.draw(framebuffer)` and adding a small wrapper in `interface/`.
- Add new apps by subclassing `App` (see `app/base.py`) and adding to the AppManager.

