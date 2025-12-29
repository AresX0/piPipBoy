"""
SPI bus wrapper and simple ILI9486 display stub.
Credits: adapted from common SPI display patterns and SirLefti/piboy (MIT)
"""
from __future__ import annotations

import logging

try:
    import spidev
except Exception:  # pragma: no cover - optional
    spidev = None

logger = logging.getLogger(__name__)


class SPIBus:
    def __init__(self, bus: int = 0, device: int = 0, max_speed_hz: int = 16000000):
        if spidev is None:
            raise RuntimeError("spidev is required for SPI support")
        self.bus_no = bus
        self.device = device
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = max_speed_hz

    def xfer2(self, data):
        return self.spi.xfer2(data)

    def close(self):
        try:
            self.spi.close()
        except Exception:
            pass


class ILI9486Display:
    """Stubbed ILI9486 SPI display. Implement init/draw_image/fill as needed."""

    def __init__(self, spi: SPIBus, dc_pin=None, reset_pin=None, cs_pin=None):
        self.spi = spi
        self.dc_pin = dc_pin
        self.reset_pin = reset_pin
        self.cs_pin = cs_pin
        self.initialized = False

    def init(self):
        # Initialize display. This is hardware-specific and requires command sequences.
        self.initialized = True

    def draw_image(self, pil_image):
        if not self.initialized:
            raise RuntimeError("Display not initialized")
        # Convert PIL to raw bytes and send via SPI (implementation omitted)
        raise NotImplementedError("draw_image must be implemented for your panel")

    def fill(self, color):
        if not self.initialized:
            raise RuntimeError("Display not initialized")
        # Fill screen with a color (implementation omitted)
        raise NotImplementedError
