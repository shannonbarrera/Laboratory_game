"""Drawing code for the Space Lab's "launch sequence" game. Mirrors the
same bold-navy-outline, flat-color clip-art style as the other rooms,
and reuses game/ui.py's generic helpers (background, HUD, GO button,
message banner) directly.
"""
import math

import pygame

from . import config, ui

ROCKET_BODY = (240, 248, 252)
ROCKET_ACCENT = (225, 70, 60)
WINDOW_COLOR = (120, 190, 235)
PAD_COLOR = (180, 188, 198)
FLAME_COLORS = [(255, 150, 60), (255, 210, 90), (235, 90, 60)]


def draw_launchpad(surface, center_x, base_y):
    pad_rect = pygame.Rect(0, 0, 140, 16)
    pad_rect.center = (center_x, base_y)
    pygame.draw.rect(surface, PAD_COLOR, pad_rect, border_radius=4)
    pygame.draw.rect(surface, config.NAVY, pad_rect, width=3, border_radius=4)

    # A simple gantry tower beside the rocket, just for flavor.
    tower_x = center_x - 90
    pygame.draw.line(surface, config.NAVY, (tower_x, base_y), (tower_x, base_y - 160), 4)
    pygame.draw.line(surface, config.NAVY, (tower_x - 14, base_y), (tower_x - 14, base_y - 110), 4)
    for i in range(4):
        y = base_y - 20 - i * 40
        pygame.draw.line(surface, config.NAVY, (tower_x - 14, y), (tower_x, y - 20), 3)


def draw_rocket(surface, center_x, base_y, armed, lift, launching):
    """lift is 0 (sitting on the pad) to 1 (flown off the top of the
    screen) during the launch animation; armed pulses the rocket gently
    once the sequence is complete, as a "ready to go" cue."""
    y_offset = lift * (base_y + 200)
    cx = center_x
    cy = base_y - y_offset

    pulse = (math.sin(pygame.time.get_ticks() * 0.008) + 1) / 2 if armed else 0
    wobble = math.sin(pygame.time.get_ticks() * 0.003) * 2 if not launching else 0

    body_w = 46
    body_h = 90
    nose_h = 36

    body_rect = pygame.Rect(0, 0, body_w, body_h)
    body_rect.center = (cx + wobble, cy)
    pygame.draw.rect(surface, ROCKET_BODY, body_rect, border_radius=16)
    pygame.draw.rect(surface, config.NAVY, body_rect, width=3, border_radius=16)

    nose_pts = [
        (cx + wobble - body_w / 2, body_rect.top),
        (cx + wobble + body_w / 2, body_rect.top),
        (cx + wobble, body_rect.top - nose_h),
    ]
    pygame.draw.polygon(surface, ROCKET_ACCENT, nose_pts)
    pygame.draw.polygon(surface, config.NAVY, nose_pts, width=3)

    pygame.draw.circle(surface, WINDOW_COLOR, (int(cx + wobble), int(body_rect.top + 28)), 11)
    pygame.draw.circle(surface, config.NAVY, (int(cx + wobble), int(body_rect.top + 28)), 11, width=2)

    fin_w, fin_h = 22, 30
    for side in (-1, 1):
        fin_pts = [
            (cx + wobble + side * body_w / 2, body_rect.bottom - fin_h),
            (cx + wobble + side * body_w / 2, body_rect.bottom),
            (cx + wobble + side * (body_w / 2 + fin_w), body_rect.bottom),
        ]
        pygame.draw.polygon(surface, ROCKET_ACCENT, fin_pts)
        pygame.draw.polygon(surface, config.NAVY, fin_pts, width=2)

    if armed and not launching:
        glow_r = int(body_w * 0.9 + pulse * 10)
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 230, 150, 90), (glow_r, glow_r), glow_r)
        surface.blit(glow, (cx + wobble - glow_r, cy - glow_r))

    if launching:
        flame_h = 26 + 10 * math.sin(pygame.time.get_ticks() * 0.03)
        flame_pts = [
            (cx + wobble - 14, body_rect.bottom),
            (cx + wobble + 14, body_rect.bottom),
            (cx + wobble, body_rect.bottom + flame_h),
        ]
        pygame.draw.polygon(surface, FLAME_COLORS[int(pygame.time.get_ticks() / 60) % 3], flame_pts)
        pygame.draw.polygon(surface, config.NAVY, flame_pts, width=2)


def draw_sequence_card(surface, rect, sequence, progress, chemicals):
    """An ordered row of colored dots (the launch code) -- completed
    steps get a checkmark, the next one pulses so it's obvious what to
    press next, and later ones are dimmed outlines."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, config.PANEL_BG, panel.get_rect(), border_radius=16)
    pygame.draw.rect(panel, config.NAVY, panel.get_rect(), width=4, border_radius=16)
    surface.blit(panel, rect.topleft)

    ui.draw_text_center(surface, "Launch Code", (rect.centerx, rect.y + 28), 22)

    n = len(sequence)
    spacing = min(40, (rect.width - 40) / max(1, n))
    start_x = rect.centerx - spacing * (n - 1) / 2
    y = rect.y + 70
    pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2

    for i, chem_index in enumerate(sequence):
        x = start_x + i * spacing
        color = chemicals[chem_index]["color"]
        if i < progress:
            pygame.draw.circle(surface, color, (x, y), 13)
            pygame.draw.circle(surface, config.NAVY, (x, y), 13, width=2)
            pygame.draw.line(surface, config.WHITE, (x - 5, y), (x - 1, y + 5), 3)
            pygame.draw.line(surface, config.WHITE, (x - 1, y + 5), (x + 6, y - 6), 3)
        elif i == progress:
            r = 13 + pulse * 4
            pygame.draw.circle(surface, color, (x, y), r)
            pygame.draw.circle(surface, config.NAVY, (x, y), r, width=3)
        else:
            pygame.draw.circle(surface, config.GLASS_COLOR, (x, y), 13)
            pygame.draw.circle(surface, color, (x, y), 13, width=2)
