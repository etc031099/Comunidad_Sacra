import unittest
from datetime import datetime
from app.screens.reuniones.reuniones_db import obtener_todas_reuniones, eliminar_reunion_completa
from app.screens.reuniones.crear_reunion_db import crear_reunion

class TestReuniones(unittest.TestCase):
    def test_obtener_todas_reuniones(self):
        reuniones = obtener_todas_reuniones()
        self.assertIsInstance(reuniones, list)
        if reuniones:
            self.assertIn("id_reunion", reuniones[0])
            self.assertIn("titulo", reuniones[0])

    def test_crear_y_eliminar_reunion(self):
        fecha = datetime.now().strftime("%Y-%m-%d")
        titulo = "Reunión de prueba unittest"
        hora_inicio = "18:00"
        descripcion = "Reunión creada por test automático"
        id_reunion = crear_reunion(fecha, titulo, hora_inicio, descripcion)
        self.assertIsNotNone(id_reunion)
        reuniones = obtener_todas_reuniones()
        ids = [r["id_reunion"] for r in reuniones]
        self.assertIn(id_reunion, ids)
        # Eliminar la reunión creada
        exito = eliminar_reunion_completa(id_reunion)
        self.assertTrue(exito)

if __name__ == "__main__":
    unittest.main() 