"""МОДУЛЬ 3 (КЛИЕНТЫ): формы."""

from django import forms

from .models import Client


class ClientForm(forms.ModelForm):
    """Форма создания/редактирования клиента."""

    class Meta:
        model = Client
        fields = ["full_name", "phone", "email", "address", "birth_date", "manager"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "manager": forms.Select(attrs={"class": "form-select"}),
        }
