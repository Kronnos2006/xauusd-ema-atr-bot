"""
Event study NFP + CPI m/m (US) -> EURUSD, ventanas +1h/+4h/+24h.
=============================================================================
Primera hipotesis del marco "EURUSD Event Study -- sorpresa macro"
(abierto 2026-08-05, ver CLAUDE.md y Bitacora de decisiones.md).

Ficha (hypothesis-gate Fase 1, aprobada 2026-08-05 con efecto tomado de
Andersen et al. 2003, "Micro Effects of Macro Announcements"):

  Hipotesis falsable: SI sign(surprise) de NFP o CPI m/m (actual-forecast)
  es positivo, ENTONCES el retorno signado
  (sign(surprise) x retorno_EURUSD) en las ventanas +1h/+4h/+24h
  post-release es en promedio >= +8 pips (0.07%, el efecto MAS DEBIL de
  los dos citados por Andersen et al. -- CPI, usado como piso conservador
  para el diseno pooled), distinto de cero con significancia estadistica.

  Variable independiente: surprise = (actual-forecast), ya en unidades
  reales (el extractor MQL5 ya divide por 10^6 -- ver EventStudyExtractor.mq5).
  direction = sign(surprise).

  Variable dependiente: signed_return = direction x retorno_EURUSD,
  retorno = close(ultima_vela_H1 con open <= t_evento+ventana) /
            close(ultima_vela_H1 con open <= t_evento-1h) - 1,
  UN SOLO t-test pooled (ambas direcciones juntas via el signo), no dos
  grupos separados -- decidido explicitamente el 2026-08-05 porque es el
  unico de los dos disenos con margen de potencia suficiente para el
  efecto citado (MDE=6.4 pips a n=58 pooled vs MDE=9.0 pips a n=29/grupo).

  REDEFINICION 2026-08-05 (post debug de datos, con el usuario): el diseno
  original pedia M1 con pre-ventana de 15min exactos. El servidor
  MetaQuotes-Demo conectado NO retiene M1 mas alla de ~3 meses hacia atras
  (M5 ~1 anio, M15 ~4 anios -- ninguno cubre 2018-2025 completo). Unico
  timeframe con cobertura 2018-2025 confirmada: H1. Se pasa TODO el diseno
  a H1, con dos ajustes deliberados, NO cosmeticos:
  - Pre-precio: NO se usa el cierre de la vela H1 que CONTIENE el evento
    (esa vela cierra despues del release -- seria look-ahead, mezclaria
    el "antes" con el propio movimiento post-noticia). Se usa el cierre
    de la vela H1 INMEDIATAMENTE ANTERIOR (target = t_evento - 1h para el
    asof) -- en la practica cae entre 30 y 90 minutos antes del release
    segun el minuto exacto de publicacion, no 15min limpios.
  - Post-precio: cierre de la vela H1 vigente en t_evento+ventana -- puede
    sobrepasar el target hasta 59min (ej. "+1h" puede en realidad reflejar
    hasta ~1h59min post-release).
  - Efecto secundario en la potencia: SIGMA_RETORNO_1H_PCT (0.16%, de la
    literatura, medido con ventanas limpias tipo M1/M5) probablemente
    SUBESTIMA el ruido real de esta version H1 -- el MDE a priori impreso
    es optimista. El t-stat real (calculado sobre la muestra real, no el
    supuesto a priori) es la fuente de verdad, no el MDE a priori -- se
    mantiene igual como referencia de diseno, no como umbral de decision.

  Regla de corte (fijada de antemano, NO se toca despues de ver numeros):
  1. Screen IN-SAMPLE (2018-2022, ~70% de los eventos, orden cronologico):
     t-stat UNILATERAL (direccion esperada = positiva) >= 1.65. Si no,
     PARAR ese ventana -- no se mira el OOS para esa ventana.
  2. Si pasa el screen, OOS (2023-2025, ~30% restante): t-stat BILATERAL
     >= 1.96 (p<0.05, dos colas) decide pasa/no pasa.
  3. Robustez (equivalente sin-folds de "t-stat sin el fold dominante"):
     recalcular el t-stat OOS excluyendo el evento de mayor |retorno| --
     la conclusion cualitativa (pasa/no pasa) no puede cambiar.
  4. MDE (80% poder, alpha=0.05 dos colas) reportado con el N real
     obtenido en cada etapa -- no solo el N teorico (192/58) estimado
     antes de bajar los datos.

  Folds: NO walk-forward de folds -- split cronologico anclado unico
  (70% exploracion / 30% confirmacion), justificado porque este diseno
  no tiene parametros a barrer en TRAIN (direccion y ventanas son fijas
  a priori, no se optimiza nada) -- el motivo original del walk-forward
  multi-fold (evitar data snooping de seleccion de parametros) no aplica
  igual aca. Ver nota en CLAUDE.md / Bitacora de decisiones (2026-08-05).

  N variantes para DSR: 3 (las tres ventanas testeadas -- 1h/4h/24h; no
  hay grilla de parametros adicional).

Fuente de precios: MT5 en vivo (H1 -- ver REDEFINICION arriba, M1/M5/M15
no tienen profundidad historica suficiente en este servidor), no un CSV
pre-descargado -- las ventanas por evento son chicas (~25h c/u), no hace
falta bajar el historico completo de 8 anios (chocaria con el limite de
maxbars ya documentado en diagnostico_frecuencia_momentum_xauusd_h1.py).

LIMITACION CONOCIDA, no resuelta en este script (documentar antes de
confiar en el resultado): MT5 CalendarValueHistory devuelve el
actual_value ACTUAL (probablemente la version mas reciente conocida por
el terminal), no necesariamente el valor tal como se conocia en el
momento del release -- NFP en particular se revisa en los 2 meses
siguientes y tiene revisiones de benchmark anuales grandes. Esto es
exactamente el tipo de riesgo que el skill `data-integrity` esta
disenado para chequear (revisiones retroactivas de la fuente) -- correr
ese skill sobre event_study_releases.csv (comparando actual_value contra
una fuente point-in-time, ej. FRED/ALFRED para PAYEMS) antes de tratar
cualquier t-stat de acá como confirmatorio, no solo exploratorio.
"""
import math
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

