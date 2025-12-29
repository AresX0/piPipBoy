# Optional Hardware Dependencies and Install Notes

This project provides optional hardware support for Raspberry Pi cases (fan,
LED strips, OLED displays, camera). These dependencies are NOT required for
running the application on non‑Pi systems and are intentionally optional so CI
and developer machines don't need Pi-only libraries.

Recommended optional packages (install only on a Pi when you need them):
- picamera2       — Preferable Pi camera API (better integration on Raspberry Pi OS)
- opencv-python   — cv2-based camera capture fallback
- rpi_ws281x      — WS281x (NeoPixel / LED strip) control
- luma.oled       — Small I2C OLED text displays
- gpiozero / RPi.GPIO — PWM and GPIO control (fan or other outputs)
- pillow          — Image support used by OLED wrappers and tests

Example install (Raspberry Pi OS):

    sudo apt-get update && sudo apt-get install -y libjpeg-dev libopenjp2-7-dev
    pip install -r requirements-hardware.txt

Notes:
- `picamera2` is distribution-specific and usually installed from Raspberry
  Pi OS packages or via pip in supported environments.
- `rpi_ws281x` may require kernel headers and C build toolchain.
- If using `opencv-python` on Pi, prefer prebuilt wheels where possible.

Using the backends
------------------
The library's `driver.backends` module attempts imports at runtime and will
return None if hardware libraries are unavailable. To instantiate real
hardware backends, call your hardware setup with `use_backends=True` on a Pi.

See `docs/FREENOVE.md` for wiring diagrams, pin mappings, and case-specific
notes.
