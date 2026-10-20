"""Copia verificable del registro prospectivo y corridas tecnicas del panel.

No consulta mercados ni ejecuta modelos. No incluye entornos, pesos o claves.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT/'panel'))
from market import MarketLedger


def export_snapshot():
    ledger=MarketLedger(PROJECT/'panel/market-records')
    ledger.records()  # Verificar huellas del registro antes de copiar.
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    destination=PROJECT/'docs/evidencia/panel-snapshots'/stamp
    destination.mkdir(parents=True,exist_ok=False)
    manifest=dict(created_at=datetime.now(timezone.utc).isoformat(),files=[],
        scope='Registro BTC y corridas tecnicas existentes al capturar; no respaldo de pesos/entornos',
        limitations='Una instantanea no guarda resultados posteriores ni certifica fecha externamente')
    sources=[]
    for group,pattern in [('market-records','*/*.json'),('runtime','*/*')]:
        for source in sorted((PROJECT/'panel'/group).glob(pattern)):
            if source.is_file() and source.suffix in ['.json','.csv','.txt']:
                sources.append((group,source))
    for group,source in sources:
        if source.stat().st_size>10_000_000:
            raise ValueError('Archivo inesperadamente grande: '+str(source))
        content=source.read_bytes()
        relative=Path(group)/source.relative_to(PROJECT/'panel'/group)
        target=destination/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(content)
        sha=hashlib.sha256(content).hexdigest()
        assert hashlib.sha256(target.read_bytes()).hexdigest()==sha
        manifest['files'].append(dict(path=relative.as_posix(),bytes=len(content),sha256=sha))
    # Solo exigir que cada fichero capturado siga identico. Nuevas evaluaciones
    # concurrentes quedan fuera de esta instantanea y se capturan en la siguiente.
    for item in manifest['files']:
        source=PROJECT/'panel'/item['path']
        if hashlib.sha256(source.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('La fuente cambio durante la copia; no publicar esta instantanea')
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(dict(destination=destination.relative_to(PROJECT).as_posix(),
        files=len(manifest['files']),bytes=sum(x['bytes'] for x in manifest['files'])),indent=2))
    return destination


if __name__=='__main__':export_snapshot()
