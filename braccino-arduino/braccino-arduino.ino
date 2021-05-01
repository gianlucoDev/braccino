const byte startMarker = 0x3C;
const byte endMarker = 0x3E;

const byte numBytes = 32;
byte receivedBytes[numBytes];
byte numReceived = 0;

boolean newData = false;

void setup() { Serial.begin(9600); }

void loop() {
  receiveData();
  handlePacket();
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

const byte PING_ID = 0x00;

void handlePacket() {
  if (!newData) return;

  switch (receivedBytes[0]) {
    case PING_ID:
      handlePing();
      break;
  }

  newData = false;
}

void handlePing() {
  byte ping_data[] = {startMarker, 0x00, 0xFF, endMarker};
  Serial.write(ping_data, 3);
}
