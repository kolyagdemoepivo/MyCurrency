from datetime import datetime
import importlib
from typing import List, Dict

from app.models import Provider, Currency, CurrencyExchangeRate
from app.providers.abstracts.provider import AbstractProvider
from app.providers.exceptions import GeneralProviderException
from app.providers.types import ProviderResponse
from app.services.exceptions import ServiceProviderUnknownException
from MyCurrency.settings import EXCHANGE_PROVIDERS


def _load_provider_class(class_path: str) -> AbstractProvider:
    try:
        module_path, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        provider_class = getattr(module, class_name)

        return provider_class
    except (ImportError, AttributeError, ValueError) as e:
        raise ImportError(f"Could not load class '{class_path}': {str(e)}")


def get_exchange_data_rates(
    source_currency: str, exchange_currency_list: List[str]
) -> ProviderResponse:
    active_providers = Provider.objects.filter(is_active=True)
    for active_provider in active_providers:
        provider_class_name = active_provider.name
        class_path = EXCHANGE_PROVIDERS[provider_class_name]["class"]
        provider_class = _load_provider_class(class_path)
        provider_instance = provider_class()
        try:
            return provider_instance.get_exchange_rate_data(
                source_currency, exchange_currency_list
            )
        except GeneralProviderException:
            continue
        except Exception as e:
            raise ServiceProviderUnknownException(provider_class_name, e)
    return None


def fetch_timeseries_data(
    source_currency: str, from_date: datetime, to_date: datetime
) -> List[ProviderResponse]:
    active_providers = Provider.objects.filter(is_active=True)
    currencies = list(Currency.objects.values_list("code", flat=True))

    for active_provider in active_providers:
        provider_class_name = active_provider.name
        class_path = EXCHANGE_PROVIDERS[provider_class_name]["class"]
        provider_class = _load_provider_class(class_path)
        provider_instance = provider_class()
        try:
            return provider_instance.get_exchange_timeseries_rate_data(
                source_currency, currencies, from_date, to_date
            )
        except GeneralProviderException:
            continue
        except Exception as e:
            raise ServiceProviderUnknownException(provider_class_name, e)
    return None


def save_provider_data(
    source_currency: str,
    provider_response: ProviderResponse,
    currency_map: Dict[str, Currency],
):
    new_exchange_rates = []
    for provider_rate in provider_response.currency_rates:
        currency = currency_map.get(provider_rate.name)
        if not currency:
            continue
        new_exchange_rates.append(
            CurrencyExchangeRate(
                source_currency=source_currency,
                exchanged_currency=currency,
                valuation_date=provider_response.valuation_date,
                rate_value=provider_rate.rate,
            )
        )
    CurrencyExchangeRate.objects.bulk_create(new_exchange_rates)
