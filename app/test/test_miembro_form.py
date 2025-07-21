import unittest
from app.screens.miembros.miembros_db import obtener_miembros

class TestMiembroForm(unittest.TestCase):
    def test_obtener_miembros(self):
        miembros = obtener_miembros()
        self.assertIsInstance(miembros, list)
        if miembros:
            self.assertIn("Nombre", miembros[0])
            self.assertIn("DNI", miembros[0])

if __name__ == '__main__':
    unittest.main()