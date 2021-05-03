import time
from enum import Enum

from serial import Serial, to_bytes, SerialException

START_MARKER = b'<'  # 0x3C
END_MARKER = b'>'  # 0x3E


class ArduinoStatus(Enum):
    NOT_CONNECTED = (0, False)
    ERR_NO_SERIAL = (1, False)
    ERR_NO_HANDSHAKE = (2, False)
    CONNECTED = (3, True)

    def __new__(cls, value, _ok):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, _value, ok):
        self.ok = ok


class Arduino:
    def __init__(self, name, serial_number, serial_path, auto_connect=True):
        self.name = name
        self.serial_number = serial_number

        self.serial_path = serial_path
        self.serial = None
        self.status = ArduinoStatus.NOT_CONNECTED
        if auto_connect:
            self.connect()

    def _write_packet(self, data):
        data = to_bytes(data)
        packet = START_MARKER + data + END_MARKER
        self.serial.write(packet)

    def _read_packet(self):
        packet = self.serial.read_until(expected=END_MARKER)
        if not packet:
            return None

        # remove start marker, and anything before it
        parts = packet.split(START_MARKER)
        if len(parts) != 2:
            return None

        _, data = parts
        return data

    def _handshake(self):
        self._write_packet([0x00])
        data = self._read_packet()

        if data == to_bytes([0x00, 0xFF]):
            self.status = ArduinoStatus.CONNECTED
        else:
            self.status = ArduinoStatus.ERR_NO_HANDSHAKE

    def connect(self):
        if self.status != ArduinoStatus.NOT_CONNECTED:
            raise ValueError("Serial port already open")

        try:
            self.serial = Serial(self.serial_path, 9600, timeout=1)
        except SerialException:
            self.status = ArduinoStatus.ERR_NO_SERIAL
            return

        # give the Arduino time to reset when the serial connection is opened
        time.sleep(1)
        self._handshake()

    def disconnect(self):
        if self.serial.is_open:
            self.serial.close()
