"""Targeted static token-policy regression checks, not a GitHub security certification."""
import json
from pathlib import Path
import sys
import yaml

TARGETS = {'estado.yml':('validar_pr','estado'),
           'progreso.yml':('validar_pr','progreso'),
           'kt004.yml':('pruebas',None)}
PR_IF = "github.event_name == 'pull_request'"
PRODUCTION_IF = "github.event_name != 'pull_request' && github.ref == 'refs/heads/master'"


def inspect(root):
    problems=[]
    for name,(pr_job,production_job) in TARGETS.items():
        try:
            doc=yaml.load((Path(root)/'.github/workflows'/name).read_text(encoding='utf-8'),Loader=yaml.BaseLoader)
            job=doc['jobs'][pr_job]
            if job.get('if') != PR_IF:
                problems.append(name+': PR job condition changed')
            permissions=job.get('permissions',doc.get('permissions'))
            if not isinstance(permissions,dict) or not permissions or any(v!='read' for v in permissions.values()):
                problems.append(name+': PR job must declare read-only permissions')
            checkout=[s for s in job['steps'] if s.get('uses','').startswith('actions/checkout@')]
            if not checkout or any(s.get('with',{}).get('persist-credentials')!='false' for s in checkout):
                problems.append(name+': PR checkout persists credentials')
            if production_job and doc['jobs'][production_job].get('if') != PRODUCTION_IF:
                problems.append(name+': publisher not restricted to master/non-PR')
        except (OSError,ValueError,KeyError,TypeError,AttributeError,yaml.YAMLError):
            problems.append(name+': missing or malformed policy')
    return {'status':'FAIL' if problems else 'PASS','problems':problems,
            'scope':'Three named PR jobs and two publisher guards only; no expression evaluator',
            'github_effective_settings_verified':False,'full_permissions_audit_approved':False}


if __name__=='__main__':
    result=inspect(Path(__file__).resolve().parents[1])
    print(json.dumps(result,sort_keys=True,indent=2))
    sys.exit(result['status']!='PASS')
