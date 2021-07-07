// make sure there are no alignment bytes, so I can copy directly the received
// buffer in the packet struct
#pragma pack(push, 1)

/* django -> arduino */

enum rcvPacketId : uint8_t {
  setAngles = 0x01,
  posQuery = 0x02,
  setSpeed = 0x03,
};

struct setAnglesData {
  uint8_t base;
  uint8_t shoulder;
  uint8_t elbow;
  uint8_t wrist_ver;
  uint8_t wrist_rot;
  uint8_t gripper;
};

struct posQueryData {};

struct setSpeedData {
  uint8_t speed;
};

struct rcvPacket {
  rcvPacketId id;
  union {
    setAnglesData setAngles;
    posQueryData posQuery;
    setSpeedData setSpeed;
  } data;
};

/* django <- arduino */

enum sndPacketId : uint8_t {
  hello = 0x00,
  posQueryReply = 0x02,
};

struct helloData {
  uint8_t magicByte;
};

struct posQueryReplyData {
  bool onPosition;
};

struct sndPacket {
  sndPacketId id;
  union {
    helloData hello;
    posQueryReplyData posQueryReply;
  } data;
};

#pragma pack(pop)
