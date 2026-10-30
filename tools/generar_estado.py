#!/usr/bin/env python3
"""Actualiza la sección automática de ESTADO.md. Sin IA, solo stdlib.

Lee archivos del repo (y, si hay GH_TOKEN, el estado de corridas y PR por la
API REST de GitHub) y reescribe solo lo que está entre los marcadores
AUTO:INICIO y AUTO:FIN. Lo escrito a mano fuera de los marcadores no se toca.

Uso: python3 tools/generar_estado.py [--raiz .] [--sin-red]
"""
import argparse
import csv
import json
import os
import subprocess
import urllib.request
from datetime import datetime, timezone

INI = "<!-- AUTO:INICIO (lo escribe tools/generar_estado.py; no editar a mano) -->"
FIN = "<!-- AUTO:FIN -->"
REPO = "Kronnos2006/xauusd-ema-atr-bot"
WORKFLOWS = ["kt002.yml", "guardia.yml", "informe-gerencia-sin-ia.yml", "kronnos-ensemble.yml"]
RUTINA = ("KT-002: registro", "Mercado: datos de BTC", "Guardia")


def ahora():
    return datetime.now(timezone.utc)


def pct(x):
    return f"{x * 100:.1f} %"


def horas_desde(iso):
    try:
        t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (ahora() - t).total_seconds() / 3600
    except Exception:
        return None


def seccion_kt002(raiz):
    ruta = os.path.join(raiz, "data/kt002/resumen.json")
    if not os.path.exists(ruta):
        return ["- KT-002: NO DISPONIBLE (falta data/kt002/resumen.json)."]
    d = json.load(open(ruta, encoding="utf-8"))
    s = d.get("sin_solape", {})
    out = [f"- Pronósticos: {d.get('pronosticos')} · vencidos: {d.get('vencidos')} · "
           f"horas omitidas: {d.get('horas_omitidas')} · actualizado: {d.get('updated_utc', '')[:16]} UTC"]
    ultimo = None
    pred = os.path.join(raiz, "data/kt002/predicciones.csv")
    if os.path.exists(pred):
        with open(pred, encoding="utf-8") as f:
            for fila in csv.DictReader(f):
                ultimo = fila.get("run_utc") or ultimo
    if ultimo:
        h = horas_desde(ultimo)
        alerta = " **ALERTA: más de 3 h sin registro**" if h is not None and h > 3 else ""
        out.append(f"- Último registro: {ultimo[:16]} UTC (hace {h:.1f} h){alerta}")
    out.append(f"- **Sin solape (lo que cuenta), n = {s.get('n_vencidos')}:**")
    ref = s.get("siempre_sube", {})
    out.append(f"  - Siempre sube (referencia): {ref.get('aciertos')}/{ref.get('n')} = {pct(ref.get('tasa', 0))}")
    for k, nombre in (("kronos", "Kronos"), ("timesfm", "TimesFM"), ("kt001", "KT-001 50/50")):
        m = s.get(k, {})
        if not m:
            continue
        p = m.get("mcnemar_vs_sube", {}).get("p")
        ic = m.get("ic95", [0, 0])
        out.append(f"  - {nombre}: {m.get('aciertos')}/{m.get('n')} = {pct(m.get('tasa', 0))} "
                   f"(IC95 {pct(ic[0])}–{pct(ic[1])}; p vs sube = {p})")
    gana = [k for k in ("kronos", "timesfm", "kt001")
            if s.get(k, {}).get("mcnemar_vs_sube", {}).get("p", 1) < 0.05]
    out.append("- Veredicto automático: " + (
        "algún modelo difiere de «siempre sube» con p < 0,05 (revisar antes de creer: es descriptivo)."
        if gana else "ningún modelo supera a «siempre sube». Sin ventaja demostrada."))
    return out


def gh(ruta):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/{ruta}", headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception:
        return None


def seccion_github(sin_red):
    if sin_red:
        return ["- (sin consulta a GitHub en esta corrida)"]
    out = []
    for wf in WORKFLOWS:
        d = gh(f"actions/workflows/{wf}/runs?per_page=10")
        if not d:
            out.append(f"- {wf}: NO DISPONIBLE")
            continue
        runs = d.get("workflow_runs", [])
        hechas = [r for r in runs if r.get("status") == "completed"]
        verdes = sum(r.get("conclusion") == "success" for r in hechas)
        ult = hechas[0] if hechas else None
        txt = f"última {ult.get('conclusion')} {ult.get('created_at', '')[:16]}" if ult else "sin corridas terminadas"
        out.append(f"- {wf}: {verdes}/{len(hechas)} verdes en las últimas 10 · {txt}")
    prs = gh("pulls?state=open&per_page=20")
    if prs is not None:
        out.append("- PR abiertos: " + (", ".join(
            f"#{p['number']}{' (borrador)' if p.get('draft') else ''} {p['title'][:60]}" for p in prs) or "ninguno"))
    iss = gh("issues?labels=guardia&state=open")
    if iss is not None:
        out.append(f"- Avisos «guardia» abiertos: {len(iss)}")
    return out


def seccion_commits(raiz):
    try:
        log = subprocess.run(["git", "-C", raiz, "log", "-60", "--format=%ad|%an|%s", "--date=short"],
                             capture_output=True, text=True, check=True).stdout.splitlines()
    except Exception:
        return ["- NO DISPONIBLE (sin historial git)"]
    utiles = [l for l in log if not any(l.split("|", 2)[-1].startswith(r) for r in RUTINA)][:8]
    return [f"- {l.split('|')[0]} · {l.split('|')[1]} · {l.split('|', 2)[2][:90]}" for l in utiles] or ["- (solo commits de rutina)"]


def generar(raiz, sin_red):
    lineas = [INI, f"_Generado {ahora():%Y-%m-%d %H:%M} UTC · 0 llamadas a IA_", "",
              "### KT-002 (BTC, dirección a 4 h, prospectivo)"] + seccion_kt002(raiz)
    lineas += ["", "### GitHub Actions y PR"] + seccion_github(sin_red)
    lineas += ["", "### Últimos cambios no rutinarios"] + seccion_commits(raiz) + [FIN]
    return "\n".join(lineas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--sin-red", action="store_true")
    a = ap.parse_args()
    ruta = os.path.join(a.raiz, "ESTADO.md")
    texto = open(ruta, encoding="utf-8").read()
    if INI not in texto or FIN not in texto:
        raise SystemExit("ESTADO.md no tiene los marcadores AUTO:INICIO / AUTO:FIN")
    antes, resto = texto.split(INI, 1)
    _, despues = resto.split(FIN, 1)
    open(ruta, "w", encoding="utf-8").write(antes + generar(a.raiz, a.sin_red) + despues)
    print("ESTADO.md actualizado")


if __name__ == "__main__":
    main()
