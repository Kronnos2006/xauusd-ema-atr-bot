# Contexto compartido

## KT-003 prueba superada y Enmienda D (2026-10-20, Costa Rica)

Autor Claude; auditor desconfiado (revision de la prueba: DUDAS ABIERTAS con 2 bloqueos MEDIOS, sin ALTOS); revisor Codex pendiente. Prueba (run 39447082961): 2928 bases, 404 saltadas, 842 post corte, 43 velas desalineadas excluidas, predict = predict_batch, ~65 min por shard. Bloqueos resueltos en Enmienda D: el modo completo usa el CSV sellado con hash verificado; corte descriptivo desde 2025-10-03 declarado antes de resultados. Se declara que el autor vio tasas de referencias triviales en un ensayo de la union con pronosticos aleatorios.

## KT-003 Enmienda B y corrida de prueba (2026-10-20, Costa Rica)

Autor Claude; auditor desconfiado (2a revision del diseno: DUDAS ABIERTAS, sin look-ahead); revisor Codex pendiente. El usuario acepta explicitamente que KT-003 exponga toda la historia BTC 2017-2026. Enmienda B escrita antes de cualquier dato: Holm sobre 3 modelos en post corte como resultado primario, MDE 4,8 pts, hashes y CSV versionado, persistencia como referencia, guardas de rama y de conjunto de bases. Se lanza primero el modo prueba (datos, equivalencia predict/predict_batch, tiempos, fechas de checkpoints), sin pronosticar el diagnostico; el modo completo espera la revision del auditor.

## Auditoria desconfiado y arranque KT-002 (2026-10-20 14:30 UTC)

Autor Claude; auditor agente desconfiado; revisor Codex pendiente. La primera auditoria dio DUDAS ABIERTAS: el workflow KT-002 no tuvo ninguna corrida (cron sin ejecutar). Aplicado lo pedido: disparo por push del propio script, McNemar exacto vs siempre sube, conteo de horas omitidas, chequeo de reproducibilidad en la primera corrida, Enmienda A del registro KT-002 (antes del primer dato), cambios.json corregido, CLAUDE.md con las tareas descriptivas autorizadas. KT-003 sigue en la rama kt003-diseno; su workflow se lanza solo a mano. Auditoria diaria programada 6:33 Costa Rica con notificacion al usuario.

## KT-002 prospectivo en GitHub Actions (2026-10-20, Costa Rica)

Autor Claude; revisor Codex pendiente. El usuario pide medir el acierto con datos reales sin depender de su PC. Elige prueba prospectiva y evaluar Kronos, TimesFM y KT-001 por separado. Registro previo, escrito antes de recolectar datos, en docs/KT-002_registro_prospectivo.md. Workflow .github/workflows/kt002.yml, cada hora, BTCUSDT 1h, 400 velas cerradas, horizonte 4h, misma configuracion y revisiones que KT-001. Script tools/kt002_prospectivo.py. Salida data/kt002/ (predicciones.csv, resumen.md/json). La logica de puntuacion se probo localmente con velas sinteticas y modelos simulados; la inferencia real solo corre en Actions porque este entorno no llega a Hugging Face ni a Binance. Es descriptivo: sin ordenes, MT5, costos ni rentabilidad, sin cambio de N canonico y sin abrir reservas. Las velas posteriores al 2026-10-20 quedan expuestas para cualquier holdout BTC futuro.

## Publicacion solicitada (2026-10-19, Costa Rica)

Commit local 38a0531 creado. Integracion de origin/master 5ca75e4: unico conflicto en registro_checksums.json, hashes/tamaños identicos; conservadas fechas remotas mas recientes (2026-08-19 21:33 frente a 21:27), sin recalcular ni certificar datos. Cambios remotos de rutas de loggers/monitor preservados como historial existente, sin ejecutar ni modificar tareas. Evidencia KT-001 versionada; requirements publicado usa URL Git con revision TimesFM fija en lugar de ruta absoluta local. Publicacion autorizada por el usuario; revision funcional independiente sigue pendiente.

