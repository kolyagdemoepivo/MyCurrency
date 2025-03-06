from datetime import datetime
import requests
from typing import Dict, List
from urllib.parse import urlencode

from app.providers.abstracts.provider import AbstractProvider
from app.providers.types import ProviderResponse, CurrencyRate
from app.providers.exceptions import GeneralProviderException
from MyCurrency.settings import EXCHANGE_PROVIDERS


class CurrencyBeacon(AbstractProvider):
    API = "https://api.currencybeacon.com/v1"

    def _parse_api_response(self, response: any) -> ProviderResponse:
        data = response.json()
        data_response = data.get("response", {})
        rates = data_response.get("rates", {})
        date = data_response.get("date", "")
        if not rates:
            return None
        date = datetime.fromisoformat(date.replace("Z", "+00:00"))
        provider_response = ProviderResponse()
        provider_response.valuation_date = date
        for currency_code, rate in rates.items():
            provider_response.currency_rates.append(CurrencyRate(currency_code, rate))
        return provider_response

    def _parse_api_timeseries_response(
        self, base: str, response: any
    ) -> List[ProviderResponse]:
        data = response.json()
        data_response = data.get("response", {})
        if not data_response:
            return None
        res: List[ProviderResponse] = []
        for date, rates in data_response.items():
            provider_response = ProviderResponse()
            provider_response.valuation_date = date
            provider_response.base = base
            for currency_code, currency_rate in rates.items():
                provider_response.currency_rates.append(
                    CurrencyRate(currency_code, currency_rate)
                )
            res.append(provider_response)
        return res

    def get_exchange_timeseries_rate_data(
        self,
        source_currency: str,
        exchange_currencies: List[str],
        from_date: datetime,
        to_date: datetime,
    ):
        api_key = EXCHANGE_PROVIDERS["currencybeacon"]["api_key"]
        params = {
            "base": source_currency,
            "symbols": ",".join(exchange_currencies),
            "start_date": from_date.strftime("%Y-%m-%d"),
            "end_date": to_date.strftime("%Y-%m-%d"),
        }
        query_string = urlencode(params)
        url = f"{CurrencyBeacon.API}/timeseries?{query_string}"
        resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
        if resp.status_code != 200:
            raise GeneralProviderException("CurrencyBeacon")
        return self._parse_api_timeseries_response(source_currency, resp)

    def get_exchange_historical_rate_data(
        self,
        source_currency: str,
        exchange_currency_list: List[str],
        valuation_date: datetime,
    ) -> ProviderResponse:
        api_key = EXCHANGE_PROVIDERS["currencybeacon"]["api_key"]
        params = {
            "base": source_currency,
            "symbols": ",".join(exchange_currency_list),
            "date": valuation_date.strftime("%Y-%m-%d"),
        }
        query_string = urlencode(params)
        url = f"{CurrencyBeacon.API}/historical?{query_string}"
        resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
        if resp.status_code != 200:
            raise GeneralProviderException("CurrencyBeacon")
        provider_response = self._parse_api_response(resp)
        if provider_response:
            provider_response.base = source_currency
        return provider_response

    def get_exchange_rate_data(
        self,
        source_currency: str,
        exchange_currency_list: List[str],
    ) -> ProviderResponse:
        api_key = EXCHANGE_PROVIDERS["currencybeacon"]["api_key"]
        params = {"base": source_currency, "symbols": ",".join(exchange_currency_list)}
        query_string = urlencode(params)
        url = f"{CurrencyBeacon.API}/latest?{query_string}"
        resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})

        if resp.status_code != 200:
            raise GeneralProviderException("CurrencyBeacon")

        data = resp.json()
        data_response = data.get("response", {})
        rates = data_response.get("rates", {})
        date = data_response.get("date", "")

        if not rates:
            return None
        date = datetime.fromisoformat(date.replace("Z", "+00:00"))
        provider_response = self._parse_api_response(resp)
        if provider_response:
            provider_response.base = source_currency
        return provider_response
