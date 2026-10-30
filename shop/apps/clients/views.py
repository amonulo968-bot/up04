from rest_framework import filters, viewsets

from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """CRUD для клиентов."""
    queryset = Client.objects.select_related("manager")
    serializer_class = ClientSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["full_name", "phone", "email"]
    ordering_fields = ["created_at", "full_name"]

    def perform_create(self, serializer):
        # если менеджер не указан — закрепляем клиента за создателем
        if not serializer.validated_data.get("manager"):
            serializer.save(manager=self.request.user)
        else:
            serializer.save()
