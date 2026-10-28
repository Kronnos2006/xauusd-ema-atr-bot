#!/usr/bin/env python3
"""Kronnos ATLAS: verifica RFC3161 usando OpenSSL. Nunca promociona estrategias."""
import argparse,hashlib,json,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path

def openssl(args):
    try:
        p=subprocess.run(["openssl",*args],capture_output=True,text=True,timeout=20)
        return p.returncode==0,(p.stdout+"\n"+p.stderr)[-3000:]
    except (OSError,subprocess.TimeoutExpired) as exc:
        return False,str(exc)

def check(data,tsr,ca,event_utc,untrusted=None):
    report={"integridad":"NO_VERIFICADA","firma_rfc3161":"NO_VERIFICADA",
            "anterior_al_evento":"NO_VERIFICADO","custodia_independiente":"NO_DEMOSTRADA",
            "promocion_permitida":False}
    paths=[data,tsr,ca]+([untrusted] if untrusted else [])
    if not all(Path(p).is_file() and Path(p).stat().st_size>0 for p in paths):
        report["error"]="Archivos inexistentes o vacios";return report
    report["data_sha256"]=hashlib.sha256(Path(data).read_bytes()).hexdigest()
    cmd=["ts","-verify","-data",str(data),"-in",str(tsr),"-CAfile",str(ca)]
    if untrusted:cmd+=["-untrusted",str(untrusted)]
    ok,log=openssl(cmd)
    if not ok:
        report["error"]="OpenSSL rechazo sello, hash o confianza: "+log[-400:];return report
    report["integridad"]="VALIDADA_OPENSSL"
    report["firma_rfc3161"]="VALIDADA_CON_CA_SUMINISTRADA"
    try:
        event=datetime.fromisoformat(event_utc.replace("Z","+00:00"))
        if event.tzinfo is None:raise ValueError()
        event=event.astimezone(timezone.utc)
    except (ValueError,AttributeError):
        report["error"]="Fecha evento invalida o sin zona";return report
    good,details=openssl(["ts","-reply","-in",str(tsr),"-text"])
    if not good:
        report["error"]="No se puede leer genTime";return report
    match=re.search(r"^Time stamp:\s*(.+?)\s*$",details,re.MULTILINE|re.IGNORECASE)
    if not match:
        report["error"]="genTime ausente";return report
    try:
        raw=match.group(1).strip()
        timestamp=datetime.strptime(raw,"%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    except ValueError:
        report["error"]="genTime no reconocido";return report
    report["token_time_utc"]=timestamp.isoformat()
    report["event_utc"]=event.isoformat()
    report["anterior_al_evento"]="CONFIRMADO" if timestamp<event else "FALLO"
    return report

def main():
    p=argparse.ArgumentParser()
    for name in ("data","tsr","ca-file"):p.add_argument("--"+name,required=True)
    p.add_argument("--untrusted")
    p.add_argument("--event-utc",required=True)
    p.add_argument("--out",default="artifacts/atlas-rfc3161.json")
    a=p.parse_args()
    r=check(a.data,a.tsr,a.ca_file,a.event_utc,a.untrusted)
    output=Path(a.out);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print(json.dumps(r,sort_keys=True))
    return 0 if r["anterior_al_evento"]=="CONFIRMADO" else 2
if __name__=="__main__":sys.exit(main())
