from datetime import datetime, timedelta
from random import choice

from car_sales.models import Car, CarColor, CarModel, Customer, Sales
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse_lazy
from loguru import logger


class SalesCrudTestCase(TestCase):

    def setUp(self):

        self.test_salesperson = get_user_model()(username="test salesperson", email="test_user@email.com", is_staff=True)
        permission = Permission.objects.get(name='Can sell cars')
        self.test_salesperson.save()
        self.test_salesperson.user_permissions.add(permission)
        self.test_salesperson.refresh_from_db()

        self.client = Client()
        self.client.force_login(self.test_salesperson)
        self.client_with_referer = Client(HTTP_REFERER="cars_crud")
        self.client_with_referer.force_login(self.test_salesperson)

        self.url = reverse_lazy('sales_crud')

        return

    def test_basic(self):
        r = self.client_with_referer.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['form'].base_fields['salesperson'].disabled)

        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['form'].base_fields['salesperson'].disabled)
        return

    def test_form_enable_field_if_super(self):

        superuser = get_user_model().objects.create_superuser('admin', 'admin@myproject.com', 'password')

        client = Client()
        client.force_login(superuser)

        r = client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.context['form'].base_fields['salesperson'].disabled)

    def test_delete_sale_wo_referer(self):
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
        sales_model = Sales(**model_data)
        sales_model.save()
        sales_model.refresh_from_db()

        self.assertTrue(Sales.objects.get(pk=sales_model.pk))

        data = {"action": "delete", "delete_sale_id": sales_model.id}
        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)

        sale_exist = Sales.objects.filter(pk=sales_model.pk).exists()
        self.assertFalse(sale_exist)

    def test_delete_sale_referer(self):

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
        sales_model = Sales(**model_data)
        sales_model.save()
        sales_model.refresh_from_db()

        self.assertTrue(Sales.objects.get(pk=sales_model.pk))

        data = {"action": "delete", "delete_sale_id": sales_model.id}
        r = self.client_with_referer.post(self.url, data=data)
        self.assertEqual(r.status_code, 302)

        sale_exist = Sales.objects.filter(pk=sales_model.pk).exists()
        self.assertFalse(sale_exist)

    def test_update_sale(self):

        self.test_customer = Customer(name="test customer", address="street", phone="123456789")
        self.test_customer.save()

        self.test_car = Car(name="Carro teste", price=10000, color=choice(CarColor.objects.all()), model=choice(CarModel.objects.all()))
        self.test_car.save()

        model_data = {
            "salesperson": self.test_salesperson,
            "customer": self.test_customer,
            "car": self.test_car,
            "purchase_date": datetime.now() - timedelta(days=1),
        }
        sales_model = Sales(**model_data)
        sales_model.save()
        sales_model.refresh_from_db()

        self.assertTrue(Sales.objects.get(pk=sales_model.pk))

        data = {"action": "update", "update_sale_id": sales_model.id}
        model_data["salesperson"] = sales_model.customer.pk
        model_data["customer"] = sales_model.customer.pk
        model_data["car"] = sales_model.car.pk
        model_data["purchase_date"] = datetime.now().strftime('%Y-%m-%d')
        data = {**model_data, **data}

        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.context.get("form_errors"))

        sale = Sales.objects.get(pk=sales_model.pk)
        self.assertNotEqual(model_data["purchase_date"], sale.purchase_date)

    def test_update_sale_error(self):

        self.test_customer = Customer(name="test customer", address="street", phone="123456789")
        self.test_customer.save()

        self.test_car = Car(name="Carro teste", price=10000, color=choice(CarColor.objects.all()), model=choice(CarModel.objects.all()))
        self.test_car.save()

        model_data = {
            "salesperson": self.test_salesperson,
            "customer": self.test_customer,
            "car": self.test_car,
            "purchase_date": datetime.now() - timedelta(days=1),
        }
        sales_model = Sales(**model_data)
        sales_model.save()
        sales_model.refresh_from_db()

        self.assertTrue(Sales.objects.get(pk=sales_model.pk))

        data = {"action": "update", "update_sale_id": sales_model.id}
        model_data["salesperson"] = sales_model.customer.pk
        model_data["customer"] = sales_model.customer.pk
        model_data["car"] = sales_model.car.pk
        model_data["purchase_date"] = datetime.now().strftime('%d/%m/%Y')
        data = {**model_data, **data}

        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context.get("form_errors"), {'purchase_date': ['Enter a valid date.']})

        sale = Sales.objects.get(pk=sales_model.pk)
        self.assertNotEqual(model_data["purchase_date"], sale.purchase_date)

    def test_create_sale(self):

        self.test_customer = Customer(name="test customer", address="street", phone="123456789")
        self.test_customer.save()

        self.test_car = Car(name="Carro teste", price=10000, color=choice(CarColor.objects.all()), model=choice(CarModel.objects.all()))
        self.test_car.save()

        model_data = {
            "salesperson": self.test_salesperson.pk,
            "customer": self.test_customer.pk,
            "car": self.test_car.pk,
            "purchase_date": datetime.now().strftime('%Y-%m-%d'),
        }

        data = {"action": "create"}
        data = {**model_data, **data}

        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.context.get("form_errors"))
        sale = Sales.objects.get(salesperson=model_data["salesperson"], customer=model_data["customer"], car=model_data["car"], purchase_date=model_data["purchase_date"])
        self.assertIsNotNone(sale)

    def test_create_sale_error(self):

        self.test_customer = Customer(name="test customer", address="street", phone="123456789")
        self.test_customer.save()

        self.test_car = Car(name="Carro teste", price=10000, color=choice(CarColor.objects.all()), model=choice(CarModel.objects.all()))
        self.test_car.save()

        model_data = {
            "salesperson": self.test_salesperson.pk,
            "customer": self.test_customer.pk,
            "car": self.test_car.pk,
            "purchase_date": datetime.now(),
        }

        data = {"action": "create"}
        data = {**model_data, **data}

        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context.get("form_errors"), {'purchase_date': ['Enter a valid date.']})

    def test_unknow_action(self):
        data = {
            "action": "not_exists",
        }
        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form_errors'], 'Unknow action!')
