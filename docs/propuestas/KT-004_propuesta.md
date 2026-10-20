# KT-004 — propuesta v2: confirmación prospectiva del acierto balanceado de Kronos, TimesFM y KT-001

2026-10-20, Costa Rica. Autor: agente `mejorador`. Estado: **PROPUESTA v2**, corrige el RECHAZO de `desconfiado` a la v1. Sin OK del usuario. No se registró nada, no se tocó KT-002 ni KT-003 y el evaluador solo se probó con datos sintéticos.

Cambio de fondo respecto de la v1, por decisión del usuario: **TimesFM no sale de la prueba**. La familia confirmatoria vuelve a tener los 3 modelos (Kronos, TimesFM, KT-001) con Holm. El ajuste para mejorar TimesFM va aparte, en `docs/propuestas/KT-005_propuesta.md`.

## 0. Qué cambié por cada punto del desconfiado

| Gravedad | Punto | Qué cambié |
|---|---|---|
| ALTA | La guarda «acierto bruto > 4 referencias triviales» equivale a superar max(p_sube, 1−p_sube, p_rev, 1−p_rev), reintroduce la deriva y la potencia cae a 0,35–0,86 | **Quité la guarda.** La regla de aprobado es solo la métrica primaria (acierto balanceado > 50 %). Las 4 referencias quedan descriptivas. Simulé la regla nueva (bootstrap por bloques + Holm, n = 1310) con tasa de subida 45 %, 50 % y 55 %: tamaño real 0,6–1,2 % (nominal 0,83 % en el escalón más exigente de Holm) y potencia 0,88–0,89 con acierto balanceado 55 %, 0,69–0,72 con 54 %. La tasa de subida ya no mueve la potencia (§5). |
| MEDIA | Ganar a «reversión» por 0,1 pt no descarta reversión | Ya no se afirma que se descarte. Lo único que KT-004 puede concluir es "el modelo distingue subidas de bajadas mejor que una moneda". El acierto cuando coincide o no con la reversión se informa como **descriptivo**, sin prueba y sin efecto sobre el veredicto (§4). |
| MEDIA | Reversión y tasa de subida varían por hora base; el efecto de planificación salió solo de 00:00 UTC | Declarado con números (§1.3). La potencia se informa también con un efecto menor (54 %) por si el efecto se diluye al mezclar 6 horas. Se informa el acierto balanceado por hora, solo descriptivo; no se agregan cortes por hora a la regla. |
| MEDIA | Persistencia/reversión no se pueden calcular unívocamente con KT-002 | Fuente fijada: cierre de B−4h de los **ZIP oficiales de data.binance.vision con .CHECKSUM**. Si falta esa vela, la base se excluye de las referencias descriptivas, **no** de la métrica primaria. Escribí el evaluador y 17 pruebas sintéticas con huecos (§8). |
| MEDIA | Bootstrap no especificado | Especificado completo y reproducible (§4): filas ordenadas por `base_open_utc`, bloques circulares de 42 filas, 10 000 réplicas, `numpy.random.default_rng(42)`, una sola matriz de índices compartida por los 3 modelos, versiones fijadas y comprobadas por el evaluador. |
| MEDIA | Congelar KT-002 como fuente | SHA-256 completos fijados (§6). El evaluador aborta si cambian, si hay commits que los toquen después del registro, si `kt002.yml` deja de fijar torch/Kronos/pesos, si algún pronóstico ya escrito se borra o cambia (`git log -p`), o si `base_close`/`actual_ret` difieren de los ZIP en más de 1e-9. Vigía de cobertura a los 7 días. |
| BAJA | Inicio y qué pasa si en la fecha límite n < 1000 | T_registro = fecha del commit del registro tal como queda en `origin/master`; regla estricta `base_open_utc > T_registro`. Fecha límite y n mínimo definidos (§5). |
| BAJA | Con TimesFM, familia de 3 con Holm | Recalculado: n ≈ 1047 independientes, **1310** con factor 1,25; ≈ 218 días al 100 % de cobertura, ≈ 273 días al 80 % (§5). |

