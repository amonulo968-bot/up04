"""ViewSet автоматически создаёт все CRUD-эндпоинты:
  GET    /api/products/        — список
  POST   /api/products/        — создать
  GET    /api/products/{id}/   — детали
  PUT    /api/products/{id}/   — обновить
  DELETE /api/products/{id}/   — удалить
"""

from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD для категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD для товаров с фильтрами, поиском и сортировкой."""
    queryset = Product.objects.select_related("category")
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "sku", "category__name"]
    ordering_fields = ["price", "stock", "name", "created_at"]
