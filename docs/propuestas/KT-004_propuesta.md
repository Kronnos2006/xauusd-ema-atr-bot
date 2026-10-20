# KT-004 — propuesta: confirmación prospectiva de Kronos solo, contra el sesgo bajista

2026-10-20, Costa Rica. Autor: agente `mejorador`. Estado: **PROPUESTA**, sin auditar por `desconfiado` y sin OK del usuario. No se registró, no se escribió código y no se tocó KT-002 ni KT-003.

## 1. Qué aprendí de KT-003 y KT-002 (todo es post hoc)

Fuente: `data/kt003/predicciones.csv` (842 bases post corte, 2085 dentro del entrenamiento) y `data/kt002/` (3 pronósticos, 1 vencido: no sirve para nada todavía). Scripts en `/tmp/claude-0/-home-claude/14241745-63d7-59dc-a6ae-501840d3a10b/scratchpad/mejorador/a1.py`, `a2.py` y `a3.py`.

Verifiqué las cifras del contexto: Kronos 56,8 %, KT-001 55,5 %, TimesFM 48,7 %, «siempre sube» 50,9 %, p Holm de Kronos 0,086; Kronos predice baja el 57,1 % (post) y el 60,0 % (dentro) de las veces; va contra la persistencia el 61 %; |retorno previsto| medio de KT-001 0,19 %; en los días con |previsto| > 0,20 % el neto es −0,21 %.

Lo nuevo, mirando si el acierto de Kronos post corte se explica por el sesgo bajista o por la reversión:

| Post corte (n=842) | Valor |
|---|---|
| Acierto esperado si Kronos fuera independiente del mercado con su mismo sesgo bajista | 49,9 % |
| Acierto balanceado (promedio de acierto en días de subida y de bajada) | 56,9 % (bootstrap 95 %: 53,6–60,2) |
| Acierto cuando predice **sube** / cuando predice **baja** | 59,0 % / 55,1 % |
| Referencia «siempre baja» / «reversión» (contrario a las 4 h previas) | 49,0 % / 51,5 % |
| McNemar Kronos vs «siempre baja» / vs «reversión» (sin corregir) | p = 0,0007 / 0,017 |
| Acierto de Kronos cuando coincide con la reversión / cuando no | 56,8 % / 56,7 % |

Lectura: **en el período post corte el sesgo bajista y la reversión no explican el acierto de Kronos**; acierta incluso mejor cuando predice subida. Dentro del entrenamiento pasa lo contrario: allí la reversión sola acertaba 56,3 % y Kronos acertaba 57,3 % cuando coincidía con ella y 45,4 % cuando no; ese período está contaminado y no mide nada.

Otros datos descriptivos:

- Por trimestre post corte, Kronos queda entre 52,7 % y 64,1 % en los 10 trimestres (el de 2026Q4 con n=20). TimesFM queda por debajo de 50 % en 5 de 10.
- El acierto no crece de forma ordenada con el tamaño del retorno previsto (quintiles: 55,6 / 53,0 / 56,6 / 61,3 / 57,4 %). No hay base para un filtro por magnitud.
- Autocorrelación de aciertos día a día: 0,04. El bootstrap por bloques (10 y 30 días) da casi el mismo intervalo que el simple.
- Kronos y TimesFM coinciden en el signo solo el 57 % de las veces; promediarlos (KT-001) diluye a Kronos (55,5 % < 56,8 %).

Advertencias: (a) Kronos fue elegido como el mejor de 3 modelos en el mismo período donde se mide, así que 56,8 % está inflado (maldición del ganador); (b) el post corte no está certificado como fuera del entrenamiento (Enmienda C de KT-003); (c) todas estas cuentas las hice después de ver los resultados. Nada de esto es evidencia confirmatoria; solo justifica qué probar con datos nuevos.

## 2. Propuesta principal: KT-004

### Qué cambia

No se cambia ningún modelo ni parámetro. Cambian **qué se confirma y cómo**:

