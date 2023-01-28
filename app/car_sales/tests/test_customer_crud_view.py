from car_sales.models import Customer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse_lazy
from loguru import logger


class CustomerCrudTestCase(TestCase):

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

        self.url = reverse_lazy('customers_crud')

        return

    def test_without_referer(self):
        request = self.client_with_referer.get(self.url)
        self.assertEqual(request.status_code, 200)

        request = self.client.get(self.url)
        self.assertEqual(request.status_code, 200)
        return

    def test_delete_customer_wo_referer(self):
        test_customer = Customer(name="test customer", address="street", phone="123456789")
        test_customer.save()
        test_customer.refresh_from_db()

        self.assertTrue(Customer.objects.get(pk=test_customer.pk))

        data = {"action": "delete", "delete_customer_id": test_customer.id}
        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.context.get("form_errors"))

        customer = Customer.objects.filter(pk=test_customer.pk).exists()
        self.assertFalse(customer)

    def test_delete_customer_from_detail(self):
        test_customer = Customer(name="test customer", address="street", phone="123456789")
        test_customer.save()
        test_customer.refresh_from_db()

        self.assertTrue(Customer.objects.get(pk=test_customer.pk))

        data = {"action": "delete", "delete_customer_id": test_customer.id, "from_detail": 1}
        r = self.client_with_referer.post(self.url, data=data)
        self.assertEqual(r.status_code, 302)

        if r.context:
            self.assertIsNone(r.context.get("form_errors"))

        customer = Customer.objects.filter(pk=test_customer.pk).exists()
        self.assertFalse(customer)

    def test_delete_customer(self):
        test_customer = Customer(name="test customer", address="street", phone="123456789")
        test_customer.save()
        test_customer.refresh_from_db()

        self.assertTrue(Customer.objects.get(pk=test_customer.pk))

        data = {"action": "delete", "delete_customer_id": test_customer.id}
        r = self.client_with_referer.post(self.url, data=data)
        self.assertEqual(r.status_code, 302)

        if r.context:
            self.assertIsNone(r.context.get("form_errors"))

        customer = Customer.objects.filter(pk=test_customer.pk).exists()
        self.assertFalse(customer)

    def test_update_customer(self):
        customer_data = dict(name="test customer", address="street", phone="123456789")
        test_customer = Customer(**customer_data)
        test_customer.save()
        test_customer.refresh_from_db()

        self.assertTrue(Customer.objects.get(pk=test_customer.pk))

        data = {"action": "update", "update_customer_id": test_customer.id}
        customer_data["name"] = "updated customer"
        data = {**data, **customer_data}
        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.context.get("form_errors"))

        customer = Customer.objects.get(pk=test_customer.pk)
        self.assertEqual(customer.name, "updated customer")

    def test_update_customer_error(self):
        customer_data = dict(name="test customer", address="street", phone="123456789")
        test_customer = Customer(**customer_data)
        test_customer.save()
        test_customer.refresh_from_db()

        self.assertTrue(Customer.objects.get(pk=test_customer.pk))

        data = {"action": "update", "update_customer_id": test_customer.id}
        customer_data["name"] = "a" * 201
        data = {**data, **customer_data}
        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context.get("form_errors"), {'name': ['Ensure this value has at most 200 characters (it has 201).']})

    def test_create_customer(self):
        customer_data = dict(name="test customer", address="street", phone="123456789")

        data = {
            "action": "create",
        }
        data = {**data, **customer_data}
        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.context.get("form_errors"))

        customer = Customer.objects.get(**customer_data)
        self.assertIsNotNone(customer)

    def test_create_customer_error(self):
        customer_data = dict(name="a" * 201, address="street", phone="123456789")

        data = {
            "action": "create",
        }
        data = {**data, **customer_data}
        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context.get("form_errors"), {'name': ['Ensure this value has at most 200 characters (it has 201).']})

    def test_unknow_action(self):
        data = {
            "action": "not_exists",
        }
        r = self.client.post(self.url, data=data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form_errors'], 'Unknow action!')
