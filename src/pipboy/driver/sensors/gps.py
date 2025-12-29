"""GPS stub (serial-based)

Provides a small interface for GPS NMEA parsing and availability detection.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class GPSFix:
    lat: float | None = None
    lon: float | None = None
    valid: bool = False


class GPS:
    def __init__(self, port: str = "/dev/serial0", baud: int = 9600):
        self.port = port
        self.baud = baud
        self.available = False
        try:
            # In real code, attempt to open serial.Serial
            pass
        except Exception:
            self.available = False

    def read_fix(self) -> GPSFix:
        if not self.available:
            return GPSFix()
        # Placeholder: return dummy fix
        return GPSFix(lat=0.0, lon=0.0, valid=True)