DIR_PROYECTO = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta"
RUTA_RELEASES = r"C:\Users\josem\AppData\Roaming\MetaQuotes\Terminal\Common\Files\event_study_releases.csv"
RUTA_TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
SYMBOL = "EURUSD"
PIP = 0.0001

VENTANAS_HORAS = {"1h": 1, "4h": 4, "24h": 24}
TIMEFRAME_PRECIOS = "H1"  # M1/M5/M15 sin profundidad suficiente en este servidor -- ver REDEFINICION en el docstring
FRACCION_IN_SAMPLE = 0.70

T_SCREEN_IN_SAMPLE = 1.65   # unilateral, direccion esperada positiva
T_CORTE_OOS = 1.96          # bilateral
EFECTO_MINIMO_PIPS = 8.0    # Andersen et al. 2003, piso conservador (CPI)
SIGMA_RETORNO_1H_PCT = 0.16  # literatura, referencia para el MDE a priori

N_VARIANTES_DSR = len(VENTANAS_HORAS)  # 3 ventanas, sin grilla de parametros

import importlib.util
spec_dsr = importlib.util.spec_from_file_location("deflated_sharpe", DIR_PROYECTO + r"\deflated_sharpe.py")
dsr_mod = importlib.util.module_from_spec(spec_dsr)
sys.modules["deflated_sharpe"] = dsr_mod
spec_dsr.loader.exec_module(dsr_mod)


def cargar_releases():
    df = pd.read_csv(RUTA_RELEASES, dtype={"date": str, "time": str})
    df["evento_time"] = pd.to_datetime(df["date"] + " " + df["time"], format="%Y.%m.%d %H:%M")
    df["surprise"] = pd.to_numeric(df["surprise"], errors="coerce")
    df = df.dropna(subset=["surprise"]).reset_index(drop=True)
    df["direction"] = np.sign(df["surprise"])
    df = df[df["direction"] != 0].reset_index(drop=True)  # sorpresa exactamente 0 no aporta señal direccional
    df = df.sort_values("evento_time").reset_index(drop=True)
    return df


