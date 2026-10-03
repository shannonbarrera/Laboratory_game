"""Level data for the Space Lab's "launch sequence" game.

Each level is a list of chemical-color indices (0=red, 1=blue, 2=green,
3=yellow -- the same four color buttons as every other room) that must
be pressed in that exact order to arm the rocket for launch. Unlike the
Chemistry Lab (any order, just the final counts) or the Bug & Plant Lab
(two independent targets), this introduces a new idea: order matters,
and a single wrong press means starting the sequence over.
"""
import random

LEVELS = [
    [0],
    [0, 0],
    [1, 0],
    [0, 1, 0],
    [2],
    [1, 2, 1],
    [3],
    [0, 3, 2, 1],
    [2, 2, 3, 0],
    [1, 0, 3, 2, 1],
]

MAX_LENGTH = 7
NUM_COLORS = 4


def total_levels():
    return len(LEVELS)


def get_level(level_number):
    """1-indexed. Returns a hand-built sequence while we have one,
    otherwise makes up a new one that's a bit longer/harder, forever."""
    if 1 <= level_number <= len(LEVELS):
        return LEVELS[level_number - 1]
    return _random_level(level_number)


def _random_level(level_number):
    rng = random.Random(3000 + level_number)  # stable per-level, still varied
    length = min(MAX_LENGTH, 3 + (level_number - len(LEVELS)) // 2)
    return [rng.randrange(NUM_COLORS) for _ in range(length)]
