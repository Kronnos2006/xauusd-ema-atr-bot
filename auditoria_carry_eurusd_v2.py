"""
Auditoria por capas -- REFORMULACION (2026-08-04) del intento anterior
(auditoria_carry_eurusd.py). El intento anterior probaba si el diferencial
de tasas predice la DIRECCION del spot EURUSD -- eso es el UIP puzzle
(famosamente debil/inestable en la literatura), no el carry trade real.
La auditoria anterior confirmo que el pipeline no tiene errores (signo
correcto y consistente en los 4 horizontes) -- el problema era la
formulacion de la hipotesis, no la implementacion.

Hipotesis reformulada: el carry trade real gana por DEVENGO del
diferencial de tasas, no por prediccion de direccion del spot.
Regla de posicion (fija, no una señal continua a correlacionar):
  - LARGO EURUSD (largo EUR, corto USD) cuando tasa_eur > tasa_usd.
  - CORTO EURUSD (largo USD, corto EUR) cuando tasa_usd > tasa_eur.
Se mantiene la posicion durante M días, cobrando el diferencial de tasas
devengado ademas de cualquier movimiento de precio.

Retorno total(t, M) = retorno_direccional(t,M) + carry_devengado(t,M)
  retorno_direccional = signo(D) * retorno_spot_M   (P&L del movimiento de precio)
  carry_devengado     = |D| * (M/365) / 100          (diferencial anualizado,
                         prorrateado a M días, siempre positivo por
                         construccion -- siempre se está largo el que paga más)
  D = tasa_eur - tasa_usd (pp)

Capa 1 y 2 (alineación temporal, convención de signo): mismos datos y
mismo rezago de publicación (1 mes) que la auditoría anterior -- no
cambia nada de eso, solo cambia qué se hace con la señal.

Capa 3+4 (horizontes + relación simple, ANTES del motor de backtest
completo): en vez de correlación (no aplica a una regla de posición fija,
no a una señal continua), se descompone el retorno total en su componente
direccional vs. su componente de devengo, por horizonte y por decil de
|D| (magnitud del diferencial) -- para ver si el devengo domina (como
predice la literatura de carry) y si la magnitud del diferencial se
relaciona con el retorno total de forma creciente.
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
DIAS_ANIO = 365


def cargar_tasas_mensuales_con_rezago(ruta, nombre_col):
    df = pd.read_csv(ruta)
    df.columns = ["fecha", nombre_col]
    df["fecha"] = pd.to_datetime(df["fecha"])
    df[nombre_col] = pd.to_numeric(df[nombre_col], errors="coerce")
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

    # D > 0 -> EUR paga mas -> largo EURUSD. D < 0 -> USD paga mas -> corto EURUSD.
    fechas["D"] = fechas["tasa_eur"] - fechas["tasa_usd"]
    fechas["posicion"] = np.sign(fechas["D"])
    return fechas[["fecha", "tasa_eur", "tasa_usd", "D", "posicion"]]


def capa1_alineacion_temporal(df):
    print("=" * 70)
    print("CAPA 1 -- Alineación temporal (sin cambios respecto al intento anterior)")
    print("=" * 70)
    print("Posición fijada al cierre del día t (D conocido con rezago de "
          f"{REZAGO_PUBLICACION_MESES} mes) se mantiene desde el cierre de t hasta "
          "el cierre de t+M -- el retorno del período (t, t+M] no incluye el día t.")
    primero_valido = df.dropna(subset=["D"])["fecha"].min()
    print(f"Primer día con señal disponible: {primero_valido.date()}")


def capa2_convencion_signo(df):
    print("\n" + "=" * 70)
    print("CAPA 2 -- Convención de signo (REFORMULADA)")
    print("=" * 70)
    print("D = tasa_eur - tasa_usd. Regla de posición (no una correlación a testear):")
    print("  D > 0 (EUR paga más) -> LARGO EURUSD (compra EUR, vende USD, cobra el diferencial)")
    print("  D < 0 (USD paga más) -> CORTO EURUSD (compra USD, vende EUR, cobra el diferencial)")
    dist = df["posicion"].value_counts(normalize=True) * 100
    print(f"Distribución histórica de la posición: largo EURUSD {dist.get(1.0, 0):.1f}% de los días, "
          f"corto EURUSD {dist.get(-1.0, 0):.1f}% de los días.")


def capa3_y_4_horizontes_y_relacion(df, df_eurusd):
    print("\n" + "=" * 70)
    print("CAPA 3 + 4 -- Horizontes y descomposición direccional vs. devengo")
    print("=" * 70)

    df = df.merge(df_eurusd[["fecha", "close"]], on="fecha", how="left").reset_index(drop=True)
    resultados = {}

    for m in HORIZONTES_M:
        spot_return_m = df["close"].shift(-m) / df["close"] - 1.0
        sub = df[["D", "posicion"]].copy()
        sub["spot_return_m"] = spot_return_m
        sub = sub.dropna()

        sub["retorno_direccional"] = sub["posicion"] * sub["spot_return_m"]
        sub["carry_devengado"] = sub["D"].abs() * (m / DIAS_ANIO) / 100.0
        sub["retorno_total"] = sub["retorno_direccional"] + sub["carry_devengado"]

        n = len(sub)
        media_total = sub["retorno_total"].mean()
        media_direccional = sub["retorno_direccional"].mean()
        media_carry = sub["carry_devengado"].mean()
        std_total = sub["retorno_total"].std(ddof=1)
        t_stat = media_total / (std_total / np.sqrt(n)) if std_total else float("nan")

        sub["decil_abs_D"] = pd.qcut(sub["D"].abs(), N_DECILES, labels=False, duplicates="drop")
        por_decil = sub.groupby("decil_abs_D")[["retorno_total", "retorno_direccional", "carry_devengado"]].mean()

        resultados[m] = {
            "n": n, "media_total": media_total, "media_direccional": media_direccional,
            "media_carry": media_carry, "t_stat": t_stat, "por_decil": por_decil,
        }

        print(f"\n--- M={m} día(s) ---")
        print(f"n={n} | retorno total medio={media_total*100:+.4f}% "
              f"(direccional={media_direccional*100:+.4f}% + devengo={media_carry*100:+.4f}%) "
              f"| t-stat(total)={t_stat:+.3f}")
        print("Por decil de |D| (0=diferencial más chico -> 9=diferencial más grande), "
              "retorno medio total / direccional / devengo:")
        for d, fila in por_decil.iterrows():
            print(f"  decil {int(d)}: total={fila['retorno_total']*100:+.4f}%  "
                  f"| direccional={fila['retorno_direccional']*100:+.4f}%  "
                  f"| devengo={fila['carry_devengado']*100:+.4f}%")

        diffs_total = por_decil["retorno_total"].diff().dropna()
        creciente = (diffs_total > 0).sum()
        print(f"Monotonía creciente del retorno TOTAL por decil de |D|: {creciente}/{len(diffs_total)} pasos")

    return resultados


def veredicto_capa4(resultados):
    print("\n" + "#" * 70)
    print("VEREDICTO -- ¿el devengo domina y el total es consistentemente positivo?")
    print("#" * 70)
    for m, r in resultados.items():
        signo_total = "positivo" if r["media_total"] > 0 else "negativo"
        devengo_domina = abs(r["media_carry"]) > abs(r["media_direccional"])
        print(f"M={m:>2}d | total={r['media_total']*100:+.4f}% ({signo_total}, t={r['t_stat']:+.2f}) | "
              f"direccional={r['media_direccional']*100:+.4f}% | devengo={r['media_carry']*100:+.4f}% | "
              f"{'devengo domina' if devengo_domina else 'direccional domina'}")
    print("\nNota: esto es la Capa 4 (relación simple), no el veredicto de hypothesis-gate "
          "(walk-forward + t-stat con fold dominante + DSR). Sirve para decidir si hay base "
          "para invertir en el pipeline completo, no reemplaza la Fase 1/Fase 2 del gate.")


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
