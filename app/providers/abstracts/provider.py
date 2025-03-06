from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from app.providers.types import ProviderResponse


class AbstractProvider(ABC):
    @abstractmethod
    def get_exchange_historical_rate_data(
        self, source_currency: str, exchange_currency: str, valuation_date: datetime
    ) -> ProviderResponse:
        pass

    @abstractmethod
    def get_exchange_timeseries_rate_data(
        self,
        source_currency: str,
        exchange_currencies: List[str],
        date_from: datetime,
        date_to: datetime,
    ) -> List[ProviderResponse]:
        pass

    @abstractmethod
    def get_exchange_rate_data(
        self, source_currency: str, exchange_currency: str
    ) -> ProviderResponse:
        pass
