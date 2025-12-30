import builtins
import importlib
import os
import sys


def test_choose_lgpio(monkeypatch):
    # Simulate lgpio present
    monkeypatch.setitem(sys.modules, 'lgpio', object())
    monkeypatch.delenv('GPIOZERO_PIN_FACTORY', raising=False)
    # reload module to trigger selection
    import importlib
    m = importlib.reload(importlib.import_module('pipboy.driver.gpio'))
    assert os.environ.get('GPIOZERO_PIN_FACTORY') == 'lgpio'


def test_choose_pigpio_connected(monkeypatch):
    # Simulate no lgpio, pigpio present and connected
    monkeypatch.setitem(sys.modules, 'lgpio', None)

    class FakePi:
        connected = 1
        def stop(self):
            pass

    class fakepigpio:
        def pi(self):
            return FakePi()

    monkeypatch.setitem(sys.modules, 'pigpio', fakepigpio())
    monkeypatch.delenv('GPIOZERO_PIN_FACTORY', raising=False)
    import importlib
    m = importlib.reload(importlib.import_module('pipboy.driver.gpio'))
    assert os.environ.get('GPIOZERO_PIN_FACTORY') == 'pigpio'


def test_choose_none(monkeypatch):
    # Neither lgpio nor pigpio present
    monkeypatch.setitem(sys.modules, 'lgpio', None)
    monkeypatch.setitem(sys.modules, 'pigpio', None)
    monkeypatch.delenv('GPIOZERO_PIN_FACTORY', raising=False)
    import importlib
    m = importlib.reload(importlib.import_module('pipboy.driver.gpio'))
    assert os.environ.get('GPIOZERO_PIN_FACTORY') is None
