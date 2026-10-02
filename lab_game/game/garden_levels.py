"""Level data for the Bug & Plant Lab's "grow the plant" game.

Each level is just {"water": n, "sun": m} -- press the water button n
times and the sun button m times, then GO. Too much or too little of
either and the plant wilts instead of blooming, so unlike the chemistry
room's "any order is fine" recipes, this introduces a second idea: two
things can each be right or wrong independently.
"""
import random

LEVELS = [
    {"water": 1, "sun": 0},
    {"water": 3, "sun": 0},
    {"water": 0, "sun": 2},
    {"water": 1, "sun": 1},
    {"water": 2, "sun": 1},
    {"water": 2, "sun": 2},
    {"water": 4, "sun": 1},
    {"water": 1, "sun": 3},
    {"water": 3, "sun": 3},
    {"water": 2, "sun": 4},
]

MAX_PER_RESOURCE = 6


def total_levels():
    return len(LEVELS)


def get_level(level_number):
    """1-indexed. Returns a hand-built level while we have one, otherwise
    makes up a new one that's a bit harder than the last hand-built
    level, forever."""
    if 1 <= level_number <= len(LEVELS):
        return LEVELS[level_number - 1]
    return _random_level(level_number)


def _random_level(level_number):
    rng = random.Random(2000 + level_number)  # stable per-level, still varied
    max_amount = min(MAX_PER_RESOURCE, 3 + (level_number - len(LEVELS)) // 2)
    water = rng.randint(0, max_amount)
    sun = rng.randint(0, max_amount)
    if water == 0 and sun == 0:
        water = 1
    return {"water": water, "sun": sun}
