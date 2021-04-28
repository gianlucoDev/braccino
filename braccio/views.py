from django.http import Http404
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Routine
from .serializers import BraccioSerializer, RoutineSerializer

from .arduino import ARDUINO_MANAGER


class BraccioViewSet(viewsets.ViewSet):

    def list(self, request):
        ARDUINO_MANAGER.refresh_list()

        serializer = BraccioSerializer(ARDUINO_MANAGER.arduinos, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        ARDUINO_MANAGER.refresh_list()

        try:
            i = int(pk)
            arduino = ARDUINO_MANAGER.arduinos[i]
        except (ValueError, TypeError, IndexError) as error:
            raise Http404("Braccio not found") from error

        serializer = BraccioSerializer(arduino)
        return Response(serializer.data)


class RoutineViewSet(viewsets.ModelViewSet):
    queryset = Routine.objects.all()
    serializer_class = RoutineSerializer