def conectar_mt5():
    import MetaTrader5 as mt5
    if not mt5.initialize(path=RUTA_TERMINAL):
        raise RuntimeError(f"No se pudo conectar a MT5: {mt5.last_error()}")
    if not mt5.symbol_select(SYMBOL, True):
        mt5.shutdown()
        raise RuntimeError(f"No se pudo seleccionar {SYMBOL}: {mt5.last_error()}")
    return mt5


def debug_conexion_precios(df_eventos, n=3):
    """Diagnostico aislado -- no toca el pipeline principal. Corre con:
    python event_study_eurusd.py --debug
    Chequea, en orden, cada eslabon que puede estar fallando silenciosamente
    (path del terminal, simbolo real del broker -- posible sufijo tipo
    EURUSD.a/EURUSDm --, profundidad de historial por timeframe) para los
    primeros N eventos del CSV. Confirmado 2026-08-05: M1/M5/M15 no tienen
    profundidad suficiente en este servidor (MetaQuotes-Demo) para cubrir
    2018-2025 -- solo H1 la tiene, por eso el pipeline usa H1 (ver
    REDEFINICION en el docstring del modulo)."""
    import MetaTrader5 as mt5

    print("=" * 70)
    print("DEBUG: conexion y datos de precio")
    print("=" * 70)

    ok = mt5.initialize(path=RUTA_TERMINAL)
    print(f"1) mt5.initialize(path={RUTA_TERMINAL!r}) -> {ok}")
    if not ok:
        print(f"   mt5.last_error() = {mt5.last_error()}")
        print("   Reintentando mt5.initialize() SIN path (auto-detectar terminal ya abierto)...")
        mt5.shutdown()
        ok = mt5.initialize()
        print(f"   mt5.initialize() -> {ok}")
        if not ok:
            print(f"   mt5.last_error() = {mt5.last_error()}")
            print("\nNo hay conexion -- el resto del debug no puede correr. Revisar que el "
                  "terminal MT5 este abierto y logueado, y que RUTA_TERMINAL apunte a ese exe.")
            return

    print(f"\n2) mt5.terminal_info() = {mt5.terminal_info()}")
    print(f"   mt5.account_info() = {mt5.account_info()}")

    sel = mt5.symbol_select(SYMBOL, True)
    print(f"\n3) mt5.symbol_select({SYMBOL!r}, True) -> {sel} | last_error={mt5.last_error()}")
    info_symbol = mt5.symbol_info(SYMBOL)
    if info_symbol is None:
        print(f"   mt5.symbol_info({SYMBOL!r}) -> None -- el simbolo puede no existir con ese nombre exacto "
              f"en este broker (sufijos comunes: EURUSD.a, EURUSDm, EURUSD.raw, etc.)")
    else:
        print(f"   visible={info_symbol.visible} | path={info_symbol.path} | "
              f"digits={info_symbol.digits} | trade_mode={info_symbol.trade_mode}")

    similares = mt5.symbols_get("*EURUSD*")
    nombres_similares = [s.name for s in similares] if similares else []
    print(f"   mt5.symbols_get('*EURUSD*') -> {nombres_similares}")
    if nombres_similares and SYMBOL not in nombres_similares:
        print(f"   ⚠️  '{SYMBOL}' no esta en la lista -- probablemente el nombre real del simbolo "
              f"en este broker es otro (usar uno de la lista de arriba como SYMBOL).")

    tick = mt5.symbol_info_tick(SYMBOL)
    print(f"   mt5.symbol_info_tick({SYMBOL!r}) = {tick}")

    print(f"\n4) Primeras 3 filas de {RUTA_RELEASES}:")
    print(pd.read_csv(RUTA_RELEASES).head(3).to_string(index=False))

    for i, (_, ev) in enumerate(df_eventos.head(n).iterrows()):
        print("\n" + "-" * 70)
        print(f"5) Evento {i + 1}/{n}: {ev['event']} en {ev['evento_time']}")
        desde = ev["evento_time"] - timedelta(hours=3)
        hasta = ev["evento_time"] + timedelta(hours=max(VENTANAS_HORAS.values()) + 2)
        print(f"   Ventana solicitada (para copy_rates_range): {desde} -> {hasta}")
        print(f"   Target pre-precio (asof, sin look-ahead): {ev['evento_time'] - timedelta(hours=1)}")
        for horas in VENTANAS_HORAS.values():
            print(f"   Target post-precio +{horas}h (asof): {ev['evento_time'] + timedelta(hours=horas)}")

        for etiqueta_tf, tf in [("M1", mt5.TIMEFRAME_M1), ("M5", mt5.TIMEFRAME_M5),
                                 ("M15", mt5.TIMEFRAME_M15), ("H1", mt5.TIMEFRAME_H1)]:
            rates = mt5.copy_rates_range(SYMBOL, tf, desde, hasta)
            n_rates = 0 if rates is None else len(rates)
            resultado = "None" if rates is None else f"{n_rates} barras"
            print(f"   copy_rates_range(SYMBOL, TIMEFRAME_{etiqueta_tf}, desde, hasta) -> {resultado} "
                  f"| last_error={mt5.last_error()}")
            if rates is not None and n_rates > 0:
                primero = pd.to_datetime(rates[0]["time"], unit="s")
                ultimo = pd.to_datetime(rates[-1]["time"], unit="s")
                print(f"     primera barra: {primero} | ultima barra: {ultimo}")

    print("\n" + "=" * 70)
    mt5.shutdown()


