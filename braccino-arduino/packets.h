
/* django -> arduino */

const byte SETPOS_ID = 0x01;
const byte POS_QUERY_ID = 0x02;
const byte SETSPEED_ID = 0x03;

/* django <- arduino */

const byte HELLO_ID = 0x00;
const byte SETPOS_REPLY_ID = 0x01;
const byte POS_QUERY_REPLY_ID = 0x02;

// NOTE: if a packet contains only the ID and no data then its useless to define
// a struct

#pragma pack(push, 1)

/* django -> arduino */

struct setposPacket {
  uint8_t id;
  int16_t x;
  int16_t y;
  int16_t z;
  int16_t attack_angle;
  uint8_t wrist_rot;
  uint8_t gripper;
};

struct setspeedPacket {
  uint8_t id;
  uint8_t speed;
};

/* django <- arduino */

struct helloPacket {
  uint8_t id;
  uint8_t magicByte;
};

struct setpostReplyPacket {
  uint8_t id;
  bool ok;
};

struct posQueryReplyPacket {
  uint8_t id;
  bool onPosition;
};

#pragma pack(pop)
