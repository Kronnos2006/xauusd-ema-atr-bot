"""
Chequeo de frecuencia -- hipotesis candidata "VIX como sorpresa -> EURUSD"
(H3 reformulada, 2026-08-04 -- ver Plan de investigación EURUSD.md).

Diferencia con Risk-off US500 (H2, descartado): no es "el VIX esta alto"
(nivel), es "el VIX subio mas de lo esperado dado su regimen reciente"
(sorpresa) -- rolling std de N dias en vez de std de la serie completa.

Definicion (Fase 0, SOLO conteo de episodios, sin M todavia):
retorno_diario(VIX) > k * std_rolling(retorno_diario, N dias), direccional
(solo SUBAS de VIX cuentan -- sesgo bajista en EURUSD es la hipotesis, una
baja de VIX no es la condicion testeada). Grilla de Fase 0: k en
{0.75, 1.0, 1.25} x N en {20, 60}.
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RUTA_VIX = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\vixcls.csv"
K_GRID = [0.75, 1.0, 1.25]
N_GRID = [20, 60]


def contar_episodios(serie_bool):
    cambios = serie_bool.ne(serie_bool.shift()).cumsum()
    grupos = serie_bool.groupby(cambios)
    episodios = [grupo for _, grupo in grupos if grupo.iloc[0]]
    duraciones = [len(g) for g in episodios]
    return len(episodios), duraciones


def main():
    df = pd.read_csv(RUTA_VIX)
    df.columns = ["fecha", "vix"]
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["vix"] = pd.to_numeric(df["vix"], errors="coerce")
    df = df.dropna(subset=["vix"]).reset_index(drop=True)

    anios_total = (df["fecha"].max() - df["fecha"].min()).days / 365.25
    print(f"VIXCLS disponible: {df['fecha'].min().date()} -> {df['fecha'].max().date()} "
          f"({anios_total:.1f} años, {len(df)} obs)")

    ret = df["vix"].pct_change(1)

    print(f"\n{'k':>6} | {'N':>4} | {'episodios':>9} | {'ep/año':>8} | {'dur. media (días)':>18} | {'dur. max':>8}")
    for n in N_GRID:
        std_rolling = ret.rolling(n, min_periods=n).std()
        anios_efectivos = (len(df) - n) / len(df) * anios_total if len(df) > n else 0
        for k in K_GRID:
            cond = (ret > k * std_rolling).fillna(False)  # SOLO subas
            n_ep, duraciones = contar_episodios(cond)
            ep_anio = n_ep / anios_efectivos if anios_efectivos > 0 else 0
            dur_prom = sum(duraciones) / len(duraciones) if duraciones else 0
            dur_max = max(duraciones) if duraciones else 0
            print(f"{k:>6.2f} | {n:>4} | {n_ep:>9} | {ep_anio:>8.2f} | {dur_prom:>18.1f} | {dur_max:>8}")

    print("\nUsar el ep/año del k más restrictivo (por cada N) como input conservador de "
          "triage_frecuencia.py.")


if __name__ == "__main__":
    main()
