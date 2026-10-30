from datetime import timedelta

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.catalog.models import Product
from apps.orders.models import Order, OrderItem

LOW_STOCK = 5  # «заканчивается» — остаток не больше этого числа


class ReportService:
    """Сервис отчётов. Выручка считается по завершённым заказам."""

    @staticmethod
    def _completed(days: int):
        since = timezone.now() - timedelta(days=days)
        return Order.objects.filter(status=Order.Status.COMPLETED, completed_at__gte=since)

    @staticmethod
    def kpi(days: int = 30) -> dict:
        """Главные KPI."""
        completed = ReportService._completed(days)
        revenue = completed.aggregate(total=Sum("total_amount"))["total"] or 0
        count = completed.count()
        return {
            "revenue": float(revenue),
            "orders_count": count,
            "avg_check": float(revenue) / count if count else 0,
            "in_stock_products": Product.objects.filter(is_active=True, stock__gt=0).count(),
            "period_days": days,
        }

    @staticmethod
    def revenue_by_day(days: int = 30) -> list:
        """Выручка по дням."""
        rows = (
            ReportService._completed(days)
            .annotate(day=TruncDate("completed_at"))
            .values("day")
            .annotate(total=Sum("total_amount"))
            .order_by("day")
        )
        return [{"date": str(r["day"]), "total": float(r["total"])} for r in rows]

    @staticmethod
    def top_products(limit: int = 5) -> list:
        """Топ товаров по количеству продаж (завершённые заказы)."""
        line_sum = ExpressionWrapper(
            F("quantity") * F("price"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
        rows = (
            OrderItem.objects.filter(order__status=Order.Status.COMPLETED)
            .values("product__name", "product__category__name")
            .annotate(qty=Sum("quantity"), revenue=Sum(line_sum))
            .order_by("-qty")[:limit]
        )
        return [
            {
                "product": r["product__name"],
                "category": r["product__category__name"],
                "qty": r["qty"],
                "revenue": float(r["revenue"]),
            }
            for r in rows
        ]

    @staticmethod
    def manager_load(days: int = 30) -> list:
        """Загрузка менеджеров (без отменённых заказов)."""
        since = timezone.now() - timedelta(days=days)
        rows = (
            Order.objects.filter(created_at__gte=since)
            .exclude(status=Order.Status.CANCELLED)
            .values("manager__username")
            .annotate(orders=Count("id"), total=Sum("total_amount"))
            .order_by("-orders")
        )
        return [
            {"manager": r["manager__username"], "orders": r["orders"], "total": float(r["total"] or 0)}
            for r in rows
        ]

    @staticmethod
    def stock_status() -> list:
        """Состояние склада."""
        active = Product.objects.filter(is_active=True)
        return [
            {"status": "В наличии", "count": active.filter(stock__gt=LOW_STOCK).count()},
            {"status": "Заканчивается", "count": active.filter(stock__gt=0, stock__lte=LOW_STOCK).count()},
            {"status": "Нет в наличии", "count": active.filter(stock=0).count()},
        ]
