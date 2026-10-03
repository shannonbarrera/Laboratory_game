"""The Magnet Lab's state machine: GUESSING -> SUCCESS -> (next level) or
GUESSING -> FAIL -> (reset streak, keep going). Same forgiving shape as
the other rooms, but a different kind of challenge: instead of counting
or sequencing, the player classifies real objects ("does it stick to a
magnet or not?") using real-world knowledge rather than a visual recipe
that spells out the answer.

Red = "yes, it's magnetic;" blue = "no, it isn't" -- picking a guess,
then GO tests it against the truth. A streak of correct-in-a-row guesses
(the level's target, which grows over time) triggers the big success
celebration; a single wrong guess resets the streak but, true to the
rest of the game, never ends the room or loses real progress.
"""
import random

import pygame

from . import config, magnet_levels, magnet_ui, ui
from .particles import ParticleSystem

SUCCESS_HOLD = 2.4
FAIL_HOLD = 1.6

MAGNET_X = 422
MAGNET_Y = 420
ITEM_X = 422
ITEM_Y = 230


class MagnetGame:
    def __init__(self, screen, input_manager, sound_bank):
        self.screen = screen
        self.canvas = pygame.Surface((config.CANVAS_WIDTH, config.CANVAS_HEIGHT))
        self.input = input_manager
        self.sound = sound_bank
        self.particles = ParticleSystem()

        self.level_number = 1
        self.streak = 0
        self.state = "guessing"
        self.state_timer = 0.0
        self.message = ""
        self.message_color = config.GOOD_COLOR

        self.target = 0
        self.progress = 0
        self.current_item = None
        self.guess = None
        self._load_level(self.level_number)

    # -- level setup ---------------------------------------------------
    def _load_level(self, number):
        self.target = magnet_levels.get_target(number)
        self.progress = 0
        self._load_next_item()

    def _load_next_item(self):
        self.current_item = random.choice(magnet_ui.ALL_OBJECTS)
        self.guess = None

    # -- per-frame API, driven by World's main loop -----------------------
    def handle_actions(self, actions):
        for action in actions:
            kind = action[0]
            if kind == "drop" and self.state == "guessing":
                if action[1] == 0:
                    self.guess = True
                    self.sound.play("drop_0")
                elif action[1] == 1:
                    self.guess = False
                    self.sound.play("drop_1")
            elif kind == "go" and self.state == "guessing":
                self._on_go()
            elif kind == "reset" and self.state == "guessing":
                self.guess = None
                self.sound.play("reset")

    def _on_go(self):
        if self.guess is None:
            self.sound.play("full")
            return

        correct = self.guess == self.current_item["magnetic"]
        if not correct:
            self._trigger_fail()
            return

        self.progress += 1
        if self.current_item["magnetic"]:
            self.sound.play("cling")
        else:
            self.sound.play("drop_2")
        self.particles.spawn_bubble(ITEM_X, ITEM_Y, self.current_item["color"])

        if self.progress >= self.target:
            self.state = "success"
            self.state_timer = SUCCESS_HOLD
            self.streak += 1
            self.message = "Perfect sorting! Great job, scientist!"
            self.message_color = config.GOOD_COLOR
            self.particles.spawn_celebration(MAGNET_X, MAGNET_Y - 40,
                                              [(250, 170, 60), config.GOOD_COLOR, config.WHITE])
            self.sound.play("success")
        else:
            self._load_next_item()

    def _trigger_fail(self):
        self.state = "fail"
        self.state_timer = FAIL_HOLD
        self.progress = 0
        self.streak = 0
        verb = "sticks" if self.current_item["magnetic"] else "doesn't stick"
        self.message = f"Oops! A {self.current_item['name'].lower()} {verb}!"
        self.message_color = config.BAD_COLOR
        self.sound.play("fail")
        self.particles.spawn_fizzle(ITEM_X, ITEM_Y, magnet_ui.METAL_COLOR)

    def update(self, dt):
        self.particles.update(dt)

        if self.state == "fail":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self._load_next_item()
                self.state = "guessing"
        elif self.state == "success":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.level_number += 1
                self._load_level(self.level_number)
                self.state = "guessing"

    def draw(self):
        ui.draw_background(self.canvas)

        magnet_ui.draw_magnet(self.canvas, MAGNET_X, MAGNET_Y)

        bob = pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() * 0.1).x * 6
        item_y = ITEM_Y + bob
        if self.current_item is not None:
            magnet_ui.draw_object(self.canvas, self.current_item, ITEM_X, item_y)
            magnet_ui.draw_guess_indicator(self.canvas, ITEM_X, item_y, self.guess)

        progress_rect = pygame.Rect(config.CANVAS_WIDTH - 230, 70, 200, 110)
        magnet_ui.draw_progress_dots(self.canvas, progress_rect, self.progress, self.target)

        go_rect = pygame.Rect(0, 0, 90, 90)
        go_rect.center = (config.CANVAS_WIDTH - 130, 390)
        pulse = 0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(
            pygame.time.get_ticks() * 0.2).x
        ui.draw_go_button(self.canvas, go_rect, pulse)

        ui.draw_hud(self.canvas, self.level_number, self.streak)
        ui.draw_text_center(self.canvas, "grey button: back to hallway",
                             (160, config.CANVAS_HEIGHT - 14), 14, bold=False)
        ui.draw_text_center(self.canvas, "red: it sticks!   blue: nope!",
                             (650, config.CANVAS_HEIGHT - 14), 14, bold=False)

        self.particles.draw(self.canvas)

        if self.state in ("success", "fail"):
            ui.draw_message_banner(self.canvas, self.message, self.message_color)

        scaled = pygame.transform.smoothscale(self.canvas, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))
