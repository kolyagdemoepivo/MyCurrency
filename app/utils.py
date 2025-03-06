from datetime import datetime, timedelta, date
from django.db.models import Max, Q
from typing import List

from app.models import CurrencyExchangeRate


def adjust_to_date(to_date):
    """Adjust to_date if it exceeds the current date."""
    current_date = date.today()
    return min(to_date, current_date)


def get_existing_rates(source_currency, base_currency, from_date, to_date):
    """Fetch existing exchange rates from the database."""
    return (
        CurrencyExchangeRate.objects.filter(
            Q(source_currency__code=source_currency)
            | Q(source_currency__code=base_currency),
            valuation_date__range=(from_date, to_date),
        )
        .values("valuation_date")
        .annotate(max_id=Max("id"))
    )


def generate_list_of_dates(start_date: datetime, end_date: datetime) -> List[datetime]:
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    return dates
