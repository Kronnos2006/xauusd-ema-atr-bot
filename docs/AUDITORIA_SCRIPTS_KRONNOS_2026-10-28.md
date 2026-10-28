# Kronnos — Auditoría de automatizaciones (2026-10-28)

**Estado:** modificaciones en PR apilado #47, sin fusión a master.
Se ha añadido auditoría estática AST y CI de pruebas, con SHA-256 por archivo. Este control cubre los scripts nuevos, no el repositorio completo ni la infraestructura viva.

## Hallazgos y acciones
1. CRÍTICO: el evaluador aceptaba fechas de commit controlables por el autor y una bandera de madurez. Se corrigió a FAIL CLOSED: siempre 0 operaciones válidas hasta comprobación externa sellada. No confundir SHA de Git y sello previo confiable.
2. ALTO: el recolector HTTPS validaba DNS antes de abrir conexión susceptible de rebinding. Se deshabilitó el CLI para uso de red y se exige aislamiento de egreso externo antes de activarlo. Hay función experimental, no habilitada en CI.
3. MEDIO: el manifiesto podía aceptar symlinks y valores de SHA sin validar. Se restringió.
4. MEDIO: el comparador admite solo claves consistentes y trades exactos, y rechaza tolerancias inválidas.
5. La auditoría de AST detecta importaciones LLM directas y ejecución dinámica, pero NO garantiza que un módulo importado no haga llamadas de red. Se añade auditoría humana de PR y tests.
6. La programación de informes en #45 sigue sin estar activa hasta que se fusione a master y se complete revisión.
7. No se modifican workflows existentes KT-002/guardia/ATLAS, ni se habilitan órdenes reales.

## Condiciones para despliegue
- PR #47, #46, #45 apilados, fusionar en orden solo tras revisión de permisos, scripts y workflow CI verde.
- Los controles ATLAS #42 y Bloqueo A siguen independientes: no declarar validez científica ni trading.
- El recolector deberá instalarse únicamente en runner con política de salida de red, DNS fijado o proxy que valide IP efectiva, y pruebas de rebinding antes de cualquier uso.
- Las herramientas de Memento/LEAN/NautilusTrader son patrones propios ligeros, no instalación de SDKs externos.
- GitHub Actions artifacts no reemplazan sello externo con retención inmutable.
