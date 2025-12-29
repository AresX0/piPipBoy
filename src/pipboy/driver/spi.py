"""SPI driver scaffold

Provides a thin, testable wrapper around `spidev` for use with displays and other SPI devices.
Gracefully degrades if `spidev` is not available (e.g., on dev machines).
"""
# Credit: small adaptation to fit piPipBoy project
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SPIConfig:
    bus: int = 0
    device: int = 0
    max_speed_hz: int = 10_000_000


class SPI:
    def __init__(self, config: Optional[SPIConfig] = None):
        self.config = config or SPIConfig()
        self._spidev = None
        self.available = False
        try:
            import spidev

            self._spidev = spidev.SpiDev()
            self._spidev.open(self.config.bus, self.config.device)
            self._spidev.max_speed_hz = self.config.max_speed_hz
            self.available = True
        except Exception:
            # Not on a Raspberry Pi or spidev not installed — degrade gracefully
            self._spidev = None
            self.available = False

    def xfer2(self, data: bytes) -> bytes:
        if not self.available or self._spidev is None:
            raise RuntimeError("SPI not available")
        return bytes(self._spidev.xfer2(list(data)))

    def close(self) -> None:
        if self._spidev:
            try:
                self._spidev.close()
            except Exception:
                pass