Usuario solicita subir todo el proyecto al repo. Autor Codex; revision independiente pendiente. Destino: origin, Kronnos2006/xauusd-ema-atr-bot, rama master. Alcance: snapshot de cambios previos y nuevos, incluida eliminacion local preexistente del CSV EURUSD, codigo MQL5/Experts/bot, documentos, estudio PDF y herramientas sinteticas. Revision basica de patrones de secretos sin coincidencias, sin afirmar auditoria exhaustiva. Excluidos entornos/pesos/clones descargados y estado operativo local de coordinacion, senales.csv y respaldo _to_delete. Evidencia sintetica copiada a docs/evidencia/KT-001 para publicarla sin caches. Fetch encontro tres commits remotos previos; integrar preservando historial sin force push. No ejecutar scripts de trading, loggers, tareas, reservas ni backtests. Registro documental de preparacion de publicacion; resultado se verifica contra HEAD remoto al terminar.

## Integracion Kronos + TimesFM (2026-10-19, Costa Rica)

Resultado final tecnico: PASS_TECHNICAL_ONLY en ejecucion inicial 141.06 s y repeticion offline del script final 29.91 s. Ambos generan cuatro pronosticos finitos desde 400 velas sinteticas; promedio 50/50 y rechazo de fechas desalineadas verificados. Tres pesos con SHA256 y revisiones fijadas, reporte/CSV/versiones en tools/ensemble-output. No se verifico ventaja financiera ni independencia de errores en mercado. Revision Claude aun pendiente; ninguna aprobacion cruzada afirmada. Esto reemplaza «en ejecucion» de la entrada previa.

Autor Codex; revisor Claude pendiente. Usuario autoriza prueba conjunta sintetica («VAMSO }») de promedio fijo 50/50 de retornos previstos. Variante local KT-001 registrada antes de ejecutar en docs/Kronos_TimesFM_registro.md; N canonico de resultados financieros no modificado. TimesFM 2.5 200M elegido para CPU antes de resultados, implementacion del paquete 3.0.2 desde upstream e51928e27119cb17bebc005be2696b75e0a9e688. Preflight RAM/disco correcto; pip check correcto. Script tools/kronos_timesfm_smoke.py en ejecucion: 400 velas sinteticas horarias, cuatro futuras, Kronos 20 trayectorias y TimesFM mediana de cierre. Sin precios de mercado, backtest, ordenes ni acceso a reservas. Aun no hay veredicto tecnico conjunto. Reglas financieras previas no se cambian; potencia/Fase 0 real y procedencia de entrenamiento TimesFM siguen pendientes. La cifra ~31 años anterior es aproximacion para detectar Sharpe verdadero 0.5 con potencia 80 %, no minimo universal de historial ni prueba de ausencia de edge.

## Kronos / BTC Spot (2026-10-19, Costa Rica)

Usuario acepta reglas para viabilidad («si}}»). Autor Codex; revisor Claude pendiente. Diagnostico previo: articulo declara entrenamiento hasta junio 2024; procedencia exacta del checkpoint no auditada. Test de Sharpe iid/normal bilateral 5 %, potencia 80 %, efecto 0.5 requeriria 31.3955 años; MDE a cinco años 1.25291. Es chequeo de diseño del criterio Sharpe, no triage empirico de trades ni evidencia de ausencia de edge. NO LISTO para backtest confirmatorio: señal aceptada pero Fase 0 real/folds/reserva pendientes y horizonte insuficiente cerca del umbral. No precios descargados ni backtest, ordenes, tareas o MT5. No se cambian parametros, no se declara descarte empirico de Kronos y no se modifica N canonico. Detalle y limitaciones en docs/Kronos_BTC_preparacion.md.

Prueba tecnica completada: PASS_TECHNICAL_ONLY, Kronos-small CPU, 64 velas sinteticas a 4 futuras finitas, 14.87 s incluyendo carga/descarga inicial. El usuario pide recomendaciones de reglas: propuesta unica detallada en docs/Kronos_BTC_preparacion.md, pendiente de eleccion explicita; no equivale a aprobacion. Sin resultados de mercado ni revision independiente. No hay backtest.

Autor Codex; revision por Claude pendiente. El usuario solicita probar Kronos y confirma preparar evaluacion de estrategia BTCUSDT Spot en simulacion. Repositorio oficial descargado en tools/kronos-upstream, revision 67b630e67f6a18c9e9be918d9b4337c960db1e9a; entorno aislado y prueba sintetica en preparacion. Plan y pendientes en docs/Kronos_BTC_preparacion.md. No se ha definido señal/horizonte/corte por el usuario ni completado Fase 0; sin backtest ni descarga de mercado, ordenes, MT5 o apertura de reservas. La autorizacion de preparar no completa los requisitos del hypothesis-gate.

