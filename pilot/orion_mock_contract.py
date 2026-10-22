#!/usr/bin/env python3
"""B1: prototipo ejecutable de contratos de trabajo; NO ejecuta OpenHands ni TradingAgents.

Sólo datos sintéticos y directorio temporal. La fuente de evidencia es cada evento.
"""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path

ALLOWED = {"workspace/nota.txt"}
PHASES = ("CREATED", "CLAIMED", "PROPOSED", "REVIEWED", "DELIVERED")
ROLES = ("developer", "analyst", "risk", "auditor")


def digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class Evidence:
    def __init__(self):
        self.events = []
        self.previous = "0" * 64

    def append(self, actor, kind, payload):
        event = {"seq": len(self.events) + 1, "actor": actor, "kind": kind,
                 "payload": payload, "prev_hash": self.previous}
        event["hash"] = digest(event)
        self.events.append(event)
        self.previous = event["hash"]
        return event

    def verify(self):
        parent = "0" * 64
        for index, entry in enumerate(self.events):
            if entry["seq"] != index + 1 or entry["prev_hash"] != parent:
                return False
            stripped = {key: value for key, value in entry.items() if key != "hash"}
            if digest(stripped) != entry["hash"]:
                return False
            parent = entry["hash"]
        return True


def write_synthetic(workspace, path, content, evidence):
    if path not in ALLOWED:
        raise PermissionError("Ruta protegida o desconocida")
    relative = Path(path)
    target = (workspace / relative).resolve()
    if not target.is_relative_to(workspace.resolve()):
        raise PermissionError("Ruta fuera de sandbox")
    if not isinstance(content, str) or not content or len(content) > 500:
        raise ValueError("Contenido sintético inválido")
    target.parent.mkdir(parents=True, exist_ok=True)
    # Solo el archivo permitido en sandbox efímero.
    target.write_text(content, encoding="utf-8")
    evidence.append("developer", "synthetic_patch",
                    {"path": path, "sha256": hashlib.sha256(content.encode()).hexdigest()})
    return target


def review(proposal, evidence):
    """La decisión de riesgo es independiente; no se reescribe desde developer."""
    if proposal.get("asset") != "FAKEBTC" or proposal.get("real_orders") is not False:
        raise PermissionError("Solo ejemplo sintético, sin órdenes")
    evidence.append("analyst", "synthetic_analysis", {"dataset": "fabricated", "edge_claimed": False})
    risk_reject = proposal.get("risk_veto", True)
    evidence.append("risk", "veto" if risk_reject else "review_pass",
                    {"reason": "No evidence of edge" if risk_reject else "Synthetic format only"})
    evidence.append("auditor", "independent_review",
                    {"finding": "NO SCIENTIFIC APPROVAL", "veto_respected": True})
    if risk_reject:
        evidence.append("manager", "blocked", {"reason": "risk veto"})
        return "BLOCKED"
    evidence.append("manager", "documented", {"reason": "synthetic demo only"})
    return "DOCUMENTED_ONLY"


def demonstrate():
    evidence = Evidence()
    evidence.append("owner", "request", {"task": "ejemplo-sintetico", "authorized": "sandbox only"})
    evidence.append("developer", "claim", {"scope": sorted(ALLOWED)})
    with tempfile.TemporaryDirectory(prefix="orion-pilot-") as d:
        target = write_synthetic(Path(d), "workspace/nota.txt",
                                 "DEMO: ningún dato real.\n", evidence)
        file_digest = hashlib.sha256(target.read_bytes()).hexdigest()
        evidence.append("developer", "synthetic_test", {"passed": True, "sha256": file_digest})
        decision = review({"asset": "FAKEBTC", "real_orders": False, "risk_veto": True}, evidence)
    if not evidence.verify():
        raise RuntimeError("Cadena de evidencia rota")
    return {
        "stage": "B1 MOCK CONTRACT; NO THIRD-PARTY ENGINE RUN",
        "task": "synthetic file + synthetic finance review",
        "status": decision,
        "evidence_chain_valid": evidence.verify(),
        "generated_orders": 0,
        "connected_agent_sessions": False,
        "external_code_executed": False,
        "scientific_approval": False,
        "events": evidence.events,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    report = json.dumps(demonstrate(), indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    print(report)
