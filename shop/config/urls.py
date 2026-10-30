from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # === МОДУЛЬ 1: АВТОРИЗАЦИЯ ===
    path("api/auth/", include("apps.accounts.urls")),

    # === МОДУЛЬ 2: КАТАЛОГ (categories/, products/) ===
    path("api/", include("apps.catalog.urls")),

    # === МОДУЛЬ 3: КЛИЕНТЫ (clients/) ===
    path("api/", include("apps.clients.urls")),

    # === МОДУЛЬ 4: ЗАКАЗЫ (orders/) ===
    path("api/", include("apps.orders.urls")),

    # === МОДУЛЬ 5: ОТЧЁТЫ ===
    path("api/reports/", include("apps.reports.urls")),

    # Вход через браузер DRF (для тестирования)
    path("api/drf-login/", include("rest_framework.urls")),
]
