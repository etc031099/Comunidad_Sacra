import unittest
from app.screens.faenas.faenas_db import obtener_faenas

class TestFaenas(unittest.TestCase):
    def test_obtener_faenas(self):
        faenas = obtener_faenas()
        self.assertIsInstance(faenas, list)
        if faenas:
            self.assertIn("idFaena", faenas[0])
            self.assertIn("nombre", faenas[0])

if __name__ == "__main__":
    unittest.main()