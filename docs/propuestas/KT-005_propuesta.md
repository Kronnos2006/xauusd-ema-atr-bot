# KT-005 — propuesta: ajustar TimesFM para que mejore (log-retornos en vez de cierres)

2026-10-20, Costa Rica. Autor: agente `mejorador`. Estado: **PROPUESTA v1**, sin auditar por `desconfiado` y sin OK. No se registró, no se escribió el código del modelo ni el workflow y no se tocó KT-002 ni KT-003.

Pedido del usuario: TimesFM sigue en la prueba (KT-002 y KT-004 no cambian) y además hay que proponer cómo ajustarlo para que mejore. Regla del `mejorador`: un modelo que rinde peor no se saca, se entiende por qué y se ajusta.

## 1. Evidencia: por qué TimesFM rinde peor (post hoc, datos ya vistos)

Fuente: `data/kt003/predicciones.csv` y `data/kt003/btcusdt_1h.csv.gz`. Scripts: `/tmp/claude-0/-home-claude/14241745-63d7-59dc-a6ae-501840d3a10b/scratchpad/mejorador/tfm_diag.py` y `tfm_diag2.py`. Post corte, n = 842, una base por día a las 00:00 UTC.

| Qué medí | TimesFM | Kronos |
|---|---|---|
| Acierto / acierto balanceado | 48,7 % / 48,7 % | 56,8 % / 56,9 % |
| Spearman (retorno previsto, retorno real) | **−0,011** (p = 0,76) | +0,124 (p < 0,001) |
| Desvío del retorno previsto / desvío del real (0,92 %) | **0,22 %** (24 %) | 0,51 % (55 %) |
| Bases con \|previsto\| < 0,05 % / < 0,10 % | **34 % / 57 %** | — / 26 % |
| Su signo coincide con «volver al promedio de las 400 h» | **65,6 %** | 62,5 % |
| Su signo coincide con «revertir las últimas 24 h» | 54,8 % | **68,1 %** |
| Acierto por año: 2024 (2.º sem.) / 2025 / 2026 | **40,8 %** / 51,0 % / 50,9 % | — |
| Dentro del entrenamiento: acierto / Spearman | 51,6 % / 0,000 | 52,7 % / 0,046 |

Lectura (todo post hoc):

1. **El retorno previsto de TimesFM no tiene relación con el real** (Spearman ≈ 0, tanto post corte como dentro del entrenamiento). No es que se equivoque de signo con información: su signo es casi ruido.
2. **Predice movimientos muy chicos**: la mitad de las veces menos de 0,1 % en 4 h, cuando el real se mueve en promedio 0,62 %. El signo de algo tan cercano a cero lo decide un detalle numérico.
3. **Lo poco que tiene de dirección viene del nivel de precio**: su signo sigue sobre todo a «volver al promedio de las 400 velas» (65,6 %). Recibe la serie de **cierres en dólares**, normalizada por la ventana entera; el pronóstico mediano se queda pegado al último precio y se inclina apenas hacia el nivel medio de la ventana. Esa vuelta al promedio de 400 h casi no sirve a 4 h (como regla sola, acierto balanceado 53,0 %), y lo de TimesFM rinde aún menos.
4. Kronos, en cambio, reacciona a las últimas 24 h (68 % contra esa tendencia) y su retorno previsto sí se relaciona con el real.
5. El mal resultado de TimesFM se concentra en el 2.º semestre de 2024 (40,8 %, n = 184); en 2025–2026 está en ≈ 51 %. Es decir: **más que "equivocado", TimesFM está "ciego"** a la dirección a 4 h con esta forma de alimentarlo.

Hipótesis de la causa (post hoc): **la entrada en niveles de precio hace que TimesFM pronostique el nivel, no el cambio**. Las variaciones hora a hora, que son lo que importa a 4 h, quedan como ruido pequeño frente a la escala de la ventana.

Advertencias: Kronos fue el mejor de 3 en ese mismo período; el post corte no está certificado fuera del entrenamiento (Enmienda C de KT-003), sobre todo para TimesFM (publicado en 2025-09). Nada de esto es confirmatorio.