## Objetivo actual
Sin tarea de coordinacion automatica activa. El usuario solicito retirar la integracion y documentacion del orquestador el 2026-10-16.

## Proyecto y estado
Investigacion cuantitativa via MT5, Python y MQL5. PAUSA ACTIVA, sin hipotesis abierta ni capital real desplegado. Las reglas vigentes estan en CLAUDE.md y AGENTS.md, ahora independientes.

## Cambios y evidencia (2026-10-16, Costa Rica)
Autor: Codex. Retirados los archivos del orquestador y sus informes dentro del proyecto; eliminadas las referencias de Infraestructura.md y la dependencia de instrucciones generadas. Conservadas las restricciones de investigacion. Sin ejecucion de scripts de trading ni cambios a datos, loggers o tareas programadas.

## Pendientes
Revision por Claude pendiente; no se afirma aprobacion cruzada. La instalacion externa y los registros MCP globales quedan fuera de esta limpieza de la carpeta.

## Nueva solicitud de investigacion (2026-10-16, Costa Rica)
Autor: Codex; revision pendiente. El usuario solicita crear y evaluar una estrategia para Bitcoin con operaciones de minutos. Esto autoriza retomar el diseno de investigacion; no autoriza operaciones ni capital real. Mercado spot o futuros aun por confirmar. No se encontro historico local con nombres BTC/Bitcoin; el conector Binance ofrece velas de 1 minuto. Sin descarga de historico, simulacion ni resultados de rentabilidad. Pendientes: precisar mercado, Fase 0 de frecuencia y potencia con datos reales, y definiciones explicitas del usuario exigidas por hypothesis-gate antes del backtest.

## Lectura y recomendacion inicial para Bitcoin (2026-10-16)
Autor: Codex; revision pendiente. Leidos README, informe del 2026-07-30, cierre formal, estado actual, TF_Basket_H1 y documentos investigacion/fase2-4. Hay estudios posteriores a la sintesis de CLAUDE.md: seis estrategias ICT/SMC descartadas, momentum/Donchian EURUSD cerrados, tres variantes momentum cross-sectional sin supervivencia en Validation y carry descartado en triage. README e informe de julio no representan el estado mas reciente. research/config.example.yaml corresponde a EMA XAUUSD M15/H1; no asumir soporte Binance ni trasladar sus costos.
Recomendacion presentada: investigar BTCUSDT Spot en simulacion, barras de 5 minutos y datos base de 1 minuto para auditoria de ejecucion. Es una propuesta pendiente de decision del usuario, no una hipotesis registrada ni estrategia validada. Revisar cobertura, comisiones de ambos lados, spread y slippage antes de backtest. Sin descarga, ejecucion de backtests, conexion privada ni ordenes. No trasladar automaticamente efectos macro R-multiple a scalping BTC para el power analysis.

## BTC: ajustes al borrador de Fase 0 (2026-10-16)
Autor Codex; revision pendiente. Se acepta retirar 5 min como decision previa al costo. Borrador en docs/BTCUSDT_Fase_0_borrador.md: fuente oficial Binance, costos por ambos lados, limites de klines para spread/slippage, reserva temporal y manifiesto con hash pendientes, registro de intentos pendiente de N_total canonico. Tarifa publica regular confirmada 0,100 % maker/taker sin descuento. No se encontraron tsm-volscaling ni estrategias-clasicas en esta carpeta ni por nombre bajo su padre; se solicito su ruta. Prioridad de cierre TSM antes de ejecutar BTC. No hubo descarga, sellado de holdout, backtest, commit ni push. No asumir que hash prueba no exposicion, ni que el rango de vela sea retorno capturable. Temporalidad, señal y cortes aun no aprobados.

## Rutas migradas verificadas
Localizados C:\proyectos\tsm-volscaling, estrategias-clasicas y xauusd-ema-atr-bot. Lecturas desde cada carpeta, sin tocar final_test. TSM no tiene .git y exige OK por paso en CLAUDE.md; cierre pendiente. Clasicas declara holdout cerrado en datos/registro_holdout.json; no se verificaron hashes actuales. Registro n=8 frente a N=13 planificado por TSM (8+4+1); BTC unica variante daria N previsto=14, no registrado. Git de repos migrados presenta errores de worktree/permisos; no reparado. Borrador BTC ampliado en carpeta original, sin migracion ni escritura en C:\proyectos. No hay commit/push, descargas ni backtest.

