import unittest
from tools.publicar_mercado_seguro import merge_spread, merge_json

class TestPublicacion(unittest.TestCase):
    def test_conserva_ambos_escritores_sin_duplicados(self):
        head = "utc,bid\n"
        a = head + "2026-11-01T01:00:00Z,1\n"
        b = head + "2026-11-01T02:00:00Z,2\n"
        self.assertEqual(merge_spread(a,b), head+"2026-11-01T01:00:00Z,1\n2026-11-01T02:00:00Z,2\n")
        self.assertEqual(merge_spread(b,a), head+"2026-11-01T01:00:00Z,1\n2026-11-01T02:00:00Z,2\n")
    def test_rechaza_mismo_utc_distinto_dato(self):
        with self.assertRaises(ValueError):
            merge_spread("utc,bid\nt,1\n","utc,bid\nt,2\n")
    def test_no_retrocede_tendencia(self):
        old='{"generado_utc":"2026-11-01T01:00:00Z"}'
        new='{"generado_utc":"2026-11-01T02:00:00Z"}'
        self.assertEqual(merge_json("tendencia.json", new, old, new, old),new)
        self.assertEqual(merge_json("tendencia.json", old, new, old, new),new)
if __name__ == "__main__":
    unittest.main()