def precio_asof(rates_df, target_time):
    """Ultimo close H1 con time (=open de la vela) <= target_time. None si no hay barra."""
    sub = rates_df[rates_df["time"] <= target_time]
    if sub.empty:
        return None
    return sub.iloc[-1]["close"]


def calcular_retornos(mt5, df_eventos):
    filas = []
    n_sin_datos = 0
    for _, ev in df_eventos.iterrows():
        desde = ev["evento_time"] - timedelta(hours=3)
        hasta = ev["evento_time"] + timedelta(hours=max(VENTANAS_HORAS.values()) + 2)
        rates = mt5.copy_rates_range(SYMBOL, mt5.TIMEFRAME_H1, desde, hasta)
        if rates is None or len(rates) == 0:
            n_sin_datos += 1
            continue
        rates_df = pd.DataFrame(rates)
        rates_df["time"] = pd.to_datetime(rates_df["time"], unit="s")

        # Pre-precio SIN look-ahead: la vela H1 que CONTIENE el evento cierra
        # despues del release (mezclaria el "antes" con el propio movimiento
        # post-noticia) -- se usa la vela INMEDIATAMENTE ANTERIOR, target =
        # t_evento - 1h para el asof (cae 30-90min antes del release segun
        # el minuto exacto de publicacion). Ver REDEFINICION en el docstring.
        precio_pre = precio_asof(rates_df, ev["evento_time"] - timedelta(hours=1))
        if precio_pre is None:
            n_sin_datos += 1
            continue

        fila = {"evento_time": ev["evento_time"], "event": ev["event"],
                "surprise": ev["surprise"], "direction": ev["direction"],
                "precio_pre": precio_pre}
        ok = True
        for etiqueta, horas in VENTANAS_HORAS.items():
            precio_post = precio_asof(rates_df, ev["evento_time"] + timedelta(hours=horas))
            if precio_post is None:
                ok = False
                break
            retorno = precio_post / precio_pre - 1.0
            fila[f"retorno_{etiqueta}"] = retorno
            fila[f"signed_return_{etiqueta}"] = ev["direction"] * retorno
        if not ok:
            n_sin_datos += 1
            continue
        filas.append(fila)

    print(f"Eventos con precio H1 completo: {len(filas)} | descartados por falta de datos H1: {n_sin_datos}")
    return pd.DataFrame(filas)


