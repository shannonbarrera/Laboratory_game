"""Reads movement from an Arduino or ESP32 acting as a translator for an
analog (VRx/VRy/SW) joystick module -- the Pi's own GPIO pins can't read
an analog voltage directly, so the microcontroller does that job and
relays the result to the Pi over a USB cable as plain serial text lines
("dx,dy,sw\\n"; see arduino/joystick_bridge/joystick_bridge.ino).

Like the GPIO and pygame-joystick paths, this fails quietly (prints a
message, keeps the rest of the game running on keyboard/other inputs) if
pyserial isn't installed or no board is plugged in -- it's an optional
extra input source, not a requirement.
"""
import glob
import queue
import threading
import time

from . import config

try:
    import serial
except ImportError:  # pragma: no cover - optional dependency
    serial = None


def _candidate_ports():
    if config.SERIAL_JOYSTICK_PORT:
        return [config.SERIAL_JOYSTICK_PORT]
    return sorted(glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*"))


class SerialJoystick:
    """Opens the first serial port that looks like an Arduino/ESP32 and
    reads movement lines from it on a background thread, since a blocking
    serial read can't happen on the main game loop's thread without
    stalling every other frame."""

    def __init__(self, action_queue):
        self._action_queue = action_queue
        self._dx = 0.0
        self._dy = 0.0
        self._prev_sw = 0
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self._serial = None

        if serial is None:
            print("[input] pyserial not installed, skipping Arduino/ESP32 joystick "
                  "(pip install pyserial to enable it)")
            return
        if not config.SERIAL_JOYSTICK_ENABLED:
            return

        for port in _candidate_ports():
            try:
                self._serial = serial.Serial(port, config.SERIAL_JOYSTICK_BAUD, timeout=0.5)
                print(f"[input] Arduino/ESP32 joystick bridge found on {port}")
                break
            except (OSError, serial.SerialException):
                continue

        if self._serial is None:
            print("[input] No Arduino/ESP32 joystick bridge found, continuing without it")
            return

        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _read_loop(self):
        while self._running:
            try:
                line = self._serial.readline().decode("ascii", errors="ignore").strip()
            except (OSError, serial.SerialException):
                break
            if not line:
                continue
            parsed = self._parse_line(line)
            if parsed is None:
                continue
            dx, dy, sw = parsed
            with self._lock:
                self._dx, self._dy = dx, dy
            if sw and not self._prev_sw:
                self._action_queue.put(("back",))
            self._prev_sw = sw

    @staticmethod
    def _parse_line(line):
        parts = line.split(",")
        if len(parts) != 3:
            return None
        try:
            dx = max(-1.0, min(1.0, float(parts[0])))
            dy = max(-1.0, min(1.0, float(parts[1])))
            sw = 1 if parts[2].strip() == "1" else 0
            return dx, dy, sw
        except ValueError:
            return None

    def get_vector(self):
        with self._lock:
            return self._dx, self._dy

    def close(self):
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
