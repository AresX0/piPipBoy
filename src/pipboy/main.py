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
}


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

        ui = TkInterface(CONFIG_PATH, sensors=sensors)
        ui.run()
    else:
        print(f"piPipBoy {__version__} — starting on Raspberry Pi hardware")
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

            # Support hardware profiles (e.g., freenove) for pre-wired setups
            profile = args.profile
            if profile == "freenove":
                from .driver.freenove_case import create_hardware

                app_manager = AppManager([
                    FileManagerApp(),
                    MapApp(),
                    EnvironmentApp(sensors=sensors),
                    ClockApp(),
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
                    MapApp(),
                    EnvironmentApp(sensors=sensors),
                    ClockApp(),
                    RadioApp(),
                    UpdateApp(),
                    DebugApp(),
                    PeripheralsApp(),
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
