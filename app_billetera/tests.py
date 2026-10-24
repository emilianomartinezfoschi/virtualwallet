from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Cliente, Historial

User = get_user_model()


class BilleteraSeguridadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pw = "una-clave-larga-123"
        cls.luciana = Cliente.objects.create(
            name="LUCIANA",
            balance=Decimal("1000.00"),
            user=User.objects.create_user("luciana", password=cls.pw),
        )
        cls.mario = Cliente.objects.create(
            name="MARIO",
            balance=Decimal("1000.00"),
            user=User.objects.create_user("mario", password=cls.pw),
        )
        cls.jorge = Cliente.objects.create(
            name="JORGE",
            balance=Decimal("1000.00"),
            user=User.objects.create_user("jorge", password=cls.pw),
        )

    def saldos(self):
        return tuple(
            Cliente.objects.get(name=n).balance for n in ("LUCIANA", "MARIO", "JORGE")
        )

    def login(self, usuario):
        self.assertTrue(self.client.login(username=usuario, password=self.pw))

    # --- Autenticación ---
    def test_anonimo_es_redirigido_al_login(self):
        for url in ("/", "/perfil/LUCIANA", "/cambio/LUCIANA"):
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302, url)
            self.assertIn("/login/", r["Location"])

    def test_anonimo_no_puede_mover_dinero(self):
        self.client.post("/cambio/LUCIANA", {"destino_del_dinero": "MARIO", "change": "100"})
        self.assertEqual(self.saldos(), (Decimal("1000.00"),) * 3)
        self.assertEqual(Historial.objects.count(), 0)

    # --- Autorización (acceso a cuentas ajenas) ---
    def test_no_se_puede_ver_cuenta_ajena(self):
        self.login("mario")
        self.assertEqual(self.client.get("/perfil/LUCIANA").status_code, 404)
        self.assertEqual(self.client.get("/cambio/LUCIANA").status_code, 404)

    def test_no_se_puede_operar_cuenta_ajena(self):
        self.login("mario")
        r = self.client.post("/cambio/LUCIANA", {"destino_del_dinero": "MARIO", "change": "500"})
        self.assertEqual(r.status_code, 404)
        self.assertEqual(self.saldos(), (Decimal("1000.00"),) * 3)

    def test_origen_falsificado_se_ignora(self):
        self.login("luciana")
        self.client.post(
            "/cambio/LUCIANA",
            {"origin": "MARIO", "destino_del_dinero": "JORGE", "change": "500"},
        )
        self.assertEqual(self.saldos(), (Decimal("500.00"), Decimal("1000.00"), Decimal("1500.00")))
        self.assertEqual(Historial.objects.get().origin, "LUCIANA")

    def test_inicio_solo_muestra_cuenta_propia(self):
        self.login("mario")
        r = self.client.get("/")
        self.assertContains(r, "MARIO")
        self.assertNotContains(r, "LUCIANA")

    # --- Lógica de dinero ---
    def test_transferencia_ok(self):
        self.login("luciana")
        r = self.client.post("/cambio/LUCIANA", {"destino_del_dinero": "MARIO", "change": "100.50"})
        self.assertRedirects(r, "/perfil/LUCIANA")
        self.assertEqual(self.saldos(), (Decimal("899.50"), Decimal("1100.50"), Decimal("1000.00")))
        self.assertEqual(Historial.objects.count(), 1)

    def test_extraccion_y_deposito(self):
        self.login("luciana")
        self.client.post("/cambio/LUCIANA", {"destino_del_dinero": "EXTRACION", "change": "200"})
        self.client.post("/cambio/LUCIANA", {"destino_del_dinero": "LUCIANA", "change": "50"})
        self.assertEqual(self.saldos()[0], Decimal("850.00"))
        self.assertEqual(Historial.objects.count(), 2)

    def test_saldo_insuficiente(self):
        self.login("luciana")
        for destino in ("MARIO", "EXTRACION"):
            r = self.client.post("/cambio/LUCIANA", {"destino_del_dinero": destino, "change": "5000"})
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, "Saldo insuficiente")
        self.assertEqual(self.saldos(), (Decimal("1000.00"),) * 3)
        self.assertEqual(Historial.objects.count(), 0)

    def test_montos_invalidos(self):
        self.login("luciana")
        for monto in ("-5", "0", "abc", "99999999999"):
            r = self.client.post("/cambio/LUCIANA", {"destino_del_dinero": "MARIO", "change": monto})
            self.assertEqual(r.status_code, 200, monto)
        self.assertEqual(self.saldos(), (Decimal("1000.00"),) * 3)
        self.assertEqual(Historial.objects.count(), 0)

    def test_destino_inexistente(self):
        self.login("luciana")
        r = self.client.post("/cambio/LUCIANA", {"destino_del_dinero": "HACKER", "change": "10"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.saldos(), (Decimal("1000.00"),) * 3)

    def test_cliente_inexistente_da_404_no_500(self):
        self.login("luciana")
        self.assertEqual(self.client.get("/perfil/NOEXISTE").status_code, 404)

    # --- Logout solo por POST ---
    def test_logout_requiere_post(self):
        self.login("luciana")
        self.assertEqual(self.client.get("/logout/").status_code, 405)
        self.client.post("/logout/")
        self.assertEqual(self.client.get("/").status_code, 302)

class LoginMenuTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.demo = User.objects.create_user("luciana", password="demo1234")
        Cliente.objects.create(name="LUCIANA", balance=Decimal("1000.00"), user=cls.demo)
        User.objects.create_superuser("jefe", password="una-clave-muy-larga-2026")

    def test_menu_lista_solo_cuentas_de_demo(self):
        r = self.client.get("/login/")
        self.assertContains(r, "<select")
        self.assertContains(r, "LUCIANA")
        self.assertNotContains(r, "jefe")
        self.assertContains(r, "demo1234")
        self.assertContains(r, "Contraseña")

    def test_login_correcto(self):
        r = self.client.post("/login/", {"username": "luciana", "password": "demo1234"})
        self.assertRedirects(r, "/", fetch_redirect_response=False)

    def test_error_en_espanol(self):
        r = self.client.post("/login/", {"username": "luciana", "password": "mal"})
        self.assertContains(r, "La contraseña no es correcta")

    def test_superusuario_no_puede_entrar_por_este_login(self):
        r = self.client.post("/login/", {"username": "jefe", "password": "una-clave-muy-larga-2026"})
        self.assertContains(r, "Elegí una cuenta de la lista")
        self.assertNotIn("_auth_user_id", self.client.session)