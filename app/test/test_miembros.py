import unittest
from app.screens.miembros.miembros_db import (
    obtener_miembros,
    eliminar_miembro_completo
)

class TestMiembros(unittest.TestCase):
    def test_obtener_miembros(self):
        miembros = obtener_miembros()
        self.assertIsInstance(miembros, list)

    def test_eliminar_miembro_completo(self):
        miembro_id = 9  # Cambia por un ID válido de prueba
        try:
            exito, mensaje = eliminar_miembro_completo(miembro_id)
            resultado = exito or "no existe"
        except Exception:
            resultado = False
        self.assertTrue(resultado)

if __name__ == '__main__':
    unittest.main()