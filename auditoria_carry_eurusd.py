"""
Auditoria por capas -- validacion de pipeline reproduciendo el carry trade
EUR/USD (2026-08-04). Objetivo: NO buscar edge nuevo, sino confirmar que
el pipeline detecta un efecto ya documentado (carry) antes de confiar en
el pipeline para candidatos nuevos. Orden fijado por el usuario, cada capa
se reporta antes de pasar a la siguiente; si la Capa 4 no muestra relacion
basica, se para y se reporta -- no se corre el motor de backtest completo.

Datos (ver mensaje de cobertura previo, aprobado por el usuario):
- EUR 3M interbank (proxy EURIBOR 3M): FRED IR3TIB01EZM156N, mensual, 1994-2026.
- USD 3M interbank (misma familia OECD, comparable): FRED IR3TIB01USM156N,
  mensual, 1964-2026. Se usa esta serie en todo el rango en vez de empalmar
  con SOFR a mitad de camino (mas consistente metodologicamente).
- EURUSD: MT5, diario, 2000-2026 (historial/eurusd_d1.csv) -- acota el
  rango util a ~26 años.

Capa 0 (implicita, antes de la Capa 1): las series de tasas son
MENSUALES, no diarias -- se hace forward-fill del ultimo valor conocido.
Se asume 1 mes de rezago de publicacion (el dato de tasas del mes M se
considera "conocido" recien desde el dia 1 del mes M+1) para evitar
look-ahead sutil sobre una serie macro publicada con rezago real.
"""
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RUTA_EUR = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\eur_3m_interbank.csv"
RUTA_USD = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\usd_3m_interbank.csv"
RUTA_EURUSD = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\eurusd_d1.csv"

REZAGO_PUBLICACION_MESES = 1
HORIZONTES_M = [1, 5, 10, 20]
N_DECILES = 10


def cargar_tasas_mensuales_con_rezago(ruta, nombre_col):
    df = pd.read_csv(ruta)
    df.columns = ["fecha", nombre_col]
    df["fecha"] = pd.to_datetime(df["fecha"])
    df[nombre_col] = pd.to_numeric(df[nombre_col], errors="coerce")
    # el dato del mes M se considera conocido desde el mes M + REZAGO
    df["fecha_conocida"] = df["fecha"] + pd.DateOffset(months=REZAGO_PUBLICACION_MESES)
    return df[["fecha_conocida", nombre_col]].dropna()


def construir_señal_diaria(df_eurusd):
    eur = cargar_tasas_mensuales_con_rezago(RUTA_EUR, "tasa_eur")
    usd = cargar_tasas_mensuales_con_rezago(RUTA_USD, "tasa_usd")

    fechas = df_eurusd[["fecha"]].copy()
    fechas = fechas.merge(eur.rename(columns={"fecha_conocida": "fecha"}), on="fecha", how="left")
    fechas = fechas.merge(usd.rename(columns={"fecha_conocida": "fecha"}), on="fecha", how="left")
    fechas["tasa_eur"] = fechas["tasa_eur"].ffill()
    fechas["tasa_usd"] = fechas["tasa_usd"].ffill()

    # Convencion de signo (Capa 2, fijada por el usuario):
    # EURUSD = dolares por 1 euro. Diferencial A FAVOR DEL DOLAR (tasa_usd > tasa_eur)
    # -> sesgo BAJISTA en EURUSD. D positivo = favorece al dolar.
    fechas["D_favor_usd"] = fechas["tasa_usd"] - fechas["tasa_eur"]
    return fechas[["fecha", "tasa_eur", "tasa_usd", "D_favor_usd"]]


def capa1_alineacion_temporal(df):
    print("=" * 70)
    print("CAPA 1 -- Alineación temporal")
    print("=" * 70)
    print("Definición: D_favor_usd conocido al cierre del día t (con rezago de "
          f"{REZAGO_PUBLICACION_MESES} mes sobre la publicación mensual) predice "
          "el retorno de EURUSD desde el cierre de t hasta el cierre de t+M "
          "(el período (t, t+M], NO incluye el día t mismo) -- 'la señal de hoy "
          "predice el retorno de mañana en adelante, no de hoy'.")
    primero_valido = df.dropna(subset=["D_favor_usd"])["fecha"].min()
    print(f"Primer día con señal disponible (tras rezago + forward-fill): {primero_valido.date()}")
    print(f"Filas totales: {len(df)} | Filas con señal NaN (antes del primer dato de tasas): "
          f"{df['D_favor_usd'].isna().sum()}")


