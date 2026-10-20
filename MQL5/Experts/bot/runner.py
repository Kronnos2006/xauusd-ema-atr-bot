"""
Lazo principal: feed -> estrategia -> maquina de estados -> broker.

Combinaciones utiles:
  --feed synthetic --broker paper   ofline, para desarrollar
  --feed mt5       --broker paper   PRECIOS REALES, ordenes simuladas.
                                    Es el arnes de paper trading (paso 11).
  --feed mt5       --broker mt5     ejecuta de verdad. Solo cuenta demo.

Por defecto el broker es paper. Hay que pedir explicitamente el real.
"""
import argparse
import csv
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from contracts import Direction
from feeds.replay import CsvFeed, SyntheticFeed
from signals.registry import REGISTRY, build
from risk import RiskConfig, RiskManager
from state import Action, PositionManager

CAMPOS = ["ts_bot", "ts_vela", "symbol", "timeframe", "close", "strategy",
          "direction", "reason", "accion", "detalle", "pos_antes",
          "pos_despues", "volumen", "sl", "tp", "riesgo", "motivo_riesgo"]


def armar_feed(a):
    if a.feed == "synthetic":
        return SyntheticFeed(symbol=a.symbol, timeframe=a.timeframe,
                             n=a.bars, window=a.window, seed=a.seed)
    if a.feed == "csv":
        if not a.path:
            sys.exit("--feed csv necesita --path")
        return CsvFeed(a.path, symbol=a.symbol, timeframe=a.timeframe,
                       window=a.window)
    if a.feed == "mt5":
        from feeds.mt5 import Mt5Feed
        return Mt5Feed(symbol=a.symbol, timeframe=a.timeframe, window=a.window)
    sys.exit(f"feed desconocido: {a.feed}")


