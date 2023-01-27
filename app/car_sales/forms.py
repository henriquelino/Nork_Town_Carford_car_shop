from datetime import datetime
from typing import Any

from django import forms

from .models import Car, Customer, Sales


class CarForm(forms.ModelForm):

    class Meta:
        model = Car
        fields = ("name", "price", "color", "model")


class SaleForm(forms.ModelForm):

    class Meta:
        model = Sales
        fields = ("salesperson", "customer", "car", "purchase_date")


class SaleFormCreate(SaleForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['purchase_date'].initial = datetime.now()
        self.fields['car'].queryset = Car.objects.filter(owner=None)


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ("name", "address", "phone")
