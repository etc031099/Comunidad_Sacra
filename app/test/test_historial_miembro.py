import unittest
from app.screens.miembros.historial_miembro_db import (
    obtener_miembros,
    obtener_historial_miembro
)

class TestHistorialMiembro(unittest.TestCase):
    def test_obtener_miembros(self):
        miembros = obtener_miembros()
        self.assertIsInstance(miembros, list)

    def test_obtener_historial_miembro(self):
        miembros = obtener_miembros()
        if miembros:
            id_miembro = miembros[0][0]  # Primer miembro
            periodo = "Todo el Historial"
            tipo_evento_filtro = "Todos"
            estado_filtro = "Todos"
            historial = obtener_historial_miembro(id_miembro, periodo, tipo_evento_filtro, estado_filtro)
            self.assertIsInstance(historial, list)

if __name__ == '__main__':
    unittest.main()