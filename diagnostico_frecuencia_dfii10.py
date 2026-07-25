"""
Chequeo de frecuencia -- hipotesis macro (tasas reales DFII10), fase 1.
=============================================================================
Antes de tocar walk-forward: cuenta cuantos episodios de "caida sostenida"
genera la regla candidata sobre el historial completo de DFII10 (desde 2003),
para cada N de la grilla declarada (20/60/120 dias habiles). Mismo chequeo
de sanidad que se hizo antes de bajar datos de H1 -- si da un puñado de
episodios en 23 anios, hay que avisar antes de seguir (mismo problema de
tamanio de muestra que descarto a D1).

Definicion fija de "caida sostenida en los ultimos N dias habiles"
(unica forma declarada, sin variantes): DFII10[t] < DFII10[t-N] -- el nivel
de la tasa real hoy es menor que hace N dias habiles. No hay parametro
adicional (no se exige monotonia estricta dia a dia, solo el nivel neto de
la ventana), para no introducir un grado de libertad extra no declarado.

Un "episodio" es una racha maxima de dias consecutivos donde la condicion
se cumple -- eso es lo que importa para el tamanio de muestra efectivo (si
la regla se mantiene senalizada 40 dias seguidos, es 1 episodio, no 40
observaciones independientes).

Fuente: FRED DFII10, descarga publica sin API key
(https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFII10).
"""
import pandas as pd

RUTA_CSV = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\dfii10.csv"
GRID_N = [20, 60, 120]
INICIO_DATOS_ORO_MT5 = pd.Timestamp("2004-06-11")  # confirmado via copy_rates_range D1 en MT5


def cargar_dfii10():
    df = pd.read_csv(RUTA_CSV)
    df.columns = ["fecha", "dfii10"]
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["dfii10"] = pd.to_numeric(df["dfii10"], errors="coerce")  # "." (feriados sin dato) -> NaN
    n_nan = df["dfii10"].isna().sum()
    df = df.dropna(subset=["dfii10"]).reset_index(drop=True)
    return df, n_nan


def contar_episodios(serie_bool):
    """Cuenta rachas maximas de True consecutivos en una serie booleana."""
    cambios = serie_bool.ne(serie_bool.shift()).cumsum()
    grupos = serie_bool.groupby(cambios)
    episodios = [grupo for _, grupo in grupos if grupo.iloc[0]]
    duraciones = [len(g) for g in episodios]
    return len(episodios), duraciones


def main():
    df, n_nan = cargar_dfii10()
    print(f"Filas cargadas (dias habiles con dato valido): {len(df)}")
    print(f"Filas con '.' (feriado/no dato) descartadas: {n_nan}")
    print(f"Rango DFII10 completo: {df['fecha'].min().date()} -> {df['fecha'].max().date()}")
    anios_total = (df['fecha'].max() - df['fecha'].min()).days / 365.25
    print(f"Total anios cubiertos (DFII10): {anios_total:.1f}\n")

    for n in GRID_N:
        cond = df["dfii10"] < df["dfii10"].shift(n)
        cond = cond.fillna(False)

        print(f"=== N={n} dias habiles ===")
        for etiqueta, mask_rango in [
            ("Historial completo DFII10 (2003+)", pd.Series(True, index=df.index)),
            (f"Restringido a datos de oro MT5 ({INICIO_DATOS_ORO_MT5.date()}+)", df["fecha"] >= INICIO_DATOS_ORO_MT5),
        ]:
            cond_r = cond & mask_rango
            n_dias = int(cond_r.sum())
            n_dias_base = int(mask_rango.sum())
            n_episodios, duraciones = contar_episodios(cond[mask_rango].reset_index(drop=True))
            dur_prom = sum(duraciones) / len(duraciones) if duraciones else 0
            dur_max = max(duraciones) if duraciones else 0
            pct_tiempo = 100 * n_dias / n_dias_base if n_dias_base else 0
            anios_rango = n_dias_base / 252  # ~252 dias habiles/año
            print(f"  [{etiqueta}]")
            print(f"    Dias con señal activa: {n_dias} ({pct_tiempo:.1f}% de {n_dias_base} dias)")
            print(f"    Episodios: {n_episodios} | Episodios/año: {n_episodios / anios_rango:.2f}"
                  f" | Duracion media: {dur_prom:.1f}d | max: {dur_max}d")
        print()


if __name__ == "__main__":
    main()
