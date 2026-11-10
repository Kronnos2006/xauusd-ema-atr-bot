# KT-006 — propuesta: Kronos y TimesFM «especializados» en BTCUSDT con datos públicos (capa de probabilidad, ensemble normalizado y ajuste fino diferido)

2026-11-10, Costa Rica. Autor: agente `mejorador`. Estado: **PROPUESTA v1**, sin auditar por `desconfiado`, sin OK del usuario/gerente. No se registró nada, no se escribió código ni workflow, **no se ejecutó ningún modelo ni se calculó ningún resultado** y no se tocó KT-002 (`data/kt002/`, `tools/kt002_prospectivo.py`, `kt002.yml`). Pedido del propietario (2026-11-10): una versión de Kronos y TimesFM especializada en BTCUSDT, usando solo datos públicos como referencia.

Nota de nombres: en `docs/` el registro `KT-004_registro_multiactivo.md` (ETH/SOL/BNB/XRP, **NO PASA**, 2026-10-31) ya ocupa el número KT-004. Las propuestas `KT-004_propuesta.md` (confirmar acierto balanceado con KT-002) y `KT-005_propuesta.md` (TimesFM con log-retornos) **siguen sin registro** (no existe `docs/KT-005_registro_*` ni `tools/kt005_*` al 2026-11-10). Aquí las llamo KT-004p y KT-005p. KT-006 no depende de ellas ni las reemplaza.

## 0. Resumen en cinco líneas

1. «Especializar» en BTC con ajuste fino aporta poco y es caro: Kronos ya se preentrenó con datos de más de 45 bolsas (README) y los únicos datos BTC realmente nuevos son los posteriores a junio de 2024; y toda la historia BTC 2017–2026-10-20 ya está expuesta (KT-003, Enmienda B). El único «holdout sellado» posible es **futuro**.
2. Lo barato y que ataca las carencias (a), (b), (c), (d) y (f) es una **corrida paralela nueva** (KT-006) que guarda lo que KT-002 descarta (las 20 trayectorias de Kronos y los cuantiles de TimesFM) y evalúa dos reglas sin parámetros libres: **voto de las 20 trayectorias** (C1) y **ensemble normalizado por desvío fijo** (C2).
3. Prueba confirmatoria: acierto balanceado > 50 % (que equivale a ganarle a «siempre sube» sin depender de la deriva), Holm sobre 2 pruebas, n = 1200 bases sin solape, ≈ 200–250 días. MDE ≈ 5,0 puntos.
4. Régimen (e), magnitud (d) y costos (f) quedan como descriptivos pre-declarados: no hay potencia para confirmarlos. A 4 h, cubrir 0,30 % ida y vuelta exige ≈ 80–90 % de acierto: KT-006 **no sirve para operar**, solo para saber si los modelos ven algo.
5. Recomendación: registrar solo A + B (KT-006) con TimesFM y Kronos adentro; **no** hacer ajuste fino ahora, ni grilla de pesos, ni filtro de régimen confirmatorio.

## 1. Exposición previa declarada (qué números ya vi)

En esta sesión leí, y no calculé nada nuevo:

- De los documentos del repo (KT-004p/KT-005p, post hoc, `data/kt003/predicciones.csv`, 842 bases post corte): Kronos 56,8 % acierto / 56,9 % balanceado, «baja» el 57 % de las veces; TimesFM 48,7 %; KT-001 55,5 %; «siempre sube» 50,9 %, persistencia 48,5 %, reversión 51,5 %; Spearman Kronos +0,124 y TimesFM −0,011; desvío del retorno previsto 0,51 % (Kronos) y 0,22 % (TimesFM).
- De `data/kt002/resumen.json` (actualizado 2026-11-10 12:07 UTC), **solo el bloque «todos_solapados»**: 476 pronósticos, 472 vencidos; Kronos 51,27 % (242/472), TimesFM 47,67 % (225), KT-001 48,52 % (229), «siempre sube» 46,61 % (220); McNemar vs «siempre sube»: p 0,115 / 0,672 / 0,507. **No vi el bloque «sin_solape»** ni filas individuales (solo las dos primeras filas del CSV).
- De `ESTADO.md`: KT-004 multiactivo, Kronos/ETH 52,06 % vs 50,3 %, p = 0,067, **no pasa**.
- De `data/mercado/tendencia.json` (2026-11-10): régimen diario LATERAL, 4 h BAJISTA, ret 7 d −1,88 %, ret 30 d −9,18 %.
- De `data/kt003/predicciones.csv`: solo el conteo por período (2086 dentro del entrenamiento, 842 post corte; 2017-09-03 a 2026-10-20) y la primera fila.

