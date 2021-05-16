from routines.serializers import PositionSerializer
from channels.generic.websocket import JsonWebsocketConsumer

from .arduino import BraccioController, BraccioManager


class BraccioConsumer(JsonWebsocketConsumer, BraccioController):

    def connect(self):
        #pylint: disable=attribute-defined-outside-init

        serial_number = self.scope['url_route']['kwargs']['serial_number']
        self.braccio = BraccioManager().get_by_serial(serial_number)
        self.running = True

        if self.braccio is None or self.braccio.is_busy():
            self.close()
        else:
            self.braccio.run_action(self)
            self.accept()

    def disconnect(self, code):
        self.running = False

    def receive_json(self, content):
        #pylint: disable=arguments-differ

        serializer = PositionSerializer(data=content)
        if serializer.is_valid():
            position = serializer.validated_data
            self.braccio.set_target_position(position)

    def is_running(self) -> bool:
        return self.running

    @property
    def name(self):
        return "Remote control"

    def start(self):
        pass
