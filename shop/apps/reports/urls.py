from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("kpi/", views.KPIApiView.as_view(), name="kpi"),
    path("revenue/", views.RevenueByDayApiView.as_view(), name="revenue"),
    path("top-products/", views.TopProductsApiView.as_view(), name="top_products"),
    path("manager-load/", views.ManagerLoadApiView.as_view(), name="manager_load"),
    path("stock/", views.StockApiView.as_view(), name="stock"),
]
