from channels.generic.websocket import JsonWebsocketConsumer

from .arduino import BraccioManager, get_braccio_or_404


class BraccioConsumer(JsonWebsocketConsumer):

    def connect(self):
        #pylint: disable=attribute-defined-outside-init

        serial_number = self.scope['url_route']['kwargs']['serial_number']
        braccio = BraccioManager().get_by_serial(serial_number)

        if braccio is not None:
            self.braccio = get_braccio_or_404(BraccioManager(), serial_number)
            self.accept()
        else:
            self.close(code=404)

    def receive_json(self, content):
        #pylint: disable=arguments-differ

        # echo
        self.send_json(content)
