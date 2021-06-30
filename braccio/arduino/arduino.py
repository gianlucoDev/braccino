from enum import Enum
import logging
import struct

from serial import Serial, to_bytes, SerialException
from cobs import cobs

logger = logging.getLogger(__name__)

# the 0 byte signals the end of a packet
END_MARKER = b'\x00'

# django <- arduino
HELLO_ID = 0x00

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
        self.connection_status = ConnectionStatus.NOT_CONNECTED

    def _write_packet(self, data):
        data = to_bytes(data)
        packet = cobs.encode(data) + END_MARKER
        self.serial.write(packet)

    def _read_packet(self, timeout=None):
        self.serial.timeout = timeout

        packet = self.serial.read_until(expected=END_MARKER)
        if not packet:
            return None

        packet = packet[:-1]  # remove trailing 0 byte
        data = cobs.decode(packet)
        return data

    def _wait_ready(self):
        data = self._read_packet(timeout=MAX_CONNECTION_WAIT_TIME)

        if data is None:
            logger.error('Arduino at port %s took more than %s seconds to send "hello" message',
                         self.serial_path, MAX_CONNECTION_WAIT_TIME)
            self.connection_status = ConnectionStatus.ERR_NO_HANDSHAKE
            return

        packet_id, confirmation_byte = struct.unpack('<BB', data)
        if packet_id == HELLO_ID and confirmation_byte == 0xAA:
            self.connection_status = ConnectionStatus.CONNECTED
        else:
            logger.error(
                'Arduino at port %s sent malformed "hello" message', self.serial_path)
            self.connection_status = ConnectionStatus.ERR_NO_HANDSHAKE

    def connect(self):
        if self.connection_status != ConnectionStatus.NOT_CONNECTED:
            raise ValueError("Serial port already open")

        self.connection_status = ConnectionStatus.CONNECTING
        try:
            self.serial = Serial(self.serial_path, 38400)
        except SerialException:
            logger.exception('Could not open serial port %s', self.serial_path)
            self.connection_status = ConnectionStatus.ERR_NO_SERIAL
            return

        self._wait_ready()

    def disconnect(self):
        if self.serial is not None and self.serial.is_open:
            self.serial.close()
            self.connection_status = ConnectionStatus.NOT_CONNECTED
