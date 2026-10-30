from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ClientViewSet

router = SimpleRouter()
router.register("clients", ClientViewSet, basename="clients")

urlpatterns = [
    path("", include(router.urls)),
]