## Cierre TSM verificado (2026-10-16, Costa Rica)
El usuario autorizo cerrar unicamente Fase 0 de TSM y conciliar N en clasicas. Autor Codex; revision independiente pendiente. Trabajos en C:\proyectos con acceso elevado aprobado: .venv aislada, yfinance=1.6.0 pandas=3.0.5 numpy=2.5.2 scipy=1.18.1, requirements completo y pip check correcto; .gitattributes CSV binary y textos LF; .gitignore; Git main y remoto privado creado. Pre-registro original sin cambios (SHA256 779be16e87570770a718a9c29e06dfe1c4040c35272e90c40d3b94ee17c6a4c6). Primer commit TSM 3762def90f4f7df7f71bd14e819e50e37567c093; cierre y hashes en 17e6ac8bc7eac49663292827d795a667834138a1. Push y HEAD remoto verificados. Clasicas N=13 (8+4 reservadas+1 TSM), commits a96954a1d601c60386dc513d701c9fa6a59fad5d y c32769dcecc958fa46c4bbf06666bbe2f3c4d671, ambos publicados; inventario no versionado preexistente intacto. Credencial Git operativa permitio publicar sin imprimir/guardar secretos; gh global no modificado. Evidencia completa en salidas del chat y docs/cierre_fase0.md + docs/registro_commits.md de TSM. Fase 0 cerrada; no fases 1/2, descargas financieras, senales, backtest ni acceso a final_test. BTC permanece como borrador; su N=14 previsto no se registro.

## Conexion MT5 solicitada (2026-10-16)
El usuario autorizo conectar MT5. Modulo Python MetaTrader5 disponible y terminal instalado en C:\Program Files\MetaTrader 5\terminal64.exe. Intento directo con acceso elevado devolvio error -6, Terminal: Authorization failed. No se envio orden ni se cambiaron credenciales/configuracion. Hace falta iniciar sesion valida desde el terminal para repetir verificacion de solo lectura. No se acredita conexion al broker.

## Pase de Claude a Codex (2026-10-20, 20:56 Costa Rica)
Autor: Claude; revision cruzada de Codex pendiente (informativa, sin aprobacion asumida).
- **KT-002** (prospectivo BTC, Kronos-small / TimesFM 2.5 / KT-001 50-50, direccion a 4 h): GitHub Actions horario (`.github/workflows/kt002.yml`, minuto 7 UTC), datos en `data/kt002/`. Primeras predicciones 2026-10-20; muestra minima, nada concluyente. Registro `docs/KT-002_registro_prospectivo.md` (Enmienda A).
- **KT-003** (historico 2017-2026, 2928 bases diarias, datos sellados SHA-256 c3ccfb0a…): terminado y auditado por `desconfiado`. Post corte (n=842): Kronos 56,8 %, TimesFM 48,7 %, KT-001 55,5 %, «siempre sube» 50,9 %; McNemar con Holm no significativo (Kronos p=0,086). Registro con Enmiendas A-D y Nota E (cancelacion erronea del intento 1).
- **Propuestas sin aprobar**: `docs/propuestas/KT-004_propuesta.md` (confirmar Kronos con datos nuevos) y `KT-005_propuesta.md` (TimesFM con log-retornos). Pendientes de auditoria del `desconfiado`.
- **Gerencia** (`docs/gerencia/`, `.claude/agents/`): gerente + jefes (mejorador, desconfiado, vigia-datos, jefe-operaciones, jefe-documentacion, jefe-innovacion con subordinado innovacion-noticias). El usuario delego al gerente aprobar mediciones sin dinero aprobadas por el desconfiado sin ALTO/MEDIO; 7 casos se escalan al usuario (ver CLAUDE.md). Tarea programada diaria 6:30 CR "Gerente: informe diario".
- **Oficina del dueño** (artefacto privado de Claude): ordenes del usuario, escalaciones e informes en su base; el gerente las procesa. No accesible desde Codex.
- **Skills de terceros en prueba** (`.claude/skills/TERCEROS.md`): ponytail, ponytail-review, code-review-and-quality, debugging-and-error-recovery; solo SKILL.md, sin hooks.
- Sin ordenes, capital, MT5 operativo ni holdouts abiertos. Borrador BTC intradia de Codex (2026-10-16) sigue sin registrar; N canonico sin cambios.
Pendiente para Codex: revision cruzada de KT-003 (resultados y Nota E) y de las propuestas KT-004/KT-005, si el usuario lo pide.

