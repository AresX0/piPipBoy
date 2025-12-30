import importlib
import sys
import types
import os

import importlib
from pathlib import Path

# Load the local source file directly to ensure tests exercise the working tree
root = Path(__file__).resolve().parents[1]
main_path = root / 'src' / 'pipboy' / 'main.py'
_spec = importlib.util.spec_from_file_location('pipboy.main_local', main_path)
main = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(main)


def _clear_env():
    os.environ.pop('GPIOZERO_PIN_FACTORY', None)


def test_prefers_lgpio(monkeypatch):
    # Simulate lgpio present
    sys.modules.pop('lgpio', None)
    sys.modules.pop('pigpio', None)
    sys.modules['lgpio'] = types.ModuleType('lgpio')
    _clear_env()
    # force the selection to run inside pytest
    main.choose_gpio_pin_factory(force=True)
    assert os.environ.get('GPIOZERO_PIN_FACTORY') == 'lgpio'


def test_pigpio_connected(monkeypatch):
    # Ensure lgpio absent and pigpio present with connected=True
    sys.modules.pop('lgpio', None)

    # Ensure import of lgpio fails so we exercise pigpio code even if lgpio is
    # installed on the test runner (e.g., on the Pi).
    import builtins
    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        # Block lgpio and any submodules (e.g., lgpio._lgpio) to force pigpio path
        if name == 'lgpio' or name.startswith('lgpio.'):
            raise ImportError()
        return orig_import(name, globals, locals, fromlist, level)

    builtins.__import__ = fake_import

    class MockPi:
        connected = True

    mod = types.ModuleType('pigpio')
    mod.pi = lambda: MockPi()
    sys.modules['pigpio'] = mod

    _clear_env()
    try:
        main.choose_gpio_pin_factory(force=True)
    finally:
        builtins.__import__ = orig_import

    assert os.environ.get('GPIOZERO_PIN_FACTORY') == 'pigpio'


def test_pigpio_not_connected(monkeypatch):
    sys.modules.pop('lgpio', None)

    # Ensure import of lgpio fails so we exercise pigpio code even if lgpio is
    # installed on the test runner (e.g., on the Pi).
    import builtins
    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        # Block lgpio and any submodules (e.g., lgpio._lgpio) to force pigpio path
        if name == 'lgpio' or name.startswith('lgpio.'):
            raise ImportError()
        return orig_import(name, globals, locals, fromlist, level)

    builtins.__import__ = fake_import

    class MockPi:
        connected = False

    mod = types.ModuleType('pigpio')
    mod.pi = lambda: MockPi()
    sys.modules['pigpio'] = mod

    _clear_env()
    try:
        main.choose_gpio_pin_factory(force=True)
    finally:
        builtins.__import__ = orig_import

    assert os.environ.get('GPIOZERO_PIN_FACTORY') is None


def test_pigpio_init_failure_logs(monkeypatch, capsys):
    sys.modules.pop('lgpio', None)

    # Ensure import of lgpio fails so we exercise pigpio code even if lgpio is
    # installed on the test runner (e.g., on the Pi).
    import builtins
    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        # Block lgpio and any submodules (e.g., lgpio._lgpio) to force pigpio path
        if name == 'lgpio' or name.startswith('lgpio.'):
            raise ImportError()
        return orig_import(name, globals, locals, fromlist, level)

    builtins.__import__ = fake_import

    def bad_pi():
        raise RuntimeError("mmap dma failed")

    mod = types.ModuleType('pigpio')
    mod.pi = bad_pi
    sys.modules['pigpio'] = mod

    _clear_env()
    try:
        main.choose_gpio_pin_factory(force=True)
    finally:
        builtins.__import__ = orig_import

    captured = capsys.readouterr()
    assert "failed to initialize" in captured.out or "mmap" in captured.out