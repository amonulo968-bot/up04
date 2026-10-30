from rest_framework import serializers

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ["id", "full_name", "phone", "email", "address", "birth_date",
                  "manager", "manager_name", "created_at"]
        read_only_fields = ["created_at"]
        # уникальность телефона DRF проверяет сам (unique=True в модели)
        extra_kwargs = {"phone": {"error_messages": {"unique": "Клиент с таким телефоном уже есть"}}}

    def get_manager_name(self, obj):
        if obj.manager is None:
            return None
        return obj.manager.get_full_name() or obj.manager.username
