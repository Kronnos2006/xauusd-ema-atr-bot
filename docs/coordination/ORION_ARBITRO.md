# ORION — Árbitro de tareas entre Claude, ChatGPT y operadores

## Qué hace
`.github/workflows/orion-arbitro.yml` permite que un usuario autenticado con permisos para ejecutar workflows consulte, reserve o libere una tarea pública con título `[ORION]`. La reserva usa `concurrency` por número de issue: las solicitudes simultáneas al mismo número se procesan secuencialmente.

Un comentario del bot de GitHub registra el evento `reserved` o `released`, el nombre GitHub de quien lo ejecutó y el operador **propuesto**, Claude, ChatGPT, Gerencia u Operaciones. El árbitro solo confía en comentarios con estructura interna publicados por `github-actions[bot]`; no acepta reclamaciones escritas por terceros como bloqueo auténtico.

La liberación solo puede hacerla la misma cuenta GitHub que reservó. No hay transferencia de reservas ni cambio de propietario sin liberación. Si una cuenta queda inaccesible, el dueño deberá gestionar una intervención excepcional y documentada; el sistema no fuerza un desbloqueo invisible.

## Cómo usarlo desde el celular
1. En ORION, registrar una tarea con el formulario ORION dentro de GitHub Issues; anotar el número del issue.
2. Abrir **Operaciones → Reservar o liberar tarea** para ir al workflow protegido en GitHub.
3. Presionar `Ejecutar flujo de trabajo`, escoger `master`, ingresar el número de issue, seleccionar `estado`, `reservar` o `liberar`, y el operador **propuesto**.
4. Verificar el resultado del workflow y el comentario automático en el issue. Los resultados se conservan en el historial de GitHub.
5. Cuando haya trabajo efectivo, el operador humano/IA conectado deberá añadir INICIO con su identidad real, rama y PR, y luego ENTREGA y pruebas. La reserva por sí sola **no constituye ejecución de Claude ni ChatGPT**.

## Protección
- El workflow no requiere contraseñas externas, solo `GITHUB_TOKEN` del propio repositorio, con `contents:read` y `issues:write`.
- No escribe en el código, no ejecuta modelos y no abre/cierra PR automáticamente.
- No modifica los archivos científicos o privados, holdouts, prerregistro, auditorías o reglas.
- No integra Claude con su sesión privada: para control automático futuro se necesita una API compatible y conectada expresamente, backend seguro y política de autorización.
- **Publicación Pages es pública.** No publicar tokens, prompts privados ni datos personales en issues.
- GitHub puede reejecutar un mismo job: el árbitro aplica la última secuencia válida; reintentar una reserva ya activa se rechaza sin generar otro evento.
- El alcance de la reserva es un único issue. No es un bloqueo real de Git ni impide que otra persona edite archivos directamente; las ramas, revisiones y protecciones GitHub siguen siendo necesarias.

## Pruebas
`python -m unittest discover -s tests -p 'test_orion_arbitro.py' -v`

## Qué falta para control directo de IA
Un servicio privado de orquestación, autenticación del dueño, conectores/API de cada proveedor, registro de ejecuciones observadas, límites de costo, permisos mínimos y autorización previa a cada acción de escritura. Hasta instalar y conectar esos sistemas, ORION no debe anunciar agentes «ejecutándose».
