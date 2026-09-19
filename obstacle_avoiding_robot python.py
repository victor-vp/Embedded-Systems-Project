"""
Obstacle-Avoiding Robot — Python control script

This mirrors the original obstacle-detection and path-decision logic
that was later ported to C/C++ for the standalone Arduino sketch
(obstacle_avoiding_robot.ino). This version drives the same Arduino
board directly from Python over a serial connection, using the
pyFirmata library.

--- IMPORTANT SETUP NOTE ---
To run THIS version instead of the .ino sketch:

1. Flash the Arduino with the built-in Firmata example instead of the
   custom sketch:
       Arduino IDE > File > Examples > Firmata > StandardFirmata > Upload
   This replaces the C++ program with a generic "listener" that lets
   Python control the pins directly. (Uploading obstacle_avoiding_robot.ino
   again later will restore the standalone C++ version.)

2. Install pyfirmata:
       pip install pyfirmata

3. Set SERIAL_PORT below to match your Arduino
   (e.g. 'COM5' on Windows, '/dev/ttyUSB0' or '/dev/cu.usbmodemXXXX' on Mac/Linux)

4. Run:
       python obstacle_avoiding_robot.py

--- KNOWN LIMITATION ---
Reading the HC-SR04's echo pulse over a serial link from Python is
slower and less precise than timing it directly in C++ on the Arduino
itself (that's exactly why the deployed version runs natively as C++
on the board). This script is kept as a readable reference of the
original logic design, not as a replacement for the .ino sketch.
"""

import time
from pyfirmata import Arduino, util, SERVO

SERIAL_PORT = 'COM5'  # change this to match your Arduino's port

# ---- Pin assignments (same as the Arduino sketch) ----
TRIG_PIN = 12
ECHO_PIN = 13
SERVO_PIN = 11

ENA = 5   # left motor speed (PWM)
IN1 = 7
IN2 = 8

ENB = 6   # right motor speed (PWM)
IN3 = 9
IN4 = 10

MOTOR_SPEED = 180 / 255  # pyfirmata PWM values run 0.0-1.0, original was 0-255
SAFE_DISTANCE = 25       # cm

# ---- Board setup ----
board = Arduino(SERIAL_PORT)
it = util.Iterator(board)
it.start()

trig = board.digital[TRIG_PIN]
trig.mode = board.OUTPUT

echo = board.digital[ECHO_PIN]
echo.mode = board.INPUT

servo = board.digital[SERVO_PIN]
servo.mode = SERVO

ena = board.digital[ENA]
in1 = board.digital[IN1]
in2 = board.digital[IN2]

enb = board.digital[ENB]
in3 = board.digital[IN3]
in4 = board.digital[IN4]

for pin in (ena, in1, in2, enb, in3, in4):
    pin.mode = board.OUTPUT


# ---------------- DISTANCE ----------------

def get_distance():
    """Send an ultrasonic pulse and estimate distance in cm from the echo."""
    trig.write(0)
    time.sleep(0.000002)
    trig.write(1)
    time.sleep(0.00001)
    trig.write(0)

    start = time.time()
    while echo.read() == 0:
        if time.time() - start > 0.03:
            return 400  # timeout -> treat as "clear"

    pulse_start = time.time()
    while echo.read() == 1:
        if time.time() - pulse_start > 0.03:
            break
    pulse_end = time.time()

    duration_us = (pulse_end - pulse_start) * 1_000_000
    distance_cm = duration_us * 0.0343 / 2
    return distance_cm


# ---------------- SCANNING ----------------

def scan_left():
    servo.write(150)
    time.sleep(0.5)
    return get_distance()


def scan_right():
    servo.write(30)
    time.sleep(0.5)
    return get_distance()


# ---------------- MOTOR CONTROL ----------------

def move_forward():
    ena.write(MOTOR_SPEED)
    enb.write(MOTOR_SPEED)
    in1.write(1)
    in2.write(0)
    in3.write(1)
    in4.write(0)


def move_backward():
    ena.write(MOTOR_SPEED)
    enb.write(MOTOR_SPEED)
    in1.write(0)
    in2.write(1)
    in3.write(0)
    in4.write(1)


def turn_left():
    ena.write(MOTOR_SPEED)
    enb.write(MOTOR_SPEED)
    # Left wheel backward
    in1.write(0)
    in2.write(1)
    # Right wheel forward
    in3.write(1)
    in4.write(0)


def turn_right():
    ena.write(MOTOR_SPEED)
    enb.write(MOTOR_SPEED)
    # Left wheel forward
    in1.write(1)
    in2.write(0)
    # Right wheel backward
    in3.write(0)
    in4.write(1)


def stop_robot():
    ena.write(0)
    enb.write(0)
    in1.write(0)
    in2.write(0)
    in3.write(0)
    in4.write(0)


# ---------------- MAIN LOOP ----------------

def main():
    servo.write(90)
    stop_robot()
    time.sleep(1)

    try:
        while True:
            # Look straight ahead
            servo.write(90)
            time.sleep(0.15)

            distance_cm = get_distance()
            print(f"Front: {distance_cm:.1f} cm")

            # No obstacle
            if distance_cm > SAFE_DISTANCE:
                move_forward()

            # Obstacle detected
            else:
                stop_robot()
                time.sleep(0.2)

                # Reverse a little
                move_backward()
                time.sleep(0.5)
                stop_robot()
                time.sleep(0.2)

                # Scan both sides
                left_distance = scan_left()
                right_distance = scan_right()
                print(f"Left: {left_distance:.1f} cm | Right: {right_distance:.1f} cm")

                # Choose the side with more free space
                if left_distance > right_distance and left_distance > SAFE_DISTANCE:
                    turn_left()
                    time.sleep(0.6)
                    stop_robot()

                elif right_distance > SAFE_DISTANCE:
                    turn_right()
                    time.sleep(0.6)
                    stop_robot()

                else:
                    # Both sides blocked - reverse further and try again
                    move_backward()
                    time.sleep(0.7)
                    stop_robot()

                # Return sensor to center
                servo.write(90)
                time.sleep(0.2)

    except KeyboardInterrupt:
        stop_robot()
        board.exit()
        print("\nStopped.")


if __name__ == "__main__":
    main()