Consecuencias: (i) toda la evidencia de este documento es **post hoc** y solo sirve para formular hipótesis; (ii) los pronósticos de KT-002 hasta 2026-11-10 están vistos (tasas), por lo que **no cuentan** para confirmar nada de KT-006; (iii) las velas BTC hasta 2026-11-10 quedan expuestas; el único dato confirmatorio es el posterior a `T_registro` de KT-006.

## 2. Evidencia y diagnóstico por carencia (post hoc)

| Carencia | Qué muestra el repo | Qué se puede hacer barato |
|---|---|---|
| (a) KT-001 promedia retornos sin normalizar ni votar | TimesFM predice ≈ 0,22 % de desvío contra 0,51 % de Kronos: en 0,5·r̂K + 0,5·r̂T pesa más Kronos de hecho, y nadie decidió ese peso | Normalizar cada modelo por un desvío fijo y combinar (Opción B) |
| (b) Kronos descarta sus 20 muestras (`predict` las promedia; README: «paths to generate and average») | Con T=1 y top_p=0,9 la fracción de muestras al alza es una probabilidad; hoy no existe en ningún archivo | Guardar las 20 muestras y votar (Opción A). Imposible re-derivar desde `data/kt002` o `data/kt003` |
| (c) TimesFM ve solo cierres, Kronos ve OHLCV | KT-005p ya propone log-retornos (post hoc: TimesFM «ciego», Spearman −0,011) | **No se duplica**: KT-006 deja la entrada de TimesFM igual que KT-002; si KT-005p se registra, queda como variante independiente |
| (d) Cada acierto pesa igual | Spearman de Kronos 0,124 (post corte) sugiere relación con la magnitud, pero con la métrica de signo no se explota | Descriptivo: acierto por tercil de \|z\| y retorno direccional bruto (no confirmatorio) |
| (e) Sin régimen | No hay cruce por régimen visto. Régimen hoy: diario LATERAL, 4 h BAJISTA | Descriptivo con las reglas fijas del analista; sin potencia para confirmar (§4.C) |
| (f) Sin costos | `COSTOS_BTCUSDT.md`: a 4 h la mediana de \|ret\| de 2026 es 0,377 %; con 0,30 % se necesita ≈ 89,8 % de acierto (129,6 % con 0,60 %, imposible) | Reportar el umbral; no se opera |

## 3. Cambio exacto: variante nueva, corrida paralela (no toca KT-002)

KT-006 corre en un workflow propio, en la rama del `jefe-desarrollo`, solo tras los dos OK. Cada vez que cierra una base con hora UTC múltiplo de 4, con las mismas 400 velas cerradas de BTCUSDT 1h de `data-api.binance.vision` y las mismas revisiones de KT-002 (Kronos-small `901c26c1…`, tokenizer `0e011738…`, código Kronos `67b630e6…`, TimesFM 2.5 `1d952420…`, código `e51928e2…`), guarda en `data/kt006/predicciones.csv`:

1. **Kronos**: las 20 trayectorias (cierre de la 4.ª vela de cada una y cierres de los 4 pasos), su media (r̂K, regla KT-002) y p_K = fracción de trayectorias con cierre 4.ª vela > C₀.
2. **TimesFM**: mediana (r̂T, regla KT-002) y los cuantiles que devuelve `forecast` (hoy KT-002 hace `point, _ = …` y los descarta). p_T = P(ret > 0) por interpolación lineal de los cuantiles en la 4.ª vela.
3. **No guarda resultado real ni aciertos.** El CSV no tiene `actual_*`; el evaluador baja el cierre real de los ZIP oficiales al final. El `resumen` de KT-006 solo cuenta bases y cobertura (sellado «de disciplina»: el CSV es público en el repo, pero ningún script calcula acierto hasta el cierre).

Reglas candidatas (congeladas ahora, **sin parámetros ajustados con datos de resultado**):

