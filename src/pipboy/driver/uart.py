"""
UART wrapper and Neo6m GPS reader using pyserial and pynmea2.
"""
from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Optional

try:
    import serial
except Exception:  # pragma: no cover - optional
    serial = None

try:
    import pynmea2
except Exception:
    pynmea2 = None

logger = logging.getLogger(__name__)


class UART:
    def __init__(self, port: str = "/dev/serial0", baud: int = 9600, timeout: float = 1.0):
        if serial is None:
            raise RuntimeError("pyserial is required for UART support")
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self._ser = serial.Serial(port, baudrate=baud, timeout=timeout)

    def write(self, data: bytes):
        self._ser.write(data)

    def read_line(self) -> Optional[bytes]:
        return self._ser.readline()

    def close(self):
        try:
            self._ser.close()
        except Exception:
            pass


class Neo6mGps:
    """Background NMEA reader. get_latest_fix() returns dict or None."""

    def __init__(self, uart: UART, maxlen: int = 16):
        if pynmea2 is None:
            raise RuntimeError("pynmea2 is required for GPS parsing")
        self.uart = uart
        self._runs = True
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._lock = threading.Lock()
        self._fixes = deque(maxlen=maxlen)
        self._thread.start()

    def _reader(self):
        while self._runs:
            try:
                line = self.uart.read_line()
                if not line:
                    time.sleep(0.1)
                    continue
                try:
                    msg = pynmea2.parse(line.decode('ascii', errors='ignore'))
                except Exception:
                    continue
                if hasattr(msg, 'latitude'):
                    with self._lock:
                        self._fixes.append({'lat': msg.latitude, 'lon': msg.longitude, 'timestamp': getattr(msg, 'timestamp', None)})
            except Exception:
                time.sleep(0.2)

    def get_latest_fix(self):
        with self._lock:
            if not self._fixes:
                return None
            return dict(self._fixes[-1])

    def close(self):
        self._runs = False
        self._thread.join(timeout=1.0)
        try:
            self.uart.close()
        except Exception:
            pass
