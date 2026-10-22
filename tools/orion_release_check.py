#!/usr/bin/env python3
"""ORION release gate: verifica las dos interfaces, datos y controles sin red."""
import argparse
import json
import re
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from centro_control import build, ROOT

REPO = "Kronnos2006/xauusd-ema-atr-bot"
EXPECTED_PAGES = "https://kronnos2006.github.io/xauusd-ema-atr-bot/"
REQUIRED_IDS = (
    "chart-main", "chart-models", "history-chart", "workflow-runs",
    "open-issues", "orion-queue", "agents-count", "ops-links", "refresh-live",
    "alerts", "live-time", "command-output",
)
WORKFLOWS = ("orion-pages.yml", "orion-ci.yml", "orion-comandos.yml",
             "orion-arbitro.yml")


def verify(root=ROOT):
    violations = []
    workflow_dir = root / ".github/workflows"
    wf = (workflow_dir / "orion-pages.yml").read_text(encoding="utf-8")
    for needle in ("cp docs/visor/index.html", "cmp docs/visor/index.html",
                   "actions/deploy-pages@v4", "python tools/centro_control.py build --public"):
        if needle not in wf:
            violations.append("Publicación conjunta sin comprobación: " + needle)
    for name in WORKFLOWS:
        if not (workflow_dir / name).is_file():
            violations.append("Workflow ausente: " + name)
    publisher_count = sum("actions/deploy-pages@" in p.read_text(encoding="utf-8")
                          for p in workflow_dir.glob("*.yml"))
    if publisher_count != 1:
        violations.append("Debe haber un único workflow que publique Pages, hay " + str(publisher_count))

    original = (root / "docs/visor/index.html").read_bytes()
    if not original or b"Visor del proyecto" not in original:
        violations.append("Visor Claude original ausente o inesperado")

    with tempfile.TemporaryDirectory() as d:
        target = Path(d) / "site"
        build(target, root=root, public=True)
        (target / "visor").mkdir(parents=True)
        (target / "visor/index.html").write_bytes(original)
        (target / "orion").mkdir(parents=True)
        (target / "orion/index.html").write_bytes((target / "index.html").read_bytes())
        (target / "orion/data.json").write_bytes((target / "data.json").read_bytes())

        if (target / "visor/index.html").read_bytes() != original:
            violations.append("Visor Claude publicado no es idéntico a la fuente")
        if (target / "orion/index.html").read_bytes() != (target / "index.html").read_bytes():
            violations.append("El alias /orion no coincide con la página principal")
        if (target / "orion/data.json").read_bytes() != (target / "data.json").read_bytes():
            violations.append("El alias /orion carece de datos correspondientes")

        html = (target / "index.html").read_text(encoding="utf-8")
        data = json.loads((target / "data.json").read_text(encoding="utf-8"))
        for item in REQUIRED_IDS:
            if not re.search(r'\bid=["\']' + re.escape(item) + r'["\']', html):
                violations.append("Control visual faltante: " + item)
        if "refreshLive();" not in html or "historyChart(" not in html:
            violations.append("Carga de telemetría/históricos ausente")
        if "Claude privado NO VERIFICADO" not in html:
            violations.append("Debe explicitarse que Claude privado no es observable")
        if data["meta"].get("readonly") is not True:
            violations.append("ORION no está declarado solo lectura")
        if data["kt002"].get("rentabilidad_evaluada") is not False:
            violations.append("No se debe afirmar rentabilidad")
        links = data["governance"]["links"]
        if "office" in links or "claude.ai/artifact" in json.dumps(data).lower():
            violations.append("Se expuso una Oficina privada en datos públicos")
        if any(node.get("description") for node in data["agents"]["nodes"]):
            violations.append("Se expusieron instrucciones internas de agentes")
        if links.get("visor") != EXPECTED_PAGES + "visor/":
            violations.append("Enlace al visor Claude incorrecto")
        for key in ("repository", "actions", "tasks", "commands", "arbitro", "pr3", "plan"):
            url = links.get(key)
            if not isinstance(url, str) or urlparse(url).scheme != "https":
                violations.append("Enlace obligatorio ausente/no HTTPS: " + key)
        history = data["kt002"].get("historia", [])
        if history and (history[-1].get("n") != len(history)
                        or any(not 0 <= rate <= 1
                               for pt in history for rate in pt["rates"].values())):
            violations.append("Histórico inconsistente")

    return {"ok": not violations, "checks": {
        "single_pages_publisher": publisher_count == 1,
        "original_claude_visor_preserved": bool(original),
        "orion_mobile_ui_ids": len(REQUIRED_IDS),
        "kt002_readonly": data["meta"].get("readonly"),
        "observations_nonoverlap": len(history),
        "openai_claude_live_control": False,
        "google_login_enabled": False,
        "public_pages_site": True,
    }, "violations": violations}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("ORION release: " + ("PASS" if result["ok"] else "FAIL"))
        for error in result["violations"]:
            print("ERROR:", error)
        for name, value in result["checks"].items():
            print(name + ": " + str(value))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
