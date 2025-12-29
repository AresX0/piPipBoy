"""I2C driver scaffold using smbus2

Provides a small wrapper for I2C devices and degrades gracefully if `smbus2` is not present.
"""
# Credit: small adaptation to fit piPipBoy project
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class I2CConfig:
    bus: int = 1


class I2C:
    def __init__(self, config: Optional[I2CConfig] = None):
        self.config = config or I2CConfig()
        self._bus = None
        self.available = False
        try:
            from smbus2 import SMBus

            self._bus = SMBus(self.config.bus)
            self.available = True
        except Exception:
            self._bus = None
            self.available = False

    def read_byte_data(self, addr: int, register: int) -> int:
        if not self.available or self._bus is None:
            raise RuntimeError("I2C not available")
        return self._bus.read_byte_data(addr, register)

    def close(self) -> None:
        if self._bus:
            try:
                self._bus.close()
            except Exception:
                pass