- **C1 — Voto de Kronos**: «sube» si p_K > 0,5; «baja» si p_K < 0,5; si p_K = 0,5 (10/20) decide el signo de r̂K; si r̂K = 0 se excluye.
- **C2 — Ensemble normalizado**: S = ½·(r̂K / sK) + ½·(r̂T / sT); «sube» si S > 0. sK y sT = desvío poblacional de `kronos_ret` y `timesfm_ret` en las filas `periodo = post_corte` de `data/kt003/predicciones.csv` (SHA-256 del archivo fijado en el registro; el script los calcula y los escribe en el registro **antes** del primer dato prospectivo). Valores esperados ≈ 0,51 % y ≈ 0,22 % (no verificados al centavo: los dan KT-005p). Peso igual en espacio normalizado: no se ajusta.
- **Controles dentro de KT-006** (mismas bases, mismas muestras): M = signo de r̂K (regla KT-002 de Kronos), T = signo de r̂T, K1 = KT-001 original (0,5·r̂K + 0,5·r̂T sin normalizar).
- **Control clásico opcional (descriptivo, +1 variante)**: Ridge sobre rasgos simples de BTC (retornos rezagados, sin volumen en nivel), entrenado con `data/kt003/btcusdt_1h.csv.gz` hasta el cierre del dato de KT-003 (2026-10-20) y congelado. Reusa `tools/kronnos_entrenamiento_piloto.py` (ver §8). Responde: ¿Kronos/TimesFM agregan algo sobre un modelo trivial entrenado en BTC?

Prueba técnica previa (antes de registrar, **solo con velas sintéticas**): finitud, determinismo de dos corridas, y que la media de las 20 trayectorias capturadas coincida con la salida de `predict(sample_count=20)` con la misma semilla (tolerancia a declarar). Si la captura individual obliga a llamar 20 veces con `sample_count=1` y semillas 42…61, la media no será bit a bit igual a la de KT-002; se declara y el control M de KT-006 usa **sus propias** 20 muestras. **No verificado** cómo extraer las muestras del código a esa revisión (§12).

## 4. Opciones evaluadas

Cada ficha: frase falsable · regla de corte · folds · n · variantes para DSR · costos · datos y licencia · comparación.

### Opción A — Probabilidad desde las 20 trayectorias de Kronos (y desde los cuantiles de TimesFM)  **[RECOMENDADA, en KT-006]**

- Frase falsable: «En BTCUSDT 1h, sobre bases prospectivas sin solape, el voto de las 20 trayectorias de Kronos (C1) tiene acierto balanceado > 50 % a 4 h». H0: ≤ 50 %.
- Regla de corte: APRUEBA si Holm (con C2) rechaza H0 a α unilateral familiar 0,025; si no, NO APRUEBA y Kronos sigue en la prueba.
- Folds: 4 bloques consecutivos de igual cantidad de bases (≈ 300 cada uno, ≈ 50 días) **derivados del n real al cierre**; se informa el acierto balanceado por bloque y sin el mejor bloque. Piso: ≥ 30 bases de cada signo de r por bloque; si no, se fusionan bloques adyacentes.
- n: 1200 puntuadas (§6). Variantes para DSR: +1 (C1).
- Costos: no opera; umbral 0,30 % base / 0,60 % x2 (marco de riesgo v1.0 §7) solo descriptivo.
- Datos: velas BTCUSDT 1h públicas de Binance (§9). Cero datos de entrenamiento.
- Comparación: ver §7.
- Lo que no promete: el voto y la media comparten las mismas muestras; si coinciden en ≈ 85–90 % de las bases (supuesto, no medido), C1 casi repite a Kronos de KT-002. El valor real es **dejar guardadas las muestras** para poder calibrar con datos nuevos más adelante.
- p_T (cuantiles de TimesFM): solo descriptivo. Si su mediana está pegada a cero (KT-005p: 34 % de bases con \|r̂\| < 0,05 %), P(ret>0) ≈ 0,5 y su signo es igual de ruidoso.

### Opción B — Ensemble normalizado (y, descriptivo, «solo si coinciden»)  **[RECOMENDADA, en KT-006]**

