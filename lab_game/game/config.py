"""All tunable constants live here so the game is easy to re-shape for a
different Pi screen, different buttons, or a different kid's taste."""
import os

# --- Display -----------------------------------------------------------
# Everything is drawn onto a fixed logical canvas, then scaled to whatever
# the real screen size is. That way the same code looks right on a tiny
# 800x480 official Pi touchscreen or a full HDMI monitor.
CANVAS_WIDTH = 1024
CANVAS_HEIGHT = 600
FPS = 30

FULLSCREEN = os.environ.get("LAB_GAME_FULLSCREEN", "0") == "1"
WINDOW_WIDTH = int(os.environ.get("LAB_GAME_WIDTH", CANVAS_WIDTH))
WINDOW_HEIGHT = int(os.environ.get("LAB_GAME_HEIGHT", CANVAS_HEIGHT))
# Whether LAB_GAME_WIDTH/HEIGHT were explicitly set, vs. just defaulted.
# In fullscreen, main.py normally asks SDL to auto-detect the screen size,
# but some Pi + display combos report the wrong size (e.g. a small HDMI
# panel that doesn't report its real resolution). Setting both of these
# env vars forces that exact size instead of trusting auto-detection.
SIZE_OVERRIDDEN = "LAB_GAME_WIDTH" in os.environ and "LAB_GAME_HEIGHT" in os.environ

# --- Colors --------------------------------------------------------------
# A bright, clean "science classroom" palette: bold navy outlines and flat
# saturated colors, like classroom clip-art beakers, instead of a dim
# moody background -- it reads more like a lab and less like a potion den.
WHITE = (255, 255, 255)
BLACK = (20, 20, 25)
NAVY = (36, 42, 94)
BG_TOP = (214, 240, 255)
BG_BOTTOM = (179, 222, 250)
BENCH_COLOR = (223, 229, 235)
BENCH_EDGE = (169, 181, 194)
GLASS_COLOR = (240, 248, 252)
GLASS_OUTLINE = NAVY
PANEL_BG = (255, 255, 255)
TEXT_COLOR = NAVY
GOOD_COLOR = (70, 200, 120)
BAD_COLOR = (235, 90, 90)
GO_BUTTON_COLOR = (255, 90, 90)
GO_BUTTON_GLOW = (255, 180, 120)

# One entry per chemical slot. Only the first N (len of a level's bottles)
# are used on screen. Order matters: it's index-matched to every control
# mapping below (KEYBOARD_DROP_KEYS, JOYSTICK_DROP_BUTTONS,
# GPIO_DROP_PINS), so chemical 0 is always whatever button/pin is
# assigned to slot 0, etc. This order (red, blue, green, yellow) is
# meant to match a physical button pack wired left to right in that
# same order.
CHEMICALS = [
    {"name": "Ruby Bubbles", "color": (235, 60, 70)},       # 0: red button
    {"name": "Blueberry Fizz", "color": (60, 120, 235)},    # 1: blue button
    {"name": "Goo Green", "color": (90, 200, 90)},          # 2: green button
    {"name": "Sunshine Splash", "color": (250, 210, 60)},   # 3: yellow button
]

MAX_DROPS_PER_CHEMICAL = 6
MAX_TOTAL_DROPS = 12

# --- Controls --------------------------------------------------------------
# Keyboard: number keys add a drop of that chemical; space is the big GO
# button; r resets the beaker; escape quits.
KEYBOARD_DROP_KEYS = {
    "1": 0,
    "2": 1,
    "3": 2,
    "4": 3,
}
KEYBOARD_GO_KEY = "space"
KEYBOARD_RESET_KEY = "r"
KEYBOARD_QUIT_KEY = "escape"

# Joystick / gamepad: face buttons 0-3 add drops, button 4 (or whatever your
# pad calls its "start"/"A" button) triggers GO. Change these to match
# whatever controller you actually plug in -- run `jstest` or look at
# game/input_manager.py's debug logging to find the right numbers.
JOYSTICK_DROP_BUTTONS = {0: 0, 1: 1, 2: 2, 3: 3}
JOYSTICK_GO_BUTTON = 4
JOYSTICK_RESET_BUTTON = 5

# Raspberry Pi GPIO buttons (BCM numbering). Wire each button between the
# pin and GND; gpiozero's internal pull-up means you do NOT need an
# external resistor for a simple push button. This is only used when
# gpiozero + real GPIO hardware are available; otherwise it's silently
# skipped so the game still runs fine from a keyboard on a laptop.
#
# Matches a 6-button colored pack wired left to right as:
#   red, blue, green, yellow, white, black   (grey left spare/unused)
GPIO_ENABLED = os.environ.get("LAB_GAME_GPIO", "1") != "0"
GPIO_DROP_PINS = {
    0: 17,  # red button    -> chemical 0 (Ruby Bubbles)
    1: 27,  # blue button   -> chemical 1 (Blueberry Fizz)
    2: 22,  # green button  -> chemical 2 (Goo Green)
    3: 23,  # yellow button -> chemical 3 (Sunshine Splash)
}
GPIO_GO_PIN = 24     # white button -> GO / mix
GPIO_RESET_PIN = 25  # black button -> reset the beaker
GPIO_BOUNCE_TIME = 0.05  # seconds, debounces noisy physical buttons

# --- Misc ---------------------------------------------------------------
HINT_AFTER_FAILURES = 3
