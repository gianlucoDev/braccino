from dataclasses import dataclass

import shutil
import subprocess
import json
import threading
import time

from django.http import Http404

REFRESH_INTERVAL = 5


@dataclass
class Arduino:
    name: str
    serial: str


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
        arduino = ARDUINO_MANAGER.arduinos[pk]
        return arduino


def get_arduino_or_404(manager, pk):
    try:
        i = int(pk)
        arduino = manager.get_arduino(i)
        return arduino
    except (ValueError, TypeError, IndexError) as error:
        raise Http404("Braccio not found") from error


ARDUINO_MANAGER = ArduinoManager()
