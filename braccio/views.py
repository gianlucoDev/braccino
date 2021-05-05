import time
import threading
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from routines.models import Routine
from .arduino import ArduinoManager, get_arduino_or_404
from .serializers import BraccioSerializer

def _wait_for_position(arduino, expected):
    current = arduino.get_current_position()
    while current != expected:
        current = arduino.get_current_position()
        time.sleep(500 / 1000)

def _run(arduino, routine):
    for step in routine.steps.all():
        pos = (step.m1, step.m2, step.m3, step.m4, step.m5, step.m6)

        arduino.set_target_position(*pos)
        _wait_for_position(arduino, pos)
        time.sleep(step.delay / 1000)


class BraccioViewSet(viewsets.ViewSet):

    def list(self, request):
        serializer = BraccioSerializer(
            ArduinoManager().arduinos.values(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        arduino = get_arduino_or_404(ArduinoManager(), pk)
        serializer = BraccioSerializer(arduino)
        return Response(serializer.data)

    @action(methods=["POST"], detail=True, url_path='run/(?P<routine_pk>[^/.]+)')
    def run(self, request, pk=None, routine_pk=None):
        braccio = get_arduino_or_404(ArduinoManager(), pk)
        routine = get_object_or_404(Routine, pk=routine_pk)

        t = threading.Thread(target=_run, args=(braccio, routine))
        t.start()

        return Response({"ok": True})
