"""Main entry point for piPipBoy
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml

from . import __version__

CONFIG_PATH = Path(__file__).parent / "config.yaml"


DEFAULT_CONFIG = {
    "theme": "green",
    "themes": {
        "green": {"fg": "#99ff66", "bg": "#001100"},
        "amber": {"fg": "#ffd24d", "bg": "#1a0f00"},
    },
    "display": {"type": "ili9486", "rotation": 0},
    "input": {"type": "gpio"},
    "ui": {"fullscreen": False, "touch": False, "touch_target": 48},
}


def choose_gpio_pin_factory(force: bool = False, prefer: str | None = None):
    """Choose a GPIOZERO pin factory.

    Preference order: lgpio -> pigpio (only if pigpiod is connected) -> default.
    When running under pytest we avoid mutating the environment unless `force=True` is
    passed — this prevents tests from accidentally claiming real GPIO hardware during
    the unit test process.

    For easier testing, `prefer` may be set to 'lgpio' or 'pigpio' to force that
    path without relying on import-time side effects.
    """
    # If running under pytest and not forced, skip automatic selection to avoid
    # claiming hardware pins used by other processes or test fixtures.
    if not force and os.environ.get('PYTEST_CURRENT_TEST'):
        print("Running under pytest; skipping automatic pin-factory selection (use force=True to override)")
        return

    # If caller explicitly requested a path, try that first
    if prefer == 'lgpio':
        try:
            import lgpio  # type: ignore
            os.environ.setdefault('GPIOZERO_PIN_FACTORY', 'lgpio')
            print("Using lgpio for gpiozero pin factory (forced)")
            return
        except Exception:
            print("Forced lgpio selection failed: lgpio import error")
    elif prefer == 'pigpio':
        try:
            import pigpio  # type: ignore
            print("pigpio module found; attempting to connect to pigpiod (forced)")
            try:
                pi_instance = pigpio.pi()
                if getattr(pi_instance, "connected", False):
                    os.environ.setdefault('GPIOZERO_PIN_FACTORY', 'pigpio')
                    print("Using pigpio for gpiozero pin factory (pigpiod connected, forced)")
                    return
                else:
                    print("pigpio present but pigpiod not connected; forced pigpio selection skipped")
            except Exception as e:
                print("pigpio found but pigpiod failed to initialize (forced):", e)
        except Exception:
            print("Forced pigpio selection failed: pigpio import error")

    # Default behavior: prefer lgpio when available
    try:
        import lgpio  # type: ignore
        os.environ.setdefault('GPIOZERO_PIN_FACTORY', 'lgpio')
        print("Using lgpio for gpiozero pin factory")
        return
    except Exception:
        # lgpio not available; continue to pigpio probe
        pass

    try:
        import pigpio  # type: ignore
        print("pigpio module found; attempting to connect to pigpiod")
        try:
            pi_instance = pigpio.pi()
            if getattr(pi_instance, "connected", False):
                os.environ.setdefault('GPIOZERO_PIN_FACTORY', 'pigpio')
                print("Using pigpio for gpiozero pin factory (pigpiod connected)")
            else:
                print("pigpio present but pigpiod not connected; skipping pigpio pin factory")
        except Exception as e:
            # Helpful message for pigpiod init errors (e.g., DMA mmap failures on Pi 5)
            print("pigpio found but pigpiod failed to initialize:", e)
    except Exception:
        # No pigpio available; leave default factory
        pass


def is_raspberry_pi() -> bool:
    # Simple heuristic: presence of /proc/device-tree/model and 'Raspberry' in it
    try:
        with open("/proc/device-tree/model", "r") as f:
            return "Raspberry" in f.read()
    except Exception:
        return False


def ensure_config():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(yaml.safe_dump(DEFAULT_CONFIG))


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Run in desktop dev mode (Tk)")
    parser.add_argument("--profile", type=str, default=None, help="Hardware profile name (e.g., 'freenove')")
    args = parser.parse_args(argv)

    ensure_config()

    dev_mode = args.dev or (not is_raspberry_pi())

    # Initialize common sensors (I2C-backed and serial GPS)
    from .driver.i2c import I2C
    from .driver.sensors.bme280 import BME280
    from .driver.sensors.ds3231 import DS3231
    from .driver.sensors.gps import GPS

    i2c = I2C()
    bme = BME280(i2c if i2c.available else None)
    rtc = DS3231(i2c if i2c.available else None)
    gps = GPS()
    sensors = {"bme280": bme, "rtc": rtc, "gps": gps}

    if dev_mode:
        print(f"piPipBoy {__version__} — starting in DEV (Tk) mode")
        from .interface.tk_interface import TkInterface
        from .interface.icon_utils import find_or_create_icon
        from pathlib import Path

        # Ensure developer-friendly icons exist (case-insensitive names will be
        # matched or a placeholder generated) so desktop launches show icons.
        repo_icons = Path(__file__).parent.parent / "resources" / "icons"
        src_icons = Path(__file__).parent / "resources" / "icons"
        for name in ("Camera", "FileManager", "Lights", "Fan", "Display"):
            p = find_or_create_icon(name, [src_icons, repo_icons])
            print(f"Icon for {name}: {p}")

        # Attach runtime icon support so the dev UI will use repository icons
        ui = TkInterface(CONFIG_PATH, sensors=sensors)
        try:
            from .interface.tk_icons_patch import attach_icon_support
            attach_icon_support(ui)
        except Exception:
            pass
        ui.run()
    else:
        print(f"piPipBoy {__version__} — starting on Raspberry Pi hardware")
        # Select and configure GPIO pin factory (prefer lgpio, else pigpio if pigpiod is available)
        choose_gpio_pin_factory()
        # Choose pin factory before importing hardware interfaces
        # Import real hardware interfaces and wire them to an AppManager
        try:
            from .interface.ili9486_display import ILI9486Display
            from .interface.gpio_input import GPIOInput
            from .interface.app_manager import AppManager
            from .interface.hardware_interface import HardwareInterface
            from .app.file_manager import FileManagerApp
            from .app.map import MapApp
            from .app.environment import EnvironmentApp
            from .app.clock import ClockApp
            from .app.radio import RadioApp
            from .app.update import UpdateApp
            from .app.debug import DebugApp
            # Extended device apps
            from .app.fan import FanApp
            from .app.camera import CameraApp
            from .app.lights import LightsApp
            from .app.display import DisplayApp

            # Support hardware profiles (e.g., freenove) for pre-wired setups
            profile = args.profile
            if profile == "freenove":
                from .driver.freenove_case import create_hardware

                app_manager = AppManager([
                    FileManagerApp(),
                    FanApp(),
                    CameraApp(),
                    LightsApp(),
                    DisplayApp(),
                    MapApp(sensors=sensors),
                    EnvironmentApp(sensors=sensors),
                    ClockApp(sensors=sensors),
                    RadioApp(),
                    UpdateApp(),
                    DebugApp(),
                ])
                hw = create_hardware(app_manager)
                # hw.peripherals available to apps via app_manager.peripherals
                hw.run()
            else:
                display = ILI9486Display()
                inputs = GPIOInput()
                apps = [
                    FileManagerApp(),
                    FanApp(),
                    CameraApp(),
                    LightsApp(),
                    DisplayApp(),
                    MapApp(sensors=sensors),
                    EnvironmentApp(sensors=sensors),
                    ClockApp(sensors=sensors),
                    RadioApp(),
                    UpdateApp(),
                    DebugApp(),
                ]
                app_manager = AppManager(apps)
                hw = HardwareInterface(display, inputs, app_manager)
                hw.run()
        except Exception as e:
            print("Hardware initialization failed:", e)
            print("Falling back to dev mode (Tk)")
            from .interface.tk_interface import TkInterface

            ui = TkInterface(CONFIG_PATH, sensors=sensors)
            ui.run()


if __name__ == "__main__":
    main()




