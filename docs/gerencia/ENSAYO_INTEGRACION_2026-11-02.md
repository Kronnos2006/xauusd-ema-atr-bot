# Ensayo conjunto de integración, 2 de noviembre de 2026

Se integraron en un worktree local los PR #97, #99, #100, #101, #102 y #103, en ese orden. Base origin/master a76e664c387095a5dfd7d4708bc27de4d7932a2e. Resultado local 79f142bce65b884b5557e5365d5b69306441e7af, conservado en la rama local ensayo/integracion-20261102.

El primer PR se aplicó limpio. Los siguientes cinco entraron en conflicto únicamente en ESTADO.md. Se conservaron las entradas manuales de ambos lados y la sección automática del master de partida. El diff resultante contiene 28 archivos y conserva data/, tools/kt002_prospectivo.py y .github/workflows/kt002.yml.

| Verificación en el árbol combinado | Resultado |
|---|---:|
| Guardia, entradas adversariales y publicación | 37 pruebas aprobadas |
| Centro de Control y entrega ORION | 13 pruebas aprobadas |
| Riskfolio real | 12 pruebas aprobadas |
| Recuperación técnica, permisos y cálculo de avance | 12 pruebas aprobadas |
| Alertas del panel | 17 comprobaciones aprobadas |
| Navegación en viewports 360, 390 y 1280 | 15 vistas aprobadas |
| Restauración sintética | 16 observaciones, restauración verificada, corrupción rechazada, cero órdenes |

La verificación del panel usó API 503 simulada en Playwright y servidor local. La restauración técnica utilizó datos sintéticos. El ensayo se ejecutó en Windows. Los PR conservan sus respectivas comprobaciones remotas en GitHub.

Para integrar, verificar que los SHA de los PR coincidan con los probados y repetir el ensayo sobre master vigente. Si cambió la bitácora, conservar las entradas manuales concurrentes y la sección automática del master actual. Este resultado local queda listo para revisión del dueño. Las casillas del tablero se actualizan cuando se acepten los hitos y se integren los cambios correspondientes.

## Recuperación desde un clon limpio

Se clonó el repositorio local con git clone --no-checkout --no-local en una carpeta nueva. Se seleccionaron solo el smoke, sus dos módulos, las pruebas y la guía mediante sparse-checkout y se fijó HEAD en 79f142bce65b884b5557e5365d5b69306441e7af. El origen de este clon fue la rama local de ensayo. La disponibilidad de ese commit como respaldo remoto queda pendiente de integración.

Se creó un entorno virtual nuevo con Python 3.13.5 y --without-pip. Los comandos python -E -s tools/installation_smoke.py y python -E -s -m unittest discover -s tests -p test_installation_smoke.py -v pasaron con un árbol limpio. El smoke verificó la restauración de 16 observaciones sintéticas, rechazó corrupción y reportó cero órdenes. Las cuatro pruebas de restauración aprobaron.

En el primer intento usé python -I con el script directo. Ese modo excluye la carpeta del script de la ruta de importación y causó ModuleNotFoundError. La forma documentada funciona. En esta prueba se usó -E -s para ignorar las variables PYTHON y el directorio de paquetes del usuario mientras se conserva la resolución de módulos locales.

La evidencia cubre recuperación del código fijado y ejecución de sus comprobaciones sintéticas en un entorno nuevo. La recuperación de servicios operativos, la aceptación del dueño y el acta final siguen pendientes.

## Reversión de una integración del PR #108

Ensayo local sobre la base a76e664c387095a5dfd7d4708bc27de4d7932a2e y el candidato 79f142bce65b884b5557e5365d5b69306441e7af. Se creó un merge commit con dos padres en ese orden. Su árbol coincidió con el del candidato.

Después se añadió un archivo sintético en un commit posterior independiente. Se ejecutó git revert -m 1 sobre el merge de ensayo. El árbol final coincidió byte por byte con la base para todos los archivos, excepto el archivo sintético, cuyo blob se conservó. El worktree terminó limpio.

- Merge de ensayo: a54f1a9618496520f81dcaf74b42b74a38745f5e.
- Reversión de ensayo: 58bc5acafa8f74bdc65c31f021511a58e146a4cc.
- Blob posterior conservado: 2cc09c680723eccca7a2ca1e51e945bc31f82736.

Si el dueño autoriza integrar y luego se requiere revertir, identificar el merge real y verificar que su primer padre es el master anterior. Preparar git revert -m 1 MERGE_REAL en una rama desde el master vigente, revisar el diff y pasar CI antes de integrar la reversión. Si hubo cambios posteriores sobre las mismas líneas, resolverlos conservando las publicaciones nuevas y detenerse ante un conflicto fuera de alcance. GitHub Pages publicaría otra versión del panel al integrar una reversión que alcance sus rutas vigiladas.

Este ensayo prueba la reversión Git con un cambio posterior independiente. La restauración de servicios en producción y la validación de Pages después del despliegue requieren una integración autorizada.

## Integración autorizada y comprobaciones posteriores

El dueño autorizó #108 con merge commit condicionado a conservar base y SHA, y nueve checks aprobados. Base a76e664 y candidato 79f142b comprobados inmediatamente antes del merge. Los nueve checks del candidato estaban en success. Merge cfff9ee2a2acd714efe6eba14ad01b506f5ceeaa, con padres a76e664 y 79f142b, el 2 de noviembre a las 21:04:38 de Costa Rica.

- Pages 41569990894 terminó success sobre el SHA del merge. Se verificaron en producción la raíz, /orion/ y /visor/. El HTML coincide con sus blobs del merge, health.js coincide entre raíz y alias, y ambos JSON exponen solo lectura y omiten enlaces de oficina y descripciones. Playwright pasó 15 vistas del sitio publicado bajo un fallo de API 503 simulado.
- Primera guardia posterior, 41570303171 a las 21:07:40 de Costa Rica, terminó success. Ejecutó 4c997cf, descendiente del merge con el mismo workflow y lógica de guardia. La revisión de KT-002 reportó accion=ok, edad_registro_min=0 y una corrida en curso. También pasó la verificación de salud contra GitHub.
- El diff del merge en productor, workflow y datos de KT-002 está vacío. El registro posterior de las 21:07 procede de la acumulación habitual.
- La única referencia a Riskfolio en workflows es kronnos-riskfolio-tests.yml. El código se conserva como evaluación aislada.
- Issue #88 conserva 10/32. La autorización del merge no incluye aceptación de hitos. El dueño dejó el piloto FreqAI sin aprobar. PR #98 permanece como propuesta.

Fuentes:
- Merge: https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/108
- Publicación: https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41569990894
- Guardia: https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41570303171
