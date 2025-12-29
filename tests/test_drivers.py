import importlib
import sys


def test_spi_fallback(monkeypatch):
    # Simulate spidev missing
    monkeypatch.setitem(sys.modules, "spidev", None)
    from pipboy.driver.spi import SPI

    s = SPI()
    assert not s.available


def test_i2c_fallback(monkeypatch):
    monkeypatch.setitem(sys.modules, "smbus2", None)
    from pipboy.driver.i2c import I2C

    i2c = I2C()
    assert not i2c.available


def test_sensors_read(monkeypatch):
    from pipboy.driver.sensors.bme280 import BME280
    from pipboy.driver.sensors.ds3231 import DS3231
    from pipboy.driver.sensors.gps import GPS

    b = BME280()
    assert b.read().temperature_c is None

    r = DS3231()
    assert r.now() is None

    g = GPS()
    assert not g.read_fix().valid
