"""Offline installation/recovery smoke with synthetic fixtures only. No market or orders."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

try:
    from .kronnos_finance_offline import metrics, exposure_guard
    from .lineage_kronnos import build_manifest, verify, write_new
except ImportError:
    from kronnos_finance_offline import metrics, exposure_guard
    from lineage_kronnos import build_manifest, verify, write_new

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ('returns.csv', 'report.json')


def verify_snapshot(folder):
    """Checks content integrity only; never external custody or financial validity."""
    try:
        manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        paths = sorted(x['path'] for x in manifest['payload']['inputs'])
        if paths != sorted(INPUTS):
            return False
        return verify(folder, manifest)
    except (OSError, ValueError, KeyError, TypeError):
        return False


def create_snapshot(folder, git_sha):
    folder.mkdir(parents=True, exist_ok=False)
    rows = [(0.01,0.005),(-0.015,-0.01),(0.02,0.015),(-0.003,0.001)]*4
    with (folder/'returns.csv').open('x',newline='',encoding='utf-8') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['synthetic_return','synthetic_benchmark'])
        writer.writerows(rows)
    with (folder/'returns.csv').open(newline='',encoding='utf-8') as stream:
        loaded=list(csv.DictReader(stream))
    a=[float(x['synthetic_return']) for x in loaded]
    b=[float(x['synthetic_benchmark']) for x in loaded]
    result=metrics(a,b,annualization=365,cost_per_period=0.002)
    gross=metrics(a,b,annualization=365,cost_per_period=0)
    if not result['net_total_return'] < gross['net_total_return']:
        raise ValueError('Cost pipeline failed')
    limits=exposure_guard([.25]*4,max_gross=1,max_single=.25)
    report={'kind':'SYNTHETIC_SOFTWARE_SMOKE_ONLY','metrics':result,'exposure':limits,
            'cost_assumption':'0.002 per synthetic period, NOT a calibrated execution model',
            'promotion_permitted':False,'full_risk_framework_verified':False,'orders_sent':0}
    (folder/'report.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    manifest=build_manifest(folder,INPUTS,'SYNTHETIC-SMOKE-v1',git_sha)
    write_new(folder/'manifest.json',manifest)
    if not verify_snapshot(folder):
        raise ValueError('Generated manifest does not verify')
    return report


def restore_snapshot(source, destination):
    if not verify_snapshot(source):
        raise ValueError('Refusing corrupt or incomplete snapshot')
    destination.mkdir(parents=True,exist_ok=False)
    for name in (*INPUTS,'manifest.json'):
        shutil.copyfile(source/name,destination/name)
    if not verify_snapshot(destination):
        raise ValueError('Restored snapshot does not verify')


def run():
    if sys.version_info < (3,10):
        raise RuntimeError('Python >=3.10 required')
    sha=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    dirty=subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain','--',
        'tools/installation_smoke.py','tools/kronnos_finance_offline.py',
        'tools/lineage_kronnos.py'],text=True).strip()
    sources={}
    for name in ('installation_smoke.py','kronnos_finance_offline.py','lineage_kronnos.py'):
        sources[name]=hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='kronnos-smoke-') as tmp:
        base=Path(tmp)
        report=create_snapshot(base/'snapshot',sha)
        restore_snapshot(base/'snapshot',base/'restored')
        if (base/'snapshot/report.json').read_bytes() != (base/'restored/report.json').read_bytes():
            raise ValueError('Restored report differs')
        (base/'restored/returns.csv').write_text('CORRUPTED',encoding='utf-8')
        if verify_snapshot(base/'restored'):
            raise ValueError('Corruption was accepted')
    return {'status':'PASS','scope':'SYNTHETIC_SOFTWARE_INSTALL_AND_RESTORE',
            'git_head':sha,'source_worktree_dirty':bool(dirty),
            'source_sha256':sources,'python':sys.version.split()[0],
            'observations':report['metrics']['observations'],
            'recovery_verified':True,'corruption_rejected':True,
            'market_data_used':False,'external_custody_verified':False,
            'full_project_delivery_approved':False,'promotion_permitted':False,'orders_sent':0}


if __name__=='__main__':
    try:
        print(json.dumps(run(),sort_keys=True,indent=2))
    except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError) as exc:
        print(json.dumps({'status':'FAIL','error':str(exc)}))
        sys.exit(1)
