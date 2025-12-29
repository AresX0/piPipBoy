"""Environment app: sensors (BME280, GPS, RTC) stubs
"""
from __future__ import annotations

from .base import SelfUpdatingApp


class EnvironmentApp(SelfUpdatingApp):
    def __init__(self, sensors=None):
        super().__init__("Environment")
        self.sensors = sensors or {}
        self._readings = {}

    def render(self, ctx):
        if self._readings:
            t = self._readings.get('temperature')
            h = self._readings.get('humidity')
            p = self._readings.get('pressure')
            tm = self._readings.get('time')
            lines = []
            if t is not None:
                lines.append(f"T: {t:.1f} C")
            if h is not None:
                lines.append(f"H: {h:.1f} %")
            if p is not None:
                lines.append(f"P: {p:.0f} Pa")
            if tm is not None:
                lines.append(str(tm))
            y = 60
            for ln in lines:
                ctx.draw_text(10, y, ln)
                y += 20
        else:
            ctx.draw_text(10, 80, "Environment: no sensor data")

    def update(self):
        # Read sensors if present and cache values
        bme = self.sensors.get('bme280')
        if bme is not None:
            try:
                self._readings['temperature'] = bme.read_temperature()
            except Exception:
                self._readings.pop('temperature', None)
            try:
                self._readings['humidity'] = bme.read_humidity()
            except Exception:
                self._readings.pop('humidity', None)
            try:
                self._readings['pressure'] = bme.read_pressure()
            except Exception:
                self._readings.pop('pressure', None)
        rtc = self.sensors.get('rtc')
        if rtc is not None:
            try:
                self._readings['time'] = rtc.read_time()
            except Exception:
                self._readings.pop('time', None)