def capa2_convencion_signo(df):
    print("\n" + "=" * 70)
    print("CAPA 2 -- Convención de signo")
    print("=" * 70)
    print("EURUSD cotiza dólares por 1 euro. D_favor_usd = tasa_usd - tasa_eur.")
    print("Hipótesis: D_favor_usd ALTO (dólar paga más) -> sesgo BAJISTA en EURUSD "
          "(el diferencial atrae flujos hacia USD, EUR se deprecia relativo).")
    print(f"D_favor_usd actual (última fila con dato): {df['D_favor_usd'].dropna().iloc[-1]:+.3f} pp")
    print(f"D_favor_usd -- media histórica: {df['D_favor_usd'].mean():+.3f} pp | "
          f"min: {df['D_favor_usd'].min():+.3f} | max: {df['D_favor_usd'].max():+.3f}")
    print("Predicción a verificar en Capa 4: correlación(D_favor_usd, retorno futuro) "
          "debe ser NEGATIVA si la hipótesis del carry es correcta en esta convención de signo.")


def capa3_y_4_horizontes_y_relacion(df, df_eurusd):
    print("\n" + "=" * 70)
    print("CAPA 3 + 4 -- Horizontes de retorno y relación señal-retorno simple")
    print("=" * 70)

    df = df.merge(df_eurusd[["fecha", "close"]], on="fecha", how="left").reset_index(drop=True)
    resultados = {}

    for m in HORIZONTES_M:
        retorno_m = df["close"].shift(-m) / df["close"] - 1.0
        sub = df[["D_favor_usd"]].copy()
        sub["retorno_m"] = retorno_m
        sub = sub.dropna()

        corr = sub["D_favor_usd"].corr(sub["retorno_m"])
        n = len(sub)

        sub["decil"] = pd.qcut(sub["D_favor_usd"], N_DECILES, labels=False, duplicates="drop")
        medias_decil = sub.groupby("decil")["retorno_m"].mean()

        # monotonicidad: contar cuantos pasos consecutivos van en la direccion
        # esperada (decreciente, porque D alto -> retorno bajo si la hipotesis vale)
        diffs = medias_decil.diff().dropna()
        pasos_monotonos_bajando = (diffs < 0).sum()
        pasos_totales = len(diffs)

        resultados[m] = {
            "n": n, "corr": corr,
            "medias_decil": medias_decil,
            "monotonia": (pasos_monotonos_bajando, pasos_totales),
        }

        print(f"\n--- M={m} día(s) ---")
        print(f"n={n} | correlación(D_favor_usd, retorno_{m}d) = {corr:+.4f} "
              f"{'(signo esperado: negativo)' if True else ''}")
        print("Retorno medio por decil de D_favor_usd (decil 0 = USD menos favorecido "
              "-> decil 9 = USD más favorecido):")
        for d, r in medias_decil.items():
            barra = "█" * int(abs(r) * 5000)
            signo = "+" if r >= 0 else "-"
            print(f"  decil {int(d)}: {r*100:+.4f}%  {signo}{barra}")
        print(f"Monotonía (pasos decrecientes / pasos totales entre deciles consecutivos): "
              f"{pasos_monotonos_bajando}/{pasos_totales}")

    return resultados


def veredicto_capa4(resultados):
    print("\n" + "#" * 70)
    print("VEREDICTO -- ¿hay relación básica señal-retorno? (antes de tocar el motor de backtest)")
    print("#" * 70)

    algun_corr_negativa_relevante = False
    for m, r in resultados.items():
        corr = r["corr"]
        mono_ok, mono_total = r["monotonia"]
        pct_mono = mono_ok / mono_total * 100 if mono_total else 0
        signo_correcto = corr < 0
        print(f"M={m:>2}d | corr={corr:+.4f} | signo {'✅ correcto' if signo_correcto else '❌ invertido'} "
              f"| monotonía {mono_ok}/{mono_total} ({pct_mono:.0f}%)")
        if signo_correcto and pct_mono >= 60:
            algun_corr_negativa_relevante = True

    print()
    if algun_corr_negativa_relevante:
        print("✅ Al menos un horizonte muestra signo correcto (correlación negativa) "
              "y monotonía razonable entre deciles -> hay relación básica señal-retorno. "
              "Procede evaluar si seguir al motor de backtest completo.")
    else:
        print("❌ Ningún horizonte muestra a la vez signo correcto Y monotonía razonable "
              "(>=60% de los pasos entre deciles en la dirección esperada) -> NO hay "
              "relación básica señal-retorno detectable con este diseño. "
              "Por instrucción del usuario: PARAR ACÁ, no correr el motor de backtest completo.")
    return algun_corr_negativa_relevante


def main():
    df_eurusd = pd.read_csv(RUTA_EURUSD)
    df_eurusd["fecha"] = pd.to_datetime(df_eurusd["time"])

    df = construir_señal_diaria(df_eurusd)

    capa1_alineacion_temporal(df)
    capa2_convencion_signo(df)
    resultados = capa3_y_4_horizontes_y_relacion(df, df_eurusd)
    veredicto_capa4(resultados)


if __name__ == "__main__":
    main()
