"""Carga y valida un config.yaml de experimento -> dict explícito de
parámetros que el resto de `research/` recibe por parámetro (reemplaza la
dependencia de leer las constantes de módulo de "Backtest ema v4.py" como
fuente de verdad en tiempo de ejecución del runner; esas constantes siguen
existiendo como default para quien importe el motor fuera de `research/`).

No expone (todavía) los parámetros hoy fijos "sin barrido" en el motor
(SWING_L, SWING_R, RETEST_VENTANA, RETEST_MARGEN_ATR_MULT) -- decisión
explícita para no agregar un schema más grande de lo que Fase 1 necesita;
se pueden sumar después sin romper nada.
"""

from datetime import date, datetime

import yaml

CLAVES_REQUERIDAS = [
    "symbol", "timeframe", "date_from", "date_to",
    "ema_fast", "ema_slow", "ema_trend", "atr_period",
    "sl_atr_mult", "rr_ratio", "spread_puntos",
    "use_session_filter", "n_folds", "strategy",
]

ESTRATEGIAS_VALIDAS = {"baseline", "mtf", "estructura", "retest"}
TIMEFRAMES_VALIDOS = {"M15", "H1"}


class ConfigError(Exception):
    """Config de experimento inválida o incompleta."""


def _a_fecha(valor, nombre_clave):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        try:
            return date.fromisoformat(valor)
        except ValueError as exc:
            raise ConfigError(
                f"'{nombre_clave}' debe ser una fecha ISO (YYYY-MM-DD), recibido: {valor!r}"
            ) from exc
    raise ConfigError(f"'{nombre_clave}' debe ser fecha o string ISO, recibido: {type(valor)}")


def load(path):
    """Carga `path` (config.yaml) y devuelve un dict validado y normalizado.

    Lanza ConfigError con un mensaje explícito si falta alguna clave
    requerida o si algún valor no tiene el tipo/rango esperado -- nunca un
    KeyError/TypeError genérico.
    """
    with open(path, "r", encoding="utf-8") as f:
        crudo = yaml.safe_load(f) or {}

    if not isinstance(crudo, dict):
        raise ConfigError(f"{path} no contiene un mapeo YAML válido en la raíz")

    faltantes = [k for k in CLAVES_REQUERIDAS if k not in crudo]
    if faltantes:
        raise ConfigError(f"Faltan claves requeridas en {path}: {', '.join(faltantes)}")

    cfg = dict(crudo)

    if cfg["timeframe"] not in TIMEFRAMES_VALIDOS:
        raise ConfigError(f"timeframe inválido: {cfg['timeframe']!r} (válidos: {sorted(TIMEFRAMES_VALIDOS)})")

    if cfg["strategy"] not in ESTRATEGIAS_VALIDAS:
        raise ConfigError(f"strategy inválida: {cfg['strategy']!r} (válidas: {sorted(ESTRATEGIAS_VALIDAS)})")

    cfg["date_from"] = _a_fecha(cfg["date_from"], "date_from")
    cfg["date_to"] = _a_fecha(cfg["date_to"], "date_to")
    if cfg["date_from"] >= cfg["date_to"]:
        raise ConfigError(f"date_from ({cfg['date_from']}) debe ser anterior a date_to ({cfg['date_to']})")

    if not isinstance(cfg["n_folds"], int) or cfg["n_folds"] < 1:
        raise ConfigError(f"n_folds debe ser un entero >= 1, recibido: {cfg['n_folds']!r}")

    if not isinstance(cfg["use_session_filter"], bool):
        raise ConfigError(f"use_session_filter debe ser bool, recibido: {cfg['use_session_filter']!r}")

    for clave in ("ema_fast", "ema_slow", "ema_trend", "atr_period"):
        if not isinstance(cfg[clave], int) or cfg[clave] < 1:
            raise ConfigError(f"{clave} debe ser un entero >= 1, recibido: {cfg[clave]!r}")

    for clave in ("sl_atr_mult", "rr_ratio"):
        if not isinstance(cfg[clave], (int, float)) or cfg[clave] <= 0:
            raise ConfigError(f"{clave} debe ser numérico > 0, recibido: {cfg[clave]!r}")

    if not isinstance(cfg["spread_puntos"], (int, float)) or cfg["spread_puntos"] < 0:
        raise ConfigError(f"spread_puntos debe ser numérico >= 0, recibido: {cfg['spread_puntos']!r}")

    return cfg
