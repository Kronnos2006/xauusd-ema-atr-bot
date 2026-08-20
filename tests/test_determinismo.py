"""Requisito 1 de Fase 1: mismos datos + misma config = mismo resultado
exacto, siempre. Corre el mismo config.yaml dos veces contra el mismo
snapshot y compara trades.csv -- debe ser idéntico."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import yaml

from research import engine
from tests.fixtures import mt5_stub

_CONFIG_CHICA = {
    "symbol": "XAUUSD",
    "timeframe": "M15",
    "date_from": "2025-01-01",
    "date_to": "2025-02-01",
    "ema_fast": 9,
    "ema_slow": 21,
    "ema_trend": 50,
    "atr_period": 14,
    "sl_atr_mult": 1.5,
    "rr_ratio": 2.0,
    "spread_puntos": 30,
    "use_session_filter": False,
    "n_folds": 2,
    "strategy": "baseline",
}


class TestDeterminismo(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.tmp_dir / "data_snapshots"
        self.config_path = self.tmp_dir / "config.yaml"
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(_CONFIG_CHICA, f)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_misma_config_mismo_snapshot_da_trades_identicos(self):
        exp_dir_1 = self.tmp_dir / "experiments_1"
        exp_dir_2 = self.tmp_dir / "experiments_2"

        carpeta_1 = engine.run(self.config_path, base_experiments_dir=exp_dir_1, base_data_dir=self.data_dir)
        carpeta_2 = engine.run(self.config_path, base_experiments_dir=exp_dir_2, base_data_dir=self.data_dir)

        trades_1 = pd.read_csv(carpeta_1 / "trades.csv")
        trades_2 = pd.read_csv(carpeta_2 / "trades.csv")

        pd.testing.assert_frame_equal(trades_1, trades_2)

        metrics_1 = (carpeta_1 / "metrics.json").read_text(encoding="utf-8")
        metrics_2 = (carpeta_2 / "metrics.json").read_text(encoding="utf-8")
        self.assertEqual(metrics_1, metrics_2)

    def test_segunda_corrida_no_vuelve_a_pedir_datos_a_mt5(self):
        engine.run(self.config_path, base_experiments_dir=self.tmp_dir / "exp_a", base_data_dir=self.data_dir)
        llamadas_antes = len(mt5_stub.call_log)
        engine.run(self.config_path, base_experiments_dir=self.tmp_dir / "exp_b", base_data_dir=self.data_dir)
        llamadas_despues = len(mt5_stub.call_log)
        self.assertEqual(
            llamadas_despues, llamadas_antes,
            "La segunda corrida con el mismo snapshot no debería volver a llamar a MT5",
        )


if __name__ == "__main__":
    unittest.main()
