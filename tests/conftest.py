import os
import pytest


@pytest.fixture(autouse=True)
def cleanup_gpio():
    """Autouse fixture to release gpiozero pin reservations before and after tests.

    Some tests instantiate gpiozero devices and may not always close them; this
    fixture attempts to clear internal reservations before each test starts and
    again after the test finishes to avoid pin-in-use errors when running the
    full suite on real hardware.
    """
    # Clear before test starts (best-effort)
    try:
        from gpiozero import Device
        pf = Device.pin_factory
        if hasattr(pf, "_reservations"):
            pf._reservations.clear()
    except Exception:
        pass

    yield

    # Clear after test completes (best-effort)
    try:
        from gpiozero import Device
        pf = Device.pin_factory
        if hasattr(pf, "_reservations"):
            pf._reservations.clear()
    except Exception:
        # Don't make tests fail due to cleanup issues
        pass
