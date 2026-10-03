"""Drawing code for the Bug & Plant Lab's "grow the plant" game. Mirrors
game/ui.py's bold-navy-outline, flat-color clip-art style, and reuses
several of its generic helpers directly (background, HUD, recipe card,
GO button, message banner, hint arrows) so the two rooms feel like the
same building.
"""
import math

import pygame

from . import config

WATER_COLOR = (60, 140, 230)
SUN_COLOR = (250, 200, 60)
POT_COLOR = (205, 120, 75)
SOIL_COLOR = (90, 60, 45)
STEM_COLOR = (70, 170, 90)
WILT_COLOR = (150, 130, 80)
LEAF_COLOR = (90, 200, 90)
PETAL_COLOR = (235, 90, 150)
BUG_COLOR = (225, 70, 60)

MAX_STEM_PRESSES = 10  # just a rendering cap, independent of gameplay max


def draw_water_source(surface, bottle, center_x, base_y, current_count):
    """A little raincloud with a droplet -- the "bottle" for water,
    reusing the same squeeze/tilt animation state bottles use."""
    cx, base_y = center_x, base_y
    wobble = bottle.tilt / 18.0  # 0..1

    cloud_y = base_y - 70
    for dx, dy, r in ((-18, 0, 18), (0, -10, 22), (18, 0, 18), (-6, 6, 16), (10, 6, 16)):
        pygame.draw.circle(surface, config.WHITE, (int(cx + dx), int(cloud_y + dy)), r)
    for dx, dy, r in ((-18, 0, 18), (0, -10, 22), (18, 0, 18), (-6, 6, 16), (10, 6, 16)):
        pygame.draw.circle(surface, config.NAVY, (int(cx + dx), int(cloud_y + dy)), r, width=2)

    drop_y = cloud_y + 36 + wobble * 14
    drop_pts = [(cx, drop_y - 12), (cx - 8, drop_y + 6), (cx + 8, drop_y + 6)]
    pygame.draw.polygon(surface, WATER_COLOR, drop_pts)
    pygame.draw.circle(surface, WATER_COLOR, (cx, drop_y + 6), 8)
    pygame.draw.polygon(surface, config.NAVY, drop_pts, width=2)
    pygame.draw.circle(surface, config.NAVY, (cx, drop_y + 6), 8, width=2)

    _draw_count_dots(surface, cx, base_y + 22, current_count, WATER_COLOR)


def draw_sun_source(surface, bottle, center_x, base_y, current_count):
    """A friendly sun with rays, pulsing a little when its button is
    pressed (reusing the same squeeze animation bottles use)."""
    cx = center_x
    cy = base_y - 60
    pulse = bottle.squeeze

    for i in range(8):
        angle = i * math.pi / 4
        inner = 22 + pulse * 4
        outer = 34 + pulse * 6
        x1, y1 = cx + inner * math.cos(angle), cy + inner * math.sin(angle)
        x2, y2 = cx + outer * math.cos(angle), cy + outer * math.sin(angle)
        pygame.draw.line(surface, SUN_COLOR, (x1, y1), (x2, y2), 6)
        pygame.draw.line(surface, config.NAVY, (x1, y1), (x2, y2), 2)

    pygame.draw.circle(surface, SUN_COLOR, (cx, cy), 22)
    pygame.draw.circle(surface, config.NAVY, (cx, cy), 22, width=3)
    # simple happy face
    pygame.draw.circle(surface, config.NAVY, (cx - 7, cy - 4), 3)
    pygame.draw.circle(surface, config.NAVY, (cx + 7, cy - 4), 3)
    pygame.draw.arc(surface, config.NAVY, (cx - 9, cy - 2, 18, 14), math.pi, 2 * math.pi, 2)

    _draw_count_dots(surface, cx, base_y + 22, current_count, SUN_COLOR)


def _draw_count_dots(surface, center_x, dot_y, count, color):
    for i in range(count):
        x = center_x - (count - 1) * 11 // 2 + i * 11
        pygame.draw.circle(surface, color, (x, dot_y), 5)
        pygame.draw.circle(surface, config.NAVY, (x, dot_y), 5, width=1)


