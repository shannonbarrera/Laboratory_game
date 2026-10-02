"""The Bug & Plant Lab's state machine: GROWING -> SUCCESS -> (next
level) or GROWING -> FAIL -> (reset, try again). Same forgiving shape as
the Chemistry Lab's game/app.py -- no "game over", just gentle retries --
but introduces a new idea: water and sun each have their own target, so
getting one right doesn't mean you're done.

Reuses the bench's two color buttons that make the most sense for this
room (blue -> water, yellow -> sun) rather than inventing new physical
controls: button colors always mean the same chemical/resource identity
on the bench, just reinterpreted per room.
"""
import pygame

from . import config, garden_levels, garden_ui, ui
from .chemical import Bottle
from .particles import ParticleSystem

SUCCESS_HOLD = 2.4
FAIL_HOLD = 1.6

WATER_DROP_INDEX = 1  # the blue button
SUN_DROP_INDEX = 3  # the yellow button

POT_CENTER_X = 422
POT_TOP_Y = 275
WATER_X = 241
SUN_X = 603
SOURCE_BASE_Y = 450


class GardenGame:
    def __init__(self, screen, input_manager, sound_bank):
        self.screen = screen
        self.canvas = pygame.Surface((config.CANVAS_WIDTH, config.CANVAS_HEIGHT))
        self.input = input_manager
        self.sound = sound_bank
        self.particles = ParticleSystem()

        self.level_number = 1
        self.streak = 0
        self.fail_count = 0
        self.state = "growing"
        self.state_timer = 0.0
        self.message = ""
        self.message_color = config.GOOD_COLOR

        self.water_source = Bottle(0, "Water", garden_ui.WATER_COLOR)
        self.sun_source = Bottle(0, "Sun", garden_ui.SUN_COLOR)
        self.plant_bloom = 0.0
        self.plant_wilt = 0.0

        self.water_count = 0
        self.sun_count = 0
        self._load_level(self.level_number)

    # -- level setup ---------------------------------------------------
    def _load_level(self, number):
        self.recipe = garden_levels.get_level(number)
        self.water_count = 0
        self.sun_count = 0
        self.fail_count = 0

    # -- per-frame API, driven by World's main loop -----------------------
    def handle_actions(self, actions):
        for action in actions:
            kind = action[0]
            if kind == "drop" and self.state == "growing":
                if action[1] == WATER_DROP_INDEX:
                    self._on_water()
                elif action[1] == SUN_DROP_INDEX:
                    self._on_sun()
            elif kind == "go" and self.state == "growing":
                self._on_go()
            elif kind == "reset" and self.state == "growing":
                self.water_count = 0
                self.sun_count = 0
                self.sound.play("reset")

    def _on_water(self):
        self.water_source.trigger()
        if self.water_count < garden_levels.MAX_PER_RESOURCE:
            self.water_count += 1
            self.sound.play("drop_1")
            self.particles.spawn_bubble(WATER_X, SOURCE_BASE_Y - 100, garden_ui.WATER_COLOR)
        else:
            self.sound.play("full")
            self.particles.spawn_fizzle(WATER_X, SOURCE_BASE_Y - 100, garden_ui.WATER_COLOR)

    def _on_sun(self):
        self.sun_source.trigger()
        if self.sun_count < garden_levels.MAX_PER_RESOURCE:
            self.sun_count += 1
            self.sound.play("drop_3")
            self.particles.spawn_bubble(SUN_X, SOURCE_BASE_Y - 100, garden_ui.SUN_COLOR)
        else:
            self.sound.play("full")
            self.particles.spawn_fizzle(SUN_X, SOURCE_BASE_Y - 100, garden_ui.SUN_COLOR)

    def _on_go(self):
        self.sound.play("go")
        if self.water_count == self.recipe["water"] and self.sun_count == self.recipe["sun"]:
            self.state = "success"
            self.state_timer = SUCCESS_HOLD
            self.streak += 1
            self.message = "It bloomed! Great job, gardener!"
            self.message_color = config.GOOD_COLOR
            self.particles.spawn_celebration(
                POT_CENTER_X, POT_TOP_Y - 120,
                [garden_ui.PETAL_COLOR, garden_ui.SUN_COLOR, garden_ui.LEAF_COLOR],
            )
            self.sound.play("success")
        else:
            self.state = "fail"
            self.state_timer = FAIL_HOLD
            self.fail_count += 1
            self.streak = 0
            self.message = "Oops! Let's try again."
            self.message_color = config.BAD_COLOR
            self.particles.spawn_fizzle(POT_CENTER_X, POT_TOP_Y - 60, garden_ui.WILT_COLOR)
            self.sound.play("fail")

    def update(self, dt):
        self.water_source.update(dt)
        self.sun_source.update(dt)
        self.particles.update(dt)

        target_bloom = 1.0 if self.state == "success" else 0.0
        self.plant_bloom += (target_bloom - self.plant_bloom) * min(1.0, dt * 4)
        target_wilt = 1.0 if self.state == "fail" else 0.0
        self.plant_wilt += (target_wilt - self.plant_wilt) * min(1.0, dt * 4)

        if self.state in ("success", "fail"):
            self.state_timer -= dt
            if self.state_timer <= 0:
                if self.state == "success":
                    self.level_number += 1
                    self._load_level(self.level_number)
                else:
                    self.water_count = 0
                    self.sun_count = 0
                self.state = "growing"

    def _show_hint(self):
        return self.state == "growing" and self.fail_count >= config.HINT_AFTER_FAILURES

    def draw(self):
        ui.draw_background(self.canvas)

        garden_ui.draw_water_source(self.canvas, self.water_source, WATER_X, SOURCE_BASE_Y,
                                     self.water_count)
        garden_ui.draw_sun_source(self.canvas, self.sun_source, SUN_X, SOURCE_BASE_Y,
                                   self.sun_count)

        if self._show_hint():
            if self.water_count != self.recipe["water"]:
                ui.draw_hint_arrow(self.canvas, WATER_X, SOURCE_BASE_Y,
                                    too_many=self.water_count > self.recipe["water"])
            if self.sun_count != self.recipe["sun"]:
                ui.draw_hint_arrow(self.canvas, SUN_X, SOURCE_BASE_Y,
                                    too_many=self.sun_count > self.recipe["sun"])

        total_presses = self.water_count + self.sun_count
        garden_ui.draw_pot_and_plant(self.canvas, POT_CENTER_X, POT_TOP_Y, total_presses,
                                      self.plant_bloom, self.plant_wilt)

        recipe_rect = pygame.Rect(config.CANVAS_WIDTH - 230, 70, 200, 60 + 34 * 2)
        fake_chemicals = {0: {"color": garden_ui.WATER_COLOR}, 1: {"color": garden_ui.SUN_COLOR}}
        fake_recipe = {0: self.recipe["water"], 1: self.recipe["sun"]}
        ui.draw_recipe_card(self.canvas, recipe_rect, fake_chemicals, fake_recipe)

        go_rect = pygame.Rect(0, 0, 90, 90)
        go_rect.center = (config.CANVAS_WIDTH - 130, 390)
        pulse = 0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(
            pygame.time.get_ticks() * 0.2).x
        ui.draw_go_button(self.canvas, go_rect, pulse)

        ui.draw_hud(self.canvas, self.level_number, self.streak)
        ui.draw_text_center(self.canvas, "grey button: back to hallway",
                             (160, config.CANVAS_HEIGHT - 14), 14, bold=False)

        self.particles.draw(self.canvas)

        if self.state in ("success", "fail"):
            ui.draw_message_banner(self.canvas, self.message, self.message_color)

        scaled = pygame.transform.smoothscale(self.canvas, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))
