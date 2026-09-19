# Obstacle-Avoiding Robot

An autonomous robot built on Arduino that uses an ultrasonic sensor mounted on a servo to scan for obstacles and steer around them in real time.

## How it works

1. The servo holds an HC-SR04 ultrasonic sensor facing forward and continuously measures distance.
2. If the path ahead is clear (beyond the safe distance threshold), the robot drives forward.
3. If an obstacle is detected:
   - The robot stops and reverses slightly.
   - The servo sweeps the sensor left (150°) and right (30°) to measure clearance on each side.
   - The robot turns toward whichever side has more open space.
   - If both sides are blocked, it reverses further and re-scans.
4. This loop repeats continuously, letting the robot navigate around obstacles on its own.

## Hardware

| Component | Role |
|---|---|
| Arduino (Uno/Nano) | Main controller |
| HC-SR04 ultrasonic sensor | Measures distance to obstacles |
| SG90 micro servo | Pans the ultrasonic sensor left/center/right |
| L298N dual H-bridge motor driver | Drives both DC motors, controls direction and speed (PWM) |
| 2x DC gear motors + wheels | Drive the robot |
| Battery pack | Powers the motors and Arduino |
| Breadboard + jumper wires | Prototyping/wiring |

## Pin Configuration

| Function | Pin |
|---|---|
| Ultrasonic TRIG | 12 |
| Ultrasonic ECHO | 13 |
| Servo signal | 11 |
| Left motor speed (PWM) | 5 |
| Left motor direction | 7, 8 |
| Right motor speed (PWM) | 6 |
| Right motor direction | 9, 10 |

## Setup

1. Wire the components according to the pin table above.
2. Open `obstacle_avoiding_robot.ino` in the Arduino IDE.
3. Install the built-in `Servo` library if not already available (Sketch → Include Library → Servo).
4. Select your board and port, then upload.
5. Power the motors from a separate battery pack (not the Arduino's USB power) — the motors draw more current than USB can safely supply.

## Tuning

- `SAFE_DISTANCE` (default 25 cm): increase for more cautious obstacle avoidance, decrease to let it get closer before turning.
- `MOTOR_SPEED` (default 180, out of 255): adjust based on your motors and battery voltage.

## Notes

The obstacle-detection and path-decision logic was originally written and reasoned through in Python, then ported to C/C++ for Arduino with the help of AI tools, since C/C++ isn't yet a language I'm fluent in. The circuit design, wiring, and all hardware testing/debugging were done independently.

## Author

Vishal Prasad — Electrical and Computer Engineering, College of Engineering Trivandrum
