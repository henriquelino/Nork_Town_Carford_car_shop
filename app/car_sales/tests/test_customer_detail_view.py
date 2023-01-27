from car_sales.models import Customer, User
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse_lazy
from loguru import logger


class CustomerCrudTestCase(TestCase):

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

        self.base_url = 'customer_detail'

        return

    def test_exists(self):

        test_customer = Customer(name="test customer", address="street", phone="123456789")
        test_customer.save()
        test_customer.refresh_from_db()

        url = reverse_lazy(self.base_url, kwargs={'pk': test_customer.pk})
        r = self.client_with_referer.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context.get("customer"), test_customer)

        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context.get("customer"), test_customer)
        return

    def test_not_exists(self):

        url = reverse_lazy(self.base_url, kwargs={'pk': 999})
        r = self.client_with_referer.get(url)
        self.assertEqual(r.status_code, 404)
        return
