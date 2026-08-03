"""
Chequeo de frecuencia -- hipotesis macro DXY MOMENTUM de corto plazo, fase 0.
=============================================================================
Distinto del ya descartado "DXY nivel/caida sostenida N=20/60/120"
(diagnostico_frecuencia_dxy.py): esa hipotesis medía el NIVEL del DXY
respecto a N dias atras. Esta mide el RETORNO de muy corto plazo (1 dia
habil) del DXY sintetico, thresholdeado por desviaciones estandar de su
propia distribucion -- mecanismo distinto (microestructura FX / conversion
mecanica de precio en USD), aunque comparte la fuente de datos
(dxy_sintetico.csv, construir_dxy_sintetico.py).

Definicion fija de "episodio" (unica forma declarada, sin variantes):
|retorno_1d(DXY sintetico)| > k * std(retorno_1d), con k=1.0. Un episodio
es una racha maxima de dias consecutivos donde la condicion se cumple.
"""
import pandas as pd

RUTA_CSV = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\dxy_sintetico.csv"
VENTANA_DIAS = 1
K_STD = 1.0
INICIO_DATOS_ORO_MT5 = pd.Timestamp("2004-06-11")


def contar_episodios(serie_bool):
    """Cuenta rachas maximas de True consecutivos en una serie booleana."""
    cambios = serie_bool.ne(serie_bool.shift()).cumsum()
    grupos = serie_bool.groupby(cambios)
    episodios = [grupo for _, grupo in grupos if grupo.iloc[0]]
    duraciones = [len(g) for g in episodios]
    return len(episodios), duraciones


def main():
    df = pd.read_csv(RUTA_CSV).rename(columns={"time": "fecha"})
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df[df["fecha"] >= INICIO_DATOS_ORO_MT5].reset_index(drop=True)

    anios_total = (df["fecha"].max() - df["fecha"].min()).days / 365.25
    print(f"Rango (restringido a oro MT5, {INICIO_DATOS_ORO_MT5.date()}+): "
          f"{df['fecha'].min().date()} -> {df['fecha'].max().date()} ({anios_total:.1f} años)")

    ret = df["dxy_sintetico"].pct_change(VENTANA_DIAS)
    std = ret.std()
    cond = (ret.abs() > K_STD * std).fillna(False)

    n_episodios, duraciones = contar_episodios(cond)
    ep_anio = n_episodios / anios_total
    dur_prom = sum(duraciones) / len(duraciones) if duraciones else 0
    dur_max = max(duraciones) if duraciones else 0

    print(f"Std retorno {VENTANA_DIAS}d: {std:.5f}")
    print(f"Episodios: {n_episodios} | Episodios/año: {ep_anio:.2f} "
          f"| Duracion media: {dur_prom:.1f}d | max: {dur_max}d")
    print(f"\nUsar este numero (episodios/año) como input de triage_frecuencia.py.")


if __name__ == "__main__":
    main()
