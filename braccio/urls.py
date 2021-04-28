from django.urls import path, include
from rest_framework import routers

from .views import BraccioViewSet, RoutineViewSet


class OptionalSlashRouter(routers.DefaultRouter):
    """
    A router that will work with endpoints both with and without a trailing slash.
    """

    def __init__(self):
        super().__init__()
        self.trailing_slash = '/?'


router = OptionalSlashRouter()
router.register(r'braccio', BraccioViewSet, basename='braccio')
router.register(r'routines', RoutineViewSet)

app_name = 'braccio'
urlpatterns = [
    path('', include(router.urls))
]
