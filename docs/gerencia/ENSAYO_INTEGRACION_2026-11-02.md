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
