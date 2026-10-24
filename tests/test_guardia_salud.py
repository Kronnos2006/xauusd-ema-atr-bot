import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import guardia_salud as g  # noqa: E402

AHORA = dt.datetime(2026, 10, 23, 12, 39, tzinfo=dt.timezone.utc)


def iso(min_atras):
    return (AHORA - dt.timedelta(minutes=min_atras)).isoformat()


def corrida(status, conclusion=None, creada_min=10, id_=1):
    return {"status": status, "conclusion": conclusion, "createdAt": iso(creada_min), "databaseId": id_}


class Kt002(unittest.TestCase):
    def test_nunca_cancela(self):
        casos = [([corrida("in_progress", creada_min=m)], r) for m in (5, 165, 400) for r in (iso(5), iso(200), None)]
        casos += [([corrida("queued", creada_min=300)], iso(300)), ([corrida("completed", "failure")], iso(500))]
        for corridas, reg in casos:
            self.assertIn(g.decidir_kt002(corridas, reg, AHORA)["accion"], g.ACCIONES)
        self.assertNotIn("cancelar", g.ACCIONES)

    def test_incidente_23_oct_corrida_viva_con_registros_es_ok(self):
        # Corrida 19: creada 09:55, 2h44 en curso, último registro 12:07 (32 min). Debió quedar intacta.
        r = g.decidir_kt002([corrida("in_progress", creada_min=164)], iso(32), AHORA)
        self.assertEqual(r["accion"], "ok")

    def test_viva_sin_registros_escala_no_cancela(self):
        r = g.decidir_kt002([corrida("in_progress", creada_min=200)], iso(180), AHORA)
        self.assertEqual(r["accion"], "alerta")
        self.assertIn("NO cancelar", r["motivo"])

    def test_solape_encola_siguiente(self):
        r = g.decidir_kt002([corrida("in_progress", creada_min=250)], iso(20), AHORA)
        self.assertEqual(r["accion"], "relanzar")

    def test_solape_no_duplica_si_ya_hay_en_cola(self):
        r = g.decidir_kt002([corrida("queued", creada_min=5, id_=2), corrida("in_progress", creada_min=250)], iso(20), AHORA)
        self.assertEqual(r["accion"], "ok")

    def test_cola_corta_ok_cola_larga_alerta(self):
        self.assertEqual(g.decidir_kt002([corrida("queued", creada_min=30)], iso(40), AHORA)["accion"], "ok")
        self.assertEqual(g.decidir_kt002([corrida("queued", creada_min=150)], iso(40), AHORA)["accion"], "alerta")

    def test_fallida_sin_vivas_relanza(self):
        r = g.decidir_kt002([corrida("completed", "failure")], iso(20), AHORA)
        self.assertEqual(r["accion"], "relanzar")

    def test_parado_relanza(self):
        r = g.decidir_kt002([corrida("completed", "success", creada_min=400)], iso(120), AHORA)
        self.assertEqual(r["accion"], "relanzar")

    def test_terminada_reciente_ok(self):
        r = g.decidir_kt002([corrida("completed", "success", creada_min=300)], iso(30), AHORA)
        self.assertEqual(r["accion"], "ok")

    def test_sin_corridas_ni_registro_relanza(self):
        self.assertEqual(g.decidir_kt002([], None, AHORA)["accion"], "relanzar")


class Frescura(unittest.TestCase):
    def test_detecta_viejo_y_faltante(self):
        p = g.frescura({"tendencia": iso(48 * 60), "spread": iso(30), "kt002": None},
                       {"tendencia": 26 * 60, "spread": 180, "kt002": 130}, AHORA)
        self.assertEqual(len(p), 2)
        self.assertTrue(any("tendencia" in x for x in p) and any("kt002: falta" in x for x in p))

    def test_sano(self):
        self.assertEqual(g.frescura({"a": iso(5)}, {"a": 60}, AHORA), [])

    def test_tendencia_vieja_independiente_de_la_hora(self):
        # Causa raíz del 22-oct: la velas solo se calculaban si la guardia corría a las 00 UTC.
        self.assertTrue(g.tendencia_vieja(iso(25 * 60), AHORA))
        self.assertFalse(g.tendencia_vieja(iso(60), AHORA))
        self.assertTrue(g.tendencia_vieja(None, AHORA))


class Cli(unittest.TestCase):
    def test_frescura_devuelve_error_si_hay_problemas(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "c.json")
            json.dump({"archivos": {"x": "2000-01-01T00:00:00+00:00"}, "limites_min": {"x": 60}}, open(f, "w"))
            r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "..", "tools", "guardia_salud.py"), "frescura", "--json", f], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)

    def test_kt002_cli(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "r.json")
            ya = dt.datetime.now(dt.timezone.utc)
            json.dump([{"status": "in_progress", "conclusion": None, "createdAt": (ya - dt.timedelta(minutes=10)).isoformat(), "databaseId": 1}], open(f, "w"))
            r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "..", "tools", "guardia_salud.py"), "kt002", "--corridas", f, "--registro", dt.datetime.now(dt.timezone.utc).isoformat()], capture_output=True, text=True)
            self.assertEqual(json.loads(r.stdout)["accion"], "ok")


if __name__ == "__main__":
    unittest.main()
