#include <Servo.h>

#include "./braccio-control.h"

// serial variables
const byte startMarker = 0x3C;
const byte endMarker = 0x3E;

const byte numBytes = 32;
byte receivedBytes[numBytes];
byte numReceived = 0;

boolean newData = false;

// django -> arduino
const byte SETPOS_ID = 0x01;
const byte GETPOS_ID = 0x02;

// django <- arduino
const byte HELLO_ID = 0x00;
const byte GETPOS_REPLY_ID = 0x02;

// braccio target position
braccioPosition targetPosition;

void setup() {
  // Initialize serial
  Serial.begin(9600);

  // set initial target position
  targetPosition.base = 90;
  targetPosition.shoulder = 45;
  targetPosition.elbow = 180;
  targetPosition.wrist_rot = 180;
  targetPosition.wrist_ver = 90;
  targetPosition.gripper = 10;

  // TODO: re-implement soft-start
  braccioBegin();

  // Signal that the arduino is ready
  sendReady();
}

void sendReady() {
  byte ping_data[] = {startMarker, HELLO_ID, 0xFF, endMarker};
  Serial.write(ping_data, 3);
}

void loop() {
  receiveData();
  handlePacket();

  // move the Braccio towards desired position
  braccioServoStep(30, targetPosition);
}

void receiveData() {
  static boolean listening = false;
  static byte index = 0;
  byte rb;

  while (Serial.available() > 0 && newData == false) {
    rb = Serial.read();

    // handle start marker
    if (!listening) {
      if (rb == startMarker) {
        listening = true;
      }

      continue;
    }

    // handle end marker
    if (rb == endMarker) {
      listening = false;
      numReceived = index;
      index = 0;
      newData = true;
      continue;
    }

    // handle message
    receivedBytes[index] = rb;

    // check to avoid out of bounds access
    if (index < numBytes - 1) index++;
  }
}

void handlePacket() {
  if (!newData) return;

  switch (receivedBytes[0]) {
    case SETPOS_ID:
      handleSetPosition();
      break;

    case GETPOS_ID:
      handleGetPosition();
      break;
  }

  newData = false;
}

void handleSetPosition() {
  // skip first byte because it's the packet type ID
  targetPosition.base = receivedBytes[1];
  targetPosition.shoulder = receivedBytes[2];
  targetPosition.elbow = receivedBytes[3];
  targetPosition.wrist_rot = receivedBytes[4];
  targetPosition.wrist_ver = receivedBytes[5];
  targetPosition.gripper = receivedBytes[6];
}

void handleGetPosition() {
  braccioPosition currentPosition = braccioCurrentPostion();

  byte packetData[] = {

      startMarker,
      GETPOS_REPLY_ID,
      (byte)currentPosition.base,
      (byte)currentPosition.shoulder,
      (byte)currentPosition.elbow,
      (byte)currentPosition.wrist_rot,
      (byte)currentPosition.wrist_ver,
      (byte)currentPosition.gripper,
      endMarker

  };

  Serial.write(packetData, 9);
}
