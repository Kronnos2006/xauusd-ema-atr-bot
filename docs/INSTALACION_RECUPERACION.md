# KRONNOS: instalación y recuperación verificables

2026-11-01, Codex. Procedimiento técnico propuesto; aprobación del dueño
pendiente. No es acta final del proyecto ni autorización de estrategias.

## Componentes y dependencias

| Componente | Requisito | Alcance |
|---|---|---|
| Smoke de instalación/recuperación | Git y Python>=3.10; CI prueba3.13 | Biblioteca estándar, fixtures sintéticos temporales, sin red |
| Centro de control | Python>=3.10 | Genera snapshot de consulta; no activa agentes ni servicios remotos |
| Pruebas móviles | Node y Playwright1.56.1 aislado | PR99, requiere integración; APIGitHub simulada en pruebas |
| Evaluación Riskfolio | VenvPython3.13, requirements específicos | PR100, requiere integración; no instalar en entorno global |
| FreqAI/combinador prospectivo | Productor, datos, protocolo y trazabilidad | No aprobado; PR98 es propuesta, no configuración operativa |
| ATLAS confirmatorio | Censo exhaustivo, custodia y validación | PR42 bloqueado; sellos recuperados no resuelven todo |
| MT5/loggers/tareas existentes | Entorno externo al smoke | No se instalan, cambian ni ejecutan por este procedimiento |

`requirements.txt` general pertenece al trabajo de investigación más amplio;
no es necesario para el smoke o el panel. No ejecutar scripts de entrenamiento
o trading como paso de instalación. Conservar los entornos opcionales separados.

## Instalación de la comprobación técnica

Usar una copia autorizada del repositorio y un commit revisado/integrado.
Si ya existe una copia con cambios locales, comprobar `git status` antes
de actualizar. Nunca resetear, limpiar ni sobrescribir el trabajo local.

```powershell
git status -sb
git rev-parse HEAD
python --version
python tools/installation_smoke.py
python -m unittest discover -s tests -p test_installation_smoke.py -v
```

Salida esperada: statusPASS, recovery_verified=true,
corruption_rejected=true, market_data_used=false, orders_sent=0.
El reporte muestra commit, hashes de fuentes y si esos tres archivos
tienen cambios sin registrar. Un SHA de HEAD no certifica por sí solo
los bytes del árbol de trabajo. No incluir tokens ni credenciales en reportes.

## Qué hace la prueba de recuperación

En una carpeta temporal nueva crea16 pares de retornos sintéticos y un
informe neto con costo ilustrativo0,002 por período. Fija explícitamente
exposición bruta1 y máximo0,25; no hereda el default0,40 del módulo antiguo.
No calcula stops, liquidez o límites diarios: no valida el marco de riesgo
completo ni simula una estrategia financiera aprobada.

Manifiesto SHA256 de CSV e informe mediante lineage_kronnos. Se copia a
otra carpeta nueva, verifica integridad y coincide el informe byte por byte.
Después altera solo la copia temporal restaurada y exige rechazo.
También hay pruebas de archivo ausente, JSON inválido, ruta no permitida y
destino existente. La prueba no borra ni restaura archivos del proyecto.
Un hash prueba integridad local, no custodia externa ni ausencia de manipulación
previa a la creación del manifiesto.

## Recuperación del código tras pérdida de la instalación

Conservar fuera de la PC el identificador del commit aprobado y la URL
del repositorio. Restaurar en una carpeta NUEVA y comprobar el SHA antes
de ejecutar el smoke; la descarga del código usa GitHub, mientras que la
prueba técnica no necesita red. No usar `git reset --hard` sobre la copia dañada.

```powershell
git clone https://github.com/Kronnos2006/xauusd-ema-atr-bot.git KRONNOS-recuperado
cd KRONNOS-recuperado
git switch --detach SHA_APROBADO
git rev-parse HEAD
python tools/installation_smoke.py
```

Reemplazar SHA_APROBADO por el commit real revisado que incluya el smoke;
la guía no inventa un SHA de entrega antes de la integración. Una copia
Git recupera lo versionado, no archivos locales ignorados, credenciales,
modelos descargados, tareasWindows ni datos no publicados. No abrir holdouts.
No se ha ejecutado aquí una recuperación destructiva de la PC o datos reales.

## Permisos y fallas

Smoke: lectura de tres fuentes y metadatos Git, escritura solo en el
directorio temporal del proceso. No necesita tokens, claves ni privilegios
de administrador. CI usa contents:read y checkout sin credenciales persistentes.
Si falla, conservar la salida y verificar versiónPython/Git y commit;
no relanzar KT002, cambiar sus registros o activar modelos para arreglarlo.

## Acta y pendientes de entrega

La comprobación sintética cubre instalación del núcleo técnico y recuperación
de un informe de prueba. No reemplaza el ensayo completo del producto
integrado, la recuperación operacional de sus servicios, evaluación prospectiva,
auditoría global, custodia ni aceptación del dueño. F8.2/F8.3/F8.4 siguen
pendientes hasta evidencia y decisión para el alcance completo. La guía aporta
inventario, dependencias, permisos y comandos para revisar F8.1; no acredita
casillas automáticamente. Mantener la meta de los ocho frentes abierta.
