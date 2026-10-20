# Bot con senal enchufable — pasos 4, 5, 6, 8 y 10

Bot con la senal, el broker y el estado desacoplados entre si.
Incluye maquina de estados con reconciliacion (paso 8) y heartbeat (paso 10).

**Combinaciones**

    --feed synthetic --broker paper   offline, para desarrollar
    --feed mt5       --broker paper   PRECIOS REALES, ordenes simuladas  <- paso 11
    --feed mt5       --broker mt5     ejecuta de verdad. Solo cuenta demo.

El broker por defecto es `paper`. El real hay que pedirlo explicitamente.

Sin dependencias externas. Python 3.9+.

## Correr

    python3 tests/test_contracts_signals.py
    python3 tests/test_state.py
    python3 runner.py --strategy dummy-dayofweek --feed synthetic
    python3 runner.py --strategy dummy-flat --feed synthetic     # control negativo
    python3 runner.py --strategy dummy-alternating --feed csv --path datos.csv

En Windows con MT5 instalado:

    python3 runner.py --strategy dummy-dayofweek --feed mt5 --symbol XAUUSD

## Que garantiza el diseno

| Garantia | Donde se hace cumplir |
|---|---|
| La estrategia nunca ve una vela en formacion | `Snapshot.__post_init__` |
| La estrategia solo devuelve direccion | `Signal` no tiene otros campos |
| Sin velas suficientes devuelve FLAT, no falla | `Strategy.__call__` |
| Velas imposibles se rechazan al construirlas | `Candle.__post_init__` |
| Cambiar de estrategia = una linea de config | `signals/registry.py` |
| El bot corre sin bróker ni MT5 | `feeds/replay.py` |

El descarte de la vela viva esta en `feeds/mt5.py`: `copy_rates_from_pos`
devuelve la vela en formacion como ultima, y se tira. Es la causa numero
uno de backtests que no se replican en vivo.

## Agregar una estrategia real

1. Subclase de `Strategy` en `signals/`, con `lookback` y `_evaluate`.
2. Sumala al dict de `signals/registry.py`.
3. Nada mas del bot se entera de que existe.

## Lo que falta (pasos 6 a 12)

- ~~**6** Riesgo~~ HECHO (`risk.py`). Sizing por % del balance derivado
  del ATR, stop obligatorio, tope de perdida diaria que apaga el bot.
- **7** Ejecutor: cada retcode de MT5 tratado, ninguno ignorado.
- ~~**8** Maquina de estados~~ HECHO (`state.py`). Pregunta al broker al
  arrancar, filtra por `magic` para no tocar operaciones tuyas, y traduce
  'direccion deseada' a accion — por eso `dummy-dayofweek` abre UNA vez
  el jueves y no doce.
- **9** Registro: CSV con flush por linea, ya incluye accion y estado
  antes/despues. Falta detalle de fills y slippage.
- ~~**10** Heartbeat~~ HECHO (`--heartbeat N`). Falta la alerta externa
  cuando el proceso muere.
- **11** Semanas en demo, sin tocarlo. Ahi salen slippage, latencia y
  rechazos: los datos que ningun backtest da.
- **12** Recien ahi, una senal real — y solo una que haya pasado el
  haircut y el DSR.

## Advertencia

Las senales dummy no tienen edge a proposito. `dummy-alternating` pierde
exactamente el costo de transaccion por operacion. No conectar a capital.


## Lo que garantiza la maquina de estados

| Garantia | Test |
|---|---|
| Sobrevive a un reinicio con posicion abierta | `test_sobrevive_a_reinicio` |
| No reentra con la misma senal repetida | `test_no_reentra_con_la_misma_senal` |
| No toca operaciones abiertas a mano (otro magic) | `test_ignora_posiciones_ajenas` |
| Detecta dos posiciones simultaneas y para | `test_detecta_estado_imposible` |
| Un rechazo del broker no se silencia | `test_falla_de_apertura_no_miente` |
| Con el broker caido no reporta estado inventado | `test_desconexion_no_se_silencia` |

El estado vive en el BROKER, nunca en un archivo del bot. `reconciliar()`
se llama al arrancar y antes de cada decision.


## Gestion de riesgo (`risk.py`)

    --riesgo 0.005          fraccion del balance por operacion
    --atr-stop 2.0          stop = 2 x ATR
    --atr-periodo 14
    --ratio-tp 0            take profit como multiplo del stop; 0 = sin TP
    --perdida-diaria 0.02   apaga el bot al 2% de perdida diaria
    --vol-max 1.0           tope duro de volumen
    --sin-riesgo            volumen fijo, sin stop. SOLO replay.

Tres reglas, ninguna decidida por la estrategia:

1. **Cuanto** — % fijo del balance, derivado del stop. Nunca lote fijo:
   un lote fijo arriesga el doble cuando la volatilidad se duplica.
   El volumen se redondea **hacia abajo**, nunca al mas cercano: redondear
   al mas cercano hace que la mitad de las operaciones excedan el
   presupuesto de riesgo.
2. **Donde** — stop obligatorio a N x ATR. Sin stop no se abre.
3. **Cuando parar** — tope de perdida diaria. Una vez apagado NO se
   re-arma solo aunque el PnL mejore: lo reinicia una persona.

Si la cuenta es demasiado chica para que el volumen llegue al minimo del
broker, devuelve 0 y no opera. No redondea para arriba.

| Garantia | Test |
|---|---|
| El riesgo en dinero respeta el % configurado | `test_riesgo_en_dinero_respeta_el_porcentaje` |
| Mas volatilidad -> menos volumen | `test_mas_volatilidad_menos_volumen` |
| Stop siempre del lado correcto | `test_stop_obligatorio_y_del_lado_correcto` |
| Cuenta chica no opera en vez de sobre-arriesgar | `test_cuenta_chica_no_opera` |
| El tope diario apaga el bot | `test_tope_diario_apaga` |
| Apagado no se re-arma solo | `test_apagado_no_se_rearma_solo` |
| Config absurda se rechaza al construirse | `test_config_rechaza_riesgo_absurdo` |
