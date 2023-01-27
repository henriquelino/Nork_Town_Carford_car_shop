from django import http
from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Car, CarColor, CarModel, Customer, Sales

# --------------------------------------------------


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone")


# --------------------------------------------------


@admin.register(CarColor)
class CarColorAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "color", "model", "owner")


# --------------------------------------------------


@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ("salesperson", "customer", "car", "purchase_date")

    def get_form(self, request: http.HttpRequest, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # fills the salesperson with the current user and disable the field
            form.base_fields["salesperson"].initial = request.user
            form.base_fields['salesperson'].disabled = True
        return form
