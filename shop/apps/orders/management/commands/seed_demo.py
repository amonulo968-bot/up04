"""Демо-данные для магазина: python manage.py seed_demo"""

import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.catalog.models import Category, Product
from apps.clients.models import Client
from apps.orders.models import Order

PRODUCTS = {
    "Смартфоны": [("Смартфон Nova X1", 29990), ("Смартфон Nova X2 Pro", 45990), ("Смартфон Lite A5", 14990)],
    "Ноутбуки": [("Ноутбук Air 14", 69990), ("Ноутбук Gamer 16", 119990)],
    "Аксессуары": [("Наушники Beat", 4990), ("Чехол Slim", 990), ("Зарядка 65W", 2490), ("Мышь Silent", 1590)],
}
CLIENTS = ["Иванов Иван", "Петрова Анна", "Сидоров Пётр", "Кузнецова Мария", "Орлов Дмитрий", "Волкова Елена"]


class Command(BaseCommand):
    help = "Создаёт демо-категории, товары, клиентов и заказы"

    def handle(self, *args, **options):
        User = get_user_model()
        manager = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if manager is None:
            raise CommandError("Сначала создайте пользователя: python manage.py createsuperuser")

        products = []
        for i, (cat_name, items) in enumerate(PRODUCTS.items()):
            cat, _ = Category.objects.get_or_create(name=cat_name)
            for j, (name, price) in enumerate(items):
                p, _ = Product.objects.get_or_create(
                    sku=f"SKU-{i}{j:02d}",
                    defaults={"category": cat, "name": name, "price": price, "stock": random.randint(3, 40)},
                )
                products.append(p)

        clients = []
        for k, name in enumerate(CLIENTS):
            c, _ = Client.objects.get_or_create(
                phone=f"+7900000{k:04d}", defaults={"full_name": name, "manager": manager}
            )
            clients.append(c)

        created = 0
        for _ in range(25):
            picked = random.sample(products, random.randint(1, 3))
            items = [{"product": p, "quantity": random.randint(1, 2)} for p in picked]
            try:
                order = Order.create_with_items(random.choice(clients), manager, items)
            except ValueError:
                continue  # не хватило остатка — пропускаем
            r = random.random()
            if r < 0.65:
                order.confirm()
                order.complete()
                # раскидываем даты завершения по последним 30 дням для графика
                when = timezone.now() - timedelta(days=random.randint(0, 29))
                Order.objects.filter(pk=order.pk).update(created_at=when, completed_at=when)
            elif r < 0.8:
                order.cancel()
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Готово: создано заказов — {created}"))
