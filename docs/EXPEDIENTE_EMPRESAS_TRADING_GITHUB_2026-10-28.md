# Kronnos — Expediente detectivesco de GitHub de firmas de trading
Fecha: 2026-10-28. Estado: investigación pública. No implica instalación, licencias aprobadas ni estrategias rentables.

## Metodología
Verificar GitHub oficial, distinguir autores originales de forks y terceros, inspeccionar propósito y compatibilidad, no inferir código privado de trading de un repo publicado. Evaluar actividad, tests, security, licencia, acceso a datos/API y costo ANTES de adoptar. Código público no prueba que se use internamente para órdenes o alpha.

## Hallazgos verificados
- Jane Street https://github.com/janestreet : 411 repos en vista GitHub de fecha investigada. core, base, async, hardcaml, magic-trace. Solo patrones de fiabilidad; no instalar OCaml/FPGA para Kronnos sin problema medido.
- Two Sigma https://github.com/twosigma : memento (https://github.com/twosigma/memento) describe pipeline incremental con procedencia reproducible; PRIORIDAD ALTA, estudiar patrón, no necesariamente instalación. flint (https://github.com/twosigma/flint) requiere Spark 2.3/2.4 según README: no instalar; copiar idea de joins temporales sin filtración futura. Cook aparece archivado en org: no implementar Kubernetes.
- Man Group https://github.com/man-group/ArcticDB : datos DataFrame versionados Python; BSL 1.1 restringe uso en producción y servicio de base de datos sin acuerdo; evaluar licencia y necesidad antes de cualquier instalación.
- Hudson River Trading https://github.com/hudson-trading : heracles-ql (https://github.com/hudson-trading/heracles-ql), lenguaje tipado de alertas sobre VictoriaMetrics, README avisa obra en construcción. corral C++20 no necesario en scripts Python. Página institucional de OSS: https://www.hudsonrivertrading.com/open-source-at-hrt/
- Goldman Sachs https://github.com/goldmansachs/gs-quant : biblioteca Python para derivados y riesgo; acceso a API institucional requiere client ID/secret. Estudiar lógica local libre, no asumir acceso completo.
- G-Research https://github.com/g-research : entidad de investigación financiera con proyectos de datos, ML, seguridad e infraestructura; investigar repos individuales antes de adopción.
- IMC Trading https://github.com/imc-trading : infraestructura, networking, testing; iceberg-python es fork de Apache, no tecnología necesariamente creada en IMC.
- Jump Trading https://github.com/jumptrading : luddite actualizado en 2024; influx-spout archivado. No prioritario.
- Wintermute Research https://github.com/WintermuteResearch : Solidity y desafios Alpha, no inferir estrategia de producción.
- D. E. Shaw https://github.com/deshaw/pyflyby : herramientas Python de productividad, MIT; baja prioridad para pipeline headless.

## Proveedores de infraestructura de trading, no fondos cuantitativos
- QuantConnect https://github.com/QuantConnect/Lean : motor backtesting/event-driven Python/C#, Apache 2.0; candidato IMPORTANTE para benchmark externo de simulación, no incorporarlo al sistema productivo ni usar live.
- Nautech Systems https://github.com/nautechsystems/nautilus_trader : motor Rust/Python basado en eventos y backtesting determinista, LGPL 3.0; candidato IMPORTANTE para estudiar arquitectura y comparar costo/resultado de simulación.
- CCXT https://github.com/ccxt/ccxt : normaliza APIs de exchanges y límites de tasa; para mercado BTC; no usar métodos de órdenes ni conectar claves sin autorización y revisión.
- Cada motor adicional aumenta superficie de mantenimiento y dependencias; pruebas de validación de resultados comparando un subset, sin añadir nuevas hipótesis.
  
## Puntuación práctica (no calidad de firmas)
P0: integridad y pruebas de Kronnos ya previstas (#42/#45/#46), sin operar capital real.
P1: Two Sigma memento: manifiestos de origen, timestamps, SHA y caché verificable.
P1: independiente de ejecución: piloto de LEAN o NautilusTrader para contrastar simulaciones en muestra fija, sin optimizaciones ni comercio real.
P1: patrones de GS Quant para análisis de riesgo, si se pueden ejecutar sin APIs institucionales.
P2: evaluar reglas de heracles-ql como diseño de alertas, pero mantener stdlib hasta necesitar VictoriaMetrics.
P2: CCXT SOLO para adquisición read-only si superior a los clientes actuales, respetando rate limits y seguridad.
P3: ArcticDB sujeto a licencia, escala y costo. Jane Street magia de rendimiento y C++ solo ante necesidad medida.

## Correcciones del expediente de Gemini
- Jane Street publica OCaml y hardware tooling, eso no permite aseverar que 'casi todo' su trading corra en OCaml o FPGA.
- Two Sigma usa Memento para reproducibilidad, pero GitHub no demuestra petabytes, notebooks ni detalle de su estrategia interna.
- Citadel vs Citadel Securities: repos de competencias terceros no son software real de producción.
- No atribuir a un fork proyectos originales de otros autores.
- Los conceptos 'open source', 'source available' y 'production free' no son equivalentes.

## Fuentes
https://github.com/janestreet
https://github.com/twosigma/memento
https://github.com/twosigma/flint
https://github.com/man-group/ArcticDB
https://github.com/hudson-trading/heracles-ql
https://github.com/goldmansachs/gs-quant
https://github.com/g-research
https://github.com/imc-trading
https://github.com/jumptrading
https://github.com/WintermuteResearch
https://github.com/deshaw/pyflyby
https://github.com/QuantConnect/Lean
https://github.com/nautechsystems/nautilus_trader
https://github.com/ccxt/ccxt

## Regla de continuidad
Cuando el usuario consulte el GitHub institucional y trading para Kronnos, leer este expediente, comprobar cambios actuales en origen, no repetir afirmaciones no verificadas y conservar uso minimo de IA. No merge ni instalar nada basándose solo en esta investigación.
