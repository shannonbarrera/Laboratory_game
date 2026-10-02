"""Level data.

Each level is a dict with:
  bottles -- which chemical indices appear on the bench, left to right
  recipe  -- {chemical_index: drop_count} for a correct mix (order of
             adding doesn't matter, just the final counts)

The first dozen levels are hand-picked to introduce one new idea at a
time (one button, one bottle, counting to 3, then combining two colors,
then a decoy bottle that isn't needed). After that, get_level() makes up
new ones forever so the game never just stops.
"""
import random

LEVELS = [
    {"bottles": [0], "recipe": {0: 1}},
    {"bottles": [0], "recipe": {0: 3}},
    {"bottles": [1], "recipe": {1: 2}},
    {"bottles": [0, 1], "recipe": {0: 2, 1: 1}},
    {"bottles": [2], "recipe": {2: 3}},
    {"bottles": [0, 1, 2], "recipe": {0: 1, 1: 1, 2: 1}},
    {"bottles": [3], "recipe": {3: 4}},
    {"bottles": [1, 3], "recipe": {1: 3, 3: 2}},
    {"bottles": [0, 2, 3], "recipe": {0: 2, 2: 2, 3: 1}},
    {"bottles": [0, 1, 2, 3], "recipe": {0: 1, 1: 1, 2: 1, 3: 1}},
    {"bottles": [0, 1, 2], "recipe": {0: 3, 2: 2}},
    {"bottles": [0, 1, 2, 3], "recipe": {1: 2, 3: 3}},
]

MAX_BOTTLES = 4


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
    rng = random.Random(1000 + level_number)  # stable per-level, still varied
    difficulty = min(4, 2 + (level_number - len(LEVELS)) // 3)
    num_active = rng.randint(2, min(difficulty, MAX_BOTTLES))
    active = rng.sample(range(MAX_BOTTLES), num_active)

    # Occasionally add one decoy bottle (visible, but needs zero drops)
    # once the player has had some practice.
    bottles = list(active)
    remaining = [i for i in range(MAX_BOTTLES) if i not in active]
    if remaining and rng.random() < 0.5:
        bottles.append(rng.choice(remaining))
    rng.shuffle(bottles)

    max_drop = min(5, 2 + difficulty)
    recipe = {i: rng.randint(1, max_drop) for i in active}
    return {"bottles": bottles, "recipe": recipe}
