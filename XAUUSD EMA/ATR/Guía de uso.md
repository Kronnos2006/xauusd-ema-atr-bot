---
tipo: guia
estado: vigente
actualizado: 2026-10-20
tags: [guia, uso, operacion]
---

# Guía de uso

Índice: [[00 Inicio]] · Ver también [[Automatizaciones]] · [[Agentes del proyecto]] · [[Mapa del repositorio]]

Cómo usar el proyecto en el día a día, sin tener que acordarse de los detalles técnicos. Repositorio: [Kronnos2006/xauusd-ema-atr-bot](https://github.com/Kronnos2006/xauusd-ema-atr-bot).

> [!warning] Reglas que no cambian
> - El proyecto **no ejecuta órdenes ni usa capital real**.
> - Ninguna hipótesis nueva se prueba sin **registro previo** escrito antes de ver datos, y sin el **OK explícito del usuario**.
> - Lo que corre no se toca: un cambio es siempre una **variante nueva** (KT-004, KT-005…).

---

## 1. Ver cómo va todo

**Panel en vivo (lo más rápido).** [Panel KT-002 BTC](https://claude.ai/artifact/2CJcKXjLjG2usbvqnp3nDN), en la app de Claude.
- *BTC en vivo*: precio, cambio en 24 h y gráfico de 24 h o 7 días. Encima van las predicciones: el punto negro es dónde se predijo, las líneas a qué precio esperaba cada modelo en 4 h, y ✓/✗ marca el resultado real (○ si está pendiente). Tocá una línea para ver el detalle.
- *Acierto de dirección*: % de acierto de cada modelo contra «siempre sube», con su intervalo de confianza.
- *Predicciones y resultados*: tabla de las últimas 48 horas.
- *Cambios en los modelos*: qué variante cambió qué.
- El panel lee los datos con el conector **TinyFish**; quien lo abra necesita tenerlo conectado.

**Resúmenes en el repo.**
- `data/kt002/resumen.md`: acierto en vivo (KT-002).
- `data/kt003/resumen.md`: resultado del diagnóstico histórico (KT-003).

**Notificaciones al celular.** Llegan a la app de Claude de cada teléfono donde esté abierta la cuenta del proyecto:
- *Desconfiado: auditoría diaria*, todos los días a las 6:33 a. m.
- *Vigía de Actions*, solo si algo se cayó y no pudo arreglarlo.

---

## 2. Qué corre solo

| Proceso | Qué hace | Dónde | Cada cuánto |
|---|---|---|---|
| KT-002 | Predice si BTC sube o baja en 4 h y puntúa al vencer | GitHub Actions | Cada hora (minuto 7 UTC) |
| Vigía de Actions | Revisa los workflows; relanza solo lo parado o fallido | Tarea programada de Claude | Cada 5 h |
| Auditoría diaria | El desconfiado revisa los datos nuevos y notifica | Tarea programada de Claude | 6:33 a. m. Costa Rica |
| Loggers MT5 (histórico) | EMA M15 y DFII10, solo lectura | Task Scheduler de la PC | Ver [[Infraestructura]] |

Detalle técnico en [[Automatizaciones]].

---

## 3. Lanzar o relanzar algo

**KT-003 (diagnóstico histórico).** Se lanza solo al editar `data/kt003/lanzar.txt` en `master`:
1. Primera línea `prueba`: descarga y sella los datos, mide tiempos y verifica equivalencias. No calcula aciertos.
2. Primera línea `completo`: corre el diagnóstico con los datos sellados (verifica el hash y aborta si cambian).
También se puede lanzar a mano desde GitHub → Actions → *KT-003* → *Run workflow*.

**Si una corrida falla en GitHub.** Entrá a la corrida y usá **Re-run failed jobs** (no *Re-run all jobs*): así se conservan las tareas que ya terminaron.

> [!tip] Si GitHub está traducido al español
> "Actions" puede aparecer como **Comportamiento**.

> [!caution] Cuidado con "En cola"
> La página de una corrida puede decir "En cola" aunque varias tareas estén corriendo, porque GitHub deja correr unas 11 a la vez. Antes de cancelar, abrí *Show all jobs* o el detalle de uso. El 2026-10-20 se canceló por error una corrida que estaba a punto de terminar ([[KT-003 — Diagnóstico histórico BTC#Incidentes]]).

**Detener algo.**
- KT-002: GitHub → Actions → *KT-002* → *Disable workflow*.
- Tareas programadas de Claude: en la app, en la lista de tareas programadas.

---

## 4. Proponer una mejora a los modelos

El flujo es siempre el mismo ([[Agentes del proyecto]]):
1. **Mejorador** estudia resultados y escribe la propuesta en `docs/propuestas/`.
2. **Desconfiado** la audita. Si hay problemas altos o medios, vuelve al mejorador.
3. **Vos** recibís un resumen de 3–5 líneas y decidís. Sin tu sí, no se ejecuta nada.
4. Se escribe el **registro previo**, después el código, y recién ahí se lanza.

Para pedirlo, basta con decirle a Claude: *"que el mejorador estudie los resultados y proponga una mejora"*.

---

## 5. Leer un resultado sin engañarse

- **Acierto de dirección no es ganancia.** A 4 h, los costos de ida y vuelta (~0,20 %) suelen ser mayores que el movimiento previsto. Para cubrirlos habría que acertar cerca del 66 %.
- **Mirá la referencia «siempre sube».** Si BTC subió más días de los que bajó, acertar 52 % puede no valer nada.
- **"Sin solape" es la cifra que cuenta en KT-002.** Las horas seguidas comparten 3 de 4 horas y no son independientes.
- **Tamaño de muestra.** Con 100 resultados el margen es de ±10 puntos; distinguir 55 % de 50 % requiere unos 780 resultados independientes.
- **Contaminación.** Kronos y TimesFM se publicaron en 2025: el histórico anterior puede estar en su entrenamiento.

---

## 6. Trabajo en la PC (MT5 y Python)

Para lo que corre localmente (backtests de XAUUSD/EURUSD, loggers MT5):
- Entorno: Python con `requirements.txt`; MT5 instalado y con sesión válida.
- Motor de investigación reproducible: `python -m research.engine --config research/config.example.yaml`.
- Tests: `python -m unittest discover tests`.
- Antes de cualquier backtest nuevo, la skill `hypothesis-gate` (Fase 0 y Fase 1). Ver [[Metodología]].
- Antes de tocar Task Scheduler o un logger en vivo, la skill `infra-ops-playbook`. Ver [[Infraestructura]].
