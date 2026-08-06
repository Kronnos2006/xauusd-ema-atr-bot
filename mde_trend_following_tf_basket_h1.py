"""
Fase 0 (recalculo) -- TF_Basket_H1. Reemplaza el efecto de referencia
DFII10 (mismatch de diseño, señalado en la corrida anterior) por un
efecto derivado de la propia ficha de la hipótesis, según instrucción
del usuario (2026-08-06):

    Sharpe objetivo OOS anual = 0.3
    Vol objetivo cartera anual = 15%
    Retorno esperado anual = Sharpe * Vol = 0.3 * 15% = 4.5%
    media_r (retorno esperado por trade) = retorno anual / N (ep/año)

std_r (por trade) no fue dado explícito -- se deriva de la misma
relación de escalamiento de Sharpe que ya implica el propio Sharpe
objetivo: si los N trades/año fueran i.i.d., Sharpe_anual =
Sharpe_trade * sqrt(N) (escalamiento estándar raíz-de-N). De ahí:

    Sharpe_trade = Sharpe_anual / sqrt(N)
    std_r = media_r / Sharpe_trade = media_r * sqrt(N) / Sharpe_anual

Reusa n_necesario_80_poder() de triage_frecuencia.py, sin reimplementar
la fórmula.
"""
import sys
import math

sys.path.insert(0, r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta")
from triage_frecuencia import n_necesario_80_poder, HORIZONTE_LIMITE_ANIOS

sys.stdout.reconfigure(encoding="utf-8")

SHARPE_OBJETIVO_ANUAL = 0.3
VOL_OBJETIVO_ANUAL = 0.15
RETORNO_ESPERADO_ANUAL = SHARPE_OBJETIVO_ANUAL * VOL_OBJETIVO_ANUAL  # 4.5%

# Ep/año basket (pooled, ver diagnostico_frecuencia_tf_basket_h1.py,
# corrida 2026-08-06) para las 2 señales que pasaron el triage original
SEÑALES = {
    "Donchian 20": 79.91,
    "MA 10/50": 69.89,
}


def main():
    print(f"Retorno esperado anual = Sharpe {SHARPE_OBJETIVO_ANUAL} x Vol {VOL_OBJETIVO_ANUAL:.0%} "
          f"= {RETORNO_ESPERADO_ANUAL:.4%}\n")

    print(f"{'Señal':<14} {'N (ep/año)':>11} {'media_r/trade':>15} {'Sharpe_trade':>13} "
          f"{'std_r/trade':>13} {'n necesario':>12} {'horizonte (años)':>18} {'veredicto':>12}")

    for nombre, n_epano in SEÑALES.items():
        media_r = RETORNO_ESPERADO_ANUAL / n_epano
        sharpe_trade = SHARPE_OBJETIVO_ANUAL / math.sqrt(n_epano)
        std_r = media_r / sharpe_trade
        n_necesario = n_necesario_80_poder(media_r, std_r)
        horizonte = n_necesario / n_epano
        veredicto = "DESCARTA" if horizonte > HORIZONTE_LIMITE_ANIOS else "PASA"
        print(f"{nombre:<14} {n_epano:>11.2f} {media_r:>14.5%} {sharpe_trade:>13.5f} "
              f"{std_r:>12.4%} {n_necesario:>12} {horizonte:>18.1f} {veredicto:>12}")

    print("\nNota: años_necesarios = n_necesario / N = ((z_alpha+z_beta)/Sharpe_anual)^2, "
          "constante e independiente de N -- el escalamiento raíz-de-N usado para derivar "
          "std_r cancela exactamente la N al dividir n_necesario por N. Esto es un resultado "
          "esperado de este método (no un bug): confirmar un Sharpe anual S con un t-test de "
          "esta forma siempre requiere ~((z_alpha+z_beta)/S)^2 años, sin importar la frecuencia "
          "de trading.")
    anios_teoricos = ((1.959963985 + 0.841621234) / SHARPE_OBJETIVO_ANUAL) ** 2
    print(f"Verificación directa: ((1.96+0.84)/{SHARPE_OBJETIVO_ANUAL})^2 = {anios_teoricos:.1f} años")


if __name__ == "__main__":
    main()
