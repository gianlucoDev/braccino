from channels.generic.websocket import JsonWebsocketConsumer

from routines.serializers import PositionSerializer
from .arduino import BraccioManager, ContinuousStepIterator


class BraccioConsumer(JsonWebsocketConsumer):

    def connect(self):
        #pylint: disable=attribute-defined-outside-init
        self.step_iterator = None

        serial_number = self.scope['url_route']['kwargs']['serial_number']
        braccio = BraccioManager().get_by_serial(serial_number)

        if braccio is None or braccio.is_busy():
            self.close()
            return

        self.step_iterator = ContinuousStepIterator()
        braccio.run(self.step_iterator)
        self.accept()

    def disconnect(self, code):
        if self.step_iterator is not None:
            self.step_iterator.stop()

    def receive_json(self, content):
        #pylint: disable=arguments-differ

        packet_type = content["type"]
        data = content["data"]

        if packet_type == "set_position":
            self._set_position(data)
        elif packet_type == "set_speed":
            self._set_speed(data)

    def _set_position(self, data):
        serializer = PositionSerializer(data=data)
        if serializer.is_valid():
            position = serializer.validated_data
            self.step_iterator.position = position

    def _set_speed(self, data):
        speed = int(data["speed"])
        self.step_iterator.speed = speed
