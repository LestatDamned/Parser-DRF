from django.test import TestCase
from rest_framework.test import APIRequestFactory, APITestCase


class ViewsTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