def draw_pot_and_plant(surface, center_x, pot_top_y, total_presses, bloom, wilt):
    """The pot sits at a fixed spot; the plant grows live as water/sun are
    added, blooms on success, and droops on failure."""
    pot_w, pot_h = 110, 70
    pot_rect_top = pygame.Rect(center_x - pot_w // 2, pot_top_y, pot_w, pot_h * 0.3)
    pot_poly = [
        (center_x - pot_w / 2, pot_top_y),
        (center_x + pot_w / 2, pot_top_y),
        (center_x + pot_w * 0.35, pot_top_y + pot_h),
        (center_x - pot_w * 0.35, pot_top_y + pot_h),
    ]
    soil_rect = pygame.Rect(center_x - pot_w / 2 + 6, pot_top_y - 8, pot_w - 12, 16)

    stem_base = (center_x, pot_top_y - 4)
    presses = min(total_presses, MAX_STEM_PRESSES)
    stem_height = 30 + presses * 16
    sway = math.sin(pygame.time.get_ticks() * 0.002) * (4 * (1 - wilt) + 1 * wilt)
    lean = wilt * 50  # degrees the stem droops over when wilted

    stem_color = _lerp_color(STEM_COLOR, WILT_COLOR, wilt)
    leaf_color = _lerp_color(LEAF_COLOR, WILT_COLOR, wilt)

    angle = math.radians(90 - lean)
    tip_x = stem_base[0] + stem_height * math.cos(angle) + sway
    tip_y = stem_base[1] - stem_height * math.sin(angle)

    pygame.draw.line(surface, stem_color, stem_base, (tip_x, tip_y), 7)
    pygame.draw.line(surface, config.NAVY, stem_base, (tip_x, tip_y), 1)

    leaf_pairs = presses // 2
    for i in range(leaf_pairs):
        t = (i + 1) / (leaf_pairs + 1)
        lx = stem_base[0] + (tip_x - stem_base[0]) * t
        ly = stem_base[1] + (tip_y - stem_base[1]) * t
        for side in (-1, 1):
            leaf_center = (lx + side * 16, ly - 4)
            leaf_surf_rect = pygame.Rect(0, 0, 26, 14)
            leaf_surf_rect.center = leaf_center
            pygame.draw.ellipse(surface, leaf_color, leaf_surf_rect)
            pygame.draw.ellipse(surface, config.NAVY, leaf_surf_rect, width=2)

    if bloom > 0.01:
        _draw_flower(surface, (tip_x, tip_y), bloom)

    # Pot drawn last so the stem appears to emerge from inside it.
    pygame.draw.polygon(surface, POT_COLOR, pot_poly)
    pygame.draw.polygon(surface, config.NAVY, pot_poly, width=4)
    pygame.draw.ellipse(surface, SOIL_COLOR, soil_rect)
    pygame.draw.ellipse(surface, config.NAVY, soil_rect, width=2)
    pygame.draw.rect(surface, POT_COLOR, pot_rect_top)
    pygame.draw.rect(surface, config.NAVY, pot_rect_top, width=3)


def _draw_flower(surface, center, bloom):
    cx, cy = center
    radius = 10 * bloom
    for i in range(6):
        angle = i * math.pi / 3
        petal_center = (cx + radius * 1.3 * math.cos(angle), cy + radius * 1.3 * math.sin(angle))
        petal_rect = pygame.Rect(0, 0, radius * 1.6, radius)
        petal_rect.center = petal_center
        pygame.draw.ellipse(surface, PETAL_COLOR, petal_rect)
        pygame.draw.ellipse(surface, config.NAVY, petal_rect, width=1)
    pygame.draw.circle(surface, SUN_COLOR, (int(cx), int(cy)), int(radius * 0.8))
    pygame.draw.circle(surface, config.NAVY, (int(cx), int(cy)), int(radius * 0.8), width=1)


def _lerp_color(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_bug(surface, x, y, eating):
    """A friendly ladybug visiting the plant. It wiggles gently while
    just sitting there, and more energetically once it starts eating --
    a clear, non-scary visual "shoo it now" cue."""
    wiggle_speed = 0.02 if eating else 0.006
    wiggle_size = 3 if eating else 1
    wiggle = math.sin(pygame.time.get_ticks() * wiggle_speed) * wiggle_size
    bx, by = x + wiggle, y

    pygame.draw.circle(surface, BUG_COLOR, (int(bx), int(by)), 11)
    pygame.draw.circle(surface, config.NAVY, (int(bx), int(by)), 11, width=2)
    pygame.draw.line(surface, config.NAVY, (bx, by - 11), (bx, by + 11), 2)
    for dx, dy in ((-5, -4), (5, -4), (-5, 4), (5, 4), (0, -7)):
        pygame.draw.circle(surface, config.NAVY, (int(bx + dx), int(by + dy)), 2)

    # Small antennae, perked up more while eating (excited/busy).
    antenna_spread = 6 if eating else 3
    pygame.draw.line(surface, config.NAVY, (bx - 3, by - 11),
                      (bx - antenna_spread, by - 17), 2)
    pygame.draw.line(surface, config.NAVY, (bx + 3, by - 11),
                      (bx + antenna_spread, by - 17), 2)
