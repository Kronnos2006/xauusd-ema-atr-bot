#!/usr/bin/env python3
"""Informe de Fase 4 desde el resumen KT-002; descriptivo y estrictamente read-only.

No recalcula pronósticos ni cambia muestras. Jamás interpreta p de filas solapadas
como prueba de ventaja. El origen científico sigue siendo el registro predeclarado.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

LABELS = (("siempre_sube", "Siempre sube"), ("kronos", "Kronos"),
          ("timesfm", "TimesFM"), ("kt001", "KT-001 (50/50)"))


def render(snapshot):
    issues = []
    if snapshot.get("variant") != "KT-002":
        issues.append("Variante inesperada")
    if snapshot.get("profitability_evaluated") is not False:
        issues.append("No consta profitability_evaluated=false")
    updated = snapshot.get("updated_utc", "NO VERIFICADO")
    try:
        datetime.fromisoformat(updated.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        issues.append("updated_utc inválida")
    all_obs = snapshot.get("todos_solapados", {})
    independent = snapshot.get("sin_solape", {})
    n_overlap = all_obs.get("n_vencidos")
    n_ind = independent.get("n_vencidos")
    if not isinstance(n_overlap, int) or not isinstance(n_ind, int) or n_ind > n_overlap:
        issues.append("Tamaños de muestras inconsistentes")
    lines = [
        "# KT-002 — Observatorio descriptivo de Fase 4",
        "",
        f"Fuente: `data/kt002/resumen.json` · actualizado UTC: {updated}.",
        "",
        "**Alcance:** acierto direccional, no backtest, no órdenes, no rentabilidad.",
        f"Pronósticos: {snapshot.get('pronosticos', '?')}; evaluados: {snapshot.get('vencidos', '?')}; "
        f"solapados n={n_overlap}; subconjunto sin solape n={n_ind}; "
        f"horas omitidas acumuladas: {snapshot.get('horas_omitidas', '?')}.",
        "",
        "## Subconjunto principal sin solape (según preregistro)",
        "",
        "| Método | Aciertos/n | Tasa | IC Wilson 95 % | McNemar exacto vs. siempre sube |",
        "|---|---:|---:|---:|---:|",
    ]
    for key, label in LABELS:
        d = independent.get(key, {})
        n = d.get("n")
        wins = d.get("aciertos")
        if not isinstance(n, int) or not isinstance(wins, int) or n < 0 or wins < 0 or wins > n or n != n_ind:
            issues.append(f"Conteos inválidos en {key}")
        ci = d.get("ic95", [])
        if not isinstance(ci, list) or len(ci) != 2 or any(not isinstance(x, (float,int)) or x < 0 or x > 1 for x in ci):
            issues.append(f"IC95 inválido en {key}")
            ic = "NO VERIFICADO"
        else:
            ic = f"{ci[0]:.1%}–{ci[1]:.1%}"
        rate = d.get("tasa")
        if not isinstance(rate, (float,int)) or rate < 0 or rate > 1 or (isinstance(n,int) and n > 0 and isinstance(wins,int) and abs(rate - wins/n) > .001):
            issues.append(f"Tasa inconsistente en {key}")
        p = d.get("mcnemar_vs_sube", {}).get("p") if key != "siempre_sube" else None
        if p is not None and (not isinstance(p,(float,int)) or p < 0 or p > 1):
            issues.append(f"p inválida en {key}")
        lines.append(f"| {label} | {wins}/{n} | {rate:.1%} | {ic} | {p if p is not None else 'Referencia'} |"
                     if isinstance(rate,(float,int)) else f"| {label} | {wins}/{n} | NO VERIFICADO | {ic} | — |")
    lines.extend([
        "",
        "## Interpretación y límites",
        "",
        "- Este subconjunto sin solape es el **principal** predeclarado; aun así puede persistir dependencia temporal por régimen.",
        "- Las observaciones solapadas se presentan como contexto y **no** como evidencia independiente de significación.",
        "- Los intervalos con n pequeño son anchos; no elegir el modelo por un resultado provisional.",
        "- No hay rentabilidad ni costos de transacción evaluados. No hay prueba de edge.",
        "- Los números provienen del resumen publicado; esta herramienta no certifica que el CSV o el modelo sean auténticos.",
        "- Se necesitan nuevas observaciones prospectivas sin cambiar los parámetros ni las reglas registradas.",
        "",
        f"**Control del documento:** {'REVISAR: ' + '; '.join(issues) if issues else 'CONSISTENTE EN ESTRUCTURA (no dictamen del auditor)'}",
        "",
    ])
    return "\n".join(lines), issues


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--summary", default="data/kt002/resumen.json")
    args = p.parse_args()
    snapshot = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    report, problems = render(snapshot)
    print(report)
    raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    main()
