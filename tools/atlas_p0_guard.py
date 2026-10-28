#!/usr/bin/env python3
"""Auditor de preparación ATLAS P0, stdlib y cero LLM.

Chequea la PRESENCIA y coherencia básica de evidencia; NO autentica fuentes
externas ni acredita suficiencia estadística. Nunca habilita promociones.
"""
import argparse
import hashlib
import json
from pathlib import Path

CHECKS = (
    ("censo_exhaustivo", ("census_sha256", "n_variants", "coverage_external_review")),
    ("custodia_inmutable", ("census_custody_uri", "census_custody_receipt_sha256", "custodian_independent")),
    ("datos_temporales", ("market_data_sha256", "market_source_receipt_sha256", "preregistration_receipt_sha256")),
    ("walk_forward", ("folds_report_sha256", "dsr_report_sha256", "costs_report_sha256")),
    ("auditoria_independiente", ("audit_report_sha256", "reviewer_independent", "owner_approval_sha256")),
)
SHA_FIELDS = {field for _, fields in CHECKS for field in fields if field.endswith("_sha256")}
BOOLEAN_FIELDS = {"coverage_external_review", "custodian_independent", "reviewer_independent"}
def plausible(value, field):
    if field in SHA_FIELDS:
        return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)
    if field in BOOLEAN_FIELDS:
        return value is True
    if field == "n_variants":
        return type(value) is int and value > 0
    return isinstance(value,str) and bool(value.strip())

def check(data):
    if not isinstance(data,dict):
        raise ValueError("Manifest JSON debe ser un objeto")
    report=[]
    for name, fields in CHECKS:
        missing=[x for x in fields if not plausible(data.get(x),x)]
        report.append({"control":name,"estado":"EVIDENCIA_DECLARADA_NO_VERIFICADA" if not missing else "BLOQUEADO",
                       "faltantes":missing})
    return {"sistema":"Kronnos ATLAS P0","autoridad":"SOLO_DIAGNOSTICO",
            "promocion_permitida":False,"cierre_p0_autorizado":False,
            "controles":report,"nota":"Campos declarados NO equivalen a prueba de custodia, integridad temporal ni auditoria externa."}

def main():
    p=argparse.ArgumentParser(description="ATLAS P0: diagnostico cero tokens de IA")
    p.add_argument("--manifest",type=Path,help="Manifest JSON de evidencias, no confiable")
    p.add_argument("--out",type=Path,default=Path("artifacts/atlas-p0-report.json"))
    a=p.parse_args()
    data=json.loads(a.manifest.read_text(encoding="utf-8")) if a.manifest and a.manifest.exists() else {}
    report=check(data)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    content=json.dumps(report,sort_keys=True,ensure_ascii=False,indent=2)+"\n"
    a.out.write_text(content,encoding="utf-8")
    digest=hashlib.sha256(content.encode("utf-8")).hexdigest()
    print("Kronnos ATLAS P0 | "+", ".join(x["control"]+":"+x["estado"] for x in report["controles"]))
    print("SHA256 reporte:",digest)
    print("Promocion: BLOQUEADA. El manifest es declarativo, no constituye prueba externa.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
