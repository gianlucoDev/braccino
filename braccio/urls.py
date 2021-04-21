from django.urls import path, include
from rest_framework import routers

from .views import BraccioViewSet, RoutineViewSet

router = routers.DefaultRouter()
router.register(r'braccio', BraccioViewSet)
router.register(r'routines', RoutineViewSet)

app_name = 'braccio'
urlpatterns = [
    path('', include(router.urls))
]
