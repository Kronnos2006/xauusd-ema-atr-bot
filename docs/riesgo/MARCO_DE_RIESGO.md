# Marco de riesgo

- **Versión:** v1.0 · **Fecha:** 2026-10-21 · **Autor:** jefe-riesgo (independiente)
- **Escrito antes** de cualquier estrategia, simulación o resultado del libro de portafolio (`docs/portafolio/estrategias/` y `hipotesis/` vacíos a esta fecha).
- **Quién puede cambiarlo:** solo el usuario, por mensaje explícito. Cada cambio sube la versión y queda en la tabla "Historial" del final. El gerente, el jefe de portafolio y el mejorador no pueden cambiarlo.
- **Alcance:** toda simulación en papel o propuesta que implique posiciones (compras, ventas, tamaños). Las mediciones descriptivas (KT-002, KT-003) no toman posiciones y quedan fuera.

## 1. Base de cálculo

- Todos los límites se expresan en **% del capital de la simulación** (capital en papel declarado en el registro previo). Si no se declara, se usa **10 000 USDT** en papel.
- El patrimonio se marca a mercado con el cierre de cada vela del horizonte de la estrategia, y como mínimo una vez por día UTC.
- "Día" = día UTC; "semana" = lunes 00:00 a domingo 23:59 UTC.

## 2. Límites de pérdida

| Límite | Valor | Qué pasa si se toca |
|---|---|---|
| Pérdida máxima por operación (riesgo hasta el stop, con costos) | 0,5 % | Una operación sin stop definido o con riesgo mayor no se aprueba |
| Pérdida máxima por día | 1,0 % | Se cierran todas las posiciones y no se abren nuevas hasta el día siguiente |
| Pérdida máxima por semana | 2,5 % | Se cierran todas y no se opera hasta la semana siguiente |
| Pérdida máxima por mes calendario | 5,0 % | Se cierran todas; revisión obligatoria del jefe de riesgo antes de seguir |
| **Pérdida total (caída desde el máximo del patrimonio)** | **10 %** | **Apagado** (sección 5). No se reactiva sin OK del jefe de riesgo y del usuario |

Las pérdidas se cuentan **netas de costos** (comisión, spread, deslizamiento, financiamiento) e incluyen lo no realizado.

## 3. Tamaño y exposición

| Límite | Valor |
|---|---|
| Apalancamiento | **1x** (sin préstamo). Futuros, margen o ventas en corto: no aprobables hasta que `riesgo-costos` mida su financiamiento y el usuario lo autorice |
| Tamaño máximo por posición (nominal) | 25 % del capital |
| Exposición bruta total (suma de nominales) | 100 % del capital |
| Exposición en un mismo instrumento (sumando estrategias) | 50 % del capital |
| Volatilidad objetivo del portafolio | ≤ 10 % anual (vol realizada 60 días, retornos diarios) |
| Número máximo de posiciones abiertas | 8 |
| Liquidez | Orden ≤ 1 % del volumen medio de 1 h del instrumento (si no, el deslizamiento medido no vale) |

## 4. Correlación

- Medida: correlación de Pearson de retornos diarios, ventana 60 días, publicada con fecha y fuente.
- Dos posiciones con **ρ > 0,70** cuentan como **una sola** para el límite de 25 % por posición.
- Correlación media del portafolio **≤ 0,50**; si se supera, se reduce exposición hasta volver al límite.
- **N efectivo** (Meucci / por autovalores) **≥ 2** para que un portafolio de varias posiciones se apruebe como "diversificado". Precedente del proyecto: TF_Basket_H1 tuvo N_ef = 4,40 de 10.
- Si no hay 60 días de historia: se asume ρ = 1 (peor caso).

## 5. Apagado inmediato ("kill switch")

Cualquiera de estas condiciones apaga la simulación (todas las posiciones a cero, no se abren nuevas). La marco como **APAGADA** en `docs/riesgo/REGISTRO_DE_REVISIONES.md` y aviso al gerente y al usuario.

