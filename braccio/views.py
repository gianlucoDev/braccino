from rest_framework import viewsets

from .models import Braccio, Routine
from .serializers import BraccioSerializer, RoutineSerializer


class BraccioViewSet(viewsets.ModelViewSet):
    queryset = Braccio.objects.all()
    serializer_class = BraccioSerializer


class RoutineViewSet(viewsets.ModelViewSet):
    queryset = Routine.objects.all()
    serializer_class = RoutineSerializer
