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
| Ruixing0328/multi-agent-investment-research-system @ `635289c` | MIT | `multi_agent_modular_investment_research_system/multi_agent_modular_investment_research_system/data_platform/freshness.py` (`classify_freshness`, que mide desde `effective/observed/available_at`); `data_platform/merge_contract.py` (no se escribe sin atribución) | **Adaptar ideas**: `atlas/procedencia.frescura` medida desde `utilizable_utc`, y la fuente obligatoria en cada `Registro`. El proyecto está en V1 con integraciones incompletas, según su README |
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
| C. Thesis Engine | `atlas/tesis.py`, `atlas/piloto.py` | Tesis con todos los campos de la orden y 8 estados. **Lo que garantiza el código:** (a) solo transiciones de la tabla; (b) el revisor tiene que estar en `REVISORES_REGISTRADOS` (propietario, desconfiado, jefe-riesgo, chatgpt-revision); (c) reabrir una tesis RECHAZADA exige evidencia estructurada (fuente, hora de uso y descripción); (d) sin `preregistro_hash` no hay ACEPTADA; (e) `Registro.anexar` valida el estado contra la última versión de la tesis; (f) cadena de hash más ancla externa (`ANCLA.json` y el PR) que detecta alteraciones, truncado y reescritura completa. **No garantiza** que la evidencia sea verdadera ni que el revisor nombrado haya revisado de verdad: eso lo controla la revisión humana del PR | Validar la verdad de la evidencia |
| D. Contradiction Engine | `atlas/contradicciones.py` | Las 10 preguntas de la orden y 4 conclusiones (FAVORABLE_CONTINUAR, CONTRADICTORIA, INCONCLUSA, INSUFICIENTE). La decisión es solo de investigación (CONTINUAR o ABSTENERSE). `fugas()` revalida cada registro, también los de una instantánea: hora de uso, hora del evento y resultados puntuados después del corte. Los casos INSUFICIENTE son: velas, predicción o spread faltantes o viejos; una fuga; falta de liquidez; o ninguna tesis direccional (predicción ausente o nula, sin dirección inventada). FAVORABLE exige 2 o más hechos independientes a favor, un modelo **a favor** con estudio confirmatorio aprobado y un movimiento mayor que el costo; un modelo con ventaja **en contra** cuenta como evidencia contraria. **Hoy FAVORABLE es inalcanzable con datos reales:** solo la tendencia tiene dirección y no hay ningún estudio confirmatorio aprobado | Emitir órdenes |
| V. Explicación de predicciones | `atlas/piloto.py` (`explicacion_prediccion`) | Separa hechos comprobados, inferencias, hipótesis causales no demostradas, información ausente y decisión | Prospectivo: los cortes actuales son retrospectivos y quedan marcados así |
| E. Strategy Lab | contrato `strategy_spec.schema.json` | Contrato que prohíbe reglas basadas en la salida de un LLM (`usa_salida_llm: false`) | Simulación (hito 5, bloqueado: ninguna hipótesis pasó la Fase 0) |
| F. Portfolio Intelligence | — | — | Hito 6, bloqueado: requiere más de una estrategia aprobada |

**Regla de ventaja, alineada con el preregistro de KT-002** (Enmienda A: «ninguna p se interpreta como prueba de edge»; distinguir 55 % de 50 % requiere unas 780 observaciones): los datos descriptivos de KT-002 **nunca** cuentan como ventaja. La p de McNemar se informa como descriptiva, sin corrección múltiple. Una señal cuenta como respaldo solo si figura en `ESTUDIOS_CONFIRMATORIOS` (hoy vacío): un estudio aparte, preregistrado y aprobado por el desconfiado y el propietario.

**Contratos** (`docs/arquitectura/contratos/`, JSON Schema 2020-12): `registro` (datos de mercado, noticias, eventos macro, pronósticos), `evidencia` (evidencia de los analistas), `tesis` (registro de tesis más revisión de contradicciones) y `strategy_spec`. `portfolio_risk`, `experiment_results` y `audit_log` quedan para los hitos 5 y 6. Hoy el registro de auditoría es la cadena JSONL y git.

## 3. Piloto BTCUSDT (hito 4): resultados reales
Datos: copias públicas de Binance que guarda la guardia (`data/mercado/btc_1d.json`, `spread_btcusdt.csv`) y `data/kt002/predicciones.csv` en solo lectura. Para cada corte se guardan la tesis y la **instantánea exacta de entradas** (`research/atlas/salidas/`), y ambas quedan en `research/atlas/registro/tesis.jsonl`.

| Corte | Predicción evaluada | v0.1 | **v0.2 (vigente)** | Motivos |
|---|---|---|---|---|
| 2026-10-21 00:00Z | KT-001 baja (−0,13 %) desde la vela de las 21:00 | INCONCLUSA | **INSUFICIENTE → ABSTENERSE** | Sin medición de liquidez antes del corte (crítico desde v0.2). Además: el régimen diario ALCISTA la contradice, los modelos no coinciden, el movimiento es menor que el costo de 0,30 % y el historial sin solape al corte es n=0 |
| 2026-10-22 00:00Z | KT-001 sube (+0,04 %) desde la vela de las 22:00 | INCONCLUSA | **INSUFICIENTE → ABSTENERSE** | Sin medición de liquidez antes del corte. Historial al corte: Kronos 0/4 y KT-001 0/4 contra «siempre sube» 4/4; los modelos no coinciden; el movimiento es menor que el costo |

