/*
  Joystick bridge: reads a GND/+5V/VRx/VRy/SW analog joystick module and
  relays it to the Raspberry Pi over USB serial as plain text lines like:

      0.482,-0.113,0

  (dx, dy, each roughly -1.0..1.0, then 1 if the stick is clicked in,
  else 0). The Pi-side game/serial_joystick.py reads these lines -- the
  Pi's own GPIO pins can't read the joystick directly since VRx/VRy are
  analog voltages, not digital on/off signals, so this board is standing
  in as the analog-to-digital converter.

  Works unmodified on both classic AVR Arduinos (Uno/Nano/Mega) and
  ESP32 boards -- the #ifdef ESP32 block below is the only difference,
  matching ESP32's ADC to the same 10-bit range as AVR's so the rest of
  the code doesn't need to care which board it's running on.

  Wiring (same for either board):
    joystick GND  -> board GND
    joystick +5V  -> board 5V (or 3V3 on a 3.3V-only board -- the cheap
                     joystick modules work fine down to 3.3V)
    joystick VRx  -> board A0
    joystick VRy  -> board A1
    joystick SW   -> board pin 2
*/

const int PIN_VRX = A0;
const int PIN_VRY = A1;
const int PIN_SW = 2;

const float DEADZONE = 0.08;  // ignore tiny drift around center

int centerX = 512;
int centerY = 512;

void setup() {
  Serial.begin(115200);

#ifdef ESP32
  analogReadResolution(10);  // match AVR's 0-1023 range
#endif

  pinMode(PIN_SW, INPUT_PULLUP);  // SW pulls LOW when pressed

  // Auto-calibrate center: assumes the stick is resting (untouched) when
  // the board powers on or is reset, which is true for a kiosk setup
  // where nobody's mid-walk when it boots.
  long sumX = 0, sumY = 0;
  const int samples = 20;
  for (int i = 0; i < samples; i++) {
    sumX += analogRead(PIN_VRX);
    sumY += analogRead(PIN_VRY);
    delay(5);
  }
  centerX = sumX / samples;
  centerY = sumY / samples;
}

float normalize(int raw, int center) {
  float value = (raw - center) / 512.0;
  if (value > 1.0) value = 1.0;
  if (value < -1.0) value = -1.0;
  if (abs(value) < DEADZONE) value = 0.0;
  return value;
}

void loop() {
  float dx = normalize(analogRead(PIN_VRX), centerX);
  float dy = normalize(analogRead(PIN_VRY), centerY);
  int sw = digitalRead(PIN_SW) == LOW ? 1 : 0;

  Serial.print(dx, 3);
  Serial.print(',');
  Serial.print(dy, 3);
  Serial.print(',');
  Serial.println(sw);

  delay(16);  // ~60Hz, plenty fast for a 30fps game
}
