"""Freenove Computer Case hardware driver adapter

Provides helpers to create display and input instances configured for the
Freenove case kit. This module intentionally depends on the project's
`ILI9486Display` and `GPIOInput` abstractions so it remains small and
testable (no hardware I/O at import time).

Attribution: Hardware/layout documented by Freenove in
Freenove_Computer_Case_Kit_for_Raspberry_Pi (CC BY-NC-SA 3.0). Do not use
Freenove-supplied code for commercial purposes and retain attribution.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..interface.ili9486_display import ILI9486Config, ILI9486Display
from ..interface.gpio_input import GPIOInput


@dataclass
class FreenoveConfig:
    # SPI bus/device for display (placeholder values; Freenove examples use bus 0)
    spi_bus: int = 0
    spi_device: int = 0
    dc_pin: int = 24
    reset_pin: int = 25

    # Default input wiring used by the Freenove Computer Case (typical mapping)
    # These map logical names used by the app to BCM GPIO pin numbers
    input_mapping: dict = None

    def __post_init__(self):
        if self.input_mapping is None:
            self.input_mapping = {
                "up": 5,
                "down": 6,
                "left": 16,
                "right": 20,
                "select": 13,
                "back": 19,
                # rotary encoder pins (A, B, switch)
                "rotary_a": 17,
                "rotary_b": 27,
                "rotary_sw": 22,
            }


class FreenoveCase:
    def __init__(self, cfg: FreenoveConfig | None = None, spi: Any | None = None):
        self.cfg = cfg or FreenoveConfig()
        self.spi = spi

    def create_display(self) -> ILI9486Display:
        disp_cfg = ILI9486Config(
            spi_bus=self.cfg.spi_bus,
            spi_device=self.cfg.spi_device,
            dc_pin=self.cfg.dc_pin,
            reset_pin=self.cfg.reset_pin,
        )
        return ILI9486Display(config=disp_cfg, spi=self.spi)

    def create_inputs(self) -> GPIOInput:
        return GPIOInput(mapping=self.cfg.input_mapping)


def create_hardware(app_manager: Any, cfg: FreenoveConfig | None = None, spi: Any | None = None, use_backends: bool = False):
    """Convenience: create a fully wired HardwareInterface instance for the Freenove case.

    If `use_backends` is True, attempt to instantiate real hardware backends (PWM, WS281x, I2C OLED, camera).
    This keeps the wiring code in one place for tests and simplifies app startup.
    """
    from ..interface.hardware_interface import HardwareInterface
    from .peripherals import FanController, LEDController, OLEDController, CameraInterface
    from .backends import create_fan_backend, create_led_backend, create_oled_backend, create_camera_backend

    case = FreenoveCase(cfg=cfg, spi=spi)
    display = case.create_display()
    inputs = case.create_inputs()

    fan_backend = create_fan_backend(cfg.input_mapping.get("fan_pin") if cfg and cfg.input_mapping else None) if use_backends else None
    led_backend = create_led_backend() if use_backends else None
    oled_backend = create_oled_backend() if use_backends else None
    camera_backend = create_camera_backend() if use_backends else None

    fan = FanController(pwm=fan_backend, pin=cfg.input_mapping.get("fan_pin") if cfg and cfg.input_mapping else None)
    leds = LEDController(driver=led_backend)
    oled = OLEDController(device=oled_backend)
    camera = CameraInterface(backend=camera_backend)

    peripherals = {"fan": fan, "leds": leds, "oled": oled, "camera": camera}

    hw = HardwareInterface(display=display, inputs=inputs, app_manager=app_manager)
    # Attach peripherals to the hardware interface and app_manager for easy access
    hw.peripherals = peripherals
    try:
        # Also provide a convenience reference on the AppManager so apps can access peripherals
        app_manager.peripherals = peripherals
    except Exception:
        pass
    return hw
