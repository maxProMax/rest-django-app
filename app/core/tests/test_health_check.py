from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


class HealthCheckTests(TestCase):
    def test_health_check(self):
        client = APIClient()
        url = reverse("health-check")
        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