1. Caída desde el máximo ≥ 10 %.
2. Se rompe cualquier límite de las secciones 2–4 y no se corrige en la vela siguiente.
3. **Costos reales > 1,5 veces los costos modelados**, medidos sobre las últimas 20 operaciones (o todas, si hay menos).
4. **Datos viejos o rotos:** falta más de 2 velas seguidas del horizonte, o el vigía de datos marca hueco/duplicado/hash inválido en los datos que alimentan la señal.
5. **Racha de pérdidas** mayor al percentil 99 de la simulación validada (o, sin esa referencia, 8 pérdidas seguidas).
6. **Desvío del registro previo:** cualquier cambio de regla, parámetro, instrumento u horizonte no registrado antes.
7. Evento de mercado extremo: movimiento de 1 h del instrumento > 5 desviaciones de su vol de 30 días, o mercado suspendido / exchange con retiros frenados.
8. Veto del desconfiado sobre el diseño o los datos.

**Reactivación:** solo con OK escrito del jefe de riesgo **y** del usuario, tras causa documentada.

## 6. Requisitos obligatorios para aprobar una simulación

Sin todos estos puntos el veredicto es **RECHAZADO** (no "con condiciones"):

1. **Registro previo** con commit/hash, fecha anterior a ver resultados, y paso por `hypothesis-gate` (Fase 0 y Fase 1).
2. **Costos completos de ida y vuelta** por instrumento, medidos por `riesgo-costos` con fecha y fuente: comisión, spread, deslizamiento para el tamaño de orden declarado y financiamiento si aplica. Lo no medido se carga en el **peor caso razonable** (sección 7).
3. **Resultado neto de costos positivo** con el costo base **y no negativo con costos x2** (prueba de estrés).
4. Piso de **30 operaciones por fold**, t-stat con y sin el fold dominante, y **DSR ≥ 0,95** contando todas las variantes realmente probadas (regla del proyecto).
5. **Caída máxima simulada ≤ 6,5 %** (dos tercios del límite total), para dejar margen a que lo real sea peor.
6. Tamaño de orden declarado y compatible con la liquidez (sección 3).
7. Datos auditados por `vigia-datos` y diseño aprobado por el `desconfiado` sin problemas ALTOS.
8. Cumple todos los límites de las secciones 2–4 en toda la simulación, no solo en promedio.

## 7. Costos: supuestos de peor caso vigentes (hasta medición)

| Instrumento | Componente | Valor provisional | Estado | Fuente |
|---|---|---|---|---|
| BTCUSDT spot | Comisión | 0,10 % por lado (taker, usuario regular, sin BNB) | Publicado | Tabla Binance consultada 2026-10-16 (`docs/BTCUSDT_Fase_0_borrador.md`) |
| BTCUSDT spot | Spread efectivo | 0,02 % por lado | **SUPUESTO** peor caso | Pendiente `riesgo-costos` |
| BTCUSDT spot | Deslizamiento | 0,03 % por lado | **SUPUESTO** peor caso | Pendiente `riesgo-costos` |
| BTCUSDT spot | Financiamiento | 0 (spot sin apalancamiento) | Por construcción | — |
| **BTCUSDT spot** | **Ida y vuelta total** | **0,30 %** | Provisional | Suma de lo anterior |
| Otros | Todo | No aprobables hasta medición | — | — |

Precedente del proyecto que justifica la severidad: en Salida 2 (2026-08-06) los costos reales (spread + swap) se comieron 603,7 % del retorno bruto y el Sharpe neto quedó en −0,27.

## 8. Dinero real

**Nunca** sin, todos a la vez: (a) resultado que pase su registro previo, (b) simulación en papel con costos positiva, (c) aprobación del jefe de riesgo, (d) aprobación del desconfiado, (e) decisión explícita del usuario. Si llega a plantearse, este marco se reescribe con el usuario para capital real (límites en dinero, no solo en %) **antes** de cualquier orden.

## Historial

| Versión | Fecha | Cambio | Autorizó |
|---|---|---|---|
| v1.0 | 2026-10-21 | Versión inicial, antes de cualquier estrategia | jefe-riesgo (creación aprobada por el usuario 2026-10-21) |
