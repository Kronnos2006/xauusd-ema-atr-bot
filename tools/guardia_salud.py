"""Lógica de salud de la guardia (ORION, 2026-10-23).

Funciones puras (sin red) para decidir qué hacer con KT-002 y si los datos de
mercado están frescos. La guardia (.github/workflows/guardia.yml) y el vigía las
usan; las pruebas están en tests/test_guardia_salud.py.

Regla absoluta: ninguna función devuelve nunca la acción "cancelar". Una corrida
viva solo se escala (alerta); jamás se cancela de forma automática.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

VIVOS = {"queued", "in_progress", "waiting", "pending", "requested"}
FALLIDOS = {"failure", "timed_out", "startup_failure"}
ACCIONES = {"ok", "relanzar", "alerta"}  # "cancelar" no existe a propósito

# Umbrales (minutos)
REGISTRO_SANO = 130      # KT-002 escribe cada hora; >130 min sin registro con una corrida viva = falla silenciosa
COLA_LARGA = 120         # en cola sin arrancar más de 2 h
SOLAPE = 240             # encolar la siguiente corrida si la última se creó hace >4 h
PARADO = 75              # sin corridas vivas y sin registro hace >75 min = parado


def _t(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def _r(x: float):
    return "∞" if x == float("inf") else round(x)


def minutos(desde: str, ahora: dt.datetime) -> float:
    return (ahora - _t(desde)).total_seconds() / 60


def decidir_kt002(corridas: list[dict], ultimo_registro: str | None, ahora: dt.datetime) -> dict:
    """corridas: de la más nueva a la más vieja, con status, conclusion, createdAt, databaseId."""
    edad_reg = minutos(ultimo_registro, ahora) if ultimo_registro else float("inf")
    vivas = [c for c in corridas if c.get("status") in VIVOS]
    en_curso = [c for c in vivas if c.get("status") == "in_progress"]
    en_cola = [c for c in vivas if c.get("status") != "in_progress"]
    ult = corridas[0] if corridas else None
    r = {"accion": "ok", "motivo": "", "edad_registro_min": None if edad_reg == float("inf") else round(edad_reg),
         "vivas": len(vivas), "en_curso": len(en_curso), "en_cola": len(en_cola)}

    if en_curso:
        if edad_reg > REGISTRO_SANO:
            r.update(accion="alerta", motivo=f"corrida viva sin registro hace {_r(edad_reg)} min: escalar al gerente, NO cancelar")
        elif not en_cola and ult and minutos(ult["createdAt"], ahora) > SOLAPE:
            r.update(accion="relanzar", motivo="solape 4 h: encolar la siguiente (espera en el grupo kt002)")
        return r
    if en_cola:
        viejo = max(minutos(c["createdAt"], ahora) for c in en_cola)
        if viejo > COLA_LARGA:
            r.update(accion="alerta", motivo=f"corrida en cola hace {round(viejo)} min sin arrancar")
        return r
    # Nada vivo
    if ult and ult.get("conclusion") in FALLIDOS:
        r.update(accion="relanzar", motivo=f"última corrida {ult.get('databaseId')} terminó en {ult.get('conclusion')}")
    elif edad_reg > PARADO:
        r.update(accion="relanzar", motivo=f"sin corridas vivas y sin registro hace {_r(edad_reg)} min")
    return r


def frescura(archivos: dict[str, str | None], limites_min: dict[str, float], ahora: dt.datetime) -> list[str]:
    """archivos: nombre -> fecha ISO del dato (o None si falta). Devuelve problemas (vacío = sano)."""
    problemas = []
    for nombre, limite in limites_min.items():
        f = archivos.get(nombre)
        if not f:
            problemas.append(f"{nombre}: falta")
            continue
        edad = minutos(f, ahora)
        if edad > limite:
            problemas.append(f"{nombre}: {round(edad)} min sin actualizar (límite {round(limite)})")
    return problemas


def tendencia_vieja(generado_utc: str | None, ahora: dt.datetime, horas: float = 20) -> bool:
    return generado_utc is None or minutos(generado_utc, ahora) > horas * 60


DEDUPE_MIN = 40
# Límites de frescura medidos sobre lo publicado en GitHub. El spread usa 50 min (DEDUPE_MIN + margen para los
# reintentos de publicación y verificación) para que una corrida saltada no se marque vieja por diseño.
LIMITES_MIN = {"tendencia.json": 26 * 60, "spread_btcusdt.csv": 50, "registro KT-002": REGISTRO_SANO}


def saltar_duplicada(ultimo_spread_publicado: str | None, origen: str, ahora: dt.datetime) -> bool:
    """Solo se salta la medición de spread (nunca la verificación de salud). Manual nunca se salta."""
    if origen == "manual" or not ultimo_spread_publicado:
        return False
    return minutos(ultimo_spread_publicado, ahora) < DEDUPE_MIN


def _filas_spread(csv_texto: str | None) -> list[str]:
    return [l for l in (csv_texto or "").splitlines() if l.strip() and not l.startswith("utc,")]


def verificar_salud(spread_csv_remoto: str | None, tendencia_remota: dict | None, registro_kt002: str | None,
                    esperado_spread_utc: str | None, esperado_tendencia: str | None,
                    pasos: dict[str, str], alerta: str | None, ahora: dt.datetime) -> list[str]:
    """Todo se mide contra lo publicado en GitHub (no contra la copia local). Vacío = sano."""
    filas = _filas_spread(spread_csv_remoto)
    ult_spread = filas[-1].split(",")[0] if filas else None
    gen = (tendencia_remota or {}).get("generado_utc")
    probs = frescura({"tendencia.json": gen, "spread_btcusdt.csv": ult_spread, "registro KT-002": registro_kt002},
                     LIMITES_MIN, ahora)
    if esperado_spread_utc and not any(f.split(",")[0] == esperado_spread_utc for f in filas):
        probs.append(f"spread de esta corrida ({esperado_spread_utc}) no aparece publicado en GitHub")
    if esperado_tendencia and gen != esperado_tendencia:
        probs.append("tendencia.json de esta corrida no aparece publicada en GitHub")
    for paso, resultado in pasos.items():
        if resultado == "failure":
            probs.append(f"paso {paso} falló")
    if alerta:
        probs.append(alerta)
    return probs


def _main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("kt002"); a.add_argument("--corridas", required=True); a.add_argument("--registro")
    b = sub.add_parser("frescura"); b.add_argument("--json", required=True)
    c = sub.add_parser("tendencia-vieja"); c.add_argument("--archivo", default="data/mercado/tendencia.json")
    d = sub.add_parser("saltar"); d.add_argument("--ultimo-spread", default=""); d.add_argument("--origen", required=True)
    e = sub.add_parser("salud"); e.add_argument("--spread-remoto", required=True); e.add_argument("--tendencia-remota", required=True)
    e.add_argument("--registro", default=""); e.add_argument("--esperado-spread", default="")
    e.add_argument("--esperado-tendencia", default=""); e.add_argument("--pasos", default="{}"); e.add_argument("--alerta", default="")
    args = p.parse_args(argv)
    ahora = dt.datetime.now(dt.timezone.utc)
    if args.cmd == "kt002":
        print(json.dumps(decidir_kt002(json.load(open(args.corridas)), args.registro or None, ahora), ensure_ascii=False))
    elif args.cmd == "frescura":
        cfg = json.load(open(args.json))
        probs = frescura(cfg["archivos"], cfg["limites_min"], ahora)
        print(json.dumps(probs, ensure_ascii=False))
        return 1 if probs else 0
    elif args.cmd == "saltar":
        print("si" if saltar_duplicada(args.ultimo_spread or None, args.origen, ahora) else "no")
    elif args.cmd == "salud":
        try:
            csv_txt = open(args.spread_remoto, encoding="utf-8").read()
        except OSError:
            csv_txt = None
        try:
            tend = json.load(open(args.tendencia_remota, encoding="utf-8"))
        except (OSError, ValueError):
            tend = None
        probs = verificar_salud(csv_txt, tend, args.registro or None, args.esperado_spread or None,
                                args.esperado_tendencia or None, json.loads(args.pasos), args.alerta or None, ahora)
        print(json.dumps(probs, ensure_ascii=False))
        return 1 if probs else 0
    else:
        try:
            g = json.load(open(args.archivo)).get("generado_utc")
        except (OSError, ValueError):
            g = None
        print("si" if tendencia_vieja(g, ahora) else "no")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
