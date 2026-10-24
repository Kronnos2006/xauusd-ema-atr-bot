import unittest
from atlas.laboratorio import Barra, Senal, simular

B = [
    Barra("2026-10-01T00:00:00Z", "2026-10-01T04:00:00Z", 100, 100),
    Barra("2026-10-01T04:00:00Z", "2026-10-01T08:00:00Z", 100, 110),
    Barra("2026-10-01T08:00:00Z", "2026-10-01T12:00:00Z", 110, 99),
]

def s(i, hora, pos, sello=True):
    return Senal(i, hora, pos, "preregistro-test", sello)

class TestLaboratorio(unittest.TestCase):
    def test_no_hay_lookahead(self):
        # La señal publicada a las 06:00 no puede beneficiarse del tramo 04:00->08:00.
        r = simular(B, [s("tardia", "2026-10-01T06:00:00Z", -1)], costo_lado=0)
        self.assertEqual(r["historial"][0]["posicion"], 0)
        self.assertEqual(r["historial"][1]["posicion"], -1)
        self.assertAlmostEqual(r["retorno_neto_simulado"], 0.10)

    def test_costo_por_entrada_y_salida(self):
        r = simular(B, [s("temprana", "2026-10-01T03:00:00Z", 1)], costo_lado=.01)
        self.assertAlmostEqual(r["capital_final_simulado"], 1.1*.99**2 * .9*.99**2)
        self.assertEqual(r["periodos"], 2)

    def test_sin_sello_no_hay_simulacion(self):
        with self.assertRaises(ValueError):
            simular(B, [s("inventada", "2026-10-01T01:00:00Z", 1, False)])

    def test_validaciones(self):
        with self.assertRaises(ValueError):
            simular(B, [s("x", "2026-10-01T01:00:00Z", 1)] * 2)
        with self.assertRaises(ValueError):
            simular(B, [], costo_lado=-.1)
        with self.assertRaises(ValueError):
            Barra("2026-10-01T04:00:00Z", "2026-10-01T00:00:00Z", 100, 101)

if __name__ == "__main__":
    unittest.main()
