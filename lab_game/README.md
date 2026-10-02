# Little Lab: Potion Drops

A kindergarten-friendly "mad scientist" game: colored chemical bottles sit
on a bench, a recipe card shows (with colored dots, no reading required)
how many drops of each color go in the beaker, and pressing the big GO
button triggers a fizzy reaction if the mix is right. Wrong mixes just
gently reset -- there's no losing, only trying again.

Built with Python + [pygame](https://www.pygame.org/), runs on a
Raspberry Pi (tested design target: Pi 4 / Pi 5, should also run fine on
a Pi Zero 2 W), and can be played with a keyboard, a USB/Bluetooth game
controller, or real push-buttons wired to the Pi's GPIO pins.

## How to play

- Each chemical bottle has its own button. Pressing it squeezes one drop
  into the beaker (with a plop sound and a little splash of bubbles).
- The **Recipe** card in the top-right shows colored dots: that's how
  many drops of each color to add.
- Press the big red **GO!** button when the beaker looks right.
  - Correct → a celebration (confetti, chime, "Great job, scientist!")
    and the next level loads automatically.
  - Not quite → a friendly "Oops! Let's try again" and the beaker empties
    so the child can try again immediately.
- Miss the same level a few times in a row and small arrows will start
  gently pointing at which bottle needs more (▲) or fewer (▼) drops.

## Controls

| Action | Keyboard | Game controller | GPIO (Pi button) |
| --- | --- | --- | --- |
| Drop red chemical | `1` | button 0 | BCM 17 -- **red** button |
| Drop blue chemical | `2` | button 1 | BCM 27 -- **blue** button |
| Drop green chemical | `3` | button 2 | BCM 22 -- **green** button |
| Drop yellow chemical | `4` | button 3 | BCM 23 -- **yellow** button |
| GO! | `space` | button 4 | BCM 24 -- **white** button |
| Reset beaker | `r` | button 5 | BCM 25 -- **black** button |
| Quit | `esc` | -- | -- |

This matches a colored 6-button pack wired left to right as red, blue,
green, yellow, white, black -- each color button always controls the
chemical of the same color, since `game/config.py`'s `CHEMICALS` list and
`GPIO_DROP_PINS` are both ordered red/blue/green/yellow. A leftover grey
button isn't wired to anything by default; see **Using the spare grey
button** below if you'd like to give it a job.

All three input methods work at the same time, so you can test with a
keyboard before wiring anything up. Edit `game/config.py` to change any
of these mappings (for example if your controller numbers its buttons
differently -- see **Finding your controller's button numbers** below).

## Running it

```bash
cd lab_game
python3 -m venv .venv   # optional but recommended
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Useful environment variables:

- `LAB_GAME_FULLSCREEN=1` -- launch fullscreen (good for the final kiosk
  setup; leave unset while you're testing on a laptop). By default this
  auto-detects your screen's resolution and scales the artwork to fill
  it, so there's usually nothing else to configure.
- `LAB_GAME_WIDTH` / `LAB_GAME_HEIGHT` -- picks a window size while
  testing on a laptop (defaults to 1024x600). **If fullscreen still
  doesn't fill your screen correctly** -- some small HDMI panels report
  the wrong resolution to the Pi -- set both of these to your screen's
  real pixel size to force it, e.g. for the 800x480 official Pi
  touchscreen:
  ```bash
  LAB_GAME_FULLSCREEN=1 LAB_GAME_WIDTH=800 LAB_GAME_HEIGHT=480 python3 main.py
  ```
  Not sure what your screen's real resolution is? Run `fbset -s` (shows
  the framebuffer's current mode) or check **Screen Configuration** in
  the Raspberry Pi OS desktop menu.
- `LAB_GAME_GPIO=0` -- turn off GPIO entirely (handy when testing on a
  laptop that prints gpiozero warnings; it's already auto-skipped if no
  GPIO hardware is found, this just silences it).

### Making your fullscreen settings stick

Once you've found the `LAB_GAME_WIDTH`/`LAB_GAME_HEIGHT` values that make
it fit your screen correctly, you don't want to retype that whole command
every time. Two options, depending on what you want:

- **Just don't want to retype the command**: edit the two numbers at the
  top of `run.sh` to match what worked for you, then from now on run:
  ```bash
  ./run.sh
  ```
- **Want it to launch automatically when the Pi boots**, with no command
  at all: see **Auto-start on boot (kiosk mode)** below -- the systemd
  service already has the same two settings built in (commented out by
  default), you just need to uncomment and fill them in.

## Setting up on a Raspberry Pi

1. Flash Raspberry Pi OS (with desktop) and boot it, or use an existing
   one.
2. Install system packages pygame needs for audio/video:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv libsdl2-mixer-2.0-0 \
       libsdl2-image-2.0-0 libsdl2-2.0-0
   ```
3. Copy this `lab_game/` folder onto the Pi (e.g. `git clone`, or `scp`).
4. `cd lab_game && pip install -r requirements.txt` (a venv is fine too).
5. Test it: `python3 main.py`. You should see the game window; try the
   number keys + space on a keyboard first.

### Wiring physical push-buttons (GPIO)

This matches a 6-color momentary push-button pack wired left to right as
**red, blue, green, yellow, white, black** -- each colored button always
controls the chemical of the same color (red button -> red chemical,
etc.), white is GO, and black is Reset. A leftover grey button is left
unwired by default (see **Using the spare grey button** below).

For each button: connect one leg to the Raspberry Pi's **GND** pin, and
the other leg to the GPIO pin listed in the controls table above. That's
it -- no resistors needed, because the game configures each pin with its
internal pull-up resistor (`gpiozero.Button`, active-low). Any physical
GND pin on the 40-pin header works; buttons don't need to share a single
GND pin unless that's more convenient to wire.

```
Raspberry Pi GPIO header (just the pins we use):

   3V3  (1) (2)  5V
 GPIO2  (3) (4)  5V
 GPIO3  (5) (6)  GND -------+---- one leg of every button
 GPIO4  (7) (8)  GPIO14     |
    GND (9)(10)  GPIO15     |
GPIO17 (11)(12)  GPIO18     |
GPIO27 (13)(14)  GND -------+
GPIO22 (15)(16)  GPIO23
   3V3 (17)(18)  GPIO24
  ...
GPIO17 -> red drop button      (other leg -> GND)
GPIO27 -> blue drop button     (other leg -> GND)
GPIO22 -> green drop button    (other leg -> GND)
GPIO23 -> yellow drop button   (other leg -> GND)
GPIO24 -> GO button            (other leg -> GND)
GPIO25 -> reset button         (other leg -> GND)
```

If you'd rather use different pins (e.g. your button box or HAT fixes
specific pins), just change `GPIO_DROP_PINS`, `GPIO_GO_PIN`, and
`GPIO_RESET_PIN` in `game/config.py`.

#### Using the spare grey button

Nothing in the game needs a 7th button, so grey is left unwired on
purpose rather than given a job it doesn't need. If you'd like to use it
anyway, pick a pin (e.g. BCM 26), wire it the same way as the others
(button leg -> GPIO 26, other leg -> GND), and add a couple of lines to
`game/input_manager.py`'s `_init_gpio` to fire whatever action you want
-- a natural choice would be a "skip this level" button for a frustrating
level, or a secret grown-up-only quit button tucked somewhere a
kindergartner won't bump into it.

### Using a game controller instead

Any USB or Bluetooth gamepad pygame recognizes will work out of the box
-- just plug it in (or pair it via `bluetoothctl`) before launching the
game. By default, face buttons 0-3 add drops and button 4 is GO.

**Finding your controller's button numbers:** run this from `lab_game/`
with the controller plugged in, then press each button and note the
number that's printed, and update `JOYSTICK_DROP_BUTTONS` /
`JOYSTICK_GO_BUTTON` / `JOYSTICK_RESET_BUTTON` in `game/config.py` to
match:

```bash
python3 -c "
import pygame; pygame.init(); pygame.joystick.init()
js = pygame.joystick.Joystick(0); js.init()
print('Found:', js.get_name())
while True:
    for e in pygame.event.get():
        if e.type == pygame.JOYBUTTONDOWN:
            print('button', e.button, 'pressed')
"
```

### Auto-start on boot (kiosk mode)

So the Pi boots straight into the game, a systemd service is included in
`systemd/lab-game.service`. Edit the `User=`, `WorkingDirectory=`, and
`ExecStart=` paths in that file to match where you copied `lab_game/`. If
you needed `LAB_GAME_WIDTH`/`LAB_GAME_HEIGHT` to get fullscreen fitting
your screen correctly (see above), also uncomment and fill in those two
`Environment=` lines in the same file. Then:

```bash
sudo cp systemd/lab-game.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now lab-game.service
```

It's set to restart automatically if the game ever crashes, and to wait
for the graphical desktop to be ready first.

## Customizing it for your kid

- **Levels / recipes**: `game/levels.py` has the first dozen levels
  spelled out explicitly (one new idea introduced at a time), then makes
  up new ones forever after that. Add, remove, or reorder entries freely
  -- `recipe` just maps a chemical index to how many drops are needed.
- **Colors & names**: `game/config.py`'s `CHEMICALS` list.
- **Difficulty pacing**: `MAX_DROPS_PER_CHEMICAL`, `MAX_TOTAL_DROPS`, and
  `HINT_AFTER_FAILURES` in `game/config.py`.
- **Sounds**: all synthesized in code in `game/sound.py` (no audio files
  to manage) -- tweak pitches/durations there.

## Project layout

```
lab_game/
  main.py              entry point
  requirements.txt
  systemd/lab-game.service
  game/
    config.py           colors, control mappings, difficulty knobs
    input_manager.py    keyboard + controller + GPIO -> unified actions
    chemical.py         bottle animation state
    beaker.py           drop counts, color blending, fill animation
    particles.py        bubbles / confetti effects
    levels.py           level/recipe definitions + endless generator
    sound.py            synthesized sound effects (no audio files)
    ui.py               all drawing code
    app.py              the game state machine (playing/success/fail)
```
