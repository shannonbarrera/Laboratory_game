"""Unifies keyboard, game controller, and Raspberry Pi GPIO buttons into
one small stream of game actions: ("drop", chem_index), ("go",),
("reset",), ("quit",).

The rest of the game never has to know whether a kid pressed the "1" key,
squeezed a button on a USB gamepad, or mashed a big red arcade button
wired to a GPIO pin -- it all turns into the same actions here.
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

            print(f"[input] GPIO buttons armed on pins {config.GPIO_DROP_PINS} "
                  f"(go={config.GPIO_GO_PIN}, reset={config.GPIO_RESET_PIN})")
        except Exception as exc:  # pragma: no cover - real hardware only
            print(f"[input] GPIO setup failed, continuing without it ({exc})")
            self._gpio_buttons = []

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
            if key_name in config.KEYBOARD_DROP_KEYS:
                return ("drop", config.KEYBOARD_DROP_KEYS[key_name])

        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == config.JOYSTICK_GO_BUTTON:
                return ("go",)
            if event.button == config.JOYSTICK_RESET_BUTTON:
                return ("reset",)
            if event.button in config.JOYSTICK_DROP_BUTTONS:
                return ("drop", config.JOYSTICK_DROP_BUTTONS[event.button])

        return None

    def close(self):
        for btn in self._gpio_buttons:
            try:
                btn.close()
            except Exception:
                pass
