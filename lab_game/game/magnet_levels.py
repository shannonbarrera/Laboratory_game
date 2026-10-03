"""Level data for the Magnet Lab's "does it stick?" game.

Unlike the other rooms, a "level" here isn't a fixed recipe -- the
objects are picked at random each round (see game/magnet.py). A level is
just the streak target: how many in a row the player needs to get right
before the big success celebration fires and the next (usually longer)
streak target loads.
"""

TARGETS = [1, 2, 2, 3, 3, 4, 4, 5, 5, 6]

MAX_TARGET = 8


def total_levels():
    return len(TARGETS)


def get_target(level_number):
    """1-indexed. Returns a hand-picked target while we have one,
    otherwise keeps creeping the target up (capped) forever."""
    if 1 <= level_number <= len(TARGETS):
        return TARGETS[level_number - 1]
    extra = (level_number - len(TARGETS) + 2) // 3
    return min(MAX_TARGET, TARGETS[-1] + extra)
