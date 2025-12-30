import pytest
import os

if not os.environ.get('RUN_PI_HARDWARE_TESTS') or os.environ.get('RUN_PI_HARDWARE_TESTS') in ("0", "false", "False"):
    pytest.skip('RUN_PI_HARDWARE_TESTS not set; skipping freenove tests', allow_module_level=True)

from pipboy.driver.freenove_case import FreenoveConfig, FreenoveCase


def test_freenove_config_defaults():
    cfg = FreenoveConfig()
    assert cfg.input_mapping["up"] == 5
    assert cfg.input_mapping["rotary_a"] == 17


def test_create_display_and_inputs():
    cfg = FreenoveConfig()
    case = FreenoveCase(cfg=cfg)
    disp = case.create_display()
    inputs = case.create_inputs()
    assert disp is not None
    assert inputs is not None
    # Input mapping should pass through
    assert hasattr(inputs, 'on')


def test_create_hardware_interface(monkeypatch):
    # Verify create_hardware wires without real gpio or spi present
    class DummyApp:
        def handle_input(self, name):
            # no-op for tests
            pass

    dummy = DummyApp()
    from pipboy.driver.freenove_case import create_hardware

    hw = create_hardware(dummy)
    # initialize should not raise
    hw.initialize()
    # run_once should render without raising
    hw.run_once()
