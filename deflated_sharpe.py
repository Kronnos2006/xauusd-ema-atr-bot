"""
Probabilistic Sharpe Ratio (PSR) y Deflated Sharpe Ratio (DSR).
=============================================================================
Bailey, D.H. & López de Prado, M. (2014), "The Deflated Sharpe Ratio:
Correcting for Selection Bias, Backtest Overfitting, and Non-Normality".

Por qué esto reemplaza/complementa al t-stat simple (`metrica_robusta`/
`t_stat_pooled` ya usados en el proyecto) para decidir si un resultado es
"significativo": el t-stat sobre R neto asume implícitamente normalidad
de los retornos (razonable con muestras grandes, pero los R-múltiplos de
este proyecto tienen un piso duro en -1.0R por el SL fijo -- asimetría
real, no un supuesto inocuo) y NO corrige por cuántas variantes se
probaron antes de encontrar la que "funciona" (el problema central de
comparaciones múltiples que motivó toda la disciplina de este proyecto).
El DSR corrige ambas cosas explícitamente en vez de dejarlas implícitas.

Dos piezas:
1. PSR(SR*): prueba si el Sharpe observado supera un benchmark SR*,
   corrigiendo por asimetría y curtosis de los retornos y por el tamaño
   de muestra real (no una aproximación normal ciega).
2. DSR: PSR evaluado contra SR* = el Sharpe máximo ESPERADO por azar si
   se hubieran probado N variantes independientes con verdadero SR=0 --
   el benchmark "cuán bueno tendría que verse este resultado para no ser
   sospechoso de haber sido elegido entre N intentos".

Sin scipy (convención del proyecto): usa `statistics.NormalDist`, en la
librería estándar de Python 3.8+.
"""
import math
from statistics import NormalDist

_NORMAL = NormalDist()
EULER_MASCHERONI = 0.5772156649015329


def _skew(retornos):
    n = len(retornos)
    media = sum(retornos) / n
    m2 = sum((r - media) ** 2 for r in retornos) / n
    m3 = sum((r - media) ** 3 for r in retornos) / n
    return m3 / (m2 ** 1.5)


def _kurtosis(retornos):
    """Curtosis NO centrada en 0 (normal = 3.0), como pide la formula
    original de Bailey/Lopez de Prado -- no confundir con "exceso de
    curtosis" (normal = 0.0) que usan otras librerias."""
    n = len(retornos)
    media = sum(retornos) / n
    m2 = sum((r - media) ** 2 for r in retornos) / n
    m4 = sum((r - media) ** 4 for r in retornos) / n
    return m4 / (m2 ** 2)


def sharpe_ratio(retornos):
    n = len(retornos)
    media = sum(retornos) / n
    std = math.sqrt(sum((r - media) ** 2 for r in retornos) / (n - 1))
    return media / std


def probabilistic_sharpe_ratio(retornos, sr_benchmark):
    """PSR(SR*): probabilidad de que el Sharpe VERDADERO supere sr_benchmark,
    dado el Sharpe observado sobre esta muestra -- corrige por asimetria,
    curtosis y tamaño de muestra (formula 2 y 5 de Bailey & Lopez de Prado
    2014)."""
    n = len(retornos)
    sr_hat = sharpe_ratio(retornos)
    skew = _skew(retornos)
    kurt = _kurtosis(retornos)

    denominador = math.sqrt(max(1e-12, 1 - skew * sr_hat + (kurt - 1) / 4 * sr_hat ** 2))
    z = (sr_hat - sr_benchmark) * math.sqrt(n - 1) / denominador
    psr = _NORMAL.cdf(z)
    return psr, sr_hat, skew, kurt


def sharpe_esperado_bajo_multiples_pruebas(n_obs, n_variantes):
    """E[max SR] esperado por azar entre n_variantes intentos independientes
    con SR verdadero = 0 (formula 8 de Bailey & Lopez de Prado 2014).
    Aproxima la varianza del SR estimado por trial como 1/(n_obs-1)
    (SR verdadero=0, retornos ~ normales -- aproximación estándar del
    paper para cuando no se tiene la distribución completa de los N SR)."""
    if n_variantes <= 1:
        return 0.0
    var_sr = 1 / (n_obs - 1)
    std_sr = math.sqrt(var_sr)
    inv_cdf_1 = _NORMAL.inv_cdf(1 - 1 / n_variantes)
    inv_cdf_2 = _NORMAL.inv_cdf(1 - 1 / (n_variantes * math.e))
    return std_sr * ((1 - EULER_MASCHERONI) * inv_cdf_1 + EULER_MASCHERONI * inv_cdf_2)


