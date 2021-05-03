from django.http import Http404
from .arduino_manager import ArduinoManager


def get_arduino_or_404(manager: ArduinoManager, serial_number: str):
    arduino = manager.get_arduino(serial_number)
    if not arduino:
        raise Http404("Braccio not found")
    return arduino
