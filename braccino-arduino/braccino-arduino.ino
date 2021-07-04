#include <PacketSerial.h>

#include "./braccio-control.h"
#include "./packets.h"

PacketSerial packetSerial;

// braccio control variables
braccioAngles targetAngles;
int speed = 30;

void setup() {
  // initialize serial
  packetSerial.begin(38400);
  packetSerial.setPacketHandler(&onPacketReceived);

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
    case SET_ANGLES_ID:
      onSetAngles(buffer, size);
      break;

    case POS_QUERY_ID:
      onPositionQuery(buffer, size);
      break;

    case SETSPEED_ID:
      onSetSpeed(buffer, size);
      break;
  }
}

void onSetAngles(const uint8_t *buffer, size_t size) {
  setAnglesPacket p;
  memcpy(&p, buffer, sizeof(p));

  // apparently someone mounted the motor upside down
  // so i'm just going to reverse the angle
  int wrist_ver = 180 - p.wrist_ver;

  targetAngles.base = p.base;
  targetAngles.shoulder = p.shoulder;
  targetAngles.elbow = p.elbow;
  targetAngles.wrist_ver = wrist_ver;
  targetAngles.wrist_rot = p.wrist_rot;
  targetAngles.gripper = p.gripper;
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

  posQueryReplyPacket p = {POS_QUERY_REPLY_ID, positionReached};
  packetSerial.send((uint8_t *)&p, sizeof(p));
}

void onSetSpeed(const uint8_t *buffer, size_t size) {
  setspeedPacket p;
  memcpy(&p, buffer, sizeof(p));

  speed = p.speed;
}
