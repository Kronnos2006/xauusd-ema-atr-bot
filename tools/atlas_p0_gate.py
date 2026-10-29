#!/usr/bin/env python3
"""Kronnos ATLAS P0 gate. Auditoría reutilizable, sin modelos, sin promoción."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from atlas_p0_guard import check as checklist
from atlas_verificador_evidencias import check as verify_stamp

def audit(manifest, proof=None):
    summary=checklist(manifest)
    stamp={"estado":"SIN_EVIDENCIA_EXTERNA"}
    if proof is not None:
        required={"data","tsr","ca_file","event_utc"}
        if not isinstance(proof,dict) or not required.issubset(proof):
            stamp={"estado":"CONFIGURACION_INCOMPLETA"}
        else:
            r=verify_stamp(proof["data"],proof["tsr"],proof["ca_file"],proof["event_utc"],proof.get("untrusted"))
            stamp={"estado":"SELLO_Y_FECHA_VALIDOS_CON_RAIZ_APORTADA" if r["anterior_al_evento"]=="CONFIRMADO" else "RECHAZADO",
                   "detalle":r}
    summary["verificacion_rfc3161"]=stamp
    summary["bloqueos"]=[c["control"] for c in summary["controles"] if c["estado"]!="EVIDENCIA_DECLARADA_NO_VERIFICADA"]
    summary["bloqueos"]+=["custodia_independiente_sin_atestacion_externa",
                         "walk_forward_confirmatorio_no_validado",
                         "auditoria_independiente_pendiente"]
    summary["promocion_permitida"]=False
    summary["cierre_p0_autorizado"]=False
    return summary

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",type=Path)
    parser.add_argument("--stamp-spec",type=Path)
    parser.add_argument("--out",type=Path,default=Path("artifacts/atlas-p0-gate.json"))
    args=parser.parse_args()
    manifest=json.loads(args.manifest.read_text(encoding="utf-8")) if args.manifest else {}
    proof=json.loads(args.stamp_spec.read_text(encoding="utf-8")) if args.stamp_spec else None
    result=audit(manifest,proof)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n"
    args.out.write_text(raw,encoding="utf-8")
    print("Kronnos ATLAS P0: BLOQUEADO | "+str(len(result["bloqueos"]))+" bloqueos | sha256="+hashlib.sha256(raw.encode()).hexdigest())
    return 0
if __name__=="__main__":sys.exit(main())
