from pathlib import Path
import tempfile
import unittest
import yaml
from tools.workflow_permissions import inspect,TARGETS

ROOT=Path(__file__).resolve().parents[1]


class TokenPolicyTests(unittest.TestCase):
    def fixture(self,root):
        dest=root/'.github/workflows';dest.mkdir(parents=True)
        for name in TARGETS:
            (dest/name).write_bytes((ROOT/'.github/workflows'/name).read_bytes())

    def test_repository_policy(self):
        r=inspect(ROOT);self.assertEqual(r['status'],'PASS',r['problems'])
        self.assertFalse(r['full_permissions_audit_approved'])

    def test_write_inheritance_and_credentials_fail(self):
        for mutation in ['write','inherit','checkout']:
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as d:
                root=Path(d);self.fixture(root);p=root/'.github/workflows/progreso.yml'
                doc=yaml.load(p.read_text(),Loader=yaml.BaseLoader);job=doc['jobs']['validar_pr']
                if mutation=='write':job['permissions']['contents']='write'
                if mutation=='inherit':del job['permissions']
                if mutation=='checkout':del job['steps'][0]['with']['persist-credentials']
                p.write_text(yaml.safe_dump(doc),encoding='utf-8')
                self.assertEqual(inspect(root)['status'],'FAIL')

    def test_publisher_without_trusted_guard_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root);p=root/'.github/workflows/estado.yml'
            doc=yaml.load(p.read_text(),Loader=yaml.BaseLoader)
            doc['jobs']['estado']['if']="github.event_name != 'pull_request'"
            p.write_text(yaml.safe_dump(doc),encoding='utf-8')
            self.assertEqual(inspect(root)['status'],'FAIL')

    def test_missing_and_malformed_policy_fails(self):
        for raw in [None,'not yaml [']:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d);self.fixture(root);p=root/'.github/workflows/kt004.yml'
                if raw is None:p.unlink()
                else:p.write_text(raw)
                self.assertEqual(inspect(root)['status'],'FAIL')


if __name__=='__main__':unittest.main()
