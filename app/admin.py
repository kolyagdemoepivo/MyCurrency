from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render
from django import forms
from django.urls import path

from app.models import Currency, Provider, CurrencyExchangeRate


class CurrencyConversionForm(forms.Form):
    source_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(), label="Source Currency"
    )
    amount = forms.DecimalField(decimal_places=2, max_digits=18, label="Amount")
    target_currencies = forms.ModelMultipleChoiceField(
        queryset=Currency.objects.all(), label="Target Currencies"
    )


def currency_converter_view(request):
    form = CurrencyConversionForm()
    return render(
        request,
        "admin/currency_converter.html",
        {"form": form, "conversion_results": []},
    )


class AppAdmin(admin.ModelAdmin):
    pass


admin.site.register(Currency)
admin.site.register(Provider)
admin.site.register(CurrencyExchangeRate, AppAdmin)
