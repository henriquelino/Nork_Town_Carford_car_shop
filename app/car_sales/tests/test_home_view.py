from car_sales.models import User
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

        self.url = reverse_lazy('home')

        return

    def test_without_referer(self):
        request = self.client_with_referer.get(self.url)
        self.assertEqual(request.status_code, 200)

        request = self.client.get(self.url)
        self.assertEqual(request.status_code, 200)
        return
