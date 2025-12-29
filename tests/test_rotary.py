import time

from pipboy.interface.gpio_input import RotaryEncoder


def test_rotary_simulate_turns(monkeypatch):
    r = RotaryEncoder(17, 27)
    seen = []
    r.on_turn(lambda d: seen.append(d))
    # simulate with small time gaps so they are accepted
    import time as _time
    t0 = _time.monotonic()
    # monkeypatch time.monotonic to advance slightly between steps
    calls = [t0, t0 + 0.02, t0 + 0.04]
    idx = {"i": 0}

    def fake_time():
        v = calls[idx["i"]]
        idx["i"] = min(idx["i"] + 1, len(calls) - 1)
        return v

    monkeypatch.setattr("time.monotonic", fake_time)

    r.simulate_step(1, steps=2)
    r.simulate_step(-1, steps=1)
    # We expect at least 2 cw and 1 ccw events
    assert sum(1 for s in seen if s > 0) >= 2
    assert sum(1 for s in seen if s < 0) >= 1


def test_rotary_debounce(monkeypatch):
    # Control time.monotonic to simulate quick events
    t = [0.0]

    def fake_time():
        return t[0]

    monkeypatch.setattr("time.monotonic", fake_time)
    r = RotaryEncoder(17, 27, debounce=0.05)
    seen = []
    r.on_turn(lambda d: seen.append(d))
    # First step at t=0
    r.simulate_step(1, steps=1)
    assert len(seen) == 1
    # Advance time less than debounce and simulate -> should be ignored
    t[0] += 0.01
    r.simulate_step(1, steps=1)
    assert len(seen) == 1
    # Advance beyond debounce -> accepted
    t[0] += 0.1
    r.simulate_step(1, steps=1)
    assert len(seen) >= 2
