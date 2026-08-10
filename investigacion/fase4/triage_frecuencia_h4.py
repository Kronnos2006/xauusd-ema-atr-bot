"""
Triage de frecuencia (Fase 0 de hypothesis-gate) para H4 -- Carry FX.

H4 NO es un sistema de trades discretos (entrada/salida con R-multiple por
señal) como DFII10, DXY sintético o ratio oro/plata -- es un portfolio de
rebalanceo mensual, siempre invertido (long 3 / short 3 / flat 3), evaluado
por Sharpe anualizado sobre retornos diarios. Los tamaños de efecto típicos
ya catalogados en triage_frecuencia.EFECTOS_OBSERVADOS (media R ~0.18-0.23,
std R ~1.1) son R-multiples por trade discreto -- no son dimensionalmente
comparables a un Sharpe de portfolio. Aplicarlos tal cual sería un error de
unidades, no un triage válido.

Para un test de Sharpe anualizado con retornos ~iid, la potencia estadística
depende de los AÑOS de datos, no de la frecuencia de rebalanceo -- rebalancear
mensual vs. semanal no cambia cuántos años hacen falta para separar una señal
de Sharpe S del ruido, porque el propio Sharpe ya está normalizado por
frecuencia. Formalmente (mismo z_alpha/z_beta que usa n_necesario_80_poder):

    años_necesarios = ((z_alpha + z_beta) / Sharpe_típico) ** 2

Esto es un caso particular de n_necesario_80_poder() de triage_frecuencia.py
con episodios_por_anio=1 y media_r/std_r expresados en unidades anuales
(media_r = Sharpe_típico, std_r = 1) -- se usa la misma función, no una
fórmula nueva.

Tamaño de efecto típico elegido: el precedente de diseño MAS CERCANO en este
proyecto no es ninguna de las hipótesis macro basadas en trades -- es H3
(momentum cross-sectional FX), que comparte EXACTAMENTE el mecanismo de H4:
mismas 9 monedas, mismos buckets 3 long / 3 short / 3 flat, mismo rebalanceo
mensual, mismo modelo de costos. Los 3 Sharpe anualizados de H3 en Train
(2005-2014, el período con más datos) fueron +0.111 (N20... en realidad N60),
+0.276 (N20) y -0.215 (N120) -- rango [-0.22, +0.28], magnitud promedio
~0.20. Se usa Sharpe_típico=0.20 como referencia (y, a título ilustrativo,
también el propio objetivo de H4 de Sharpe>0.50, aunque la Fase 0 prohíbe
usar el efecto de la hipótesis candidata como el efecto típico -- se muestra
solo para contraste).
"""
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from triage_frecuencia import n_necesario_80_poder, HORIZONTE_LIMITE_ANIOS


def triage_sharpe(nombre_hipotesis, sharpe_tipico, horizonte_limite_anios=HORIZONTE_LIMITE_ANIOS):
    n_anios = n_necesario_80_poder(media_r=sharpe_tipico, std_r=1.0)
    print(f"=== Triage de frecuencia (basado en Sharpe anual): {nombre_hipotesis} ===")
    print(f"Sharpe típico asumido: {sharpe_tipico:+.3f}")
    print(f"Años necesarios para 80% de poder (alpha=0.05, dos colas): {n_anios}")
    if n_anios > horizonte_limite_anios:
        print(f"❌ DESCARTADO EN EL TRIAGE -- horizonte proyectado ({n_anios} años) "
              f"supera el límite ({horizonte_limite_anios} años).\n")
        return False
    else:
        print(f"✅ Pasa el triage -- horizonte proyectado dentro de {horizonte_limite_anios} años.\n")
        return True


def mde_sharpe(anios_disponibles, alpha=0.05, poder_objetivo=0.80):
    """Minimum Detectable Effect: dado T años de datos, ¿cuál es el Sharpe
    verdadero MÁS CHICO que ese tamaño de muestra podría distinguir del ruido
    con el poder objetivo? Inverso de n_necesario_80_poder(): no requiere
    asumir NINGÚN Sharpe típico -- solo el número de años, que es un dato
    fijo (no una hipótesis). Agregado 2026-08-09 tras revisión del usuario:
    la versión "años necesarios para Sharpe=X" depende de adivinar X: esta
    versión da vuelta la pregunta y elimina esa dependencia."""
    z_alpha = 1.959963985
    z_beta = 0.841621234
    return (z_alpha + z_beta) / (anios_disponibles ** 0.5)


if __name__ == "__main__":
    # Referencia primaria: precedente de diseño más cercano (H3, mismo mecanismo exacto)
    triage_sharpe("H4-carry, efecto típico = precedente H3 (Sharpe~0.20)", sharpe_tipico=0.20)

    # Contraste ilustrativo, NO válido como triage per Fase 0 (usa el objetivo
    # de la propia hipótesis candidata como si fuera un efecto típico externo)
    print("--- contraste ilustrativo, no es el triage válido ---")
    triage_sharpe("H4-carry, usando su propio objetivo (Sharpe>0.50) -- solo referencia", sharpe_tipico=0.50)

    # MDE -- no depende de asumir ningún Sharpe, solo de los años realmente
    # disponibles. Ver discusión 2026-08-09 en README.md.
    print("--- MDE (Sharpe mínimo detectable), sin asumir ningún efecto típico ---")
    for anios, label in [(5, "Validation 2015-2019 (la ventana real de decisión)"),
                          (10, "Train 2005-2014"),
                          (15, "Train+Validation combinados")]:
        print(f"{label}: T={anios} años -> Sharpe mínimo detectable (80% poder, alpha=0.05) = {mde_sharpe(anios):.3f}")
    print("Criterio A pre-registrado de H4: Sharpe > 0.50 -- por debajo del MDE en las 3 ventanas.")
