from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Routine
from .serializers import BraccioSerializer, RoutineSerializer

from .arduino import ARDUINO_MANAGER, get_arduino_or_404


class BraccioViewSet(viewsets.ViewSet):

    def list(self, request):
        ARDUINO_MANAGER.refresh_list()
        serializer = BraccioSerializer(ARDUINO_MANAGER.arduinos, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        ARDUINO_MANAGER.refresh_list()
        arduino = get_arduino_or_404(ARDUINO_MANAGER, pk)
        serializer = BraccioSerializer(arduino)
        return Response(serializer.data)

    @action(methods=["POST"], detail=True, url_path='run/(?P<routine_pk>[^/.]+)')
    def run(self, request, pk=None, routine_pk=None):
        ARDUINO_MANAGER.refresh_list()
        braccio = get_arduino_or_404(ARDUINO_MANAGER, pk)
        routine = get_object_or_404(Routine, pk=routine_pk)

        print(routine)
        print(braccio)

        return Response({"ok": True})


class RoutineViewSet(viewsets.ModelViewSet):
    queryset = Routine.objects.all()
    serializer_class = RoutineSerializer
