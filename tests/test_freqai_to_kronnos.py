import csv
import hashlib
import io
import unittest
from datetime import datetime,timezone
from tools.freqai_to_kronnos import convert
from tools.kronnos_ensemble import combine

HEADER="instrument,prediction_id,created_utc,target_utc,prediction\n"
GOOD=HEADER+"BTCUSDT,real-1,2026-10-31T12:00:00Z,2026-10-31T16:00:00Z,0.4\n"
def manifest(b):
    return {"producer":"FreqAI","run_id":"run-real","created_utc":"2026-10-31T11:00:00Z","csv_sha256":hashlib.sha256(b).hexdigest()}
NOW=datetime(2026,11,1,tzinfo=timezone.utc)
class Tests(unittest.TestCase):
    def test_validated_bridge_and_ensemble(self):
        b=GOOD.encode()
        result=convert(b,manifest(b),now_utc=NOW)
        second=dict(result["predictions"][0],model="Kronos",prediction_id="k1")
        out=combine({"predictions":result["predictions"]+[second]})
        self.assertEqual(out["n_groups"],1)
        self.assertFalse(out["promotion_permitted"])
        self.assertFalse(out["source_hashes_authenticated"])
    def test_rejects_tampered_csv(self):
        b=GOOD.encode()
        with self.assertRaises(ValueError):convert(b+b" ",manifest(b),now_utc=NOW)
    def test_rejects_leakage_and_duplicate(self):
        for text in [HEADER+"BTCUSDT,id,2026-10-31T16:00:00Z,2026-10-31T12:00:00Z,0.1\n",
                     GOOD+GOOD.splitlines(True)[1]]:
            b=text.encode()
            with self.assertRaises(ValueError):convert(b,manifest(b),now_utc=NOW)
    def test_rejects_fake_nonfinite_and_future(self):
        for text in [GOOD.replace("0.4","nan"),GOOD.replace("0.4","2.3"),
                     GOOD.replace("2026-10-31T12:00:00Z","2027-01-01T12:00:00Z")]:
            b=text.encode()
            with self.assertRaises(ValueError):convert(b,manifest(b),now_utc=NOW)
if __name__=="__main__":unittest.main()
