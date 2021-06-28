#include "braccio-control.h"

#include <Arduino.h>
#include <Servo.h>

// braccio servos
Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

// current motor angles
braccioAngles current;

void softwarePWM(int high_time, int low_time) {
  digitalWrite(SOFT_START_CONTROL_PIN, HIGH);
  delayMicroseconds(high_time);
  digitalWrite(SOFT_START_CONTROL_PIN, LOW);
  delayMicroseconds(low_time);
}

void braccioBegin() {
  // connect pins for soft start
  pinMode(SOFT_START_CONTROL_PIN, OUTPUT);
  digitalWrite(SOFT_START_CONTROL_PIN, LOW);

  // initialization pin Servo motors
  base.attach(11);
  shoulder.attach(10);
  elbow.attach(9);
  wrist_ver.attach(6);
  wrist_rot.attach(5);
  gripper.attach(3);

  // For each step motor this set up the initial degree
  base.write(current.base);
  shoulder.write(current.shoulder);
  elbow.write(current.elbow);
  wrist_ver.write(current.wrist_ver);
  wrist_rot.write(current.wrist_rot);
  gripper.write(current.gripper);

  // do soft start
  long int tmp = millis();
  while (millis() - tmp < LOW_LIMIT_TIMEOUT)
    softwarePWM(80, 450);  // the sum should be 530usec

  while (millis() - tmp < HIGH_LIMIT_TIMEOUT)
    softwarePWM(75, 430);  // the sum should be 505usec

  digitalWrite(SOFT_START_CONTROL_PIN, HIGH);
}

unsigned long lastStep = 0;

void braccioServoStep(int stepDelay, braccioAngles t) {
  // Check values, to avoid dangerous positions for the Braccio
  if (stepDelay > 30) stepDelay = 30;
  if (stepDelay < 10) stepDelay = 10;
  if (t.base < 0) t.base = 0;
  if (t.base > 180) t.base = 180;
  if (t.shoulder < 15) t.shoulder = 15;
  if (t.shoulder > 165) t.shoulder = 165;
  if (t.elbow < 0) t.elbow = 0;
  if (t.elbow > 180) t.elbow = 180;
  if (t.wrist_ver < 0) t.wrist_ver = 0;
  if (t.wrist_ver > 180) t.wrist_ver = 180;
  if (t.wrist_rot > 180) t.wrist_rot = 180;
  if (t.wrist_rot < 0) t.wrist_rot = 0;
  if (t.gripper < 10) t.gripper = 10;
  if (t.gripper > 73) t.gripper = 73;

  // Apply a delay between each step
  unsigned long now = millis();
  if (now - lastStep < stepDelay) {
    return;
  }
  lastStep = now;

  // For each servo motor if next degree is not the same as the previous then
  // do the movement

  if (t.base != current.base) {
    base.write(current.base);
    // One step ahead
    if (t.base > current.base) {
      current.base++;
    }
    // One step beyond
    if (t.base < current.base) {
      current.base--;
    }
  }

  if (t.shoulder != current.shoulder) {
    shoulder.write(current.shoulder);
    // One step ahead
    if (t.shoulder > current.shoulder) {
      current.shoulder++;
    }
    // One step beyond
    if (t.shoulder < current.shoulder) {
      current.shoulder--;
    }
  }

  if (t.elbow != current.elbow) {
    elbow.write(current.elbow);
    // One step ahead
    if (t.elbow > current.elbow) {
      current.elbow++;
    }
    // One step beyond
    if (t.elbow < current.elbow) {
      current.elbow--;
    }
  }

  if (t.wrist_ver != current.wrist_ver) {
    wrist_ver.write(current.wrist_ver);
    // One step ahead
    if (t.wrist_ver > current.wrist_ver) {
      current.wrist_ver++;
    }
    // One step beyond
    if (t.wrist_ver < current.wrist_ver) {
      current.wrist_ver--;
    }
  }

  if (t.wrist_rot != current.wrist_rot) {
    wrist_rot.write(current.wrist_rot);
    // One step ahead
    if (t.wrist_rot > current.wrist_rot) {
      current.wrist_rot++;
    }
    // One step beyond
    if (t.wrist_rot < current.wrist_rot) {
      current.wrist_rot--;
    }
  }

  if (t.gripper != current.gripper) {
    gripper.write(current.gripper);
    // One step ahead
    if (t.gripper > current.gripper) {
      current.gripper++;
    }
    // One step beyond
    if (t.gripper < current.gripper) {
      current.gripper--;
    }
  }
}

braccioAngles braccioCurrentAngles() { return current; }
