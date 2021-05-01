from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from routines.models import Routine
from .arduino import ARDUINO_MANAGER, get_arduino_or_404
from .serializers import BraccioSerializer

class BraccioViewSet(viewsets.ViewSet):

    def list(self, request):
        serializer = BraccioSerializer(ARDUINO_MANAGER.arduinos, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        arduino = get_arduino_or_404(ARDUINO_MANAGER, pk)
        serializer = BraccioSerializer(arduino)
        return Response(serializer.data)

    @action(methods=["POST"], detail=True, url_path='run/(?P<routine_pk>[^/.]+)')
    def run(self, request, pk=None, routine_pk=None):
        braccio = get_arduino_or_404(ARDUINO_MANAGER, pk)
        routine = get_object_or_404(Routine, pk=routine_pk)

        print(routine)
        print(braccio)

        return Response({"ok": True})
