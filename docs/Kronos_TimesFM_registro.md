# Kronos + TimesFM: KT-001

2026-10-19 Costa Rica. Autor Codex, revisor Claude pendiente.

Usuario autoriza la integracion y prueba tecnica conjunta («VAMSO }»). Variante propuesta y aceptada: promedio fijo 50/50 de retornos previstos a cuatro horas, calculados contra el mismo ultimo cierre observado. No optimizar pesos. Esta variante es distinta de Kronos solo. Registro local previo a resultados; no es actualizacion del N canonico del programa.

Configuracion tecnica: Kronos-small, tokenizer base, 400 velas sinteticas horarias, cuatro pasos futuros, 20 trayectorias, T=1/top_p=0.9/seed=42. TimesFM 2.5 200M, punto mediano de cierre, misma ventana de 400 cierres y cuatro pasos, sin fine-tuning. Elegido antes de ejecutar por tamaño para CPU, sin comparar beneficios con otras versiones. Codigo TimesFM e51928e27119cb17bebc005be2696b75e0a9e688; paquete 3.0.2 contiene la implementacion 2.5. Pesos no son TimesFM 3.0.

No se pasa la salida de un modelo al otro. Kronos recibe OHLCVA sintetico; TimesFM solo cierre de esas mismas velas. Media de retorno esperado por muestreo de Kronos y mediana de TimesFM: combinacion heuristica de estimadores diferentes, no una distribucion calibrada ni una probabilidad de ganar. No mezclar cuantiles para producir intervalos conjuntos.

Prueba: formas, valores finitos, alineacion de cuatro timestamps y calculo exacto 0.5*(K/ultimo-1)+0.5*(T/ultimo-1). Guardar salida por modelo y conjunta, versiones/revisiones y hashes de pesos. Sin datos de mercado, metricas de rentabilidad, ordenes, MT5 o tareas programadas. Los cuatro valores generados no prueban independencia ni precision.

Estado previo: pendiente de ejecucion. Preflight del skill TimesFM correcto en CPU: ~13.7 GB RAM disponible y ~298 GB disco libre. Primera ejecucion del checker fallo por codificacion de consola; repeticion con Python -X utf8 correcta, sin editar upstream. Clon reporta cuatro imagenes de ejemplos como punteros LFS incorrectos; no son codigo ni pesos usados.

## Resultado tecnico

Primera ejecucion: PASS_TECHNICAL_ONLY en 141.06 s incluyendo descargas/carga/hashes. Ambas salidas finitas, cuatro timestamps alineados, media 50/50 correcta y rechazo de fechas distintas verificado. pip check correcto. Checkpoint TimesFM fijado antes de inferir: 1d952420fba87f3c6dee4f240de0f1a0fbc790e3. Tres archivos de pesos hasheados SHA256 en tools/ensemble-output/report.json. Salida en synthetic_ensemble.csv y entrada en synthetic_input.csv, versiones en requirements-resolved.txt, dentro de esa misma carpeta. Los resultados sinteticos no miden acierto ni retorno de BTC. No se modifican pesos tras ver salidas.

Repeticion offline del script final: PASS_TECHNICAL_ONLY, 29.91 s; ejecucion completada con HF_HUB_OFFLINE=1. Referencia ejecutable: tools/kronos_timesfm_smoke.py. Python: tools/kronos-env/Scripts/python.exe. La funcion combine rechaza timestamps distintos, referencia invalida y precios no positivos/no finitos; promedia retornos simples al mismo cierre base. TimesFM recibe cierres y Kronos OHLCVA, no identicas variables.

Evaluacion de estrategia sigue pendiente de Fase 0 real, reserva/cortes, procedencia de entrenamiento de ambos checkpoints, costos y registro canonico de variantes. No se concluye que la combinacion resuelva el diagnostico de potencia de Kronos solo. Regla propuesta de compra 0.60 %, salidas/riesgo/costos/corte previos se conservan como diseño pendiente de viabilidad.
