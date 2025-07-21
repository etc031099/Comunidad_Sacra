import unittest
from app.screens.core.login_db import validar_credenciales_admin

class TestLogin(unittest.TestCase):
    def test_login_correcto(self):
        # Uso de un usuario real de mi base de datos para esta prueba
        dni = "75846655"
        contrasena = "75846655"
        es_valido, mensaje = validar_credenciales_admin(dni, contrasena)
        self.assertTrue(es_valido)
        self.assertEqual(mensaje, "")

    def test_login_incorrecto(self):
        dni = "75846655"
        contrasena = "incorrecta"
        es_valido, mensaje = validar_credenciales_admin(dni, contrasena)
        self.assertFalse(es_valido)
        self.assertIn("incorrectos", mensaje.lower())

    def test_login_campos_vacios(self):
        dni = ""
        contrasena = ""
        es_valido, mensaje = validar_credenciales_admin(dni, contrasena)
        self.assertFalse(es_valido)
        # El mensaje puede variar según tu lógica, ajústalo si es necesario

if __name__ == '__main__':
    unittest.main()