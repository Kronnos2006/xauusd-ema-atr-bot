"""
Chequeo de frecuencia -- hipotesis macro DXY (sintetico), fase 1.
=============================================================================
Analogo a diagnostico_frecuencia_dfii10.py: cuenta cuantos episodios de
"caida sostenida" genera la regla candidata sobre el historial completo
del DXY sintetico (construir_dxy_sintetico.py, ya validado contra 21
valores reales de investing.com -- correlacion 0.9945, ver
validar_dxy_sintetico.py), para cada N de la grilla declarada
(20/60/120 dias habiles).

Misma definicion de "caida sostenida" que DFII10 (sin variantes):
DXY[t] < DXY[t-N] -- nivel neto de la ventana, sin exigir monotonia.
"""
import pandas as pd

RUTA_CSV = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\dxy_sintetico.csv"
GRID_N = [20, 60, 120]
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
    df = df.rename(columns={"time": "fecha"})
    print(f"Filas cargadas (DXY sintetico, dias con los 6 pares solapados): {len(df)}")
    print(f"Rango completo: {df['fecha'].min().date()} -> {df['fecha'].max().date()}")
    anios_total = (df['fecha'].max() - df['fecha'].min()).days / 365.25
    print(f"Total anios cubiertos: {anios_total:.1f}\n")

    for n in GRID_N:
        cond = df["dxy_sintetico"] < df["dxy_sintetico"].shift(n)
        cond = cond.fillna(False)

        print(f"=== N={n} dias habiles ===")
        for etiqueta, mask_rango in [
            ("Historial completo DXY sintetico", pd.Series(True, index=df.index)),
            (f"Restringido a datos de oro MT5 ({INICIO_DATOS_ORO_MT5.date()}+)", df["fecha"] >= INICIO_DATOS_ORO_MT5),
        ]:
            cond_r = cond & mask_rango
            n_dias = int(cond_r.sum())
            n_dias_base = int(mask_rango.sum())
            n_episodios, duraciones = contar_episodios(cond[mask_rango].reset_index(drop=True))
            dur_prom = sum(duraciones) / len(duraciones) if duraciones else 0
            dur_max = max(duraciones) if duraciones else 0
            pct_tiempo = 100 * n_dias / n_dias_base if n_dias_base else 0
            anios_rango = n_dias_base / 252
            print(f"  [{etiqueta}]")
            print(f"    Dias con señal activa: {n_dias} ({pct_tiempo:.1f}% de {n_dias_base} dias)")
            print(f"    Episodios: {n_episodios} | Episodios/año: {n_episodios / anios_rango:.2f}"
                  f" | Duracion media: {dur_prom:.1f}d | max: {dur_max}d")
        print()


if __name__ == "__main__":
    main()
