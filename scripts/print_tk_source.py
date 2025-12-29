import sys
from pathlib import Path
# Ensure src is importable when run directly
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

import inspect
from pipboy.interface.tk_interface import TkInterface
print(inspect.getsource(TkInterface))
