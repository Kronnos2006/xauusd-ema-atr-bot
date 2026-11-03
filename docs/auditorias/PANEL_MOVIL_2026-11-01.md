# Validación visual móvil del panel ORION

Autor Codex, 2026-11-01. Base master b3e7abd. Revisión independiente y
aceptación del manual por el dueño pendientes. No certifica teléfono físico.

## Hallazgo y corrección

El navegador a 360 px mostraba documento de 767 px: el contenido mínimo de
la navegación expandía toda la cuadrícula. Se cambió la columna móvil a
`minmax(0,1fr)` y se permitió reducir sidebar/main; la navegación conserva
su desplazamiento interno. No se oculta el desbordamiento de la página.

## Evidencia de aceptación

Prueba automatizada `tests/panel_mobile_qa.cjs`, Playwright 1.56.1 y Edge
instalado, vista 360/390/1280 por 844 px. Quince combinaciones tamaño/pestaña
sin desbordamiento horizontal: resumen, modelos, agentes, operaciones y
actividad. Cuatro módulos visibles; sin errores JavaScript; error GitHub
503 simulado produce NO VERIFICADO. Fuentes locales generadas con --public;
no se consulta API real ni se disparan tareas desde la prueba.

Inspección visual realizada sobre captura completa de 360 px: texto legible,
tarjetas apiladas, fuentes accesibles, gráficas contenidas, alerta de fallo
visible. Las gráficas conservan etiquetas pequeñas: ampliar el navegador
puede ayudar; no se afirma conformidad de accesibilidad completa.

Capturas y report.json se generan bajo `.local/mobile-qa` y se adjuntan como
artifact al CI del PR. No versionar salidas ni instalar dependencias QA en
el entorno de producción. La prueba confirma ambos tamaños móviles de
viewport, no hardware, sistema operativo móvil ni conectividad del teléfono.

## Reproducción y manual

```powershell
npm install --prefix .local/ui-qa --no-audit --no-fund playwright@1.56.1
python tools/centro_control.py serve --public --port 8765
```

En otra consola, desde la raíz del repo:

```powershell
$env:PLAYWRIGHT_MODULE = (Resolve-Path '.local/ui-qa/node_modules/playwright').Path
node tests/panel_mobile_qa.cjs
```

Edge instalado es el predeterminado local; CI instala Chromium de Playwright.
Manual de uso: docs/gerencia/ORION_CENTRO_CONTROL.md. Solo el dueño acepta
la entrega y acredita F6.4 después de revisar evidencia y manual. No se
acreditan aquí ATLAS, modelos, auditoría global ni resultados financieros.
