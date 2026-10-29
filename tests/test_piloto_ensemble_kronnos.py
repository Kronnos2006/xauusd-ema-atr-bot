import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from piloto_ensemble_kronnos import inspect
H="a"*64
def item(model="Kronos",created="2026-10-29T00:00:00Z",target="2026-10-29T01:00:00Z"):
    return dict(model=model,prediction_id="001",created_utc=created,target_utc=target,artifact_sha256=H)
class Tests(unittest.TestCase):
    def test_valid_not_promoted(self):
        r=inspect({"predictions":[item()]})
        self.assertEqual(r["count"],1)
        self.assertFalse(r["execution_verified"])
        self.assertFalse(r["promotion_permitted"])
    def test_future_data(self):
        with self.assertRaises(ValueError):inspect({"predictions":[item(created="2026-10-29T02:00:00Z")]})
    def test_duplicate(self):
        with self.assertRaises(ValueError):inspect({"predictions":[item(),item()]})
    def test_unknown_model(self):
        with self.assertRaises(ValueError):inspect({"predictions":[item(model="Desconocido")]})
    def test_fake_hash(self):
        x=item();x["artifact_sha256"]="fake"
        with self.assertRaises(ValueError):inspect({"predictions":[x]})
if __name__=="__main__":unittest.main()
