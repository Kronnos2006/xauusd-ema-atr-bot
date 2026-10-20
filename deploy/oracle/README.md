# Oracle Always Free: paquete de migracion

Estado: preparacion local. No hay cuenta, VM ni despliegue creados por Codex. No apagar el servidor local suponiendo que existe una nube activa. Autor Codex; revision independiente Claude pendiente.

Validacion realizada: nueve tests aislados, sintaxis Bash/JS y smoke sintetico Windows offline con dos hilos (36.04s), evidencia en docs/evidencia/oracle-preparacion/smoke-windows-2hilos.json. Validacion NO realizada: instalacion systemd/Ubuntu y ejecucion real ARM. La cuenta nueva sigue requiriendo accion del usuario.

## Cuenta y maquina

El usuario debe completar su cuenta en https://signup.oraclecloud.com/ (datos, verificacion y condiciones). No enviar claves privadas ni contraseñas al chat. Elegir region principal cuidadosamente: los recursos gratuitos deben estar en esa region.

Solo crear si el resumen de la consola confirma gratuidad dentro del total disponible de la cuenta: Ampere A1 ARM, 2 OCPU/12GB RAM, imagen Ubuntu 24.04 ARM elegible y volumen de arranque 50GB dentro de la cuota. No contratar Pay As You Go ni usar recursos fuera de cuota para sortear falta de capacidad. No prometemos cupo ni disponibilidad ininterrumpida; Oracle puede recuperar instancias ociosas. No agregar carga artificial.

Fuente de cuotas/politicas: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm

Mantener 8765 cerrado a Internet. El servidor conserva bind 127.0.0.1; acceder inicialmente mediante tunel SSH. La configuracion de red/SSH se revisa con IP y cuenta reales antes de crear la VM; no hay puertos publicos nuevos configurados por estos archivos.

## Instalar en la VM (todavia no ejecutado)

Como ubuntu, checkout de esta rama en `~/kronos-project`; si el repo es privado usar la autenticacion normal sin guardar tokens en scripts. Los comandos de abajo asumen ese directorio/home. Prerrequisitos del sistema Ubuntu: git, python3.12, python3.12-venv y libgomp1 (instalar con apt si faltan).

```bash
cd ~/kronos-project
export KRONOS_DATA_DIR="$HOME/kronos-data"
export HF_HOME="$KRONOS_DATA_DIR/huggingface"
bash deploy/oracle/bootstrap.sh
```

El instalador verifica plataforma/RAM/disco, fija los dos upstreams y dependencias, descarga pesos por revision fija y ejecuta KT-001 sintetico. Hay ruedas publicas cp312 aarch64 para torch2.14.1/numpy2.5.4/pandas3.0.6/safetensors0.6.2; esto NO prueba aun la inferencia en una VM ARM. Revisar salida/tiempo/memoria antes de continuar.

El checkout nuevo de TimesFM usa sparse-checkout de src y archivos raiz para excluir las imagenes LFS de ejemplos. Un checkout preexistente modificado provoca aborto; no ignorar cambios de codigo inesperados.

## Migrar datos antes de activar

Copiar el registro actual completo, no solo una instantanea antigua. Validar todas las huellas. Preparar la transferencia mientras el servidor local sigue contrastando; parar solo ese servidor y hacer copia final antes de arrancar la VM, para evitar dos escritores. Los resultados que vencen durante el traslado se consultan al reiniciar; no se reescriben pronosticos.

Destino: `~/kronos-data/market-records` y opcionalmente `~/kronos-data/runtime`. No sustituir registros mas nuevos por copias antiguas. La cache de pesos esta en HF_HOME, fuera del checkout. Probar backup y recuperacion antes de apagar la PC como dependencia del servicio.

## Servicio y autonomia (solo despues de validar)

Copiar `kronos.env.example` a `~/kronos.env`, ajustar rutas. Instalar las tres unidades bajo `~/.config/systemd/user/`. Configurar linger para el usuario de la VM para que no dependa de la sesion SSH. Estos archivos no instalan ni cambian tareas de Windows.

```bash
systemctl --user daemon-reload
systemctl --user enable --now kronos-panel.service kronos-backup.timer
```

Empezar con KRONOS_AUTO_FORECAST=0. Tras validar registro/backup/cierre observado, cambiar a1 y reiniciar servicio permite nuevas emisiones fijas despues de resolver +4h, sin solapamiento; backoff15min ante reintentos. Se mantiene semilla/configuracion, sin reoptimizar. No se ejecuta backtest, trading ni entrenamiento. El monitor de cierres sigue cada60s. Funcionamiento diario 24/7 (incluye las seis jornadas solicitadas); no se impone un dia libre artificial a BTC.

## Consultar y conservar informacion

Desde una computadora con SSH: `ssh -L 8765:127.0.0.1:8765 ubuntu@IP_REAL` y abrir http://127.0.0.1:8765. La VM continua calculando aunque ese tunel y tu PC esten apagados.

El timer crea copias verificadas en `~/kronos-data/backups`. Esas copias siguen en la misma VM: NO constituyen aun respaldo externo. Antes de considerar migracion completa, configurar una segunda copia (GitHub para instantaneas pequeñas u Object Storage dentro de cuota gratuita) y ensayar recuperacion. No copiar HF_HOME ni entornos en los backups de evidencia. No borrar historial para ahorrar espacio automaticamente.

Pendiente: cuenta/capacidad gratuita, VM, instalacion real ARM, smoke, transferencia final, restauracion probada, segunda copia externa y activacion. Ninguno de esos pasos se afirma ejecutado por existir este paquete.
