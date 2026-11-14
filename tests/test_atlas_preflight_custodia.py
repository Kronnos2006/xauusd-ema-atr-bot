import unittest
from atlas.preflight_custodia import huella_definicion, preflight_sin_custodia


class TestPreflightCustodia(unittest.TestCase):
    def setUp(self):
        self.base={"hipotesis":"EMA ATR", "familia":"momentum",
                   "parametros":{"atr":1.5}, "codigo_sha":"a"*40,
                   "datos_ref":{"hash_datos":"b"*64}}

    def test_sin_recibo_no_ejecuta(self):
        r=preflight_sin_custodia(self.base,"I-1")
        self.assertEqual(r["estado"],"INCONCLUSA")
        self.assertFalse(r["ejecucion_permitida"])

    def test_un_atr_distinto_requiere_nueva_alta(self):
        orig=huella_definicion(self.base)
        otra={**self.base,"parametros":{"atr":2.0}}
        self.assertNotEqual(orig,huella_definicion(otra))
        with self.assertRaisesRegex(ValueError,"definicion cambiada"):
            preflight_sin_custodia(otra,"I-1",
                {"intento_id":"I-1","hash_definicion":orig})

    def test_nueva_variante_se_identifica_pero_sigue_cerrada(self):
        otra={**self.base,"parametros":{"atr":2.0}}
        r=preflight_sin_custodia(otra,"I-2",
            {"intento_id":"I-2","hash_definicion":huella_definicion(otra)})
        self.assertFalse(r["ejecucion_permitida"])

    def test_recibo_autodeclarado_no_autoriza(self):
        r=preflight_sin_custodia(self.base,"I-1",
            {"intento_id":"I-1","hash_definicion":huella_definicion(self.base),
             "autenticado":True})
        self.assertEqual(r["estado"],"INCONCLUSA")
        self.assertFalse(r["promocion_permitida"])

    def test_falta_hash_datos_se_rechaza(self):
        self.base["datos_ref"]={}
        with self.assertRaises(ValueError):
            preflight_sin_custodia(self.base,"I-1")
