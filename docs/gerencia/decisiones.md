# Decisiones del gerente

| Fecha | Decisión | Motivo | Ejecuta |
|---|---|---|---|
| 2026-10-20 | Se crea la gerencia y la mesa directiva | Pedido del usuario para automatizar decisiones | Claude (configuración inicial) |
| 2026-10-20 | Se crea el Jefe de Innovación (jefe-innovacion) y su subordinado innovacion-noticias, por pedido del usuario. Solo proponen; el gerente decide; lo que afecte predicciones pasa por mejorador y desconfiado. Convocatoria semanal (lunes). | Pedido del usuario | Claude |
| 2026-10-21 | KT-004 v2 y KT-005 v1 NO se aprueban todavía: el desconfiado dio APRUEBA CON CAMBIOS con problemas MEDIOS (código del evaluador y simulaciones no verificables, cobertura real de KT-002 ~54 %, KT-005 empujando a master, regla de control abierta, MDE sin declarar). Vuelven al mejorador para corregir y re-auditar. | Delegación exige veredicto sin ALTOS ni MEDIOS | mejorador → desconfiado |
| 2026-10-21 | KT-002 perdió las bases 22, 23 y 00 h del 20-10 (job vivo 22:08–02:07 sin commits, paso en "success") y 14–16 h por cola del runner. Se aprueba arreglo solo de observabilidad en kt002.yml: log por vuelta y que el paso falle si una vuelta falla o el push no entra (no cambia la medición). La vuelta 03:07 del 21-10 registró bien. | Las fallas hoy son silenciosas; sin log no hay diagnóstico | jefe-operaciones (próxima corrida, coordinando con Codex para no editar a la vez) |
