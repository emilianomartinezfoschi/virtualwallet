from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Cliente
from .models import Historial
from .forms import Operacion
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from django.db import transaction


# Create your views here.
def inicio(request):
    misclientes = Cliente.objects.all().values()
    template = loader.get_template("inicio.html")
    context = {
        "misclientes": misclientes,
    }
    return HttpResponse(template.render(context, request))


def perfil(request, name):
    tabla_historial = Historial.objects.filter(origin=name).order_by("-id")[:10]
    micliente = Cliente.objects.get(name=name)
    template = loader.get_template("perfil.html")
    context = {
        "micliente": micliente,
        "dbhistorialcliente": tabla_historial,
    }
    return HttpResponse(template.render(context, request))


@transaction.atomic
def cambio(request, name):
    micliente = Cliente.objects.get(name=name)
    if name == "LUCIANA":
        origen = "LUCIANA"
    elif name == "MARIO":
        origen = "MARIO"
    else:
        origen = "JORGE"

    if request.method == "POST":
        form = Operacion(request.POST)
        if form.is_valid():
            cambio_origen = form.cleaned_data["origin"]
            cambio_destino = form.cleaned_data["destino_del_dinero"]
            form.date_time_form = timezone.now()
            form.save()
            cliente_origen = Cliente.objects.get(name=cambio_origen)
            if cambio_destino != "EXTRACION":
                cliente_destino = Cliente.objects.get(name=cambio_destino)
            if cambio_origen != cambio_destino:
                if cambio_destino == "EXTRACION":
                    cliente_origen.balance = Decimal(cliente_origen.balance) - Decimal(
                        form.cleaned_data["change"]
                    )
                    cliente_origen.date_time = form.date_time_form
                    messages.success(request, "Extracción realizada correctamente")
                else:
                    cliente_origen.balance = Decimal(cliente_origen.balance) - Decimal(
                        form.cleaned_data["change"]
                    )
                    cliente_origen.date_time = form.date_time_form
                    cliente_destino.balance = Decimal(
                        cliente_destino.balance
                    ) + Decimal(form.cleaned_data["change"])
                    cliente_destino.date_time = form.date_time_form
                    messages.success(request, "Transferencia realizada correctamente")
            elif cambio_origen == cambio_destino:
                cliente_destino.balance = Decimal(cliente_destino.balance) + Decimal(
                    form.cleaned_data["change"]
                )
                cliente_origen.date_time = form.date_time_form
                messages.success(request, "Depósito realizado correctamente")
            cliente_origen.save()
            if cambio_destino != "EXTRACION":
                cliente_destino.save()
            return HttpResponseRedirect("/perfil/" + name)
    else:
        form = Operacion(initial={"origin": origen, "date_time_form": timezone.now()})

    template = loader.get_template("cambio.html")
    context = {
        "micliente": micliente,
        "form": form,
    }
    return HttpResponse(template.render(context, request))


def transferencia(request, name):
    if request.method == "POST":
        form = Operacion(request.POST)
        if form.is_valid():
            micliente = Cliente.objects.get(name=name)
            form.origin = micliente
            form.save()
            return redirect("/perfil/{{ micliente.name }}")
    else:
        form = Operacion()
    return render(request, "perfil.html", {"form": form})
