"""Regresiones de procedencia y censo (sin datos de mercado ni red)."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from atlas.evidencia_confirmatoria import (
    censar_variantes, reconstruir_operaciones, preparar_evidencia)
from atlas.laboratorio import Barra, Senal


def fijar(root, name, data):
    raw = json.dumps(data, sort_keys=True).encode()
    path = Path(root) / name
    path.write_bytes(raw)
    return path, hashlib.sha256(raw).hexdigest()


class TestEvidencia(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.censo = {"schema": "atlas-variantes-v1", "variantes": [
            {"id": "v1", "preregistro": "pre1"},
            {"id": "v2", "preregistro": "pre2"}]}
        self.ruta_censo, self.sha_censo = fijar(self.tmp.name, "censo.json", self.censo)
        self.barras = [
            {"apertura_utc": f"2026-10-24T{h:02d}:00:00Z",
             "cierre_utc": f"2026-10-24T{h+1:02d}:00:00Z",
             "apertura": 100.0, "cierre": 101.0} for h in range(4)]
        self.ruta_barras, self.sha_barras = fijar(self.tmp.name, "barras.json", self.barras)
        self.s = Senal("s1", "2026-10-24T00:30:00Z", 1, "pre1", True)

    def sellos(self):
        return {"repo": "Kronnos2006/xauusd-ema-atr-bot",
                "referencias": {"s1": ("a"*40, "prereg.json")},
                "obtener_anclas": lambda repo, sha: [{"head_sha": sha,
                    "created_at": "2026-10-24T00:01:00Z"}],
                "leer_git": lambda sha, path: b'{"id":"pre1"}'}

    def test_censo_contado_no_parametro_manual(self):
        self.assertEqual(censar_variantes(self.ruta_censo, self.sha_censo)["n_total"], 2)

    def test_censo_inflado_reducido_rechazado(self):
        for n in (1, 3):
            doc = dict(self.censo, n_total=n)
            p, sha = fijar(self.tmp.name, "otro.json", doc)
            with self.assertRaises(ValueError):
                censar_variantes(p, sha)

    def test_censo_duplicado_rechazado(self):
        doc = dict(self.censo, variantes=[self.censo["variantes"][0]]*2)
        p, sha = fijar(self.tmp.name, "otro.json", doc)
        with self.assertRaises(ValueError):
            censar_variantes(p, sha)

    def test_censo_reescrito_falla_sha(self):
        self.ruta_censo.write_text('{"schema":"atlas-variantes-v1","variantes":[]}')
        with self.assertRaisesRegex(ValueError, "SHA256"):
            censar_variantes(self.ruta_censo, self.sha_censo)

    def test_retorno_calculado_no_inyectado(self):
        evidencia = preparar_evidencia(
            self.ruta_barras, self.sha_barras, self.ruta_censo, self.sha_censo,
            [self.s], costo_lado=0, **self.sellos())
        self.assertEqual(len(evidencia["operaciones"]), 1)
        self.assertAlmostEqual(evidencia["operaciones"][0]["retorno_neto"], 1.01**3-1)
        self.assertEqual(evidencia["n_total"], 2)
        self.assertFalse(evidencia["promocion_permitida"])

    def test_senal_no_sellada_rechazada(self):
        s = Senal("s1", self.s.publicada_utc, 1, "pre1", False)
        with self.assertRaisesRegex(ValueError, "sello"):
            reconstruir_operaciones([Barra(**x) for x in self.barras], [s])

    def test_sello_falso_no_es_prueba(self):
        with self.assertRaisesRegex(ValueError, "sello externo"):
            preparar_evidencia(
                self.ruta_barras, self.sha_barras,
                self.ruta_censo, self.sha_censo, [self.s],
                repo="Kronnos2006/xauusd-ema-atr-bot",
                referencias={"s1": ("a"*40, "prereg.json")},
                obtener_anclas=lambda *x: [],
                leer_git=lambda *x: b'{"id":"pre1"}')

    def test_barras_modificadas_rechazadas(self):
        self.ruta_barras.write_text("[]")
        with self.assertRaisesRegex(ValueError, "SHA256"):
            preparar_evidencia(self.ruta_barras, self.sha_barras,
                              self.ruta_censo, self.sha_censo, [self.s], **self.sellos())

    def test_confirmatorio_sigue_cerrado(self):
        from atlas.validacion_temporal import evaluar_confirmatorio
        with self.assertRaisesRegex(ValueError, "confirmatorio bloqueado"):
            evaluar_confirmatorio([[0.01]*30]*3, 1, 1, [self.s], "x/y", {})


if __name__ == "__main__":
    unittest.main()
