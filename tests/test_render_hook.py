class DummyCtx:
    def __init__(self):
        self.drawn = []

    def draw_text(self, x, y, text, fg=None):
        self.drawn.append((x, y, text, fg))


def test_clock_renders(monkeypatch):
    from pipboy.app.clock import ClockApp

    ctx = DummyCtx()
    c = ClockApp()
    c.render(ctx)
    assert len(ctx.drawn) == 1
