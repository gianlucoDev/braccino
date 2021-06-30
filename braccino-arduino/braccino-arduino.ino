#include <InverseK.h>
#include <PacketSerial.h>

#include "./braccio-control.h"

// serial variables
PacketSerial packetSerial;

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
  // initialize serial
  packetSerial.begin(38400);
  packetSerial.setPacketHandler(&onPacketReceived);

  // initialize ik library
  base_link.init(0, b2a(0.0), b2a(180.0));
  upperarm_link.init(200, b2a(15.0), b2a(165.0));
  forearm_link.init(200, b2a(0.0), b2a(180.0));
  hand_link.init(270, b2a(0.0), b2a(180.0));
  InverseK.attach(base_link, upperarm_link, forearm_link, hand_link);

  // initialize braccio
  braccioBegin();

  // signal that the Arduino is ready
  sendReady();
}

void loop() {
  // move the Braccio towards desired position
  braccioServoStep(speed, targetAngles);

  // handle packets
  packetSerial.update();
}

void sendReady() {
  byte ping_data[] = {HELLO_ID, 0xAA};
  packetSerial.send(ping_data, 2);
}

void onPacketReceived(const uint8_t* packet, size_t size) {
  byte packetId = packet[0];

  switch (packetId) {
    case SETPOS_ID:
      onSetPosition(packet, size);
      break;

    case POS_QUERY_ID:
      onPositionQuery(packet, size);
      break;

    case SETSPEED_ID:
      onSetSpeed(packet, size);
      break;
  }
}

int readInt(const uint8_t* buffer, int offset) {
  int x;
  memcpy(&x, buffer + offset, sizeof(int));
  return x;
}

void onSetPosition(const uint8_t* packet, size_t size) {
  // skip first byte because it's the packet type ID
  int16_t x = readInt(packet, 1 + 0 * sizeof(int16_t));
  int16_t y = readInt(packet, 1 + 1 * sizeof(int16_t));
  int16_t z = readInt(packet, 1 + 2 * sizeof(int16_t));
  int16_t attack_angle = readInt(packet, 1 + 3 * sizeof(int));
  byte wrist_rot = packet[1 + 4 * sizeof(int)];
  byte gripper = packet[1 + 4 * sizeof(int) + 1];

  float base, shoulder, elbow, wrist_ver;
  bool ok;
  if (attack_angle == -1) {
    ok = InverseK.solve(x, y, z, base, shoulder, elbow, wrist_ver);
  } else {
    float phi = b2a(attack_angle);
    ok = InverseK.solve(x, y, z, base, shoulder, elbow, wrist_ver, phi);
  }

  // if ik solution was found, set motor angles
  if (ok) {
    // apparently someone mounted the motor upside down
    // so i'm just going to reverse the angle
    int wv = (int)a2b(wrist_ver);
    wv = 180 - wv;

    targetAngles.base = (int)a2b(base);
    targetAngles.shoulder = (int)a2b(shoulder);
    targetAngles.elbow = (int)a2b(elbow);
    targetAngles.wrist_ver = wv;
    targetAngles.wrist_rot = (int)wrist_rot;
    targetAngles.gripper = (int)gripper;
  }

  // communicate wheter a ik solution was found
  byte reply_data[] = {SETPOS_REPLY_ID, (byte)ok};
  packetSerial.send(reply_data, 2);
}

void onPositionQuery(const uint8_t* packet, size_t size) {
  braccioAngles currentAngles = braccioCurrentAngles();

  // wether braccio has reached target position
  bool positionReached = currentAngles.base == targetAngles.base &&
                         currentAngles.shoulder == targetAngles.shoulder &&
                         currentAngles.elbow == targetAngles.elbow &&
                         currentAngles.wrist_ver == targetAngles.wrist_ver &&
                         currentAngles.wrist_rot == targetAngles.wrist_rot &&
                         currentAngles.gripper == targetAngles.gripper;

  byte reply_data[] = {POS_QUERY_REPLY_ID, (byte)positionReached};
  packetSerial.send(reply_data, 2);
}

void onSetSpeed(const uint8_t* packet, size_t size) {
  // first byte is packet ID
  // second byte is desired speed
  speed = packet[1];
}
