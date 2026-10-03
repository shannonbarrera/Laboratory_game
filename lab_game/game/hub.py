"""The hub: a little building the player walks around in with a
joystick (or keyboard/WASD for testing), with one room per mini-game.
Walking into a room's archway enters it; the "back" action leaves it.

The whole building fits on screen at once -- no camera/scrolling needed
-- laid out as a central lobby with one room attached on each side. Each
room shares a full open edge with the lobby (a wide, kid-easy archway)
and has walls drawn on its other three sides.
"""
import math

import pygame

from . import config, ui

ROOMS = [
    {
        "id": "chemistry",
        "name": "Chemistry Lab",
        "color": (248, 205, 205),
        "accent": (235, 60, 70),
        "rect": pygame.Rect(362, 380, 300, 170),
        "open_side": "top",
        "icon": "flask",
        "ready": True,
    },
    {
        "id": "biology",
        "name": "Bug & Plant Lab",
        "color": (210, 238, 210),
        "accent": (90, 200, 90),
        "rect": pygame.Rect(102, 220, 260, 160),
        "open_side": "right",
        "icon": "leaf",
        "ready": True,
    },
    {
        "id": "space",
        "name": "Space Lab",
        "color": (208, 218, 248),
        "accent": (60, 120, 235),
        "rect": pygame.Rect(362, 50, 300, 170),
        "open_side": "bottom",
        "icon": "star",
        "ready": True,
    },
    {
        "id": "physics",
        "name": "Magnet Lab",
        "color": (250, 236, 198),
        "accent": (250, 170, 60),
        "rect": pygame.Rect(662, 220, 260, 160),
        "open_side": "left",
        "icon": "magnet",
        "ready": False,
    },
]

LOBBY_RECT = pygame.Rect(362, 220, 300, 160)
LOBBY_COLOR = (233, 236, 240)

# Where to stand the player just inside the lobby after leaving a room,
# so they don't immediately re-trigger walking back into it.
_LOBBY_ENTRY_POINTS = {
    "chemistry": (512, 372),
    "biology": (370, 300),
    "space": (512, 228),
    "physics": (654, 300),
}

ROOMS_BY_ID = {room["id"]: room for room in ROOMS}


def _room_for_point(x, y):
    for room in ROOMS:
        if room["rect"].collidepoint(x, y):
            return room["id"]
    return None


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.facing = (0, 1)
        self.bob = 0.0

    def place_outside(self, room_id):
        x, y = _LOBBY_ENTRY_POINTS.get(room_id, (512, 300))
        self.x, self.y = x, y

    def update(self, dx, dy, dt):
        moving = abs(dx) > 0.01 or abs(dy) > 0.01
        if moving:
            self.facing = (dx, dy)
            self.bob += dt * 10
        speed = config.HUB_MOVE_SPEED
        r = config.PLAYER_RADIUS

        new_x = self.x + dx * speed * dt
        if _point_walkable(new_x, self.y, r):
            self.x = new_x
        new_y = self.y + dy * speed * dt
        if _point_walkable(self.x, new_y, r):
            self.y = new_y


def _inset_for_walls(rect, open_side, radius):
    """Shrinks a room's rect by the player's radius on every side that has
    an actual wall, but NOT on the archway side shared with the lobby --
    insetting that side too would carve out a dead zone exactly at every
    doorway, where the player could get stuck unable to walk through."""
    left = rect.left + (0 if open_side == "left" else radius)
    right = rect.right - (0 if open_side == "right" else radius)
    top = rect.top + (0 if open_side == "top" else radius)
    bottom = rect.bottom - (0 if open_side == "bottom" else radius)
    if right <= left or bottom <= top:
        return rect.copy()
    return pygame.Rect(left, top, right - left, bottom - top)


def _point_walkable(x, y, radius):
    for rect in _WALKABLE_INSET_RECTS(radius):
        if rect.collidepoint(x, y):
            return True
    return False


_inset_cache = {}


def _WALKABLE_INSET_RECTS(radius):
    if radius not in _inset_cache:
        # The lobby has no walls at all -- every side opens onto a room --
        # so it never needs insetting.
        rects = [LOBBY_RECT]
        rects += [_inset_for_walls(room["rect"], room["open_side"], radius) for room in ROOMS]
        _inset_cache[radius] = rects
    return _inset_cache[radius]


