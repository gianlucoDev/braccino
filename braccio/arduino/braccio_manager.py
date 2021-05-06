import shutil
import subprocess
import threading

from braccio.util.singleton import Singleton
from braccio.util.json import json_iter
from .braccio import Braccio


class BraccioManager(metaclass=Singleton):
    def __init__(self):
        self.braccios = {}

        # watch for board changes
        self.thread = threading.Thread(target=self._listen_for_updates)
        self.thread.start()

    def _listen_for_updates(self):
        executable = shutil.which('arduino-cli')
        if not executable:
            raise FileNotFoundError('arduino-cli is not in the system path')

        process = subprocess.Popen(
            [executable, 'board', 'list', '--watch', '--format=json'],
            stdout=subprocess.PIPE, universal_newlines=True)

        for item in json_iter(process.stdout):
            if item['type'] == 'add':
                self._on_connect(item)
            elif item['type'] == 'remove':
                self._on_disconnect(item)

    def _on_connect(self, board):
        name = board['boards'][0]['name']
        serial_no = board['serial_number']
        address = board['address']

        self.braccios[serial_no] = Braccio(name, serial_no, address)
        self.braccios[serial_no].connect()

    def _on_disconnect(self, board):
        address = board['address']

        for braccio in self.braccios.values():
            if braccio.serial_path == address:
                braccio.disconnect()
                return

    def get_by_serial(self, serial_number: str) -> Braccio:
        return self.braccios.get(serial_number)
