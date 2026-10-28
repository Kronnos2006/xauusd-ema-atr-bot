import sys
import tempfile
import json
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from preflight_motores import preflight

class ExternalEvidence(unittest.TestCase):
    def test_reject_synthetic(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a.json"
            p.write_text(json.dumps({"engine":"LEAN","engine_version":"1","run_id":"a","mode":"backtest","synthetic":True,"source_artifact_sha256":"abc"}))
            with self.assertRaises(ValueError): preflight(p,p)
    def test_reject_same_engine(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/"a.json";b=Path(d)/"b.json"
            a.write_text(json.dumps({"engine":"LEAN","engine_version":"1","run_id":"a","mode":"backtest","synthetic":False,"source_artifact_sha256":"abc"}))
            b.write_text(a.read_text())
            with self.assertRaises(ValueError): preflight(a,b)

if __name__=="__main__":unittest.main()
