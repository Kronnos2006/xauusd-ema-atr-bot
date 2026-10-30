# KT-004: acierto direccional en activos no expuestos y período posterior a los modelos (pre-registro)

2026-10-30, Costa Rica. Autor: Claude. Pedido por el propietario (Kronnos) para acelerar la respuesta sobre Kronos/TimesFM.
Revisión independiente: ChatGPT/Codex. Auditor: `desconfiado` (a pedido). **Integra y aprueba el propietario.**
**Escrito antes de descargar datos o correr modelos de estos activos.** Nada de esta prueba corre hasta que este archivo esté en `master`.

## 1. Pregunta (una sola, primaria)
¿Kronos-small acierta la dirección del retorno a 4 h **más que «siempre sube»** en criptoactivos que el proyecto no ha mirado, usando solo datos **posteriores a la última modificación pública de los modelos**?

## 2. Por qué acelera
KT-002 junta 6 datos por día; distinguir 55 % de 50 % necesita unos 780 (≈ 4 meses). KT-004 usa historia ya existente pero **no expuesta**, así que se obtiene una muestra grande en horas.

## 3. Qué es y qué no es
- Diagnóstico de acierto de dirección. **No** es backtest de estrategia ni prueba de rentabilidad. Sin órdenes, costos ni capital.
- No usa BTC (su historia 2017–2026 quedó expuesta en KT-003).
- No modifica KT-002, KT-003 ni el N canónico de otros proyectos.

## 4. Configuración fija
- **Activos (4, fijos):** ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT (Binance spot, velas 1 h).
- **Período:** bases desde **2025-10-03 00:00 UTC** (día siguiente a la última modificación de TimesFM 2.5 en Hugging Face, ver KT-003 Enmienda C/D) hasta **2026-10-29 20:00 UTC**. Nada posterior.
  - Limitación declarada: que los pesos sean anteriores no **certifica** que estos precios estén fuera del entrenamiento; se lee como "probablemente fuera de muestra".
- **Datos:** ZIP mensuales de `data.binance.vision` con SHA-256 contra CHECKSUM; el mes en curso por API pública. Huecos, duplicados y velas OHLC inválidas se cuentan en `data/kt004/manifiesto_datos.json`; no se rellenan. Los CSV quedan sellados por SHA-256 antes de pronosticar.
- **Bases:** una cada 4 h (hora UTC múltiplo de 4), sin solape, igual al subconjunto que se interpreta en KT-002. Se salta la base si sus 400 velas de contexto no son contiguas o falta la vela objetivo; se cuenta.
- **Modelos, revisiones y parámetros idénticos a KT-002/KT-003:** Kronos-small `901c26c1…`, tokenizer `0e011738…`, 20 trayectorias, T=1, top_p=0.9, semilla 42 (lotes como KT-003); TimesFM 2.5 mediana; KT-001 50/50.
- **Métrica y objetivo idénticos a KT-002:** contexto 400 velas; r̂ = cierre previsto de la 4.ª vela / C₀ − 1; acierto si signo(r̂) = signo(r).
- **Referencias:** «siempre sube» (principal) y «persistencia» (descriptiva).
- n esperado ≈ 4 activos × ~2.300 bases ≈ 9.200 (se fija con la corrida de prueba, §7).

## 5. Análisis pre-declarado
- **Primario (uno solo):** diferencia de acierto Kronos − «siempre sube», agregada en los 4 activos.
  - Inferencia: **bootstrap por bloques de 1 día** sobre fechas (remuestrea días completos con los 4 activos juntos, conservando la correlación entre activos y dentro del día), 10.000 réplicas, semilla 20261030. p unilateral (H1: Kronos > «siempre sube»).
  - **Pasa** si p < 0,05 **y** la diferencia ≥ 2 puntos. Pasar significa solo "Kronos merece un confirmatorio prospectivo con costos"; **no** es ventaja ni autoriza operar.
  - **No pasa** en cualquier otro caso → Kronos a 4 h queda descartado como predictor de dirección para cripto, salvo enmienda registrada antes de nuevos datos.
- **Secundarios:** TimesFM y KT-001 contra «siempre sube», mismo método, corrección **Holm** entre los 3 modelos. Por activo y por trimestre: solo descriptivo, sin inferencia.
- **Contraste de robustez obligatorio:** el resultado primario repetido **sin el activo que más aporta**. Si el signo se invierte, se informa como "depende de un activo".
- **Costos (descriptivo):** se informa el acierto mínimo para cubrir 0,20 % ida y vuelta dada la distribución real de |r| a 4 h, por activo.
- No se agregan activos, períodos, horizontes ni cortes después de ver resultados. Cualquier variante es otro intento, se registra aparte y suma al conteo.

## 6. Exposición previa declarada
El autor no ha visto precios de estos 4 activos en este período dentro del proyecto. Los informes del analista solo trataron BTC. Si un revisor encuentra exposición previa, se anota aquí antes de correr.

## 7. Ejecución (en orden)
1. Este archivo en `master` (revisión independiente + OK del propietario).
2. **Corrida de prueba** (`lanzar.txt = prueba`): descarga, sella datos, cuenta bases y saltos, fija n exacto y tiempos. **Sin pronósticos.** Se anota como Enmienda A antes de seguir.
3. **Corrida completa** (`lanzar.txt = completo`) en GitHub Actions, en paralelo, desde `master`, con los datos sellados (aborta si cambia el hash).
4. Resumen por script: `data/kt004/resumen.md` y `resumen.json`. Una sola corrida; un bug solo se corrige si el código no hace lo que dice este registro, y se documenta como errata.

Código previsto: `tools/kt004_multiactivo.py` (derivado de `tools/kt003_historico.py`) y `.github/workflows/kt004.yml`. Se escribe después de aprobar este registro.
