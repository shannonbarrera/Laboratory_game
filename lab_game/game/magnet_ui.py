"""Drawing code for the Magnet Lab's "does it stick?" game. Mirrors the
same bold-navy-outline, flat-color clip-art style as the other rooms.
"""
import math

import pygame

from . import config, hub, ui

METAL_COLOR = (180, 188, 200)
WOOD_COLOR = (170, 120, 75)
BALL_COLOR = (240, 140, 90)
FEATHER_COLOR = (235, 240, 245)
LEAF_COLOR = (100, 200, 110)

MAGNETIC_OBJECTS = [
    {"name": "Paperclip", "icon": "paperclip", "color": METAL_COLOR, "magnetic": True},
    {"name": "Spoon", "icon": "spoon", "color": METAL_COLOR, "magnetic": True},
    {"name": "Key", "icon": "key", "color": METAL_COLOR, "magnetic": True},
    {"name": "Nail", "icon": "nail", "color": METAL_COLOR, "magnetic": True},
]
NON_MAGNETIC_OBJECTS = [
    {"name": "Feather", "icon": "feather", "color": FEATHER_COLOR, "magnetic": False},
    {"name": "Leaf", "icon": "leaf_item", "color": LEAF_COLOR, "magnetic": False},
    {"name": "Wood Block", "icon": "block", "color": WOOD_COLOR, "magnetic": False},
    {"name": "Rubber Ball", "icon": "ball", "color": BALL_COLOR, "magnetic": False},
]
ALL_OBJECTS = MAGNETIC_OBJECTS + NON_MAGNETIC_OBJECTS


def draw_magnet(surface, center_x, center_y, scale=3.0):
    hub.draw_icon(surface, "magnet", (center_x, center_y), (250, 170, 60), scale=scale)


def draw_object(surface, item, center_x, center_y):
    icon = item["icon"]
    color = item["color"]
    cx, cy = center_x, center_y

    if icon == "paperclip":
        outer = pygame.Rect(0, 0, 26, 56)
        outer.center = (cx, cy)
        pygame.draw.rect(surface, color, outer, width=4, border_radius=13)
        inner = pygame.Rect(0, 0, 14, 38)
        inner.center = (cx, cy - 7)
        pygame.draw.rect(surface, color, inner, width=4, border_radius=7)
    elif icon == "spoon":
        bowl = pygame.Rect(0, 0, 30, 22)
        bowl.center = (cx, cy - 16)
        pygame.draw.ellipse(surface, color, bowl)
        pygame.draw.ellipse(surface, config.NAVY, bowl, width=3)
        handle = pygame.Rect(0, 0, 8, 36)
        handle.center = (cx, cy + 14)
        pygame.draw.rect(surface, color, handle, border_radius=4)
        pygame.draw.rect(surface, config.NAVY, handle, width=2, border_radius=4)
    elif icon == "key":
        pygame.draw.circle(surface, color, (cx, cy - 20), 11)
        pygame.draw.circle(surface, config.NAVY, (cx, cy - 20), 11, width=3)
        pygame.draw.circle(surface, config.GLASS_COLOR, (cx, cy - 20), 5)
        shaft = pygame.Rect(0, 0, 8, 34)
        shaft.center = (cx, cy + 6)
        pygame.draw.rect(surface, color, shaft)
        pygame.draw.rect(surface, config.NAVY, shaft, width=2)
        pygame.draw.rect(surface, color, (cx, cy + 14, 10, 6))
        pygame.draw.rect(surface, color, (cx, cy + 22, 7, 6))
    elif icon == "nail":
        head = pygame.Rect(0, 0, 20, 8)
        head.center = (cx, cy - 26)
        pygame.draw.rect(surface, color, head, border_radius=2)
        pygame.draw.rect(surface, config.NAVY, head, width=2, border_radius=2)
        shaft = pygame.Rect(0, 0, 7, 40)
        shaft.center = (cx, cy - 2)
        pygame.draw.rect(surface, color, shaft)
        pygame.draw.rect(surface, config.NAVY, shaft, width=2)
        pygame.draw.polygon(surface, color, [(cx - 3.5, cy + 18), (cx + 3.5, cy + 18), (cx, cy + 32)])
        pygame.draw.polygon(surface, config.NAVY, [(cx - 3.5, cy + 18), (cx + 3.5, cy + 18), (cx, cy + 32)], width=2)
    elif icon == "feather":
        # A narrow, tapered plume: rounded/fluffy at the top, pointed at
        # the quill tip, slightly fuller on the left than the right.
        pts = [
            (cx, cy - 36), (cx + 7, cy - 24), (cx + 8, cy - 2), (cx + 4, cy + 20),
            (cx, cy + 36),
            (cx - 4, cy + 20), (cx - 10, cy - 2), (cx - 9, cy - 24),
        ]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, config.NAVY, pts, width=3)
        pygame.draw.line(surface, config.NAVY, (cx, cy - 30), (cx, cy + 32), 2)
        for i in range(-2, 3):
            y = cy + i * 11
            pygame.draw.line(surface, config.NAVY, (cx, y), (cx - 7, y - 5), 1)
            pygame.draw.line(surface, config.NAVY, (cx, y), (cx + 6, y - 5), 1)
    elif icon == "leaf_item":
        rect = pygame.Rect(0, 0, 40, 26)
        rect.center = (cx, cy)
        pygame.draw.ellipse(surface, color, rect)
        pygame.draw.ellipse(surface, config.NAVY, rect, width=3)
        pygame.draw.line(surface, config.NAVY, (cx - 16, cy), (cx + 16, cy), 2)
    elif icon == "block":
        rect = pygame.Rect(0, 0, 40, 40)
        rect.center = (cx, cy)
        pygame.draw.rect(surface, color, rect, border_radius=6)
        pygame.draw.rect(surface, config.NAVY, rect, width=3, border_radius=6)
    elif icon == "ball":
        pygame.draw.circle(surface, color, (cx, cy), 20)
        pygame.draw.circle(surface, config.NAVY, (cx, cy), 20, width=3)
        pygame.draw.circle(surface, config.WHITE, (cx - 7, cy - 7), 5)


def draw_progress_dots(surface, rect, progress, target):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, config.PANEL_BG, panel.get_rect(), border_radius=16)
    pygame.draw.rect(panel, config.NAVY, panel.get_rect(), width=4, border_radius=16)
    surface.blit(panel, rect.topleft)

    ui.draw_text_center(surface, "Sort in a row!", (rect.centerx, rect.y + 28), 20)

    spacing = min(34, (rect.width - 40) / max(1, target))
    start_x = rect.centerx - spacing * (target - 1) / 2
    y = rect.y + 68
    for i in range(target):
        x = start_x + i * spacing
        if i < progress:
            pygame.draw.circle(surface, config.GOOD_COLOR, (x, y), 11)
            pygame.draw.circle(surface, config.NAVY, (x, y), 11, width=2)
        else:
            pygame.draw.circle(surface, config.GLASS_COLOR, (x, y), 11)
            pygame.draw.circle(surface, config.NAVY, (x, y), 11, width=2)


def draw_guess_indicator(surface, center_x, center_y, guess):
    if guess is None:
        return
    color = (235, 60, 70) if guess else (60, 120, 235)
    r = 36 + math.sin(pygame.time.get_ticks() * 0.01) * 3
    pygame.draw.circle(surface, color, (int(center_x), int(center_y)), int(r), width=4)
