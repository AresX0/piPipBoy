"""Clock app
"""
from __future__ import annotations

import time
from .base import SelfUpdatingApp


class ClockApp(SelfUpdatingApp):
    def __init__(self, sensors=None):
        super().__init__("Clock")
        self.sensors = sensors or {}
        self._time = None

    def render(self, ctx):
        if self._time is not None:
            ctx.draw_text(10, 80, str(self._time))
        else:
            ctx.draw_text(10, 80, time.strftime("%Y-%m-%d %H:%M:%S"))

    def needs_update(self):
        return True

    def update(self):
        rtc = self.sensors.get('rtc')
        if rtc is not None:
            try:
                self._time = rtc.read_time()
            except Exception:
                self._time = None
        else:
            self._time = None
