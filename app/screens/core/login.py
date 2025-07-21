from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from .login_db import validar_credenciales_admin

class LoginScreen(MDScreen):
    error_msg = StringProperty("")

    def validar_credenciales(self):
        dni = self.ids.dni_input.text
        contrasena = self.ids.contrasena_input.text

        # Validación previa de campos vacíos
        if not dni or not contrasena:
            self.error_msg = "Por favor, complete ambos campos: DNI y contraseña."
            return

        es_valido, mensaje = validar_credenciales_admin(dni, contrasena)
        
        if es_valido:
            self.error_msg = ""
            self.manager.current = "dashboard"
        else:
            self.error_msg = mensaje

