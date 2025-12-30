"""
GPIO abstraction using rpi-lgpio (lgpio) if available; falls back to gpiozero where appropriate.
Provides Buttons (debounced), Rotary encoder stub, and PWM outputs.
"""
from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)

# Try to use lgpio (recommended on Bookworm), otherwise fall back to pigpio or gpiozero
import os

try:
    import lgpio
except Exception:  # pragma: no cover - optional
    lgpio = None

# Prefer lgpio when available, else try pigpio (daemon) and fall back to gpiozero default
def _choose_pin_factory() -> None:
    try:
        if lgpio is not None:
            os.environ.setdefault("GPIOZERO_PIN_FACTORY", "lgpio")
            logger.debug("Using lgpio for gpiozero pin factory")
            return
    except Exception:
        pass

    try:
        # pigpio Python library check (requires pigpiod running)
        import pigpio

        try:
            p = pigpio.pi()
            # pigpio.pi() returns an object with connected attribute (1 if connected)
            connected = getattr(p, "connected", None)
            if connected:
                os.environ.setdefault("GPIOZERO_PIN_FACTORY", "pigpio")
                logger.debug("Using pigpio pin factory (pigpiod connected)")
                try:
                    p.stop()
                except Exception:
                    pass
                return
            else:
                try:
                    p.stop()
                except Exception:
                    pass
        except Exception as e:
            logger.debug("pigpio import or connect failed: %s", e)
    except Exception:
        # pigpio not installed
        pass

    # No special factory selected; use default gpiozero factory
    logger.debug("No special gpio pin factory selected; using default gpiozero factory")

# Run selection at import time
_choose_pin_factory()

try:
    from gpiozero import Button, PWMOutputDevice
except Exception:
    Button = None
    PWMOutputDevice = None


class GPIOManager:
    def __init__(self):
        self._handles = []

    def close(self):
        # release resources
        for h in list(self._handles):
            try:
                h.close()
            except Exception:
                pass
        self._handles.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


class DebouncedButton:
    def __init__(self, pin: int, bounce_time: float = 0.05):
        if Button is None:
            raise RuntimeError("gpiozero.Button required for button support")
        self._btn = Button(pin, bounce_time=bounce_time)

    def when_pressed(self, func):
        self._btn.when_pressed = func

    def when_released(self, func):
        self._btn.when_released = func

    def close(self):
        try:
            self._btn.close()
        except Exception:
            pass


class RotaryEncoder:
    def __init__(self, a_pin: int, b_pin: int, callback=None):
        # Implement as needed: this is a lightweight stub
        self.a_pin = a_pin
        self.b_pin = b_pin
        self.callback = callback

    def close(self):
        pass


class PWMController:
    def __init__(self, pin: int, frequency: int = 500):
        if PWMOutputDevice is None:
            raise RuntimeError("gpiozero.PWMOutputDevice required for PWM control")
        self.dev = PWMOutputDevice(pin, frequency=frequency)

    def set_duty_cycle(self, duty: float):
        # duty: 0.0-1.0
        self.dev.value = max(0.0, min(1.0, duty))

    def close(self):
        try:
            self.dev.close()
        except Exception:
            pass
