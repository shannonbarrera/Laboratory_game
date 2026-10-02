"""The game's state machine: PLAYING -> SUCCESS -> (next level) or
PLAYING -> FAIL -> (reset, try again). Kept deliberately forgiving --
there is no "game over", just gentle retries, because the audience is a
kindergartner who should feel like a scientist, not like they failed a
test.
"""
import pygame

from . import config, levels, ui
from .beaker import Beaker
from .chemical import Bottle
from .input_manager import InputManager
from .particles import ParticleSystem
from .sound import SoundBank

SUCCESS_HOLD = 2.2
FAIL_HOLD = 1.4


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.canvas = pygame.Surface((config.CANVAS_WIDTH, config.CANVAS_HEIGHT))
        self.clock = pygame.time.Clock()
        self.input = InputManager()
        self.sound = SoundBank()
        self.particles = ParticleSystem()

        self.running = True
        self.level_number = 1
        self.streak = 0
        self.fail_count = 0
        self.state = "playing"
        self.state_timer = 0.0
        self.message = ""
        self.message_color = config.GOOD_COLOR

        self.bottles = {}
        self.beaker = Beaker()
        self.bottle_positions = {}
        self._load_level(self.level_number)

    # -- level setup ---------------------------------------------------
    def _load_level(self, number):
        level = levels.get_level(number)
        self.recipe = level["recipe"]
        self.active_bottle_order = level["bottles"]
        self.beaker.reset()
        self.fail_count = 0

        self.bottles = {}
        for idx in self.active_bottle_order:
            info = config.CHEMICALS[idx]
            self.bottles[idx] = Bottle(idx, info["name"], info["color"])

        self._layout_bottles()

    def _layout_bottles(self):
        n = len(self.active_bottle_order)
        bench_top = config.CANVAS_HEIGHT - 150
        base_y = bench_top  # bottles stand with their base right on the bench surface
        usable_w = config.CANVAS_WIDTH - 300  # leave the right-hand column for the recipe card + GO button
        start_x = 60
        spacing = usable_w / max(1, n)
        self.bottle_positions = {}
        for i, idx in enumerate(self.active_bottle_order):
            x = start_x + spacing * (i + 0.5)
            self.bottle_positions[idx] = (int(x), base_y)

    # -- main loop -------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            actions = self.input.poll()
            self._handle_actions(actions)
            self._update(dt)
            self._draw()
            pygame.display.flip()
        self.input.close()

    def _handle_actions(self, actions):
        for action in actions:
            kind = action[0]
            if kind == "quit":
                self.running = False
            elif kind == "drop" and self.state == "playing":
                self._on_drop(action[1])
            elif kind == "go" and self.state == "playing":
                self._on_go()
            elif kind == "reset" and self.state == "playing":
                self.beaker.reset()
                self.sound.play("reset")

    def _on_drop(self, chem_index):
        if chem_index not in self.bottles:
            return
        bottle = self.bottles[chem_index]
        added = self.beaker.add_drop(chem_index)
        bottle.trigger()
        x, y = self.bottle_positions[chem_index]
        if added:
            self.particles.spawn_bubble(x, y - 40, bottle.color)
            self.sound.play(f"drop_{chem_index % 4}")
        else:
            self.particles.spawn_fizzle(x, y - 40, bottle.color)
            self.sound.play("full")

    def _on_go(self):
        self.sound.play("go")
        if self.beaker.matches(self.recipe):
            self.state = "success"
            self.state_timer = SUCCESS_HOLD
            self.streak += 1
            self.message = "Great job, scientist!"
            self.message_color = config.GOOD_COLOR
            cx = config.CANVAS_WIDTH // 2
            cy = config.CANVAS_HEIGHT - 260
            colors = [b.color for b in self.bottles.values()]
            self.particles.spawn_celebration(cx, cy, colors)
            self.sound.play("success")
        else:
            self.state = "fail"
            self.state_timer = FAIL_HOLD
            self.fail_count += 1
            self.streak = 0
            self.message = "Oops! Let's try again."
            self.message_color = config.BAD_COLOR
            self.sound.play("fail")

    def _update(self, dt):
        for bottle in self.bottles.values():
            bottle.update(dt)
        self.beaker.update(dt)
        self.particles.update(dt)

        if self.state in ("success", "fail"):
            self.state_timer -= dt
            if self.state_timer <= 0:
                if self.state == "success":
                    self.level_number += 1
                    self._load_level(self.level_number)
                else:
                    self.beaker.reset()
                self.state = "playing"

    def _show_hint(self):
        return self.state == "playing" and self.fail_count >= config.HINT_AFTER_FAILURES

    def _draw(self):
        ui.draw_background(self.canvas)

        for idx, bottle in self.bottles.items():
            x, y = self.bottle_positions[idx]
            count = self.beaker.counts.get(idx, 0)
            ui.draw_bottle(self.canvas, bottle, x, y, count)
            if self._show_hint():
                target = self.recipe.get(idx, 0)
                if count != target:
                    ui.draw_hint_arrow(self.canvas, x, y, too_many=count > target)

        beaker_rect = pygame.Rect(0, 0, 150, 220)
        beaker_rect.midtop = (422, 80)  # centered over the bottle area, left of the recipe/GO column
        liquid_color = self.beaker.liquid_color(self.bottles)
        ui.draw_beaker(self.canvas, beaker_rect, self.beaker, config.CHEMICALS, liquid_color)

        recipe_rect = pygame.Rect(config.CANVAS_WIDTH - 230, 70, 200, 60 + 34 * len(self.recipe))
        ui.draw_recipe_card(self.canvas, recipe_rect, config.CHEMICALS, self.recipe)

        go_rect = pygame.Rect(0, 0, 90, 90)
        go_rect.center = (config.CANVAS_WIDTH - 130, 390)
        pulse = 0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(
            pygame.time.get_ticks() * 0.2).x
        ui.draw_go_button(self.canvas, go_rect, pulse)

        ui.draw_hud(self.canvas, self.level_number, self.streak)

        self.particles.draw(self.canvas)

        if self.state in ("success", "fail"):
            ui.draw_message_banner(self.canvas, self.message, self.message_color)

        scaled = pygame.transform.smoothscale(self.canvas, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))
