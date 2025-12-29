import types
import pytest

from pipboy.interface.gpio_input import GPIOInput, KeyboardInput


def test_keyboard_input_simulate():
    k = KeyboardInput()
    called = {}

    def foo():
        called['x'] = True

    k.on('test', foo)
    k.simulate('test')
    assert called.get('x') is True


def test_gpio_input_close_no_gpio(monkeypatch):
    # Simulate environment without gpiozero (Button=None)
    monkeypatch.setattr('pipboy.interface.gpio_input.Button', None)
    g = GPIOInput(mapping=None)
    # Should not raise
    g.close()


def test_gpio_input_closes_buttons(monkeypatch):
    # Create a dummy Button type that tracks close() calls
    class DummyBtn:
        def __init__(self, pin, **kwargs):
            self.pin = pin
            self.closed = False
            self.when_pressed = None

        def close(self):
            self.closed = True

    monkeypatch.setattr('pipboy.interface.gpio_input.Button', DummyBtn)
    g = GPIOInput(mapping={'up': 5, 'down': 6, 'select': 13})
    # Ensure buttons created
    assert 'up' in g.buttons
    g.close()
    for b in g.buttons.values():
        assert b.closed is True
