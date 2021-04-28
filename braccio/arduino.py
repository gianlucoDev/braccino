import serial
import serial.tools.list_ports

from django.http import Http404


CONNECTED_ARDUINOS = []


class ArduinoManager:
    def __init__(self):
        self.arduinos = []

    def _is_arduino(self, port):
        # return "arduino" in port.description.lower()

        # TODO: actually detect arduino
        return port.device == '/dev/ttyACM0'

    def refresh_list(self):
        arduinos = []

        for i, port in enumerate(serial.tools.list_ports.comports()):
            if self._is_arduino(port):
                arduinos.append({
                    'name': f'braccio{i}',
                    'serial': port.device,
                })

        self.arduinos = arduinos

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
