import os
import pytest


@pytest.fixture(autouse=True)
def _lgpio_present():
    import importlib, sys
    try:
        spec = importlib.util.find_spec('lgpio')
        return spec is not None or 'lgpio' in sys.modules
    except Exception:
        return 'lgpio' in sys.modules


def pytest_runtest_setup(item):
    # Skip freenove/hardware-interacting tests unless explicitly enabled.
    # This avoids accidentally claiming pins on CI or on developer machines where
    # the environment isn't set up for hardware testing.
    if 'freenove' in item.nodeid:
        import pytest
        val = os.environ.get('RUN_PI_HARDWARE_TESTS')
        if not val or val in ("0", "false", "False"):
            pytest.skip('RUN_PI_HARDWARE_TESTS is not set; skipping freenove hardware tests')

    # Additionally, skip when lgpio is present since it may claim pins even when
    # RUN_PI_HARDWARE_TESTS isn't set or when the runner is a Pi used for other
    # development tasks.
    if 'freenove' in item.nodeid and _lgpio_present():
        import pytest

        pytest.skip('lgpio present on runner; skipping freenove hardware-free tests')


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
        val = os.environ.get('RUN_PI_HARDWARE_TESTS')
        # Treat unset, empty, '0', or 'false' as disabled; anything else enables
        if not val or val in ("0", "false", "False"):
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
