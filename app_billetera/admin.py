from django.contrib import admin

from .models import Cliente, Historial


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "balance", "date_time")


@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ("date_time_form", "origin", "destino_del_dinero", "change")