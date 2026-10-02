"""A chemical bottle on the bench: its color, name, and a little bit of
squeeze/tilt animation state so it visibly reacts when its button is
pressed."""


class Bottle:
    def __init__(self, index, name, color):
        self.index = index
        self.name = name
        self.color = color
        self.tilt = 0.0  # animated tilt angle in degrees, eases back to 0
        self.squeeze = 0.0  # 0..1 bulge animation when a drop is dispensed

    def trigger(self):
        self.tilt = 18.0
        self.squeeze = 1.0

    def update(self, dt):
        self.tilt += (0.0 - self.tilt) * min(1.0, dt * 8)
        self.squeeze += (0.0 - self.squeeze) * min(1.0, dt * 6)
