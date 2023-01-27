from random import choice, randint

from car_sales.models import Car, CarColor, CarModel, Customer, Sales, User
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse_lazy
from loguru import logger


class CarCRUDViewTest(TestCase):

    def setUp(self):

        self.test_salesperson = User(username="test salesperson", email="test_user@email.com", is_staff=True)
        permission = Permission.objects.get(name='Can sell cars')
        self.test_salesperson.save()
        self.test_salesperson.user_permissions.add(permission)
        self.test_salesperson.refresh_from_db()

        self.client = Client()
        self.client.force_login(self.test_salesperson)
        self.client_with_referer = Client(HTTP_REFERER="cars_crud")
        self.client_with_referer.force_login(self.test_salesperson)

        self.url = reverse_lazy('cars_crud')
        return

    def test_without_referer(self):
        request = self.client_with_referer.get(self.url)
        self.assertEqual(request.status_code, 200)

        request = self.client.get(self.url)
        self.assertEqual(request.status_code, 200)
        return

    def test_delete_car_wo_referer(self):

        self.car_data = dict(
            name=f"Carro teste n{randint(1000, 9999)}",
            price=randint(1000,
                          10000),
            color=choice(CarColor.objects.filter(name="yellow")),
            model=choice(CarModel.objects.filter(name="hatch"))
        )

        self.test_car = Car.objects.create(**self.car_data)
        data = {"action": "delete", "delete_car_id": self.test_car.id}
        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)

        car_exists = Car.objects.filter(name=self.car_data['name']).exists()
        self.assertFalse(car_exists)

    def test_delete_car(self):

        self.car_data = dict(
            name=f"Carro teste n{randint(1000, 9999)}",
            price=randint(1000,
                          10000),
            color=choice(CarColor.objects.filter(name="yellow")),
            model=choice(CarModel.objects.filter(name="hatch"))
        )

        self.test_car = Car.objects.create(**self.car_data)
        data = {"action": "delete", "delete_car_id": self.test_car.id}
        r = self.client_with_referer.post(self.url, data=data)
        self.assertEqual(r.status_code, 302)

        car_exists = Car.objects.filter(name=self.car_data['name']).exists()
        self.assertFalse(car_exists)

    def test_update_car(self):

        self.car_data = dict(
            name=f"Test car num {randint(1000, 9999)}",
            price=randint(1000,
                          10000),
            color=choice(CarColor.objects.filter(name="yellow")),
            model=choice(CarModel.objects.filter(name="hatch"))
        )
        self.test_car = Car.objects.create(**self.car_data)

        data = {"action": "update", "update_car_id": self.test_car.id}
        self.car_data["name"] = "car updated"
        self.car_data["color"] = 1
        self.car_data["model"] = 1
        data = {**self.car_data, **data}

        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)

        car_exists = Car.objects.filter(name=self.car_data['name']).exists()
        self.assertTrue(car_exists)

    def test_update_car_error(self):

        self.car_data = dict(
            name=f"Test car num {randint(1000, 9999)}",
            price=randint(1000,
                          10000),
            color=choice(CarColor.objects.filter(name="yellow")),
            model=choice(CarModel.objects.filter(name="hatch"))
        )
        self.test_car = Car.objects.create(**self.car_data)

        data = {"action": "update", "update_car_id": self.test_car.id}
        self.car_data["name"] = "car updated"
        self.car_data["color"] = 1
        # self.car_data["model"] = 1 -> keeping model as a class causes error
        data = {**self.car_data, **data}

        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)

        car_exists = Car.objects.filter(name=self.car_data['name']).exists()
        self.assertFalse(car_exists)

    def test_create_car(self):

        self.car_data = dict(
            name=f"Test car num {randint(1000, 9999)}",
            price=randint(1000,
                          10000),
            color=choice(CarColor.objects.filter(name="yellow")).pk,
            model=choice(CarModel.objects.filter(name="hatch")).pk
        )
        data = {
            "action": "create",
        }
        data = {**self.car_data, **data}

        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)

        car = Car.objects.get(name=self.car_data['name'])
        self.assertIsNotNone(car)

    def test_create_car_error(self):

        self.car_data = dict(
            name=f"Test car num {randint(1000, 9999)}",
            price=randint(1000, 10000),
            color=choice(CarColor.objects.filter(name="yellow")),  # raises error without pk
            model=choice(CarModel.objects.filter(name="hatch"))  # raises error without pk
        )
        data = {
            "action": "create",
        }
        data = {**self.car_data, **data}

        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)

        with self.assertRaises(Car.DoesNotExist):
            Car.objects.get(name=self.car_data['name'])
