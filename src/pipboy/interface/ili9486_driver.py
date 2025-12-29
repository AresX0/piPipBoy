"""ILI9486 driver: command/data protocol and simple RGB565 framebuffer

This driver implements minimal ILI9486 commands to initialize the display and write pixel data
in RGB565 format via SPI. It is intentionally small and testable — SPI operations are performed
through an injected `spi` object exposing `xfer2(bytes)`.

References: ILI9486 datasheet (command set). This is not an exhaustive implementation; it provides
basic init, set window, fill rectangle, and draw_rgb565_buffer operations useful for our UI.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass
class ILIConfig:
    width: int = 480
    height: int = 320
    rotation: int = 0


class ILI9486:
    CMD_SWRESET = 0x01
    CMD_SLPOUT = 0x11
    CMD_COLMOD = 0x3A
    CMD_MADCTL = 0x36
    CMD_CASET = 0x2A
    CMD_RASET = 0x2B
    CMD_RAMWR = 0x2C
    CMD_DISPON = 0x29

    def __init__(self, spi, dc_pin=None, reset_pin=None, config: Optional[ILIConfig] = None):
        """spi: object with xfer2(bytes) -> bytes and attribute `available`"""
        self.spi = spi
        self.dc = dc_pin
        self.reset = reset_pin
        self.config = config or ILIConfig()
        self.initialized = False

    # Low-level helpers
    def _write_cmd(self, cmd: int) -> None:
        # DC low
        self._set_dc(False)
        self._spi_xfer(bytes([cmd]))

    def _write_data(self, data: bytes) -> None:
        # DC high
        self._set_dc(True)
        # Chunk data into reasonable sizes
        for i in range(0, len(data), 4096):
            chunk = data[i : i + 4096]
            self._spi_xfer(bytes(chunk))

    def _spi_xfer(self, b: bytes) -> None:
        if not getattr(self.spi, "available", False):
            raise RuntimeError("SPI not available")
        # xfer2 returns bytes; we ignore return value
        self.spi.xfer2(b)

    def _set_dc(self, high: bool) -> None:
        # If a real GPIO pin is provided, we'd toggle it; in tests we ignore it
        pass

    def reset_display(self) -> None:
        # Toggle reset pin if provided
        pass

    # High-level operations
    def initialize(self) -> None:
        # A minimal initialization sequence
        self._write_cmd(self.CMD_SWRESET)
        # delay typically needed, omitted in tests
        self._write_cmd(self.CMD_SLPOUT)
        # Set color mode: 16-bit/pixel
        self._write_cmd(self.CMD_COLMOD)
        self._write_data(bytes([0x55]))  # 16-bit
        # Memory access control (orientation)
        self._write_cmd(self.CMD_MADCTL)
        self._write_data(bytes([0x48]))
        self._write_cmd(self.CMD_DISPON)
        self.initialized = True

    def set_window(self, x0: int, y0: int, x1: int, y1: int) -> None:
        # Column address set
        self._write_cmd(self.CMD_CASET)
        data = x0.to_bytes(2, "big") + x1.to_bytes(2, "big")
        self._write_data(data)
        # Row address set
        self._write_cmd(self.CMD_RASET)
        data = y0.to_bytes(2, "big") + y1.to_bytes(2, "big")
        self._write_data(data)

    def write_pixels_rgb565(self, pixels: Sequence[int], width: int, height: int) -> None:
        """Write a buffer of RGB565 pixel values to the current window.
        pixels: iterable of 16-bit integers in 0xRRGG format (RGB565)
        """
        # Convert to bytes big-endian
        b = bytearray()
        for p in pixels:
            b += p.to_bytes(2, "big")
        self._write_cmd(self.CMD_RAMWR)
        self._write_data(bytes(b))

    def fill_rect(self, x: int, y: int, w: int, h: int, color_rgb565: int) -> None:
        x0, y0, x1, y1 = x, y, x + w - 1, y + h - 1
        self.set_window(x0, y0, x1, y1)
        n = w * h
        # Prepare repeated color bytes
        c = color_rgb565.to_bytes(2, "big")
        # Send in chunks
        chunk = c * min(1024, n)
        self._write_cmd(self.CMD_RAMWR)
        remaining = n
        while remaining > 0:
            to_send = min(remaining, len(chunk) // 2)
            self._write_data(chunk[: to_send * 2])
            remaining -= to_send
