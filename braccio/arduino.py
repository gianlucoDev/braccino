import serial

import serial.tools.list_ports

CONNECTED_ARDUINOS = []


class ArduinoManager:
    def __init__(self):
        self.arduinos = []

    def _is_arduino(self, port):
        return "arduino" in port.description.lower()

    def refresh_list(self):
        arduinos = []

        for i, port in enumerate(serial.tools.list_ports.comports()):
            if self._is_arduino(port):
                arduinos.append({
                    'name': f'braccio{i}',
                    'serial': port.device,
                })

        self.arduinos = arduinos


ARDUINO_MANAGER = ArduinoManager()
