# Protocolo de cooperación ORION — Claude y ChatGPT
**Fecha:** 2026-10-22. **Autoridad final:** dueño del proyecto.

## Arquitectura de control compartido
- **ORION** es el panel público de observación y una puerta de entrada a tareas registradas, no un motor de ejecución de agentes.
- **Claude** y **ChatGPT** son operadores diferenciados; ninguno puede fingir el estado, aprobación, invocación o resultados del otro.
- **GitHub** es el registro común de issues, ramas, PR, pruebas y despliegues. Para tareas privadas se utiliza el entorno privado respectivo, nunca GitHub Pages público.
- **Un único despliegue Pages** desde `.github/workflows/orion-pages.yml` publica:
  - `/`: ORION;
  - `/orion/`: alias de ORION;
  - `/visor/`: copia byte a byte de `docs/visor/index.html` del visor existente de Claude.
  El visor existente se conserva sin editarlo. No configurar otro workflow que publique Pages en este repositorio: debe incorporarse a la misma publicación.

## Propiedad de archivos y prevención de sobrescrituras
| Propietario funcional | Rutas | Protección |
|---|---|---|
| Ciencia y colector existente | `tools/kt002_prospectivo.py`, `.github/workflows/kt002.yml`, `data/kt002/**`, preregistro y resultados | **NO TOCAR** durante trabajo de ORION; cambios reservados al procedimiento del dueño |
| Visor de Claude | `docs/visor/**` | ORION solo lo copia al publicar; no edita la fuente |
| ORION y visualización | `dashboard/**`, `tools/centro_control.py`, `tests/test_centro_control.py` | Cambios por rama y PR, pruebas y revisión |
| Despliegue compartido | `.github/workflows/orion-pages.yml` | **Un solo publicador** para Pages; revisión de colisiones previa al merge |
| Auditor y analista independientes | `.claude/agents/desconfiado.md`, `.claude/agents/analista.md`, informes de esos autores | Veto y propiedad independiente; ningún operador modifica sin autorización |
| Gobierno del proyecto | `CLAUDE.md`, `AGENTS.md`, sellos y decisiones del dueño | No editar sin autorización explícita separada |

## Contrato de trabajo Claude/ChatGPT
1. Registrar solicitud en **Issues → Nueva incidencia → ORION · Solicitud coordinada**, con objetivo, enlace de evidencia y responsable propuesto.
2. El agente que la atienda confirma que realmente dispone de acceso. Un issue no ejecuta a Claude ni a ChatGPT.
3. Declarar archivos a tocar, alcance y riesgos. Comprobar PRs abiertos y cambios recientes antes de escribir.
4. Trabajar en rama separada; no editar directamente `master` para funcionalidades nuevas. Crear PR con pruebas, impacto y forma de revertir.
5. Comprobar cambios del otro agente antes de merge; ante colisión, detener el merge y resolver integración sin aplicar fuerza ni sobreescribir.
6. Los PR que toquen cálculos, datos, modelos, auditoría, holdouts o experimentos exigen las autorizaciones independientes ya vigentes; el gerente no suplanta las revisiones.
7. El dueño puede consultar y ordenar tareas, pero toda operación mutante requiere identidad autenticada, autorización y registro de quién hizo qué.
8. Nunca exponer tokens, credenciales, datos privados de la Oficina o contenido sensible en Pages o un issue público.

## Qué significa «controlar»
- **Disponible hoy:** consultar estado público de Github Actions, issues y métricas KT-002; abrir visor de Claude; registrar solicitudes autenticadas en GitHub; revisarlas desde los operadores que tengan conexión.
- **No disponible hoy:** arrancar remotamente Claude/ChatGPT desde Pages, leer sus sesiones privadas o enviarles instrucciones de ejecución automática; asumir aprobación a partir de un issue.
- **Para control real remoto:** backend autenticado, secretos en servidor, cola de trabajos por agente con estados verificables, permisos por función, bitácora de acciones, aprobación humana por operación, revocación, límites de cuota, e interfaz a APIs/conectores autorizados. No conectar agentes autónomos con privilegios irrestrictos a un repositorio público.

## Comprobación de entrega
La acción de publicación debe validar que el visor de Claude publicado es idéntico a `docs/visor/index.html`, que ORION incluye el enlace a `/visor/`, que la versión pública no contiene el enlace a la Oficina privada y que un único workflow despliega la versión conjunta. Si cualquiera falla, no publicar.