- Frase falsable: «El ensemble normalizado C2 tiene acierto balanceado > 50 % a 4 h», y como secundaria descriptiva «C2 supera a K1 (KT-001 sin normalizar)».
- Regla de corte: la misma del Holm de 2.
- Folds, n, DSR: iguales; variantes +1 (C2).
- «Operar solo cuando coinciden» (Kronos y TimesFM con el mismo signo) y «TimesFM como filtro de Kronos»: **descriptivos** (acierto cuando coinciden y cuando no), no entran en la regla. Razón: en el 842 de KT-003, TimesFM es casi ruido; filtrar por coincidencia reduce n a ≈ la mitad sin evidencia previa de ganancia.
- Pesos distintos de 50/50 (p. ej. ajustados por regresión logística): **no se prueban**. Con TimesFM en Spearman ≈ 0 el peso ajustado sería ≈ 0 para TimesFM, es decir descartaría TimesFM de hecho, contra la regla de fondo; y agregarían parámetros ajustados sobre datos ya vistos.

### Opción C — Filtro de régimen con las reglas fijas del analista  **[solo descriptivo]**

- Frase falsable (no confirmable aquí): «El acierto balanceado de C1/C2 es mayor cuando el régimen diario (reglas de `analista-tendencia.md`, calculadas con velas cerradas hasta la base) es ALCISTA o BAJISTA que cuando es LATERAL».
- Por qué no confirmatoria: no hay evidencia previa de dependencia por régimen (no la calculé, §1), y con un estrato de ≈ 25 % de n = 1200 (≈ 300 bases; la proporción real de días por régimen **no se verificó**) el MDE sube a ≈ 8 puntos (0,5·2,8/√300 ≈ 8,1 pts, 80 %, α 0,025). Se pre-declara la tabla descriptiva (3 estratos diarios + 3 de tendencia corta 4 h) y nada más.
- Regla de corte: ninguna. Si un estrato sugiere algo, eso es post hoc y requiere una variante nueva con datos posteriores al cierre de KT-006.
- DSR: 0 variantes confirmatorias; 6 cortes descriptivos declarados.
- Reglas fijas: se usan tal cual, sin retocar umbrales ni medias; régimen calculado de forma punto-en-el-tiempo con la vela diaria cerrada anterior a la base (sin mirar hacia adelante).

### Opción D — Ajuste fino (Kronos-small, opcionalmente TimesFM) sobre velas BTC públicas  **[NO ahora; diseño de reserva]**

- Frase falsable: «Kronos-small ajustado con BTCUSDT 1h hasta `T_corte` supera, en bases posteriores a `T_corte` + embargo, al Kronos-small sin ajustar (mismo código y contexto) en acierto balanceado».
- Regla de corte (si el usuario la pide): entrenamiento hasta 2026-06-30, validación 2026-07-01 a 2026-09-30 (solo para elegir checkpoint), todo posterior = prospectivo y sellado. Los meses 2026-10 y 2026-11 no sirven como holdout (expuestos por KT-003/KT-002).
- Por qué no ahora: (1) casi no hay información BTC nueva (≈ 20 000 velas horarias desde 2024-07) frente a un preentrenamiento declarado hasta junio de 2024 sobre 45 bolsas; (2) el pipeline oficial de Kronos para ajuste fino es un **ejemplo con Qlib y acciones A diarias** (README: «not production-ready»); habría que escribir la preparación BTC 1h y no está verificada su viabilidad en CPU de GitHub; (3) más parámetros efectivos que datos: riesgo alto de sobreajuste; (4) el número de variantes se infla: checkpoints × tasa de aprendizaje (≥ 5 intentos); (5) el ajuste fino de TimesFM 2.5 no está verificado; (6) tardaría los mismos ≈ 200–250 días prospectivos para confirmar.
- Condición para reabrirla: que KT-006 muestre que al menos una regla pasa, o que el usuario lo pida expresamente con la advertencia anterior.
- Folds (si se hiciera): 3 ventanas expansivas con embargo de 24 h entre entrenamiento y validación (el piloto purga 1 barra, válido para horizonte 1; para 4 h el embargo mínimo es 4 barras; ver §8).
- n: 1200 bases prospectivas por comparación pareada: MDE ≈ 4,0 puntos si la discordancia entre modelos es 20 % (supuesto), ≈ 4,9 si 30 %. Variantes DSR: +5 como mínimo.
- Costos y comparación: iguales a A y B.

### Opción E — Control clásico entrenado en BTC (Ridge) con el código del piloto  **[descriptivo dentro de KT-006]**

