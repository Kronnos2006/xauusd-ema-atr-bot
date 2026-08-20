"""
Chequeo de frecuencia -- hipotesis candidata "Momentum DXY sintetico H4 ->
XAUUSD" (2026-08-04, primer candidato tras levantar la restriccion de
intradia -- ver Bitácora de decisiones.md).

Frase falsable (Fase 1, dada por el usuario): cuando el retorno del DXY
sintetico en la vela H4 cerrada supera k desvios estandar -- calculados
sobre su propia distribucion historica ROLLING de 252 dias habiles, no el
std de la serie completa como en la version diaria ya descartada -- en
valor absoluto, el oro tiene sesgo direccional inverso en las M velas H4
siguientes. Grilla: k en {0.75, 1.0, 1.25} x M en {1, 2, 3} velas H4 (M no
afecta el conteo de episodios, solo el horizonte de medicion del sesgo).

Este script SOLO cuenta episodios/año para los 3 valores de k -- no simula
ni un trade. El numero mas bajo de los 3 (k mas exigente) es el que debe
usarse para derivar el numero de folds (el punto mas restrictivo de la
grilla es el que fija el piso).
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RUTA_CSV = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\dxy_sintetico_h4.csv"
VENTANA_DIAS_HABILES = 252
K_GRID = [0.75, 1.0, 1.25]
INICIO_DATOS_ORO_MT5 = pd.Timestamp("2004-06-11")


def contar_episodios(serie_bool):
    cambios = serie_bool.ne(serie_bool.shift()).cumsum()
    grupos = serie_bool.groupby(cambios)
    episodios = [grupo for _, grupo in grupos if grupo.iloc[0]]
    duraciones = [len(g) for g in episodios]
    return len(episodios), duraciones


def main():
    df = pd.read_csv(RUTA_CSV)
    df["time"] = pd.to_datetime(df["time"])
    df = df[df["time"] >= INICIO_DATOS_ORO_MT5].reset_index(drop=True)

    anios_total = (df["time"].max() - df["time"].min()).days / 365.25
    dias_calendario = df["time"].dt.normalize().nunique()
    velas_por_dia = len(df) / dias_calendario
    ventana_velas = round(VENTANA_DIAS_HABILES * velas_por_dia)

    print(f"Rango (restringido a oro MT5, {INICIO_DATOS_ORO_MT5.date()}+): "
          f"{df['time'].min()} -> {df['time'].max()} ({anios_total:.1f} años)")
    print(f"Velas H4 totales: {len(df)} | Velas/día promedio: {velas_por_dia:.2f} "
          f"| Ventana rolling ({VENTANA_DIAS_HABILES} días hábiles) ≈ {ventana_velas} velas H4")

    ret = df["dxy_sintetico"].pct_change(1)
    std_rolling = ret.rolling(ventana_velas, min_periods=ventana_velas).std()

    print(f"\n{'k':>6} | {'episodios':>9} | {'ep/año':>8} | {'dur. media (velas)':>18} | {'dur. max':>8}")
    resultados = {}
    for k in K_GRID:
        cond = (ret.abs() > k * std_rolling).fillna(False)
        n_ep, duraciones = contar_episodios(cond)
        # años efectivos: descontar el warm-up de la ventana rolling (no hay
        # señal evaluable ahí, contarlo como "disponible" infla la frecuencia)
        anios_efectivos = (len(df) - ventana_velas) / velas_por_dia / 365.25 if len(df) > ventana_velas else 0
        ep_anio = n_ep / anios_efectivos if anios_efectivos > 0 else 0
        dur_prom = sum(duraciones) / len(duraciones) if duraciones else 0
        dur_max = max(duraciones) if duraciones else 0
        resultados[k] = (n_ep, ep_anio, dur_prom, dur_max, anios_efectivos)
        print(f"{k:>6.2f} | {n_ep:>9} | {ep_anio:>8.2f} | {dur_prom:>18.1f} | {dur_max:>8}")

    k_mas_exigente = max(K_GRID)
    print(f"\nAños efectivos post warm-up (ventana rolling descontada): {resultados[k_mas_exigente][4]:.1f}")
    print(f"Usar el ep/año de k={k_mas_exigente} (el más restrictivo de la grilla) "
          f"para derivar el número de folds -- es el punto que fija el piso de 30 trades/fold.")


if __name__ == "__main__":
    main()