## 2. Ajustes del menú: cuál elijo y por qué

| Ajuste del menú | ¿Ataca la causa del §1? | Decisión |
|---|---|---|
| **Log-retornos en vez de cierres** | Sí: el modelo ve directamente los cambios hora a hora, sin el ancla del nivel | **Brazo A (principal)** |
| **Contexto más largo (1024 velas de cierre)** | En parte: prueba si el problema es la ventana corta que define el «nivel». Si el ancla es la causa, más contexto no debería ayudar; si ayuda, la causa era otra | **Brazo B (opcional; lo decide el usuario)** |
| Cuantil en vez de mediana | No: si el pronóstico central está pegado a cero, cambiar de cuantil mueve el sesgo (más «sube» o más «baja») pero no da información | Descartado |
| Quitar `force_flip_invariance` / cambiar la normalización | No hay evidencia que lo apunte | Descartado |
| Otro horizonte | Cambiaría la pregunta; deja de ser comparable con KT-002 | Descartado |
| Ajuste fino | Caro y con mayor riesgo de fuga; primero hay que probar ajustes baratos | Descartado por ahora |

**No corrí ninguno de los ajustes sobre datos ya vistos.** La elección sale del diagnóstico, no de comparar variantes en KT-003. Eso evita inflar el resultado por elegir el mejor de varios. A cambio, no hay ninguna estimación previa del efecto del ajuste (ver §6).

## 3. Cambio exacto

Se crea una variante nueva, **KT-005**, que corre en paralelo con KT-002 y **no la toca**. En cada corrida, con el mismo contexto de velas cerradas de BTCUSDT 1h y la misma revisión de TimesFM 2.5 200M (`1d952420…`, código `e51928e2…`):

- **Control (C)**: TimesFM exactamente como en KT-002: últimos 400 cierres, mediana, `ForecastConfig(max_context=512, max_horizon=128, per_core_batch_size=1, normalize_inputs=True, use_continuous_quantile_head=True, force_flip_invariance=True, infer_is_positive=True, fix_quantile_crossing=True)`. r̂_C = cierre previsto de la 4.ª vela / C₀ − 1.
- **Brazo A (log-retornos)**: entrada = los 399 log-retornos de esos mismos 400 cierres, `log(c_t / c_{t−1})`. Igual `ForecastConfig` salvo **`infer_is_positive=False`** (los retornos pueden ser negativos; dejarlo en True sería un error). Pronóstico de 4 pasos con la mediana; r̂_A = exp(suma de las 4 medianas) − 1. Se declara que la suma de medianas no es la mediana de la suma; solo importa el signo.
- **Brazo B (opcional, contexto 1024)**: últimos 1024 cierres, `max_context=1024`, el resto igual que el control. Necesita dos llamadas a la API de Binance (límite de 1000 velas por llamada).

El control se calcula **dentro de KT-005** (y no se toma de KT-002) para que los dos lados del par usen exactamente las mismas bases y horas, aunque KT-002 omita alguna. Como chequeo, r̂_C debe coincidir con `timesfm_ret` de KT-002 para la misma base; las diferencias se informan (descriptivo) y si superan 1e-6 relativo en más del 1 % de las bases se investiga antes de evaluar.

Archivos nuevos (en rama propia, solo después de los dos OK): `docs/KT-005_registro_prospectivo.md`, `tools/kt005_timesfm_ajuste.py`, `.github/workflows/kt005.yml`, `tools/kt005_evaluar.py` (reusa las funciones de `kt004_evaluar.py`: selección, ZIP, bootstrap, Holm), `data/kt005/`.

## 4. Hipótesis falsable

- H1_A: en BTCUSDT 1h, sobre bases prospectivas sin solape, **el acierto balanceado de TimesFM con log-retornos es mayor que el de TimesFM actual** (control), sobre las mismas bases.
- H0_A: acierto balanceado(A) − acierto balanceado(C) ≤ 0.
- (Si el usuario incluye el brazo B: H1_B igual, con contexto 1024.)

## 5. Métrica primaria y regla de aprobado