def armar_broker(a):
    if a.broker == "paper":
        from broker.paper import PaperBroker
        return PaperBroker()
    if a.broker == "mt5":
        from broker.mt5 import Mt5Broker
        return Mt5Broker()
    sys.exit(f"broker desconocido: {a.broker}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--strategy", default="dummy-dayofweek", choices=sorted(REGISTRY))
    p.add_argument("--feed", default="synthetic", choices=["synthetic", "csv", "mt5"])
    p.add_argument("--broker", default="paper", choices=["paper", "mt5"])
    p.add_argument("--path")
    p.add_argument("--symbol", default="XAUUSD")
    p.add_argument("--timeframe", default="M15")
    p.add_argument("--window", type=int, default=100)
    p.add_argument("--bars", type=int, default=400)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--volume", type=float, default=0.01,
                   help="solo se usa con --sin-riesgo")
    p.add_argument("--riesgo", type=float, default=0.005,
                   help="fraccion del balance por operacion (0.005 = 0.5%%)")
    p.add_argument("--atr-periodo", type=int, default=14)
    p.add_argument("--atr-stop", type=float, default=2.0,
                   help="multiplo de ATR para el stop")
    p.add_argument("--ratio-tp", type=float, default=0.0,
                   help="take profit como multiplo del stop; 0 = sin TP")
    p.add_argument("--perdida-diaria", type=float, default=0.02,
                   help="fraccion del balance que apaga el bot")
    p.add_argument("--vol-max", type=float, default=1.0)
    p.add_argument("--sin-riesgo", action="store_true",
                   help="volumen fijo y sin stop. Solo para replay.")
    p.add_argument("--magic", type=int, default=20260905)
    p.add_argument("--no-shorts", action="store_true")
    p.add_argument("--heartbeat", type=int, default=60,
                   help="segundos entre latidos; 0 lo apaga")
    p.add_argument("--log", default="senales.csv")
    a = p.parse_args()

    estrategia = build(a.strategy)
    feed = armar_feed(a)
    brk = armar_broker(a)
    pm = PositionManager(brk, a.symbol, a.volume, a.magic,
                         permitir_shorts=not a.no_shorts)

    rm = None
    if not a.sin_riesgo:
        rm = RiskManager(brk, a.symbol, RiskConfig(
            riesgo_por_operacion=a.riesgo,
            atr_periodo=a.atr_periodo,
            atr_multiplo_stop=a.atr_stop,
            ratio_tp=a.ratio_tp,
            perdida_diaria_max=a.perdida_diaria,
            volumen_max_absoluto=a.vol_max))
        cta = brk.account()
        print(f"  cuenta: balance {cta.balance:.2f} {cta.currency} | "
              f"riesgo {a.riesgo:.2%}/op | stop {a.atr_stop}xATR({a.atr_periodo}) | "
              f"tope diario {a.perdida_diaria:.1%}")
    else:
        print(f"  *** SIN GESTION DE RIESGO: volumen fijo {a.volume}, "
              f"sin stop. Solo replay. ***")

    if a.broker == "mt5":
        print("\n  *** BROKER REAL. Verifica que sea CUENTA DEMO. ***\n")

    print(f"estrategia={estrategia.name}  feed={a.feed}  broker={a.broker}  "
          f"{a.symbol} {a.timeframe}  vol={a.volume}  magic={a.magic}")

    # Reconciliacion de arranque: la unica fuente de verdad es el broker.
    inicial = pm.reconciliar()
    if inicial:
        pos = inicial[0]
        print(f"  reconciliado: posicion {pos.direction.name} abierta "
              f"(ticket {pos.ticket}, {pos.volume} @ {pos.price_open})")
    else:
        print("  reconciliado: sin posiciones propias abiertas")
    print("-" * 70)

    ruta = Path(a.log)
    nuevo = not ruta.exists()
    ultimo_latido = time.monotonic()
    velas = 0

    with ruta.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        if nuevo:
            w.writeheader()
        try:
            for snap in feed.stream():
                if snap is None:
                    # el feed sigue vivo pero no cerro vela nueva
                    if a.heartbeat and time.monotonic() - ultimo_latido >= a.heartbeat:
                        pos = pm.direccion_actual()
                        print(f"  . esperando | {velas} velas | "
                              f"posicion {pos.name} | "
                              f"{datetime.now().strftime('%H:%M:%S')}")
                        ultimo_latido = time.monotonic()
                    continue
                velas += 1
                # el broker de papel sigue el precio del feed
                if hasattr(brk, "set_price"):
                    brk.set_price(snap.last.close)
                antes = pm.direccion_actual()
                sig = estrategia(snap)

                orden = None
                if rm is not None:
                    orden = rm.dimensionar(sig.direction, snap.candles, a.magic)

                dec = pm.procesar(sig.direction, orden)
                despues = pm.direccion_actual()

                if rm is not None and rm.apagado:
                    print(f"\n  *** BOT APAGADO: {rm.razon_apagado} ***")
                    break

                w.writerow({
                    "ts_bot": datetime.now(timezone.utc).isoformat(),
                    "ts_vela": snap.last.time.isoformat(),
                    "symbol": snap.symbol, "timeframe": snap.timeframe,
                    "close": snap.last.close, "strategy": estrategia.name,
                    "direction": int(sig.direction), "reason": sig.reason,
                    "accion": dec.action.name, "detalle": dec.reason,
                    "pos_antes": antes.name, "pos_despues": despues.name,
                    "volumen": orden.volume if orden else a.volume,
                    "sl": orden.sl if orden else 0.0,
                    "tp": orden.tp if orden else 0.0,
                    "riesgo": round(orden.riesgo_dinero, 2) if orden else "",
                    "motivo_riesgo": orden.motivo if orden else "",
                })
                fh.flush()

                if dec.action is not Action.NADA:
                    marca = " [FALLO]" if "FALLO" in dec.reason else ""
                    extra = ""
                    if orden and orden.volume > 0:
                        extra = (f"  vol {orden.volume} sl {orden.sl} "
                                 f"riesgo {orden.riesgo_dinero:.2f}")
                    print(f"{snap.last.time:%Y-%m-%d %H:%M}  "
                          f"{dec.action.name:<11} {despues.name:<5} "
                          f"@ {snap.last.close:9.2f}  ({sig.reason}){extra}{marca}")
                    ultimo_latido = time.monotonic()

                if a.heartbeat and time.monotonic() - ultimo_latido >= a.heartbeat:
                    print(f"  . vivo | {velas} velas | ultima "
                          f"{snap.last.time:%H:%M} @ {snap.last.close:.2f} | "
                          f"posicion {despues.name}")
                    ultimo_latido = time.monotonic()

        except KeyboardInterrupt:
            print("\n  interrumpido por el usuario")

    final = pm.direccion_actual()
    print("-" * 70)
    print(f"  velas procesadas: {velas}")
    print(f"  posicion al salir: {final.name}"
          + ("   <-- queda ABIERTA en el broker" if final is not Direction.FLAT else ""))
    print(f"  log -> {ruta}")


if __name__ == "__main__":
    main()
