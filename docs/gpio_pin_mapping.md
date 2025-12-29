GPIO pin mapping and recommended wiring

This document provides recommended GPIO pins for common Pip‑Boy controls and example `config.yaml` stubs.

Recommended mappings (BCM numbering):
- Up: GPIO 5
- Down: GPIO 6
- Left: GPIO 16
- Right: GPIO 20
- Select: GPIO 13
- Back: GPIO 19
- Rotary encoder A: GPIO 17
- Rotary encoder B: GPIO 27
- Rotary encoder switch: GPIO 22

Example `config.yaml` snippet for input mapping:

input:
  type: gpio
  mapping:
    up: 5
    down: 6
    left: 16
    right: 20
    select: 13
    back: 19
    rotary_a: 17
    rotary_b: 27
    rotary_sw: 22

Notes
- Use `gpiozero.Button(pin)` or `RPi.GPIO` to read buttons reliably. Consider hardware debouncing or software debouncing in `gpio_input.py`.
- The default mapping above is a suggestion; please adapt to your hardware layout.
