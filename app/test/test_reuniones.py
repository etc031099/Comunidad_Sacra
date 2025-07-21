import unittest
from datetime import datetime
from app.screens.reuniones.reuniones_db import obtener_todas_reuniones, eliminar_reunion_completa
from app.screens.reuniones.crear_reunion_db import crear_reunion, actualizar_reunion

class TestReuniones(unittest.TestCase):
    def test_obtener_todas_reuniones(self):
        reuniones = obtener_todas_reuniones()
        self.assertIsInstance(reuniones, list)
        if reuniones:
            self.assertIn("id_reunion", reuniones[0])
            self.assertIn("titulo", reuniones[0])

    def test_crear_y_eliminar_reunion(self):
        # Crear una reunión de prueba
        fecha = datetime.now().strftime("%Y-%m-%d")
        titulo = "Reunión de prueba unittest"
        hora_inicio = "18:00"
        descripcion = "Reunión creada por test automático"
        id_reunion = crear_reunion(fecha, titulo, hora_inicio, descripcion)
        self.assertIsNotNone(id_reunion)
        # Verificar que la reunión aparece en la lista
        reuniones = obtener_todas_reuniones()
        ids = [r["id_reunion"] for r in reuniones]
        self.assertIn(id_reunion, ids)
        # Eliminar la reunión
        exito = eliminar_reunion_completa(id_reunion)
        self.assertTrue(exito)
        # Verificar que ya no está
        reuniones = obtener_todas_reuniones()
        ids = [r["id_reunion"] for r in reuniones]
        self.assertNotIn(id_reunion, ids)

    def test_actualizar_reunion(self):
        # Crear una reunión de prueba
        fecha = datetime.now().strftime("%Y-%m-%d")
        titulo = "Reunión para actualizar"
        hora_inicio = "19:00"
        descripcion = "Original"
        id_reunion = crear_reunion(fecha, titulo, hora_inicio, descripcion)
        self.assertIsNotNone(id_reunion)
        # Actualizar la reunión
        nuevo_titulo = "Reunión actualizada"
        nueva_descripcion = "Descripción actualizada"
        actualizar_reunion(id_reunion, fecha, nuevo_titulo, hora_inicio, nueva_descripcion)
        reuniones = obtener_todas_reuniones()
        reunion = next((r for r in reuniones if r["id_reunion"] == id_reunion), None)
        self.assertIsNotNone(reunion)
        if reunion is not None:
            self.assertEqual(reunion["titulo"], nuevo_titulo)
            self.assertEqual(reunion["descripcion"], nueva_descripcion)
        # Limpiar
        eliminar_reunion_completa(id_reunion)

if __name__ == '__main__':
    unittest.main()