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
from game.world import World


def main():
    pygame.init()
    pygame.display.set_caption("Little Lab: Potion Drops")

    if config.FULLSCREEN:
        flags = pygame.FULLSCREEN
        if config.SIZE_OVERRIDDEN:
            # LAB_GAME_WIDTH/HEIGHT were set explicitly -- trust them over
            # auto-detection, for displays that report the wrong size.
            size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        else:
            # (0, 0) tells SDL to use the display's current resolution,
            # whatever that happens to be on this particular screen/Pi.
            size = (0, 0)
    else:
        flags = 0
        size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    screen = pygame.display.set_mode(size, flags)

    try:
        pygame.mouse.set_visible(not config.FULLSCREEN)
    except pygame.error:
        pass

    world = World(screen)
    world.run()

    pygame.quit()


if __name__ == "__main__":
    main()
