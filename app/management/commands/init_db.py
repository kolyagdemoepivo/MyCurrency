from django.core.management.base import BaseCommand

from app.models import Currency, Provider, CurrencyExchangeRate
from app.jobs import fetching_provider_data
from MyCurrency.settings import CURRENCY_CONFIG, EXCHANGE_PROVIDERS


class Command(BaseCommand):

    def handle(self, *args, **options):
        for currrency in CURRENCY_CONFIG["currencies"]:
            try:
                Currency.objects.create(
                    code=currrency["code"],
                    name=currrency["name"],
                    symbol=currrency["symbol"],
                )
            except:
                pass
        for provider_name, _ in EXCHANGE_PROVIDERS.items():
            try:
                Provider.objects.create(name=provider_name)
            except:
                pass
        if not CurrencyExchangeRate.objects.exists():
            fetching_provider_data()