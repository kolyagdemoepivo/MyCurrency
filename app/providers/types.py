from datetime import datetime
from typing import List


class CurrencyRate:
    __slot__ = ["name", "rate"]

    def __init__(self, name: str, rate: float):
        self.name = name
        self.rate = rate


class ProviderResponse:
    __slot__ = ["base", "currency_rates", "valuation_date"]

    def __init__(self):
        self.base = ""
        self.currency_rates: List[CurrencyRate] = []
        self.valuation_date = None
