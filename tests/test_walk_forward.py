"""No-leakage del walk-forward: ningún timestamp usado como TEST en un fold
aparece en el TRAIN de ese mismo fold. `construir_bloques_walk_forward` no
se modifica -- este test documenta que ya está bien, no lo arregla."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from research._engine_loader import cargar_engine
from research import data_cache

import datetime


class TestWalkForwardSinLeakage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.eng = cargar_engine()
        cls.tmp_dir = Path(__file__).resolve().parent / "_tmp_snapshots_wf"
        df, _, _ = data_cache.get_or_fetch(
            "XAUUSD", "M15", datetime.date(2025, 1, 1), datetime.date(2025, 6, 1),
            cache_dir=cls.tmp_dir,
        )
        cls.df = cls.eng.calcular_indicadores(df)

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def test_ningun_timestamp_de_test_aparece_en_train(self):
        folds = self.eng.construir_bloques_walk_forward(self.df, 4)
        self.assertEqual(len(folds), 4)
        for i, (train, test) in enumerate(folds, start=1):
            interseccion = set(train.index) & set(test.index)
            self.assertEqual(interseccion, set(), f"Fold {i}: TRAIN y TEST comparten índices {interseccion}")

    def test_test_es_siempre_posterior_a_train(self):
        folds = self.eng.construir_bloques_walk_forward(self.df, 4)
        for i, (train, test) in enumerate(folds, start=1):
            self.assertLess(
                train["time"].max(), test["time"].min(),
                f"Fold {i}: el TRAIN no termina antes de que empiece el TEST",
            )

    def test_train_crece_y_test_es_disjunto_entre_folds(self):
        folds = self.eng.construir_bloques_walk_forward(self.df, 4)
        tamanos_train = [len(train) for train, _ in folds]
        self.assertEqual(tamanos_train, sorted(tamanos_train), "TRAIN debería crecer (expanding window)")

        test_index_sets = [set(test.index) for _, test in folds]
        for i in range(len(test_index_sets)):
            for j in range(i + 1, len(test_index_sets)):
                self.assertEqual(
                    test_index_sets[i] & test_index_sets[j], set(),
                    f"TEST del fold {i+1} y {j+1} se superponen",
                )


if __name__ == "__main__":
    unittest.main()
