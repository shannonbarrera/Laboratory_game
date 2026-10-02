"""Drawing code. Nothing in here holds game logic -- it just takes the
current state (bottles, beaker, level, score...) and paints it onto the
logical canvas. Keeping this separate from game/app.py makes both halves
much easier to follow.
"""
import math

import pygame

from . import config

_fonts = {}


def get_font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        font = pygame.font.SysFont("comicsansms,arial,sans", size, bold=bold)
        _fonts[key] = font
    return _fonts[key]


def draw_background(surface):
    w, h = surface.get_size()
    top = pygame.Color(*config.BG_TOP)
    bottom = pygame.Color(*config.BG_BOTTOM)
    for y in range(h):
        t = y / h
        color = top.lerp(bottom, t)
        pygame.draw.line(surface, color, (0, y), (w, y))

    bench_h = 150
    pygame.draw.rect(surface, config.BENCH_COLOR, (0, h - bench_h, w, bench_h))
    pygame.draw.rect(surface, (90, 60, 45), (0, h - bench_h, w, 10))


def draw_text_center(surface, text, pos, size, color=config.TEXT_COLOR, bold=True, shadow=True):
    font = get_font(size, bold)
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        rect = shadow_surf.get_rect(center=(pos[0] + 2, pos[1] + 2))
        surface.blit(shadow_surf, rect)
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect(center=pos)
    surface.blit(text_surf, rect)
    return rect


