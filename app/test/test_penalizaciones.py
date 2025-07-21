import unittest
from app.screens.penalizaciones.penalizaciones_db import obtener_penalizaciones_por_miembro

class TestPenalizaciones(unittest.TestCase):
    def test_obtener_penalizaciones_por_miembro(self):
        penalizaciones = obtener_penalizaciones_por_miembro()
        self.assertIsInstance(penalizaciones, list)
        # Si hay penalizaciones, revisa la estructura
        if penalizaciones:
            self.assertGreaterEqual(len(penalizaciones[0]), 4)  # id, nombre, total multas, asistencias

if __name__ == "__main__":
    unittest.main() 