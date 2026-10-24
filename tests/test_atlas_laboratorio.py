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
        # Modelo v2: una entrada y una salida en toda la vida de la posición
        # (v1 cobraba ida y vuelta en cada barra: 1.1*.99**2 * .9*.99**2).
        self.assertAlmostEqual(r["capital_final_simulado"], 1.1 * .9 * .99**2)
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


def plano(n, precio=100.0):
    # n barras de 4 h con precio constante.
    from datetime import datetime, timedelta, timezone
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [Barra((t0 + timedelta(hours=4*i)).isoformat(),
                  (t0 + timedelta(hours=4*i + 4)).isoformat(), precio, precio)
            for i in range(n)]


class TestCostosV2(unittest.TestCase):
    """Regresión del sesgo v1: el benchmark no puede perder solo por costos repetidos."""
    C = .0015

    def test_precio_plano_30_dias_efectivo_vs_benchmark(self):
        b = plano(181)  # 180 barras de 4 h = 30 días
        r = simular(b, [s("cash", "2026-01-01T00:00:00Z", 0)], costo_lado=self.C)
        self.assertEqual(r["retorno_neto_simulado"], 0.0)
        # Benchmark: una entrada y una salida, nada más.
        self.assertAlmostEqual(r["retorno_benchmark"], (1 - self.C)**2 - 1)
        self.assertGreater(r["retorno_benchmark"], -0.004)

    def test_buy_and_hold_igual_al_benchmark(self):
        b = plano(181)
        r = simular(b, [s("larga", "2026-01-01T00:00:00Z", 1)], costo_lado=self.C)
        self.assertAlmostEqual(r["capital_final_simulado"], r["capital_benchmark"])

    def test_cambios_de_posicion_cobran_rotacion(self):
        b = plano(6)  # 5 barras simuladas, precio fijo: el retorno es solo costo
        # Señal publicada al cierre de la barra i-1 rige en la barra i; la última barra queda en efectivo.
        senales = [s("a", "2026-01-01T04:00:00Z", 1),   # entra largo (rot 1)
                   s("b", "2026-01-01T08:00:00Z", -1),  # gira a corto (rot 2)
                   s("c", "2026-01-01T12:00:00Z", -1),  # mantiene (rot 0)
                   s("d", "2026-01-01T16:00:00Z", 0)]   # sale (rot 1)
        r = simular(b, senales, costo_lado=self.C)
        self.assertEqual([h["rotacion"] for h in r["historial"]], [1, 2, 0, 1, 0])
        self.assertAlmostEqual(r["capital_final_simulado"], (1 - self.C)**4)

    def test_posicion_abierta_se_liquida_al_final(self):
        b = plano(3)
        r = simular(b, [s("a", "2026-01-01T00:00:00Z", -1)], costo_lado=self.C)
        self.assertEqual([h["rotacion"] for h in r["historial"]], [1, 1])
        self.assertAlmostEqual(r["capital_final_simulado"], (1 - self.C)**2)

    def test_operacion_con_costos_y_movimiento(self):
        r = simular(B, [s("larga", "2026-10-01T03:00:00Z", 1)], costo_lado=self.C)
        esperado = 1.1 * .9 * (1 - self.C)**2
        self.assertAlmostEqual(r["capital_final_simulado"], esperado)
        self.assertAlmostEqual(r["capital_benchmark"], esperado)
        self.assertEqual(r["modelo_costos"], "costo-por-cambio-de-posicion-v2")


if __name__ == "__main__":
    unittest.main()
