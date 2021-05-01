import json
import shutil
import subprocess
import threading
import time
from enum import Enum

from django.http import Http404
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
    def __init__(self, name, serial_path, auto_connect=True):
        self.name = name
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


def get_boards():
    executable = shutil.which('arduino-cli')
    if not executable:
        raise FileNotFoundError('arduino-cli is not in the system path')

    result = subprocess.run(
        [executable, 'board', 'list', '--format=json'], capture_output=True, check=True)
    data = json.loads(result.stdout)

    arduinos = []
    for item in data:
        if item['protocol'] == 'serial':
            arduino = Arduino(item['boards'][0]['name'], item['address'])
            arduinos.append(arduino)

    return arduinos


REFRESH_INTERVAL = 5


class ArduinoManager:
    def __init__(self):
        self.arduinos = []
        self.thread = threading.Thread(target=self._do_refresh)
        self.thread.start()

    def _do_refresh(self):
        while True:
            self.refresh_list()
            time.sleep(REFRESH_INTERVAL)

    def refresh_list(self):
        self.arduinos = get_boards()

    def get_arduino(self, pk):
        arduino = self.arduinos[pk]
        return arduino


def get_arduino_or_404(manager, pk):
    try:
        i = int(pk)
        arduino = manager.get_arduino(i)
        return arduino
    except (ValueError, TypeError, IndexError) as error:
        raise Http404("Braccio not found") from error


ARDUINO_MANAGER = ArduinoManager()
