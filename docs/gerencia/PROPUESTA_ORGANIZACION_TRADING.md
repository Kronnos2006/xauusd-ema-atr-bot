# Propuesta: organizarnos como una firma de trading cuantitativo

2026-10-21. Autor: Claude, a pedido del usuario. Estado: **propuesta**, nada aprobado ni ejecutado. Sin dinero real ni órdenes: esto prepara el camino, no lo recorre.

## 1. Cómo se divide una firma grande de trading cuantitativo

| Departamento | Qué hace | Por qué es independiente o no |
|---|---|---|
| Investigación (research) | Busca y prueba ideas de señales con datos | Propone; nunca se aprueba a sí misma |
| Gestión de portafolio | Decide qué estrategias corren y con cuánto | Responde a la dirección |
| **Riesgo** | Pone límites (pérdida máxima, tamaño, exposición) y puede **apagar** cualquier estrategia | **Independiente**: nadie de trading le da órdenes |
| Ejecución / costos | Mide y baja comisiones, spread y deslizamiento | Técnica |
| Datos | Consigue, limpia y valida los datos | Técnica |
| Tecnología | Código, sistemas y automatización | Técnica |
| Cumplimiento / auditoría | Revisa que todo siga las reglas | **Independiente** |
| Inteligencia de mercado | Lee macro, noticias y flujos | Informa; no decide trades |
| Operaciones | Que todo corra a horario | Técnica |
| Reportes | Informa a los dueños | Responde a la dirección |

El principio: **quien propone no aprueba, y quien arriesga no controla el riesgo.**

## 2. Lo que ya tenemos y lo que falta

| Firma grande | Nuestro equipo | Estado |
|---|---|---|
| Investigación | mejorador | ✓ |
| Cumplimiento / auditoría | desconfiado (independiente) | ✓ |
| Inteligencia de mercado | analista + 3 ayudantes (independiente) | ✓ |
| Datos | vigía de datos | ✓ |
| Operaciones | jefe de operaciones | ✓ (solo lectura) |
| Tecnología | jefe de desarrollo + 3 ayudantes | ✓ |
| Innovación | jefe de innovación + noticias | ✓ |
| Reportes | jefe de documentación + gerente | ✓ |
| **Riesgo** | — | **Falta.** Propuesta: crear `jefe-riesgo`, independiente como el desconfiado |
| **Ejecución / costos** | — | **Falta.** Propuesta: ayudante `riesgo-costos` (comisiones, spread y deslizamiento reales de BTC) |
| **Gestión de portafolio** | — | Todavía no hace falta: no hay estrategias. Se crea solo si una medición pasa todos los filtros |

## 3. Plan de acción mientras esperamos los datos de KT-002

KT-002 necesita unos 100 resultados sin solape (≈ 17 días) para una idea general y unos 780 (≈ 4 meses) para distinguir 55 % de 50 %. Mientras tanto:

**Semana 1 — que la medición sea confiable**
1. Desarrollo arregla los huecos de KT-002 (avisos de falla, despertador cada 4 h), sin cambiar el cálculo. Aprobado por el gerente.
2. Arreglar el analista: el gerente llama a los 3 ayudantes directamente, y una copia diaria de velas de BTC en el repo (vía GitHub Actions) para no depender de Binance desde la sesión.

**Semanas 1–2 — el puente entre «acierta» y «gana» (descriptivo, sin dinero)**
3. **Modelo de costos de BTC** (riesgo-costos): comisión real de Binance por lado, spread y deslizamiento medidos con datos públicos. Resultado: cuánto tiene que moverse BTC en 4 h para cubrir costos.
4. **Umbral de equilibrio** con datos de KT-003 ya vistos (descriptivo): qué porcentaje de acierto hace falta según el tamaño de los movimientos previstos. KT-003 ya indica que los movimientos previstos suelen ser menores que los costos; esto lo cuantifica.
5. **Marco de riesgo escrito antes de cualquier estrategia** (jefe de riesgo): pérdida máxima por día y total, tamaño máximo, condiciones para apagar todo. Sin esto no se pasa nunca a dinero real.

**Semanas 2–4 — ideas nuevas, con disciplina**
6. Corregir y re-auditar KT-004 y KT-005 (ya en curso).
7. Evaluar horizontes más largos (por ejemplo, 24 h), donde los movimientos superan más fácilmente los costos, como diagnóstico histórico registrado antes de ver datos.
8. Si el usuario lo decide: diseñar una **simulación en papel** (paper trading, sin órdenes) con reglas, costos y límites de riesgo fijados de antemano. Es una hipótesis nueva: pasa por `hypothesis-gate`, desconfiado y riesgo, y la decide el usuario.

**Puertas de decisión (fijas desde hoy)**
- A los ~100 resultados sin solape: revisión intermedia, solo descriptiva.
- A los ~780: conclusión de KT-002 según su registro previo.
- Dinero real: nunca sin (a) un resultado que pase el registro previo, (b) paper trading con costos positivo, (c) aprobación del jefe de riesgo y del desconfiado, y (d) decisión explícita del usuario.

## 4. Qué decide el usuario
1. ¿Crear el **jefe de riesgo** (independiente) con el ayudante **riesgo-costos**?
2. ¿Aprobar el plan de las semanas 1–4?
3. ¿Querés que se diseñe la simulación en papel (punto 8), o esperamos a los ~100 resultados?
