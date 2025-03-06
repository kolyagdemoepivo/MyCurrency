from rest_framework import serializers

from app.models import CurrencyExchangeRate, Currency


class CurrencySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=3)
    name = serializers.CharField()
    symbol = serializers.CharField(max_length=1)


class CurrencyExchangeRateSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=3)
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)

    def validate(self, data):
        from_date = data.get("from_date")
        to_date = data.get("to_date")

        if from_date > to_date:
            raise serializers.ValidationError("from_date and to_date have wrong dates.")
        return data


class CurrencyExchangeSerializer(serializers.Serializer):
    source = serializers.CharField(max_length=3)
    target = serializers.CharField(max_length=300)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate(self, data):
        source = data.get("source", "").upper()
        target = data.get("target", "").upper()

        if not source or not target:
            raise serializers.ValidationError(
                "Both 'source' and 'target' parameters are required."
            )
        if "," in target:
            target_currencies = target.split(",")
        else:
            target_currencies = [target]
        try:
            amount = float(data.get("amount", 1))
        except:
            raise serializers.ValidationError("Amount has an incorrect value.")

        if len(source) != 3 or not source.isalpha():
            raise serializers.ValidationError(
                "Currency has 3 characters according to the ISO 4217 standard."
            )
        for target_currency in target_currencies:
            if len(target_currency) != 3 or not target_currency.isalpha():
                raise serializers.ValidationError(
                    "Currency has 3 characters according to the ISO 4217 standard."
                )
        if len(target_currencies) > 200:
            raise serializers.ValidationError(
                "The list of requested currencies is too large."
            )
        return {
            "source": source,
            "target": target_currencies,
            "amount": amount,
        }
