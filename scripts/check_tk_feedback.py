import tempfile
from pathlib import Path
import yaml

# create a temp config file
cfg = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
cfg_path = Path(cfg.name)
cfg.write(b'theme: green\nthemes:\n  green:\n    feedback_fg: "#123456"\n    feedback_duration: 2.0\n')
cfg.close()

from pipboy.interface.tk_interface import TkInterface

try:
    tk = TkInterface(cfg_path)
    print('loaded config=', getattr(tk, 'config', None))
    am = tk.app_manager
    print('feedback_color=', am._feedback_color)
    print('feedback_duration=', am._feedback_duration)
finally:
    cfg_path.unlink()
