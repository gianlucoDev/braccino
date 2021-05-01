from django.http import Http404
from .arduino_manager import ArduinoManager


def get_arduino_or_404(manager: ArduinoManager, pk):
    try:
        i = int(pk)
        arduino = manager.get_arduino(i)
        return arduino
    except (ValueError, TypeError, IndexError) as error:
        raise Http404("Braccio not found") from error
