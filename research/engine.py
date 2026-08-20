"""Orquestador único de un experimento: config -> data_cache -> indicadores
-> señales -> walk-forward -> métricas -> export.

Reemplaza a `main()` de "Backtest ema v4.py" como comando a correr para
generar un experimento reproducible; `main()` queda intacta y congelada
(sigue imprimiendo por consola exactamente igual que antes de esta
migración) -- no se modificó ni se modifica acá.

Cómo se aplican los parámetros de config.yaml: `calcular_indicadores()` (EMA/
ATR) y la referencia de R:R/SL usada dentro de `correr_fold()` leen las
constantes de módulo de "Backtest ema v4.py" (EMA_FAST, ATR_PERIOD,
RR_RATIO, SL_ATR_MULT, ...), no un parámetro explícito -- parametrizarlas
está fuera del alcance ya aprobado para Fase 1 (tareas 2-5 solo cubrieron
backtest()/generar_senales*()/correr_fold() para el filtro de sesión y R:R
por fold). Para que config.yaml sea efectivo sin tocar esas firmas, este
módulo fija esas constantes UNA vez al principio de `run()`, antes de
cualquier fold -- mutación de módulo secuencial y de una sola vez por
corrida, no por fold, así que no reintroduce el riesgo que las tareas 2-4
eliminaron (ese era un `global` mutado y restaurado repetidamente DENTRO
del sweep por fold).

Nota conocida, no corregida acá (fuera de alcance): `elegir_mejor_rr` tiene
`default_rr=RR_RATIO` como default de argumento, evaluado una sola vez al
importar "Backtest ema v4.py" -- ese valor de último recurso queda fijo en
2.0 (el literal del archivo) sin importar `cfg["rr_ratio"]`. Solo importa
cuando NINGUNA combinación del barrido de R:R pasa el piso de trades; no
afecta la selección de R:R en el caso normal.
"""

import contextlib
import io
import sys

import pandas as pd

from research import config, data_cache, export, metrics
from research._engine_loader import cargar_engine


class _Tee(io.TextIOBase):
    """Escribe a la consola real y a un buffer en memoria al mismo tiempo,
    para que log.txt tenga la misma salida que ve el usuario en pantalla."""

    def __init__(self, *destinos):
        self._destinos = destinos

    def write(self, s):
        for d in self._destinos:
            d.write(s)
        return len(s)

    def flush(self):
        for d in self._destinos:
            d.flush()


def _resolver_estrategia(eng, nombre):
    mapa = {
        "baseline": eng.generar_senales,
        "mtf": eng.generar_senales_mtf,
        "estructura": eng.generar_senales_estructura,
        "retest": eng.generar_senales_retest,
    }
    return mapa[nombre]


def _aplicar_config_a_globals(eng, cfg):
    """Fija las constantes de módulo del motor según config.yaml -- ver
    docstring del módulo para por qué esto es seguro (una sola vez por
    corrida, antes de cualquier fold)."""
    eng.EMA_FAST = cfg["ema_fast"]
    eng.EMA_SLOW = cfg["ema_slow"]
    eng.EMA_TREND = cfg["ema_trend"]
    eng.ATR_PERIOD = cfg["atr_period"]
    eng.SL_ATR_MULT = cfg["sl_atr_mult"]
    eng.RR_RATIO = cfg["rr_ratio"]
    eng.USE_SESSION_FILTER = cfg["use_session_filter"]
    eng.SPREAD_PUNTOS = cfg["spread_puntos"]


def _construir_df_base(eng, cfg, df_m15, data_hashes, base_data_dir):
    estrategia = cfg["strategy"]

    if estrategia == "mtf":
        date_from_htf = df_m15["time"].min() - pd.Timedelta(days=eng.BUFFER_DIAS_HTF)
        date_to_htf = df_m15["time"].max() + pd.Timedelta(hours=1)
        df_h1, hash_h1, _ = data_cache.get_or_fetch(
            cfg["symbol"], "H1", date_from_htf, date_to_htf, cache_dir=base_data_dir)
        data_hashes["H1"] = hash_h1
        df_h1_tendencia = eng.calcular_tendencia_h1(df_h1)
        return eng.alinear_h1_a_m15(df_m15, df_h1_tendencia)

    if estrategia == "estructura":
        return eng.calcular_estructura_swings(df_m15)

    # baseline y retest: retest hace su propia detección de swings adentro
    # de generar_senales_retest, por fold, self-contained (ver su docstring).
    return df_m15


def _agregar_trades(resultados_folds):
    partes = [r["trades_test_df"] for r in resultados_folds if not r["trades_test_df"].empty]
    if not partes:
        return pd.DataFrame(columns=["tipo", "entrada", "sl", "tp", "time_entrada", "resultado_R", "salida", "time_salida"])
    return pd.concat(partes, ignore_index=True)


def run(config_path, base_experiments_dir=None, base_data_dir=None):
    """Corre un experimento completo a partir de un config.yaml y deja una
    carpeta `experiment_<fecha>_<NNN>/` en `experiments/` (o en
    `base_experiments_dir` si se pasa). Devuelve el Path de esa carpeta."""
    cfg = config.load(config_path)
    eng = cargar_engine()
    _aplicar_config_a_globals(eng, cfg)
    fn_generar_senales = _resolver_estrategia(eng, cfg["strategy"])

    log_buffer = io.StringIO()
    tee = _Tee(sys.stdout, log_buffer)

    with contextlib.redirect_stdout(tee):
        df_m15, hash_m15, _ = data_cache.get_or_fetch(
            cfg["symbol"], cfg["timeframe"], cfg["date_from"], cfg["date_to"], cache_dir=base_data_dir)
        df_m15 = eng.calcular_indicadores(df_m15)
        data_hashes = {cfg["timeframe"]: hash_m15}

        df_base = _construir_df_base(eng, cfg, df_m15, data_hashes, base_data_dir)

        folds = eng.construir_bloques_walk_forward(df_base, cfg["n_folds"])
        resultados_folds = [
            eng.correr_fold(train_raw, test_raw, i, cfg["n_folds"], fn_generar_senales=fn_generar_senales)
            for i, (train_raw, test_raw) in enumerate(folds, start=1)
        ]
        eng.resumen_walk_forward(resultados_folds)

        trades_agregado = _agregar_trades(resultados_folds)
        metricas = metrics.calcular_todas(trades_agregado)

    return export.escribir_experimento(
        cfg, trades_agregado, metricas, data_hashes,
        log_text=log_buffer.getvalue(), resultados_folds=resultados_folds,
        base_dir=base_experiments_dir,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Corre un experimento de research reproducible.")
    parser.add_argument("--config", required=True, help="Ruta a config.yaml")
    args = parser.parse_args()
    carpeta = run(args.config)
    print(f"\nExperimento exportado a: {carpeta}")
