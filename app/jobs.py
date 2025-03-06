from app.services.provider_service import get_exchange_data_rates, save_provider_data
from app.models import Currency
from django_apscheduler import util
from MyCurrency.settings import CURRENCY_CONFIG


def fetching_provider_data():
    currencies = Currency.objects.all()
    if not currencies:
        return
    currency_map = {currency.code: currency for currency in currencies}
    provider_response = get_exchange_data_rates(
        CURRENCY_CONFIG["base"], list(currency_map.keys())
    )
    if not provider_response:
        return

    source_currency = currency_map.get(CURRENCY_CONFIG["base"])
    if not source_currency:
        return
    save_provider_data(source_currency, provider_response, currency_map)