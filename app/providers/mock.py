from datetime import datetime
import random
from typing import List

from app.providers.types import ProviderResponse, CurrencyRate
from app.utils import generate_list_of_dates
from .abstracts.provider import AbstractProvider


class Mock(AbstractProvider):
    def get_exchange_historical_rate_data(
        self,
        source_currency: str,
        exchange_currency_list: List[str],
        valuation_date: datetime,
    ) -> ProviderResponse:
        return self.get_exchange_rate_data(
            source_currency, exchange_currency_list, valuation_date
        )

    def get_exchange_timeseries_rate_data(
        self,
        source_currency: str,
        exchange_currencies: List[str],
        date_from: datetime,
        date_to: datetime,
    ) -> List[ProviderResponse]:
        res = []
        list_of_dates = generate_list_of_dates(date_from, date_to)
        for date in list_of_dates:
            provider_response = ProviderResponse()
            provider_response.base = source_currency
            provider_response.valuation_date = date
            for exchange_currency in exchange_currencies:
                rate = 1
                if source_currency != exchange_currency:
                    rate = round(random.uniform(0.7, 1.2), 8)
                provider_response.currency_rates.append(
                    CurrencyRate(exchange_currency, rate)
                )
            res.append(provider_response)
        return res

    def get_exchange_rate_data(
        self,
        source_currency: str,
        exchange_currency_list: List[str],
    ) -> ProviderResponse:
        provider_response = ProviderResponse()
        provider_response.base = source_currency
        provider_response.valuation_date = datetime.now()
        for exchange_currency in exchange_currency_list:
            rate = 1
            if source_currency != exchange_currency:
                rate = round(random.uniform(0.7, 1.2), 8)
            provider_response.currency_rates.append(
                CurrencyRate(exchange_currency, rate)
            )
        return provider_response
