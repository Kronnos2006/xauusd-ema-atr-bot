"""
Chequeos de independencia entre 2+ factores candidatos a combinar --
implementa los 4 puntos de la skill `factor-independence`.

No se corrió todavía sobre datos reales del proyecto: al 2026-07-27 solo
hay un factor con veredicto (DFII10, archivado) -- este script queda
listo para cuando exista un segundo candidato con el que combinarlo.
No inventar una corrida de ejemplo con datos sintéticos acá (seria
enganoso); usar directamente sobre trades reales cuando corresponda.

Sin scipy ni sklearn (convencion del proyecto): Spearman via ranking +
correlacion de Pearson sobre los rangos (equivalente exacto), PCA via
autovalores/autovectores de la matriz de correlacion con numpy.linalg.
"""
import numpy as np
import pandas as pd


def _serie_diaria(trades_df, fecha_col="time_entrada", valor_col="resultado_R_neto",
                   fecha_inicio=None, fecha_fin=None):
    """Convierte trades (formato ya usado en todo el proyecto: una fila por
    trade, con fecha y resultado_R_neto) a una serie diaria con el retorno
    en la fecha de entrada de cada trade y 0 en los dias sin trade -- para
    poder alinear factores con frecuencias de señal distintas en una
    grilla temporal comun."""
    s = trades_df.set_index(fecha_col)[valor_col]
    s = s.groupby(s.index.normalize()).sum()  # por si hay >1 trade el mismo dia
    inicio = fecha_inicio or s.index.min()
    fin = fecha_fin or s.index.max()
    calendario = pd.date_range(inicio, fin, freq="D")
    return s.reindex(calendario, fill_value=0.0)


def alinear_factores(dict_trades, fecha_col="time_entrada", valor_col="resultado_R_neto"):
    """dict_trades: {nombre_factor: dataframe de trades}. Devuelve un
    DataFrame con una columna por factor, alineado a la union de sus
    rangos de fechas, 0 donde un factor no tenia trade."""
    inicio = min(df[fecha_col].min() for df in dict_trades.values())
    fin = max(df[fecha_col].max() for df in dict_trades.values())
    series = {
        nombre: _serie_diaria(df, fecha_col, valor_col, inicio, fin)
        for nombre, df in dict_trades.items()
    }
    return pd.DataFrame(series)


def correlacion_spearman(df_alineado):
    """Matriz de correlacion de Spearman -- rankea cada columna y aplica
    Pearson sobre los rangos (equivalente exacto a Spearman, sin scipy)."""
    return df_alineado.rank().corr(method="pearson")


def correlacion_condicional_drawdown(df_alineado, decil=0.10):
    """Correlacion de Spearman restringida a los dias que caen en el decil
    inferior de AL MENOS uno de los factores (union, no interseccion --
    mas conservador: cualquier dia malo de cualquier factor cuenta). Si
    esta correlacion es mucho mayor que la incondicional, la
    diversificacion es ilusoria (sube justo cuando mas duele)."""
    peores_por_factor = set()
    for col in df_alineado.columns:
        equity = (1 + df_alineado[col] * 0.01).cumprod()  # 1% riesgo/trade, misma convencion que metricas_dfii10.py
        pico = equity.cummax()
        drawdown = (equity - pico) / pico
        umbral = drawdown.quantile(decil)
        peores_por_factor |= set(drawdown[drawdown <= umbral].index)

    subset = df_alineado.loc[df_alineado.index.isin(peores_por_factor)]
    if len(subset) < 10:
        return None, len(subset)  # muestra demasiado chica para una correlacion confiable
    return correlacion_spearman(subset), len(subset)


def pca_factores(df_alineado):
    """PCA via autovalores de la matriz de correlacion (no de covarianza --
    para que factores con distinta volatilidad no dominen el primer
    componente solo por escala). Devuelve la varianza explicada por
    componente, ordenada de mayor a menor."""
    corr = df_alineado.corr().values
    autovalores, _ = np.linalg.eigh(corr)
    autovalores = np.sort(autovalores)[::-1]
    autovalores = np.clip(autovalores, 0, None)  # numerico: autovalores muy chicos pueden dar negativo
    varianza_explicada = autovalores / autovalores.sum()
    return varianza_explicada


def reportar(dict_trades, fecha_col="time_entrada", valor_col="resultado_R_neto"):
    df = alinear_factores(dict_trades, fecha_col, valor_col)
    nombres = list(dict_trades.keys())

    print(f"Factores: {nombres}")
    print(f"Rango temporal alineado: {df.index.min().date()} -> {df.index.max().date()} ({len(df)} días)\n")

    print("=== 1. Correlación de Spearman (incondicional) ===")
    corr_incond = correlacion_spearman(df)
    print(corr_incond.round(3).to_string())

    print("\n=== 2. Correlación condicional (decil inferior de drawdown) ===")
    corr_cond, n_dias = correlacion_condicional_drawdown(df)
    if corr_cond is None:
        print(f"Muestra insuficiente ({n_dias} días) para una correlación condicional confiable.")
    else:
        print(f"({n_dias} días en el decil inferior de al menos un factor)")
        print(corr_cond.round(3).to_string())
        if len(nombres) == 2:
            delta = corr_cond.iloc[0, 1] - corr_incond.iloc[0, 1]
            print(f"\nCambio vs. incondicional: {corr_incond.iloc[0,1]:+.3f} -> {corr_cond.iloc[0,1]:+.3f} "
                  f"(delta {delta:+.3f})")
            if abs(corr_cond.iloc[0, 1]) > 2 * abs(corr_incond.iloc[0, 1]) and abs(corr_incond.iloc[0, 1]) > 0.01:
                print("⚠️  La correlación más que se duplica en el decil inferior -- posible diversificación ilusoria.")

    if len(nombres) >= 3:
        print("\n=== 3. PCA -- varianza explicada por componente ===")
        varianza = pca_factores(df)
        for i, v in enumerate(varianza, start=1):
            print(f"  Componente {i}: {v*100:.1f}%")
        if varianza[0] > 0.65:
            print("⚠️  El primer componente explica >65% de la varianza -- posible factor latente compartido.")
    else:
        print("\n=== 3. PCA ===\nSe necesitan 3+ factores para que el PCA aporte más que la correlación simple.")

    print("\n=== 4. Racional económico independiente ===")
    print("Chequeo cualitativo, no calculable acá -- completar a mano antes de decidir la combinación "
          "(ver checklist en la skill factor-independence).")


if __name__ == "__main__":
    print(__doc__)
