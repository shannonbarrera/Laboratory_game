"""The hub: a little building the player walks around in with a
joystick (or keyboard/WASD for testing), with one room per mini-game.
Walking into a room enters it; the "back" action leaves it.

The whole building fits on screen at once -- no camera/scrolling needed
-- laid out as a furnished central lobby with a narrow hallway running
out to each of the four rooms, like a real small building rather than
rooms just taped directly onto the lobby.
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
        "rect": pygame.Rect(362, 450, 300, 140),
        "open_side": "top",
        "icon": "flask",
        "ready": True,
    },
    {
        "id": "biology",
        "name": "Bug & Plant Lab",
        "color": (210, 238, 210),
        "accent": (90, 200, 90),
        "rect": pygame.Rect(52, 220, 260, 160),
        "open_side": "right",
        "icon": "leaf",
        "ready": True,
    },
    {
        "id": "space",
        "name": "Space Lab",
        "color": (208, 218, 248),
        "accent": (60, 120, 235),
        "rect": pygame.Rect(362, 10, 300, 140),
        "open_side": "bottom",
        "icon": "star",
        "ready": True,
    },
    {
        "id": "physics",
        "name": "Magnet Lab",
        "color": (250, 236, 198),
        "accent": (250, 170, 60),
        "rect": pygame.Rect(712, 220, 260, 160),
        "open_side": "left",
        "icon": "magnet",
        "ready": True,
    },
]

LOBBY_RECT = pygame.Rect(372, 210, 280, 180)
LOBBY_COLOR = (233, 236, 240)

HALLWAY_COLOR = LOBBY_COLOR
# Each hallway is a corridor rect connecting the lobby to one room, plus
# which two (opposite) sides are open -- the ends that connect to the
# lobby and the room -- with walls drawn down its other two long sides.
HALLWAYS = [
    {"rect": pygame.Rect(477, 150, 70, 60), "gap_sides": ("top", "bottom")},
    {"rect": pygame.Rect(477, 390, 70, 60), "gap_sides": ("top", "bottom")},
    {"rect": pygame.Rect(312, 265, 60, 70), "gap_sides": ("left", "right")},
    {"rect": pygame.Rect(652, 265, 60, 70), "gap_sides": ("left", "right")},
]

# Where to stand the player just inside the hallway after leaving a room,
# so they don't immediately re-trigger walking back into it, and so they
# visibly step out into the corridor rather than teleporting past it.
_LOBBY_ENTRY_POINTS = {
    "chemistry": (512, 420),
    "biology": (342, 300),
    "space": (512, 180),
    "physics": (682, 300),
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


def _inset_for_walls(rect, open_sides, radius):
    """Shrinks a shape's rect by the player's radius on every side that
    has an actual wall, but NOT on side(s) that open onto a hallway or
    room -- insetting those too would carve out a dead zone exactly at
    every doorway, where the player could get stuck unable to walk
    through. This is a deliberately loose approximation (it doesn't
    model the solid wall segments that flank a narrower doorway in a
    wider wall) rather than exact doorway-width collision, which is
    plenty precise for a top-down kids' game."""
    left = rect.left + (0 if "left" in open_sides else radius)
    right = rect.right - (0 if "right" in open_sides else radius)
    top = rect.top + (0 if "top" in open_sides else radius)
    bottom = rect.bottom - (0 if "bottom" in open_sides else radius)
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
        # The lobby has a doorway gap on all four walls (one per
        # hallway), so for this same loose approximation it never needs
        # insetting either.
        rects = [LOBBY_RECT]
        rects += [_inset_for_walls(h["rect"], h["gap_sides"], radius) for h in HALLWAYS]
        rects += [_inset_for_walls(room["rect"], (room["open_side"],), radius) for room in ROOMS]
        _inset_cache[radius] = rects
    return _inset_cache[radius]


