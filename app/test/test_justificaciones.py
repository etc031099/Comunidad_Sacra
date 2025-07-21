import unittest
from app.screens.justificaciones.justificaciones_db import (
    obtener_justificaciones_faena,
    obtener_justificaciones_reunion
)

class TestJustificaciones(unittest.TestCase):
    def test_obtener_justificaciones_faena(self):
        id_faena = 6  # Cambia por un ID válido
        justificaciones = obtener_justificaciones_faena(id_faena)
        self.assertIsInstance(justificaciones, list)

    def test_obtener_justificaciones_reunion(self):
        id_reunion = 12  # Cambia por un ID válido
        justificaciones = obtener_justificaciones_reunion(id_reunion)
        self.assertIsInstance(justificaciones, list)

if __name__ == '__main__':
    unittest.main()