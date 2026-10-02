#!/bin/bash
# Launches the game fullscreen with your screen's real size baked in, so
# you never have to retype the long LAB_GAME_... command again.
#
# If "it's still big" ever comes back (e.g. after swapping screens), fix
# the two numbers below to match what `fbset -s` reports for your screen.
export LAB_GAME_FULLSCREEN=1
export LAB_GAME_WIDTH=800
export LAB_GAME_HEIGHT=480

cd "$(dirname "$0")"
exec python3 main.py
