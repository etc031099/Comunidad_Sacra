import unittest
from app.screens.notificaciones.notificaciones_db import (
    obtener_eventos_proximos, obtener_penalizaciones_pendientes, obtener_miembros_con_inasistencias
)

class TestNotificaciones(unittest.TestCase):
    def test_obtener_eventos_proximos(self):
        eventos = obtener_eventos_proximos()
        self.assertIsInstance(eventos, list)
        if eventos:
            self.assertIn("nombre", eventos[0])
            self.assertIn("fecha", eventos[0])
            self.assertIn("tipo", eventos[0])

    def test_obtener_penalizaciones_pendientes(self):
        penalizaciones = obtener_penalizaciones_pendientes()
        self.assertIsInstance(penalizaciones, list)
        if penalizaciones:
            self.assertGreaterEqual(len(penalizaciones[0]), 4)  # nombre, tipo, valor, fecha

    def test_obtener_miembros_con_inasistencias(self):
        miembros = obtener_miembros_con_inasistencias()
        self.assertIsInstance(miembros, list)
        if miembros:
            self.assertGreaterEqual(len(miembros[0]), 4)  # id, nombre, faltas, ultima falta

if __name__ == "__main__":
    unittest.main() 