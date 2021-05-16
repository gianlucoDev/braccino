from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from routines.models import Routine
from .arduino import BraccioManager, get_braccio_or_404, routine_step_iterator
from .serializers import BraccioSerializer
from .exceptions import BraccioStatusNotOkException, BraccioBusyException


class BraccioViewSet(viewsets.ViewSet):

    def list(self, request):
        serializer = BraccioSerializer(
            BraccioManager().braccios.values(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        braccio = get_braccio_or_404(BraccioManager(), pk)
        serializer = BraccioSerializer(braccio)
        return Response(serializer.data)

    @action(methods=["POST"], detail=True, url_path='run/(?P<routine_pk>[^/.]+)')
    def run(self, request, pk=None, routine_pk=None):
        braccio = get_braccio_or_404(BraccioManager(), pk)
        routine = get_object_or_404(Routine, pk=routine_pk)

        if not braccio.connection_status.ok:
            raise BraccioStatusNotOkException()

        if braccio.is_busy():
            raise BraccioBusyException()

        braccio.run(routine_step_iterator(routine))
        return Response({"ok": True})
