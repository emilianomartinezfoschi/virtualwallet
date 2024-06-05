from django import forms
from .models import Historial
from .models import Cliente


class Operacion(forms.ModelForm):
    CHOICES = [
        ("LUCIANA", "LUCIANA"),
        ("MARIO", "MARIO"),
        ("JORGE", "JORGE"),
        ("EXTRACION", "EXTRACION"),
    ]
    destino_del_dinero = forms.ChoiceField(choices=CHOICES)

    class Meta:
        model = Historial
        fields = ("date_time_form", "origin", "destino_del_dinero", "change")
        labels = {
            "destino_del_dinero": "DESTINO_DEL_DINERO",
            "change": "Monto",
        }
        placeholders = {
            "change": "1052.32 por ejemplo",
        }

    def clean_change(self):
        cleaned_data = super().clean()
        origin = cleaned_data.get("origin")
        destino = cleaned_data.get("destino_del_dinero")
        change = cleaned_data.get("change")

        if change <= 0:
            print(change)
            raise forms.ValidationError("El monto no puede ser menor a 0.01")
        if origin and destino and change is not None:
            if origin != destino:
                datos_origen = Cliente.objects.get(name=origin)
                if change > datos_origen.balance:
                    raise forms.ValidationError(
                        "La Cantidad no puede ser mayor a {}".format(
                            datos_origen.balance
                        )
                    )
        return change
