# Kronos × TimesFM: indice del proyecto

Actualizado 2026-10-19 Costa Rica. Autor Codex; revision independiente Claude pendiente.

## Empezar

- [Panel local: uso, ejecucion y seguimiento](../panel/README.md)
- [Opciones gratuitas y limites](ALOJAMIENTO_GRATUITO.md)
- [Paquete Oracle: instalacion y estado pendiente](../deploy/oracle/README.md)
- [Contexto compartido y decisiones](coordination/CONTEXTO_COMPARTIDO.md)

## Experimentos separados

| ID | Objetivo | Protocolo | Evidencia |
|---|---|---|---|
| KT-001 | Verificar inferencia con datos sinteticos; no evaluar BTC | [Registro tecnico](Kronos_TimesFM_registro.md) | [Salida reproducible](evidencia/KT-001/) |
| KT-002 | Contrastar pronosticos emitidos antes del mercado futuro | [Control prospectivo](KT-002_control_prospectivo.md) | [Instantaneas del panel](evidencia/panel-snapshots/) |

Antecedentes: [preparacion y diagnostico de potencia](Kronos_BTC_preparacion.md), [borrador BTC Fase 0](BTCUSDT_Fase_0_borrador.md). No confundir un pronostico descriptivo con backtest o estrategia validada. Los marcos historicos siguen cerrados; no se reabren por publicar este trabajo.

## Organizacion y ramas

- `master`: historial previo del proyecto, conservado.
- `codex/kronos-timesfm-panel-control`: panel, KT-001/KT-002, pruebas, evidencia y guia de almacenamiento gratuito. No se fusiona automaticamente con master.
- `codex/oracle-always-free`: adaptacion portable y paquete para la futura VM. No significa que exista despliegue.
- `panel/`: servidor, control prospectivo, interfaz `dist/`, tests y capturas.
- `tools/`: ejecutores de inferencia y exportador de instantaneas.
- `docs/evidencia/KT-001/`: salida sintetica inicial.
- `docs/evidencia/panel-snapshots/<UTC>/`: copia por fecha de registros reales y corridas del panel, con manifiesto SHA256.
- `panel/market-records/` y `panel/runtime/`: estado activo local ignorado por Git; las copias se publican bajo evidencia. Los nuevos cierres no se suben solos.
- `tools/kronos-cache/`, `kronos-env/` y clones upstream: pesos, entorno y dependencias descargadas; no se duplican en GitHub. Revisiones de pesos y hashes quedan en la evidencia; procedencia de codigo en los registros. `docs/evidencia/KT-001/requirements-resolved.txt` conserva las dependencias y revision Git de TimesFM; snapshots de pip freeze pueden contener la ruta original de instalacion, solo para auditoria.

## Respaldar y recuperar

```powershell
python tools/export_panel_snapshot.py
```

El exportador verifica las huellas existentes y copia los archivos a una carpeta nueva, sin tocar los originales ni consultar mercado. Para subir una nueva copia: revisar `git status`, agregar su carpeta, crear commit y hacer push a la rama de trabajo. No sube nada automaticamente. No ejecutar esto para modificar predicciones previas.

Para recuperar: elegir una instantanea, verificar SHA256 y bytes contra su `manifest.json`, copiar sus subcarpetas `market-records` y `runtime` a `panel/` con el servidor detenido y sin sobrescribir un registro mas reciente; reinstalar dependencias/modelos por sus revisiones fijadas y arrancar `python panel/server.py`. No copiar datos de una instantanea sobre otro registro existente sin conciliar primero IDs/evaluaciones. Las instantaneas antiguas pueden conservar horizontes pendientes; no certifican el estado actual del mercado.

La copia en GitHub conserva solo lo capturado y publicado. Un servidor gratuito tampoco sustituye una segunda copia independiente de los registros. Ninguna nube desplegada por esta tarea.