## 1. Evidencia (post hoc, datos ya vistos)

Fuente: `data/kt003/predicciones.csv` (842 bases post corte, una por día a las 00:00 UTC) y `data/kt003/btcusdt_1h.csv.gz`. Scripts: `/tmp/claude-0/-home-claude/14241745-63d7-59dc-a6ae-501840d3a10b/scratchpad/mejorador/a1.py`, `a2.py`, `a3.py`, `a4.py`, `tfm_diag.py` y `tfm_diag2.py`. KT-002 tiene 4 pronósticos y 1 vencido: no aporta nada todavía.

### 1.1 Resumen por modelo (post corte, n = 842)

| | Acierto | Acierto balanceado | Dice «sube» |
|---|---|---|---|
| Kronos | 56,8 % | 56,9 % | 42,9 % |
| TimesFM | 48,7 % | 48,7 % | 52,1 % |
| KT-001 | 55,5 % | — | — |
| «siempre sube» / «persistencia» / «reversión» 4 h | 50,9 % / 48,5 % / 51,5 % | — | — |

KT-003 (primario, McNemar contra «siempre sube» con Holm): ninguno significativo (Kronos p Holm 0,086).

### 1.2 Lo que motiva usar acierto balanceado

Kronos dice «baja» el 57 % de las veces. El acierto bruto premia o castiga ese sesgo según si el mercado sube o baja en el período, y eso no es capacidad de predecir. El acierto balanceado (promedio entre el acierto en bases que suben y en bases que bajan) vale 50 % para cualquier regla que no mire los datos, tenga el sesgo que tenga. Por eso basta compararlo con 50 % y no hace falta ninguna guarda contra «siempre sube» o «siempre baja».

### 1.3 Variación por hora base (pedido del desconfiado)

Mismos días post corte, 6 horas sin solape (`desconfiado/hora.py`):

| Hora UTC | 0 | 4 | 8 | 12 | 16 | 20 |
|---|---|---|---|---|---|---|
| Tasa de subida a 4 h | 51,0 % | 51,9 % | 50,5 % | 48,5 % | 52,4 % | 49,9 % |
| «reversión» acierta | 51,5 % | 52,0 % | 52,0 % | 48,5 % | 53,4 % | 57,7 % |

El efecto de planificación de Kronos salió **solo de las 00:00 UTC**. KT-002 mezcla las 6 horas por partes iguales, así que si el efecto de Kronos depende de la hora, el promedio puede ser menor que en KT-003. Lo asumo: la potencia se informa también con 54 %, y el reporte final mostrará el acierto balanceado por hora como descriptivo, sin poder de decisión.

### 1.4 Advertencias

(a) Kronos fue el mejor de 3 modelos en el mismo período donde se mide (maldición del ganador). (b) El post corte no está certificado como fuera del entrenamiento (Enmienda C de KT-003), sobre todo para TimesFM. (c) Todo esto se calculó después de ver los resultados. Nada es confirmatorio.

## 2. Cambio exacto

No se cambia ningún modelo ni parámetro. KT-004 es un **análisis pre-registrado** sobre los pronósticos que KT-002 ya hace, sin modificar KT-002:

1. Familia confirmatoria: **Kronos, TimesFM y KT-001**, con la configuración y las revisiones de KT-002 (TimesFM sigue, por decisión del usuario).
2. Métrica: acierto balanceado en lugar de acierto bruto; sin guardas.
3. Datos: solo bases de KT-002 sin solape posteriores al registro de KT-004.
4. Un evaluador nuevo (`tools/kt004_evaluar.py`) que se corre **una sola vez**, al final.

## 3. Hipótesis falsable

Para cada modelo m ∈ {Kronos, TimesFM, KT-001}:

