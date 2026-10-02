"""Drawing code. Nothing in here holds game logic -- it just takes the
current state (bottles, beaker, level, score...) and paints it onto the
logical canvas. Keeping this separate from game/app.py makes both halves
much easier to follow.

The look is bold-outline, flat-color "classroom clip-art" chemistry
glassware: thick navy outlines, bright saturated liquids, a couple of
white gloss streaks, and little measurement tick marks -- the same
visual language as a kid's science-poster beaker icon.
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
    bench_y = h - bench_h
    pygame.draw.rect(surface, config.BENCH_COLOR, (0, bench_y, w, bench_h))
    pygame.draw.rect(surface, config.BENCH_EDGE, (0, bench_y, w, 10))
    # Faint tile seams on the counter top, like a lab bench surface.
    for x in range(0, w, 96):
        pygame.draw.line(surface, config.BENCH_EDGE, (x, bench_y + 10), (x, h), 1)

    _draw_decor_bubbles(surface)


_DECOR_BUBBLES = [
    (120, 90, 14, (235, 60, 70), True),
    (175, 150, 7, config.NAVY, False),
    (205, 70, 10, (90, 200, 90), True),
    (998, 25, 12, (235, 60, 70), True),
    (1008, 55, 7, config.NAVY, False),
]


def _draw_decor_bubbles(surface):
    """A few floating circles up near the top corners, purely decorative,
    echoing the loose bubbles you see floating around a clip-art flask."""
    t = pygame.time.get_ticks() * 0.001
    for i, (x, y, r, color, filled) in enumerate(_DECOR_BUBBLES):
        bob = math.sin(t * 1.3 + i) * 5
        pos = (x, int(y + bob))
        if filled:
            pygame.draw.circle(surface, color, pos, r)
            pygame.draw.circle(surface, config.NAVY, pos, r, width=2)
        else:
            pygame.draw.circle(surface, color, pos, r, width=2)


def draw_text_center(surface, text, pos, size, color=None, bold=True, shadow=True):
    if color is None:
        color = config.TEXT_COLOR
    font = get_font(size, bold)
    if shadow:
        # Light text gets a dark outline, dark text gets a soft light
        # outline, so it stays legible against the bright background.
        brightness = sum(color) / 3
        shadow_color = (0, 0, 0) if brightness > 140 else config.WHITE
        shadow_surf = font.render(text, True, shadow_color)
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            rect = shadow_surf.get_rect(center=(pos[0] + dx, pos[1] + dy))
            surface.blit(shadow_surf, rect)
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect(center=pos)
    surface.blit(text_surf, rect)
    return rect


def _gloss_streak(surf_w, surf_h, rect, tilt_deg=18):
    """A translucent white diagonal stripe, the classic glass-highlight
    look. Returns a small surface to blit onto the glass area."""
    streak = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    stripe_w = max(4, rect.width // 8)
    poly = [
        (rect.x + rect.width * 0.22, rect.y),
        (rect.x + rect.width * 0.22 + stripe_w, rect.y),
        (rect.x + rect.width * 0.1 + stripe_w, rect.y + rect.height),
        (rect.x + rect.width * 0.1, rect.y + rect.height),
    ]
    pygame.draw.polygon(streak, (255, 255, 255, 90), poly)
    return streak


def draw_bottle(surface, bottle, center_x, base_y, current_count):
    """A chemistry dropper bottle: round rubber-bulb cap, narrow neck with
    tick marks, and a bright liquid fill with a gloss streak -- outlined
    in bold navy like classroom glassware clip-art."""
    body_w, body_h = 78, 92
    neck_w, neck_h = 22, 22
    bulb_r = 15

    surf_w, surf_h = body_w + 24, body_h + neck_h + bulb_r * 2 + 10
    bottle_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    cx = surf_w // 2
    top_y = bulb_r * 2 + 4

    squeeze = bottle.squeeze
    bulge = int(8 * squeeze)

    body_rect = pygame.Rect(cx - body_w // 2 - bulge // 2, top_y + neck_h,
                             body_w + bulge, body_h)
    pygame.draw.rect(bottle_surf, config.GLASS_COLOR, body_rect, border_radius=16)

    liquid_h = int(body_rect.height * 0.68)
    liquid_rect = pygame.Rect(body_rect.x + 5, body_rect.bottom - liquid_h - 5,
                               body_rect.width - 10, liquid_h)
    pygame.draw.rect(bottle_surf, bottle.color, liquid_rect, border_radius=12)

    pygame.draw.rect(bottle_surf, config.GLASS_OUTLINE, body_rect, width=4, border_radius=16)

    # Graduation tick marks on the body, like a measuring bottle.
    for i in range(1, 4):
        ty = body_rect.y + body_rect.height * i // 4
        pygame.draw.line(bottle_surf, config.GLASS_OUTLINE,
                          (body_rect.x + 6, ty), (body_rect.x + 18, ty), 2)

    # Gloss streak over the liquid.
    streak = _gloss_streak(surf_w, surf_h, liquid_rect)
    bottle_surf.blit(streak, (0, 0))

    neck_rect = pygame.Rect(cx - neck_w // 2, top_y, neck_w, neck_h + 6)
    pygame.draw.rect(bottle_surf, config.GLASS_COLOR, neck_rect, border_radius=4)
    pygame.draw.rect(bottle_surf, config.GLASS_OUTLINE, neck_rect, width=3, border_radius=4)

    # Rubber dropper bulb on top -- the classic eyedropper-bottle look.
    bulb_center = (cx, bulb_r + 2)
    pygame.draw.circle(bottle_surf, (70, 60, 65), bulb_center, bulb_r)
    pygame.draw.circle(bottle_surf, config.GLASS_OUTLINE, bulb_center, bulb_r, width=3)
    pygame.draw.circle(bottle_surf, (120, 108, 112),
                        (bulb_center[0] - 4, bulb_center[1] - 4), 4)

    rotated = pygame.transform.rotate(bottle_surf, bottle.tilt)
    rect = rotated.get_rect(center=(center_x, base_y - (body_h // 2 + neck_h // 2)))
    surface.blit(rotated, rect)

    # Dots showing how many drops of this color are already in the beaker.
    dot_y = base_y + 22
    for i in range(current_count):
        x = center_x - (current_count - 1) * 11 // 2 + i * 11
        pygame.draw.circle(surface, bottle.color, (x, dot_y), 5)
        pygame.draw.circle(surface, config.GLASS_OUTLINE, (x, dot_y), 5, width=1)


def draw_recipe_card(surface, rect, chemicals, recipe):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, config.PANEL_BG, panel.get_rect(), border_radius=16)
    pygame.draw.rect(panel, config.NAVY, panel.get_rect(), width=4, border_radius=16)
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
            pygame.draw.circle(surface, config.NAVY, (x, row_y), 9, width=2)
        row_y += 34


def draw_beaker(surface, rect, beaker, chemicals, liquid_color):
    """Draws the mixing vessel as a conical (Erlenmeyer) flask -- the
    classic "science lab" silhouette -- instead of a plain glass box."""
    shake_x = int(math.sin(pygame.time.get_ticks() * 0.08) * 8 * beaker.shake)

    x, y, w, h = rect.x + shake_x, rect.y, rect.width, rect.height
    neck_w = w * 0.34
    neck_h = h * 0.24
    cx = x + w / 2
    shoulder_y = y + neck_h

    def width_at(frac):
        """Linear taper from the neck width at the shoulder to the full
        width at the bottom; frac is 0 at the shoulder, 1 at the bottom."""
        return neck_w + (w - neck_w) * frac

    flask_surf = pygame.Surface((w + 20, h + 10), pygame.SRCALPHA)
    ox, oy = 10, 0  # offset so shapes don't clip the surface edge
    fcx = cx - x + ox

    body_poly = [
        (fcx - neck_w / 2, shoulder_y - y + oy),
        (fcx + neck_w / 2, shoulder_y - y + oy),
        (fcx + w / 2, h + oy),
        (fcx - w / 2, h + oy),
    ]
    pygame.draw.polygon(flask_surf, config.GLASS_COLOR, body_poly)

    fill_ratio = min(1.0, beaker.fill_display / config.MAX_TOTAL_DROPS)
    body_h = h - (shoulder_y - y)
    liquid_h = body_h * fill_ratio
    if liquid_h > 1:
        liquid_top_y = h - liquid_h
        frac_top = max(0.0, 1 - liquid_h / body_h)
        half_top = width_at(frac_top) / 2
        half_bottom = w / 2
        wobble = math.sin(pygame.time.get_ticks() * 0.01 + beaker.wobble * 3) * 4 * beaker.wobble
        liquid_poly = [
            (fcx - half_top + wobble, liquid_top_y + oy),
            (fcx + half_top + wobble, liquid_top_y + oy),
            (fcx + half_bottom, h + oy),
            (fcx - half_bottom, h + oy),
        ]
        liquid_surf = pygame.Surface(flask_surf.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(liquid_surf, (*liquid_color, 235), liquid_poly)
        flask_surf.blit(liquid_surf, (0, 0))

        # Gloss streak down the liquid.
        streak_rect = pygame.Rect(fcx - half_bottom * 0.5, liquid_top_y + oy,
                                   half_bottom * 0.4, liquid_h)
        streak = _gloss_streak(*flask_surf.get_size(), streak_rect)
        flask_surf.blit(streak, (0, 0))

    pygame.draw.polygon(flask_surf, config.GLASS_OUTLINE, body_poly, width=4)

    # Graduation ticks down the lower body.
    for i in range(1, 4):
        frac = i / 4
        ty = shoulder_y - y + oy + body_h * frac
        half = width_at(frac) / 2
        pygame.draw.line(flask_surf, config.GLASS_OUTLINE,
                          (fcx - half + 6, ty), (fcx - half + 20, ty), 2)

    # Neck + flared collar lip at the top.
    neck_rect = pygame.Rect(fcx - neck_w / 2, oy, neck_w, neck_h)
    pygame.draw.rect(flask_surf, config.GLASS_COLOR, neck_rect)
    pygame.draw.rect(flask_surf, config.GLASS_OUTLINE, neck_rect, width=4)
    collar = pygame.Rect(fcx - neck_w / 2 - 6, oy, neck_w + 12, 10)
    pygame.draw.rect(flask_surf, config.GLASS_COLOR, collar, border_radius=3)
    pygame.draw.rect(flask_surf, config.GLASS_OUTLINE, collar, width=3, border_radius=3)

    surface.blit(flask_surf, (x - ox, y - oy))

    draw_text_center(surface, f"{beaker.total} drops", (cx, y - 18), 22)


def draw_go_button(surface, rect, pulse):
    glow_radius = int(rect.width / 2 + 6 + pulse * 6)
    glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*config.GO_BUTTON_GLOW, 90), (glow_radius, glow_radius), glow_radius)
    surface.blit(glow, (rect.centerx - glow_radius, rect.centery - glow_radius))

    pygame.draw.circle(surface, config.GO_BUTTON_COLOR, rect.center, rect.width // 2)
    pygame.draw.circle(surface, config.NAVY, rect.center, rect.width // 2, width=4)
    draw_text_center(surface, "GO!", rect.center, 34, color=config.WHITE)
    draw_text_center(surface, "space / button", (rect.centerx, rect.bottom + 18), 14, bold=False)


def draw_hud(surface, level_number, streak):
    draw_text_center(surface, f"Level {level_number}", (90, 36), 28)
    stars = "★" * min(streak, 5)
    if stars:
        draw_text_center(surface, stars, (surface.get_width() - 110, 36), 28,
                          color=(240, 170, 20))


def draw_message_banner(surface, text, color):
    w, h = surface.get_size()
    band = pygame.Rect(0, h // 2 - 60, w, 120)
    band_surf = pygame.Surface((band.width, band.height), pygame.SRCALPHA)
    pygame.draw.rect(band_surf, (*color, 225), band_surf.get_rect(), border_radius=20)
    surface.blit(band_surf, band.topleft)
    pygame.draw.rect(surface, config.NAVY, band, width=4, border_radius=20)
    draw_text_center(surface, text, band.center, 44, color=config.WHITE)


def draw_hint_arrow(surface, center_x, base_y, too_many):
    arrow_color = config.BAD_COLOR
    bob = math.sin(pygame.time.get_ticks() * 0.01) * 6
    y = base_y - 150 + bob
    if too_many:
        points = [(center_x - 14, y), (center_x + 14, y), (center_x, y + 20)]
    else:
        points = [(center_x - 14, y + 20), (center_x + 14, y + 20), (center_x, y)]
    pygame.draw.polygon(surface, arrow_color, points)
    pygame.draw.polygon(surface, config.NAVY, points, width=2)
