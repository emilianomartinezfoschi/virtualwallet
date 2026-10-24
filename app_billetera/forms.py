from decimal import Decimal

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .models import Cliente

User = get_user_model()

# Se mantiene el valor original (con ese typo) para no romper el historial existente.
EXTRACCION = "EXTRACION"
MONTO_MAXIMO = Decimal("10000000.00")


class Operacion(forms.Form):
    destino_del_dinero = forms.ChoiceField(label="Destino del dinero")
    change = forms.DecimalField(
        label="Monto",
        min_value=Decimal("0.01"),
        max_value=MONTO_MAXIMO,
        max_digits=19,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"step": "0.01", "min": "0.01", "placeholder": "1052.32 por ejemplo"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        nombres = Cliente.objects.order_by("name").values_list("name", flat=True)
        self.fields["destino_del_dinero"].choices = [(n, n) for n in nombres] + [
            (EXTRACCION, EXTRACCION)
        ]

class LoginForm(AuthenticationForm):
    """Login con menú desplegable: solo lista las cuentas de demo (nunca admins)."""

    username = forms.ChoiceField(
        label="Cuenta",
        error_messages={
            "required": "Elegí una cuenta.",
            "invalid_choice": "Elegí una cuenta de la lista.",
        },
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
        error_messages={"required": "Ingresá la contraseña."},
    )
    error_messages = {
        "invalid_login": "La contraseña no es correcta. Revisá la que figura debajo e intentá de nuevo.",
        "inactive": "Esta cuenta está desactivada.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cuentas = (
            User.objects.filter(
                is_active=True, is_staff=False, is_superuser=False, cliente__isnull=False
            )
            .order_by("cliente__name")
            .values_list("username", "cliente__name")
        )
        self.fields["username"].choices = [("", "Elegí una cuenta")] + list(cuentas)