La elección de los cortes no tiene un registro previo con fecha que la respalde (señalado por el desconfiado). El de 10-21 se propuso en este mismo documento antes de correr el piloto; el de 10-22 es la última vela diaria disponible. Las cifras las recalculó el desconfiado con un script propio y coinciden.

En los dos cortes el sistema hizo lo que pide la orden: **no pudo justificar la tesis y se abstuvo**. No hubo ningún dato posterior al corte. `predicciones.csv` quedó con el mismo hash.

## 4. Pruebas (`tests/test_atlas.py`, 34, todas en verde)
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
| 3. Registro de tesis y motor de contradicciones | Implementado y probado | 28 pruebas; CI del PR en verde (corrida 40065809952); falta la auditoría independiente | Revisión |
| 4. Piloto BTCUSDT | Funcional con datos reales; modo prospectivo agregado | Sección 3. Primera tesis prospectiva `TS-BTC-20261024T0523Z` (INCONCLUSA → ABSTENERSE), registrada 05:23:41Z, vence 09:23Z; el commit en GitHub es su sello de tiempo. Candados: corte de hace ≤ 60 min, horizonte sin vencer, predicción de KT-002 de ≤ 2 h; la hora de registro queda fuera de la huella | Revisión. Puntuar la tesis al vencer, sin cambiar su contenido |
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
| Licencias | Sin código ajeno; GPL (freqtrade) y LGPL (nautilus) no se integran como código, solo como herramientas externas aisladas |
| Costos | $0: el CI corre en un repositorio público con runners estándar; sin APIs pagas; el piloto no usa LLM |

## 7. Valor frente al ORION actual
Aporte de ATLAS:
- un formato verificable para responder «¿esta predicción merece atención?»;
- disciplina de punto en el tiempo;
- abstención por defecto.

Lo que todavía **no** aporta: evidencia financiera. Sin una hipótesis que pase la Fase 0 no hay simulación, y sin simulación neta de costos no hay rentabilidad que afirmar.

## 8. Respuesta a la auditoría del desconfiado (2026-10-24, sobre `3a2cd9b`): DUDAS ABIERTAS
| # | Hallazgo | Corrección (v0.2) | Prueba |
|---|---|---|---|
| M1 | Un modelo con ventaja en contra daba FAVORABLE; la regla de ventaja chocaba con el preregistro de KT-002 | Solo cuenta un modelo a favor, y uno en contra suma a la evidencia contraria. La ventaja exige un estudio confirmatorio aprobado; los datos descriptivos nunca bastan | `test_modelo_contrario_con_ventaja_no_da_favorable`, `test_ventaja_nunca_sale_de_datos_descriptivos` |
| M2 | Daba INCONCLUSA donde correspondía INSUFICIENTE; inventaba la hipótesis «sube» | Velas, predicción o spread faltantes o viejos son críticos; el spread viejo no se usa como liquidez; sin predicción o con predicción nula, dirección 0 e INSUFICIENTE | `test_sin_predicciones_…`, `test_prediccion_nula_…`, `test_prediccion_vieja_…`, `test_spread_viejo_…` |
| M3 | La máquina de estados y el registro eran débiles | Revisores registrados, evidencia estructurada, `anexar` valida el estado, ancla externa, líneas malformadas reportadas | `test_rechazada_…` (con «Claude», «gpt-4», «a», «rosiver-MLL»), `test_registro_rechaza_saltos_de_estado`, `test_ancla_detecta_…` |
| M4 | Las instantáneas no se revalidaban | `fugas()` dentro del motor y `--validar-instantanea` en el CI | `test_instantanea_con_resultado_futuro_es_insuficiente` |
| B5 | Eventos sin hora o futuros se contaban | Excluidos en el adaptador (evento futuro) y en la analítica (sin hora) | `test_evento_sin_hora_queda_fuera`, `test_fuente_sin_disponibilidad_temporal` |
| B6 | FAVORABLE inalcanzable sin decirlo | Aclarado (sección 2) | — |
| B8 | El chequeo de KT-002 en el CI era trivial | El hash se toma antes de las pruebas, que leen data/kt002 real; `sha256sum -c` al final | CI |
| B9 | Exactitud | La hora se toma con `datetime`; la última predicción, por `utilizable_utc`; se corrigió la ruta de freshness y se quitó la mención a AGPL | — |
| B10 | `CONTEXTO_COMPARTIDO.md` no menciona ATLAS | Registrado | — |

**Sigue abierto, de nivel bajo:**
- `recibido_utc` queda en `None`: ATLAS lee copias del repositorio y no registra cuándo las recibió;
- `pip install` fijado por versión, no por hash;
- el desconfiado no revisó los pilotos B2–B4.

**Trabajo en paralelo:** otra sesión de Claude (`session_01TZKgEz…`, commit `81ffa29`) agregó el modo `--prospectiva` y registró la tesis **prospectiva** `TS-BTC-20261024T0523Z` (v0.1: INCONCLUSA → ABSTENERSE, vence 2026-10-24T09:23Z). Se integró con merge, sin descartar nada. Esa tesis **no se reescribe** con v0.2, porque es un registro prospectivo; consta en la cadena con su huella original. Las salidas de versiones anteriores se aceptan si figuran en el registro; las de la versión vigente se reproducen desde su instantánea.

Ancla del registro de tesis (5 líneas): `{"lineas": 5, "ultimo_hash": "42f7642a801733b2bac659aed1fb5c6322807ff5cc197d235f5dd06dcc091aae"}`.
