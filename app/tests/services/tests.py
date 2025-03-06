from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.providers.types import ProviderResponse, CurrencyRate
from app.providers.mock import Mock
from app.services.exceptions import ServiceProviderUnknownException
from app.models import CurrencyExchangeRate, Provider, Currency
from MyCurrency.settings import CURRENCY_CONFIG
from app.services.provider_service import (
    _load_provider_class,
    get_exchange_data_rates,
    fetch_timeseries_data,
    save_provider_data,
)


class ExchangeServiceTests(TestCase):
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

    def test_load_provider_class_success(self):
        """Test that provider class loads correctly."""
        class_path = "app.providers.mock.Mock"
        provider_class = _load_provider_class(class_path)

        self.assertEqual(provider_class, Mock)

    def test_load_provider_class_failure(self):
        """Test failure when loading an invalid provider class."""
        with self.assertRaises(ImportError):
            _load_provider_class("invalid.module.ProviderClass")

    @patch("app.models.Provider.objects.filter")
    @patch("app.services.provider_service._load_provider_class")
    def test_get_exchange_data_rates_success(
        self, mock_load_class, mock_provider_filter
    ):
        """Test fetching exchange rates successfully from an active provider."""
        mock_provider = MagicMock()
        mock_provider.name = "mock"
        mock_provider_filter.return_value = [mock_provider]

        mock_provider_instance = MagicMock()
        provider_response = ProviderResponse()
        provider_response.currency_rates = []
        mock_provider_instance.get_exchange_rate_data.return_value = provider_response
        mock_load_class.return_value = MagicMock(return_value=mock_provider_instance)

        result = get_exchange_data_rates("USD", ["EUR", "GBP"])

        self.assertIsNotNone(result)
        mock_provider_instance.get_exchange_rate_data.assert_called_once()

    @patch("app.models.Provider.objects.filter", return_value=[])
    def test_get_exchange_data_rates_no_providers(self, mock_provider_filter):
        """Test fetching exchange rates when no providers are available."""
        result = get_exchange_data_rates("USD", ["EUR", "GBP"])
        self.assertIsNone(result)

    @patch("app.models.Provider.objects.filter")
    @patch("app.services.provider_service._load_provider_class")
    def test_get_exchange_data_rates_provider_exception(
        self, mock_load_class, mock_provider_filter
    ):
        """Test handling of provider exceptions while fetching exchange rates."""
        mock_provider = MagicMock()
        mock_provider.name = "mock"
        mock_provider_filter.return_value = [mock_provider]

        mock_provider_instance = MagicMock()
        mock_provider_instance.get_exchange_rate_data.side_effect = (
            ServiceProviderUnknownException("TestProvider", Exception("Error"))
        )
        mock_load_class.return_value = MagicMock(return_value=mock_provider_instance)

        with self.assertRaises(ServiceProviderUnknownException):
            get_exchange_data_rates("USD", ["EUR", "GBP"])

    @patch("app.models.Provider.objects.filter")
    @patch("app.services.provider_service._load_provider_class")
    def test_fetch_timeseries_data_success(self, mock_load_class, mock_provider_filter):
        """Test successful fetching of historical exchange rates."""
        mock_provider = MagicMock()
        mock_provider.name = "mock"
        mock_provider_filter.return_value = [mock_provider]

        mock_provider_instance = MagicMock()
        provider_response = ProviderResponse()
        provider_response.currency_rates = []
        mock_provider_instance.get_exchange_timeseries_rate_data.return_value = [
            provider_response
        ]
        mock_load_class.return_value = MagicMock(return_value=mock_provider_instance)

        result = fetch_timeseries_data(
            "USD", datetime(2025, 1, 1), datetime(2025, 1, 31)
        )

        self.assertIsInstance(result, list)
        mock_provider_instance.get_exchange_timeseries_rate_data.assert_called_once()

    @patch("app.models.CurrencyExchangeRate.objects.bulk_create")
    def test_save_provider_data(self, mock_bulk_create):
        """Test storing provider exchange rates in the database."""
        curr_1 = Currency.objects.get(code=CURRENCY_CONFIG["base"])
        curr_2 = Currency.objects.get(code="USD")
        currency_map = {"EUR": curr_1, "USD": curr_2}
        provider_response = ProviderResponse()
        provider_response.base = "EUR"
        provider_response.valuation_date = (datetime(2025, 1, 1),)
        provider_response.currency_rates = [CurrencyRate("USD", 1.1)]

        save_provider_data(curr_1, provider_response, currency_map)

        mock_bulk_create.assert_called_once()
        self.assertEqual(len(mock_bulk_create.call_args[0][0]), 1)
