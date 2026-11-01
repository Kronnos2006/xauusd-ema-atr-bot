#!/usr/bin/env python3
"""Compute verified plan progress from issue #88 checkboxes, without an LLM."""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

REPO = "Kronnos2006/xauusd-ema-atr-bot"
ISSUE = 88
CHECKBOX = re.compile(r"^\\s*- \\[([ xX])\\] ", re.MULTILINE)
PHASE = re.compile(r"^### (Fase \\d+[^\\n]*)", re.MULTILINE)


def parse_progress(body):
    """Reject missing or changed 32-item baseline instead of displaying a false percentage."""
    sections = list(PHASE.finditer(body))
    if len(sections) != 8:
        raise ValueError(f"Expected 8 phases; found {len(sections)}")
    parsed = []
    for i, phase in enumerate(sections):
        part = body[phase.end():sections[i + 1].start() if i + 1 < len(sections) else len(body)]
        # Stop at next non-phase heading, so references don't count.
        part = re.split(r"^## ", part, maxsplit=1, flags=re.MULTILINE)[0]
        checks = CHECKBOX.findall(part)
        if len(checks) != 4:
            raise ValueError(f"{phase.group(1)} has {len(checks)} milestones, expected 4")
        parsed.append((phase.group(1), sum(c.lower() == "x" for c in checks), 4))
    return parsed


def render(phases, issue_url):
    done = sum(p[1] for p in phases)
    total = sum(p[2] for p in phases)
    percent = done * 100 / total
    lines = [
        "# KRONNOS — avance verificado del plan de cierre",
        "",
        f"## {percent:.1f}% — {done}/{total} hitos acreditados",
        "",
        "> Este indicador mide hitos marcados en el plan de cierre, no el desarrollo histórico,",
        "> la calidad del sistema ni una rentabilidad demostrada. Cada hito necesita PR, SHA y CI.",
        "",
        "| Fase | Hitos | Avance |",
        "|---|---:|---:|",
    ]
    for title, completed, count in phases:
        lines.append(f"| {title} | {completed}/{count} | {completed * 100/count:.0f}% |")
    lines += ["", f"[Revisar y actualizar tareas del plan]({issue_url})", "",
              "Fuente: casillas de GitHub Issue #88; no hay estimaciones ni IA en el cálculo.",
              "Si la fuente no está disponible o cambia la estructura, la actualización falla sin alterar el reporte.",
              ""]
    return "\\n".join(lines)


def main():
    token = os.getenv("GH_TOKEN")
    if not token:
        raise RuntimeError("GH_TOKEN missing: cannot verify project progress")
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/issues/{ISSUE}", headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "User-Agent": "kronnos-progress-bot",
    })
    with urllib.request.urlopen(req, timeout=20) as response:
        issue = json.load(response)
    phases = parse_progress(issue["body"])
    result = render(phases, issue["html_url"])
    target = Path("docs/gerencia/PROGRESO.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(result, encoding="utf-8")
    print(f"Progreso verificado: {sum(x[1] for x in phases)}/32")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("NO VERIFICADO: " + str(exc), file=sys.stderr)
        sys.exit(1)
