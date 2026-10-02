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

    flags = pygame.FULLSCREEN if config.FULLSCREEN else 0
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), flags)

    try:
        pygame.mouse.set_visible(not config.FULLSCREEN)
    except pygame.error:
        pass

    game = Game(screen)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
