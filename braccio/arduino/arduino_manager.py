import json
import shutil
import subprocess
import threading
import time

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


ARDUINO_MANAGER = ArduinoManager()
