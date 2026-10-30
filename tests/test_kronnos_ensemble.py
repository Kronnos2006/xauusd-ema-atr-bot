import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from kronnos_ensemble import combine
def row(model,pred,id):
    return {"model":model,"prediction":pred,"prediction_id":id,"instrument":"BTCUSDT",
      "created_utc":"2026-10-28T00:00:00Z","target_utc":"2026-10-28T01:00:00Z","artifact_sha256":"a"*64}
class Tests(unittest.TestCase):
    def test_mean(self):
        r=combine({"predictions":[row("Kronos",1,"1"),row("TimesFM",-0.5,"2")]})
        self.assertEqual(r["ensemble"][0]["score"],.25)
        self.assertFalse(r["promotion_permitted"])
    def test_insufficient(self):
        self.assertEqual(combine({"predictions":[row("Kronos",1,"1")]})["n_groups"],0)
    def test_duplicate(self):
        with self.assertRaises(ValueError):combine({"predictions":[row("Kronos",1,"1")]*2})
    def test_future(self):
        x=row("Kronos",1,"1");x["created_utc"]=x["target_utc"]
        with self.assertRaises(ValueError):combine({"predictions":[x]})
    def test_nan(self):
        x=row("Kronos",float("nan"),"1")
        with self.assertRaises(ValueError):combine({"predictions":[x]})
    def test_multiple_model_same_target(self):
        with self.assertRaises(ValueError):combine({"predictions":[row("Kronos",1,"1"),row("Kronos",.5,"2")]})
    def test_missing_required(self):
        x=row("Kronos",1,"1");del x["instrument"]
        with self.assertRaises(ValueError):combine({"predictions":[x]})
if __name__=="__main__":unittest.main()
