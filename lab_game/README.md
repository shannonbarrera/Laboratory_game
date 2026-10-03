# Little Lab: Potion Drops

A kindergarten-friendly "mad scientist" game. The player walks their
little scientist around a building with a joystick, and each room is a
different kind of lab:

- **Chemistry Lab**: colored chemical bottles sit on a bench, a recipe
  card shows (with colored dots, no reading required) how many drops of
  each color go in the beaker, and pressing the big GO button triggers a
  fizzy reaction if the mix is right.
- **Bug & Plant Lab**: grow a plant by pressing the water and sun buttons
  the number of times the recipe card shows, then GO to see if it
  blooms. Too much or too little of either and it wilts instead --
  same idea as the chemistry room, but now two things have to each be
  right, not just one. Starting a few levels in, ladybugs occasionally
  wander onto the plant and start nibbling it; the green button shoos
  them away.
- **Space Lab**: press the four color buttons in the exact order the
  "Launch Code" card shows, then GO to launch the rocket. A different
  idea than the other two rooms: order matters here, not just counts --
  one wrong button and the code resets, same as a real launch sequence.
- **Magnet Lab**: an object appears -- guess whether it's magnetic (red)
  or not (blue), then GO to test it. Get a streak of guesses right in a
  row to complete the level. Unlike the other rooms, there's no on-screen
  recipe that spells out the right answer -- it's real-world knowledge
  (metal sticks, wood/plastic/feathers don't), and a wrong guess tells you
  the right answer so it doubles as a little lesson.

All four are forgiving by design: a mistake just gently resets -- there's
no losing, only trying again. Every room in the building is a real
mini-game now; see **Adding a new lab room** below if you want to build
a fifth.

Built with Python + [pygame](https://www.pygame.org/), runs on a
Raspberry Pi (tested design target: Pi 4 / Pi 5, should also run fine on
a Pi Zero 2 W), and can be played with a keyboard, a USB/Bluetooth game
controller, real push-buttons wired to the Pi's GPIO pins, or an analog
joystick relayed through an Arduino or ESP32 (see **Using an analog
joystick (via Arduino/ESP32)** below).

## How to play

- **Walking around**: push a joystick's analog stick or d-pad (or arrow
  keys/WASD on a keyboard) to walk your scientist between rooms. Walk
  into a room's archway to go in -- no button needed.
- **Leaving a room**: the grey button (or Backspace on a keyboard) always
  takes you back out to the hallway, from any room.
- **In the Chemistry Lab**: each chemical bottle has its own button.
  Pressing it squeezes one drop into the beaker (with a plop sound and a
  little splash of bubbles). The **Recipe** card in the top-right shows
  colored dots: that's how many drops of each color to add. Press the
  big red **GO!** button when the beaker looks right.
  - Correct → a celebration (confetti, chime, "Great job, scientist!")
    and the next level loads automatically.
  - Not quite → a friendly "Oops! Let's try again" and the beaker empties
    so the child can try again immediately.
  - Miss the same level a few times in a row and small arrows will start
    gently pointing at which bottle needs more (▲) or fewer (▼) drops.
- **In the Bug & Plant Lab**: the blue button waters the plant, the
  yellow button gives it sun -- each press adds one to that resource,
  with the plant visibly growing a little taller and leafier as you go.
  The **Recipe** card shows how many of each (blue dots for water,
  yellow for sun). Press **GO!** when you think it's right.
  - Correct → the plant blooms into a flower with a confetti burst and
    "It bloomed! Great job, gardener!", then the next level loads.
  - Not quite → the plant gently droops and browns, a friendly "Oops!
    Let's try again," and it resets so the child can try again.
  - Same hint arrows as the Chemistry Lab kick in after repeated misses.
  - From level 4 onward, a ladybug occasionally wanders in and starts
    nibbling the plant. Press the **green** button to shoo it away for a
    happy little chime. Ignore it and it takes one gentle "bite" -- one
    water or sun press' worth -- then leaves on its own; nothing is ever
    lost for good, it just might mean pressing water or sun again before
    GO.
- **In the Space Lab**: the **Launch Code** card shows a row of colored
  dots in order -- press the matching color buttons in that exact
  sequence. Each correct press checks off that step; the rocket glows
  once the whole code is entered correctly. Press **GO!** to launch.
  - Correct order, then GO → the rocket blasts off in a burst of flame
    and confetti, "Blast off! Great job, astronaut!", then the next
    (usually longer) sequence loads.
  - Wrong button at any point → an immediate, quick reset back to the
    start of the sequence -- no long pause, just try again right away.
  - Pressing GO before finishing the code also resets it, with a "Finish
    the launch code first!" reminder.
- **In the Magnet Lab**: an object (paperclip, spoon, key, nail, feather,
  leaf, wood block, rubber ball...) appears above the magnet. Press
  **red** if you think it'll stick, **blue** if you think it won't, then
  **GO!** to test it.
  - Correct → a satisfying "cling!" (if it stuck) or a soft pop (if it
    didn't), and the next object appears. Get enough right in a row (the
    "Sort in a row!" card shows how many) to finish the level with a big
    celebration.
  - Wrong → a quick, friendly correction ("Oops! A nail sticks!") and the
    streak starts over, but the level itself is never lost.

## Controls

| Action | Keyboard | Game controller | GPIO (Pi button) |
| --- | --- | --- | --- |
| Walk around the hub | arrow keys / WASD | analog stick / d-pad | -- (joystick/keyboard only) |
| Drop red chemical | `1` | button 0 | BCM 17 -- **red** button |
| Drop blue chemical | `2` | button 1 | BCM 27 -- **blue** button |
| Drop green chemical | `3` | button 2 | BCM 22 -- **green** button |
| Drop yellow chemical | `4` | button 3 | BCM 23 -- **yellow** button |
| GO! | `space` | button 4 | BCM 24 -- **white** button |
| Reset beaker | `r` | button 5 | BCM 25 -- **black** button |
| Back to hallway | `backspace` | button 6 | BCM 26 -- **grey** button |
| Quit | `esc` | -- | -- |

This matches a colored 7-button pack wired left to right as red, blue,
green, yellow, white, black, grey -- each color button always controls
the chemical of the same color, since `game/config.py`'s `CHEMICALS`
list and `GPIO_DROP_PINS` are both ordered red/blue/green/yellow.

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

This matches a 7-color momentary push-button pack wired left to right as
**red, blue, green, yellow, white, black, grey** -- each colored button
always controls the chemical of the same color (red button -> red
chemical, etc.), white is GO, black is Reset, and grey leaves whatever
room you're in and returns to the hallway.

Walking around the hallway itself is joystick/keyboard-only (an analog
stick or d-pad, or arrow keys/WASD) -- there's no GPIO wiring for that,
since continuous movement doesn't map onto simple push-buttons the way a
single "add one drop" press does.

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
GPIO26 -> back button          (other leg -> GND)
```

If you'd rather use different pins (e.g. your button box or HAT fixes
specific pins), just change `GPIO_DROP_PINS`, `GPIO_GO_PIN`,
`GPIO_RESET_PIN`, or `GPIO_BACK_PIN` in `game/config.py`.

### Using a game controller instead

Any USB or Bluetooth gamepad pygame recognizes will work out of the box
-- just plug it in (or pair it via `bluetoothctl`) before launching the
game. The left analog stick or d-pad walks around the hub; by default,
face buttons 0-3 add drops, button 4 is GO, button 5 is Reset, and
button 6 is Back.

**Finding your controller's button numbers:** run this from `lab_game/`
with the controller plugged in, then press each button and note the
number that's printed, and update `JOYSTICK_DROP_BUTTONS` /
`JOYSTICK_GO_BUTTON` / `JOYSTICK_RESET_BUTTON` / `JOYSTICK_BACK_BUTTON`
in `game/config.py` to match:

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

### Using an analog joystick (via Arduino/ESP32)

A classic analog joystick breakout board (labeled GND, +5V, VRx, VRy,
SW -- the kind with two round dials and a center click button, often
sold under names like "Xinda" or just "KY-023") can't be wired to the
Pi's GPIO pins directly: VRx and VRy are analog voltages, and GPIO pins
can only read digital on/off signals. If you have a spare Arduino
(Uno/Nano/Mega/etc.) or ESP32, it can act as the translator, since both
have a built-in analog-to-digital converter the Pi doesn't.

**1. Wire the joystick to the Arduino/ESP32** (not the Pi):

| Joystick pin | Goes to |
| --- | --- |
| GND | board GND |
| +5V | board 5V (or 3V3 on a 3.3V-only board -- these modules work fine down to 3.3V) |
| VRx | board A0 |
| VRy | board A1 |
| SW | board pin 2 |

**2. Flash the sketch**: open `arduino/joystick_bridge/joystick_bridge.ino`
in the Arduino IDE, select your board under **Tools → Board**, and
upload. It works unmodified on both AVR Arduinos and ESP32 boards.

> **Arduino Nano note**: if you get an upload error like "programmer is
> not responding," try **Tools → Processor → "ATmega328P (Old
> Bootloader)"** -- common on Nano clones.

**3. Plug it into the Pi via USB cable.** That's it for wiring -- the
sketch just prints readings over the same USB cable used to power/flash
it; there's no separate connection to the Pi's GPIO pins at all.

**4. Install pyserial and run the game** (already in `requirements.txt`):

```bash
pip install -r requirements.txt
python3 main.py
```

You should see `[input] Arduino/ESP32 joystick bridge found on /dev/ttyACM0`
(or `/dev/ttyUSB0`) printed at startup. If it instead says it couldn't
find one, double check the board actually uploaded successfully (its
onboard LED usually blinks right after upload) and that no other program
(like the Arduino IDE's Serial Monitor) is already holding the port open.

If you have more than one USB-serial device plugged in and it picks the
wrong one, force a specific port:

```bash
LAB_GAME_SERIAL_PORT=/dev/ttyACM0 python3 main.py
```

The joystick's own click button (SW) is already wired to the same
"back to hallway" action as the grey GPIO button and Backspace key, so
clicking the stick in also leaves a room -- no extra wiring needed for
that.

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

- **Chemistry levels / recipes**: `game/levels.py` has the first dozen
  levels spelled out explicitly (one new idea introduced at a time), then
  makes up new ones forever after that. Add, remove, or reorder entries
  freely -- `recipe` just maps a chemical index to how many drops are
  needed.
- **Garden levels / recipes**: `game/garden_levels.py`, same shape --
  hand-built levels first, then an endless generator. Each level is just
  `{"water": n, "sun": m}`.
- **Space launch sequences**: `game/space_levels.py`, same shape again --
  each level is just a list of color indices, e.g. `[0, 3, 2, 1]` for
  red-yellow-green-blue in that order.
- **Magnet Lab streak targets**: `game/magnet_levels.py` -- a level here
  is just how many correct guesses in a row are needed. The objects
  themselves are `game/magnet_ui.py`'s `MAGNETIC_OBJECTS` /
  `NON_MAGNETIC_OBJECTS` lists -- add your own by giving it a name, a
  color, whether it's magnetic, and either reusing an existing `icon`
  key or adding a new drawing case to `draw_object()`.
- **Colors & names**: `game/config.py`'s `CHEMICALS` list for the
  Chemistry Lab and (reused directly) the Space Lab's launch code;
  `WATER_COLOR`/`SUN_COLOR` etc. at the top of `game/garden_ui.py` for the
  Bug & Plant Lab.
- **Difficulty pacing**: `MAX_DROPS_PER_CHEMICAL`, `MAX_TOTAL_DROPS`, and
  `HINT_AFTER_FAILURES` in `game/config.py` for Chemistry;
  `MAX_PER_RESOURCE` in `game/garden_levels.py` for the garden;
  `MAX_LENGTH` in `game/space_levels.py` for how long sequences can get;
  `MAX_TARGET` in `game/magnet_levels.py` for the longest required streak.
- **Bugs**: `BUGS_START_LEVEL`, `BUG_WARN_TIME`, `BUG_LIFESPAN`,
  `BUG_SPAWN_MIN`/`BUG_SPAWN_MAX` at the top of `game/garden.py` -- e.g.
  raise `BUGS_START_LEVEL` to delay them further, or widen the spawn
  range to make them rarer.
- **Sounds**: all synthesized in code in `game/sound.py` (no audio files
  to manage) -- tweak pitches/durations there.
- **The hub building**: room names, colors, positions, and icons are all
  in the `ROOMS` list in `game/hub.py`. Walking speed is
  `HUB_MOVE_SPEED` in `game/config.py`.

### Adding a new lab room

Every room in the building is a real mini-game now, but the hub was
built so a new one is a clean addition, not a rewrite -- a placeholder
room shows a "coming soon" sign and nothing else until it's wired up,
so the building can grow without every mini-game needing to exist up
front. `game/garden.py` (Bug & Plant Lab), `game/space.py` (Space Lab),
and `game/magnet.py` (Magnet Lab) are three complete, working examples
to read end to end before making a fourth -- between them they show
three very different mechanics (two independent targets, an ordered
sequence, and a classification quiz with no visual recipe at all) built
on the exact same pattern. That pattern:

1. Write a class the same shape as `game/app.py`'s `Game` (or
   `GardenGame`/`SpaceGame`/`MagnetGame`): takes `(screen, input_manager,
   sound_bank)` and exposes `handle_actions(actions)`, `update(dt)`, and
   `draw()`. It's free to reinterpret the same color-button presses
   differently than other rooms do -- `GardenGame` treats the
   blue/yellow buttons as "water"/"sun", `SpaceGame` treats all four as
   ordered launch-code steps, `MagnetGame` treats red/blue as "yes"/"no"
   -- since the physical button a player presses always means the same
   color, not the same fixed action.
2. In `game/world.py`, add a new room by first creating it in `hub.py`'s
   `ROOMS` list (with `"ready": False` while you build it), then add an
   instance of your class to the `self.rooms` dict in `World.__init__`
   (keyed by that room's `id`).
3. Flip `"ready"` to `True` once it's working -- `World` already routes
   to any room id present in `self.rooms` automatically.

## Project layout

```
lab_game/
  main.py              entry point
  run.sh                launcher with fullscreen size baked in
  requirements.txt
  systemd/lab-game.service
  arduino/
    joystick_bridge/joystick_bridge.ino   relays an analog joystick to the
                                           Pi over USB serial (Arduino/ESP32)
  game/
    config.py           colors, control mappings, difficulty knobs
    input_manager.py    keyboard + controller + GPIO + serial joystick ->
                         unified actions, plus continuous movement for
                         walking the hub
    serial_joystick.py  reads the Arduino/ESP32 joystick bridge over USB
    world.py            top-level orchestrator: hub vs. each room's game
                         vs. a "coming soon" placeholder room
    hub.py              the building: rooms, walls, the walking player
    particles.py        bubbles / confetti effects (shared by all rooms)
    sound.py            synthesized sound effects (no audio files)
    chemical.py         bottle animation state (Chemistry Lab)
    beaker.py           drop counts, color blending, fill animation (Chemistry Lab)
    levels.py           Chemistry Lab level/recipe definitions + endless generator
    ui.py               Chemistry Lab drawing code
    app.py              Chemistry Lab's state machine (playing/success/fail)
    garden_levels.py    Bug & Plant Lab level/recipe definitions + endless generator
    garden_ui.py        Bug & Plant Lab drawing code (pot, growing plant, water/sun)
    garden.py           Bug & Plant Lab's state machine (growing/success/fail)
    space_levels.py     Space Lab launch-sequence definitions + endless generator
    space_ui.py         Space Lab drawing code (rocket, launchpad, sequence card)
    space.py            Space Lab's state machine (ready/success/fail)
    magnet_levels.py    Magnet Lab streak-target definitions + endless generator
    magnet_ui.py        Magnet Lab drawing code (objects, magnet, progress dots)
    magnet.py           Magnet Lab's state machine (guessing/success/fail)
```
