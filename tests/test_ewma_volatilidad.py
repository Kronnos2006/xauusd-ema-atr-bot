import math
import unittest
from tools.ewma_volatilidad import forecasts, compare

class EWMATests(unittest.TestCase):
    def test_primera_prediccion_no_mira_el_futuro(self):
        a=[0.01]*30+[0.8,0.02]
        b=[0.01]*30+[-0.5,0.02]
        self.assertEqual(forecasts(a)[0][1],forecasts(b)[0][1])
        self.assertNotEqual(forecasts(a)[1][1],forecasts(b)[1][1])
    def test_no_acepta_nan_ni_lambda_invalida(self):
        with self.assertRaises(ValueError): forecasts([0.01]*35,1)
        with self.assertRaises(ValueError): forecasts([0.01]*34+[math.nan])
    def test_ventana_valida_y_muestra(self):
        r=[(i%7-3)/100 for i in range(100)]
        v=compare(r)
        self.assertEqual(v["observaciones"],70)
        self.assertGreaterEqual(v["mse_ewma"],0)
        self.assertGreaterEqual(v["mse_historica"],0)

if __name__=="__main__": unittest.main()
