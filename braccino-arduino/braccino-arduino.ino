#include <Braccio.h>
#include <Servo.h>

// serial variables
const byte startMarker = 0x3C;
const byte endMarker = 0x3E;

const byte numBytes = 32;
byte receivedBytes[numBytes];
byte numReceived = 0;

boolean newData = false;

// braccio variables
Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

int M1 = 90, M2 = 45, M3 = 180, M4 = 180, M5 = 90, M6 = 10;

void setup() {
  // Initialize serial
  Serial.begin(9600);

  // Initialize braccio
  // All the servo motors will be positioned in the "safety" position:
  //   Base (M1):90 degrees
  //   Shoulder (M2): 45 degrees
  //   Elbow (M3): 180 degrees
  //   Wrist vertical (M4): 180 degrees
  //   Wrist rotation (M5): 90 degrees
  //   gripper (M6): 10 degrees
  Braccio.begin();

  // Signal that the arduino is ready
  sendReady();
}

void sendReady() {
  byte ping_data[] = {startMarker, 0x00, 0xFF, endMarker};
  Serial.write(ping_data, 3);
}

void loop() {
  receiveData();
  handlePacket();

  // Step Delay = a milliseconds delay between the movement of each servo;
  //   Allowed values from 10 to 30 msec.
  // M1 = base degrees. Allowed values from 0 to 180 degrees.
  // M2 = shoulder degrees. Allowed values from 15 to 165 degrees.
  // M3 = elbow degrees. Allowed values from 0 to 180 degrees.
  // M4 = wrist vertical degrees. Allowed values from 0 to 180 degrees.
  // M5 = wrist rotation degrees. Allowed values from 0 to 180 degrees.
  // M6 = gripper degrees. Allowed values from 10 to 73 degrees; 10: the toungue
  //   is open, 73: the gripper is closed.
  Braccio.ServoMovement(30, M1, M2, M3, M4, M5, M6);
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

const byte SETPOS_ID = 0x01;
const byte GETPOS_ID = 0x02;

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
  M1 = receivedBytes[1];
  M2 = receivedBytes[2];
  M3 = receivedBytes[3];
  M4 = receivedBytes[4];
  M5 = receivedBytes[5];
  M6 = receivedBytes[6];
}

void handleGetPosition() {
  byte pos_data[] = {startMarker, 0x02, M1, M2, M3, M4, M5, M6, endMarker};
  Serial.write(pos_data, 9);
}