Frase falsable: «Ridge sobre rasgos simples (retornos de 1, 2, 3, 4 h y volumen normalizado) entrenado hasta 2026-10-20 tiene acierto balanceado > 50 % en las mismas bases». Solo descriptivo (no entra en Holm). Sirve para saber si hay algo que Kronos y TimesFM no superan. +1 variante declarada.

## 5. Hipótesis falsable de la recomendación (KT-006)

Familia confirmatoria de **2 pruebas**, una por regla candidata m ∈ {C1, C2}:

- H1_m: en BTCUSDT 1h, sobre bases prospectivas sin solape (hora UTC múltiplo de 4), el signo de la regla m a 4 h tiene **acierto balanceado > 50 %**.
- H0_m: acierto balanceado ≤ 50 %.

Acierto balanceado = ½·(acierto en bases con r > 0 + acierto en bases con r < 0), r = cierre de la 4.ª vela siguiente / C₀ − 1 (misma definición que KT-002). Vale 50 % para cualquier regla constante («siempre sube», «siempre baja»), así que superarlo es superar a «siempre sube» sin que la deriva del período decida (argumento de KT-004p §1.2).

## 6. Métrica, regla de aprobado, bootstrap, potencia y calendario

- **Muestra**: filas de `data/kt006/predicciones.csv` con `base_open_utc > T_registro` (estricto), hora UTC múltiplo de 4, primera fila por base; se descartan r = 0 y reglas con signo indefinido. Se ordenan por `base_open_utc` y se toman las **primeras 1200 puntuadas**. Si C1 y C2 tienen n distinto, cada una usa sus filas válidas y se informa.
- **Bootstrap**: el de KT-004p sin cambios: bloques circulares de 42 filas, 10 000 réplicas, `numpy.random.default_rng(42)`, una sola matriz de índices para ambas reglas, Python 3.13, numpy 2.5.4, pandas 3.0.6 (`docs/evidencia/KT-001/requirements-resolved.txt`). p unilateral = (1 + #{réplicas con acierto balanceado ≤ 0,50}) / 10 001.
- **Corrección**: Holm sobre 2 pruebas, α unilateral familiar 0,025 (escalones 0,0125 / 0,025).
- **APRUEBA** cada regla cuya H0 rechaza Holm. **NO APRUEBA** si no. Aprobar significa «la regla distingue subidas de bajadas mejor que una moneda a 4 h en BTC»; no significa rentable, ni mejor que KT-002, ni apta para operar.
- **Señal de fragilidad (descriptiva, no cambia el veredicto)**: si el acierto balanceado sin el mejor de los 4 bloques es ≤ 50 %, el veredicto se publica como «APRUEBA (frágil)». También se informa t-stat con y sin el bloque dominante (regla del proyecto).
- **Efecto de planificación**: 55 % (rebajado desde 56,9 % por maldición del ganador, posible contaminación del post corte de KT-003, y porque KT-002 hoy marca 51,3 % para Kronos con n solapado).
- **Potencia** (aproximación normal; EE = 0,5/√n_ef; factor 1,25 por dependencia intradía → n_ef = 960 para n = 1200): escalón más exigente α = 0,0125.

| Efecto verdadero | 54 % | 55 % | 56 % |
|---|---|---|---|
| Potencia con n = 1200 | ≈ 0,59 | ≈ 0,80 | ≈ 0,93 |

  MDE al 80 % ≈ 5,0 puntos. Efectos menores no se detectan. Fórmula reproducible, no es simulación; KT-004p simuló la misma regla con bootstrap (potencia 0,88–0,89 a 55 % con n = 1310 y α 0,0083).
- **Ritmo**: 6 bases por día. Con `T_registro` ≈ 2026-12-15 (fecha estimada, depende de las auditorías y del desarrollo): 100 % de cobertura ≈ 200 días → 2027-07-03; 80 % ≈ 250 días → 2027-08-22.
- **Vigía de cobertura** a los 7 días (solo cuenta bases): si < 80 %, se recalculan fechas y se anota.
- **Fecha límite 2027-12-31**: con n ≥ 500 se evalúa con la misma regla etiquetada «potencia menor»; con n < 500, solo descriptivo.
- **Sin miradas intermedias con poder de decisión.** Un solo análisis al final.

## 7. Cómo se compara con «siempre sube» y con KT-002, sin tocar KT-002

- **«Siempre sube»**: (i) inferencial, vía el acierto balanceado de §5 (50 % por construcción); (ii) descriptivo: acierto bruto de cada regla y de «siempre sube» sobre las mismas filas, con Wilson 95 % y McNemar exacto pareado (como en KT-002 Enmienda A). No hay guarda adicional (KT-004p la quitó por pérdida de potencia).
- **KT-002**: solo lectura de `data/kt002/predicciones.csv`, solo filas con `base_open_utc > T_registro(KT-006)`, hora UTC múltiplo de 4 y con `actual_ret` ya escrito, unidas por `base_open_utc` a las de KT-006. Se informa la diferencia pareada de acierto balanceado (C1 − Kronos KT-002; C2 − KT-001 KT-002) con IC 95 % por el mismo bootstrap y la tabla de discordancias. **Es descriptivo y no puede declararse «mejora sobre KT-002» como resultado confirmatorio**: con discordancia de 20–30 % el MDE pareado es ≈ 4,0–4,9 puntos, y la discordancia real no está medida. Si KT-002 omite una base, esa base no entra en la comparación (sí en la primaria de KT-006).
- Los hashes de `tools/kt002_prospectivo.py`, `model_revisions.json` y `requirements-resolved.txt` se fijan en el registro (como en KT-004p §6). Si cambian, la comparación con KT-002 se rotula «no comparable»; la primaria de KT-006 no depende de KT-002.

## 8. Reuso del trabajo de entrenamiento piloto (no se duplica)

- `tools/kronnos_entrenamiento_piloto.py`: Ridge (alpha 1,0) con rasgos de retornos y log1p(volumen), partición temporal 70/30, validador de barras. **Se reusa su validación de velas y su Ridge** para el control E. Cambios que necesita (los hace el desarrollador, no yo): horizonte 4 h con embargo de 4 barras (hoy solo 1), objetivo = signo de retorno a 4 h, quitar o estandarizar `log1p(volumen)` (es un nivel no estacionario), y corregir los indicadores fijos `training_data_synthetic: True` y `data_source_provenance: INPUT_NOT_AUTHENTICATED` cuando se alimente con datos reales sellados (hoy mentirían).
- `tools/kronnos_freqai_native_fit.py`: LightGBM de FreqAI con `--historical-csv`; purga solo 1 etiqueta (válido para horizonte 1). **No se usa** en KT-006 (solo duplicaría E con otro motor y suma una variante). Queda como alternativa si el desconfiado prefiere un control no lineal.
- `tools/kronnos_binance_vision_archive.py`: descarga mensual con SHA-256 contra `.CHECKSUM`. Se reusa para el control E; no hace falta para la corrida prospectiva.
- Datos sellados: `data/kt003/btcusdt_1h.csv.gz` (SHA-256 `c3ccfb0a077574b9aa9611e0589c01ed1f679adb9caa38889ffd7f1b36f2cc61`, KT-003 Enmienda D). Sirve para fijar sK, sT y entrenar E; **no** sirve como holdout.

## 9. Datos públicos exactos y licencias

| Dato / código | Fuente exacta | Licencia | Estado |
|---|---|---|---|
| Velas prospectivas BTCUSDT 1h | `https://data-api.binance.vision/api/v3/klines` (igual que KT-002) | Términos de uso de Binance | **No verificado** el texto de los términos para uso de investigación |
| Velas verificación final | ZIP mensuales/diarios `https://data.binance.vision/data/spot/{monthly,daily}/klines/BTCUSDT/1h/` con `.CHECKSUM` (SHA-256) | Ídem | **No verificado**; intenté `binance/binance-public/master/LICENSE` y devolvió 404, no se pudo confirmar licencia del repositorio |
| Copia histórica en el repo | `data/kt003/btcusdt_1h.csv.gz` (derivada de data.binance.vision) | Ídem | No verificado que la redistribución esté permitida; el repo es público |
| Kronos (código) | `github.com/shiyu-coder/Kronos`, fijado a `67b630e6…` | MIT (leí `LICENSE` en `master` el 2026-11-10, no en el commit fijado) | Parcialmente verificado |
| Kronos pesos | `NeoQuasar/Kronos-small` `901c26c1…`, tokenizer `0e011738…` | Licencia de los pesos **no verificada** | No verificado |
| TimesFM (código) | `github.com/google-research/timesfm`, `e51928e2…` | Apache-2.0 (leí `LICENSE` en `master` el 2026-11-10, encabezado) | Parcialmente verificado |
| TimesFM pesos | `google/timesfm-2.5-200m-pytorch` `1d952420…` | **No verificado** | No verificado |
| Referencias externas (Lumina, etc.) | — | CC BY-NC 4.0 (norma 2026-10-29): **no se copia código** | No se usan |

Para el ajuste fino (Opción D) haría falta además verificar la licencia de los pesos derivados; no se entra en eso ahora.

## 10. Costos (marco de riesgo v1.0, `COSTOS_BTCUSDT.md`)

- Ida y vuelta base **0,30 %** (2 × (0,10 comisión + 0,02 spread + 0,03 deslizamiento)); estrés x2 = **0,60 %**. Solo la comisión está publicada; spread y deslizamiento son SUPUESTOS (Binance bloqueada desde el proxy cuando se midió, 2026-10-21). Los borradores KT usan 0,20 %; para KT-006 manda el marco (0,30 %).
- A 4 h la mediana de \|ret\| en 2026 es 0,377 %; el acierto mínimo para cubrir 0,30 % es ≈ 89,8 % y para 0,60 % ≈ 129,6 % (imposible). **KT-006 no apunta a operar** y no puede aprobar una estrategia. Cualquier uso con dinero exige otra variante, otro horizonte (a 24 h el mínimo sería ≈ 63 %), la Fase 0 completa, límites de riesgo (caída ≤ 6,5 %, resultado neto positivo con costos x2) y decisión explícita del usuario.
- Se reportan, descriptivo: retorno direccional bruto medio (signo × r) y neto de 0,30 % / 0,60 % por base, para dejar constancia de que son negativos si el acierto ronda 55 %.

## 11. Costo operativo en GitHub Actions

- Patrón KT-005p §7–8: workflow nuevo `kt006.yml` (a escribir por el `jefe-desarrollo`, no por mí), `concurrency: kt006`, disparado por push sobre `data/kt002/despertar.txt` (solo lo lee), escribe solo en `data/kt006/`; hash de `tools/kt006_*.py` y `model_revisions.json` fijados en el registro; aborta si cambian o si se reescribe un pronóstico guardado.
- Cómputo: una inferencia Kronos (con captura de 20 muestras) + una de TimesFM por base de 4 h; KT-002 tarda ≈ 33–60 s por base con ambos. Estimo 1–3 min por base, ≈ 6–18 min de CPU por día, **no medido**. Si se usa un job vivo por falta de cron (como KT-002), serían ≈ 1440 min de runner por día, gratis mientras el repo sea público (**no reverificado hoy**); si el repo pasa a privado, hay que decidir qué corrida se pausa.
- Riesgo operativo: otro job que empuja a `master`; mismo ciclo `pull --rebase` con reintentos que KT-002/KT-005p. Un push perdido cuenta como hora omitida.
- No se cancela ninguna corrida (norma del propietario).

## 12. Qué NO se pudo verificar

1. Cómo extraer las 20 muestras individuales de Kronos en el código a la revisión `67b630e6…` (el README solo dice que `predict` las promedia) y si coinciden con `predict(sample_count=20)`.
2. Que `tfm.forecast` devuelva los cuantiles en la forma que asumo (KT-002 los desecha con `_`).
3. Licencia de los datos de Binance, de los pesos de Kronos y de los de TimesFM; licencia de MIT/Apache solo vista en `master`.
4. Viabilidad y tiempo del ajuste fino de Kronos en CPU de GitHub con BTC 1h (el pipeline oficial es de Qlib diario con acciones A), y existencia de un camino oficial de ajuste fino para TimesFM 2.5.
5. Valores exactos de sK y sT; la proporción de días por régimen; el porcentaje de concordancia entre voto y media; la discordancia entre modelos (todas son supuestos de potencia).
6. Costos reales de spread y deslizamiento; minutos de Actions por día de KT-006.
7. Que el post corte de KT-003 y la historia previa no estuvieran en el entrenamiento de TimesFM/Kronos (Enmiendas C/D de KT-003).
8. El bloque «sin_solape» de KT-002: no lo vi; la cifra de 51,3 % es del conjunto solapado.

## 13. Riesgos de sobreajuste y conteo de intentos

- La idea (voto, normalización) sale de leer resultados ya vistos: **post hoc**, declarado. Solo se confirma con bases posteriores a `T_registro`.
- Sin parámetros libres en C1 y C2. Los únicos números fijados con datos vistos son sK y sT (escala), y se escriben antes de la primera base.
- KT-006 y KT-004p/KT-005p (si se registran) usan las mismas fechas futuras con preguntas distintas; se declara la superposición.
- «Maldición del ganador»: Kronos fue el mejor de 3 modelos en el período de donde sale el efecto.
- Conteo del frente Kronos/TimesFM: KT-001/002/003 (1 familia, misma configuración) + KT-004 multiactivo (1, no pasa) + **KT-006: +2 confirmatorias (C1, C2)**, +1 control clásico (E, descriptivo), +6 cortes de régimen (descriptivos, sin prueba). Si luego se registran KT-004p (+1) y KT-005p (+1 o +2), el total es mayor. Opción D, si se abre, suma ≥ 5. DSR (≥ 0,95) no aplica a una métrica de acierto sin estrategia, pero este conteo es el N que habría que usar si algún día se evalúa una estrategia basada en estos modelos.
- Se declara que miré 5 opciones (A–E) y descarté o difirí 3 (C confirmatoria, D, pesos ajustados) por razonamiento, sin correrlas.

## 14. Recomendación

**Hacer**: registrar KT-006 con Opciones A + B (voto y ensemble normalizado), con Holm de 2, n = 1200, control clásico E y régimen como tablas descriptivas. Es lo único que cambia lo que se mide (guarda lo que hoy se tira) sin tocar KT-002, sin entrenamiento y con costo de desarrollo bajo.

**No hacer**:
- No ajuste fino de Kronos ni TimesFM ahora (Opción D): poca información nueva, alto riesgo y costo, y confirmación igual de lenta.
- No ajustar pesos ni umbrales (regresión logística, Platt, grillas) sobre los datos de KT-003 o KT-002 ya vistos; cualquier calibración se entrena con datos de KT-006 y se confirma en datos posteriores, como variante nueva.
- No filtro de régimen confirmatorio ni «solo si coinciden» como prueba primaria: sin potencia y sin evidencia previa.
- No sacar TimesFM de la prueba ni reemplazarlo; no duplicar el brazo de log-retornos de KT-005p.
- No leer resultados intermedios de KT-006 con poder de decisión; no usar los datos de KT-002 hasta 2026-11-10 como confirmación.
- No decir «Kronos/TimesFM especializados en BTC» como resultado: lo que KT-006 puede concluir es «estas reglas ven o no ven dirección a 4 h». Ninguna conclusión es de rentabilidad.

## 15. Qué decide el usuario (o el gerente, según `CLAUDE.md`, si el desconfiado aprueba sin ALTOS ni MEDIOS)

1. Si acepta A + B (recomendado) o prefiere también abrir la Opción D (ajuste fino) pese a lo dicho.
2. Si acepta efecto de planificación 55 %, n = 1200, fecha estimada julio–agosto de 2027 y límite 2027-12-31.
3. Si acepta una corrida nueva viva en Actions (gratis mientras el repo sea público) y, si KT-005p se registra, dos corridas adicionales a KT-002.
4. Qué costo usa como referencia (0,30 % del marco, no 0,20 %).
5. Si autoriza verificar las licencias de datos y pesos antes de registrar (pendiente de §12).

## 16. Resumen sencillo para el usuario

- Especializar los modelos en BTC con ajuste fino no vale la pena por ahora: casi no hay datos nuevos y todo el pasado ya está visto.
- Lo que sí se puede hacer es guardar lo que hoy se tira (las 20 «opiniones» de Kronos) y probar dos reglas simples y fijas: votar con esas 20 y combinar los dos modelos con la misma escala.
- Se mide hacia adelante, en paralelo con KT-002 (que no se toca): unos 7 a 9 meses para 1200 pronósticos.
- Si pasa, quiere decir que ve algo de la dirección a 4 horas; para ganar dinero tras comisiones haría falta acertar casi siempre, así que no se opera.
