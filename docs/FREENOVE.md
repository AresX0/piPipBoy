Freenove Computer Case (FNK0100) — Integration notes

This document describes the wiring and configuration used to run piPipBoy with
Freenove's "Computer Case Kit for Raspberry Pi" (FNK0100 series).

License & attribution
- The Freenove tutorial and diagrams are licensed CC BY-NC-SA 3.0. You may
  reference and re-implement wiring based on those materials, but do not reuse
  Freenove code for commercial use. Keep attribution when adapting diagrams or
  verbatim content from Freenove's materials.

Default pin mapping (BCM)
- Display (SPI): bus 0, device 0
  - DC: GPIO 24
  - RESET: GPIO 25
- Input buttons / encoder
  - up: GPIO 5
  - down: GPIO 6
  - left: GPIO 16
  - right: GPIO 20
  - select: GPIO 13
  - back: GPIO 19
  - rotary A: GPIO 17
  - rotary B: GPIO 27
  - rotary switch: GPIO 22

Using the Freenove profile
- In `src/pipboy/config.yaml` a `hardware_profiles.freenove` section exists with
  the defaults above. To start the app with these settings, run in dev mode:

    python -m pipboy --profile freenove

Or set values in `config.yaml` or environment variables as appropriate for your
deployment.

Notes
- These mappings correspond to the Freenove case wiring recommended in their
  tutorial; if your kit revision differs, adjust `config.yaml` accordingly.
