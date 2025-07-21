import unittest
from app.screens.core.dashboard_db import calcular_kpis

class TestDashboard(unittest.TestCase):
    def test_calculo_kpis(self):
        kpis = calcular_kpis()
        self.assertIn("miembro_del_mes", kpis)
        self.assertIn("asistencia_perfecta", kpis)
        self.assertIn("cero_penalizaciones", kpis)
        # Puedes agregar más asserts según los valores esperados

if __name__ == '__main__':
    unittest.main()