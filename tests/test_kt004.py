"""Pruebas de KT-004 con datos sinteticos (sin red, sin modelos, sin datos reales)."""
import gzip
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import kt004_multiactivo as k4
import kt002_prospectivo as kt2


def sintetico(folder, hueco=None):
    rng = np.random.default_rng(1)
    t = pd.date_range('2024-07-01', k4.LAST_CANDLE.tz_localize(None), freq='h', tz='UTC')
    man = dict(activos={})
    for s in k4.SYMBOLS:
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, len(t))))
        df = pd.DataFrame(dict(open_time=t, open=c, high=c * 1.01, low=c * 0.99, close=c, volume=1.0,
                               close_time=t + pd.Timedelta(minutes=59, seconds=59), amount=1.0))
        if hueco and s == 'SOLUSDT':
            df = df[df.open_time != pd.Timestamp(hueco, tz='UTC')]
        p = Path(folder) / f'{s.lower()}_1h.csv.gz'
        df.to_csv(p, index=False, compression='gzip')
        man['activos'][s] = dict(sha256_csv_gz=hashlib.sha256(p.read_bytes()).hexdigest())
    (Path(folder) / 'manifiesto_datos.json').write_text(json.dumps(man))


def shards_falsos(folder, n=3, sesgo=0.0, siempre_sube=False):
    """Pronosticos aleatorios con el formato real; 'sesgo' hace que Kronos acierte mas en ETH."""
    rng = np.random.default_rng(2)
    lista, _ = k4.todas_las_bases(folder)
    frames = {s: k4.load(folder, s) for s in k4.SYMBOLS}
    rows = []
    for s, i in lista:
        df = frames[s]
        ctx = df.iloc[i - k4.CONTEXT + 1:i + 1].reset_index(drop=True)
        c0 = float(ctx.close.iloc[-1])
        real = float(df.close.iloc[i + 4]) / c0 - 1
        kr = abs(rng.normal(0, 0.01)) if siempre_sube else rng.normal(0, 0.01)
        if s == 'ETHUSDT' and rng.random() < sesgo:
            kr = abs(kr) * np.sign(real)
        row = kt2.build_row(ctx, c0 * (1 + kr), c0 * (1 + rng.normal(0, 0.01)), pd.Timestamp.now(tz='UTC'), 0.0)
        row['symbol'] = s
        rows.append(row)
    paths = []
    for j in range(n):
        p = Path(folder) / f'shard-{j}.csv'
        pd.DataFrame(rows[j::n], columns=['symbol'] + kt2.COLUMNS).to_csv(p, index=False)
        paths.append(str(p))
    return paths


class Tests(unittest.TestCase):
    def test_bases_periodo_y_saltos(self):
        with tempfile.TemporaryDirectory() as d:
            sintetico(d, hueco='2025-01-10 05:00')
            lista, info = k4.todas_las_bases(d)
            self.assertEqual(info['ETHUSDT']['primera'], '2024-08-01T00:00:00+00:00')
            self.assertEqual(info['ETHUSDT']['ultima'], '2026-07-31T20:00:00+00:00')
            self.assertEqual(info['ETHUSDT']['bases'], 730 * 6)
            self.assertEqual(info['ETHUSDT']['saltadas'], 0)
            self.assertGreater(info['SOLUSDT']['saltadas'], 90)  # 400 h de contexto con hueco
            frames = {s: k4.load(d, s) for s in k4.SYMBOLS}
            self.assertTrue(all(frames[s].open_time.iloc[i].hour % 4 == 0 for s, i in lista))
            self.assertTrue(all(frames[s].open_time.iloc[i] <= k4.LAST_BASE for s, i in lista))

    def test_hash_alterado_aborta(self):
        with tempfile.TemporaryDirectory() as d:
            sintetico(d)
            p = Path(d) / 'ethusdt_1h.csv.gz'
            p.write_bytes(gzip.compress(gzip.decompress(p.read_bytes()) + b'\n'))
            with self.assertRaises(SystemExit):
                k4.verificar(d)

    def test_unir_nulo_no_pasa_y_sesgo_pasa(self):
        for kw, esperado in ((dict(siempre_sube=True), False), (dict(sesgo=0.2), True)):
            with tempfile.TemporaryDirectory() as d:
                sintetico(d)
                paths = shards_falsos(d, **kw)
                k4.OUT = Path(d) / 'out'
                k4.cmd_unir(d, *paths)
                r = json.loads((k4.OUT / 'resumen.json').read_text())
                self.assertEqual(r['primario']['pasa'], esperado, r['primario'])
                if not esperado:
                    self.assertEqual((r['primario']['solo_modelo'], r['primario']['solo_sube']), (0, 0))
                self.assertEqual(len(r['secundarios_holm']), 5)
                self.assertTrue(all(x['p_holm'] >= x['p_unilateral'] for x in r['secundarios_holm']))

    def test_unir_rechaza_bases_faltantes(self):
        with tempfile.TemporaryDirectory() as d:
            sintetico(d)
            paths = shards_falsos(d)
            k4.OUT = Path(d) / 'out'
            with self.assertRaises(ValueError):
                k4.cmd_unir(d, *paths[:-1])


if __name__ == '__main__':
    unittest.main()
