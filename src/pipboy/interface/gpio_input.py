"""GPIO / input abstraction

Provides a GPIOInput class for Raspberry Pi and a KeyboardInput fallback for dev.
Includes RotaryEncoder support with software debouncing and simulation hooks for tests.
"""
from __future__ import annotations

import time
from typing import Callable, Optional

try:
    from gpiozero import Button
    from gpiozero import RotaryEncoder as GPIOZeroRotary
except Exception:
    Button = None  # type: ignore
    GPIOZeroRotary = None  # type: ignore


class GPIOInput:
    def close(self):
        try:
            for b in getattr(self, 'buttons', {}).values():
                try:
                    b.close()
                except Exception:
                    pass
            self.buttons = {}
        except Exception:
            pass

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def __init__(self, mapping: dict | None = None, debounce: float = 0.01):
        self.mapping = mapping or {"up": 5, "down": 6, "select": 13}
        self.handlers: dict[str, Callable[[], None]] = {}
        self.debounce = debounce
        self._rotary: Optional[RotaryEncoder] = None
        self._setup()

    def _setup(self):
        # Buttons
        if Button is None:
            # On systems without gpiozero, we won't create real Button objects
            self.buttons = {}
        else:
            self.buttons = {name: Button(pin) for name, pin in self.mapping.items() if name in ("up", "down", "select", "back") and pin is not None}
            for name, btn in self.buttons.items():
                btn.when_pressed = lambda n=name: self._invoke(n)

        # Rotary encoder setup (mapping keys: rotary_a, rotary_b, rotary_sw)
        a = self.mapping.get("rotary_a")
        b = self.mapping.get("rotary_b")
        sw = self.mapping.get("rotary_sw")
        if GPIOZeroRotary is not None and a is not None and b is not None:
            # Use gpiozero's Rotary if available
            try:
                r = GPIOZeroRotary(a, b)
                r.when_rotated = self._handle_rotary_gpiozero
                if sw is not None and Button is not None:
                    s = Button(sw)
                    s.when_pressed = lambda: self._rotary and self._rotary.push_down()
                    s.when_released = lambda: self._rotary and self._rotary.push_up()
                self._rotary = RotaryEncoder.from_gpiozero(r)
            except Exception:
                self._rotary = RotaryEncoder(a, b, sw, debounce=self.debounce)
        elif a is not None and b is not None:
            self._rotary = RotaryEncoder(a, b, sw, debounce=self.debounce)
            if sw is not None and Button is not None:
                s = Button(sw)
                s.when_pressed = lambda: self._rotary.push_down()
                s.when_released = lambda: self._rotary.push_up()

    def _handle_rotary_gpiozero(self, direction: int):
        # gpiozero's when_rotated supplies direction: 1 or -1
        if direction > 0:
            self._invoke("rot_right")
        else:
            self._invoke("rot_left")

    def _invoke(self, name: str):
        h = self.handlers.get(name)
        if h:
            h()

    def on(self, name: str, handler: Callable[[], None]):
        self.handlers[name] = handler


class RotaryEncoder:
    """Software rotary encoder that can be driven by GPIO edges or simulated in tests.

    It decodes quadrature (A/B) edges. Call `process(a_state, b_state)` on each edge, or use
    `simulate_step(direction, steps=1)` in tests to emit logical steps. Debounces events
    by ignoring steps that occur within `debounce` seconds.
    """

    def __init__(self, pin_a: int, pin_b: int, pin_sw: int | None = None, debounce: float = 0.01):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.pin_sw = pin_sw
        self.debounce = debounce
        # initialize last_time to a very negative value so first event is always accepted
        self._last_time = -9e9
        self._state = 0  # combined state (A<<1 | B)
        self._on_turn: Optional[Callable[[int], None]] = None
        self._on_push: Optional[Callable[[], None]] = None

    @classmethod
    def from_gpiozero(cls, gz_rotary):
        # Wrap a gpiozero Rotary instance so we can still simulate in tests
        inst = cls(0, 0)
        inst._gz = gz_rotary
        return inst

    def on_turn(self, handler: Callable[[int], None]):
        self._on_turn = handler

    def on_push(self, handler: Callable[[], None]):
        self._on_push = handler

    def on_push_long(self, handler: Callable[[], None]):
        self._on_push_long = handler

    def process(self, a: int, b: int):
        """Process an edge by reading current A/B levels (0/1)."""
        now = time.monotonic()
        # Simple debounce: ignore if too soon after last
        if now - self._last_time < self.debounce:
            return
        new_state = (a << 1) | b
        delta = 0
        # Determine direction using typical quadrature state transitions
        # this simplistic approach interprets a rising edge on A
        if self._state == 0 and new_state == 1:
            delta = 1
        elif self._state == 1 and new_state == 3:
            delta = 1
        elif self._state == 3 and new_state == 2:
            delta = 1
        elif self._state == 2 and new_state == 0:
            delta = 1
        elif self._state == 0 and new_state == 2:
            delta = -1
        elif self._state == 2 and new_state == 3:
            delta = -1
        elif self._state == 3 and new_state == 1:
            delta = -1
        elif self._state == 1 and new_state == 0:
            delta = -1
        self._state = new_state
        if delta != 0:
            self._last_time = now
            if self._on_turn:
                self._on_turn(delta)

    def push_down(self):
        # Record push start time
        self._push_start = time.monotonic()

    def push_up(self):
        # Determine if short or long press
        dur = time.monotonic() - getattr(self, "_push_start", 0)
        if dur >= getattr(self, "_long_press_threshold", 0.5):
            if getattr(self, "_on_push_long", None):
                self._on_push_long()
        else:
            if self._on_push:
                self._on_push()

    # Test helper
    def simulate_step(self, direction: int, steps: int = 1):
        """Simulate turning the encoder. direction=1 for CW, -1 for CCW.

        This helper bypasses the need for real GPIO events and triggers the
        `on_turn` handler while respecting debounce timing.
        """
        for _ in range(steps):
            now = time.monotonic()
            if now - self._last_time < self.debounce:
                # ignore this simulated step due to debounce
                continue
            self._last_time = now
            if self._on_turn:
                self._on_turn(direction)

    # Test helper
    def simulate_step(self, direction: int, steps: int = 1):
        """Simulate turning the encoder. direction=1 for CW, -1 for CCW.

        This helper bypasses the need for real GPIO events and triggers the
        `on_turn` handler while respecting debounce timing.
        """
        for _ in range(steps):
            now = time.monotonic()
            if now - self._last_time < self.debounce:
                # ignore this simulated step due to debounce
                continue
            self._last_time = now
            if self._on_turn:
                self._on_turn(direction)


class KeyboardInput:
    """Simple keyboard fallback used in dev mode"""

    def __init__(self):
        self.handlers = {}

    def on(self, name: str, handler: Callable[[], None]):
        self.handlers[name] = handler

    def simulate(self, name: str):
        # Call the registered handler once for the given input name
        if name in self.handlers:
            self.handlers[name]()
        # Support explicit short/long rotary push simulation
        if name == "rot_push_short" and "rot_push_short" in self.handlers:
            self.handlers["rot_push_short"]()
        if name == "rot_push_long" and "rot_push_long" in self.handlers:
            self.handlers["rot_push_long"]()
