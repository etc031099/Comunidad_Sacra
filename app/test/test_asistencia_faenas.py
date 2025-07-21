import unittest
from app.screens.asistencia.asistencia_faena_db import (
    obtener_miembros_asignados,
    obtener_asistencias_fecha,
    guardar_justificacion,
    marcar_estado_asistencia
)
from datetime import date

class TestAsistenciaFaenas(unittest.TestCase):
    def test_obtener_miembros_asignados(self):
        id_faena = 3  # Cambia por un ID válido
        miembros = obtener_miembros_asignados(id_faena)
        self.assertIsInstance(miembros, list)

    def test_obtener_asistencias_fecha(self):
        id_faena = 3  # Cambia por un ID válido
        fecha = date.today()
        miembros = obtener_asistencias_fecha(id_faena, fecha)
        self.assertIsInstance(miembros, list)

    def test_guardar_justificacion(self):
        id_faena = 2  # Cambia por un ID válido
        miembro_id = 4  # Cambia por un ID válido
        fecha = date.today()
        descripcion = "Justificación de prueba"
        try:
            guardar_justificacion(id_faena, miembro_id, fecha, descripcion)
            resultado = True
        except Exception:
            resultado = False
        self.assertTrue(resultado)

    def test_marcar_estado_asistencia(self):
        id_faena = 3  # Cambia por un ID válido
        miembro_id = 4  # Cambia por un ID válido
        fecha = "2025-06-20"
        estado = "Presente"
        try:
            # Primero intenta marcar como 'Ausente' para asegurarte de que el registro existe
            marcar_estado_asistencia(id_faena, miembro_id, fecha, "Ausente")
            # Ahora marca como 'Presente'
            marcar_estado_asistencia(id_faena, miembro_id, fecha, estado)
            resultado = True
        except Exception as e:
            print("Error en test_marcar_estado_asistencia:", e)
            resultado = False
        self.assertTrue(resultado)

if __name__ == '__main__':
    unittest.main()