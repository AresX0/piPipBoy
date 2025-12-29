FREENOVE Wiring Diagrams (Supplement)

This file supplements `docs/FREENOVE.md` with simple ASCII circuit diagrams and
pin mapping notes for quick reference.

ASCII Diagram (conceptual)

      +5V ---+----------------+--------- LED V+
            |                |
           Fan             [WS281x]
            |                |
           GND--------------+--------- LED GND

      Pi GPIO18 ---[Level Shifter]--- LED Data

      Pi 3.3V --- OLED VCC
      Pi GND  --- OLED GND
      Pi SDA  --- OLED SDA (GPIO2)
      Pi SCL  --- OLED SCL (GPIO3)

Pin Notes
- LED Data: GPIO18 (commonly used by rpi_ws281x)
- Use level shifter for WS281x when necessary to ensure 5V data logic
- Fan: use MOSFET/transistor for switching if fan draws > GPIO ratings

Pi 5 / Notes for Raspberry Pi 5 ⚠️
- Install runtime packages on the Pi: `sudo apt-get install python3-lgpio liblgpio1 liblgpio-dev swig libcap-dev`.
- In the project virtualenv you can `pip install lgpio` (requires `liblgpio-dev` and `swig`) or make the system `dist-packages` visible to the venv (e.g., add `/usr/lib/python3/dist-packages` to a `.pth` file in the venv site-packages).
- To prefer the lgpio backend for gpiozero, set `GPIOZERO_PIN_FACTORY=lgpio` (or configure pin factory in code) — this avoids relying on pigpio or RPi.GPIO on Pi 5.
- Known issue: `pigpiod` may fail to initialise on Pi 5 with `initPeripherals: mmap dma failed (Invalid argument)`. If you need `pigpio`, investigate kernel/IOMMU/CMA settings or use `lgpio` as a working alternative.

License and Attribution
- This repo includes adapted wiring notes from Freenove's case kit material.
  Follow CC BY‑NC‑SA 3.0 license for redistributed materials and include
  attribution where appropriate.
