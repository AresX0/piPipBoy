from __future__ import annotations

from typing import Any, Optional, Tuple


class LightsApp:
    """Controls LED patterns via HardwareController.set_led_pattern(pattern, color)"""

    name = "Lights"

    def __init__(self, controller: Any = None):
        self.controller = controller
        self._pattern = 'off'
        self._color: Optional[Tuple[int, int, int]] = None

    def render(self, ctx):
        pass

    def handle_input(self, evt):
        # Accept {'pattern': 'solid', 'color': (r,g,b)}
        if isinstance(evt, dict) and 'pattern' in evt:
            pattern = str(evt['pattern'])
            color = evt.get('color')
            self._pattern = pattern
            self._color = tuple(color) if color is not None else None
            if self.controller:
                return bool(self.controller.set_led_pattern(pattern, color))
            return True
        if evt == 'select':
            # toggle between off and solid red for quick test
            if self._pattern == 'off':
                return self.handle_input({'pattern': 'solid', 'color': (255, 0, 0)})
            return self.handle_input({'pattern': 'off'})
        return False
