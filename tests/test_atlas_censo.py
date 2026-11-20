import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from atlas.censo_variantes import CERO, construir_evento, verificar_censo, conciliar_con_inventario_externo


class TestCensoIntentos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ruta = Path(self.tmp.name) / "intentos.jsonl"
        a = construir_evento(CERO, "prueba-1", "variante-a", "pre-1",
                             "2026-10-24T11:00:00Z")
        b = construir_evento(a["hash"], "prueba-2", "variante-b", "pre-2",
                             "2026-10-24T12:00:00Z")
        self.eventos = [a, b]
        self.escribir()

    def escribir(self):
        data = "".join(json.dumps(x, sort_keys=True) + "\n"
                       for x in self.eventos).encode()
        self.ruta.write_bytes(data)
        self.ancla = {"sha256": hashlib.sha256(data).hexdigest(),
                      "lineas": len(self.eventos),
                      "ultimo_hash": self.eventos[-1]["hash"],
                      "corte_utc": "2026-10-24T13:00:00Z"}

    def test_faltan_95_de_100_rechazo(self):
        with self.assertRaisesRegex(ValueError, "censo incompleto"):
            conciliar_con_inventario_externo(self.ruta,self.ancla,
                ["prueba-1","prueba-2"]+[f"oculto-{i}" for i in range(95)],
                autenticado=True)

    def test_cinco_entregados_de_cien_rechazo(self):
        with self.assertRaisesRegex(ValueError, "censo incompleto"):
            conciliar_con_inventario_externo(self.ruta,self.ancla,
                ["prueba-1","prueba-2"]+[f"oculto-{i}" for i in range(98)],
                autenticado=True)

    def test_inventario_no_autenticado_falla_cerrado(self):
        with self.assertRaisesRegex(ValueError, "sin autenticacion"):
            conciliar_con_inventario_externo(self.ruta,self.ancla,["prueba-1","prueba-2"])

    def test_conciliacion_es_diagnostica_no_promueve(self):
        r=conciliar_con_inventario_externo(self.ruta,self.ancla,
            ["prueba-1","prueba-2"],autenticado=True)
        self.assertEqual(r["n_total"],2)
        self.assertFalse(r["promocion_permitida"])

    def test_cuenta_intentos_sin_reduccion(self):
        self.assertEqual(verificar_censo(self.ruta, self.ancla)["n_total"], 2)

    def test_intento_eliminado_falla_anchura(self):
        self.ruta.write_text(json.dumps(self.eventos[0])+"\n")
        with self.assertRaises(ValueError):
            verificar_censo(self.ruta, self.ancla)

    def test_reordenamiento_falla(self):
        self.eventos.reverse()
        self.escribir()
        with self.assertRaisesRegex(ValueError, "cadena rota"):
            verificar_censo(self.ruta, self.ancla)

    def test_reescritura_completa_no_cambia_ancla(self):
        self.eventos[0]["variante_id"] = "revisada"
        self.escribir()
        self.ancla["ultimo_hash"] = "0"*64
        with self.assertRaises(ValueError):
            verificar_censo(self.ruta, self.ancla)

    def test_fecha_posterior_al_corte(self):
        self.ancla["corte_utc"] = "2026-10-24T10:00:00Z"
        with self.assertRaisesRegex(ValueError, "posterior"):
            verificar_censo(self.ruta, self.ancla)

    def test_evento_repetido(self):
        e = construir_evento(self.eventos[-1]["hash"], "prueba-1", "c", "pre-3",
                             "2026-10-24T12:30:00Z")
        self.eventos.append(e)
        self.escribir()
        with self.assertRaisesRegex(ValueError, "repetido"):
            verificar_censo(self.ruta, self.ancla)


from tests.test_atlas_preflight_custodia import TestPreflightCustodia

if __name__ == "__main__":
    unittest.main()
