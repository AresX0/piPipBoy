import time

from pipboy.interface.gpio_input import RotaryEncoder


def test_rotary_push_short_and_long(monkeypatch):
    t = [0.0]

    def fake_time():
        return t[0]

    monkeypatch.setattr("time.monotonic", fake_time)

    r = RotaryEncoder(17, 27)
    short = []
    longp = []
    r.on_push(lambda: short.append(True))
    r.on_push_long(lambda: longp.append(True))

    # simulate short press
    r.push_down()
    t[0] += 0.1
    r.push_up()
    assert len(short) == 1 and len(longp) == 0

    # simulate long press
    r.push_down()
    t[0] += 1.0
    r.push_up()
    assert len(longp) == 1
