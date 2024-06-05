from django.db import models
from django.core.validators import MinValueValidator


# Create your models here.
class MoneyField(models.Field):
    def db_type(self, connection):
        return "money"


class Cliente(models.Model):
    name = models.CharField(max_length=80)
    balance = models.DecimalField(max_digits=19, decimal_places=2)
    date_time = models.DateTimeField(auto_now=True)


class Historial(models.Model):
    origin = models.CharField(max_length=80)
    destino_del_dinero = models.CharField(max_length=80)
    change = models.DecimalField(
        max_digits=19, decimal_places=2, validators=[MinValueValidator(0.001)]
    )
    date_time_form = models.DateTimeField(null=True)
