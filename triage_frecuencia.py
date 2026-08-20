"""
Triage de frecuencia -- el filtro MAS BARATO de hypothesis-gate, corre
ANTES de escribir un solo backtest completo.

Lección de DFII10 (2026-07-27): la hipótesis pasó el checkpoint
exploratorio, sobrevivió una auditoría completa de robustez (spread,
look-ahead, métricas), y solo al final -- después de todo ese trabajo --
el power analysis reveló que confirmarla sola necesitaría ~13 años más
de holdout. Ese cálculo se podría haber hecho en 5 minutos, con la
frecuencia de episodios ya conocida y un tamaño de efecto típico de este
proyecto, ANTES de construir el pipeline completo (walk-forward, folds,
simulación de trades). Este script formaliza ese chequeo para que sea
lo primero que se corre con cualquier candidato nuevo, no lo último.

Uso: correr el chequeo de frecuencia liviano de la hipótesis candidata
(mismo patrón que diagnostico_frecuencia_dfii10.py / _dxy.py /
_ratio_oro_plata.py -- contar episodios/año sobre el histórico
disponible, SIN simular un solo trade todavía), y pasar ese número acá
junto con un tamaño de efecto típico (o el de la hipótesis más cercana
ya evaluada, si hay una razón para esperar un efecto similar).
"""
import sys
import math

sys.stdout.reconfigure(encoding="utf-8")

# Tamaños de efecto ya observados en este proyecto, para referencia --
# NO usar automáticamente el más optimista: usar el que corresponda por
# similitud de diseño con la hipótesis candidata, y documentar por qué.
EFECTOS_OBSERVADOS = {
    "DFII10 (macro diario, N=60/M=5)": {"media_R": 0.230, "std_R": 1.135},
    "Ratio oro/plata (macro diario)": {"media_R": 0.210, "std_R": None},  # ver Ratio oro-plata - fase 1.md
    "DXY sintético (macro diario)": {"media_R": 0.182, "std_R": None},
}

HORIZONTE_LIMITE_ANIOS = 5  # regla de corte: por encima de esto, se descarta en el triage


def n_necesario_80_poder(media_r, std_r, alpha=0.05, poder_objetivo=0.80):
    """n para detectar, con poder_objetivo, un efecto de esta magnitud --
    misma formula ya usada en metricas_dfii10.py, generalizada acá."""
    z_alpha = 1.959963985   # alpha=0.05, dos colas
    z_beta = 0.841621234    # poder=0.80
    return math.ceil(((z_alpha + z_beta) * std_r / media_r) ** 2)


def triage(nombre_hipotesis, episodios_por_anio, media_r_tipica, std_r_tipico,
           horizonte_limite_anios=HORIZONTE_LIMITE_ANIOS):
    n_necesario = n_necesario_80_poder(media_r_tipica, std_r_tipico)
    anios_proyectados = n_necesario / episodios_por_anio

    print(f"=== Triage de frecuencia: {nombre_hipotesis} ===")
    print(f"Frecuencia estimada: {episodios_por_anio:.2f} episodios/año")
    print(f"Efecto típico asumido: media R={media_r_tipica:+.3f}, std R={std_r_tipico:.3f}")
    print(f"n necesario para 80% de poder (alpha=0.05, dos colas): {n_necesario}")
    print(f"Horizonte proyectado DESDE CERO (sin datos previos, el escenario real al hacer "
          f"este triage antes de cualquier holdout): {anios_proyectados:.1f} años")

    if anios_proyectados > horizonte_limite_anios:
        print(f"\n❌ DESCARTADO EN EL TRIAGE -- horizonte proyectado ({anios_proyectados:.1f} años) "
              f"supera el límite ({horizonte_limite_anios} años). No se construye el pipeline completo.")
        return False
    else:
        print(f"\n✅ Pasa el triage de frecuencia -- horizonte proyectado dentro de {horizonte_limite_anios} años. "
              f"Procede a hypothesis-gate Fase 1 (frase falsable + regla de corte + folds derivados).")
        return True


if __name__ == "__main__":
    # Ejemplo: re-chequear DFII10 con esta herramienta, para confirmar que
    # hubiera capturado el problema si hubiera existido antes.
    triage("DFII10 (retrospectivo, para validar la herramienta)",
           episodios_por_anio=8, media_r_tipica=0.230, std_r_tipico=1.135)
