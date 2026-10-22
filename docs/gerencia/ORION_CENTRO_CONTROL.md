# ORION — Centro de Control del Dueño (v1)

**Alcance:** aplicación local de solo lectura; gráficas, métricas y organigrama obtenidos de datos reales del repositorio.

## Instalación y ejecución
En una computadora con Python 3.10+ y una copia del repositorio actualizada:

```bash
python tools/centro_control.py status
python tools/centro_control.py serve
```

Abrir **http://127.0.0.1:8765** en el navegador de la misma computadora. Detener con Ctrl+C.
No se necesitan paquetes externos ni tokens de Claude.

Para generar una carpeta estática sin iniciar servidor:

```bash
python tools/centro_control.py build
```

Se crea `.local/centro-control/index.html` y `data.json`. Como el dashboard usa `fetch('./data.json')`, abrir el HTML con `file://` puede bloquear la carga: usar `serve` o `python -m http.server` en esa carpeta.

## Qué es real y qué no
- **Datos auténticos pero no en vivo:** la fuente KT-002 es `data/kt002/resumen.json` de la copia local. Para refrescar, actualizar la copia del repositorio y reiniciar `serve`; la página no ejecuta automáticamente `git pull`.
- Los intervalos Wilson son los publicados; el dashboard no reestima modelos ni modifica preregistros.
- **Grafo:** se basa en `docs/gerencia/equipo.json`; las líneas indican `reporta_a`, no llamadas o actividad real. Independencia se colorea aparte.
- **Github Actions/PRs/Oficina:** enlaces que abren los servicios originales. La Oficina es privada; esta web no sincroniza órdenes ni escalaciones.
- No hay autenticación ni servidor público. Escucha exclusivamente en `127.0.0.1`; no exponer por túneles ni redes sin implementar control de acceso.
- Sin órdenes, brokers, MT5, dinero real, escritura en GitHub, creación de agentes, lanzamiento de workflows ni modificación de KT-002. **No es una terminal de ejecución remota.**
- Las operaciones futuras solo se habilitarán con backend autenticado, control de roles, confirmación explícita, registros inmutables y revisiones independientes; se excluirán acciones prohibidas.
- No se mide el consumo real semanal de Claude porque esa información no existe en los archivos.

## Estructura
- `tools/centro_control.py`: assemble, build, status y servidor local.
- `dashboard/index.html`: interfaz responsive sin CDN ni dependencias de red.
- `tests/test_centro_control.py`: pruebas de integridad de entradas y generación.
- Salidas bajo `.local/centro-control/` no deben incluirse en commits ni desplegarse públicamente sin revisar datos.

## Próximo incremento
1. Integración read-only autenticada de GitHub (Actions/PR/issues) con caché, estados observados y timestamps. Nunca inferir "agente trabajando" solo por organigrama.
2. Comandos de gestión de issues con alcance limitado; separar consultas y mutaciones, pedir confirmación explícita.
3. Integración con Oficina privada **solo** si hay un conector autorizado compatible; sin copiar datos privados al frontend estático.
4. Gráficos de series históricas por snapshot; no inventar evolución desde un solo resumen puntual.
5. Auditoría de seguridad antes de permitir acceso externo.


## ORION publicado para celular (GitHub Pages)
El workflow `.github/workflows/orion-pages.yml` genera un sitio estático público en GitHub Pages cuando cambian los datos, cada cuatro horas y por ejecución manual.

**Enlace previsto después de la primera implementación exitosa:**
`https://kronnos2006.github.io/xauusd-ema-atr-bot/`

**Importante:** este enlace debe confirmarse desde la página de GitHub Actions/Pages. GitHub Pages puede requerir una habilitación inicial por el propietario en **Settings → Pages → Build and deployment → Source → GitHub Actions**; sin eso no se puede afirmar que esté publicado.

