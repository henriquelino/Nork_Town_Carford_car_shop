from datetime import datetime
from random import choice

from car_sales.forms import SaleForm
from car_sales.models import Car, CarColor, CarModel, Customer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from loguru import logger


class SaleTestCase(TestCase):

    def setUp(self):
        self.sale = None
        permission = Permission.objects.get(name='Can sell cars')
        self.test_salesperson = get_user_model()(username="test salesperson", email="test_user@email.com", is_staff=True)
        self.test_salesperson.save()
        self.test_salesperson.user_permissions.add(permission)
        self.test_salesperson.refresh_from_db()

        self.test_customer = Customer(name="test customer", address="street", phone="123456789")
        self.test_customer.save()

        self.test_car = Car(name="Carro teste", price=10000, color=choice(CarColor.objects.all()), model=choice(CarModel.objects.all()))
        self.test_car.save()

        form_data = {"salesperson": self.test_salesperson, "customer": self.test_customer, "car": self.test_car, "purchase_date": datetime.now()}
        self.sales_form = SaleForm(data=form_data)
        return

    def test_save_sale_form(self):
        if self.sales_form.errors:
            logger.debug(f"{self.sales_form.errors = }")
        self.sales_form.save()
        self.assertTrue(True)
