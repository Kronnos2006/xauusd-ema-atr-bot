# Revisor de PR sin IA

Revisa un PR con reglas fijas y da **PASA / NO PASA**. Hace 0 llamadas a IA,
así que no gasta tokens. La IA solo se usa cuando el informe muestra algo raro.

## Qué revisa

| Tipo | Ejemplo en `reglas_kronnos.json` |
|---|---|
| Rutas prohibidas | KT-002, `.github/workflows/`, `data/`, holdouts |
| Rutas permitidas | Solo `MQL5/Experts/bot/` |
| Debe contener | `ACCOUNT_TRADE_MODE_DEMO` y `raise PermissionError` en el adaptador MT5 |
| No debe contener | Anulaciones del tipo `forzar_real`, `skip_demo`, `override` |
| Envíos directos MT5 | Una sola llamada directa a `order_send` entre los archivos Python versionados. Debe estar en el adaptador |
| Pruebas | Cuatro scripts del bot, incluido `test_mt5_broker.py` del PR #118 |

Los avisos (por ejemplo, demasiados archivos) se muestran, pero no bloquean.

## Uso

```bash
# Traer el PR sin cambiar de rama
git -C RUTA_REPO fetch origin pull/118/head:pr118

python3 revisor_pr.py --repo RUTA_REPO --base origin/master --head pr118 \
    --reglas reglas_kronnos.json --salida informe.md
```

El código de salida es `0` si pasa, `1` si falla y `2` si hay un error de uso. `--sin-pruebas` omite los comandos de prueba.

El revisor lee el head con `git show` y corre las pruebas en un worktree temporal.
Usá `--aislar-pruebas` para ejecutar los tests en Docker. Sin esa opción, los
comandos se ejecutan en tu equipo con tus permisos. Reservá ese modo para código
que ya hayas revisado.

## Adaptarlo

Todo se cambia en el JSON, sin tocar el código:

- **Nuevo PR con otro alcance:** edita `rutas_permitidas`.
- **Nueva garantía de seguridad:** agrega un bloque en `invariantes`. Por
  ejemplo, para el bloqueo acumulado de 5 dólares, exige que `risk.py` contenga
  el nombre del archivo de estado persistente.
- **Nuevas pruebas:** agrega una entrada en `pruebas`.
- **Otro repo:** copia el JSON con otro nombre y pasa ese con `--reglas`.

## Automatizarlo en GitHub

`.github/workflows/revisor-pr.yml` revisa los PR contra `master` que toquen
el bot. Usa el script y las reglas del SHA base del evento, desactiva la
persistencia de credenciales de Git y escribe el resultado en el resumen del
job. Las pruebas del PR se ejecutan en Docker, sin red, con el directorio del
bot en solo lectura y sin pasar secretos ni credenciales del host. El resumen
publica los códigos de salida de las pruebas.

Integrá primero el PR #118 para que las pruebas de MT5 estén disponibles en los
PR nuevos del bot. Este workflow entra en uso al integrar su propio PR.

## Pruebas del revisor

```bash
python3 -m unittest test_revisor_pr
```

Usa un repo git sintético: comprueba que pasa un cambio limpio y que falla con
una ruta prohibida, con un archivo fuera de alcance, si se quita el control demo,
con una anulación, con un segundo `order_send` y con una prueba roja.

## Límites

- Las reglas de texto detectan cambios en patrones conocidos. Las pruebas
  verifican el comportamiento del bloqueo demo.
- El conteo usa el AST de Python para llamadas directas. Los alias y llamadas
  dinámicas quedan fuera del conteo.
- Un informe PASA no aprueba el PR. Integra el dueño.
