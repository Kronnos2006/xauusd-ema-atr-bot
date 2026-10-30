# KT-002: plan de análisis secuencial (pre-registro de cortes)

2026-10-30, Costa Rica. Autor: Claude. Pedido por el propietario. Revisión: ChatGPT/Codex. **Aprueba el propietario.**
**No cambia nada de lo que mide KT-002** (modelos, horario, código, datos). Solo fija **cuándo y con qué regla** se decide, para no mirar resultados sin control.

## Exposición declarada
Al escribir este plan ya se vieron n = 57 bases sin solape (Kronos 49,1 %, «siempre sube» 45,6 %). Por eso los cortes empiezan en n = 200 y la regla no depende de esos 57 valores.

## Prueba
- Comparación pareada **Kronos vs «siempre sube»** sobre bases sin solape (hora UTC múltiplo de 4), estadístico de McNemar en forma z: z = (b − c) / √(b + c), con b = solo Kronos acierta y c = solo «siempre sube» acierta.
- TimesFM y KT-001: descriptivos en cada corte, sin regla de parada.

## Cortes y límites (O'Brien-Fleming, 4 miradas, α = 0,05 bilateral)
| Mirada | n sin solape | Eficacia: \|z\| ≥ | Futilidad (no vinculante) |
|---|---|---|---|
| 1 | 200 | 4,05 | — |
| 2 | 400 | 2,86 | Kronos − «siempre sube» ≤ 0 puntos |
| 3 | 600 | 2,34 | Kronos − «siempre sube» ≤ 1 punto |
| 4 (final) | 780 | 2,02 | — |

- **Eficacia** (z positivo y supera el límite): Kronos pasa a un confirmatorio prospectivo **con costos**, registrado aparte. No autoriza operar.
- **Futilidad:** se declara "Kronos sin ventaja a 4 h en BTC" y KT-002 puede seguir corriendo solo como registro, sin más miradas inferenciales.
- **Final sin cruzar:** sin ventaja demostrada.
- Si KT-004 resuelve antes, se informa junto a KT-002 sin cambiar estos límites.

## Automatización
Un script sin IA calcula z en cada corte y lo deja en `data/kt002/secuencial.json`; el propietario recibe el resultado. Ninguna IA mira resultados intermedios fuera de estos cortes. (Script a escribir después de aprobar este plan.)
