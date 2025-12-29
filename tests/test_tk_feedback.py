from pathlib import Path
import tempfile
import yaml

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pipboy.interface.tk_interface import TkInterface


def test_tkinterface_uses_theme_feedback(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text('theme: green\nthemes:\n  green:\n    feedback_fg: "#123456"\n    feedback_duration: 2.0\n')
    tk = TkInterface(cfg)
    am = tk.app_manager
    assert am._feedback_color == "#123456"
    assert am._feedback_duration == 2.0
