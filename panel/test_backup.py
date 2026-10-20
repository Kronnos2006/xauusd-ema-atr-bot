"""Ensayo de copia y lectura del archivo, sobre datos artificiales aislados."""
import importlib.util
import json
from pathlib import Path
import tempfile
import tarfile
import unittest
from unittest.mock import patch
from market import MarketLedger,digest


class BackupTests(unittest.TestCase):
    def test_archive_contains_verifiable_record_and_no_model_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp);ledger=MarketLedger(data/'market-records')
            folder=ledger.root/'fixture';folder.mkdir()
            prediction=dict(id='fixture',issued_ms=123,forecast=[])
            ledger.exclusive(folder/'forecast.json',dict(prediction=prediction,sha256=digest(prediction)))
            (data/'huggingface').mkdir();(data/'huggingface'/'model.safetensors').write_bytes(b'not-a-real-model')
            file=Path(__file__).resolve().parents[1]/'deploy/oracle/backup.py'
            spec=importlib.util.spec_from_file_location('cloud_backup',file)
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            with patch.dict('os.environ',{'KRONOS_DATA_DIR':str(data)}):archive=module.backup()
            with tarfile.open(archive) as tar:
                names=tar.getnames();self.assertIn('manifest.json',names)
                self.assertIn('market-records/fixture/forecast.json',names)
                self.assertFalse(any('huggingface' in name for name in names))
                restored=json.load(tar.extractfile('market-records/fixture/forecast.json'))
                self.assertEqual(digest(restored['prediction']),restored['sha256'])


if __name__=='__main__':unittest.main()
