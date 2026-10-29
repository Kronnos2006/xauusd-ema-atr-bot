import csv,sys,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from kronnos_freqai_bridge import convert

class TestBridge(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.src=Path(self.temp.name)/"bars.csv";self.dst=Path(self.temp.name)/"out.csv"
    def write(self,rows):
        with self.src.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=("time_open_ms","open","high","low","close","volume","time_close_ms"))
            w.writeheader();w.writerows(rows)
    def rows(self):
        return [dict(time_open_ms=i*3600000+1000,open=100,high=110,low=90,close=105,volume=5,time_close_ms=i*3600000+3599999) for i in range(3)]
    def test_valid(self):
        self.write(self.rows());m=convert(self.src,self.dst)
        self.assertEqual(m["rows"],3);self.assertFalse(m["training_executed"])
    def test_duplicates_rejected(self):
        rows=self.rows();rows[1]["time_open_ms"]=rows[0]["time_open_ms"]
        self.write(rows)
        with self.assertRaises(ValueError):convert(self.src,self.dst)
    def test_nan_rejected(self):
        rows=self.rows();rows[1]["high"]="nan";self.write(rows)
        with self.assertRaises(ValueError):convert(self.src,self.dst)
    def test_future_rejected(self):
        rows=self.rows();rows[2]["time_close_ms"]=int(datetime.now(timezone.utc).timestamp()*1000)+1000000
        self.write(rows)
        with self.assertRaises(ValueError):convert(self.src,self.dst)
if __name__=="__main__":unittest.main()
