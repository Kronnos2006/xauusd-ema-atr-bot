import json
from pathlib import Path
import tempfile
import unittest
from tools.installation_smoke import create_snapshot, restore_snapshot, verify_snapshot

SHA='1'*40  # Synthetic fixture identifier, never asserted as a real commit.


class RecoveryTests(unittest.TestCase):
    def test_end_to_end_restore_and_costs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            r=create_snapshot(root/'source',SHA)
            restore_snapshot(root/'source',root/'dest')
            self.assertEqual((root/'source/report.json').read_bytes(),(root/'dest/report.json').read_bytes())
            self.assertTrue(verify_snapshot(root/'dest'))
            self.assertEqual(r['metrics']['observations'],16)
            self.assertFalse(r['promotion_permitted'])
            self.assertEqual(r['orders_sent'],0)

    def test_tampered_missing_and_malformed_backup_rejected(self):
        for failure in ['tampered','missing','malformed']:
            with self.subTest(failure=failure),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);create_snapshot(root/'source',SHA)
                if failure=='tampered': (root/'source/report.json').write_text('{}')
                if failure=='missing': (root/'source/returns.csv').unlink()
                if failure=='malformed': (root/'source/manifest.json').write_text('not JSON')
                with self.assertRaises(ValueError): restore_snapshot(root/'source',root/'dest')
                self.assertFalse((root/'dest').exists())

    def test_existing_destination_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);create_snapshot(root/'source',SHA)
            (root/'dest').mkdir();(root/'dest/keep.txt').write_text('keep')
            with self.assertRaises(FileExistsError): restore_snapshot(root/'source',root/'dest')
            self.assertEqual((root/'dest/keep.txt').read_text(),'keep')

    def test_manifest_cannot_choose_arbitrary_restore_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);create_snapshot(root/'source',SHA)
            p=root/'source/manifest.json';m=json.loads(p.read_text())
            m['payload']['inputs'][0]['path']='../outside'
            p.write_text(json.dumps(m))
            with self.assertRaises(ValueError): restore_snapshot(root/'source',root/'dest')


if __name__=='__main__': unittest.main()
