"""Scaffold driver for ILI9486-like SPI displays

This is a lightweight scaffold with clear hooks for SPI initialization and rendering.
"""
# Credit: portions derived from SirLefti/piboy (MIT) — https://github.com/SirLefti/piboy

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ILI9486Config:
    spi_bus: int = 0
    spi_device: int = 0
    dc_pin: int = 24
    reset_pin: int = 25
    width: int = 480
    height: int = 320


class ILI9486Display:
    def __init__(self, config: ILI9486Config | None = None, spi=None):
        self.config = config or ILI9486Config()
        # Optionally accept an SPI wrapper object
        self.spi = spi
        self.initialized = False

    def initialize(self) -> None:
        # Set up SPI, reset pins, etc.
        self.initialized = True
        # Framebuffer for testable rendering
        self._framebuffer = []

    def clear(self) -> None:
        # Clear buffer / screen
        self._framebuffer = []

    def draw_text(self, x: int, y: int, text: str, color: str = "#99ff66") -> None:
        # Convert text to framebuffer operations
        # For testability, we append text ops to an internal framebuffer list
        if not hasattr(self, "_framebuffer"):
            self._framebuffer = []
        self._framebuffer.append({"type": "text", "x": x, "y": y, "text": text, "color": color})

    def _flush_to_spi(self):
        # Simple placeholder flush: convert text ops to bytes and send via SPI.xfer2
        if not self.spi or not getattr(self.spi, "available", False):
            return
        try:
            for op in getattr(self, "_framebuffer", []):
                if op.get("type") == "text":
                    payload = op.get("text", "").encode("utf-8", errors="replace")
                    # send in chunks to SPI
                    for i in range(0, len(payload), 64):
                        chunk = payload[i : i + 64]
                        # In a real driver we'd send commands/data; use xfer2 for bulk bytes
                        self.spi.xfer2(bytes(chunk))
        except Exception:
            # Don't crash on SPI errors — degrade gracefully
            pass

    def update(self) -> None:
        # Flush framebuffer to display - in real driver this would write to SPI
        # For testing, we just keep last_frame and optionally flush to SPI
        self.last_frame = list(getattr(self, "_framebuffer", []))
        self._flush_to_spi()

    def get_last_frame(self):
        return getattr(self, "last_frame", [])