class HubWorld:
    def __init__(self):
        self.player = Player(LOBBY_RECT.centerx, LOBBY_RECT.centery)

    def update(self, move_vector, dt):
        """Moves the player and returns a room id the player just walked
        into, or None if they're still wandering the hallways/lobby."""
        dx, dy = move_vector
        self.player.update(dx, dy, dt)
        return _room_for_point(self.player.x, self.player.y)

    def leave_room(self, room_id):
        self.player.place_outside(room_id)

    def draw(self, surface):
        ui.draw_background(surface)

        pygame.draw.rect(surface, LOBBY_COLOR, LOBBY_RECT)
        lobby_gaps = {"top": (477, 547), "bottom": (477, 547),
                      "left": (265, 335), "right": (265, 335)}
        _draw_walls_with_gaps(surface, LOBBY_RECT, lobby_gaps)
        _draw_lobby_furniture(surface)

        for hallway in HALLWAYS:
            pygame.draw.rect(surface, HALLWAY_COLOR, hallway["rect"])
            gaps = {side: None for side in hallway["gap_sides"]}
            _draw_walls_with_gaps(surface, hallway["rect"], gaps)

        for room in ROOMS:
            pygame.draw.rect(surface, room["color"], room["rect"])
            doorway_gap = _doorway_gap(room["rect"], room["open_side"])
            _draw_walls_with_gaps(surface, room["rect"], {room["open_side"]: doorway_gap})
            _draw_room_icon(surface, room)
            # The label sits just inside the room's top edge -- simpler
            # and safer than positioning it outside the room (in the
            # canvas margin), which risks running off-screen now that
            # hallways eat into how much margin each room actually has.
            title_y = room["rect"].y + 24
            ui.draw_text_center(surface, room["name"], (room["rect"].centerx, title_y), 22)
            if not room["ready"]:
                ui.draw_text_center(surface, "(coming soon)",
                                     (room["rect"].centerx, title_y + 22), 14,
                                     color=config.NAVY, bold=False)

        _draw_player(surface, self.player)


def _doorway_gap(rect, side):
    """The 70px-wide doorway centered on a room's wall, matching the
    hallway it connects to."""
    if side in ("top", "bottom"):
        return (rect.centerx - 35, rect.centerx + 35)
    return (rect.centery - 35, rect.centery + 35)


def _draw_walls_with_gaps(surface, rect, gaps):
    """Draws navy wall lines around a rect's four sides. `gaps` maps a
    side name to either None (that whole side is open, no wall at all)
    or a (start, end) range along that side to leave open, drawing wall
    segment(s) for whatever's left. A side simply absent from `gaps` is
    drawn as one unbroken wall."""
    sides = {
        "top": ("h", rect.top, rect.left, rect.right),
        "bottom": ("h", rect.bottom, rect.left, rect.right),
        "left": ("v", rect.left, rect.top, rect.bottom),
        "right": ("v", rect.right, rect.top, rect.bottom),
    }
    for side, (orient, fixed, lo, hi) in sides.items():
        gap = gaps.get(side, "closed")
        if gap is None:
            continue
        segments = []
        if gap == "closed":
            segments.append((lo, hi))
        else:
            g0, g1 = gap
            if g0 > lo:
                segments.append((lo, g0))
            if g1 < hi:
                segments.append((g1, hi))
        for s0, s1 in segments:
            start = (s0, fixed) if orient == "h" else (fixed, s0)
            end = (s1, fixed) if orient == "h" else (fixed, s1)
            pygame.draw.line(surface, config.NAVY, start, end, 5)


COUCH_COLOR = (90, 150, 160)
PLANT_POT_COLOR = (190, 110, 70)
PLANT_LEAF_COLOR = (90, 180, 100)


def _draw_lobby_furniture(surface):
    """A couch and a couple of potted plants, tucked into the lobby's
    corners so they never block a doorway (each doorway is centered on
    its wall, leaving the corners clear)."""
    _draw_couch(surface, LOBBY_RECT.left + 55, LOBBY_RECT.top + 35)
    _draw_potted_plant(surface, LOBBY_RECT.right - 30, LOBBY_RECT.top + 30)
    _draw_potted_plant(surface, LOBBY_RECT.right - 30, LOBBY_RECT.bottom - 30)


def _draw_couch(surface, x, y):
    back_rect = pygame.Rect(0, 0, 70, 20)
    back_rect.midtop = (x, y)
    pygame.draw.rect(surface, COUCH_COLOR, back_rect, border_radius=6)
    pygame.draw.rect(surface, config.NAVY, back_rect, width=2, border_radius=6)

    seat_rect = pygame.Rect(0, 0, 76, 24)
    seat_rect.midtop = (x, y + 14)
    pygame.draw.rect(surface, COUCH_COLOR, seat_rect, border_radius=6)
    pygame.draw.rect(surface, config.NAVY, seat_rect, width=2, border_radius=6)
    for i in (-1, 0, 1):
        cx = x + i * 22
        pygame.draw.line(surface, config.NAVY, (cx, seat_rect.top + 3), (cx, seat_rect.bottom - 3), 1)

    for side in (-1, 1):
        leg = pygame.Rect(0, 0, 4, 6)
        leg.midtop = (x + side * 32, seat_rect.bottom - 2)
        pygame.draw.rect(surface, config.NAVY, leg)


