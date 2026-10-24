from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


# NO borrar: las migraciones antiguas (0002, 0003, 0004) la importan.
class MoneyField(models.Field):
    def db_type(self, connection):
        return "money"


class Cliente(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cliente",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=80, unique=True)
    balance = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    date_time = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=0), name="cliente_balance_no_negativo"
            )
        ]

    def __str__(self):
        return self.name


class Historial(models.Model):
    origin = models.CharField(max_length=80)
    destino_del_dinero = models.CharField(max_length=80)
    change = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    date_time_form = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(change__gt=0), name="historial_monto_positivo"
            )
        ]