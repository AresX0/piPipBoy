import os
import pytest


@pytest.fixture(autouse=True)
def cleanup_gpio():
    """Autouse fixture to release gpiozero pin reservations between tests.

    Some tests instantiate gpiozero devices and may not always close them; this
    fixture attempts to clear internal reservations after each test to avoid
    pin-in-use errors when running the full suite on real hardware.
    """
    yield
    try:
        from gpiozero import Device
        pf = Device.pin_factory
        # Best-effort: clear internal reservations if present
        if hasattr(pf, "_reservations"):
            pf._reservations.clear()
    except Exception:
        # Don't make tests fail due to cleanup issues
        pass
