"""The Space Lab's state machine: READY -> SUCCESS -> (next level) or
READY -> FAIL -> (reset progress, try again). Same forgiving shape as
the other rooms -- no "game over" -- but introduces a new idea: the
colors must be pressed in a specific ORDER, not just the right counts.
A single wrong press means starting the sequence over, same as a real
launch code.

Reuses all four color buttons as generic "launch code" steps (same
physical buttons as the Chemistry Lab's chemicals), since the sequence
card itself always shows which color comes next -- no separate hint
system needed the way the other rooms have one.
"""
import pygame

from . import config, space_levels, space_ui, ui
from .particles import ParticleSystem

SUCCESS_HOLD = 2.6
FAIL_HOLD = 1.0  # short and snappy -- mistakes during memorization shouldn't feel like a big stop

ROCKET_X = 422
ROCKET_BASE_Y = 450


class SpaceGame:
    def __init__(self, screen, input_manager, sound_bank):
        self.screen = screen
        self.canvas = pygame.Surface((config.CANVAS_WIDTH, config.CANVAS_HEIGHT))
        self.input = input_manager
        self.sound = sound_bank
        self.particles = ParticleSystem()

        self.level_number = 1
        self.streak = 0
        self.state = "ready"
        self.state_timer = 0.0
        self.message = ""
        self.message_color = config.GOOD_COLOR
        self.lift = 0.0

        self.progress = 0
        self._load_level(self.level_number)

    # -- level setup ---------------------------------------------------
    def _load_level(self, number):
        self.sequence = space_levels.get_level(number)
        self.progress = 0
        self.lift = 0.0

    @property
    def armed(self):
        return self.state == "ready" and self.progress >= len(self.sequence)

    # -- per-frame API, driven by World's main loop -----------------------
    def handle_actions(self, actions):
        for action in actions:
            kind = action[0]
            if kind == "drop" and self.state == "ready":
                self._on_press(action[1])
            elif kind == "go" and self.state == "ready":
                self._on_go()
            elif kind == "reset" and self.state == "ready":
                self.progress = 0
                self.sound.play("reset")

    def _on_press(self, chem_index):
        expected = self.sequence[self.progress] if self.progress < len(self.sequence) else None
        if expected is not None and chem_index == expected:
            self.progress += 1
            self.sound.play(f"drop_{chem_index % 4}")
            color = config.CHEMICALS[chem_index]["color"]
            self.particles.spawn_bubble(ROCKET_X, ROCKET_BASE_Y - 80, color)
        else:
            self._trigger_fail("Oops! Let's try again.")

    def _on_go(self):
        self.sound.play("go")
        if self.armed:
            self.state = "success"
            self.state_timer = SUCCESS_HOLD
            self.streak += 1
            self.message = "Blast off! Great job, astronaut!"
            self.message_color = config.GOOD_COLOR
            self.particles.spawn_celebration(ROCKET_X, ROCKET_BASE_Y - 60,
                                              space_ui.FLAME_COLORS)
            self.sound.play("success")
        else:
            self._trigger_fail("Finish the launch code first!")

    def _trigger_fail(self, message):
        self.state = "fail"
        self.state_timer = FAIL_HOLD
        self.streak = 0
        self.message = message
        self.message_color = config.BAD_COLOR
        self.sound.play("fail")
        self.particles.spawn_fizzle(ROCKET_X, ROCKET_BASE_Y - 80, space_ui.ROCKET_ACCENT)

    def update(self, dt):
        self.particles.update(dt)

        if self.state == "fail":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.progress = 0
                self.state = "ready"
        elif self.state == "success":
            self.state_timer -= dt
            elapsed_fraction = 1.0 - max(0.0, self.state_timer) / SUCCESS_HOLD
            self.lift = min(1.0, elapsed_fraction)
            if self.state_timer <= 0:
                self.level_number += 1
                self._load_level(self.level_number)
                self.state = "ready"

    def draw(self):
        ui.draw_background(self.canvas)

        space_ui.draw_launchpad(self.canvas, ROCKET_X, ROCKET_BASE_Y)
        space_ui.draw_rocket(self.canvas, ROCKET_X, ROCKET_BASE_Y, self.armed, self.lift,
                              launching=(self.state == "success"))

        sequence_rect = pygame.Rect(config.CANVAS_WIDTH - 230, 70, 200, 130)
        space_ui.draw_sequence_card(self.canvas, sequence_rect, self.sequence, self.progress,
                                     config.CHEMICALS)

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
