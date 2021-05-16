from channels.generic.websocket import JsonWebsocketConsumer

from routines.serializers import PositionSerializer
from .arduino import BraccioManager, ContinuousStepIterator


class BraccioConsumer(JsonWebsocketConsumer):

    def connect(self):
        #pylint: disable=attribute-defined-outside-init

        serial_number = self.scope['url_route']['kwargs']['serial_number']
        braccio = BraccioManager().get_by_serial(serial_number)

        if braccio is None or braccio.is_busy():
            self.close()
            return

        self.step_iterator = ContinuousStepIterator()
        braccio.run(self.step_iterator)
        self.accept()

    def disconnect(self, code):
        self.step_iterator.stop()

    def receive_json(self, content):
        #pylint: disable=arguments-differ

        serializer = PositionSerializer(data=content)
        if serializer.is_valid():
            position = serializer.validated_data
            self.step_iterator.position(position)
