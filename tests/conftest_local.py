import os
import pytest


@pytest.fixture(autouse=True)
def mock_gpio_pin_factory():
    """When not running hardware tests on the Pi, replace gpiozero's pin factory
    with a MockFactory to prevent tests from claiming real GPIO.

    This fixture is intentionally conservative: it only swaps the factory when
    RUN_PI_HARDWARE_TESTS is not set. It also attempts best-effort cleanup after
    each test.
    """
    old_factory = None
    try:
        if not os.environ.get('RUN_PI_HARDWARE_TESTS'):
            try:
                from gpiozero import Device
                from gpiozero.pins.mock import MockFactory
                old_factory = Device.pin_factory
                Device.pin_factory = MockFactory()
            except Exception:
                old_factory = None
    except Exception:
        old_factory = None

    yield

    try:
        from gpiozero import Device
        if old_factory is not None:
            Device.pin_factory = old_factory
        pf = Device.pin_factory
        if hasattr(pf, "_reservations"):
            pf._reservations.clear()
    except Exception:
        pass
