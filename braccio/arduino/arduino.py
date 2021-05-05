import time
from enum import Enum

from serial import Serial, to_bytes, SerialException

START_MARKER = b'<'  # 0x3C
END_MARKER = b'>'  # 0x3E

# how many seconds should the Django app wait for the
# Arduino to be ready before showing an error
MAX_CONNECTION_WAIT_TIME = 20


class ConnectionStatus(Enum):
    NOT_CONNECTED = (0, False)
    CONNECTING = (1, False)
    ERR_NO_SERIAL = (2, False)
    ERR_NO_HANDSHAKE = (3, False)
    CONNECTED = (4, True)

    def __new__(cls, value, _ok):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, _value, ok):
        self.ok = ok


class Arduino:
    def __init__(self, name, serial_number, serial_path):
        self.name = name
        self.serial_number = serial_number

        self.serial_path = serial_path
        self.serial = None
        self.status = ConnectionStatus.NOT_CONNECTED

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

    def _wait_ready(self):
        start_time = time.time()

        while True:
            data = self._read_packet()

            if data is not None:
                if data == to_bytes([0x00, 0xFF]):
                    self.status = ConnectionStatus.CONNECTED
                else:
                    self.status = ConnectionStatus.ERR_NO_HANDSHAKE
                return

            elapsed_time = time.time() - start_time
            if elapsed_time > MAX_CONNECTION_WAIT_TIME:
                self.status = ConnectionStatus.ERR_NO_HANDSHAKE
                return

    def connect(self):
        if self.status != ConnectionStatus.NOT_CONNECTED:
            raise ValueError("Serial port already open")

        self.status = ConnectionStatus.CONNECTING
        try:
            self.serial = Serial(self.serial_path, 9600, timeout=1)
        except SerialException:
            self.status = ConnectionStatus.ERR_NO_SERIAL
            return

        self._wait_ready()

    def disconnect(self):
        if self.serial.is_open:
            self.serial.close()

    def set_target_position(self, m1, m2, m3, m4, m5, m6):
        self._write_packet([0x01, m1, m2, m3, m4, m5, m6])

    def get_current_position(self):
        self._write_packet([0x02])
        data = self._read_packet()

        # ignore fist byte because it's packet ID
        # return bytes 1-6 as m1, m2, m3, m4, m5, m6
        return tuple(data[1:7])
