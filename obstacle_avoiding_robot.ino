#include <Servo.h>

Servo scanner;

// Ultrasonic sensor
#define TRIG_PIN 12
#define ECHO_PIN 13

// Servo
#define SERVO_PIN 11

// Left motor
#define ENA 5
#define IN1 7
#define IN2 8

// Right motor
#define ENB 6
#define IN3 9
#define IN4 10

// Settings
#define MOTOR_SPEED 180
#define SAFE_DISTANCE 25

long distanceCM;

void setup() {
  Serial.begin(9600);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  scanner.attach(SERVO_PIN);

  // Start facing forward
  scanner.write(90);

  stopRobot();
  delay(1000);
}

void loop() {

  // Look straight ahead
  scanner.write(90);
  delay(150);

  distanceCM = getDistance();

  Serial.print("Front: ");
  Serial.print(distanceCM);
  Serial.println(" cm");

  // No obstacle
  if (distanceCM > SAFE_DISTANCE) {
    moveForward();
  }

  // Obstacle detected
  else {
    stopRobot();
    delay(200);

    // Reverse a little
    moveBackward();
    delay(500);
    stopRobot();
    delay(200);

    // Scan both sides
    int leftDistance = scanLeft();
    int rightDistance = scanRight();

    Serial.print("Left: ");
    Serial.print(leftDistance);
    Serial.print(" cm | Right: ");
    Serial.print(rightDistance);
    Serial.println(" cm");

    // Choose the side with more free space
    if (leftDistance > rightDistance &&
        leftDistance > SAFE_DISTANCE) {

      turnLeft();
      delay(600);
      stopRobot();

    }
    else if (rightDistance > SAFE_DISTANCE) {

      turnRight();
      delay(600);
      stopRobot();

    }
    else {
      // Both sides blocked
      // Reverse further and try again
      moveBackward();
      delay(700);
      stopRobot();
    }

    // Return sensor to center
    scanner.write(90);
    delay(200);
  }
}


// ---------------- DISTANCE ----------------

long getDistance() {

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);

  if (duration == 0) {
    return 400;
  }

  return duration * 0.0343 / 2;
}


// ---------------- SCANNING ----------------

int scanLeft() {

  scanner.write(150);
  delay(500);

  int distance = getDistance();

  return distance;
}


int scanRight() {

  scanner.write(30);
  delay(500);

  int distance = getDistance();

  return distance;
}


// ---------------- MOTOR CONTROL ----------------

void moveForward() {

  analogWrite(ENA, MOTOR_SPEED);
  analogWrite(ENB, MOTOR_SPEED);

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}


void moveBackward() {

  analogWrite(ENA, MOTOR_SPEED);
  analogWrite(ENB, MOTOR_SPEED);

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}


void turnLeft() {

  analogWrite(ENA, MOTOR_SPEED);
  analogWrite(ENB, MOTOR_SPEED);

  // Left wheel backward
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  // Right wheel forward
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}


void turnRight() {

  analogWrite(ENA, MOTOR_SPEED);
  analogWrite(ENB, MOTOR_SPEED);

  // Left wheel forward
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  // Right wheel backward
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}


void stopRobot() {

  analogWrite(ENA, 0);
  analogWrite(ENB, 0);

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}
