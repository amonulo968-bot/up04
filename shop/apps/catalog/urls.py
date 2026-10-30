from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import CategoryViewSet, ProductViewSet

router = SimpleRouter()
router.register("categories", CategoryViewSet, basename="categories")
router.register("products", ProductViewSet, basename="products")

urlpatterns = [
    path("", include(router.urls)),
]
