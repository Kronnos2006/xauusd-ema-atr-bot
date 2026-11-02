# ATLAS: evidencia original recuperada de GitHub

Autor Codex, consulta 2026-11-01 Costa Rica. Lectura y verificación local;
sin ejecutar ni relanzar workflows, alterar experimentos o abrir holdouts.
El propietario indicó que el trabajo compartido se conserva en GitHub.

## Hallazgo confirmado

Claude había creado la rama research/atlas-bloqueo-a-custodia-20261027,
commit 9b39ff94437655773efdaf39c4dcc714340cf100, con censo de 74 entradas,
ancla, fuentes Git y workflow atlas-custodia.yml. No está en master.

La ejecución original **40507359902**, evento push del 27-oct, terminó
SUCCESS y conserva el artifact **12734829078**, no expirado al consultar.
La ejecución ATLAS CI **40507386454** también terminó SUCCESS.

- Corrida original: https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/40507359902
- Commit: https://github.com/Kronnos2006/xauusd-ema-atr-bot/commit/9b39ff94437655773efdaf39c4dcc714340cf100
- Artifact: sello-censo-9b39ff94437655773efdaf39c4dcc714340cf100
- Retención declarada del artifact: 90 días; no equivale a Object Lock.

Descargado el artifact existente, sin solicitar sellos nuevos. Incluye
MANIFIESTO.sha256, manifiesto.tsq, freetsa.tsr, digicert.tsr y cadena FreeTSA.

## Verificación realizada

Los tres hashes del manifiesto coinciden con los bytes de los archivos
en el commit original (`git show SHA:ruta`, sin checkout de datos):

| Archivo | SHA-256 |
|---|---|
| censo_intentos.jsonl | 82a94500cd50d9c18e97e7f02322e4c4b3dd23c8dd1c50f226cc25022920ff75 |
| ANCLA_CENSO.json | 00723b10ef2012ca6f76bd7e7a198e71987c3e87cb6025403e78940f633b6c2d |
| fuentes_git.json | e9e3cf8c17a75d017a1297782e8ec2edd5dfa82ed83ad477f4245bf258ff4eb5 |

OpenSSL `ts -verify -data MANIFIESTO.sha256 -in freetsa.tsr` da
**Verification: OK** con la cadena del artifact. Además se descargó por
HTTPS la CA publicada en https://freetsa.org/files/cacert.pem: su huella
SHA-256 coincide con la CA del artifact y la verificación vuelve a dar OK.

Huella CA: A6:37:9E:7C:EC:C0:5F:AA:3C:BF:07:60:13:D7:45:E3:27:BB:BA:A3:8C:0B:9A:F2:24:69:D4:70:1D:18:AA:BC.

Ambas respuestas TSR declaran Granted y genTime **2026-10-27 12:53:34 UTC**.
FreeTSA: firma y vinculación de contenido verificadas como se describe.
DigiCert: solo se inspeccionó respuesta/fecha; su firma y cadena NO se
certifican aquí. No se comprobaron revocación ni política institucional
independiente de selección de raíz. La coincidencia con CA HTTPS actual
no sustituye una política de confianza fijada antes del experimento.

## Qué demuestra y qué sigue pendiente

Demuestra existencia del manifiesto en la fecha externa de FreeTSA y su
vinculación con tres archivos del commit localizado. Es más evidencia que
un sello de prueba autofirmado; no se debe clasificar como inexistente.

No demuestra que existieran antes del sello todos los intentos históricos,
que 74 sea un N exhaustivo o que no haya variantes fuera del repositorio.
El propio README excluye otras carpetas, chats y repos. Primer commit no
equivale a primer experimento ni a disponibilidad punto-en-tiempo de barras.
No valida H3/DSR, folds, costos, procedencia de precios ni ventaja financiera.

Custodio independiente con retención inmutable y certificación global
siguen pendientes según el documento original. Un artifact con retención90d
puede expirar o ser borrado: no se etiqueta custodia WORM. No se abre ni
fusiona PR42, que sigue draft/bloqueado.

Próximo trabajo: revisar completitud del censo entre fuentes autorizadas,
verificar cadena DigiCert con raíz independiente, diseñar retención e
identidades separadas y registrar nuevas pruebas antes de nuevos resultados.
No se reescriben fechas históricas ni se acreditan los cuatro hitos F2.

## Preservación local del artifact original

Copia byte por byte en docs/evidencia/ATLAS-CENSO-20261027/artifact-original.zip;
provenance.json conserva IDs, origen y SHA256. Es respaldo en Git, no WORM ni
autorización de promoción. No contiene URL temporal de descarga ni credenciales.
