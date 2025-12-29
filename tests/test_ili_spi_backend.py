class FakeSPI:
    def __init__(self):
        self.available = True
        self.sent = []

    def xfer2(self, b: bytes):
        self.sent.append(bytes(b))
        return b


def test_ili_flushes_to_spi():
    from pipboy.interface.ili9486_display import ILI9486Display

    spi = FakeSPI()
    d = ILI9486Display(spi=spi)
    d.initialize()
    d.draw_text(0, 0, "HELLO SPI")
    d.update()
    # SPI should have been called with bytes containing the text
    all_bytes = b"".join(spi.sent)
    assert b"HELLO SPI" in all_bytes
