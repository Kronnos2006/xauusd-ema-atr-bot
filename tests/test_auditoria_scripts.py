import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from auditoria_scripts import inspect

class AuditTests(unittest.TestCase):
    def test_no_prohibited_import_or_dynamic_exec(self):
        report=inspect(Path(__file__).resolve().parents[1])
        self.assertEqual(report["status"],"PASS",report["issues"])
        self.assertEqual(len(report["sha256"]),7)

if __name__=="__main__":
    unittest.main()
