# Plan de acción mientras esperamos los datos de KT-002 (octubre 2026)

2026-10-21. Autor: gerente general. Base: `docs/gerencia/PROPUESTA_ORGANIZACION_TRADING.md` (propuesta de Claude), evaluada a pedido del usuario.
Sin dinero real, sin órdenes, sin holdouts y sin cambios en experimentos que estén corriendo. Lo que no me toca decidir quedó como escalación en la Oficina del dueño.

## 1. Veredicto sobre la propuesta

La comparación con una firma grande es correcta y el principio "quien propone no aprueba, y quien arriesga no controla el riesgo" ya es el nuestro. Hay que hacer 4 correcciones:

1. **Plazos optimistas.** Los "≈17 días" para 100 resultados sin solape y "≈4 meses" para ~780 suponen cobertura completa. Hoy la cobertura real de KT-002 es ~54 % (auditoría del desconfiado, 2026-10-21). Con esa cobertura serían ~1 mes y ~8 meses. Por eso el arreglo de los huecos va primero: así los plazos se acortan sin tocar la medición.
2. **El analista no se toca sin el usuario.** El punto 2 de la propuesta (que el gerente llame directamente a los ayudantes del analista) cambia cómo trabaja el analista, y eso no lo puedo decidir yo (`gerente.md`). La copia diaria de velas, en cambio, es infraestructura de datos y no cambia al analista.
3. **El modelo de costos no depende de crear al jefe de riesgo.** Es descriptivo y sin dinero, así que puede arrancar ya. Si el usuario crea al jefe de riesgo, pasa a ser suyo.
4. **Una sola propuesta en auditoría por vez.** KT-004 y KT-005 ya están en corrección. El horizonte de 24 h espera su turno, para no saturar al desconfiado ni mezclar decisiones.

## 2. Qué apruebo (dentro de lo que me toca: operativo y sin dinero)

| # | Punto | Decisión | Quién ejecuta | Condiciones |
|---|---|---|---|---|
| 1 | Arreglar huecos de KT-002 (log por vuelta, que el paso falle si falla una vuelta, despertador solapado cada ~4 h) | **Aprobado** (ya lo estaba el 2026-10-21) | jefe-desarrollo (programador) implementa; Codex revisa | Entre jobs, nunca con uno corriendo. No tocar `tools/kt002_prospectivo.py`, el minuto 7 ni el cálculo. Prueba: 24 h seguidas sin horas omitidas |
| 2a | Copia diaria de velas BTC (1d y 4h, Binance pública) en el repo vía GitHub Actions | **Aprobado** | jefe-desarrollo; jefe-operaciones vigila | Workflow aparte que escribe solo en `data/velas_btc/`, no toca `kt002.yml` ni `data/kt002/`. Arranca después del punto 1 (no editar a la vez). Hash por archivo |
| 2b | Que el gerente llame directo a los ayudantes del analista | **No lo decido** → escalación | usuario | Límite de `gerente.md` sobre el analista |
| 3 | Modelo de costos de BTC (comisión por lado, spread, deslizamiento con datos públicos) | **Aprobado, descriptivo** | mejorador redacta; desconfiado audita | Fuentes citadas y fecha. Resultado: el movimiento mínimo en 4 h (y 24 h) que cubre costos ida y vuelta. No usa datos de KT-002. Pasa a riesgo-costos si se crea |
| 4 | Umbral de equilibrio con resultados de KT-003 ya publicados | **Aprobado, descriptivo**, después del 3 | mejorador; desconfiado audita | Una página de especificación escrita **antes** de calcular. Solo describe: no elige variantes ni horizontes. No toca KT-002 ni ningún holdout |
| 5 | Marco de riesgo escrito (pérdida máxima, tamaño, apagado) | **Espera** al jefe de riesgo → escalación | usuario | No es urgente: no hay estrategia. Es requisito antes de cualquier simulación |
| 6 | Corregir y re-auditar KT-004 v2 y KT-005 | **Sigue en curso** | mejorador → desconfiado | Lo apruebo solo si el desconfiado no deja problemas ALTOS ni MEDIOS y el registro previo se escribe antes de ver datos |
| 7 | Diagnóstico histórico a 24 h | **Aprobado para redactar el registro previo**, no para correr | mejorador → desconfiado → gerente | Después del punto 6. El desconfiado debe evaluar el riesgo de sobreajuste por reusar la misma historia 2017–2026 de KT-003 |
| 8 | Simulación en papel | **No lo decido** → escalación | usuario | Es una hipótesis nueva de trading (`hypothesis-gate`) |

## 3. Orden y calendario

- **Semana 1 (21–27 oct):** punto 1 (huecos de KT-002) → al cerrar, 2a (velas). En paralelo, el mejorador redacta el punto 3 (costos) y corrige KT-004 y KT-005 (punto 6).
- **Semana 2 (28 oct–3 nov):** el desconfiado audita costos y KT-004/005. Después, punto 4 (umbral, con especificación previa). Ojo: FOMC el 28-oct y PCE/PIB el 29-oct; las ✗ de KT-002 de esos días se anotan solo como descripción.
- **Semanas 3–4 (4–17 nov):** punto 7 (registro previo a 24 h) entra a auditoría solo si el punto 6 ya salió. Si el usuario lo aprueba: jefe de riesgo, marco de riesgo (punto 5) y el diseño de la simulación en papel.
- **Todos los días:** informe del gerente con el analista. El desconfiado revisa KT-002 los lunes. Innovación, lunes y jueves.

## 4. Puertas de decisión

Las adopto como criterio de gerencia. Para que pasen a ser reglas del proyecto (`CLAUDE.md`) hace falta el OK del usuario:
- **~100 resultados sin solape:** revisión intermedia, solo descriptiva, con la cobertura informada.
- **~780 resultados sin solape** (para distinguir 55 % de 50 %, con α=0,05 y potencia del 80 %): conclusión de KT-002 según su registro previo. Nunca antes.
- **Dinero real:** nunca sin (a) un resultado que pase su registro previo, (b) una simulación en papel con costos y resultado positivo, (c) la aprobación del jefe de riesgo y del desconfiado, y (d) la decisión explícita del usuario.

## 5. Escalaciones creadas en la Oficina (estado "esperando")

1. **Crear el jefe de riesgo (independiente) con el ayudante riesgo-costos.** Recomendación: **sí**, con la misma independencia que el desconfiado. Se convoca solo cuando haya algo que toque simulación o dinero (modo ahorro), y su primer trabajo es el marco de riesgo (punto 5).
2. **Simulación en papel.** Recomendación: **todavía no**. Esperar a (a) el modelo de costos y el umbral de equilibrio (puntos 3 y 4) y (b) los ~100 resultados sin solape. Si los costos superan lo que los modelos prevén moverse, simular solo confirmaría pérdidas. Reevaluar a mediados de noviembre.
3. **Analista: que el gerente llame directo a sus 3 ayudantes.** Recomendación: **sí**, pero solo como forma de convocarlo. Las reglas, los archivos y las conclusiones siguen siendo del analista. Con la copia de velas (2a) desaparece además el bloqueo de Binance.
