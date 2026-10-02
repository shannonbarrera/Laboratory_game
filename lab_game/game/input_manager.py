"""Unifies keyboard, game controller, and Raspberry Pi GPIO buttons into
one small stream of game actions: ("drop", chem_index), ("go",),
("reset",), ("back",), ("quit",).

The rest of the game never has to know whether a kid pressed the "1" key,
squeezed a button on a USB gamepad, or mashed a big red arcade button
wired to a GPIO pin -- it all turns into the same actions here.

Walking around the hub building needs continuous movement, not a single
press, so that's handled separately by get_move_vector() instead of
going through the one-shot action queue.
"""
import queue

import pygame

from . import config


class InputManager:
    def __init__(self):
        self._queue = queue.Queue()
        self._joysticks = {}
        self._gpio_buttons = []
        self._init_joysticks()
        self._init_gpio()

    # -- setup ------------------------------------------------------------
    def _init_joysticks(self):
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            try:
                js = pygame.joystick.Joystick(i)
                js.init()
                self._joysticks[js.get_instance_id()] = js
                print(f"[input] Found controller: {js.get_name()}")
            except pygame.error as exc:
                print(f"[input] Could not init joystick {i}: {exc}")

    def _init_gpio(self):
        if not config.GPIO_ENABLED:
            return
        try:
            from gpiozero import Button
        except Exception as exc:  # pragma: no cover - not on this hardware
            print(f"[input] GPIO not available, skipping physical buttons ({exc})")
            return

        try:
            for idx, pin in config.GPIO_DROP_PINS.items():
                btn = Button(pin, bounce_time=config.GPIO_BOUNCE_TIME)
                btn.when_pressed = lambda idx=idx: self._queue.put(("drop", idx))
                self._gpio_buttons.append(btn)

            go_btn = Button(config.GPIO_GO_PIN, bounce_time=config.GPIO_BOUNCE_TIME)
            go_btn.when_pressed = lambda: self._queue.put(("go",))
            self._gpio_buttons.append(go_btn)

            reset_btn = Button(config.GPIO_RESET_PIN, bounce_time=config.GPIO_BOUNCE_TIME)
            reset_btn.when_pressed = lambda: self._queue.put(("reset",))
            self._gpio_buttons.append(reset_btn)

            back_btn = Button(config.GPIO_BACK_PIN, bounce_time=config.GPIO_BOUNCE_TIME)
            back_btn.when_pressed = lambda: self._queue.put(("back",))
            self._gpio_buttons.append(back_btn)

            print(f"[input] GPIO buttons armed on pins {config.GPIO_DROP_PINS} "
                  f"(go={config.GPIO_GO_PIN}, reset={config.GPIO_RESET_PIN}, "
                  f"back={config.GPIO_BACK_PIN})")
        except Exception as exc:  # pragma: no cover - real hardware only
            print(f"[input] GPIO setup failed, continuing without it ({exc})")
            self._gpio_buttons = []

    # -- continuous movement ------------------------------------------------
    def get_move_vector(self):
        """Returns a (dx, dy) movement vector for walking around the hub,
        each in roughly [-1, 1]. Combines held arrow/WASD keys with any
        connected joystick's analog stick and d-pad (hat), since this
        needs to be read every frame rather than as one-shot events."""
        dx = dy = 0.0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1.0

        for js in self._joysticks.values():
            if js.get_numaxes() >= 2:
                ax, ay = js.get_axis(0), js.get_axis(1)
                if abs(ax) > config.JOYSTICK_AXIS_DEADZONE:
                    dx += ax
                if abs(ay) > config.JOYSTICK_AXIS_DEADZONE:
                    dy += ay
            if js.get_numhats() >= 1:
                hx, hy = js.get_hat(0)
                dx += hx
                dy -= hy  # hat's y-axis is 1 = up, opposite of screen y

        magnitude = (dx * dx + dy * dy) ** 0.5
        if magnitude > 1.0:
            dx /= magnitude
            dy /= magnitude
        return dx, dy

    # -- per-frame polling --------------------------------------------------
    def poll(self):
        """Returns a list of actions gathered since the last call."""
        actions = []

        for event in pygame.event.get():
            action = self._translate_pygame_event(event)
            if action:
                actions.append(action)

        while True:
            try:
                actions.append(self._queue.get_nowait())
            except queue.Empty:
                break

        return actions

    def _translate_pygame_event(self, event):
        if event.type == pygame.QUIT:
            return ("quit",)

        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            if key_name == config.KEYBOARD_QUIT_KEY:
                return ("quit",)
            if key_name == config.KEYBOARD_GO_KEY:
                return ("go",)
            if key_name == config.KEYBOARD_RESET_KEY:
                return ("reset",)
            if key_name == config.KEYBOARD_BACK_KEY:
                return ("back",)
            if key_name in config.KEYBOARD_DROP_KEYS:
                return ("drop", config.KEYBOARD_DROP_KEYS[key_name])

        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == config.JOYSTICK_GO_BUTTON:
                return ("go",)
            if event.button == config.JOYSTICK_RESET_BUTTON:
                return ("reset",)
            if event.button == config.JOYSTICK_BACK_BUTTON:
                return ("back",)
            if event.button in config.JOYSTICK_DROP_BUTTONS:
                return ("drop", config.JOYSTICK_DROP_BUTTONS[event.button])

        return None

    def close(self):
        for btn in self._gpio_buttons:
            try:
                btn.close()
            except Exception:
                pass
