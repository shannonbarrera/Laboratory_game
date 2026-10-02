"""The beaker in the middle of the bench: tracks how many drops of each
chemical have been added, blends the liquid color live as drops go in,
and eases its fill level smoothly instead of snapping -- small touches
that make the toy feel alive."""
from . import config


def _blend(colors_and_weights):
    total = sum(w for _, w in colors_and_weights)
    if total <= 0:
        return config.GLASS_COLOR
    r = sum(c[0] * w for c, w in colors_and_weights) / total
    g = sum(c[1] * w for c, w in colors_and_weights) / total
    b = sum(c[2] * w for c, w in colors_and_weights) / total
    return (int(r), int(g), int(b))


class Beaker:
    def __init__(self):
        self.counts = {}
        self.fill_display = 0.0
        self.shake = 0.0
        self.wobble = 0.0

    @property
    def total(self):
        return sum(self.counts.values())

    def can_add(self):
        return self.total < config.MAX_TOTAL_DROPS

    def add_drop(self, chem_index):
        if not self.can_add():
            self.shake = 0.25
            return False
        self.counts[chem_index] = min(
            self.counts.get(chem_index, 0) + 1, config.MAX_DROPS_PER_CHEMICAL
        )
        self.wobble = 1.0
        return True

    def reset(self):
        self.counts = {}
        self.wobble = 0.4

    def liquid_color(self, bottles):
        pairs = [(bottles[i].color, n) for i, n in self.counts.items() if n > 0]
        if not pairs:
            return config.GLASS_COLOR
        return _blend(pairs)

    def matches(self, recipe):
        if self.total == 0:
            return False
        normalized = {k: v for k, v in self.counts.items() if v > 0}
        return normalized == recipe

    def update(self, dt):
        target = self.total
        self.fill_display += (target - self.fill_display) * min(1.0, dt * 6)
        self.shake *= max(0.0, 1 - dt * 6)
        self.wobble *= max(0.0, 1 - dt * 4)
