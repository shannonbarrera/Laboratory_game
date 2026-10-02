"""A tiny particle system for bubbles and celebration confetti.

Deliberately simple (no physics engine, no sprite sheets) so it stays
light enough for a Raspberry Pi Zero, while still giving a kindergartner
a satisfying "plop" and a big celebratory burst when they get it right.
"""
import random

import pygame


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "radius", "color", "life", "age", "gravity")

    def __init__(self, x, y, vx, vy, radius, color, life, gravity=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.life = life
        self.age = 0.0
        self.gravity = gravity

    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        return self.age < self.life

    def draw(self, surface):
        t = max(0.0, 1.0 - self.age / self.life)
        if t <= 0:
            return
        radius = max(1, int(self.radius * (0.5 + 0.5 * t)))
        color = self.color
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*color, int(255 * t)), (radius, radius), radius)
        surface.blit(glow, (self.x - radius, self.y - radius))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def spawn_bubble(self, x, y, color):
        for _ in range(4):
            self.particles.append(Particle(
                x=x + random.uniform(-6, 6),
                y=y,
                vx=random.uniform(-15, 15),
                vy=random.uniform(-70, -30),
                radius=random.uniform(3, 7),
                color=color,
                life=random.uniform(0.5, 0.9),
                gravity=-20,
            ))

    def spawn_celebration(self, x, y, colors):
        for _ in range(60):
            color = random.choice(colors)
            angle = random.uniform(0, 6.283)
            speed = random.uniform(80, 260)
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=speed * 0.6 * random.choice((-1, 1)) * random.random() + speed * (0.3 if angle else 0),
                vy=-speed,
                radius=random.uniform(3, 6),
                color=color,
                life=random.uniform(0.8, 1.4),
                gravity=320,
            ))

    def spawn_fizzle(self, x, y, color):
        for _ in range(16):
            self.particles.append(Particle(
                x=x + random.uniform(-20, 20),
                y=y + random.uniform(-10, 10),
                vx=random.uniform(-40, 40),
                vy=random.uniform(-40, 10),
                radius=random.uniform(2, 5),
                color=color,
                life=random.uniform(0.3, 0.6),
                gravity=60,
            ))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
