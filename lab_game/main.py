#!/usr/bin/env python3
"""Entry point for the Little Lab potion-mixing game.

Run it with:
    python3 main.py

See README.md for how to wire up Raspberry Pi GPIO buttons or plug in a
USB/Bluetooth game controller.
"""
import os
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import config
from game.app import Game


def main():
    pygame.init()
    pygame.display.set_caption("Little Lab: Potion Drops")

    if config.FULLSCREEN:
        # (0, 0) tells SDL to use the display's current resolution,
        # whatever that happens to be on this particular screen/Pi,
        # instead of guessing a fixed size that might not match it.
        flags = pygame.FULLSCREEN
        size = (0, 0)
    else:
        flags = 0
        size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    screen = pygame.display.set_mode(size, flags)

    try:
        pygame.mouse.set_visible(not config.FULLSCREEN)
    except pygame.error:
        pass

    game = Game(screen)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