- **Muestra**: bases de `data/kt005/predicciones.csv` con `base_open_utc > T_registro(KT-005)`, hora UTC múltiplo de 4, primera fila por base, puntuadas, r ≠ 0; las primeras **1310** en orden de `base_open_utc`. Por par, se excluyen las filas con r̂ = 0 en cualquiera de los dos lados.
- **Métrica**: Δ = acierto balanceado(brazo) − acierto balanceado(control), mismas filas.
- **Bootstrap**: el de KT-004 sin cambios (bloques circulares de 42 filas ordenadas por `base_open_utc`, 10 000 réplicas, `numpy.random.default_rng(42)`, una sola matriz de índices para todos los brazos, numpy 2.5.4 y pandas 3.0.6). p unilateral = (1 + #{Δ* ≤ 0}) / 10 001.
- **Corrección**: solo brazo A → una prueba, α unilateral 0,025. Con brazo B → Holm sobre 2, α familiar 0,025.
- **APRUEBA** el brazo cuya H0 rechaza Holm (o la prueba única). **NO APRUEBA** en otro caso.
- **Descriptivo** (sin efecto en el veredicto): acierto balanceado de cada brazo contra 50 %, acierto bruto, proporción de «sube», Spearman entre previsto y real, desvío del previsto, por hora base, y una combinación descriptiva «Kronos de KT-002 + brazo A 50/50».
- Qué significa aprobar: "este ajuste mejora a TimesFM". No significa que TimesFM ajustado le gane a una moneda ni que sirva para operar. Si aprueba, el TimesFM ajustado entra como candidato en un registro confirmatorio nuevo; el TimesFM actual sigue en KT-002 igual.
- Si no aprueba: TimesFM no sale. Se vuelve al diagnóstico con los datos nuevos (ya vistos desde ese momento) para elegir otro ajuste del menú, que contará como intento nuevo.

## 6. Potencia, n y fecha

No hay estimación previa del efecto (no corrí el ajuste sobre datos vistos). Efecto de planificación: **Δ = 6 puntos** (llevar a TimesFM de ≈ 49 % a ≈ 55 %, cerca de lo que logró Kronos). Supuesto: los dos lados discrepan de signo en ≈ 45 % de las bases (desconocido; si discrepan menos, la potencia sube).

Con n = 1310 (≈ 1048 efectivos con factor 1,25):

| | Δ = 5 pt | Δ = 6 pt |
|---|---|---|
| Solo brazo A (α = 0,025) | 0,68 | **0,83** |
| A y B con Holm (α = 0,0125 en el peor escalón) | 0,57 | 0,75 |

Por eso **recomiendo solo el brazo A**. Con B, la potencia de cada brazo cae.

- Ritmo: 6 bases por día. Mismo calendario que KT-004: ≈ 218 días al 100 % de cobertura, ≈ 273 días al 80 % → **mayo a julio de 2027**.
- Vigía de cobertura a los 7 días (solo cuenta bases, sin aciertos): si < 80 %, se recalculan las fechas y se anota en el registro.
- Fecha límite **2027-12-31**: con n ≥ 500 se evalúa con la misma regla y se etiqueta "potencia menor"; con n < 500 queda solo descriptivo.
- Diferencias menores a ~5 puntos no se van a detectar con buena probabilidad.

## 7. Cómo correrlo en paralelo sin tocar KT-002

- Workflow nuevo `.github/workflows/kt005.yml`, copia del esquema de `kt002.yml` (job vivo ~4 h 45 min que corre el script en el minuto 12 de cada hora, 5 minutos después de KT-002 para no competir por el push), con `concurrency: kt005`.
- Se dispara también por push sobre `data/kt002/despertar.txt`, el archivo que ya toca el despertador externo. Solo lo **lee** como disparador: no hace falta una tarea programada nueva ni modificar nada de KT-002.
- Escribe solo en `data/kt005/` (`predicciones.csv`, `resumen.md`, `model_revisions.json`, `reproducibilidad.json`). Mismas versiones fijadas (torch 2.14.1, Python 3.13, `requirements-resolved.txt`), mismos pesos y caché de pesos aparte (`hf-kt005-1d952420`).
- Mismas protecciones que KT-004: hashes de `tools/kt005_timesfm_ajuste.py` y `data/kt005/model_revisions.json` fijados en el registro; aborta si cambian, si se reescribe un pronóstico ya guardado, o si `base_close`/`actual_ret` difieren de los ZIP oficiales en más de 1e-9.
- Prueba técnica previa (antes de registrar), **solo con velas sintéticas**: que los tres cálculos den números finitos, que dos corridas den lo mismo, y que el brazo A con `infer_is_positive=False` acepte retornos negativos.

## 8. Costo en GitHub Actions

- Tiempo de cálculo: KT-002 tarda ≈ 33 s por hora con Kronos y TimesFM juntos (`elapsed_s`). KT-005 corre solo TimesFM, 2 o 3 veces: estimo **15–30 s por hora** de CPU, más la carga del modelo.
- Ocupación real: como el cron de GitHub no dispara en este repo, el job queda vivo todo el tiempo. Son ≈ 1440 minutos de runner por día (≈ 43 000 por mes), igual que KT-002.
- Dinero: el repositorio `Kronnos2006/xauusd-ema-atr-bot` hoy es **público**, y en repos públicos los minutos de los runners estándar no se cobran. **Si el repo pasa a privado**, KT-002 + KT-005 sumarían ≈ 86 000 minutos por mes, muy por encima de los 2000 gratis del plan Free: habría que pausar uno o pagar. Lo dejo como decisión.
- Riesgo operativo: dos jobs empujando a `master` cada hora. Escriben en carpetas distintas y usan el mismo ciclo de `pull --rebase` con 3 reintentos; un push perdido se cuenta como hora omitida.

## 9. Costos de operación (0,20 % ida y vuelta)

KT-005 no apunta a operar. Aun si aprueba, TimesFM ajustado tendría que llegar a un acierto ≈ 66 % a 4 h para cubrir 0,20 % (§9 de KT-004). Cualquier uso con dinero exige otra variante y la Fase 0 completa de `hypothesis-gate`.

## 10. Riesgos de sobreajuste

- La causa propuesta (ancla de nivel) y el ajuste salen de mirar KT-003: post hoc, declarado. Solo se confirma con datos posteriores al registro.
- No se probó ningún valor del ajuste en datos vistos; no hay grilla.
- Sin parámetros libres: log-retornos de las mismas 400 velas, mediana, mismo horizonte y revisión.
- El brazo A cambia dos cosas a la vez por necesidad técnica (la serie y `infer_is_positive=False`); se declara que no se pueden separar.
- Superposición con KT-004: mismas fechas, preguntas distintas. El control de KT-005 es el mismo TimesFM que KT-004 evalúa contra 50 %; los dos resultados se leen por separado.

## 11. Conteo de intentos

- Brazo A: **+1** variante del frente Kronos/TimesFM. Con brazo B: **+2**. No financieras; no cambian el N canónico.
- Declaro que miré, en exploración, 6 opciones del menú y descarté 4 por razonamiento, sin correrlas.

## 12. Qué decide el usuario (o el gerente, según `CLAUDE.md`, si el desconfiado aprueba sin ALTOS ni MEDIOS)

1. Si se prueba solo el brazo A (log-retornos, recomendado por potencia) o también el B (contexto 1024).
2. Si acepta el efecto de planificación de 6 puntos y n = 1310 (fecha estimada mayo–julio de 2027, límite 2027-12-31).
3. Si acepta tener un segundo workflow vivo todo el día (gratis mientras el repo sea público).

## 13. Resumen sencillo para el usuario

- TimesFM no se equivoca "con criterio": sus pronósticos son tan pequeños y tan pegados al precio actual que su dirección es casi al azar.
- La causa más probable es que le damos precios en dólares y pronostica el nivel, no el cambio. El ajuste es darle los cambios hora a hora (log-retornos).
- Se corre en paralelo con KT-002, sin tocarla, comparando el TimesFM ajustado contra el actual con los mismos datos nuevos. Tarda lo mismo que KT-004: unos 7 a 9 meses.
- Si mejora, el TimesFM ajustado pasa a una prueba nueva. Si no mejora, TimesFM sigue en la prueba y se busca otro ajuste.
