"""Tiny synthesized sound effects.

We generate every sound effect in code with numpy instead of shipping
audio files. That keeps the project tiny, avoids any licensing questions,
and still gives a kindergartner nice chimes/plops/fizzles to react to.
If no audio device is available (e.g. a headless Pi with no speaker
wired up yet) everything here fails quietly and the game keeps running
silently instead of crashing.
"""
import math

try:
    import numpy as np
except ImportError:  # pragma: no cover - numpy is a listed dependency
    np = None

import pygame

SAMPLE_RATE = 22050


def _tone(freq, duration, volume=0.5, fade=True, shape="sine"):
    if np is None:
        return None
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    if shape == "square":
        wave = np.sign(np.sin(2 * math.pi * freq * t))
    else:
        wave = np.sin(2 * math.pi * freq * t)
    if fade:
        fade_n = max(1, int(n * 0.1))
        envelope = np.ones(n)
        envelope[:fade_n] = np.linspace(0, 1, fade_n)
        envelope[-fade_n:] = np.linspace(1, 0, fade_n)
        wave = wave * envelope
    wave = (wave * volume * 32767).astype(np.int16)
    stereo = np.repeat(wave.reshape(n, 1), 2, axis=1)
    return np.ascontiguousarray(stereo)


def _concat(*arrays):
    if np is None or any(a is None for a in arrays):
        return None
    return np.concatenate(arrays, axis=0)


class SoundBank:
    """Builds and plays all effects. Safe to use even with no mixer."""

    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2)
            self.enabled = np is not None
        except pygame.error:
            self.enabled = False
        if self.enabled:
            self._build()

    def _make(self, name, array):
        if array is None:
            return
        try:
            self.sounds[name] = pygame.sndarray.make_sound(array)
        except Exception:
            self.enabled = False

    def _build(self):
        # One gentle "plop" per chemical slot, pitch rises per bottle so
        # each color has its own recognizable sound.
        for i in range(4):
            freq = 300 + i * 90
            self._make(f"drop_{i}", _tone(freq, 0.12, volume=0.4))

        self._make("go", _tone(220, 0.08, volume=0.5, shape="square"))

        # Rising three-note chime for success.
        notes = [_tone(f, 0.12, volume=0.5) for f in (523, 659, 784)]
        self._make("success", _concat(*notes))

        # Low wobbly "aw shucks" for a miss -- friendly, not scary.
        fail_notes = [_tone(f, 0.15, volume=0.4) for f in (300, 220)]
        self._make("fail", _concat(*fail_notes))

        self._make("reset", _tone(180, 0.1, volume=0.3))
        self._make("full", _tone(150, 0.08, volume=0.35, shape="square"))

        # A cheerful little blip for shooing a bug away...
        shoo_notes = [_tone(f, 0.06, volume=0.4) for f in (500, 700)]
        self._make("shoo", _concat(*shoo_notes))
        # ...and a gentle (not scary) one for when a bug gets a bite in.
        self._make("munch", _tone(260, 0.1, volume=0.35, shape="square"))

        # A bright little metallic "cling!" for a magnet correctly catching something.
        cling_notes = [_tone(f, 0.07, volume=0.4) for f in (900, 1200)]
        self._make("cling", _concat(*cling_notes))

    def play(self, name):
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()
