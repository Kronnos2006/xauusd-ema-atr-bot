import unittest
from datetime import datetime, timedelta, timezone
from atlas.laboratorio import Barra, Senal
from atlas.validacion_temporal import construir_folds, evaluar_fuera_muestra


def barras(n):
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [Barra((t+timedelta(hours=4*i)).isoformat(),
                  (t+timedelta(hours=4*(i+1))).isoformat(), 100, 101)
            for i in range(n)]


class TestValidacionTemporal(unittest.TestCase):
    def test_folds_con_embargo_y_sin_solape_del_mismo_fold(self):
        fs = construir_folds(25, entrenamiento=10, prueba=4, paso=4, embargo=2)
        self.assertEqual(len(fs), 3)
        for f in fs:
            self.assertEqual(f.prueba_inicio - f.entrenamiento_fin, 2)
            self.assertLessEqual(f.entrenamiento_fin, f.prueba_inicio)

    def test_rechaza_sin_datos(self):
        with self.assertRaises(ValueError):
            construir_folds(5, entrenamiento=10, prueba=2, paso=2)

    def test_evaluacion_sin_poder_usar_senal_futura(self):
        bs = barras(20)
        futura = Senal("tarde", bs[-1].cierre_utc, 1, "pre", True)
        r = evaluar_fuera_muestra(bs, [futura], 8, 4, 4, 1, 0)
        self.assertEqual(r["total_folds"], 2)
        self.assertEqual(r["superan_referencia"], 0)

    def test_sello_falso_se_rechaza(self):
        bs = barras(20)
        falsa = Senal("no-validada", bs[2].cierre_utc, 1, "pre", False)
        with self.assertRaises(ValueError):
            evaluar_fuera_muestra(bs, [falsa], 8, 4, 4)

if __name__ == "__main__":
    unittest.main()
