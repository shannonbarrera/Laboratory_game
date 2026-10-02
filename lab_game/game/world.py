"""Top-level orchestrator: owns the one shared InputManager/SoundBank
(GPIO pins and the audio mixer can each only be claimed once) and the
main loop, and switches between the hub (walking around the building)
and whichever room the player has walked into.
"""
import pygame

from . import config, hub, ui
from .app import Game
from .input_manager import InputManager
from .sound import SoundBank


class World:
    def __init__(self, screen):
        self.screen = screen
        self.canvas = pygame.Surface((config.CANVAS_WIDTH, config.CANVAS_HEIGHT))
        self.clock = pygame.time.Clock()
        self.input = InputManager()
        self.sound = SoundBank()

        self.hub = hub.HubWorld()
        self.chem_game = Game(screen, self.input, self.sound)

        self.mode = "hub"  # "hub" | "chemistry" | "placeholder"
        self.current_room = None
        self.running = True

    def run(self):
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            actions = self.input.poll()

            for action in actions:
                if action[0] == "quit":
                    self.running = False
            if not self.running:
                break

            if self.mode != "hub" and any(a[0] == "back" for a in actions):
                self.hub.leave_room(self.current_room)
                self.mode = "hub"
                self.current_room = None

            if self.mode == "hub":
                self._update_hub(dt)
            elif self.mode == "chemistry":
                self.chem_game.handle_actions(actions)
                self.chem_game.update(dt)
                self.chem_game.draw()
            elif self.mode == "placeholder":
                self._draw_placeholder()

            pygame.display.flip()

        self.input.close()

    def _update_hub(self, dt):
        move = self.input.get_move_vector()
        entered_room = self.hub.update(move, dt)
        self.hub.draw(self.canvas)
        self._blit_canvas()

        if entered_room:
            room = hub.ROOMS_BY_ID[entered_room]
            self.current_room = entered_room
            self.mode = "chemistry" if room["ready"] else "placeholder"

    def _draw_placeholder(self):
        room = hub.ROOMS_BY_ID[self.current_room]
        self.canvas.fill(room["color"])
        center = (config.CANVAS_WIDTH // 2, config.CANVAS_HEIGHT // 2 - 40)
        bob = 10 * pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() * 0.1).x
        icon_center = (center[0], center[1] + bob)
        hub.draw_icon(self.canvas, room["icon"], icon_center, room["accent"], scale=2.2)
        ui.draw_text_center(self.canvas, room["name"], (center[0], center[1] + 90), 40)
        ui.draw_text_center(self.canvas, "Coming soon!", (center[0], center[1] + 130), 26,
                             color=room["accent"])
        ui.draw_text_center(self.canvas, "grey button: back to hallway",
                             (center[0], config.CANVAS_HEIGHT - 30), 18, bold=False)
        self._blit_canvas()

    def _blit_canvas(self):
        scaled = pygame.transform.smoothscale(self.canvas, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))
