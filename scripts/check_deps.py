"""Check runtime dependencies and print actionable instructions."""
import importlib
import sys

checks = []

# tkinter
try:
    import tkinter  # type: ignore
    checks.append(("tkinter", True, ""))
except Exception:
    checks.append(("tkinter", False, "On Debian/Ubuntu: sudo apt install python3-tk. On Windows: install Python with Tk/Tcl support."))

# spidev
try:
    import spidev  # type: ignore
    checks.append(("spidev", True, ""))
except Exception:
    checks.append(("spidev", False, "spidev is usually only available on Raspberry Pi; install via pip on Pi or ensure kernel SPI is enabled."))

# gpiozero
try:
    import gpiozero  # type: ignore
    checks.append(("gpiozero", True, ""))
except Exception:
    checks.append(("gpiozero", False, "pip install gpiozero (and ensure RPi.GPIO or pigpio is available on Pi)."))

print("Dependency check:\n")
for name, ok, hint in checks:
    print(f"{name}: {'OK' if ok else 'MISSING'}")
    if not ok and hint:
        print("  ", hint)

if not all(ok for _, ok, _ in checks):
    sys.exit(2)
else:
    sys.exit(0)