class HubWorld:
    def __init__(self):
        self.player = Player(LOBBY_RECT.centerx, LOBBY_RECT.centery)

    def update(self, move_vector, dt):
        """Moves the player and returns a room id the player just walked
        into, or None if they're still wandering the hallway/lobby."""
        dx, dy = move_vector
        self.player.update(dx, dy, dt)
        return _room_for_point(self.player.x, self.player.y)

    def leave_room(self, room_id):
        self.player.place_outside(room_id)

    def draw(self, surface):
        ui.draw_background(surface)
        pygame.draw.rect(surface, LOBBY_COLOR, LOBBY_RECT)

        for room in ROOMS:
            pygame.draw.rect(surface, room["color"], room["rect"])
            _draw_room_walls(surface, room["rect"], room["open_side"])
            _draw_room_icon(surface, room)
            # Keep the label on whichever side doesn't have the archway.
            # When the label sits above the room, the subtitle has to be
            # the line nearer the room (with the title further up) so
            # reading order stays title-then-subtitle while both still
            # clear the room's top wall.
            below = room["open_side"] == "top"
            if below:
                title_y = room["rect"].bottom + 18
                subtitle_y = title_y + 20
            else:
                subtitle_y = room["rect"].y - 14
                title_y = subtitle_y - 20
            ui.draw_text_center(surface, room["name"], (room["rect"].centerx, title_y), 22)
            if not room["ready"]:
                ui.draw_text_center(surface, "(coming soon)",
                                     (room["rect"].centerx, subtitle_y), 14,
                                     color=config.NAVY, bold=False)

        _draw_player(surface, self.player)


def _draw_room_walls(surface, rect, open_side):
    sides = {
        "top": (rect.topleft, rect.topright),
        "bottom": (rect.bottomleft, rect.bottomright),
        "left": (rect.topleft, rect.bottomleft),
        "right": (rect.topright, rect.bottomright),
    }
    for side, (start, end) in sides.items():
        if side == open_side:
            continue
        pygame.draw.line(surface, config.NAVY, start, end, 5)


def _draw_room_icon(surface, room):
    draw_icon(surface, room["icon"], room["rect"].center, room["accent"])


def draw_icon(surface, icon, center, color, scale=1.0):
    """Draws one of the room icons at an arbitrary point/size -- used both
    for the small icons inside each hub room and for the bigger one shown
    on a "coming soon" room's full-screen placeholder."""
    cx, cy = center
    s = scale
    line_w = max(1, round(3 * s))

    if icon == "flask":
        poly = [(cx - 10 * s, cy - 18 * s), (cx + 10 * s, cy - 18 * s),
                 (cx + 22 * s, cy + 18 * s), (cx - 22 * s, cy + 18 * s)]
        pygame.draw.polygon(surface, config.GLASS_COLOR, poly)
        pygame.draw.polygon(surface, color, [(cx - 16 * s, cy + 18 * s), (cx + 16 * s, cy + 18 * s),
                                              (cx + 8 * s, cy), (cx - 8 * s, cy)])
        pygame.draw.polygon(surface, config.NAVY, poly, width=line_w)
    elif icon == "leaf":
        rect = (cx - 20 * s, cy - 14 * s, 40 * s, 28 * s)
        pygame.draw.ellipse(surface, color, rect)
        pygame.draw.ellipse(surface, config.NAVY, rect, width=line_w)
        pygame.draw.line(surface, config.NAVY, (cx - 16 * s, cy), (cx + 16 * s, cy), max(1, round(2 * s)))
    elif icon == "star":
        points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            radius = (20 if i % 2 == 0 else 9) * s
            points.append((cx + radius * math.cos(angle), cy - radius * math.sin(angle)))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, config.NAVY, points, width=line_w)
    elif icon == "magnet":
        # A horseshoe magnet: a U-shaped arc with two prongs sticking up,
        # red and blue tips like a real toy magnet.
        rect = pygame.Rect(cx - 16 * s, cy - 16 * s, 32 * s, 32 * s)
        pygame.draw.arc(surface, color, rect, math.pi, 2 * math.pi, max(2, round(10 * s)))
        prong_w, prong_h = 10 * s, 16 * s
        left_prong = (cx - 16 * s, cy - 16 * s, prong_w, prong_h)
        right_prong = (cx + 6 * s, cy - 16 * s, prong_w, prong_h)
        pygame.draw.rect(surface, (235, 60, 70), left_prong)
        pygame.draw.rect(surface, (60, 120, 235), right_prong)
        pygame.draw.rect(surface, config.NAVY, left_prong, width=max(1, round(2 * s)))
        pygame.draw.rect(surface, config.NAVY, right_prong, width=max(1, round(2 * s)))


def _draw_player(surface, player):
    bob = math.sin(player.bob) * 2
    x, y = int(player.x), int(player.y + bob)
    r = config.PLAYER_RADIUS

    pygame.draw.circle(surface, (240, 248, 252), (x, y), r)
    pygame.draw.circle(surface, config.NAVY, (x, y), r, width=3)

    # Little goggles, offset toward whichever way they're facing.
    fx, fy = player.facing
    offset_x = 4 if fx >= 0 else -4
    pygame.draw.circle(surface, config.NAVY, (x - 6 + offset_x // 2, y - 2), 4, width=2)
    pygame.draw.circle(surface, config.NAVY, (x + 6 + offset_x // 2, y - 2), 4, width=2)
