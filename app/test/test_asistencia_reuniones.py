import unittest
from app.screens.asistencia.asistencia_reunion_db import (
    obtener_miembros_asignados,
    guardar_justificacion,
    cambiar_estado_miembro
)

class TestAsistenciaReuniones(unittest.TestCase):
    def test_obtener_miembros_asignados(self):
        id_reunion = 1  # Usa un ID válido de tu base de datos
        miembros = obtener_miembros_asignados(id_reunion)
        self.assertIsInstance(miembros, list)

    def test_guardar_justificacion(self):
        id_reunion = 1  # Usa un ID válido
        miembro_id = 1  # Usa un ID válido
        descripcion = "Motivo de prueba"
        try:
            guardar_justificacion(id_reunion, miembro_id, descripcion)
            resultado = True
        except Exception:
            resultado = False
        self.assertTrue(resultado)

    def test_cambiar_estado_miembro(self):
        id_reunion = 1  # Usa un ID válido
        miembro_id = 1  # Usa un ID válido
        presente = True
        try:
            cambiar_estado_miembro(id_reunion, miembro_id, presente)
            resultado = True
        except Exception:
            resultado = False
        self.assertTrue(resultado)

if __name__ == '__main__':
    unittest.main()