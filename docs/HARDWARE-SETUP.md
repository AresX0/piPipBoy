Hardware setup (Raspberry Pi)

Quick steps to enable I2C/SPI/UART and install recommended packages on Raspberry Pi 4/5:

- Enable interfaces (if using raspi-config or the equivalent on your OS):
  - sudo raspi-config -> Interface Options -> enable I2C, SPI, Serial (UART)
- Install LGPIO (recommended):
  - sudo apt-get update
  - sudo apt-get install -y python3-lgpio liblgpio1 liblgpio-dev swig libcap-dev
  - (Optional) In your venv: pip install lgpio  # requires liblgpio-dev & swig to build
  - If pip build fails, make system site-packages available to the venv by adding a .pth file pointing to /usr/lib/python3/dist-packages
- Set gpiozero to prefer lgpio in environments that support it:
  - export GPIOZERO_PIN_FACTORY=lgpio
- Note about pigpio on Raspberry Pi 5:
  - The pigpiod daemon may fail to initialise on Pi 5 with a DMA mmap error ("initPeripherals: mmap dma failed (Invalid argument)"). If you require pigpio, investigate kernel/IOMMU/CMA settings or contact the pigpio maintainers. Using lgpio is a stable alternative.

Test the environment:
- In the project venv: python -c "from gpiozero import devices; print(devices.pin_factory)"  # should indicate lgpio if configured
- Run the hardware tests: RUN_PI_HARDWARE_TESTS=1 pytest tests/test_freenove_driver.py

If you want me to automatically apply these steps on the Pi or open a PR with these docs and code changes here, say "Do it".