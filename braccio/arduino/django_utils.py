from django.http import Http404
from .braccio_manager import BraccioManager

def get_braccio_or_404(manager: BraccioManager, serial_number: str):
    arduino = manager.get_by_serial(serial_number)
    if not arduino:
        raise Http404("Braccio not found")
    return arduino
