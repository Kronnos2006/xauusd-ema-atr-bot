#!/usr/bin/env python3
"""ORION: comandos seguros con lista cerrada, no modifica archivos ni convoca agentes.

Uso: python tools/orion_comandos.py <estado|modelos|publicacion|integridad-basica>
La CI lanza solo scripts de consulta. Los resultados son verificaciones técnicas,
nunca dictámenes independientes ni una señal de trading.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIONS = {
    "estado": ("tools/centro_control.py", "status"),
    "modelos": ("tools/observatorio_kt002.py",),
    "integridad-basica": ("tools/resumen_gerente_kt002.py",),
}
FORBIDDEN = {"kt002_prospectivo.py", "kt003.py"}


def publication_check(root=ROOT):
    files = ("dashboard/index.html", "docs/visor/index.html",
             ".github/workflows/orion-pages.yml")
    missing = [x for x in files if not (root / x).is_file()]
    if missing:
        raise ValueError("Faltan fuentes de los visores: " + ", ".join(missing))
    script = (root / ".github/workflows/orion-pages.yml").read_text(encoding="utf-8")
    for expected in ('cp docs/visor/index.html', 'cmp docs/visor/index.html',
                     'actions/deploy-pages@v4'):
        if expected not in script:
            raise ValueError("Publicación conjunta incompleta: " + expected)
    return "ORION/visor: fuentes conservadas y plantilla de publicador conjunto verificada (NO prueba de despliegue remoto)."


def command_spec(action):
    if action not in ACTIONS:
        raise ValueError("Comando no permitido")
    command = ACTIONS[action]
    if not command[0].startswith("tools/") or Path(command[0]).name in FORBIDDEN:
        raise ValueError("Script no autorizado")
    return command


def execute(action, root=ROOT):
    if action == "publicacion":
        return {"accion": action, "resultado": publication_check(root), "ok": True}
    script = command_spec(action)
    if not (root / script[0]).is_file():
        raise ValueError("Script ausente: " + script[0])
    result = subprocess.run([sys.executable, *script], cwd=root,
                            capture_output=True, text=True, timeout=40, check=False)
    return {"accion": action, "ok": result.returncode == 0,
            "salida": (result.stdout or "")[-6000:],
            "errores": (result.stderr or "")[-2000:],
            "returncode": result.returncode,
            "advertencia": "Consulta local de snapshot. No equivale a una auditoría independiente."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accion", choices=(*ACTIONS, "publicacion"))
    args = parser.parse_args()
    try:
        outcome = execute(args.accion)
    except (ValueError, subprocess.TimeoutExpired, OSError) as exc:
        outcome = {"accion": args.accion, "ok": False, "errores": str(exc)}
    print(json.dumps(outcome, ensure_ascii=False, indent=2))
    raise SystemExit(0 if outcome["ok"] else 1)


if __name__ == "__main__":
    main()