def deflated_sharpe_ratio(retornos, n_variantes_probadas):
    """DSR: PSR evaluado contra el Sharpe esperado por azar dado el número
    de variantes (grilla de parámetros, hipótesis relacionadas, etc.) que
    se probaron antes de llegar a este resultado. n_variantes_probadas
    tiene que contar TODO lo que se miró antes de elegir esta config --
    ej. el tamaño de la grilla N×M×... de cada fold del walk-forward, no
    solo "1 hipótesis" -- subestimar este número invalida la corrección."""
    sr_benchmark = sharpe_esperado_bajo_multiples_pruebas(len(retornos), n_variantes_probadas)
    dsr, sr_hat, skew, kurt = probabilistic_sharpe_ratio(retornos, sr_benchmark)
    return {
        "sharpe_observado": sr_hat,
        "skewness": skew,
        "kurtosis": kurt,
        "n_variantes_probadas": n_variantes_probadas,
        "sharpe_esperado_por_azar": sr_benchmark,
        "deflated_sharpe_ratio": dsr,
    }


def reportar(resultado, umbral=0.95):
    print(f"Sharpe observado: {resultado['sharpe_observado']:+.4f}")
    print(f"Asimetría (skew): {resultado['skewness']:+.3f} | Curtosis: {resultado['kurtosis']:.3f}")
    print(f"Variantes probadas (N): {resultado['n_variantes_probadas']}")
    print(f"Sharpe esperado por azar con esas N variantes: {resultado['sharpe_esperado_por_azar']:+.4f}")
    print(f"Deflated Sharpe Ratio: {resultado['deflated_sharpe_ratio']:.4f}")
    veredicto = "✅ PASA" if resultado['deflated_sharpe_ratio'] >= umbral else "❌ NO PASA"
    print(f"{veredicto} (umbral DSR ≥ {umbral:.2f}, equivalente a exigir >{umbral*100:.0f}% de "
          f"confianza de que el Sharpe verdadero supera el esperable por puro azar de N pruebas)")
    return resultado['deflated_sharpe_ratio'] >= umbral


if __name__ == "__main__":
    # Ejemplo ilustrativo con los R netos reales de DFII10 (87 trades) y
    # una estimación conservadora de variantes probadas: 9 combinaciones
    # de grilla (N×M) evaluadas por cada uno de los 4 folds = 36, más las
    # 3 hipótesis macro previas descartadas en el camino (2s10s, ratio
    # oro/plata, DXY) que comparten la misma familia de diseño -- 39 en
    # total. Este número es una estimación razonada, no un cálculo exacto;
    # documentar siempre cómo se llegó a N al reportar un DSR.
    import importlib.util
    import sys

    DFII10_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\hipotesis_macro_dfii10.py"
    spec = importlib.util.spec_from_file_location("hipotesis_macro_dfii10", DFII10_PATH)
    hip = importlib.util.module_from_spec(spec)
    sys.modules["hipotesis_macro_dfii10"] = hip
    spec.loader.exec_module(hip)
    mod = hip.mod

    df_dfii10 = hip.cargar_dfii10()
    df_oro = hip.bajar_oro_diario()
    folds = mod.construir_bloques_walk_forward(df_oro, hip.N_FOLDS)
    resultados = [hip.correr_fold_macro(df_dfii10, train, test, i, hip.N_FOLDS)
                  for i, (train, test) in enumerate(folds, start=1)]
    validos = [r for r in resultados if r.get("n_trades_test")]
    import pandas as pd
    todos = pd.concat([r["td_test"] for r in validos], ignore_index=True)
    todos = mod.descontar_spread(todos)
    retornos = todos["resultado_R_neto"].tolist()

    print("\n" + "=" * 70)
    print("DEFLATED SHARPE RATIO -- DFII10, 87 trades TEST, N=39 variantes estimadas")
    print("=" * 70)
    resultado = deflated_sharpe_ratio(retornos, n_variantes_probadas=39)
    reportar(resultado)
