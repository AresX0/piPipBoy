"""CI-friendly dependency checker.
Runs the same checks as `check_deps.py` but treats missing optional deps as warnings by default.
"""
import argparse
import sys


def main(warn_only: bool = True) -> int:
    checks = []

    try:
        import tkinter  # type: ignore
        checks.append(("tkinter", True, ""))
    except Exception:
        checks.append(("tkinter", False, "On Debian/Ubuntu: sudo apt install python3-tk. On Windows: install Python with Tk/Tcl support."))

    try:
        import spidev  # type: ignore
        checks.append(("spidev", True, ""))
    except Exception:
        checks.append(("spidev", False, "spidev is usually only available on Raspberry Pi; install via pip on Pi or ensure kernel SPI is enabled."))

    try:
        import gpiozero  # type: ignore
        checks.append(("gpiozero", True, ""))
    except Exception:
        checks.append(("gpiozero", False, "pip install gpiozero (and ensure RPi.GPIO or pigpio is available on Pi)."))

    print("CI Dependency check:\n")
    for name, ok, hint in checks:
        print(f"{name}: {'OK' if ok else 'MISSING'}")
        if not ok and hint:
            print("  ", hint)

    missing = [name for name, ok, _ in checks if not ok]
    if missing and not warn_only:
        print("Missing required dependencies:", ", ".join(missing))
        return 2
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--warn-only', action='store_true', default=True, help='Treat missing deps as warnings (default True for CI)')
    args = parser.parse_args()
    rc = main(warn_only=args.warn_only)
    sys.exit(rc)
