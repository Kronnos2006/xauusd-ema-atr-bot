# Revisión de riesgo: ES-001 y ES-002 (borradores)

Jefe de riesgo · 2026-10-21 · Marco v1.0 (sin cambios) · Costos: `COSTOS_BTCUSDT.md` (PARCIAL). Son borradores no simulables: esto revisa el diseño, no resultados.

## ES-001 (BTC spot largo en ALCISTA): OK CON CAMBIOS
1. Tamaño: min(25 %; 0,5 %/(d+0,30 %)) cumple 25 % por posición y 50 % por instrumento. Con d=15 % da 3,27 %; con d=2 % da 21,7 %. Correcto.
2. Pérdida por operación: se calcula con 0,30 % base. Con estrés (0,60 %) el riesgo pasa de 0,50 % a ~0,5 %·(d+0,60)/(d+0,30), sobre el límite. CAMBIO: dimensionar con 0,60 %.
3. Stop evaluado con cierre de 1 h y ejecutado en la vela siguiente: hay hueco no medido. CAMBIO: sumar al riesgo un margen de gap (peor movimiento de 1 h histórico) o justificar con datos que 0,5 % no se supera.
4. Exposición 25 % × vol 33 % ≈ 8,3 % anual ≤ 10 %: OK, re-verificar con vol 60 d.
5. Parámetros: dice "únicos 2" (n_conf, k_stop) pero agrega "o pase 1 día" tras un stop (tercer parámetro, ambiguo). CAMBIO: fijarlo o meterlo en la grilla del DSR; si no, es desvío del registro (kill switch 6).
6. "Si da menos del mínimo operable, no se opera": CAMBIO: declarar ese mínimo en USDT.
7. Costos: 0,30 %/0,60 % bien cargados, pero spread y deslizamiento siguen SUPUESTOS; no hay aprobación final hasta medirlos (marco 6.2).
8. Ya reconocido en el borrador y lo comparto: piso de 30 operaciones por fold probablemente inalcanzable (si no se alcanza, RECHAZADO por marco 6.4); caída máxima ≤ 6,5 % y comparación con comprar-y-mantener 25 % obligatorias. Depende de HP-003, con triage propuesto de DESCARTE.

## ES-002 (BAJISTA: salir/reducir): VETO tal como está escrita
1. Sin stop ni riesgo por operación acotado: la exposición base (comprar-y-mantener o ES-001) no tiene límite de 0,5 % (marco sec. 2, fila 1: "sin stop definido: no se aprueba"). "La reducción es en sí misma la condición" no es un stop: el aviso llega con cierre diario más 1 día de confirmación, y 1 día de BTC puede romper el límite diario de 1 % (25 % × 4 % = 1 %).
2. No tiene retorno propio ni exposición base definida: no se puede verificar tamaño, exposición ni caída máxima.
3. Superpuesta a ES-001 es redundante: ES-001 ya sale en LATERAL o BAJISTA. Solo aportaría contra comprar-y-mantener, que no está aprobado como estrategia.
4. Costos: rotación 0,30 %/0,60 % bien cargada (r=50 % cuesta la mitad), pero la ganancia esperada es no medida y la pata bajista es la más débil de HP-003 (MDE 0,092 > efecto 0,059). Piso de 30 operaciones casi seguro inalcanzable.
5. Cortos: bien excluidos (marco sec. 3).
Para levantar el veto: reescribir como regla de salida de ES-001 con su stop, o con base declarada que tenga stop, y declarar la grilla (n_conf × r) para el DSR.

Corte común: ninguna se aprueba sin registro previo, Fase 1 de Kensy, desconfiado sin ALTOS, `vigia-datos` y costos medidos. Dinero real: no (marco sec. 8).
