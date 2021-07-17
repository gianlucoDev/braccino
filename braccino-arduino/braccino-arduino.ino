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
  sndPacket p;
  p.id = sndPacketId::hello;
  p.data.hello = {0xAA};
  packetSerial.send((uint8_t *)&p, sizeof(p));
}

void onPacketReceived(const uint8_t *buffer, size_t size) {
  rcvPacket p;
  size_t copySize = min(size, sizeof(p));
  memcpy(&p, buffer, copySize);

  switch (p.id) {
    case rcvPacketId::setAngles:
      onSetAngles(p.data.setAngles);
      break;

    case rcvPacketId::posQuery:
      onPositionQuery(p.data.posQuery);
      break;

    case rcvPacketId::setSpeed:
      onSetSpeed(p.data.setSpeed);
      break;
  }
}

void onSetAngles(setAnglesData d) {
  // apparently someone mounted the motor upside down
  // so i'm just going to reverse the angle
  int wrist_ver = 180 - d.wrist_ver;

  targetAngles.base = d.base;
  targetAngles.shoulder = d.shoulder;
  targetAngles.elbow = d.elbow;
  targetAngles.wrist_ver = wrist_ver;
  targetAngles.wrist_rot = d.wrist_rot;
  targetAngles.gripper = d.gripper;
}

void onPositionQuery(posQueryData d) {
  braccioAngles currentAngles = braccioCurrentAngles();

  // wether braccio has reached target position
  bool positionReached = currentAngles.base == targetAngles.base &&
                         currentAngles.shoulder == targetAngles.shoulder &&
                         currentAngles.elbow == targetAngles.elbow &&
                         currentAngles.wrist_ver == targetAngles.wrist_ver &&
                         currentAngles.wrist_rot == targetAngles.wrist_rot &&
                         currentAngles.gripper == targetAngles.gripper;

  sndPacket p;
  p.id = sndPacketId::posQueryReply;
  p.data.posQueryReply = {positionReached};
  packetSerial.send((uint8_t *)&p, sizeof(p));
}

void onSetSpeed(setSpeedData d) { speed = d.speed; }
