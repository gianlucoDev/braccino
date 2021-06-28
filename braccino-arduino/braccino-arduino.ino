#include <InverseK.h>

#include "./braccio-control.h"

// serial variables
const byte startMarker = 0xFF;
const byte endMarker = 0xF0;

const byte numBytes = 32;
byte receivedBytes[numBytes];
byte numReceived = 0;

boolean newData = false;

// django -> arduino
const byte SETPOS_ID = 0x01;
const byte POS_QUERY_ID = 0x02;
const byte SETSPEED_ID = 0x03;

// django <- arduino
const byte HELLO_ID = 0x00;
const byte SETPOS_REPLY_ID = 0x01;
const byte POS_QUERY_REPLY_ID = 0x02;

// braccio links
Link base_link, upperarm_link, forearm_link, hand_link;

// braccio control variables
braccioAngles targetAngles;
int speed = 30;

// Quick conversion from the Braccio angle system to radians
float b2a(float b) { return b / 180.0 * PI - HALF_PI; }

// Quick conversion from radians to the Braccio angle system
float a2b(float a) { return (a + HALF_PI) * 180 / PI; }

void setup() {
  // Initialize serial
  Serial.begin(38400);

  // initialize ik library
  base_link.init(0, b2a(0.0), b2a(180.0));
  upperarm_link.init(200, b2a(15.0), b2a(165.0));
  forearm_link.init(200, b2a(0.0), b2a(180.0));
  hand_link.init(270, b2a(0.0), b2a(180.0));
  InverseK.attach(base_link, upperarm_link, forearm_link, hand_link);

  braccioBegin();

  // Signal that the arduino is ready
  sendReady();
}

void sendReady() {
  byte ping_data[] = {startMarker, HELLO_ID, 0xAA, endMarker};
  Serial.write(ping_data, 4);
}

void loop() {
  receiveData();
  handlePacket();

  // move the Braccio towards desired position
  braccioServoStep(speed, targetAngles);
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

    case POS_QUERY_ID:
      handlePositionQuery();
      break;

    case SETSPEED_ID:
      handleSetSpeed();
      break;
  }

  newData = false;
}

void handleSetPosition() {
  // skip first byte because it's the packet type ID

  // target position
  byte x = receivedBytes[1];
  byte y = receivedBytes[2];
  byte z = receivedBytes[3];

  // TODO: handle attack angle
  byte attack_angle = receivedBytes[4];
  byte wrist_rot = receivedBytes[5];
  byte gripper = receivedBytes[6];

  float base, shoulder, elbow, wrist_ver;
  bool ok;
  if (attack_angle == 255) {
    ok = InverseK.solve(x, y, z, base, shoulder, elbow, wrist_ver);
  } else {
    attack_angle = b2a(attack_angle);
    ok =
        InverseK.solve(x, y, z, base, shoulder, elbow, wrist_ver, attack_angle);
  }

  // if ik solution was found, set motor angles
  if (ok) {
    targetAngles.base = (int)a2b(base);
    targetAngles.shoulder = (int)a2b(shoulder);
    targetAngles.elbow = (int)a2b(elbow);
    targetAngles.wrist_ver = (int)a2b(wrist_ver);
    targetAngles.wrist_rot = (int)wrist_rot;
    targetAngles.gripper = (int)gripper;
  }

  // communicate wheter a ik solution was found
  byte reply_data[] = {startMarker, SETPOS_REPLY_ID, (byte)ok, endMarker};
  Serial.write(reply_data, 4);
}

void handlePositionQuery() {
  braccioAngles currentAngles = braccioCurrentAngles();

  bool positionReached = currentAngles.base == targetAngles.base &&
                         currentAngles.shoulder == targetAngles.shoulder &&
                         currentAngles.elbow == targetAngles.elbow &&
                         currentAngles.wrist_ver == targetAngles.wrist_ver &&
                         currentAngles.wrist_rot == targetAngles.wrist_rot &&
                         currentAngles.gripper == targetAngles.gripper;

  byte reply_data[] = {
      startMarker, POS_QUERY_REPLY_ID, (byte)positionReached,
      //
      0xFA, (byte)currentAngles.base, (byte)currentAngles.shoulder,
      (byte)currentAngles.elbow, (byte)currentAngles.wrist_ver,
      (byte)currentAngles.wrist_rot, (byte)currentAngles.gripper,
      //
      0xFA, (byte)targetAngles.base, (byte)targetAngles.shoulder,
      (byte)targetAngles.elbow, (byte)targetAngles.wrist_ver,
      (byte)targetAngles.wrist_rot, (byte)targetAngles.gripper,
      //
      endMarker};

  Serial.write(reply_data, 18);
}

void handleSetSpeed() {
  // first byte is packet ID
  // second byte is desired speed
  speed = receivedBytes[1];
}
