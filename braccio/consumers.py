from channels.generic.websocket import JsonWebsocketConsumer

from braccio.serializers import BraccioPositionUpdateCommandSerializer
from .arduino import BraccioManager, RepeatingStepIterator


class BraccioConsumer(JsonWebsocketConsumer):

    def connect(self):
        #pylint: disable=attribute-defined-outside-init
        self.step_iterator = None

        serial_number = self.scope['url_route']['kwargs']['serial_number']
        braccio = BraccioManager().get_by_serial(serial_number)

        if braccio is None or braccio.is_busy():
            self.close()
            return

        self.step_iterator = RepeatingStepIterator()
        braccio.run(self.step_iterator)
        self.accept()

    def disconnect(self, code):
        if self.step_iterator is not None:
            self.step_iterator.stop()

    def receive_json(self, content):
        #pylint: disable=arguments-differ

        packet_type = content["type"]
        data = content["data"]

        if packet_type == "update":
            self._update(data)
        else:
            raise ValueError("Unknow packet type")

    def _update(self, data):
        serializer = BraccioPositionUpdateCommandSerializer(data=data)
        if serializer.is_valid():
            self.step_iterator.update(serializer.validated_data)
