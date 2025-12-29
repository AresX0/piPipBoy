"""BME280 sensor stub

Provides an interface to read temperature/pressure/humidity. Degrades gracefully if hardware or library absent.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class BMEReading:
    temperature_c: float | None = None
    pressure_hpa: float | None = None
    humidity_pct: float | None = None


class BME280:
    def __init__(self, i2c=None):
        self.i2c = i2c
        self.available = False
        # In real implementation, would attempt to initialize sensor via I2C
        try:
            # placeholder for import or driver detection
            pass
        except Exception:
            self.available = False

    def read(self) -> BMEReading:
        # Return None fields if not available
        if not self.available:
            return BMEReading()
        # Placeholder for real readings
        return BMEReading(temperature_c=20.0, pressure_hpa=1013.25, humidity_pct=40.0)
