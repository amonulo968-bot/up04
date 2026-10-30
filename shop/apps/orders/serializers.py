from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price", "line_total"]
        read_only_fields = ["price"]  # цену берём из товара, а не от клиента API

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество должно быть не меньше 1")
        return value


class OrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.full_name", read_only=True)
    manager_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    items = OrderItemSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ["id", "client", "client_name", "manager", "manager_name",
                  "status", "status_display", "total_amount", "comment",
                  "items", "created_at", "completed_at"]
        read_only_fields = ["manager", "status", "total_amount", "created_at", "completed_at"]

    def get_manager_name(self, obj):
        return obj.manager.get_full_name() or obj.manager.username

    def create(self, validated_data):
        items = validated_data.pop("items")
        try:
            return Order.create_with_items(
                client=validated_data["client"],
                manager=validated_data["manager"],  # передаётся из view.perform_create
                items=items,
                comment=validated_data.get("comment", ""),
            )
        except ValueError as exc:
            raise serializers.ValidationError({"items": str(exc)})
