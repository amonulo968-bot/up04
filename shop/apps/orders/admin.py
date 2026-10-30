"""МОДУЛЬ 4 (ЗАКАЗЫ): админка."""

from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("product",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "manager", "total_amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("client__full_name", "client__phone")
    readonly_fields = ("created_at", "completed_at")
    inlines = [OrderItemInline]