- Visor publico de solo lectura: `docs/visor/index.html` (BTC con predicciones, KT-002, KT-003, organigrama, decisiones, corridas). Abrir en https://raw.githack.com/Kronnos2006/xauusd-ema-atr-bot/master/docs/visor/index.html o, si se activa GitHub Pages (master /docs), en https://kronnos2006.github.io/xauusd-ema-atr-bot/visor/

- **Portafolio (2026-10-21, autor Claude)**: PF-001 (paraguas), HP-001 (13F "mejores ideas") y HP-002 (flujos de ETF de BTC) con Fase 0 en `docs/portafolio/hipotesis/`; inventario en `docs/portafolio/INVENTARIO_DATOS.md`. Sin resultados ni retornos calculados; 0 variantes probadas. Desconfiado: sin problemas ALTOS ni MEDIOS, triage propone descarte (`docs/auditorias/2026-10-21_HP-001_HP-002.md`). Esperan decisión del usuario. Revisor posible: Codex.
- **KT-002 observabilidad (2026-10-21, autor Claude, revisión de Codex pendiente)**: merge 72cf911 en master; cambia solo `.github/workflows/kt002.yml` (log por vuelta, fallas visibles) y `guardia.yml` (solape cada ~4 h). No cambia la medición. La rama vieja `kt002-observabilidad` queda obsoleta.

## ORION: reparación de guardia y protección de KT-002 (2026-10-23, Claude)
Operated-By: Claude (Anthropic) · Requested-By: propietario (orden maestra 2026-10-23) · Review-Status: pending (ChatGPT) · Validation: tests/test_guardia_salud.py (15 OK), actionlint OK.
- Rama `fix/orion-guardia-kt002-20261023`, PR pendiente de revisión cruzada; no fusionada.
- Modelo de colaboración ORION registrado en CLAUDE.md (texto original conservado).
- Informe completo: `docs/ops/INFORME_REPARACION_ORION_2026-10-23.md`.

- 2026-10-23 (Claude, autor; revisor pendiente: ChatGPT/Codex): protección provisional del vigía aplicada a la tarea programada (sin cancelar/relanzar, solo avisa al gerente). En la rama del PR #32: dedupe de la guardia por último spread publicado y un solo relanzador (la guardia). Detalle: `docs/ops/INFORME_REPARACION_ORION_2026-10-23.md` §13.
- 2026-10-23 21:00 (Claude, autor; revisor: ChatGPT): resueltas las 6 observaciones de revisión cruzada del PR #32 (merge de master, verificación contra GitHub sin `|| true`, dedupe que no oculta fallas, 28/28 pruebas, KT-002 intacto). Informe §14. PR sin fusionar.
- 2026-10-23 21:40 (Claude, autor; auditor interno: desconfiado, DUDAS ABIERTAS sin ALTOS, resueltas; revisor: ChatGPT pendiente): orden ejecutiva final ORION. Guardia probada en GitHub real desde la rama (verde, rojo con simulacro y sin actuar sobre producción); verificador de integridad de KT-002; vigía v2 compatible; plan de reversión. Pendiente: fusión del PR #32 (propietario) y verificación en master. Informe §15.
- 2026-10-24 (Claude, autor; auditor: desconfiado, DUDAS ABIERTAS sobre 3a2cd9b, MEDIOS corregidos en v0.2; revisor: ChatGPT pendiente): ORION–ATLAS (PR #34), por orden del propietario «ORION — PROYECTO ATLAS». Es solo investigación: no abre hipótesis ni estrategias (la PAUSA ACTIVA sigue vigente), no usa dinero y no toca KT-002. Piloto BTCUSDT retrospectivo: INSUFICIENTE → ABSTENERSE en 2 cortes. Detalle: `docs/arquitectura/ORION_ARQUITECTURA_FINANCIERA.md`.
- 2026-10-24 05:35Z (Claude, sesión 01YUSKLx…): dos sesiones de Claude editaron la rama de ATLAS a la vez (81ffa29, de la sesión 01TZKgEz…, y la v0.2 de esta sesión). Se resolvió con merge, conservando todo. Para no repetirlo, que **una sola sesión trabaje la rama `research/orion-atlas-20261024`** por vez; la otra revisa o espera.
