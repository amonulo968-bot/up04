from django.conf import settings
from django.db import models, transaction
from django.db.models import F, Sum
from django.utils import timezone

from apps.catalog.models import Product
from apps.clients.models import Client


class Order(models.Model):
    """Заказ: клиент + менеджер + список позиций."""

    class Status(models.TextChoices):
        NEW = "new", "Новый"
        CONFIRMED = "confirmed", "Подтверждён"
        COMPLETED = "completed", "Завершён"
        CANCELLED = "cancelled", "Отменён"

    client = models.ForeignKey(
        Client, on_delete=models.PROTECT,
        related_name="orders", verbose_name="Клиент",
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="orders", verbose_name="Менеджер",
    )
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    total_amount = models.DecimalField("Сумма, ₽", max_digits=12, decimal_places=2, default=0)
    comment = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    completed_at = models.DateTimeField("Завершён", null=True, blank=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ №{self.pk} — {self.client.full_name}"

    # ---------- бизнес-логика ----------
    @classmethod
    @transaction.atomic
    def create_with_items(cls, client, manager, items, comment=""):
        """Создать заказ. items = [{"product": Product, "quantity": int}, ...].
        Товар резервируется сразу: остаток уменьшается."""
        if not items:
            raise ValueError("Добавьте хотя бы одну позицию")
        order = cls.objects.create(client=client, manager=manager, comment=comment)
        for item in items:
            # блокируем строку товара, чтобы два заказа не купили один и тот же остаток
            product = Product.objects.select_for_update().get(pk=item["product"].pk)
            qty = item["quantity"]
            if not product.is_active:
                raise ValueError(f"Товар «{product.name}» снят с продажи")
            if product.stock < qty:
                raise ValueError(
                    f"Недостаточно товара «{product.name}»: в наличии {product.stock}, нужно {qty}"
                )
            product.stock -= qty
            product.save(update_fields=["stock"])
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=product.price)
        order.recalc_total()
        return order

    def recalc_total(self):
        total = sum(i.quantity * i.price for i in self.items.all())
        self.total_amount = total
        self.save(update_fields=["total_amount"])

    @transaction.atomic
    def confirm(self):
        if self.status != self.Status.NEW:
            raise ValueError("Подтвердить можно только новый заказ")
        self.status = self.Status.CONFIRMED
        self.save(update_fields=["status"])

    @transaction.atomic
    def complete(self):
        if self.status != self.Status.CONFIRMED:
            raise ValueError("Завершить можно только подтверждённый заказ")
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at"])

    @transaction.atomic
    def cancel(self):
        """Отмена: возвращаем товары на склад."""
        if self.status not in (self.Status.NEW, self.Status.CONFIRMED):
            raise ValueError(f"Нельзя отменить заказ в статусе «{self.get_status_display()}»")
        for item in self.items.all():
            Product.objects.filter(pk=item.product_id).update(stock=F("stock") + item.quantity)
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])


class OrderItem(models.Model):
    """Позиция заказа. Цена фиксируется на момент покупки."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items", verbose_name="Товар")
    quantity = models.PositiveIntegerField("Количество", default=1)
    price = models.DecimalField("Цена за шт., ₽", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

    @property
    def line_total(self):
        return self.quantity * self.price
