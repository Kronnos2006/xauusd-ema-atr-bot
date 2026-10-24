import unittest
from atlas.portafolio import evaluar_portafolio

class TestPortafolio(unittest.TestCase):
    def test_concentracion_y_correlacion(self):
        r = evaluar_portafolio({"a":[.01,-.02,.03,.01],"b":[.01,-.02,.03,.01]},
                               {"a":.5,"b":.5})
        self.assertFalse(r["aprobado_riesgo"])
        self.assertTrue(any("correlación" in a for a in r["alertas"]))
        self.assertTrue(any("concentración" in a for a in r["alertas"]))
    def test_limite_drawdown(self):
        r = evaluar_portafolio({"a":[-.3,0,.01,.02]}, {"a":1},
                               limite_peso=1, limite_drawdown=.2)
        self.assertTrue(any("drawdown" in a for a in r["alertas"]))
    def test_pesos_invalidos(self):
        with self.assertRaises(ValueError):
            evaluar_portafolio({"a":[.01,.02,.03]}, {"a":.5})
    def test_informes_sin_operaciones(self):
        r = evaluar_portafolio({"a":[.01,-.02,.03]}, {"a":1}, limite_peso=1)
        self.assertEqual(r["periodos"],3)
        self.assertIn("retorno_total",r)
        self.assertNotIn("orden",r)
if __name__ == "__main__":
    unittest.main()
