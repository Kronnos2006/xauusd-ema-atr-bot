import unittest
from atlas.cartera_integrada import conectar_historiales, ejecutar_cartera

class TestCarteraIntegrada(unittest.TestCase):
    def test_conexion_real_de_historial_simulado(self):
        h = {"a":[{"barra":1,"capital_simulado":1.01},{"barra":2,"capital_simulado":1.02},{"barra":3,"capital_simulado":1.01}],
             "b":[{"barra":1,"capital_simulado":.99},{"barra":2,"capital_simulado":1.01},{"barra":3,"capital_simulado":1.0}]}
        x = ejecutar_cartera(h, {"a":.5,"b":.5}, {"choque": {"a":-.3, "b":-.3}},
                            limite_peso=.6)
        self.assertEqual(x["base"]["periodos"],3)
        self.assertFalse(x["pasa_todos"])
        self.assertGreater(x["escenarios"]["choque"]["drawdown_maximo"], .2)
    def test_rechaza_series_desalineadas(self):
        with self.assertRaises(ValueError):
            conectar_historiales({"a":[{"barra":1,"capital_simulado":1}],
                                  "b":[{"barra":2,"capital_simulado":1}]})
    def test_rechaza_capital_corrupto(self):
        with self.assertRaises(ValueError):
            conectar_historiales({"a":[{"barra":1,"capital_simulado":0}]})
    def test_rechaza_escenario_desconocido(self):
        h = {"a":[{"barra":i,"capital_simulado":1+i*.01} for i in range(1,4)]}
        with self.assertRaises(ValueError):
            ejecutar_cartera(h, {"a":1}, {"x":{"desconocido":-.1}}, limite_peso=1)
if __name__ == "__main__":
    unittest.main()
