import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.screens.miembros import MiembrosScreen

# test_miembros.py
from kivy.lang import Builder
from kivymd.app import MDApp
from app.screens.miembros import MiembrosScreen  # Ajusta el import según tu estructura

# Carga el kv de miembros
Builder.load_file("app/kv/miembros.kv")  # Ajusta la ruta si es necesario

class TestMiembrosApp(MDApp):
    def build(self):
        self.miembros_screen = MiembrosScreen()
        return self.miembros_screen

    def on_start(self):
        self.miembros_screen.cargar_miembros()

if __name__ == "__main__":
    TestMiembrosApp().run()

import unittest
from kivy.tests.common import GraphicUnitTest
from app.screens.miembros.miembros import MiembrosScreen
from kivymd.app import MDApp

class TestMiembrosScreen(GraphicUnitTest):
    def setUp(self):
        super().setUp()
        self.app = MDApp()
        from app.screens.miembros.miembros import MiembrosScreen  # Ajusta el import según tu estructura