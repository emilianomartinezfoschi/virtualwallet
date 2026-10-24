from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import EXTRACCION, Operacion
from .models import Cliente, Historial


class SaldoInsuficiente(Exception):
    pass


@login_required
def inicio(request):
    # Cada usuario ve únicamente su propia cuenta.
    misclientes = Cliente.objects.filter(user=request.user).values()
    return render(request, "inicio.html", {"misclientes": misclientes})


@login_required
def perfil(request, name):
    micliente = get_object_or_404(Cliente, name=name, user=request.user)
    tabla_historial = Historial.objects.filter(origin=micliente.name).order_by("-id")[:10]
    return render(
        request,
        "perfil.html",
        {"micliente": micliente, "dbhistorialcliente": tabla_historial},
    )


@login_required
def cambio(request, name):
    # Solo se puede operar sobre la cuenta propia (si no, 404).
    micliente = get_object_or_404(Cliente, name=name, user=request.user)

    if request.method == "POST":
        form = Operacion(request.POST)
        if form.is_valid():
            destino = form.cleaned_data["destino_del_dinero"]
            monto = form.cleaned_data["change"]
            try:
                with transaction.atomic():
                    # Bloqueamos las filas involucradas (en orden fijo para evitar deadlocks)
                    nombres = {micliente.name}
                    if destino != EXTRACCION:
                        nombres.add(destino)
                    filas = {
                        c.name: c
                        for c in Cliente.objects.select_for_update()
                        .filter(name__in=nombres)
                        .order_by("pk")
                    }
                    origen = filas[micliente.name]  # origen SIEMPRE = usuario logueado

                    if destino == EXTRACCION:
                        if monto > origen.balance:
                            raise SaldoInsuficiente(origen.balance)
                        origen.balance -= monto
                        origen.save()
                        mensaje = "Extracción realizada correctamente"
                    elif destino == origen.name:
                        origen.balance += monto
                        origen.save()
                        mensaje = "Depósito realizado correctamente"
                    else:
                        if monto > origen.balance:
                            raise SaldoInsuficiente(origen.balance)
                        receptor = filas[destino]
                        origen.balance -= monto
                        receptor.balance += monto
                        origen.save()
                        receptor.save()
                        mensaje = "Transferencia realizada correctamente"

                    Historial.objects.create(
                        origin=origen.name,
                        destino_del_dinero=destino,
                        change=monto,
                        date_time_form=timezone.now(),  # fecha tomada del servidor
                    )
            except SaldoInsuficiente as e:
                form.add_error("change", f"Saldo insuficiente. Tu saldo es $ {e.args[0]}")
            else:
                messages.success(request, mensaje)
                return redirect("perfil", name=micliente.name)
    else:
        form = Operacion()

    return render(request, "cambio.html", {"micliente": micliente, "form": form})