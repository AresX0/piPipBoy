# piPipBoy

piPipBoy ΓÇö A PipΓÇæBoyΓÇæstyle UI for Raspberry Pi 5

A retro, Fallout-inspired, PipΓÇæBoy-style user interface designed to run on Raspberry Pi 5 (Raspberry Pi OS / Debian Bookworm). This project provides a modular app framework (FileManager, Map, Environment, Clock, Radio, Update, Debug) with pluggable hardware interface drivers and a desktop Tk-based dev mode.

Features
- Retro green terminal-style UI with theme support (classic green + extras)
- Modular apps: FileManager, Update, Map, Environment, Clock, Radio, Debug
- Hardware support: SPI displays (ILI9486 style), GPIO buttons, rotary encoder (KYΓÇæ040), optional sensors (BME280, DS3231)
- Dev mode: Desktop Tk loop for testing on Windows/Linux
- Optional systemd service to auto-start on boot

Hardware requirements
- Raspberry Pi 5 running Raspberry Pi OS (Bookworm)
- Optional SPI display (ILI9486-compatible), buttons and rotary encoder
- Optional sensors: BME280 (I2C), DS3231 RTC (I2C), GPS (serial)

Optional hardware
- Additional optional hardware (camera, WS281x LED strips, SSD1306 OLED, gpio-based fans) can be installed on a Pi. See `docs/OPTIONAL-HARDWARE.md` for recommended packages and installation notes.

Installation (Raspberry Pi)
1. Clone: `git clone https://github.com/AresX0/piPipBoy /home/pi/pipboy`
2. Create venv: `python3 -m venv venv && source venv/bin/activate`
3. Install OS packages (example): `sudo apt update && sudo apt install -y python3-dev python3-pip python3-venv libatlas-base-dev python3-tk`
   - Note: `python3-tk` is required for the Tk-based dev UI on Debian/Ubuntu.
4. Install Python deps: `pip install -r requirements-pi.txt`
5. Optional: install systemd service: `sudo bash scripts/install_systemd_service.sh`

Development
1. Create dev venv and install dev deps: `pip install -r requirements-dev.txt`
2. Run in dev mode: `python -m pipboy` or `python src/pipboy/main.py --dev`
3. Run tests: `pytest -q`

Acknowledgements
- Portions of this project build upon the `app` module from **piboy** by SirLefti (MIT). See https://github.com/SirLefti/piboy ΓÇö MIT license notices are preserved in adapted files and credited in `CREDITS.md`.

License
- This repository is distributed under **GPL-3.0**. Any MIT-licensed code we adapt is retained with its original notices; the combined project is licensed under GPL-3.0 (see `LICENSE` and `CREDITS.md`).

Screenshots
- (placeholder) screenshots/ui-home.png
- (placeholder) screenshots/ui-map.png

Repository cleanup note
- This repository's history was cleaned to remove several large binary artifacts (Playwright browsers, packaged executables, and other build artifacts) to improve clone/push performance. Non-core files were moved into `archive/` to keep the root focused. The application source is located at `src/pipboy/`; development scripts, tests, and resources required for local development and CI are available at the repository root or under `archive/` if previously archived.

