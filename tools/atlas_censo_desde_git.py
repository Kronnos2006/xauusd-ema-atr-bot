"""Construye el censo de intentos ATLAS a partir del historial Git (Bloqueo A.1).

Determinista: dos ejecuciones sobre el mismo commit producen bytes idénticos.
Reglas de inclusión fijas y públicas (ver REGLAS). Cada intento usa como
`ejecutado_utc` la fecha del primer commit que introdujo el artefacto: GitHub
registra ese commit, así que la fecha no la elige quien construye el censo.

Alcance honesto: el N resultante es una COTA INFERIOR de los intentos de este
repositorio. No cubre corridas del Strategy Tester no versionadas, pruebas en
chats ni otros repositorios. La exhaustividad sigue requiriendo conciliación
con un inventario independiente (control A.2/A.5).

Uso:  python tools/atlas_censo_desde_git.py [--salida research/atlas/censo]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from atlas.censo_variantes import CERO, construir_evento  # noqa: E402

# (categoria, regex sobre la ruta versionada)
REGLAS = [
    ("script", r"^(hipotesis_|diagnostico_frecuencia_|diagnostico_cointegracion|"
               r"backtest|auditoria_|event_study_|calibracion_|correlacion_|mde_|"
               r"depth_check_|analizar_|triage_|metricas_)[^/]*\.py$"),
    ("script", r"^Backtest ema v\d+\.py$"),
    ("script", r"^investigacion/fase\d+/(h\d+_|analisis_|triage_)[^/]*\.py$"),
    ("ea", r"^(MQL5/Experts/|estrategias/)[^/]*\.mq5$"),
    ("nota", r"^XAUUSD EMA/ATR/(EMA baseline|MTF - filtro|H1 retuneado|Ruptura y retest|"
             r"Estructura de swings|Macro .* - fase 1|Ratio oro-plata - fase 1|"
             r"Risk-off .* - fase 1|TF_Basket_H1 — Fase 0|KT-00\d)[^/]*\.md$"),
]
REGISTRO_0031 = "estrategias/outputs/estrategias_registro.md"
TESIS = "research/atlas/registro/tesis.jsonl"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *args], check=True,
                          capture_output=True, text=True).stdout


def utc(iso: str) -> str:
    return datetime.fromisoformat(iso.strip()).astimezone(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def alta(ruta: str) -> tuple[str, str]:
    """(fecha UTC, commit) del primer commit que añadió la ruta."""
    out = git("log", "--diff-filter=A", "--format=%cI %H", "--", ruta).split("\n")
    lineas = [x for x in out if x.strip()]
    if not lineas:
        raise RuntimeError(f"sin commit de alta para {ruta}")
    fecha, commit = lineas[-1].split()
    return utc(fecha), commit


def preregistro_de(ruta: str, notas: list[str]) -> str:
    stem = Path(ruta).stem.lower()
    for clave in re.findall(r"(dfii10|2s10s|dxy_h4|dxy|oro_plata|us500_h4_eurusd|"
                            r"us500_h4|tf_basket)", stem):
        for n in notas:
            m = n.lower().replace(" ", "_").replace("-", "_")
            if clave.replace("_", "") in m.replace("_", ""):
                return n
    return "NO_PREREGISTRADO"


def inventario() -> list[dict]:
    rutas = git("ls-files").splitlines()
    notas = [r for r in rutas if re.match(REGLAS[-1][1], r)]
    filas = []
    for ruta in rutas:
        for cat, rx in REGLAS:
            if re.match(rx, ruta):
                fecha, commit = alta(ruta)
                filas.append({"intento_id": f"{cat}:{ruta}", "variante_id": Path(ruta).stem,
                              "preregistro": ruta if cat == "nota" else preregistro_de(ruta, notas),
                              "ejecutado_utc": fecha, "commit": commit})
                break
    # Corridas del Strategy Tester documentadas en el registro 0031 (una por fila).
    fecha, commit = alta(REGISTRO_0031)
    for linea in (RAIZ / REGISTRO_0031).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (Judas|Venom|Bernd|LonClose|SilverBullet|CRT[^|]*) \| \d+", linea)
        if m:
            nombre = m.group(1).strip()
            filas.append({"intento_id": f"run0031:{nombre}", "variante_id": f"0031:{nombre}",
                          "preregistro": REGISTRO_0031, "ejecutado_utc": fecha, "commit": commit})
    # Tesis ATLAS ya encadenadas.
    fecha, commit = alta(TESIS)
    for linea in (RAIZ / TESIS).read_text(encoding="utf-8").splitlines():
        ev = json.loads(linea)
        t = ev["tesis"]
        # Una tesis re-evaluada con el mismo id cuenta como intento aparte.
        filas.append({"intento_id": f"tesis:{t['id']}#{ev['hash'][:12]}", "variante_id": t["id"],
                      "preregistro": TESIS, "ejecutado_utc": fecha, "commit": commit})
    filas.sort(key=lambda f: (f["ejecutado_utc"], f["intento_id"]))
    return filas


def construir(salida: Path) -> dict:
    filas = inventario()
    salida.mkdir(parents=True, exist_ok=True)
    prev, lineas, fuentes = CERO, [], []
    for f in filas:
        ev = construir_evento(prev, f["intento_id"], f["variante_id"],
                              f["preregistro"], f["ejecutado_utc"])
        lineas.append(json.dumps(ev, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
        fuentes.append({"intento_id": f["intento_id"], "commit_alta": f["commit"]})
        prev = ev["hash"]
    censo = ("\n".join(lineas) + "\n").encode("utf-8")
    (salida / "censo_intentos.jsonl").write_bytes(censo)
    (salida / "fuentes_git.json").write_text(
        json.dumps(fuentes, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    corte = max(f["ejecutado_utc"] for f in filas)
    ancla = {"sha256": hashlib.sha256(censo).hexdigest(), "lineas": len(lineas),
             "ultimo_hash": prev, "corte_utc": corte,
             "alcance": "cota inferior, solo artefactos versionados en este repo",
             "custodia": "PENDIENTE: sello RFC 3161 por workflow atlas-custodia"}
    (salida / "ANCLA_CENSO.json").write_text(
        json.dumps(ancla, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return ancla


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--salida", default="research/atlas/censo")
    print(json.dumps(construir(RAIZ / p.parse_args().salida), indent=1, ensure_ascii=False))
