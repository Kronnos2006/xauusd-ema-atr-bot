# ATLAS — Laboratorio de estrategias, piloto inicial

**Estado:** implementación experimental aislada, no estrategia validada.

## Contrato
- Entrada: barras con aperturas/cierres UTC, señales preregistradas con ID y sello externo **verificado por el proceso que entrega los datos**. El campo booleano es un control de admisión, **no prueba criptográfica** de un sello; se requiere verificador remoto independiente en la fase de integración.
- La última señal conocida al cierre de la barra anterior determina posición para la barra siguiente. Nunca se utiliza la señal publicada dentro de la barra que se evalúa.
- Posición -1, 0, +1. Ejecución sintética a apertura y cierre de la misma barra para evitar suponer financiación/overnight. Cargo costo por ambos lados para cada operación; comparo contra estar largo en cada barra con idénticos costos.
- El laboratorio entrega historial, rendimiento neto simulado, benchmark y drawdown; no genera órdenes, no se conecta a proveedores, no toca `data/kt002`.
- No interpreta resultados sintéticos como evidencia de rentabilidad. No hay optimización, walk-forward ni aprobación de tesis para simulación por este mero módulo.

## Uso programático
```python
from atlas.laboratorio import Barra, Senal, simular
resultado = simular(barras, senales, costo_lado=0.0015)
```

## Pendientes antes de promoción
1. Verificación criptográfica independiente de preregistro y publicación anterior al corte.
2. Pruebas sobre datos de mercados reales con origen, reglas y costos documentados.
3. Protocolo walk-forward, benchmark y holdout sellado sin filtración.
4. Risk officer y aprobación auténtica, sin confiar en identidades de cadena.
5. CI en GitHub con pruebas de regresión y evidencia de que KT-002 permanece intacto.

## Versión metodológica de costos (2026-10-24)
- **v1** (commits hasta `4cb744e`): cobraba entrada y salida en **cada barra**, también al benchmark. Con precio plano, 180 barras de 4 h, el benchmark perdía −41,7 % solo por costos y una estrategia en efectivo "le ganaba". Sesgo a favor de cualquier estrategia con tiempo fuera del mercado.
- **v2** (`MODELO_COSTOS = "costo-por-cambio-de-posicion-v2"`): costo por unidad de posición que cambia (entrada, salida, giro), liquidación de lo abierto al final; el benchmark paga una entrada y una salida. Con el mismo precio plano: benchmark −0,30 %.
- Ningún resultado guardado en el repo usaba `simular()` (las salidas `research/atlas/salidas/` son del piloto de tesis), así que no hay resultados v1 que conservar. Cualquier cifra v1 citada fuera del repo debe leerse como sesgada.
