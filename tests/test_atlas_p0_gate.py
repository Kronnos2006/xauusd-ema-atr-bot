import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from atlas_p0_gate import audit

class AtlasP0GateTests(unittest.TestCase):
    def test_default_blocks(self):
        r=audit({})
        self.assertFalse(r["promocion_permitida"])
        self.assertFalse(r["cierre_p0_autorizado"])
        self.assertEqual(r["verificacion_rfc3161"]["estado"],"SIN_EVIDENCIA_EXTERNA")
    def test_invalid_spec_rejected(self):
        r=audit({},{"data":"fake"})
        self.assertEqual(r["verificacion_rfc3161"]["estado"],"CONFIGURACION_INCOMPLETA")
    def test_even_valid_stamp_never_promotes(self):
        with patch("atlas_p0_gate.verify_stamp",return_value={"anterior_al_evento":"CONFIRMADO"}):
            r=audit({},{"data":"d","tsr":"t","ca_file":"c","event_utc":"2026-01-01T00:00:00Z"})
        self.assertEqual(r["verificacion_rfc3161"]["estado"],"SELLO_Y_FECHA_VALIDOS_CON_RAIZ_APORTADA")
        self.assertFalse(r["promocion_permitida"])
    def test_all_manifest_claims_still_block(self):
        r=audit({"n_variants":74,"custodian_independent":True})
        self.assertFalse(r["cierre_p0_autorizado"])
if __name__=="__main__":unittest.main()
