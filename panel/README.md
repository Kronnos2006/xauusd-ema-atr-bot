# Laboratorio visual Kronos × TimesFM

Panel local para explorar KT-001 y ejecutar de nuevo ambos modelos sobre 400 velas **sintéticas**, con horizonte de cuatro horas y combinación fija 50/50. Sin datos de mercado, órdenes ni backtest. La guía animada reproduce salidas; el botón **Ejecutar modelos** sí lanza inferencia Python offline.

Desde la raíz del proyecto:

```powershell
python panel/server.py
```

Abrir http://127.0.0.1:8765. El servidor escucha únicamente en loopback y sirve una lista fija de recursos. Ctrl+C lo detiene. Una sola inferencia a la vez; timeout de cuatro minutos. No crea servicios ni tareas programadas. Los modelos se ejecutan en CPU usando tools/kronos-env/Scripts/python.exe, con los pesos ya guardados en tools/kronos-cache. Si faltan, el panel permite explorar la evidencia pero la ejecución requiere completar la instalación y la descarga inicial autorizada.

Los resultados de nuevas ejecuciones se guardan en panel/runtime, separado de la evidencia versionada en docs/evidencia/KT-001. Se muestran las etapas reales emitidas por el proceso, no porcentajes simulados. La repetición usa semilla y configuración fijas; no está diseñada para buscar variantes ganadoras.

Funciones: capas de modelos, contexto visible, inspección OHLC al pasar el cursor, horizonte de 0–4 h, guía paso a paso, tabla por horizonte, fórmula de combinación, revisiones/SHA256 y descarga JSON. Los gráficos mantienen la última salida completa mientras trabaja el motor. Los precios están en unidades artificiales; no se muestran como BTC ni como cotización actual. Las fechas de la serie son etiquetas sintéticas; la fecha de ejecución se muestra en Costa Rica.

El modelo TimesFM es 2.5 (200M), aunque la implementación se instala desde el paquete 3.0.2. Kronos promedia 20 trayectorias; TimesFM aporta una mediana. La combinación de esos estimadores no es un intervalo calibrado. Revisión por Claude pendiente.

## Control prospectivo del mercado (KT-002)

**Crear predicción BTC** descarga 400 velas BTCUSDT Spot horarias cerradas desde la API pública de Binance y registra cuatro pronósticos antes de sus cierres. Usa la misma configuración fijada, con 20 trayectorias explícitas Kronos y mediana TimesFM. El registro se guarda localmente en `panel/market-records/`, excluido de Git por ser datos de ejecución; respáldalo para conservar el seguimiento. No es el ensayo sintético ni un backtest.

El servidor revisa cada 60 segundos los cierres vencidos y registra resultados separados sin sobrescribir el pronóstico. El navegador puede cerrarse mientras el servidor siga activo. Al detener el servidor se detiene la observación; al reiniciarlo retoma pendientes. No se crean tareas programadas. Una predicción pendiente bloquea otra hasta resolver +4 h para evitar solapamiento. El siguiente pronóstico se inicia con el botón; no se genera automáticamente.

La dirección se puntúa 1/0; el precio, por error absoluto y score relativo a la referencia «el precio no cambia»: 100 perfecto, 0 igual a referencia, negativo peor. Mercado sin cambio: score relativo indefinido. Se explica cada acierto/error y el aporte cuantitativo sin inventar causas macro. Resumen principal solo +4 h.

La fracción de trayectorias alcistas de Kronos **no es probabilidad calibrada**; q10–q90 TimesFM es intervalo nominal 80 %, sin cobertura demostrada para BTC. Tras observar el mercado se registra Brier descriptivo y cobertura. No existe probabilidad conjunta del promedio. Las mejoras se proponen tras 30 emisiones resueltas, sin ajuste automático. El protocolo completo y sus límites están en docs/KT-002_control_prospectivo.md. Una sola fuente de mercado; revisión independiente y validación financiera siguen pendientes.
