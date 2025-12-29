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

License and Attribution
- This repo includes adapted wiring notes from Freenove's case kit material.
  Follow CC BY‑NC‑SA 3.0 license for redistributed materials and include
  attribution where appropriate.
