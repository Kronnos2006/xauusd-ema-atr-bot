---
name: factor-independence
description: Evalúa si 2 o más factores/señales candidatas a combinar son genuinamente independientes (no solo estadísticamente descorrelacionadas en promedio) antes de sumarlas a la biblioteca de factores del proyecto, y define la única forma permitida de combinarlos. Usar en cuanto haya 2+ factores que pasaron (o pasaron con reservas) hypothesis-gate y se esté considerando combinarlos.
---

# Factor Independence

El objetivo del proyecto (desde 2026-07-27, ver `Objetivo del proyecto - biblioteca de factores` en el vault) es construir una biblioteca de factores independientes de baja correlación, no encontrar una sola señal fuerte. Un factor débil individualmente (como [[Macro DFII10 - fase 1]], que pasa `hypothesis-gate` con reservas) solo aporta valor real a esa biblioteca si además de tener un edge propio, aporta algo que los demás factores no aportan. Este skill es el filtro para esa segunda pregunta — no reemplaza a `hypothesis-gate`, corre DESPUÉS de que cada factor individualmente ya lo pasó.

## Cuándo correr esto

Solo cuando hay **2 o más factores candidatos**, cada uno ya evaluado por separado con `hypothesis-gate`. No tiene sentido correrlo con un solo factor (no hay nada que comparar) ni antes de que un factor tenga su propio veredicto.

## Los cuatro chequeos, en orden

### 1. Correlación de Spearman de los retornos

Sobre una grilla temporal común (no las fechas de trade de cada señal por separado — hay que resamplear ambas a un calendario compartido, ej. diario, con retorno 0 en los períodos sin posición abierta). Spearman, no Pearson — los R-múltiplos de este proyecto no son normales (ver `deflated_sharpe.py` en `hypothesis-gate`, que ya mide skew/curtosis reales), y Spearman no asume linealidad ni normalidad.

Umbral de referencia: correlación absoluta < 0.3 es "razonablemente independiente"; entre 0.3 y 0.5, zona gris a documentar con el racional económico (punto 4); > 0.5, tratar como el mismo factor a efectos prácticos, no como dos.

### 2. Correlación CONDICIONAL en el decil inferior de drawdown — el test que realmente importa

La correlación promedio (punto 1) puede ser baja y aun así esconder el problema real: **las correlaciones entre activos/factores suelen subir justo cuando más duele** (crisis, eventos de liquidez, shocks macro) — que es exactamente cuando la diversificación tiene que funcionar y a menudo no lo hace. Medirlo así:

1. Para cada señal, identificar el decil de peores retornos (el 10% de períodos con peor P&L de esa señal individual).
2. Calcular la correlación de Spearman entre las señales **restringida a esos períodos** (la unión o intersección de los deciles inferiores de cada señal, documentar cuál de las dos se usó).
3. Comparar contra la correlación incondicional del punto 1. **Si la correlación condicional es sustancialmente mayor que la incondicional, la diversificación es ilusoria** — dos factores que parecen independientes en promedio pueden fallar juntos exactamente cuando se los necesita.

No hay un umbral único publicado para esto — reportar ambos números (incondicional y condicional) siempre juntos, nunca uno sin el otro, y tratar una suba grande (aprox. el doble o más) como señal de alerta a documentar explícitamente, no a promediar/ignorar.

### 3. PCA sobre las señales — detectar factor latente compartido

Con 3 o más factores candidatos (con 2 el PCA no aporta más que la correlación simple del punto 1), correr un análisis de componentes principales sobre la matriz de retornos alineados (misma grilla temporal del punto 1). Si un solo componente principal explica una fracción grande de la varianza conjunta (no hay un umbral universal — como referencia, >60-70% en el primer componente es señal fuerte), es evidencia de que varias señales son expresiones del mismo factor de riesgo subyacente, no factores independientes.

Ejemplo concreto de este proyecto: DFII10 (tasas reales), un eventual DXY, y el spread de tasas (2s10s, ya descartado como señal propia pero relevante acá como *ejemplo de razonamiento*) son todas, en el fondo, expresiones del mismo régimen de política monetaria de la Fed. Combinarlas sin este chequeo podría verse como "3 factores" cuando en realidad aportan la misma información una vez controlado por el primer componente principal.

### 4. Chequeo de racional económico independiente — no solo estadístico

Los tres chequeos de arriba son estadísticos y pueden fallar por razones espurias de muestra chica (con pocos años de datos, una correlación baja puede ser casualidad tanto como una señal real de independencia). Antes de aceptar dos factores como independientes, escribir explícitamente **por qué mecanismos económicos distintos** explican cada uno — si la respuesta es "ambos capturan expectativas de tasas de la Fed, solo que con proxies distintos", no son independientes aunque la correlación numérica dé baja esta vez. Este chequeo cualitativo tiene poder de veto sobre los tres estadísticos: un racional económico claramente solapado descarta la combinación aunque los números den bien.

## Regla de combinación — la única permitida en esta etapa del proyecto

Una vez que 2+ factores pasan los cuatro chequeos de arriba:

- **Primero, pesos iguales.** Es el punto de partida por defecto, no una opción entre varias.
- **Como mucho, risk-parity** (peso inversamente proporcional a la volatilidad de cada factor) — nunca más sofisticado que eso.
- **NUNCA optimización de pesos** (mean-variance, Kelly, o cualquier método que ajuste pesos maximizando una métrica sobre estos datos) — con el tamaño de muestra que maneja este proyecto (decenas a pocos cientos de trades por factor), cualquier optimización de pesos es sobreajuste garantizado, el mismo problema de fondo que ya motivó toda la disciplina de walk-forward. Esto no es negociable por "esta vez parece que mejora el resultado".

### Los tres bloques de datos para elegir el método de combinación

Igual que el walk-forward de cada hipótesis individual (TRAIN elige, TEST confirma una sola vez), pero un nivel arriba, sobre la combinación:

1. **TRAIN**: donde cada señal individual ya fue ajustada (esto ya pasó, en el `hypothesis-gate` de cada factor por separado — no se vuelve a tocar acá).
2. **VALIDATION**: se elige el método de combinación (pesos iguales vs. risk-parity) — la ÚNICA decisión que se permite tomar mirando datos en esta etapa, y solo entre esas dos opciones, nunca optimizando valores continuos de pesos.
3. **TEST**: veredicto único, una sola vez, con el método ya elegido en VALIDATION — mismo principio de "una sola pasada" que el resto del proyecto.

## Qué hacer con el resultado

- Si los 4 chequeos dan bien (correlación incondicional y condicional bajas, sin componente principal dominante, racional económico distinto): combinar con pesos iguales o risk-parity, evaluar en TEST una sola vez.
- Si cualquiera de los 4 chequeos falla: no combinar. Documentar cuál falló y por qué en la nota de vault correspondiente — sigue siendo información útil (ej. "DFII10 y DXY no diversifican entre sí, ambos van a la misma canasta de política monetaria").

## Por qué importa

El objetivo del proyecto cambió justamente porque ninguna señal individual alcanzó la barra de "fuerte por sí sola" — la apuesta ahora es que la SUMA de factores débiles-pero-independientes puede superar a cualquiera de ellos solo. Esa apuesta se rompe si los factores "independientes" en realidad no lo son — combinar dos versiones del mismo riesgo no reduce nada, solo da la ilusión de diversificación hasta el día que todos fallan juntos.
