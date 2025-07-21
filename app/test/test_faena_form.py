import unittest
from app.screens.faenas.faena_form_db import crear_faena, existe_faena_nombre_fecha

class TestFaenaForm(unittest.TestCase):
    def test_crear_faena_y_verificar_duplicado(self):
        datos = {
            "nombre": "Faena Unittest",
            "descripcion": "Prueba automática",
            "fecha_inicio": "2024-07-01 08:00:00",
            "fecha_fin": "2024-07-01 12:00:00",
            "ubicacion": "Parque",
            "estado": "Pendiente",
            "tipo": "Ordinaria",
            "tipoJornada": "Mañana",
            "motivoExtra": ""
        }
        crear_faena(datos)
        self.assertTrue(existe_faena_nombre_fecha("Faena Unittest", "2024-07-01 08:00:00"))
        # Intentar crear duplicado
        self.assertTrue(existe_faena_nombre_fecha("Faena Unittest", "2024-07-01 08:00:00"))

if __name__ == "__main__":
    unittest.main()