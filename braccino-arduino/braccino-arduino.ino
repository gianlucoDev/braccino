#include <InverseK.h>
#include <PacketSerial.h>

#include "./braccio-control.h"
#include "./packets.h"

PacketSerial packetSerial;
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
  helloPacket p = {HELLO_ID, 0xAA};
  packetSerial.send((uint8_t *)&p, sizeof(p));
}

void onPacketReceived(const uint8_t *buffer, size_t size) {
  byte packetId = buffer[0];

  switch (packetId) {
    case SETPOS_ID:
      onSetPosition(buffer, size);
      break;

    case POS_QUERY_ID:
      onPositionQuery(buffer, size);
      break;

    case SETSPEED_ID:
      onSetSpeed(buffer, size);
      break;
  }
}

void onSetPosition(const uint8_t *buffer, size_t size) {
  setposPacket p;
  memcpy(&p, buffer, sizeof(p));

  // args
  float x = (float)p.x;
  float y = (float)p.y;
  float z = (float)p.z;
  float phi = p.attack_angle == -1 ? FREE_ANGLE : b2a((float)p.attack_angle);

  // outuputs
  float base, shoulder, elbow, wrist_ver;

  // find a ik solution for the given coordinates
  bool ok = InverseK.solve(x, y, z, base, shoulder, elbow, wrist_ver, phi);

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
    targetAngles.wrist_rot = (int)p.wrist_rot;
    targetAngles.gripper = (int)p.gripper;
  }

  // communicate wheter a ik solution was found
  setpostReplyPacket response = {SETPOS_REPLY_ID, ok};
  packetSerial.send((uint8_t *)&response, sizeof(response));
}

void onPositionQuery(const uint8_t *buffer, size_t size) {
  braccioAngles currentAngles = braccioCurrentAngles();

  // wether braccio has reached target position
  bool positionReached = currentAngles.base == targetAngles.base &&
                         currentAngles.shoulder == targetAngles.shoulder &&
                         currentAngles.elbow == targetAngles.elbow &&
                         currentAngles.wrist_ver == targetAngles.wrist_ver &&
                         currentAngles.wrist_rot == targetAngles.wrist_rot &&
                         currentAngles.gripper == targetAngles.gripper;

  posQueryReplyPacket p = {POS_QUERY_REPLY_ID, (byte)positionReached};
  packetSerial.send((uint8_t *)&p, sizeof(p));
}

void onSetSpeed(const uint8_t *buffer, size_t size) {
  setspeedPacket p;
  memcpy(&p, buffer, sizeof(p));

  speed = p.speed;
}
