import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from kivy.lang import Builder
from kivymd.app import MDApp
from app.screens.faenas.faena_form import FaenaFormScreen
import unittest
from kivy.tests.common import GraphicUnitTest

# Carga el kv de faena_form
Builder.load_file("app/kv/faena_form.kv")

class TestFaenaFormApp(MDApp):
    def build(self):
        self.form_screen = FaenaFormScreen()
        return self.form_screen

    def on_start(self):
        # Simula la entrada al formulario
        self.form_screen.on_pre_enter()
        # Comprueba que los campos principales existen
        assert hasattr(self.form_screen.ids, "input_nombre")
        assert hasattr(self.form_screen.ids, "input_fecha_inicio")
        assert hasattr(self.form_screen.ids, "radio_ordinaria")
        assert hasattr(self.form_screen.ids, "radio_extraordinaria")
        print("Todos los campos principales existen en el formulario.")

if __name__ == "__main__":
    TestFaenaFormApp().run()