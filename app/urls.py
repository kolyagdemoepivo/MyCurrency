from django.urls import path
from rest_framework.routers import DefaultRouter

from app.views import CurrencyExchangeRateViewSet, ExchangeRateView, CurrencyView

urlpatterns = [
    path("exchange/", ExchangeRateView.as_view(), name="exchange"),
    path("rates/", CurrencyExchangeRateViewSet.as_view(), name="rates"),
    path("currencies/", CurrencyView.as_view(), name="currencies"),
]
