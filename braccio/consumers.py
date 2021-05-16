from channels.generic.websocket import JsonWebsocketConsumer

from .arduino import BraccioManager


class BraccioConsumer(JsonWebsocketConsumer):

    def connect(self):
        #pylint: disable=attribute-defined-outside-init

        serial_number = self.scope['url_route']['kwargs']['serial_number']
        self.braccio = BraccioManager().get_by_serial(serial_number)

        if self.braccio is None or self.braccio.is_busy():
            self.close()
        else:
            self.accept()

    def receive_json(self, content):
        #pylint: disable=arguments-differ

        # echo
        self.send_json(content)