def t_stat(valores):
    n = len(valores)
    media = valores.mean()
    std = valores.std(ddof=1)
    if n < 2 or not std or pd.isna(std):
        return n, media, float("nan"), float("nan")
    t = media / (std / math.sqrt(n))
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    return n, media, t, p


def mde(n, sigma_pct=SIGMA_RETORNO_1H_PCT):
    """MDE en % de retorno (mismas unidades que sigma_pct, ej. 0.0457 = 0.0457%)."""
    z_alpha, z_beta = 1.959963985, 0.841621234
    if n < 2:
        return float("nan")
    return (z_alpha + z_beta) * sigma_pct / math.sqrt(n)


def pct_a_pips(valor_pct, precio_referencia=1.08):
    """Convierte un % de retorno a pips aproximados, EURUSD~1.08 (mismo factor
    usado en la power analysis previa de la ficha, hypothesis-gate 2026-08-05)."""
    return valor_pct / 100 * precio_referencia / PIP


def evaluar_ventana(etiqueta, df_in, df_oos):
    print("\n" + "=" * 70)
    print(f"VENTANA {etiqueta}")
    print("=" * 70)

    col = f"signed_return_{etiqueta}"
    n_in, media_in, t_in, p_in = t_stat(df_in[col])
    pips_in = pct_a_pips(media_in * 100)
    mde_in = mde(n_in)
    print(f"IN-SAMPLE (2018-{df_in['evento_time'].max().year if not df_in.empty else '?'}): "
          f"n={n_in} | media={pips_in:+.2f} pips ({media_in*100:+.4f}%) | t={t_in:+.3f} | p={p_in:.4f}")
    print(f"  MDE a priori (sigma={SIGMA_RETORNO_1H_PCT}%, n={n_in}): {pct_a_pips(mde_in):.2f} pips")

    if not (t_in >= T_SCREEN_IN_SAMPLE):
        print(f"\n❌ NO PASA el screen in-sample (t={t_in:+.3f} < {T_SCREEN_IN_SAMPLE} unilateral) -- "
              f"PARAR, no se evalua OOS para {etiqueta}.")
        return {"ventana": etiqueta, "estado": "descartada_screen_in_sample",
                "n_in": n_in, "t_in": t_in, "p_in": p_in}

    print(f"\n✅ Pasa el screen in-sample (t={t_in:+.3f} >= {T_SCREEN_IN_SAMPLE}). Evaluando OOS...")

    n_oos, media_oos, t_oos, p_oos = t_stat(df_oos[col])
    pips_oos = pct_a_pips(media_oos * 100)
    mde_oos = mde(n_oos)
    mde_oos_pips = pct_a_pips(mde_oos)
    print(f"OOS (2023-2025): n={n_oos} | media={pips_oos:+.2f} pips ({media_oos*100:+.4f}%) | "
          f"t={t_oos:+.3f} | p={p_oos:.4f}")
    print(f"  MDE a priori (sigma={SIGMA_RETORNO_1H_PCT}%, n={n_oos}): {mde_oos_pips:.2f} pips "
          f"(efecto citado: {EFECTO_MINIMO_PIPS} pips -- "
          f"{'>= MDE, potencia OK' if EFECTO_MINIMO_PIPS >= mde_oos_pips else '< MDE, DISENO SUBPOTENCIADO'})")

    pasa_oos = abs(t_oos) >= T_CORTE_OOS
    print(f"\n{'✅ PASA' if pasa_oos else '❌ NO PASA'} el corte OOS "
          f"(|t|={abs(t_oos):.3f} {'>=' if pasa_oos else '<'} {T_CORTE_OOS} bilateral)")

    idx_extremo = df_oos[col].abs().idxmax()
    evento_extremo = df_oos.loc[idx_extremo]
    df_sin_extremo = df_oos.drop(idx_extremo)
    n_se, media_se, t_se, p_se = t_stat(df_sin_extremo[col])
    pasa_sin_extremo = abs(t_se) >= T_CORTE_OOS
    print(f"\nRobustez -- sin el evento OOS de mayor |retorno| "
          f"({evento_extremo['event']} {evento_extremo['evento_time'].date()}, "
          f"{pct_a_pips(evento_extremo[col] * 100):+.2f} pips): n={n_se} | t={t_se:+.3f} | p={p_se:.4f} | "
          f"{'✅ PASA' if pasa_sin_extremo else '❌ NO PASA'}")

    if pasa_oos != pasa_sin_extremo:
        print("  ⚠️  La conclusion CAMBIA al sacar el evento mas extremo -- resultado dependiente de 1 evento, "
              "no robusto (mismo criterio que 'sin el fold dominante' en el resto del proyecto).")

    return {
        "ventana": etiqueta, "estado": "evaluada",
        "n_in": n_in, "t_in": t_in, "p_in": p_in,
        "n_oos": n_oos, "media_oos_pips": pips_oos, "t_oos": t_oos, "p_oos": p_oos,
        "pasa_oos": pasa_oos, "t_oos_sin_extremo": t_se, "pasa_sin_extremo": pasa_sin_extremo,
        "robusto": pasa_oos == pasa_sin_extremo,
        "signed_returns_oos": df_oos[col],
    }


