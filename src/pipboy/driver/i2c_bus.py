"""
Simple I2C bus wrapper and device helpers.
Credits: adapted patterns inspired by SirLefti/piboy (MIT) — see CREDITS.md
"""
from __future__ import annotations

import logging
from typing import Optional

try:
    from smbus2 import SMBus
except Exception:  # pragma: no cover - optional dependency
    SMBus = None

logger = logging.getLogger(__name__)


class I2CBus:
    """A minimal SMBus wrapper. Use context manager or call close()."""

    def __init__(self, bus: int = 1):
        if SMBus is None:
            raise RuntimeError("smbus2 is required for I2C support")
        self.bus_no = bus
        self._bus = SMBus(bus)

    def read_i2c_block_data(self, addr, register, length):
        return self._bus.read_i2c_block_data(addr, register, length)

    def write_i2c_block_data(self, addr, register, data):
        return self._bus.write_i2c_block_data(addr, register, data)

    def close(self):
        try:
            self._bus.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


# Device helpers
class BME280Device:
    """Minimal BME280 reader using smbus2; defaults to 0x76."""

    DEFAULT_ADDRESS = 0x76

    def __init__(self, bus: I2CBus, address: int = DEFAULT_ADDRESS):
        self.bus = bus
        self.address = address

    def read_raw(self) -> bytes:
        # Minimal placeholder: real implementation should read calibration & measurement regs
        raise NotImplementedError("Direct BME280 parsing not implemented; implement as needed")

    def read_temperature(self) -> float:
        raise NotImplementedError

    def read_pressure(self) -> float:
        raise NotImplementedError

    def read_humidity(self) -> float:
        raise NotImplementedError


class DS3231RtcDevice:
    """Minimal DS3231 RTC helper. Exposes read_time/set_time hooks.
    Defaults address 0x68.
    """

    DEFAULT_ADDRESS = 0x68

    def __init__(self, bus: I2CBus, address: int = DEFAULT_ADDRESS):
        self.bus = bus
        self.address = address

    def read_time(self):
        """Return a naive datetime or None if not implemented"""
        raise NotImplementedError

    def set_time(self, dt):
        """Set RTC time from a datetime"""
        raise NotImplementedError


class OledDisplaySSD1306:
    """Minimal SSD1306 wrapper using luma.oled if available."""

    def __init__(self, i2c_address: int = 0x3C, i2c_bus: int = 1):
        try:
            from luma.core.interface.serial import i2c
            from luma.core.render import canvas
            from luma.oled.device import ssd1306
        except Exception:  # pragma: no cover - optional dependency
            raise RuntimeError("luma.oled and dependencies are required for SSD1306 support")
        self._serial = i2c(port=i2c_bus, address=i2c_address)
        self.device = ssd1306(self._serial)
        self._canvas = None

    def clear(self):
        self.device.clear()

    def text(self, x: int, y: int, text: str):
        with canvas(self.device) as draw:
            draw.text((x, y), text, fill="white")

    def image(self, pil_image):
        self.device.display(pil_image)

    def show(self):
        # With luma the display is immediate; keep method for API compatibility
        return
