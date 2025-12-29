"""Run the dev Tk UI with helpful diagnostics when dependencies are missing."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

try:
    from pipboy.interface.tk_interface import TkInterface
    from pipboy.main import CONFIG_PATH
    tk = TkInterface(CONFIG_PATH)
    tk.run()
except ModuleNotFoundError as e:
    print("Module not found:", e)
    print("Make sure the virtualenv is active and that dependencies are installed.")
    print("On Debian/Ubuntu, install runtime deps with: sudo apt install python3-tk && pip install -r requirements-pi.txt")
    sys.exit(2)
except Exception as e:
    # Common issue: tkinter missing or TclError
    print("Failed to start Tk UI:", e)
    print("If this is a headless environment, install tkinter with: sudo apt install python3-tk")
    sys.exit(3)
