#!/usr/bin/env python3
"""
Revisor de PR determinista: 0 llamadas a IA.

Compara una rama (head) contra su base y aplica reglas de un archivo JSON:
  1. Alcance: rutas prohibidas y, opcionalmente, rutas permitidas.
  2. Invariantes: patrones que DEBEN o NO DEBEN aparecer en archivos del head.
  3. Pruebas: comandos que deben terminar con codigo 0.

Uso:
  python revisor_pr.py --repo RUTA --base origin/master --head pr118 \
      --reglas reglas_kronnos.json [--salida informe.md]

Codigo de salida: 0 = PASA, 1 = NO PASA, 2 = error de uso.
Solo usa la biblioteca estandar. No modifica el repositorio revisado
(lee el head con `git show`, no hace checkout), salvo lo que hagan
los comandos de prueba, que corren en un worktree temporal.
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Resultado:
    regla: str
    ok: bool
    detalle: str = ""
    bloqueante: bool = True


@dataclass
class Informe:
    base: str
    head: str
    archivos: list[str] = field(default_factory=list)
    resultados: list[Resultado] = field(default_factory=list)

    @property
    def pasa(self) -> bool:
        return all(r.ok for r in self.resultados if r.bloqueante)

    def markdown(self) -> str:
        veredicto = "PASA" if self.pasa else "NO PASA"
        lineas = [
            f"# Revision automatica: {veredicto}",
            "",
            f"- Base: `{self.base}` - Head: `{self.head}`",
            f"- Generado: {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC} - 0 llamadas a IA",
            f"- Archivos cambiados ({len(self.archivos)}): "
            + ", ".join(f"`{a}`" for a in self.archivos),
            "",
            "| Estado | Regla | Detalle |",
            "|---|---|---|",
        ]
        for r in self.resultados:
            if r.ok:
                estado = "OK"
            else:
                estado = "FALLA" if r.bloqueante else "AVISO"
            detalle = r.detalle.replace("|", "\\|").replace("\n", " ")
            lineas.append(f"| {estado} | {r.regla} | {detalle} |")
        lineas += ["", "Este informe no aprueba el PR: integra el dueño."]
        return "\n".join(lineas) + "\n"


def git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def coincide(ruta: str, patrones: list[str]) -> str | None:
    for p in patrones:
        if fnmatch.fnmatch(ruta, p):
            return p
    return None


def revisar_alcance(archivos: list[str], reglas: dict, inf: Informe) -> None:
    prohibidas = reglas.get("rutas_prohibidas", [])
    for a in archivos:
        p = coincide(a, prohibidas)
        if p:
            inf.resultados.append(Resultado(
                "alcance: ruta prohibida", False, f"`{a}` coincide con `{p}`"))
    if not any(r.regla == "alcance: ruta prohibida" for r in inf.resultados):
        inf.resultados.append(Resultado(
            "alcance: ruta prohibida", True, "ningun archivo prohibido"))

    permitidas = reglas.get("rutas_permitidas")
    if permitidas:
        fuera = [a for a in archivos if not coincide(a, permitidas)]
        inf.resultados.append(Resultado(
            "alcance: solo rutas permitidas", not fuera,
            "fuera de alcance: " + ", ".join(f"`{a}`" for a in fuera)
            if fuera else "todo dentro del alcance"))

    maximo = reglas.get("max_archivos")
    if maximo is not None:
        inf.resultados.append(Resultado(
            "alcance: numero de archivos", len(archivos) <= maximo,
            f"{len(archivos)} cambiados, maximo {maximo}",
            bloqueante=False))


def leer_en_head(repo: Path, head: str, ruta: str) -> str | None:
    try:
        return git(repo, "show", f"{head}:{ruta}")
    except RuntimeError:
        return None


def revisar_invariantes(repo: Path, head: str, reglas: dict,
                        inf: Informe) -> None:
    for inv in reglas.get("invariantes", []):
        nombre = inv["nombre"]
        texto = leer_en_head(repo, head, inv["archivo"])
        bloq = inv.get("bloqueante", True)
        if texto is None:
            inf.resultados.append(Resultado(
                nombre, False, f"no existe `{inv['archivo']}` en el head", bloq))
            continue
        for patron in inv.get("debe_contener", []):
            ok = re.search(patron, texto, re.MULTILINE) is not None
            inf.resultados.append(Resultado(
                nombre, ok, f"debe contener /{patron}/", bloq))
        for patron in inv.get("no_debe_contener", []):
            m = re.search(patron, texto, re.MULTILINE)
            inf.resultados.append(Resultado(
                nombre, m is None,
                f"no debe contener /{patron}/"
                + (f" (encontrado: `{m.group(0)}`)" if m else ""), bloq))
        if "max_apariciones" in inv:
            patron, maximo = inv["max_apariciones"]
            n = len(re.findall(patron, texto, re.MULTILINE))
            inf.resultados.append(Resultado(
                nombre, n <= maximo,
                f"/{patron}/ aparece {n} veces, maximo {maximo}", bloq))


def revisar_envios_mt5(repo: Path, head: str, archivo_esperado: str,
                      inf: Informe) -> None:
    nombre = "MT5: una sola llamada directa a order_send en Python"
    busqueda = subprocess.run(
        ["git", "-C", str(repo), "grep", "-l", "-z", "-w", "order_send", head, "--", "*.py"],
        capture_output=True, text=True,
    )
    if busqueda.returncode not in (0, 1):
        raise RuntimeError(f"git grep: {busqueda.stderr.strip()}")
    llamadas = []
    for coincidencia in filter(None, busqueda.stdout.split("\0")):
        ruta = coincidencia.split(":", 1)[1]
        try:
            arbol = ast.parse(git(repo, "show", f"{head}:{ruta}"), filename=ruta)
        except SyntaxError as exc:
            inf.resultados.append(Resultado(nombre, False, f"{ruta}: {exc}"))
            continue
        for nodo in ast.walk(arbol):
            if not isinstance(nodo, ast.Call):
                continue
            funcion = nodo.func
            if ((isinstance(funcion, ast.Attribute) and funcion.attr == "order_send")
                    or (isinstance(funcion, ast.Name) and funcion.id == "order_send")):
                llamadas.append((ruta, nodo.lineno))
    ubicaciones = ", ".join(f"{ruta}:{linea}" for ruta, linea in llamadas)
    inf.resultados.append(Resultado(
        nombre, [ruta for ruta, _ in llamadas] == [archivo_esperado],
        ubicaciones or "no se encontraron llamadas",
    ))


def revisar_pruebas(repo: Path, head: str, reglas: dict,
                    inf: Informe, aislar: bool) -> None:
    pruebas = reglas.get("pruebas", [])
    if not pruebas:
        return
    tmp = Path(tempfile.mkdtemp(prefix="revisor_pr_"))
    arbol = tmp / "arbol"
    try:
        git(repo, "worktree", "add", "--detach", str(arbol), head)
        for prueba in pruebas:
            cwd = (arbol / prueba.get("directorio", ".")).resolve()
            if not cwd.is_relative_to(arbol.resolve()):
                inf.resultados.append(Resultado(
                    f"pruebas: {prueba['nombre']}", False, "directorio fuera del worktree"))
                continue
            comando = ["sh", "-c", prueba["comando"]]
            if aislar:
                comando = [
                    "docker", "run", "--rm", "--network=none", "--read-only",
                    "--cap-drop=ALL", "--security-opt=no-new-privileges",
                    "--pids-limit=128", "--memory=512m", "--cpus=1",
                    "--user=65534:65534", "--tmpfs=/tmp",
                    "--env=PYTHONDONTWRITEBYTECODE=1",
                    f"--mount=type=bind,src={cwd},dst=/bot,readonly", "--workdir=/bot",
                    "python:3.12-slim", *comando,
                ]
            try:
                salida_pruebas = subprocess.DEVNULL if aislar else subprocess.PIPE
                r = subprocess.run(comando, cwd=cwd, stdout=salida_pruebas,
                                   stderr=salida_pruebas, text=True,
                                   timeout=prueba.get("timeout_s", 600))
                salida = [] if aislar else (r.stdout + r.stderr).strip().splitlines()
                resumen = " / ".join(salida[-3:]) if salida else "(sin salida)"
                inf.resultados.append(Resultado(
                    f"pruebas: {prueba['nombre']}", r.returncode == 0,
                    f"codigo {r.returncode}" if aislar else f"codigo {r.returncode}: {resumen}"))
            except subprocess.TimeoutExpired:
                inf.resultados.append(Resultado(
                    f"pruebas: {prueba['nombre']}", False, "tiempo agotado"))
    finally:
        try:
            git(repo, "worktree", "remove", "--force", str(arbol))
        except RuntimeError:
            pass
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Revisor de PR sin IA")
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--reglas", required=True, type=Path)
    ap.add_argument("--salida", type=Path)
    ap.add_argument("--sin-pruebas", action="store_true",
                    help="omite los comandos de prueba")
    ap.add_argument("--aislar-pruebas", action="store_true",
                    help="ejecuta las pruebas en Docker sin red ni credenciales del host")
    a = ap.parse_args(argv)

    try:
        reglas = json.loads(a.reglas.read_text(encoding="utf-8"))
        head = git(a.repo, "rev-parse", "--verify", "--end-of-options",
                   f"{a.head}^{{commit}}").strip()
        base = git(a.repo, "rev-parse", "--verify", "--end-of-options",
                   f"{a.base}^{{commit}}").strip()
        base_comun = git(a.repo, "merge-base", base, head).strip()
        archivos = [l for l in git(a.repo, "diff", "--name-only",
                                   "--no-renames", "-z", base_comun, head,
                                   "--").split("\0") if l]
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    inf = Informe(a.base, a.head, archivos)
    revisar_alcance(archivos, reglas, inf)
    revisar_invariantes(a.repo, head, reglas, inf)
    try:
        archivo_esperado = reglas.get("archivo_envio_mt5")
        if archivo_esperado:
            revisar_envios_mt5(a.repo, head, archivo_esperado, inf)
        if inf.pasa and not a.sin_pruebas:
            revisar_pruebas(a.repo, head, reglas, inf, a.aislar_pruebas)
    except (OSError, RuntimeError) as exc:
        inf.resultados.append(Resultado("ejecución del revisor", False, str(exc)))

    texto = inf.markdown()
    if a.salida:
        a.salida.write_text(texto, encoding="utf-8")
    print(texto)
    return 0 if inf.pasa else 1


if __name__ == "__main__":
    sys.exit(main())