- H1_m: en BTCUSDT 1h, sobre bases prospectivas sin solape, el signo del retorno previsto a 4 h por m tiene **acierto balanceado > 50 %**.
- H0_m: acierto balanceado ≤ 50 %.

Lo que **no** se prueba: que el acierto no venga de una regla simple como la reversión, ni que sirva para operar.

## 4. Métrica primaria y regla de aprobado

**Muestra.** Filas de `data/kt002/predicciones.csv` con:
- `base_open_utc > T_registro` (estricto) y hora UTC de la base múltiplo de 4;
- si una base aparece repetida, cuenta la fila con `run_utc` más temprano;
- con `actual_ret` ya puntuado; se descartan r = 0;
- por modelo se descartan las filas con r̂ = 0 (como KT-002).

Se ordenan por `base_open_utc` y se toman las **primeras 1310 puntuadas válidas**.

**Métrica.** Acierto balanceado = ½·(acierto en bases con r > 0 + acierto en bases con r < 0).

**Bootstrap (exacto y reproducible).**
- Filas ordenadas por `base_open_utc`, n = número de filas de la muestra.
- Bloques circulares de 42 filas (7 días × 6 bases). Por réplica se sortean ⌈n/42⌉ inicios con `numpy.random.default_rng(42).integers(0, n, size=(10000, ⌈n/42⌉))` (una sola llamada) y se recorta a n filas.
- 10 000 réplicas. **La misma matriz de índices para los 3 modelos** (pareado).
- p unilateral por modelo = (1 + #{réplicas con acierto balanceado ≤ 0,50}) / 10 001.
- Se informa además el percentil 2,5 (`numpy.percentile`, método por defecto `linear`).
- Versiones: Python 3.13, numpy 2.5.4, pandas 3.0.6 (las de `docs/evidencia/KT-001/requirements-resolved.txt`). El evaluador aborta si no coinciden.

**Corrección.** Holm sobre las 3 p, α unilateral familiar = 0,025 (umbrales 0,0083 / 0,0125 / 0,025).

**Veredicto por modelo.** **APRUEBA** si Holm rechaza su H0. **NO APRUEBA** en otro caso. No hay segunda condición.

**Descriptivo, sin efecto en el veredicto:** acierto bruto; referencias «siempre sube», «siempre baja», «persistencia» y «reversión» (con el cierre de B−4h de los ZIP); acierto de cada modelo cuando coincide y cuando no coincide con la reversión; proporción de «sube»; acierto balanceado y tasas por hora base.

**Sin miradas con poder de decisión.** El resumen horario de KT-002 seguirá mostrando tasas; por eso la parada es solo por n o por fecha, nunca por resultado.

## 5. Potencia, n y fechas

- Efecto de planificación: acierto balanceado **55 %** (rebajado desde 56,9 % por maldición del ganador, posible contaminación y mezcla de horas).
- Familia de 3 con Holm; para planificar se usa el escalón más exigente (α = 0,025/3): n ≈ **1047** independientes con potencia 80 %.
- Dependencia entre las 6 bases del día: factor 1,25 → **n fijo = 1310** bases puntuadas.
- Simulación de la regla exacta (bootstrap de 2000 réplicas por corrida, `mejorador/pot_kt004.py` y `tam_kt004.py`), n = 1310, sesgo del modelo 57 % «baja»:

| Tasa de subida futura | Tamaño (balanceado 50 %, nivel 0,0083) | Potencia (55 %) | Potencia (54 %) |
|---|---|---|---|
| 45 % | 0,6 % | 0,89 | 0,69 |
| 50 % | 1,2 % | 0,88 | 0,72 |
| 55 % | 0,85 % | 0,89 | 0,71 |

  La simulación supone filas independientes; con dependencia real la potencia efectiva es menor (eso cubre el factor 1,25).
- Ritmo: 6 bases sin solape por día. Al 100 % de cobertura ≈ 218 días; al 80 % ≈ 273 días. Con inicio cerca del 2026-10-22: **entre fines de mayo y fines de julio de 2027**.
- **Vigía de cobertura**: a los 7 días del registro informa solo cuántas bases sin solape se generaron sobre las esperadas (sin tasas de acierto). Si es < 80 %, se recalculan la fecha estimada y la fecha límite y se anota en el registro antes de seguir; la regla no cambia.
- **Fecha límite: 2027-12-31.** Si no se llegó a 1310:
  - con n ≥ 500, se evalúa con la misma regla y se etiqueta "potencia menor a la planificada"; un NO APRUEBA así no descarta al modelo;
  - con n < 500, solo descriptivo, sin veredicto.
- Efectos menores a ~4 puntos no se van a poder distinguir del azar. Hay que aceptarlo antes de empezar.

## 6. KT-002 congelado como fuente

El registro repetirá estos hashes y el evaluador los comprueba:

| Archivo | SHA-256 |
|---|---|
| `tools/kt002_prospectivo.py` | `81d28203a41e15145ccd211590d07cd41830e9681097df1b27762726cccdc4c7` |
| `data/kt002/model_revisions.json` | `cc86978d83b3b29e53982e38b0b52f60e8e3ca8a6cebb8ba0c913255708d6f20` |
| `docs/evidencia/KT-001/requirements-resolved.txt` | `f5b4b5aab4b78c1bbd7930ea6f421d9cfda2506f335ec5fd4027e1650e0557ac` |

El evaluador **aborta** (no evalúa, que no es lo mismo que rechazar) si:
1. algún hash cambió, o hay commits que tocan esos archivos después de T_registro;
2. `.github/workflows/kt002.yml` deja de fijar `torch==2.14.1`, el commit de Kronos `67b630e6…`, Python 3.13, `requirements-resolved.txt` o la clave de caché de pesos;
3. en `git log -p` de `predicciones.csv` posterior al registro, una fila con base > T_registro se borra o cambia alguno de sus 10 campos de pronóstico (solo se permite completar el resultado);
4. al recomputar con los ZIP oficiales, `base_close` difiere en más de 1e-9 (relativo) o `actual_ret` en más de 1e-9 (absoluto) en cualquier base de la muestra;
5. falta en los ZIP la vela base o la vela objetivo de alguna base de la muestra: se espera a que Binance publique el ZIP diario o mensual.

Los ZIP se bajan con su `.CHECKSUM` (mensuales y, para el último mes, diarios) y se guarda el manifiesto con los SHA-256. Los cambios solo operativos de KT-002 que no toquen esas piezas (por ejemplo, el despertador) no abortan.

Consecuencia declarada: si alguien corrige `tools/kt002_prospectivo.py` durante la prueba, KT-004 se aborta y hay que registrar otra.

## 7. Inicio

- T_registro = fecha de commit (`%cI`) del commit que agrega `docs/KT-004_registro_prospectivo.md`, comprobando que ese commit está en `origin/master`.
- Cuentan solo bases con `base_open_utc > T_registro`. La primera base que cuenta es la primera múltiplo de 4 h después de esa hora.

## 8. Evaluador (borrador probado con datos sintéticos)

- Borrador: `/tmp/claude-0/-home-claude/14241745-63d7-59dc-a6ae-501840d3a10b/scratchpad/mejorador/kt004_evaluar.py` (SHA-256 `fe2457da2b84341e951fbd23643890c4e5f6ce37cc8773ea9f79fc1b3e5972d5`). Destino: `tools/kt004_evaluar.py`, en rama propia y solo después de los dos OK.
- Pruebas: `/tmp/claude-0/-home-claude/14241745-63d7-59dc-a6ae-501840d3a10b/scratchpad/mejorador/test_kt004_evaluar.py`, **17 pruebas, todas pasan**, solo con datos sintéticos. Cubren: regla estricta de inicio, solo horas múltiplo de 4, duplicados, filas sin puntuar, vela B−4h faltante (excluida de la guarda descriptiva, no de la primaria), horas omitidas que no se rellenan, vigía < 80 %, vela objetivo faltante (aborta), discrepancia de 1e-8 con el ZIP (aborta), evaluación antes de tiempo (aborta), fecha límite con n < 500 (solo descriptivo), efecto fuerte que aprueba y azar que no, bootstrap reproducible con bloques circulares de 42, Holm, ZIP con marcas de tiempo en microsegundos (Binance desde 2025) y velas desalineadas, CHECKSUM malo, hashes congelados y pines del workflow, y pronóstico reescrito o borrado en el historial de git (aborta).
- No se ejecutó sobre `data/kt002/` real.

## 9. Costos (0,20 % ida y vuelta)

KT-004 **no apunta a operar** y no puede aprobar ninguna estrategia. Con los números post corte (post hoc): el retorno direccional bruto medio de Kronos es +0,041 % por base y el neto tras 0,20 % es −0,16 %. Con |retorno real| medio de 0,62 % a 4 h, cubrir 0,20 % exigiría un acierto ≈ 66 %. Llevar cualquier resultado a dinero exige otra variante, otro horizonte y la Fase 0 completa de `hypothesis-gate`.

## 10. Riesgos de sobreajuste

- La idea (acierto balanceado) sale de mirar KT-003; por eso solo se prueba con datos posteriores al registro.
- No hay parámetros que ajustar: modelos, horizonte, contexto, semilla y muestra son los de KT-002.
- Transferencia: KT-003 usa solo 00:00 UTC; KT-002 usa 6 horas (§1.3).
- KT-004 y KT-005 usan las mismas fechas futuras, pero preguntan cosas distintas (KT-004: ¿cada modelo actual supera el 50 %?; KT-005: ¿TimesFM ajustado le gana a TimesFM actual?). Se declara la superposición.

## 11. Conteo de intentos

- KT-004 suma **1** variante confirmatoria (3 pruebas con Holm) al frente Kronos/TimesFM. No es financiera y no cambia el N canónico.
- Se declara: en la exploración el autor miró 3 modelos, 4 referencias triviales, cortes por trimestre, año, magnitud, volatilidad y hora, y reversión a 1, 4, 24, 100 y 400 h. Ninguno entra en la regla.
- La v1 (Kronos solo + guarda) se rechazó en auditoría y nunca se registró ni se evaluó; queda anotada.

## 12. Qué decide el usuario

Nota: según `CLAUDE.md` (2026-10-20), el gerente puede aprobar mediciones sin dinero que el desconfiado haya aprobado sin ALTOS ni MEDIOS. Igual dejo listas las decisiones para quien apruebe:

1. Si acepta KT-004 tal como está (o cambia algo de la Fase 1: hipótesis, métrica, efecto de 55 %, n = 1310, fecha límite 2027-12-31). Según `hypothesis-gate`, estos puntos los confirma el usuario, no el agente.
2. Si acepta que una corrección de `tools/kt002_prospectivo.py` durante la prueba aborte KT-004.

## 13. Resumen sencillo para el usuario

- Se van a usar los pronósticos que KT-002 ya hace cada hora, desde el día en que se registre, sin cambiar nada de KT-002. Los tres (Kronos, TimesFM y la mezcla 50/50) siguen en la prueba.
- La medida es "¿acierta mejor que una moneda, tanto cuando el mercado sube como cuando baja?". Así un modelo que dice "baja" casi siempre no puede ganar por suerte del mercado.
- Hacen falta 1310 pronósticos sin solaparse: entre 7 y 9 meses (hacia mediados de 2027). Se evalúa una sola vez, al final.
- Si un modelo aprueba, quiere decir que "ve algo" de la dirección a 4 horas; no que sirva para ganar dinero (haría falta acertar cerca del 66 % para cubrir comisiones). Si no aprueba, no se saca: se estudia por qué.
