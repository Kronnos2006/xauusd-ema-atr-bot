import json
import unittest
from datetime import datetime,timedelta,timezone
from atlas.barreras_estadisticas import evaluar_folds_operaciones, diagnosticar_varianza_entre_ensayos
from atlas.sello_preregistro import verificar_sello
from atlas.laboratorio import Senal
from atlas.validacion_temporal import evaluar_confirmatorio

SHA="a"*40
PUB="2026-10-24T14:00:00Z"
def sellar(s,when="2026-10-24T13:00:00Z"):
    return verificar_sello(s,"Kronnos2006/xauusd-ema-atr-bot",SHA,"research/preregistro.json",
        lambda repo,sha:[{"head_sha":sha,"created_at":when,"status":"completed","conclusion":"success"}],
        lambda sha,path:json.dumps({"id":s.preregistro,"senal_id":s.id,"posicion":s.posicion,"publicada_utc":s.publicada_utc}).encode())

class TestBarreras(unittest.TestCase):
    def test_h3_varianza_entre_ensayos_sin_promocion(self):
        a=[.02,-.01]*15
        b=[.03,-.01]*15
        r=diagnosticar_varianza_entre_ensayos([a,b],2)
        self.assertEqual(r["estado"],"DIAGNOSTICO_NO_CONFIRMATORIO")
        self.assertGreater(r["varianza_sharpe_observada"],0)
        self.assertFalse(r["promocion_permitida"])
    def test_h3_un_ensayo_inconcluso(self):
        r=diagnosticar_varianza_entre_ensayos([[.02,-.01]*15],1)
        self.assertEqual(r["estado"],"INCONCLUSA")
    def test_h3_no_acepta_n_reducido(self):
        with self.assertRaises(ValueError):
            diagnosticar_varianza_entre_ensayos([[.02,-.01]*15]*3,1)
    def test_29_operaciones_invalida_fold(self):
        r=evaluar_folds_operaciones([[.01,-.01]*14+[.01]],4,4)
        self.assertEqual(r["folds"][0]["estado"],"INVALIDO")
        self.assertFalse(r["promocion_permitida"])
    def test_30_operaciones_y_fold_dominante(self):
        a=[.03,-.01]*15
        b=[.01,-.005]*15
        r=evaluar_folds_operaciones([a,b],4,4)
        self.assertEqual([f["estado"] for f in r["folds"]],["VALIDO","VALIDO"])
        self.assertEqual(r["fold_dominante"],0)
        self.assertIsNotNone(r["t_stat"])
        self.assertIsNotNone(r["t_stat_sin_dominante"])
        self.assertEqual(r["n_total"],4)
    def test_n_inflado_y_reducido(self):
        for n in (3,5):
            with self.assertRaises(ValueError):
                evaluar_folds_operaciones([[.01,-.01]*15],4,n)
    def test_fecha_igual_o_posterior_rechazada(self):
        senal=Senal("a",PUB,1,"PRE-1",True)
        self.assertFalse(sellar(senal,PUB))
        self.assertFalse(sellar(senal,"2026-10-24T15:00:00Z"))
        self.assertTrue(sellar(senal))
    def test_run_fallido_no_sella(self):
        s=Senal("a",PUB,1,"PRE-1",True)
        doc=json.dumps({"id":s.preregistro,"senal_id":s.id,"posicion":s.posicion,"publicada_utc":s.publicada_utc}).encode()
        for conclusion in ("failure","cancelled",None):
            self.assertFalse(verificar_sello(s,"Kronnos2006/xauusd-ema-atr-bot",SHA,"x.json",
                lambda *a:[{"head_sha":SHA,"created_at":"2026-10-24T13:00:00Z","status":"completed","conclusion":conclusion}],
                lambda *a:doc))
    def test_senal_modificada_mismo_preregistro(self):
        s=Senal("a",PUB,1,"PRE-1",True)
        self.assertFalse(verificar_sello(s,"Kronnos2006/xauusd-ema-atr-bot",SHA,"x.json",
            lambda *a:[{"head_sha":SHA,"created_at":"2026-10-24T13:00:00Z","status":"completed","conclusion":"success"}],
            lambda *a:json.dumps({"id":"PRE-1","senal_id":"otra","posicion":1,"publicada_utc":PUB}).encode()))
    def test_dsr_descriptivo_no_pasa_barrera(self):
        r=evaluar_folds_operaciones([[.02,.01]*15]*3,1,1)
        self.assertFalse(r["pasa_barreras_estadisticas"])
    def test_cadena_git_con_documento_distinto(self):
        s=Senal("a",PUB,1,"PRE-1",True)
        self.assertFalse(verificar_sello(s,"Kronnos2006/xauusd-ema-atr-bot",SHA,
                          "x.json",lambda *a:[{"head_sha":SHA,"created_at":"2026-10-24T13:00:00Z"}],
                          lambda *a:b'{"id":"OTRO"}'))
    def test_cadena_sin_ancla_rechazada_aunque_bool_true(self):
        s=Senal("a",PUB,1,"PRE-1",True)
        self.assertFalse(verificar_sello(s,"Kronnos2006/xauusd-ema-atr-bot",SHA,
                          "x.json",lambda *a:[],lambda *a:b'{"id":"PRE-1"}'))
    def test_gate_rechaza_retornos_inventados_aunque_sello_valido(self):
        s=Senal("a",PUB,1,"PRE-1",True)
        with self.assertRaisesRegex(ValueError,"confirmatorio bloqueado"):
            evaluar_confirmatorio([[.01]*30]*3,1,1,[s],
                "Kronnos2006/xauusd-ema-atr-bot",{"a":(SHA,"x.json")},
                lambda *a:[{"head_sha":SHA,"created_at":"2026-10-24T13:00:00Z"}],
                lambda *a:b'{"id":"PRE-1"}')
    def test_resultados_descriptivos_jamas_promueven(self):
        r=evaluar_folds_operaciones([[.01]*30]*3,1,1)
        self.assertFalse(r["promocion_permitida"])
    def test_created_at_none_falla_cerrado(self):
        s=Senal("a",PUB,1,"PRE-1",True)
        self.assertFalse(verificar_sello(s,"Kronnos2006/xauusd-ema-atr-bot",SHA,
             "x.json",lambda *a:[{"head_sha":SHA,"created_at":None}],
             lambda *a:b'{"id":"PRE-1"}'))
    def test_gate_no_permite_resultado_sin_sello(self):
        s=Senal("a",PUB,1,"PRE-1",True)
        with self.assertRaises(ValueError):
            evaluar_confirmatorio([[.02,-.01]*15],4,4,[s],
                    "Kronnos2006/xauusd-ema-atr-bot",{"a":(SHA,"x.json")},
                    lambda *a:[],lambda *a:b'{"id":"PRE-1"}')
if __name__=="__main__":
    unittest.main()