def analisis_dsr(resultados):
    evaluadas = [r for r in resultados if r["estado"] == "evaluada" and r["pasa_oos"]]
    if not evaluadas:
        print("\nNinguna ventana pasa el corte OOS -- no corresponde DSR.")
        return
    print("\n" + "#" * 70)
    print(f"Deflated Sharpe Ratio (N={N_VARIANTES_DSR} ventanas testeadas: "
          f"{', '.join(VENTANAS_HORAS.keys())})")
    print("#" * 70)
    for r in evaluadas:
        print(f"\n-- Ventana {r['ventana']} --")
        resultado = dsr_mod.deflated_sharpe_ratio(r["signed_returns_oos"].tolist(), N_VARIANTES_DSR)
        dsr_mod.reportar(resultado)


def main():
    df_eventos = cargar_releases()
    print(f"Releases NFP+CPI m/m con surprise valido: {len(df_eventos)} "
          f"({df_eventos['evento_time'].min().date()} -> {df_eventos['evento_time'].max().date()})")

    if "--debug" in sys.argv:
        debug_conexion_precios(df_eventos)
        return

    corte = int(len(df_eventos) * FRACCION_IN_SAMPLE)
    fecha_corte = df_eventos.iloc[corte]["evento_time"]
    print(f"Split cronologico: primeros {corte} eventos = IN-SAMPLE (hasta {fecha_corte.date()}), "
          f"resto ({len(df_eventos) - corte}) = OOS")

    mt5 = conectar_mt5()
    try:
        df_ret = calcular_retornos(mt5, df_eventos)
    finally:
        mt5.shutdown()

    if df_ret.empty:
        print("Sin eventos con datos de precio completos -- no se puede evaluar nada.")
        return

    df_in = df_ret[df_ret["evento_time"] < fecha_corte].reset_index(drop=True)
    df_oos = df_ret[df_ret["evento_time"] >= fecha_corte].reset_index(drop=True)

    resultados = [evaluar_ventana(etiqueta, df_in, df_oos) for etiqueta in VENTANAS_HORAS]

    print("\n" + "#" * 70)
    print("RESUMEN")
    print("#" * 70)
    for r in resultados:
        if r["estado"] == "descartada_screen_in_sample":
            print(f"{r['ventana']:>4}: descartada en screen in-sample (t={r['t_in']:+.3f})")
        else:
            estado = "PASA" if r["pasa_oos"] else "no pasa"
            robusto = "robusto" if r["robusto"] else "NO robusto (depende del evento extremo)"
            print(f"{r['ventana']:>4}: {estado} OOS (t={r['t_oos']:+.3f}, p={r['p_oos']:.4f}, "
                  f"n={r['n_oos']}) -- {robusto}")

    analisis_dsr(resultados)


if __name__ == "__main__":
    main()
