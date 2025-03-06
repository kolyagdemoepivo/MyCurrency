from django.db import models
from django.core.exceptions import ValidationError


class ProtectedModel(models.Model):
    """
    A custom base model that prevents deletion of instances.
    """

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        raise ValidationError("This model is protected and cannot be deleted.")


class Provider(models.Model):
    name = models.CharField(max_length=200, unique=True)
    priority = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(
        default=True, help_text="smaller values have higher priority"
    )

    class Meta:
        ordering = ["priority"]

    def __str__(self):
        return self.name


class Currency(ProtectedModel):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20, db_index=True)
    symbol = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.code} {self.name}"
    
    def save(self, force_insert=False, force_update=False, using=None,
            update_fields=None):
        if self.code:
            self.code = self.code.upper()
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                        update_fields=update_fields)


class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(
        Currency, related_name="exchanges", on_delete=models.CASCADE
    )
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(db_index=True, decimal_places=6, max_digits=18)

    class Meta:
        ordering = ["-valuation_date"]
