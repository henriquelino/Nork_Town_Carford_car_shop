from datetime import datetime
from random import choice, randint

from car_sales.models import Car, CarColor, CarModel, Customer, Sales, User
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.db.utils import IntegrityError
from django.test import TestCase
from loguru import logger


class NamesTestCase(TestCase):

    def setUp(self):
        self.test_salesperson = User(username="test salesperson", email="test_user@email.com", is_staff=True)
        self.test_customer = Customer(name="test customer", address="street", phone="123456789")

        self.car_data = dict(
            name=f"Carro teste n{randint(1000, 9999)}",
            price=randint(1000,
                          10000),
            color=choice(CarColor.objects.filter(name="yellow")),
            model=choice(CarModel.objects.filter(name="hatch"))
        )

        self.test_car = Car(**self.car_data)
        self.test_car.save()

    def test_customer_name(self):
        self.assertEqual(str(self.test_customer), "test customer")

    def test_car_name(self):
        name = f"{self.car_data['color']} {self.car_data['model']} {self.car_data['name']} @ ${self.car_data['price']}"
        self.assertEqual(str(self.test_car), name)

    def test_car_model_name(self):
        self.assertEqual(str(self.test_car.model), "hatch")

    def test_car_color_name(self):
        self.assertEqual(str(self.test_car.color), "yellow")


class MaximumCarsPerPersonTestCase(TestCase):

    def setUp(self):
        self.sale = None
        self.test_salesperson = User(username="test salesperson", email="test_user@email.com", is_staff=True)
        permission = Permission.objects.get(name='Can sell cars')
        self.test_salesperson.save()
        self.test_salesperson.user_permissions.add(permission)
        self.test_salesperson.refresh_from_db()

        self.test_customer = Customer(name="test customer", address="street", phone="123456789")
        self.test_customer.save()

        self.sale_models: list[Sales] = []
        self.test_cars: list[Car] = []

        return

    def test_sell_four_cars(self):
        self.assertEqual(Car.objects.filter(owner=self.test_customer).count(), 0)

        with self.assertRaises(IntegrityError):
            for _ in range(5):

                test_car = Car(name=f"Carro teste n{randint(1000, 9999)}", price=randint(1000, 10000), color=choice(CarColor.objects.all()), model=choice(CarModel.objects.all()))
                test_car.save()
                self.test_cars.append(test_car)

                model_data = {
                    "salesperson": self.test_salesperson,
                    "customer": self.test_customer,
                    "car": test_car,
                    "purchase_date": datetime.now(),
                }
                sale = Sales(**model_data)
                self.sale_models.append(sale)

                sale.save()

        self.assertEqual(Car.objects.filter(owner=self.test_customer).count(), 3)

    def tearDown(self) -> None:
        if self.sale_models:
            [sale.delete() for sale in self.sale_models if sale.id is not None]
        if self.test_cars:
            [car.delete() for car in self.test_cars]

        self.test_salesperson.delete()
        self.test_customer.delete()


class SaleTestCase(TestCase):

    def setUp(self):
        self.sale = None
        self.test_salesperson = User(username="test salesperson", email="test_user@email.com", is_staff=True)
        self.test_salesperson.save()

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

        return

    def test_no_permission(self):
        with self.assertRaises(PermissionDenied):
            self.sales_model.save()

    def test_with_permission(self):
        permission = Permission.objects.get(name='Can sell cars')
        self.test_salesperson.user_permissions.add(permission)

        self.sales_model.save()

        self.sale = Sales.objects.filter(salesperson=self.test_salesperson, customer=self.test_customer)
        self.assertTrue(self.sale.exists())
        self.test_car.refresh_from_db()
        logger.critical(f"{self.test_car.owner = }")
        logger.critical(f"{self.test_customer = }")
        self.assertTrue(self.test_car.owner == self.test_customer)

    def tearDown(self) -> None:
        if self.sale:
            self.sale.delete()
        self.test_salesperson.delete()
        self.test_customer.delete()
        self.test_car.delete()
