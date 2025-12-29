"""Environment app: sensors (BME280, GPS, RTC) stubs
"""
from __future__ import annotations

from .base import SelfUpdatingApp


class EnvironmentApp(SelfUpdatingApp):
    def __init__(self, sensors=None):
        super().__init__("Environment")
        self.sensors = sensors or {}

    def render(self, ctx):
        ctx.draw_text(10, 80, "Environment: sensors")

    def update(self):
        # Read sensors if present
        pass
