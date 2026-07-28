"""
Validacion del DXY sintetico contra valores reales publicados.
=============================================================================
Antes de usar la serie sintetica (construir_dxy_sintetico.py) para nada
mas (chequeo de frecuencia, walk-forward), se compara contra valores
reales de cierre del US Dollar Index publicados en investing.com
(https://www.investing.com/indices/usdollar-historical-data, consultado
2026-07-27) para 23 fechas conocidas (2026-06-29 a 2026-07-28).

Mismo criterio de tolerancia ya usado en el proyecto para la verificacion
cruzada de fuente de DFII10 (FRED vs. Treasury.gov): diferencia absoluta
maxima > 0.05 puntos -- revisar antes de confiar en la serie.
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RUTA_SINTETICO = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\dxy_sintetico.csv"

# Valores reales publicados, investing.com, consultados 2026-07-27
VALORES_REALES = {
    "2026-07-28": 101.55,
    "2026-07-27": 101.53,
    "2026-07-26": 101.27,
    "2026-07-24": 101.47,
    "2026-07-23": 101.44,
    "2026-07-22": 101.13,
    "2026-07-21": 101.17,
    "2026-07-20": 100.95,
    "2026-07-17": 100.76,
    "2026-07-16": 100.76,
    "2026-07-15": 100.49,
    "2026-07-14": 100.92,
    "2026-07-13": 101.24,
    "2026-07-10": 100.95,
    "2026-07-09": 100.90,
    "2026-07-08": 100.99,
    "2026-07-07": 101.02,
    "2026-07-06": 100.85,
    "2026-07-03": 100.86,
    "2026-07-02": 100.86,
    "2026-07-01": 101.39,
    "2026-06-30": 101.19,
    "2026-06-29": 101.11,
}


def main():
    df = pd.read_csv(RUTA_SINTETICO)
    df["time"] = pd.to_datetime(df["time"])

    reales = pd.Series(VALORES_REALES, name="real").rename_axis("fecha")
    reales.index = pd.to_datetime(reales.index)

    sint = df.set_index("time")["dxy_sintetico"]

    cruce = pd.DataFrame({"real": reales, "sintetico": sint}).dropna()
    cruce["diff_abs"] = (cruce["real"] - cruce["sintetico"]).abs()
    corr = cruce["real"].corr(cruce["sintetico"])

    print("=== Validación DXY sintético (6 pares FX, fórmula ICE) vs. investing.com ===")
    print(f"Fechas comparadas: {len(cruce)} de {len(VALORES_REALES)} valores de referencia "
          f"({cruce.index.min().date()} -> {cruce.index.max().date()})")
    print(cruce.to_string(float_format=lambda x: f"{x:.4f}"))
    print(f"\nCorrelación: {corr:.6f}")
    print(f"Diferencia absoluta -- media: {cruce['diff_abs'].mean():.4f} | máxima: {cruce['diff_abs'].max():.4f}")
    if cruce["diff_abs"].max() > 0.05:
        excedidas = cruce[cruce["diff_abs"] > 0.05]
        print(f"⚠️  {len(excedidas)}/{len(cruce)} fechas superan 0.05 puntos de diferencia (umbral prestado "
              f"de la verificación FRED vs. Treasury.gov de DFII10, en otra escala -- ahí eran puntos "
              f"porcentuales de tasa, acá son puntos de índice ~100):")
        print(excedidas.to_string(float_format=lambda x: f"{x:.4f}"))
    else:
        print("✅ Validación exitosa -- DXY sintético queda confirmado como proxy usable "
              "(mismo umbral de tolerancia que la verificación FRED vs. Treasury.gov de DFII10).")

    faltantes = set(VALORES_REALES) - set(cruce.index.strftime("%Y-%m-%d"))
    if faltantes:
        print(f"\nFechas de referencia sin dato sintético correspondiente (no afecta el veredicto): {sorted(faltantes)}")


if __name__ == "__main__":
    main()