1. **Un solo modelo en la prueba confirmatoria: Kronos solo** (misma configuración y revisiones que KT-002). TimesFM y KT-001 salen de la familia confirmatoria: TimesFM rinde peor que el azar post corte y probablemente está contaminado; KT-001 lo diluye. Siguen calculándose en KT-002 como descriptivos (no se modifica esa variante). Con un solo test no hace falta Holm, y eso recupera potencia.
2. **Métrica que no se deja engañar por el sesgo**: acierto balanceado en lugar de acierto bruto, más una guarda contra todas las referencias triviales («siempre sube», «siempre baja», «persistencia», «reversión»).
3. **Datos nuevos**: solo pronósticos de KT-002 cuya base abra después de la fecha y hora en que se registre KT-004.

Ventaja práctica: KT-002 ya produce exactamente estos pronósticos. KT-004 es un **análisis pre-registrado** sobre ellos; solo falta un script de evaluación (`tools/kt004_evaluar.py`) que se corre una vez, al final.

### Hipótesis falsable

H1: en BTCUSDT 1h, sobre bases prospectivas sin solape, el signo del retorno a 4 h previsto por Kronos-small acierta la dirección real con **acierto balanceado mayor que 50 %**.
H0: acierto balanceado ≤ 50 % (Kronos no distingue subidas de bajadas mejor que una moneda, aunque tenga sesgo).

### Métrica primaria

Acierto balanceado = ½·(acierto en bases donde el mercado subió + acierto en bases donde bajó). Bases con r = 0 o r̂ = 0 no se cuentan (igual que KT-002).

Muestra: filas de `data/kt002/predicciones.csv` con hora UTC de base múltiplo de 4 (el subconjunto sin solape de KT-002), base posterior al registro de KT-004.

### Regla de aprobado/rechazo (una sola evaluación, al llegar al n fijado)

- Intervalo: bootstrap por bloques circulares de 7 días (42 bases), 10 000 réplicas, semilla 42. Unilateral, α = 0,025 (equivale al bilateral 0,05 usado en KT-003).
- **APRUEBA** si se cumplen las dos:
  1. el límite inferior del intervalo unilateral 97,5 % del acierto balanceado es > 50 %;
  2. guarda contra el sesgo: el acierto bruto de Kronos es mayor que el de cada referencia trivial («siempre sube», «siempre baja», «persistencia», «reversión») sobre las mismas filas. La guarda no exige significancia, solo que ninguna referencia trivial iguale o supere a Kronos.
- **RECHAZA** en cualquier otro caso. Si (1) se cumple pero (2) no, se informa como "acierto explicado por una regla trivial", rechazo.
- Sin miradas intermedias con poder de decisión: no se para antes por resultados buenos ni malos. El resumen horario de KT-002 seguirá mostrando tasas (eso no se puede evitar); por eso la regla de parada es solo por n o por fecha, nunca por resultado.
- Corrección por pruebas múltiples: un solo test primario. Las comparaciones contra cada referencia y los resultados de TimesFM/KT-001 son descriptivos.

### Potencia y tiempo

- Efecto de planificación: **55 %** de acierto balanceado (rebajado desde 56,9 % por la maldición del ganador y la duda de contaminación). MDE con potencia 80 % y α unilateral 0,025: n ≈ 785 bases independientes.
- Corrección por dependencia: las 6 bases diarias sin solape comparten régimen; asumo efecto de diseño 1,25 → **n fijo = 1000 bases puntuadas**.
- Ritmo: 6 bases sin solape por día; KT-002 ya pierde horas (3 omitidas en su primer día). Con 80 % de cobertura ≈ 4,8 bases/día → **≈ 210 días, hacia mediados de mayo de 2027**.
- Fecha límite: si al **2027-10-20** no se llegó a 1000, se evalúa con lo que haya, con la misma regla, y el resultado se etiqueta "potencia insuficiente": un rechazo así no descarta a Kronos, solo cierra KT-004.
- Efectos menores a ~5 puntos no se van a poder distinguir del azar. Eso hay que aceptarlo antes de empezar.

### Costos

KT-004 **no apunta a operar** y no puede aprobar ninguna estrategia. Lo dejo explícito con números post corte (post hoc):

