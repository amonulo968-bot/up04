from django.db import models


class Category(models.Model):
    """Категория товаров."""
    name = models.CharField("Название", max_length=100, unique=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар."""
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        related_name="products", verbose_name="Категория",
    )
    name = models.CharField("Название", max_length=200)
    sku = models.CharField("Артикул", max_length=50, unique=True)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена, ₽", max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField("Остаток, шт.", default=0)
    is_active = models.BooleanField("Продаётся", default=True)
    created_at = models.DateTimeField("Добавлен", auto_now_add=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def in_stock(self):
        return self.is_active and self.stock > 0