La versión pública elimina el enlace a la Oficina privada y las descripciones internas de los agentes; no utiliza claves ni credenciales. El número de agentes y los nombres/relaciones que aparecen son metadatos publicados, **no estado de actividad en vivo**.

Para actualizarlo manualmente: Actions → `ORION - Publicar GitHub Pages (móvil)` → Run workflow.
El contenido sigue reflejando un snapshot de GitHub con fecha UTC; aunque el despliegue sea reciente, los datos de KT-002 pueden estar atrasados. No poner órdenes, contraseñas, datos personales ni decisiones privadas en este sitio público.


## ORION v2 — telemetría pública y gráficos históricos (2026-10-22)
- **Histórico prospectivo real** a partir de `data/kt002/predicciones.csv`: solo observaciones evaluadas, únicas y bases en horas UTC divisibles por cuatro. Tasas acumuladas comparadas con el benchmark; no son operaciones ni rendimiento económico.
- **Actividad verificada** consulta sin token la API pública de GitHub: últimas 12 corridas de Actions e issues abiertos recientes. La consulta sale directamente del navegador, indica cuándo se realizó y muestra **NO VERIFICADO** si falla la API (incluidos límites de solicitudes).
- **Alertas** se basan en ese subconjunto de ejecuciones e issues, no son una certificación integral de todos los workflows.
- **Consola segura** admite actualizar la consulta y copiar un diagnóstico. No crea issues, no reejecuta workflows, no llama agentes ni altera datos.
- **Agentes Claude**: la red se basa en configuración `equipo.json`; la actividad de agentes privados continúa **NO VERIFICADA**. No fabricar estado «en vivo» sin telemetría explícita de esos agentes.
- El sitio de GitHub Pages es **público**. No contiene credenciales ni descripción privada de agentes en el snapshot. No introducir claves ni información de la Oficina privada.
- **Actualización**: las métricas de KT-002 se reconstruyen al publicar desde GitHub, mientras las tarjetas de Actions/Issues realizan peticiones directas al ver el panel. Si se abre desde celular, GitHub Pages debe estar operativo.
- **Pendiente** para operaciones de escritura y flujos de aprobación: backend autenticado, privilegios mínimos, registro de órdenes, protección contra abuso y auditoría externa. No se puede habilitar de forma segura en una web pública estática.


## Publicación conjunta sin sobrescribir el visor de Claude
Desde la versión protegida, el **único** workflow que debe desplegar GitHub Pages es `.github/workflows/orion-pages.yml`. En un mismo artefacto publica:
- `https://kronnos2006.github.io/xauusd-ema-atr-bot/` → ORION;
- `https://kronnos2006.github.io/xauusd-ema-atr-bot/orion/` → ORION (alias);
- `https://kronnos2006.github.io/xauusd-ema-atr-bot/visor/` → visor existente creado por Claude, copiado sin cambios de `docs/visor/index.html`.

Las URLs son públicas. El publicador comprueba que el visor de Claude se conserva byte por byte y que ORION no publica la Oficina privada. No editar el visor de Claude desde ORION; sus cambios de fuente se incorporan de manera íntegra a la siguiente publicación.

### Cooperación y trabajo desde el celular
ORION enlaza a **Issues → Nueva incidencia**, usando `.github/ISSUE_TEMPLATE/orion-solicitud.yml`. Las instrucciones se registran con la cuenta autenticada de GitHub, se asignan por responsabilidad y se ejecutan exclusivamente cuando Claude, ChatGPT o un operador autorizado las acepten por un canal conectado. Abrir un issue **no invoca agentes**.

Consultar el [protocolo de coordinación](../coordination/ORION_PROTOCOLO_COOPERACION.md) antes de editar workflows, visores o permisos. Las órdenes automáticas y la telemetría privada de Claude aún necesitan un servicio autorizado, autenticación, controles de acceso y auditoría. GitHub Pages no proporciona esas capacidades por sí mismo.
