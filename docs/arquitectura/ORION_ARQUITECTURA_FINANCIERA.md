# ORION–ATLAS: arquitectura, componentes reutilizados y piloto BTCUSDT

Fecha: 2026-10-24. Autor: Claude (Anthropic). Revisor: ChatGPT (pendiente). Autoridad: el propietario.
Rama: `research/orion-atlas-20261024`. **Solo investigación**: sin órdenes, claves ni dinero real.
No toca KT-002 ni el PR #32; está separado por directorio (`atlas/`, `research/atlas/`) y lo prueban `tests/test_atlas.py` y `.github/workflows/atlas-ci.yml`.

## 1. Repositorios externos (hito 1)
Inspección del 2026-10-24:
- clon sin contenidos (`--filter=blob:none --no-checkout`) en una carpeta temporal fuera del repositorio;
- lectura puntual de archivos con `git show`, más `LICENSE`, `pyproject.toml` y PyPI.

**Nada se copió, instaló ni ejecutó.** ATLAS reimplementa en código propio solo las ideas marcadas como «adaptar», así que no hay obligaciones de licencia. TradingAgents ya se instaló y probó aislado en los pilotos B2–B4 (PR #25 a #28).

| Repositorio @ commit | Licencia | Archivos concretos revisados | Decisión y motivo |
|---|---|---|---|
| TauricResearch/TradingAgents @ `e8f5503` | Apache-2.0 | `tradingagents/dataflows/date_window.py` (`as_of`, `coverage_gap`); `agents/researchers/bull_researcher.py` y `bear_researcher.py`; `agents/risk_mgmt/*_debator.py` | **Adaptar ideas**: (a) «sin cobertura no es vacío», aplicada en `atlas/procedencia.cobertura_faltante`; (b) debate a favor y en contra, aplicado en `atlas/contradicciones.revisar` con **reglas deterministas en vez de LLM**. No se usa su grafo: decide con LLM y usa yfinance |
| OpenBB-finance/OpenBB @ `78020ee` | Apache-2.0 | `openbb_platform/core/openbb_core/provider/abstract/fetcher.py` (`Fetcher`: `transform_query` → `extract_data` → `transform_data`); `standard_models/crypto_historical.py`, `world_news.py`, `economic_calendar.py` | **Adaptar el patrón** en `atlas/datos.VelasArchivo`. Adoptar el paquete queda para cuando haga falta un activo fuera de cripto: suma muchos proveedores con clave |
| Ruixing0328/multi-agent-investment-research-system @ `635289c` | MIT | `data_platform/freshness.py` (`classify_freshness`, que mide desde `effective/observed/available_at`); `data_platform/merge_contract.py` (no se escribe sin atribución) | **Adaptar ideas**: `atlas/procedencia.frescura` medida desde `utilizable_utc`, y la fuente obligatoria en cada `Registro`. El proyecto está en V1 con integraciones incompletas, según su README |
| virattt/ai-hedge-fund @ `4e1657d` | MIT | `pyproject.toml` (5 proveedores LLM y financialdatasets.ai, de pago) | **Descartar.** Su README dice «not intended for real trading»; decide por opinión de LLM, lo que choca con la regla 8 |
| freqtrade/freqtrade @ `12e0878` | GPL-3.0 | `freqtrade/strategy/interface.py` (`IStrategy`), `optimize/backtesting.py`, `freqai/freqai_interface.py` | **Candidato para el hito 5, como herramienta externa aislada** (dry-run o backtest), sin integrar código: la GPL contagia. Riesgos: hyperopt (sobreajuste) y modo en vivo con ccxt (prohibido) |
| microsoft/qlib @ `5435523` | MIT | `qlib/data/dataset/handler.py`, `workflow/recorder.py`, `backtest/exchange.py` | **Referencia** para la ingeniería de factores y el registro de experimentos. Pesado (Redis, Mongo, mlflow) y orientado a acciones |
| nautechsystems/nautilus_trader @ `9e59d7a` | LGPL-3.0 | Motor de eventos (README; 5 293 archivos, Rust/Cython) | **Referencia o candidato para el hito 5**: simulación con microestructura, sin adaptadores en vivo |

## 2. Arquitectura implementada
Cada pieza es pequeña, solo usa la biblioteca estándar y `jsonschema` para validar, y se prueba sola.

| Subsistema (orden) | Módulo | Qué hace (implementado) | No hace |
|---|---|---|---|
| A. Data Intelligence | `atlas/procedencia.py`, `atlas/datos.py` | `Registro` con fuente, identificador, evento, publicación, recepción, hora de uso, calidad, hash y licencia. Adaptadores de solo lectura para velas, spread, predicciones de KT-002 (oculta resultados puntuados después del corte) y eventos. Ante un fallo, devuelve cobertura faltante. `discrepancia()` conserva las dos fuentes | Descargar de internet (lee las copias de la guardia); noticias reales (no hay fuente con hora de publicación verificable configurada) |
| B. Analytics | `atlas/analitica.py` | Módulos independientes: tendencia (reglas del analista), volatilidad, volumen, liquidez, predictivo (Kronos, TimesFM y KT-001 con su historial **al corte**) y eventos. Cada uno etiquetado como hecho, inferencia, hipótesis causal o ausente | Macro y fundamental (sin fuente confiable con fecha: se declara ausencia) |
| C. Thesis Engine | `atlas/tesis.py`, `atlas/piloto.py` | Tesis con todos los campos de la orden. 8 estados con transiciones válidas. RECHAZADA→ACEPTADA es imposible sin evidencia nueva y un revisor registrado que no sea un LLM; sin preregistro no hay aceptación. Registro JSONL encadenado por hash | — |
| D. Contradiction Engine | `atlas/contradicciones.py` | Las 10 preguntas de la orden y 4 conclusiones (FAVORABLE_CONTINUAR, CONTRADICTORIA, INCONCLUSA, INSUFICIENTE). La decisión es solo de investigación (CONTINUAR o ABSTENERSE). FAVORABLE exige 2 o más módulos independientes a favor, una señal predictiva con ventaja demostrada y un movimiento mayor que el costo | Emitir órdenes |
| V. Explicación de predicciones | `atlas/piloto.py` (`explicacion_prediccion`) | Separa hechos comprobados, inferencias, hipótesis causales no demostradas, información ausente y decisión | Prospectivo: los cortes actuales son retrospectivos y quedan marcados así |
| E. Strategy Lab | contrato `strategy_spec.schema.json` | Contrato que prohíbe reglas basadas en la salida de un LLM (`usa_salida_llm: false`) | Simulación (hito 5, bloqueado: ninguna hipótesis pasó la Fase 0) |
| F. Portfolio Intelligence | — | — | Hito 6, bloqueado: requiere más de una estrategia aprobada |

**Regla propia de ATLAS** (no cambia KT-002): una señal predictiva cuenta como respaldo solo con n sin solape ≥ 100 y McNemar p < 0,05 contra «siempre sube», usando únicamente los resultados conocidos al corte.

**Contratos** (`docs/arquitectura/contratos/`, JSON Schema 2020-12): `registro` (datos de mercado, noticias, eventos macro, pronósticos), `evidencia` (evidencia de los analistas), `tesis` (registro de tesis más revisión de contradicciones) y `strategy_spec`. `portfolio_risk`, `experiment_results` y `audit_log` quedan para los hitos 5 y 6. Hoy el registro de auditoría es la cadena JSONL y git.

## 3. Piloto BTCUSDT (hito 4): resultados reales
Datos: copias públicas de Binance que guarda la guardia (`data/mercado/btc_1d.json`, `spread_btcusdt.csv`) y `data/kt002/predicciones.csv` en solo lectura. Para cada corte se guardan la tesis y la **instantánea exacta de entradas** (`research/atlas/salidas/`), y ambas quedan en `research/atlas/registro/tesis.jsonl`.

| Corte (elegido antes de mirar) | Predicción evaluada | Conclusión | Motivos |
|---|---|---|---|
| 2026-10-21 00:00Z | KT-001 baja (−0,13 %) desde la vela de las 21:00 | **INCONCLUSA → ABSTENERSE** | El régimen diario ALCISTA la contradice; Kronos y TimesFM no coinciden; el movimiento es menor que el costo de 0,30 %; historial sin solape al corte n=0; sin cobertura de noticias ni spread |
| 2026-10-22 00:00Z | KT-001 sube (+0,04 %) desde la vela de las 22:00 | **INCONCLUSA → ABSTENERSE** | Historial al corte: Kronos 0/4 y KT-001 0/4 contra «siempre sube» 4/4; los modelos no coinciden; el movimiento es menor que el costo |

En los dos cortes el sistema hizo lo que pide la orden: **no pudo justificar la tesis y se abstuvo**. No hubo ningún dato posterior al corte. `predicciones.csv` quedó con el mismo hash.

## 4. Pruebas (`tests/test_atlas.py`, 24, todas en verde)
- **Contratos:** los esquemas son válidos, la salida del piloto cumple su contrato y una estrategia con LLM es rechazada.
- **Sin look-ahead:** se excluyen las velas que cierran después del corte, se ocultan los resultados puntuados después del corte, y un registro futuro inyectado vuelve la conclusión INSUFICIENTE.
- **Casos adversos:**
  - noticias contradictorias → CONTRADICTORIA;
  - fuente sin hora verificable → excluida y señalada;
  - datos viejos → INSUFICIENTE;
  - fallo de proveedor → INSUFICIENTE y ausencia declarada;
  - modelos en desacuerdo → señalado y abstención;
  - predicción sin respaldo → abstención;
  - sin liquidez → INSUFICIENTE;
  - tendencia contraria → abstención;
  - FAVORABLE solo con ventaja demostrada.
- **Reproducibilidad:** misma entrada, misma huella. La instantánea reproduce la tesis aunque cambien los datos vivos, y las salidas publicadas se reproducen.
- **Procedencia:** la discrepancia conserva las dos fuentes; cobertura faltante no es lo mismo que ausencia.
- **Estados y registro:** reglas de transición; la cadena de hash detecta alteraciones.
- **Aislamiento:** no se escribe en `data/kt002` y su hash no cambia; ATLAS no importa librerías de ejecución, red ni claves.

## 5. Hitos
| Hito | Estado | Evidencia o bloqueo | Decisión |
|---|---|---|---|
| 1. Investigación y matriz | Hecho (lectura de código, sin ejecución) | Sección 1 | Continuar |
| 2. Arquitectura, contratos, riesgos | Hecho | Secciones 2 y 6, contratos | Continuar |
| 3. Registro de tesis y motor de contradicciones | Implementado y probado localmente | 24 pruebas; falta el CI del PR y la auditoría | Revisión |
| 4. Piloto BTCUSDT | Funcional con datos reales, retrospectivo | Sección 3 | Revisión. Siguiente paso: tesis **prospectivas** registradas antes de que venza el horizonte |
| 5. Laboratorio de estrategias | **Bloqueado** | Ninguna hipótesis pasó la Fase 0 (HP-001 a HP-007 descartadas); simular sin hipótesis sería sobreajuste | Esperar |
| 6. Portafolio | **Bloqueado** por el hito 5 | — | Esperar |
| 7. Integración con el panel ORION | No iniciado | Requiere la aprobación de los hitos 3 y 4 | Después |

## 6. Riesgos y controles
| Riesgo | Control implementado |
|---|---|
| Fuga de información futura | `utilizable_utc` en cada registro, filtros en los adaptadores y pruebas de inyección |
| LLM que inventa o decide | El motor no usa LLM; el contrato de estrategia prohíbe reglas basadas en LLM; las transiciones exigen revisor |
| Causalidad atribuida a noticias | Los eventos son siempre `hipotesis_causal`, nunca evidencia a favor; si son mixtos, la conclusión es CONTRADICTORIA |
| Contaminar KT-002 | Solo lectura, escritura prohibida en `data/kt002`, comprobación de hash en pruebas y CI |
| Muestra pequeña | Regla de ventaja (n ≥ 100, p < 0,05). Hoy ningún modelo la cumple |
| Licencias | Sin código ajeno; GPL y AGPL descartadas para integrar |
| Costos | $0: el CI corre en un repositorio público con runners estándar; sin APIs pagas; el piloto no usa LLM |

## 7. Valor frente al ORION actual
Aporte de ATLAS:
- un formato verificable para responder «¿esta predicción merece atención?»;
- disciplina de punto en el tiempo;
- abstención por defecto.

Lo que todavía **no** aporta: evidencia financiera. Sin una hipótesis que pase la Fase 0 no hay simulación, y sin simulación neta de costos no hay rentabilidad que afirmar.
