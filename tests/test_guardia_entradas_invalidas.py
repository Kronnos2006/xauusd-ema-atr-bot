"""Regresiones de falsos sanos; datos sintéticos, sin red ni ejecuciones Actions."""
import datetime as dt
import unittest
from tools import guardia_salud as g

NOW = dt.datetime(2026, 11, 1, 18, tzinfo=dt.timezone.utc)
GOOD = '2026-11-01T17:59:00+00:00'
INVALID = ['mañana', '2026-11-01T17:00:00', '2026-11-02T00:00:00Z', 7]


class InvalidInputs(unittest.TestCase):
    def test_invalid_or_future_dates_never_fresh(self):
        for stamp in INVALID:
            with self.subTest(stamp=stamp):
                self.assertTrue(g.frescura({'dato': stamp}, {'dato': 60}, NOW))
                self.assertFalse(g.saltar_duplicada(stamp, 'cron', NOW))
                self.assertTrue(g.tendencia_vieja(stamp, NOW))

    def test_untrusted_run_data_never_relaunches(self):
        cases = [None, {}, [None], [{'status': 'misterio'}],
                 [{'status': 'completed', 'createdAt': GOOD, 'conclusion': None}]]
        cases += [[{'status': 'completed', 'conclusion': 'success', 'createdAt': s}] for s in INVALID]
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(g.decidir_kt002(case, GOOD, NOW)['accion'], 'alerta')
        for stamp in INVALID:
            self.assertEqual(g.decidir_kt002([], stamp, NOW)['accion'], 'alerta')

    def test_unordered_runs_cannot_trigger_dispatch(self):
        runs = [{'status': 'completed', 'conclusion': 'success', 'createdAt': '2026-11-01T12:00:00Z'},
                {'status': 'in_progress', 'createdAt': GOOD}]
        self.assertEqual(g.decidir_kt002(runs, GOOD, NOW)['accion'], 'alerta')

    def test_required_step_not_executed_is_not_healthy(self):
        for result in ['skipped', 'cancelled', '', None, 'neutral']:
            for step in ['publicar', 'kt002']:
                problems = g.verificar_salud('utc,bid\n'+GOOD+',1\n',
                    {'generado_utc': GOOD}, GOOD, None, None, {step: result}, None, NOW)
                self.assertTrue(any('NO VERIFICADO' in p for p in problems))

    def test_optional_measurement_skipped_keeps_remote_validation(self):
        self.assertEqual(g.verificar_salud('utc,bid\n'+GOOD+',1\n',
            {'generado_utc': GOOD}, GOOD, None, None,
            {'spread': 'skipped', 'velas': 'skipped'}, None, NOW), [])

    def test_wrong_json_shape_is_not_healthy(self):
        for trend in [[], 'invalid', 17]:
            self.assertIn('tendencia.json: falta', g.verificar_salud(
                'utc,bid\n'+GOOD+',1\n', trend, GOOD, None, None, {}, None, NOW))


if __name__ == '__main__':
    unittest.main()
