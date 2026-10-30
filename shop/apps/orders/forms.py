"""МОДУЛЬ 4 (ЗАКАЗЫ): формы."""

from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    """Форма создания заказа (шапка; позиции добавляются через API/админку)."""

    class Meta:
        model = Order
        fields = ["client", "comment"]
        widgets = {
            "client": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
