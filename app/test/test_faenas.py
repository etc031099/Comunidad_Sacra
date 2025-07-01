import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from kivy.lang import Builder
from kivymd.app import MDApp
from app.screens.faenas.faenas import FaenasScreen  # Ajusta el import si tu estructura cambia
import unittest
from kivy.tests.common import GraphicUnitTest

# Carga el kv de faenas
Builder.load_file("app/kv/faenas.kv")  # Ajusta la ruta si es necesario

class TestFaenasApp(MDApp):
    def build(self):
        self.faenas_screen = FaenasScreen()
        return self.faenas_screen

    def on_start(self):
        self.faenas_screen.cargar_faenas()

if __name__ == "__main__":
    TestFaenasApp().run()