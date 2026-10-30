from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """Заказы. Удаления и правки нет — только смена статуса действиями:
      POST /api/orders/{id}/confirm/   — подтвердить
      POST /api/orders/{id}/complete/  — завершить
      POST /api/orders/{id}/cancel/    — отменить (товар вернётся на склад)
    """
    queryset = Order.objects.select_related("client", "manager").prefetch_related("items__product")
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "client", "manager"]
    search_fields = ["client__full_name", "client__phone"]
    ordering_fields = ["created_at", "total_amount"]

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

    def _change_status(self, method_name):
        order = self.get_object()
        try:
            getattr(order, method_name)()
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        order.refresh_from_db()
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        return self._change_status("confirm")

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        return self._change_status("complete")

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        return self._change_status("cancel")