def draw_bottle(surface, bottle, center_x, base_y, current_count, button_label):
    """A simple round-shouldered bottle with colored liquid inside and a
    number badge below it showing which button fills it."""
    body_w, body_h = 86, 100
    neck_w, neck_h = 30, 26

    bottle_surf = pygame.Surface((body_w + 20, body_h + neck_h + 20), pygame.SRCALPHA)
    cx = bottle_surf.get_width() // 2

    squeeze = bottle.squeeze
    bulge = int(10 * squeeze)

    body_rect = pygame.Rect(cx - body_w // 2 - bulge // 2, neck_h + 10, body_w + bulge, body_h)
    pygame.draw.rect(bottle_surf, config.GLASS_COLOR, body_rect, border_radius=18)
    pygame.draw.rect(bottle_surf, config.GLASS_OUTLINE, body_rect, width=3, border_radius=18)

    neck_rect = pygame.Rect(cx - neck_w // 2, 4, neck_w, neck_h + 10)
    pygame.draw.rect(bottle_surf, config.GLASS_COLOR, neck_rect, border_radius=6)
    pygame.draw.rect(bottle_surf, config.GLASS_OUTLINE, neck_rect, width=3, border_radius=6)

    liquid_h = int(body_rect.height * 0.65)
    liquid_rect = pygame.Rect(body_rect.x + 6, body_rect.bottom - liquid_h - 6,
                               body_rect.width - 12, liquid_h)
    pygame.draw.rect(bottle_surf, bottle.color, liquid_rect, border_radius=14)

    cap_rect = pygame.Rect(cx - neck_w // 2 - 4, 0, neck_w + 8, 12)
    pygame.draw.rect(bottle_surf, (80, 80, 90), cap_rect, border_radius=4)

    rotated = pygame.transform.rotate(bottle_surf, bottle.tilt)
    rect = rotated.get_rect(center=(center_x, base_y - body_h // 2))
    surface.blit(rotated, rect)

    # Button badge
    badge_y = base_y + 24
    pygame.draw.circle(surface, bottle.color, (center_x, badge_y), 22)
    pygame.draw.circle(surface, config.WHITE, (center_x, badge_y), 22, width=3)
    draw_text_center(surface, button_label, (center_x, badge_y), 22, color=config.WHITE)

    # Dots showing how many drops of this color are already in the beaker.
    dot_y = badge_y + 34
    for i in range(current_count):
        x = center_x - (current_count - 1) * 11 // 2 + i * 11
        pygame.draw.circle(surface, bottle.color, (x, dot_y), 5)
        pygame.draw.circle(surface, config.WHITE, (x, dot_y), 5, width=1)


def draw_recipe_card(surface, rect, chemicals, recipe):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*config.PANEL_BG, 230), panel.get_rect(), border_radius=16)
    pygame.draw.rect(panel, config.WHITE, panel.get_rect(), width=3, border_radius=16)
    surface.blit(panel, rect.topleft)

    draw_text_center(surface, "Recipe", (rect.centerx, rect.y + 28), 26)

    row_y = rect.y + 64
    for chem_index, count in recipe.items():
        if count <= 0:
            continue
        color = chemicals[chem_index]["color"]
        start_x = rect.x + 24
        for i in range(count):
            x = start_x + i * 24
            pygame.draw.circle(surface, color, (x, row_y), 9)
            pygame.draw.circle(surface, config.WHITE, (x, row_y), 9, width=2)
        row_y += 34


def draw_beaker(surface, rect, beaker, chemicals, liquid_color):
    shake_x = int(math.sin(pygame.time.get_ticks() * 0.08) * 8 * beaker.shake)

    glass = pygame.Rect(rect.x + shake_x, rect.y, rect.width, rect.height)
    pygame.draw.rect(surface, (255, 255, 255, 40), glass, border_radius=10)
    pygame.draw.rect(surface, config.GLASS_COLOR, glass, width=0, border_radius=10)

    fill_ratio = min(1.0, beaker.fill_display / config.MAX_TOTAL_DROPS)
    liquid_h = int((glass.height - 16) * fill_ratio)
    if liquid_h > 0:
        wobble = math.sin(pygame.time.get_ticks() * 0.01 + beaker.wobble * 3) * 4 * beaker.wobble
        liquid_rect = pygame.Rect(glass.x + 8, glass.bottom - 8 - liquid_h,
                                   glass.width - 16, liquid_h)
        liquid_surf = pygame.Surface((liquid_rect.width, liquid_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(liquid_surf, (*liquid_color, 230), liquid_surf.get_rect(),
                          border_bottom_left_radius=8, border_bottom_right_radius=8)
        surface.blit(liquid_surf, (liquid_rect.x + wobble, liquid_rect.y))

    pygame.draw.rect(surface, config.GLASS_OUTLINE, glass, width=4, border_radius=10)
    # Little spout flares at the top rim
    pygame.draw.line(surface, config.GLASS_OUTLINE,
                      (glass.x - 6, glass.y + 10), (glass.x, glass.y + 10), 4)
    pygame.draw.line(surface, config.GLASS_OUTLINE,
                      (glass.right, glass.y + 10), (glass.right + 6, glass.y + 10), 4)

    draw_text_center(surface, f"{beaker.total} drops", (glass.centerx, glass.y - 18), 22)


def draw_go_button(surface, rect, pulse):
    glow_radius = int(rect.width / 2 + 6 + pulse * 6)
    glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*config.GO_BUTTON_GLOW, 90), (glow_radius, glow_radius), glow_radius)
    surface.blit(glow, (rect.centerx - glow_radius, rect.centery - glow_radius))

    pygame.draw.circle(surface, config.GO_BUTTON_COLOR, rect.center, rect.width // 2)
    pygame.draw.circle(surface, config.WHITE, rect.center, rect.width // 2, width=4)
    draw_text_center(surface, "GO!", rect.center, 34)
    draw_text_center(surface, "space / button", (rect.centerx, rect.bottom + 18), 14, bold=False)


def draw_hud(surface, level_number, streak):
    draw_text_center(surface, f"Level {level_number}", (90, 36), 28)
    stars = "★" * min(streak, 5)
    if stars:
        draw_text_center(surface, stars, (surface.get_width() - 110, 36), 28,
                          color=(255, 220, 80))


def draw_message_banner(surface, text, color):
    w, h = surface.get_size()
    band = pygame.Rect(0, h // 2 - 60, w, 120)
    band_surf = pygame.Surface((band.width, band.height), pygame.SRCALPHA)
    pygame.draw.rect(band_surf, (*color, 210), band_surf.get_rect(), border_radius=20)
    surface.blit(band_surf, band.topleft)
    draw_text_center(surface, text, band.center, 44)


def draw_hint_arrow(surface, center_x, base_y, too_many):
    arrow_color = config.BAD_COLOR
    bob = math.sin(pygame.time.get_ticks() * 0.01) * 6
    y = base_y - 150 + bob
    if too_many:
        points = [(center_x - 14, y), (center_x + 14, y), (center_x, y + 20)]
    else:
        points = [(center_x - 14, y + 20), (center_x + 14, y + 20), (center_x, y)]
    pygame.draw.polygon(surface, arrow_color, points)
