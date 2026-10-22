#!/usr/bin/env python3
"""Centro de Control v1: servidor local de solo lectura, sin dependencias externas.

No coloca órdenes, no modifica datos ni arranca Claude. GitHub Actions continúa
siendo la fuente de las métricas publicadas. No expone servicios en red pública.
"""
import argparse
import csv
import json
import shutil
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "dashboard"
DEFAULT_OUT = ROOT / ".local" / "centro-control"
MODELS = ("siempre_sube", "kronos", "timesfm", "kt001")


def history_series(path):
    """Serie histórica primaria: solo bases UTC múltiplos de 4, puntajes publicados."""
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    points = []
    count = {name: 0 for name in MODELS}
    seen = set()
    for row in sorted(rows, key=lambda x: x.get("base_open_utc", "")):
        base = row.get("base_open_utc", "")
        try:
            instant = datetime.fromisoformat(base.replace("Z", "+00:00"))
            if instant.tzinfo is None or instant.astimezone(timezone.utc).hour % 4:
                continue
            if not row.get("actual_ret", "").strip() or base in seen:
                continue
            actual = float(row["actual_ret"])
            if actual == 0:
                continue
            signs = {"siempre_sube": 1, "kronos": float(row["kronos_ret"]),
                     "timesfm": float(row["timesfm_ret"]), "kt001": float(row["kt001_ret"])}
            if any(value == 0 for value in signs.values()):
                continue
            seen.add(base)
            for name, predicted in signs.items():
                count[name] += int((predicted > 0) == (actual > 0))
            n = len(points) + 1
            points.append({"base_utc": instant.astimezone(timezone.utc).isoformat(),
                           "n": n, "rates": {key: count[key] / n for key in MODELS}})
        except (ValueError, KeyError, TypeError):
            continue
    return points


def assemble(root=ROOT):
    summary = json.loads((root / "data/kt002/resumen.json").read_text(encoding="utf-8"))
    team = json.loads((root / "docs/gerencia/equipo.json").read_text(encoding="utf-8"))
    members = team.get("miembros", [])
    ids = {x["clave"] for x in members}
    if len(ids) != len(members):
        raise ValueError("Claves duplicadas en organigrama")
    links = []
    for member in members:
        parent = member.get("reporta_a")
        if parent:
            if parent not in ids:
                raise ValueError("Reporta a un agente inexistente: " + str(parent))
            links.append({"from": parent, "to": member["clave"], "kind": "reporta"})
    independent = [m["clave"] for m in members if m.get("independiente")]
    nonoverlap = summary["sin_solape"]
    if summary["variant"] != "KT-002" or summary.get("profitability_evaluated") is not False:
        raise ValueError("Experimento distinto o rentabilidad supuestamente evaluada")
    samples = []
    n = nonoverlap.get("n_vencidos", 0)
    for model in MODELS:
        m = nonoverlap[model]
        if m["n"] != n or not (0 <= m["aciertos"] <= n):
            raise ValueError("Conteos incompatibles para " + model)
        samples.append({
            "key": model, "aciertos": m["aciertos"], "n": m["n"],
            "tasa": m["tasa"], "ic95": m.get("ic95", [])})
    return {
        "meta": {
            "source_updated_utc": summary.get("updated_utc"),
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "mode": "SNAPSHOT; NO ES TIEMPO REAL",
            "readonly": True,
        },
        "kt002": {
            "pronosticos": summary.get("pronosticos"),
            "evaluados": summary.get("vencidos"),
            "independientes": n,
            "horas_omitidas_acumuladas": summary.get("horas_omitidas"),
            "rentabilidad_evaluada": False,
            "modelos": samples,
            "historia": history_series(root / "data/kt002/predicciones.csv"),
        },
        "agents": {
            "nodes": [{
                "id": m["clave"], "name": m["nombre"], "area": m["area"],
                "independent": bool(m.get("independiente")),
                "description": m.get("que_hace", ""), "registered_state": m.get("estado", "no registrado"),
            } for m in members],
            "links": links,
            "independent": independent,
            "areas": team.get("areas", {}),
            "important": "El organigrama es configuración, no telemetría en vivo. Los enlaces indican jerarquía declarada, no comunicación observada.",
        },
        "governance": {
            "money": "PAPER ONLY",
            "edge": "NO DEMOSTRADO",
            "reviews": "Consultar GitHub; no sincronizado en vivo",
            "links": {
                "repository": "https://github.com/Kronnos2006/xauusd-ema-atr-bot",
                "actions": "https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions",
                "visor": "https://kronnos2006.github.io/xauusd-ema-atr-bot/visor/",
                "tasks": "https://github.com/Kronnos2006/xauusd-ema-atr-bot/issues/new/choose",
                "commands": "https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/workflows/orion-comandos.yml",
                "arbitro": "https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/workflows/orion-arbitro.yml",
                "pr3": "https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/3",
                "plan": "https://github.com/Kronnos2006/xauusd-ema-atr-bot/blob/master/docs/gerencia/PLAN_MAESTRO_EJECUCION_2026-10-22.md",
                "office": "https://claude.ai/artifact/CJjo7mMyMEdyvTKbLc3wJc",
            },
        }
    }


def build(out=DEFAULT_OUT, root=ROOT, public=False):
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / "dashboard/index.html", out / "index.html")
    snapshot = assemble(root)
    if public:
        # GitHub Pages es público. Nunca enlazar ni copiar recursos de la Oficina privada.
        snapshot["governance"]["links"].pop("office", None)
        snapshot["meta"]["publication"] = "PUBLIC_GITHUB_PAGES"
        for member in snapshot["agents"]["nodes"]:
            member["description"] = ""  # Las instrucciones internas no son telemetría pública.
    (out / "data.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("status", "build", "serve"))
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--public", action="store_true", help="Genera un snapshot seguro para GitHub Pages (sin enlaces privados)")
    args = p.parse_args()
    if args.command == "status":
        d = assemble()
        k = d["kt002"]
        print(f"KT-002: {k['pronosticos']} pronosticos, {k['evaluados']} puntuados, {k['independientes']} sin solape")
        print(f"Agentes registrados: {len(d['agents']['nodes'])}; independientes: {len(d['agents']['independent'])}")
        print(f"Snapshot UTC: {d['meta']['source_updated_utc']}. Paper only; edge no demostrado.")
        return
    out = build(args.out.resolve(), public=args.public)
    if args.command == "build":
        print(f"Centro generado: {out / 'index.html'}")
        print("Para verlo, ejecutar: python tools/centro_control.py serve")
        return
    if not (1024 <= args.port <= 65535):
        p.error("--port debe estar entre 1024 y 65535")
    import os
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(out), **kw)
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        print(f"Centro de Control: http://127.0.0.1:{args.port}")
        print("Solo local, sin autenticación, sin operaciones reales. Ctrl+C para detener.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
