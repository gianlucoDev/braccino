import json
import shutil
import subprocess
import threading
import time

from braccio.util import Singleton
from .braccio import Braccio


def get_serial_boards():
    """
    Retieves a list of boards using the Arduino CLI

    Example output from the CLI:
    ```json
    [
        {
            "address": "/dev/ttyACM0",
            "protocol": "serial",
            "protocol_label": "Serial Port (USB)",
            "boards": [
                {
                    "name": "Arduino Mega or Mega 2560",
                    "fqbn": "arduino:avr:mega",
                    "vid": "0x2341",
                    "pid": "0x0042"
                }
            ],
            "serial_number": "95931323132351011210"
        }
    ]
    ```
    """

    executable = shutil.which('arduino-cli')
    if not executable:
        raise FileNotFoundError('arduino-cli is not in the system path')

    result = subprocess.run(
        [executable, 'board', 'list', '--format=json'], capture_output=True, check=True)
    data = json.loads(result.stdout)

    boards = []
    for item in data:
        if item['protocol'] == 'serial' and 'boards' in item:
            boards.append(item)

    return boards


REFRESH_INTERVAL = 60


class BraccioManager(metaclass=Singleton):
    def __init__(self):
        self.braccios = {}

        # start auto-refresh
        self.thread = threading.Thread(target=self._do_refresh)
        self.thread.start()

    def _do_refresh(self):
        while True:
            self.refresh()
            time.sleep(REFRESH_INTERVAL)

    def refresh(self):
        board_list = get_serial_boards()
        board_dict = {board['serial_number']: board for board in board_list}

        old_keys = set(self.braccios.keys())
        new_keys = set(board_dict.keys())

        removed = old_keys - new_keys
        for key in removed:
            braccio = self.braccios.pop(key)
            braccio.disconnect()

        added = new_keys - old_keys
        for key in added:
            board = board_dict[key]
            self.braccios[key] = Braccio(board['boards'][0]['name'],
                                         board['serial_number'], board['address'])
            self.braccios[key].connect()

    def get_by_serial(self, serial_number: str) -> Braccio:
        return self.braccios.get(serial_number)