- Retorno direccional bruto medio de Kronos: +0,041 % por base; neto tras 0,20 % de ida y vuelta: **−0,16 %**.
- El |retorno real| medio a 4 h es 0,62 %. Para cubrir 0,20 % con operaciones a 4 h haría falta, aproximadamente, un acierto ≥ 0,5 + 0,002/(2·0,0062) ≈ **66 %**. Ni el mejor caso observado se acerca.
- Conclusión: aun si KT-004 aprueba, solo diría que Kronos "ve algo" en la dirección a 4 h. Llevarlo a dinero exigiría otra variante, otro horizonte y la Fase 0 completa de `hypothesis-gate`.

### Riesgo de sobreajuste

- La idea (Kronos solo, acierto balanceado, referencia reversión) sale de mirar KT-003. Por eso no se prueba en KT-003 ni en ningún dato anterior al registro.
- No hay parámetros que ajustar: modelo, horizonte, contexto, semilla y muestra quedan fijos en KT-002.
- Riesgo de transferencia: KT-003 usa una base por día (00:00 UTC); KT-002 usa 6 horas distintas por día. Si el efecto dependía de la hora, KT-004 puede fallar por eso. No se agregarán cortes por hora después de ver resultados.
- Riesgo de fallos operativos de KT-002 (horas omitidas): se cuentan, no se rellenan.

### Conteo de intentos

- KT-004 suma **1** variante confirmatoria al conteo de intentos del frente Kronos/TimesFM (no financiero, no cambia el N canónico de resultados financieros).
- Se declara que Kronos se eligió entre 3 modelos (Kronos, TimesFM, KT-001) y que el autor de la propuesta probó, en exploración, 4 referencias triviales y cortes por trimestre y por magnitud. Ninguno de esos cortes entra en la regla.

## 3. Alternativa (solo si el usuario prefiere no abrir una hipótesis)

**No registrar KT-004 y dejar KT-002 como está, solo descriptivo**, agregando a su resumen el acierto balanceado y las referencias «siempre baja» y «reversión» como nuevas columnas descriptivas en una variante de reporte aparte (sin tocar el cálculo ni el registro de KT-002). Costo: casi nada. Contra: sin regla previa, cualquier "Kronos acierta 57 %" que aparezca en mayo de 2027 seguirá siendo descriptivo y no confirmará nada. Por eso recomiendo la principal.

Descarté por falta de evidencia: filtros por magnitud del retorno previsto (no monótono), filtros por régimen o año (post hoc puro) y cualquier umbral para operar (no cubre costos).

## 4. Lo que falta antes de ejecutar

1. Auditoría de `desconfiado` hasta quedar sin problemas ALTOS ni MEDIOS.
2. OK explícito del usuario (`CLAUDE.md`: hipótesis nueva). Según `hypothesis-gate`, los puntos de Fase 1 (frase falsable, regla de corte) deben quedar aceptados por el usuario, no completados por el agente: esta propuesta los sugiere, el usuario los confirma o cambia.
3. Registro `docs/KT-004_registro_prospectivo.md` con fecha y hora UTC de inicio **antes** de la primera base que cuente, y `tools/kt004_evaluar.py` probado con datos sintéticos, en rama propia.

## 5. Resumen sencillo para el usuario

- En los datos históricos, Kronos acertó la dirección un 57 % de las veces. Revisé si eso era solo porque tiende a decir "baja" y no lo parece: acierta igual o mejor cuando dice "sube".
- Pero eso lo encontré mirando los mismos datos, y Kronos ganó entre 3 modelos, así que puede ser suerte. La única forma honesta de saberlo es probarlo con datos nuevos.
- Propongo usar los pronósticos que KT-002 ya hace cada hora, desde hoy, con una regla fija: si después de 1000 pronósticos (unos 7 meses) Kronos supera claramente el 50 % y le gana a reglas tontas como «siempre baja», se aprueba; si no, se descarta. TimesFM queda fuera de la prueba.
- Aunque apruebe, no sirve para ganar dinero a 4 horas: haría falta acertar cerca del 66 % para cubrir comisiones.
