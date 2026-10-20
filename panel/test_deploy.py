"""Pruebas de portabilidad y planificacion, sin red ni modelos."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch,Mock
from config import model_python,data_directory
from server import Engine


class DeployTests(unittest.TestCase):
    def test_explicit_python_and_storage(self):
        with patch.dict(os.environ,{'KRONOS_PYTHON':str(Path('custom-python').resolve()),
                                    'KRONOS_DATA_DIR':str(Path('custom-data').resolve())}):
            self.assertEqual(model_python(),Path('custom-python').resolve())
            self.assertEqual(data_directory(),Path('custom-data').resolve())

    def engine(self):
        engine=Engine.__new__(Engine)
        import threading
        engine.lock=threading.Lock();engine.auto=True;engine.ready=True
        engine.next_auto_attempt=0;engine.job={'status':'idle'}
        engine.market=Mock();engine.market.records.return_value=[]
        engine.start=Mock(return_value=(True,'started'))
        return engine

    def test_auto_is_opt_in_and_avoids_overlap(self):
        engine=self.engine();engine.auto=False;engine.auto_tick();engine.start.assert_not_called()
        engine.auto=True;engine.market.records.return_value=[dict(evaluations=[],forecast=[])]
        engine.auto_tick();engine.start.assert_not_called()
        engine.market.records.return_value=[];engine.job={'status':'running'}
        engine.auto_tick();engine.start.assert_not_called()

    def test_auto_starts_once_then_backs_off(self):
        engine=self.engine();engine.auto_tick();engine.start.assert_called_once_with('market')
        engine.auto_tick();engine.start.assert_called_once()

    def test_completed_record_waits_until_last_target(self):
        engine=self.engine()
        engine.market.records.return_value=[dict(evaluations=[{}]*4,
            forecast=[dict(target_close_ms=9999999999999)])]
        engine.auto_tick();engine.start.assert_not_called()


if __name__=='__main__':unittest.main()
