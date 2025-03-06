from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from app.models import CurrencyExchangeRate, Currency, Provider
from datetime import date, datetime

from MyCurrency.settings import CURRENCY_CONFIG


class ExchangeViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.base_currency = Currency.objects.create(code=CURRENCY_CONFIG["base"])
        self.target_currency = Currency.objects.create(code="USD")
        self.exchange_rate = CurrencyExchangeRate.objects.create(
            source_currency=self.base_currency,
            exchanged_currency=self.target_currency,
            rate_value=0.85,
            valuation_date=date.today(),
        )
        self.provider = Provider.objects.create(name="mock")

    def test_valid_exchange_request(self):
        response = self.client.get(
            "/api/v1/exchange/",
            {"source": CURRENCY_CONFIG["base"], "target": ["USD"], "amount": 100},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("exchange", response.data)
        self.assertAlmostEqual(response.data["exchange"]["USD"], 85.0)

    def test_invalid_currency(self):
        response = self.client.get(
            "/api/v1/exchange/",
            {"source": "XYZ", "target": ["USD"], "amount": 100},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CurrencyExchangeRateViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.currency = Currency.objects.create(code=CURRENCY_CONFIG["base"])
        self.currency_eur = Currency.objects.create(code="USD")
        self.exchange_rate = CurrencyExchangeRate.objects.create(
            source_currency=self.currency,
            exchanged_currency=self.currency_eur,
            rate_value=0.85,
            valuation_date=datetime.strptime(str("2025-03-04"), "%Y-%m-%d").date(),
        )
        self.provider = Provider.objects.create(name="mock")

    def test_get_currency_exchange_rates(self):
        response = self.client.get(
            "/api/v1/rates/",
            {"currency": "EUR", "from_date": "2025-01-01", "to_date": "2025-03-04"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("rates", response.data)

    def test_missing_parameters(self):
        response = self.client.get("/api/v1/rates/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CurrencyViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.currency = Currency.objects.create(code=CURRENCY_CONFIG["base"])

    def test_list_currencies(self):
        response = self.client.get("/api/v1/currencies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

