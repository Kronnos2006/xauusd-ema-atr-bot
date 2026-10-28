#!/usr/bin/env python3
"""Kronnos: prueba criptográfica RFC3161 con TSA local autocreada SOLO para CI.
Prueba el código de verificación, NO demuestra custodia independiente.
"""
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from atlas_verificador_evidencias import check

def cmd(*args):
    p=subprocess.run(args,check=False,capture_output=True,text=True,timeout=30)
    if p.returncode:
        raise RuntimeError(f"Comando fallido: {args[0]} {args[1] if len(args)>1 else ''}: {p.stderr[-300:]}")
    return p

def run():
    with tempfile.TemporaryDirectory() as td:
        d=Path(td)
        (d/"data.txt").write_text("KRONNOS RFC3161 TEST ONLY",encoding="utf-8")
        (d/"ext.cnf").write_text("[v3_tsa]\nbasicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,nonRepudiation\nextendedKeyUsage=critical,timeStamping\n")
        cmd("openssl","req","-x509","-newkey","rsa:2048","-nodes","-keyout",str(d/"tsa.key"),"-out",str(d/"tsa.pem"),"-subj","/CN=Kronnos Test TSA Only","-days","1","-sha256","-extensions","v3_tsa","-config",str(d/"req.cnf")) if False else None
        (d/"req.cnf").write_text("[req]\ndistinguished_name=dn\nx509_extensions=v3_tsa\nprompt=no\n[dn]\nCN=Kronnos Test TSA Only\n[v3_tsa]\nbasicConstraints=critical,CA:TRUE\nkeyUsage=critical,keyCertSign,cRLSign,digitalSignature\n")
        cmd("openssl","req","-x509","-newkey","rsa:2048","-nodes","-keyout",str(d/"ca.key"),"-out",str(d/"ca.pem"),"-days","1","-sha256","-config",str(d/"req.cnf"))
        cmd("openssl","req","-new","-newkey","rsa:2048","-nodes","-keyout",str(d/"tsa.key"),"-out",str(d/"tsa.csr"),"-subj","/CN=Kronnos Test Timestamp Signer")
        cmd("openssl","x509","-req","-in",str(d/"tsa.csr"),"-CA",str(d/"ca.pem"),"-CAkey",str(d/"ca.key"),"-CAcreateserial","-out",str(d/"tsa.pem"),"-days","1","-sha256","-extfile",str(d/"ext.cnf"),"-extensions","v3_tsa")
        (d/"serial").write_text("01\n")
        (d/"ts.cnf").write_text(""+
            "[tsa]\ndefault_tsa=tsa_config\n[tsa_config]\nserial="+str(d/"serial")+"\n"+
            "signer_cert="+str(d/"tsa.pem")+"\nsigner_key="+str(d/"tsa.key")+"\n"+
            "signer_digest=sha256\ndefault_policy=1.2.3.4.1\ndigests=sha256\n"+
            "accuracy=secs:1\nordering=yes\ntsa_name=yes\ness_cert_id_chain=no\n")
        cmd("openssl","ts","-query","-data",str(d/"data.txt"),"-sha256","-cert","-out",str(d/"query.tsq"))
        cmd("openssl","ts","-reply","-config",str(d/"ts.cnf"),"-queryfile",str(d/"query.tsq"),"-out",str(d/"token.tsr"))
        event=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()
        valid=check(d/"data.txt",d/"token.tsr",d/"ca.pem",event,untrusted=d/"tsa.pem")
        if valid["anterior_al_evento"]!="CONFIRMADO":
            raise AssertionError("Sello de prueba no verificó: "+json.dumps(valid))
        (d/"data.txt").write_text("TAMPERED")
        tampered=check(d/"data.txt",d/"token.tsr",d/"ca.pem",event,untrusted=d/"tsa.pem")
        if tampered["integridad"]!="NO_VERIFICADA":
            raise AssertionError("El sello aceptó datos modificados")
        return {"test_ca":"SELF_SIGNED_CI_ONLY","real_external_custody":False,
                "valid_token_verified":True,"tamper_rejected":True,"promotion_permitted":False}
if __name__=="__main__":
    try:
        print(json.dumps(run(),sort_keys=True))
    except Exception as e:
        print(str(e),file=sys.stderr)
        sys.exit(2)
