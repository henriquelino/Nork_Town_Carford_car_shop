from datetime import datetime
from random import choice

from car_sales.admin import SalesAdmin
from car_sales.models import Car, CarColor, CarModel, Customer, Sales
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from loguru import logger


class MockRequest:
    pass


class MockSuperUser:

    def __init__(self, is_superuser: bool):
        self.is_superuser = is_superuser

    def has_perm(self, perm, obj=None):
        return True


class SaleTestCase(TestCase):

    def setUp(self):
        self.sale = None
        self.site = AdminSite()

        permission = Permission.objects.get(name='Can sell cars')
        self.test_salesperson = get_user_model()(username="test salesperson", email="test_user@email.com", is_staff=True)
        self.test_salesperson.save()
        self.test_salesperson.user_permissions.add(permission)
        self.test_salesperson.refresh_from_db()

        self.test_customer = Customer(name="test customer", address="street", phone="123456789")
        self.test_customer.save()

        self.test_car = Car(name="Carro teste", price=10000, color=choice(CarColor.objects.all()), model=choice(CarModel.objects.all()))
        self.test_car.save()

        model_data = {
            "salesperson": self.test_salesperson,
            "customer": self.test_customer,
            "car": self.test_car,
            "purchase_date": datetime.now(),
        }
        self.sales_model = Sales(**model_data)
        self.my_model_admin: SalesAdmin = SalesAdmin(model=Sales, admin_site=AdminSite())

        return

    def test_default_fields_superuser(self):

        request = MockRequest()
        request.user = MockSuperUser(is_superuser=True)
        ma = SalesAdmin(Sales, self.site)
        self.assertEqual(list(ma.get_form(request).base_fields), ['salesperson', 'customer', 'car', 'purchase_date'])

        self.assertEqual(list(ma.get_fields(request)), ['salesperson', 'customer', 'car', 'purchase_date'])

        self.assertEqual(list(ma.get_fields(request, self.sales_model)), ['salesperson', 'customer', 'car', 'purchase_date'])

    def test_default_fields(self):

        request = MockRequest()
        request.user = MockSuperUser(is_superuser=False)
        ma = SalesAdmin(Sales, self.site)
        self.assertEqual(list(ma.get_form(request).base_fields), ['salesperson', 'customer', 'car', 'purchase_date'])

        self.assertEqual(list(ma.get_fields(request)), ['salesperson', 'customer', 'car', 'purchase_date'])

        self.assertEqual(list(ma.get_fields(request, self.sales_model)), ['salesperson', 'customer', 'car', 'purchase_date'])
