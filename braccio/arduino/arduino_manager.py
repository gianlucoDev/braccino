import json
import shutil
import subprocess
import threading
import time

from braccio.util import Singleton
from .arduino import Arduino


def get_boards():
    executable = shutil.which('arduino-cli')
    if not executable:
        raise FileNotFoundError('arduino-cli is not in the system path')

    result = subprocess.run(
        [executable, 'board', 'list', '--format=json'], capture_output=True, check=True)
    data = json.loads(result.stdout)

    arduinos = []
    for item in data:
        if item['protocol'] == 'serial' and 'boards' in item:
            arduino = Arduino(item['boards'][0]['name'], item['serial_number'],
                              item['address'], auto_connect=False)
            arduinos.append(arduino)

    return arduinos


REFRESH_INTERVAL = 60


class ArduinoManager(metaclass=Singleton):
    def __init__(self):
        self.arduinos = {}

        # start auto-refresh
        self.thread = threading.Thread(target=self._do_refresh)
        self.thread.start()

    def _do_refresh(self):
        while True:
            self.refresh()
            time.sleep(REFRESH_INTERVAL)

    def refresh(self):
        board_list = get_boards()
        board_dict = {arduino.serial_number: arduino for arduino in board_list}

        old_keys = set(self.arduinos.keys())
        new_keys = set(board_dict.keys())

        removed = old_keys - new_keys
        for key in removed:
            arduino = self.arduinos.pop(key)
            arduino.disconnect()

        added = new_keys - old_keys
        for key in added:
            self.arduinos[key] = board_dict[key]
            self.arduinos[key].connect()

    def get_arduino(self, serial_number: str) -> Arduino:
        return self.arduinos.get(serial_number)
