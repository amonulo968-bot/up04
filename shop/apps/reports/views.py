from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsDirectorOrAdmin

from .services import ReportService


def _int_param(request, name, default, min_value=1, max_value=3650):
    """Безопасно читаем числовой GET-параметр (мусор -> значение по умолчанию)."""
    try:
        value = int(request.query_params.get(name, default))
    except (TypeError, ValueError):
        return default
    return max(min_value, min(value, max_value))


class ReportBaseView(APIView):
    permission_classes = [IsDirectorOrAdmin]


class KPIApiView(ReportBaseView):
    """GET /api/reports/kpi/?days=30"""
    def get(self, request):
        return Response(ReportService.kpi(_int_param(request, "days", 30)))


class RevenueByDayApiView(ReportBaseView):
    """GET /api/reports/revenue/?days=30"""
    def get(self, request):
        return Response(ReportService.revenue_by_day(_int_param(request, "days", 30)))


class TopProductsApiView(ReportBaseView):
    """GET /api/reports/top-products/?limit=5"""
    def get(self, request):
        return Response(ReportService.top_products(_int_param(request, "limit", 5, max_value=100)))


class ManagerLoadApiView(ReportBaseView):
    """GET /api/reports/manager-load/?days=30"""
    def get(self, request):
        return Response(ReportService.manager_load(_int_param(request, "days", 30)))


class StockApiView(ReportBaseView):
    """GET /api/reports/stock/"""
    def get(self, request):
        return Response(ReportService.stock_status())
