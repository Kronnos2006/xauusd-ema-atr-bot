# Evaluación: 4 complementos del post de @sebastiankra.ia

Fecha: 2026-10-20 · Autor: Jefe de Innovación · Pedido del gerente · Solo lectura, nada instalado.
Limitación: la API de GitHub no está disponible en esta sesión; estrellas/licencia vienen de las páginas de los repos (WebFetch). Las fechas de último commit NO se pudieron leer: verificar antes de instalar.

## Resumen
| # | Complemento | Veredicto |
|---|---|---|
| 1 | Ponytail | PROBAR (con medición propia) |
| 2 | OmniRoute | DESCARTAR |
| 3 | Graphify | DESCARTAR por ahora (reevaluar si el repo crece) |
| 4 | Agent Skills | PROBAR 2-3 skills sueltas, no el paquete completo |

## 1. Ponytail
- Fuente: https://github.com/DietrichGebert/ponytail · MIT · ~169k estrellas (según la página) · 363 commits.
- Qué hace: un skill con una regla: antes de escribir código, buscar si ya existe (reusar, librería estándar, dependencia existente) y solo entonces escribir lo mínimo. Plugin de Claude Code con 2 hooks (requiere `node`).
- Cifras: -53% código, -41% tiempo, -26% costo, -45% tokens. Son del propio proyecto (39 tareas, 5 corridas, repo FastAPI+React), sin evaluador independiente. Verificables solo parcialmente. Ojo: ese benchmark es de apps web; este repo es investigación/Python, el efecto puede ser menor.
- Entorno: Claude Code sí (plugin). App del celular no. Costo: gratis; agrega texto a cada sesión (tamaño no documentado, medirlo).
- Riesgo: hooks ejecutan código local; llamadas de red no documentadas; "menos código" puede chocar con el rigor del proyecto (tests, pre-registro). Los dos hooks hay que leerlos antes.
- Veredicto: PROBAR en una sola rama/tarea no sensible, comparando tokens con y sin. Adopta quien: operaciones.

## 2. OmniRoute
- Fuente: github.com/diegosouzapw/OmniRoute · MIT · ~74k estrellas, v3.8.51 (30-sep-2026), según un blog de Pinggy (empresa de túneles que se promociona; fuente secundaria).
- Qué hace: gateway autoalojado (puerto 20128, API tipo OpenAI) que reparte pedidos entre cientos de proveedores y salta al siguiente cuando uno se queda sin cupo; incluye pools gratuitos sin autenticación.
- Entorno: exige un servidor propio (Docker) y apuntar el cliente a él. No sirve en la app del celular y en la nube remota no hay dónde alojarlo sin costo.
- Riesgos (graves): (a) concentra todas las claves/tokens OAuth en un solo servicio; contraseña por defecto `CHANGEME`; (b) los "pools gratuitos" mandan el código y prompts a terceros desconocidos, choca con la regla de no enviar datos a servicios no autorizados; (c) enrutar cuentas de suscripción de Claude por un tercero probablemente viola los términos de Anthropic (no verificado en el texto oficial; revisar antes de cualquier uso); (d) cambiar de modelo a mitad de trabajo rompe la consistencia de resultados de investigación.
- Cifras del post: no hay cifra, solo promesa; los números de tokens gratis son del propio proyecto y fueron revisados.
- Veredicto: DESCARTAR. Para ahorrar tokens hay opciones sin terceros (modelo más barato en tareas simples, menos contexto).

## 3. Graphify
- Fuente: github.com/safishamsi/graphify (también aparece Graphify-Labs/graphify; confirmar cuál es el oficial) · ~130k estrellas · Apache-2.0/MIT · Python 3.10+, `uv tool install graphifyy` (doble "y": ojo con paquetes imitadores).
- Qué hace: arma un grafo de conocimiento del repo (código con tree-sitter, local, sin LLM; docs/PDF/imágenes pasan por el modelo) para consultar sin releer todo.
- Cifras: "-80% de tokens" aparece en la promoción de un producto de pago (Graphify Cloud); el método no está a la vista. Solo del autor.
- Entorno: Claude Code sí (skill + CLI local); celular no. Costo: gratis local; la parte semántica gasta tokens.
- Riesgo: dependencia Python extra y un proveedor a configurar si se usa extracción por API (algunos, como Kimi, envían a servidores en China: no usar). Este repo es chico y está documentado en CLAUDE.md/contexto compartido: el beneficio es bajo y construir el grafo cuesta tokens.
- Veredicto: DESCARTAR por ahora. Reevaluar si el repo supera varios cientos de archivos.

## 4. Agent Skills (Addy Osmani)
- Fuente: https://github.com/addyosmani/agent-skills · MIT · ~109k estrellas · 702 commits · 25 skills (24 de ciclo + 1 meta) en Definir/Planear/Construir/Verificar/Revisar/Publicar, 9 comandos y 4 personas.
- Qué hace: flujos en Markdown con pasos y puertas de verificación; instalación `/plugin marketplace add addyosmani/agent-skills`. Tiene carpeta `hooks/` (contenido no leído).
- Cifras: el post no trae cifra de ahorro; no hay nada que verificar. Es proceso, no ahorro: instalar 25 skills ocupa contexto y puede costar más tokens.
- Solapamiento: el proyecto ya tiene hypothesis-gate, data-integrity, desconfiado, etc. Varias skills duplican lo existente; otras (revisión de código, tests, git/CI) sí podrían aportar.
- Veredicto: PROBAR solo 2-3 skills sueltas (revisión y pruebas), copiadas a `.claude/skills/` tras leerlas, no el paquete completo. Adopta quien: operaciones/documentación.

## Qué necesito del gerente
- OK para que el usuario pruebe Ponytail en una rama (mide tokens antes/después). Nada se instala sin ese OK; instalar es del usuario.
- Antes de cualquier instalación: leer hooks y SKILL.md de lo elegido y confirmar fecha del último commit.
- Si se quiere ahorrar tokens de verdad: priorizar medir el consumo actual (qué sesiones gastan más) antes de sumar herramientas.
