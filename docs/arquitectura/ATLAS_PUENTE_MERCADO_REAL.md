# ATLAS: puente de mercado archivado a laboratorio

`atlas/puente_mercado.py` lee velas de Binance archivadas en JSON y devuelve `Barra` para el simulador. No hace peticiones de red, no escribe ficheros, mantiene la huella SHA-256 de entrada y admite corte UTC; excluye velas todavía abiertas.

Ejemplo: `cargar_barras("data/mercado/btc_4h.json", "4h", "2026-10-24T08:00:00Z")`.

**Límite científico:** una vela que cerró antes de un corte no demuestra que el archivo existía o se recibió entonces. Por eso, los resultados históricos solo son exploratorios si no existe evidencia independiente de recepción. Las señales necesitan sellos externos auténticos. No inventar señales prospectivas para justificar pruebas históricas.

**Próximo requisito:** sellos GitHub y preregistros verificables, más evaluación sobre señales genuinamente registradas antes del resultado. No ejecutar órdenes.
