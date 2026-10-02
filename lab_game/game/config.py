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

# --- Colors --------------------------------------------------------------
WHITE = (255, 255, 255)
BLACK = (20, 20, 25)
BG_TOP = (30, 20, 70)
BG_BOTTOM = (70, 30, 110)
BENCH_COLOR = (120, 80, 60)
GLASS_COLOR = (210, 230, 235)
GLASS_OUTLINE = (255, 255, 255)
PANEL_BG = (40, 30, 80)
TEXT_COLOR = (255, 255, 255)
GOOD_COLOR = (90, 230, 140)
BAD_COLOR = (255, 120, 120)
GO_BUTTON_COLOR = (255, 90, 90)
GO_BUTTON_GLOW = (255, 180, 120)

# One entry per chemical slot. Only the first N (len of a level's bottles)
# are used on screen. Feel free to add more colors/names here.
CHEMICALS = [
    {"name": "Ruby Bubbles", "color": (235, 60, 70)},
    {"name": "Blueberry Fizz", "color": (60, 120, 235)},
    {"name": "Goo Green", "color": (90, 200, 90)},
    {"name": "Sunshine Splash", "color": (250, 210, 60)},
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
GPIO_ENABLED = os.environ.get("LAB_GAME_GPIO", "1") != "0"
GPIO_DROP_PINS = {0: 17, 1: 27, 2: 22, 3: 23}
GPIO_GO_PIN = 24
GPIO_RESET_PIN = 25
GPIO_BOUNCE_TIME = 0.05  # seconds, debounces noisy physical buttons

# --- Misc ---------------------------------------------------------------
HINT_AFTER_FAILURES = 3
