import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from adapter_qlib_kronnos import adapt
def row():
    return dict(model="TimesFM",instrument="BTCUSDT",prediction_id="p1",artifact_sha256="a"*64,
    created_utc="2026-10-28T00:00:00Z",target_utc="2026-10-28T01:00:00Z",prediction=.4)
class TestAdapter(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(adapt([row()])[0]["score"],.4)
    def test_lookahead(self):
        x=row();x["created_utc"]=x["target_utc"]
        with self.assertRaises(ValueError):adapt([x])
    def test_duplicate(self):
        with self.assertRaises(ValueError):adapt([row(),row()])
    def test_hash(self):
        x=row();x["artifact_sha256"]="fake"
        with self.assertRaises(ValueError):adapt([x])
    def test_nonfinite_nan(self):
        x=row();x["prediction"]=float("nan")
        with self.assertRaises(ValueError):adapt([x])
    def test_bool(self):
        x=row();x["prediction"]=True
        with self.assertRaises(ValueError):adapt([x])
if __name__=="__main__":unittest.main()
