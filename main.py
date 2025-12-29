"""raspi_pipboy prototype
A minimal Pygame-based prototype showing a Fallout/Pip-Boy-styled interface.
"""
import sys
import pygame
from pygame import Color

# Configuration
WIDTH, HEIGHT = 1024, 600
FPS = 60
TITLE = "raspi_pipboy — prototype"

# A small palette inspired by Pip-Boy (green monochrome)
PALETTE = {
    'bg': Color('#061d0f'),
    'panel': Color('#0a2620'),
    'accent': Color('#7ef58b'),
    'muted': Color('#184b3a'),
    'text': Color('#bdfec4'),
    'orange': Color('#ffb86b')
}

MENU_ITEMS = [
    'Status',
    'Inventory',
    'Data',
    'Map',
    'Radio',
    'Settings'
]


def draw_left_panel(surface, font, selected_index, t):
    panel_w = 300
    pygame.draw.rect(surface, PALETTE['panel'], (0, 0, panel_w, HEIGHT))
    # Title
    title_surf = font.render('PIP-BOY', True, PALETTE['accent'])
    surface.blit(title_surf, (16, 16))

    # Menu
    for idx, item in enumerate(MENU_ITEMS):
        y = 80 + idx * 44
        is_sel = idx == selected_index
        color = PALETTE['accent'] if is_sel else PALETTE['text']
        rect = pygame.Rect(12, y - 6, panel_w - 24, 36)
        if is_sel:
            # subtle animated highlight
            glow = 8 + int(4 * (1 + pygame.math.sin(t * 4)))
            pygame.draw.rect(surface, PALETTE['muted'], rect, border_radius=6)
        txt_surf = font.render(item, True, color)
        surface.blit(txt_surf, (24, y))


def draw_main_area(surface, font_small, selected_index, t):
    x = 320
    w = WIDTH - x - 16
    pygame.draw.rect(surface, PALETTE['bg'], (x, 8, w, HEIGHT - 16))
    # Header
    header = f"{MENU_ITEMS[selected_index]}"
    hdr_surf = font_small.render(header, True, PALETTE['orange'])
    surface.blit(hdr_surf, (x + 12, 16))
    # Animated bars / content
    for i in range(6):
        y = 80 + i * 48
        # example animated value
        v = 0.5 + 0.5 * pygame.math.sin(t * (0.8 + i * 0.2))
        bar_w = int((w - 64) * v)
        pygame.draw.rect(surface, PALETTE['muted'], (x + 32, y, w - 64, 28), border_radius=6)
        pygame.draw.rect(surface, PALETTE['accent'], (x + 32, y, bar_w, 28), border_radius=6)
        txt = font_small.render(f"Param {i+1}: {int(v*100)}%", True, PALETTE['text'])
        surface.blit(txt, (x + 40, y + 4))


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    font = pygame.font.SysFont('dejavusans', 28)
    font_small = pygame.font.SysFont('dejavusans', 20)

    selected = 0
    t = 0.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        t += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = max(0, selected - 1)
                elif event.key == pygame.K_DOWN:
                    selected = min(len(MENU_ITEMS) - 1, selected + 1)
                elif event.key == pygame.K_ESCAPE:
                    running = False
        screen.fill(PALETTE['bg'])
        draw_left_panel(screen, font, selected, t)
        draw_main_area(screen, font_small, selected, t)

        # Footer / FPS
        fps_surf = font_small.render(f"FPS: {int(clock.get_fps())}", True, PALETTE['muted'])
        screen.blit(fps_surf, (WIDTH - 120, HEIGHT - 32))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