def _draw_potted_plant(surface, x, y):
    pot = pygame.Rect(0, 0, 22, 16)
    pot.midtop = (x, y + 14)
    pygame.draw.rect(surface, PLANT_POT_COLOR, pot, border_radius=2)
    pygame.draw.rect(surface, config.NAVY, pot, width=2, border_radius=2)

    for angle_deg, length in ((200, 16), (160, 16), (270, 18), (320, 16), (90, 20)):
        angle = math.radians(angle_deg)
        tip = (x + length * math.cos(angle), y + 14 - length * math.sin(angle))
        pygame.draw.line(surface, PLANT_LEAF_COLOR, (x, y + 10), tip, 4)


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


PLAYER_SKIN = (250, 210, 170)
PLAYER_HAIR = (240, 120, 30)
PLAYER_COAT = (248, 250, 252)
PLAYER_SHOE = (70, 75, 90)


def _draw_player(surface, player):
    """A little scientist in a lab coat: orange mohawk, round glasses, a
    walk cycle (legs and arms swing oppositely, torso bobs) driven by
    Player.bob, which only advances while actually moving -- so he's
    only animated when walking, not while standing still."""
    bob = math.sin(player.bob) * 2.5
    step = math.sin(player.bob * 2)
    fx = int(player.x)
    fy = int(player.y + bob)  # feet/collision anchor; body extends upward

    leg_w, leg_h = 7, 13
    for side, phase in ((-1, step), (1, -step)):
        leg_rect = pygame.Rect(0, 0, leg_w, leg_h)
        leg_rect.midbottom = (fx + side * 6, fy + int(phase * 3))
        pygame.draw.rect(surface, PLAYER_SHOE, leg_rect, border_radius=3)

    torso_w = 30
    torso_h = 30
    torso_rect = pygame.Rect(0, 0, torso_w, torso_h)
    torso_rect.midbottom = (fx, fy - leg_h + 4)
    pygame.draw.rect(surface, PLAYER_COAT, torso_rect, border_radius=10)
    pygame.draw.rect(surface, config.NAVY, torso_rect, width=3, border_radius=10)
    pygame.draw.line(surface, config.NAVY,
                      (fx, torso_rect.top + 6), (fx, torso_rect.bottom - 4), 2)
    for i in range(2):
        pygame.draw.circle(surface, config.NAVY, (fx, torso_rect.top + 13 + i * 9), 2)

    arm_w, arm_h = 8, 22
    for side, phase in ((-1, -step), (1, step)):
        arm_rect = pygame.Rect(0, 0, arm_w, arm_h)
        arm_rect.midtop = (fx + side * (torso_w // 2 + 2), torso_rect.top + 4 + int(phase * 3))
        pygame.draw.rect(surface, PLAYER_COAT, arm_rect, border_radius=4)
        pygame.draw.rect(surface, config.NAVY, arm_rect, width=2, border_radius=4)
        pygame.draw.circle(surface, PLAYER_SKIN, arm_rect.midbottom, 4)

    head_r = 11
    head_x, head_y = fx, torso_rect.top - head_r + 2

    pygame.draw.circle(surface, PLAYER_SKIN, (head_x, head_y), head_r)
    pygame.draw.circle(surface, config.NAVY, (head_x, head_y), head_r, width=2)

    # An orange mohawk: a narrow row of spikes running down the center of
    # the head, with bare skin showing at the sides (no hair elsewhere).
    for dx in (-5, 0, 5):
        tip = (head_x + dx, head_y - head_r - 11)
        pygame.draw.polygon(surface, PLAYER_HAIR, [
            (head_x + dx - 3, head_y - head_r + 3),
            (head_x + dx + 3, head_y - head_r + 3),
            tip,
        ])
        pygame.draw.polygon(surface, config.NAVY, [
            (head_x + dx - 3, head_y - head_r + 3),
            (head_x + dx + 3, head_y - head_r + 3),
            tip,
        ], width=1)

    gx, gy = head_x, head_y + 1
    pygame.draw.circle(surface, config.NAVY, (gx - 5, gy), 4, width=2)
    pygame.draw.circle(surface, config.NAVY, (gx + 5, gy), 4, width=2)
    pygame.draw.line(surface, config.NAVY, (gx - 1, gy), (gx + 1, gy), 2)

    pygame.draw.arc(surface, config.NAVY, (gx - 4, gy + 2, 8, 6), math.pi, 2 * math.pi, 2)
