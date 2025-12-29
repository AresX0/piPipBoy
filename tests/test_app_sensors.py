from datetime import datetime

from pipboy.app.environment import EnvironmentApp
from pipboy.app.clock import ClockApp
from pipboy.app.map import MapApp


class DummyBME:
    def read_temperature(self):
        return 22.5

    def read_humidity(self):
        return 45.2

    def read_pressure(self):
        return 101325


class DummyRTC:
    def read_time(self):
        return datetime(2025, 12, 29, 12, 0, 0)


class DummyGPS:
    def last_fix(self):
        return (51.5, -0.12)


def test_environment_app_reads_sensors():
    sensors = {'bme280': DummyBME(), 'rtc': DummyRTC()}
    app = EnvironmentApp(sensors=sensors)
    app.update()
    # Ensure readings are stored
    assert 'temperature' in app._readings
    assert app._readings['temperature'] == 22.5
    assert 'time' in app._readings


def test_clock_app_reads_rtc():
    sensors = {'rtc': DummyRTC()}
    app = ClockApp(sensors=sensors)
    app.update()
    assert app._time == datetime(2025, 12, 29, 12, 0, 0)


def test_map_app_uses_gps():
    sensors = {'gps': DummyGPS()}
    app = MapApp(sensors=sensors)
    app.render(type('C', (), {'draw_text': lambda *a, **k: None}))
    assert app.center == (51.5, -0.12)
