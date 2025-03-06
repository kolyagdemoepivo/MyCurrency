from datetime import datetime
from django.db.models import Max, Subquery, Q
from django.db.models.functions import TruncDate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from app.models import CurrencyExchangeRate, Currency
from app.serializers import (
    CurrencyExchangeRateSerializer,
    CurrencyExchangeSerializer,
    CurrencySerializer,
)
from app.services.provider_service import (
    fetch_timeseries_data,
    save_provider_data,
    get_exchange_data_rates,
)
from app.utils import get_existing_rates, adjust_to_date
from MyCurrency.settings import CURRENCY_CONFIG


class CurrencyView(APIView):
    def get(self, request):
        currencies = Currency.objects.all()
        serializer = CurrencySerializer(currencies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExchangeRateView(APIView):
    def get(self, request):
        serializer = CurrencyExchangeSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        source_currency = serializer.validated_data["source"]
        target_currencies = serializer.validated_data["target"]
        amount = serializer.validated_data["amount"]

        base_currency = CURRENCY_CONFIG["base"]
        currencies_to_fetch = (
            [*target_currencies, source_currency]
            if source_currency != base_currency
            else target_currencies
        )
        existing_rates = get_existing_rates(
            source_currency, CURRENCY_CONFIG["base"], datetime.now(), datetime.now()
        )
        if not existing_rates:
            currencies = Currency.objects.all()
            if not currencies:
                return Response(
                    {
                        "msg": f"Exchange rate not found for {base_currency} to {source_currency}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            currency_map = {currency.code: currency for currency in currencies}
            provider_response = get_exchange_data_rates(
                CURRENCY_CONFIG["base"], list(currency_map.keys())
            )
            if not provider_response:
                return Response(
                    {
                        "msg": f"Exchange rate not found for {base_currency} to {source_currency}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            source_currency = currency_map.get(CURRENCY_CONFIG["base"])
            if not source_currency:
                return Response(
                    {
                        "msg": f"Exchange rate not found for {base_currency} to {source_currency}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            save_provider_data(source_currency, provider_response, currency_map)
        exchange_rates = CurrencyExchangeRate.objects.filter(
            Q(
                source_currency__code=base_currency,
                exchanged_currency__code__in=currencies_to_fetch,
            )
            | Q(
                source_currency__code=source_currency,
                exchanged_currency__code=base_currency,
            )
        ).select_related("source_currency", "exchanged_currency")

        exchange_rate_map = {
            (rate.source_currency.code, rate.exchanged_currency.code): rate.rate_value
            for rate in exchange_rates
        }
        conversion_factor = 1.0
        if source_currency != base_currency:
            base_to_source_rate = exchange_rate_map.get(
                (base_currency, source_currency)
            )
            if not base_to_source_rate:
                return Response(
                    {
                        "msg": f"Exchange rate not found for {base_currency} to {source_currency}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            conversion_factor = float(1 / base_to_source_rate)

        exchange_results = {}
        for target_currency in target_currencies:
            base_to_target_rate = exchange_rate_map.get(
                (base_currency, target_currency)
            )
            if not base_to_target_rate:
                continue
            exchange_results[target_currency] = (
                amount * conversion_factor * float(base_to_target_rate)
            )

        response_data = {
            "base": source_currency,
            "amount": amount,
            "exchange": exchange_results,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CurrencyExchangeRateViewSet(APIView):

    def get(self, request):
        # Validate query parameters
        serializer = CurrencyExchangeRateSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        source_currency = serializer.validated_data["currency"]
        from_date = serializer.validated_data["from_date"]
        to_date = serializer.validated_data["to_date"]

        # Convert dates to datetime objects
        from_date = datetime.strptime(str(from_date), "%Y-%m-%d").date()
        to_date = datetime.strptime(str(to_date), "%Y-%m-%d").date()

        to_date = adjust_to_date(to_date)
        difference_days = (to_date - from_date).days
        existing_rates = get_existing_rates(
            source_currency, CURRENCY_CONFIG["base"], from_date, to_date
        )
        existing_dates = {
            rate["valuation_date"].strftime("%Y-%m-%d"): 1 for rate in existing_rates
        }

        if len(existing_dates) != difference_days + 1:
            provider_timeseries_data_list = fetch_timeseries_data(
                CURRENCY_CONFIG["base"], from_date, to_date
            )
            provider_timeseries_data_list = list(
                filter(
                    lambda a: a.valuation_date not in existing_dates,
                    provider_timeseries_data_list,
                )
            )
            if provider_timeseries_data_list:
                currencies = Currency.objects.all()
                if not currencies:
                    return
                currency_map = {currency.code: currency for currency in currencies}
            for provider_timeseries_data in provider_timeseries_data_list:
                save_provider_data(
                    currency_map[CURRENCY_CONFIG["base"]],
                    provider_timeseries_data,
                    currency_map,
                )

        # We retrieve currency exchange rates grouped by day, 
        # selecting the most recently added rates in the database. 
        # This way, we obtain the latest exchange rates for each day.
        exchange_rates = (
            CurrencyExchangeRate.objects.filter(
                Q(source_currency__code=source_currency)
                | Q(source_currency__code=CURRENCY_CONFIG["base"]),
                valuation_date__range=(from_date, to_date),
            )
            .select_related("source_currency", "exchanged_currency")
            .annotate(date=TruncDate("valuation_date"))
            .values("valuation_date", "exchanged_currency__code")
            .annotate(max_id=Max("id"))
            .values("max_id")
        )
        exchange_rates = CurrencyExchangeRate.objects.select_related(
            "source_currency", "exchanged_currency"
        ).filter(id__in=Subquery(exchange_rates))
        rates_by_date = {}
        conversion_factors = {}
        for rate_entry in exchange_rates:
            date_str = rate_entry.valuation_date.strftime("%Y-%m-%d")
            if date_str not in rates_by_date:
                rates_by_date[date_str] = []
            rates_by_date[date_str].append(
                {
                    "code": rate_entry.exchanged_currency.code,
                    "rate": rate_entry.rate_value,
                }
            )
            if source_currency == rate_entry.exchanged_currency.code:
                conversion_factors[date_str] = 1 / rate_entry.rate_value
        if source_currency != CURRENCY_CONFIG["base"]:
            for date, rates in rates_by_date.items():
                conversion_factor = conversion_factors[date]
                for rate_entry in rates:
                    rate_entry["rate"] = round(
                        conversion_factor * rate_entry["rate"], 2
                    )

        return Response(
            {"base": source_currency, "rates": rates_by_date}, status=status.HTTP_200_OK
        )
