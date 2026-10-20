"""Copia local con manifiesto. Segunda copia externa requiere configuracion aparte."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tarfile
import io

PROJECT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PROJECT/'panel'))
from config import data_directory
from market import MarketLedger


def backup():
    data=data_directory()
    ledger=MarketLedger(data/'market-records')
    ledger.records()
    files=[]
    for kind in ['market-records','runtime']:
        files.extend(p for p in sorted((data/kind).glob('*/*'))
                     if p.is_file() and p.suffix in ['.json','.csv','.txt'])
    capture=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    destination=data/'backups'
    destination.mkdir(parents=True,exist_ok=True)
    archive=destination/f'{capture}.tar.gz'
    manifest=dict(created_at=datetime.now(timezone.utc).isoformat(),files=[])
    with archive.open('xb') as output, tarfile.open(fileobj=output,mode='w:gz') as tar:
        for source in files:
            blob=source.read_bytes();name=source.relative_to(data).as_posix()
            item=tarfile.TarInfo(name);item.size=len(blob);item.mode=0o600
            tar.addfile(item,io.BytesIO(blob))
            manifest['files'].append(dict(path=name,bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest()))
        blob=json.dumps(manifest,indent=2).encode('utf-8')
        item=tarfile.TarInfo('manifest.json');item.size=len(blob);item.mode=0o600
        tar.addfile(item,io.BytesIO(blob))
    # Abrir y verificar cada contenido antes de dar copia por correcta.
    with tarfile.open(archive,'r:gz') as tar:
        for item in manifest['files']:
            blob=tar.extractfile(item['path']).read()
            assert hashlib.sha256(blob).hexdigest()==item['sha256']
    print(json.dumps(dict(archive=str(archive),files=len(files),external_copy=False)))
    return archive


if __name__=='__main__':backup()
