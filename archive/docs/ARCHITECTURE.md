# Architecture Overview

piPipBoy is organized into clear layers to keep hardware-specific code separated from UI and app logic.

- src/pipboy/interface: Display and input abstractions (TkInterface, ILI9486 driver scaffold, GPIO input). Dev mode uses Tk for desktop testing.
- src/pipboy/driver: Low-level hardware drivers (SPI/I2C/sensor hooks). Keep drivers minimal and testable.
- src/pipboy/app: Modular apps (FileManager, Map, Clock, Environment, Update, Radio, Debug). Each app implements a simple `render(ctx)` and `handle_input(event)` API.
- src/pipboy/data: Data provider stubs (tile providers, IP/geolocation providers). No hardcoded network calls; provider interfaces allow offline caches.
- resources: Fonts and theme assets (open fonts only)

Design goals
- Modular, testable, and small modules
- Dev mode parity: Desktop Tk interface behaves similarly to embedded display rendering so UI logic is testable on non-Pi systems
- Explicit extension points for hardware and data providers
