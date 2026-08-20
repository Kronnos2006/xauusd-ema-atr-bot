"""
Depth-check puntual (no logger productivo) sobre MetaQuotes-Demo para
el basket de 10 simbolos propuesto (FX + ETFs). Mismo criterio de
entrada usado en el chequeo anterior (GLD/SLV/QQQ/SPY/IWM/XAGUSD/USDCNH):
D1 desde 2010 o antes + trade_mode=4 (full) + bid/ask > 0.

Solo lectura: symbol_info / symbol_info_tick / copy_rates_from. No
coloca ni modifica ninguna orden.
"""
import os
import time
from datetime import datetime, timezone

import MetaTrader5 as mt5

SIMBOLOS = [
    "USDJPY", "GBPUSD", "USDCHF", "NZDUSD", "USDCAD",
    "TLT", "GDX", "XLE", "DIA", "EEM",
]

TRADE_MODE_NOMBRE = {
    0: "DISABLED",
    1: "LONGONLY",
    2: "SHORTONLY",
    3: "CLOSEONLY",
    4: "FULL",
}


def fila(simbolo):
    existe = mt5.symbol_select(simbolo, True)
    if not existe:
        return {
            "simbolo": simbolo, "existe": False, "trade_mode": None,
            "d1_barras": None, "d1_primera": None,
            "swap_long": None, "swap_short": None,
            "spread": None, "bid": None, "ask": None,
        }

    info = mt5.symbol_info(simbolo)
    tick = mt5.symbol_info_tick(simbolo)

    rates = None
    for intento in range(5):
        rates = mt5.copy_rates_from_pos(simbolo, mt5.TIMEFRAME_D1, 0, 50000)
        if rates is not None and len(rates) > 0:
            break
        time.sleep(1.0)

    if rates is not None and len(rates) > 0:
        d1_barras = len(rates)
        d1_primera = datetime.fromtimestamp(int(rates[0]["time"]), tz=timezone.utc).strftime("%Y-%m-%d")
    else:
        d1_barras = 0
        d1_primera = None
        print(f"  [diag] {simbolo}: sin barras tras reintentos, last_error={mt5.last_error()}")

    return {
        "simbolo": simbolo,
        "existe": True,
        "trade_mode": info.trade_mode if info else None,
        "d1_barras": d1_barras,
        "d1_primera": d1_primera,
        "swap_long": info.swap_long if info else None,
        "swap_short": info.swap_short if info else None,
        "spread": info.spread if info else None,
        "bid": tick.bid if tick else None,
        "ask": tick.ask if tick else None,
    }


def pasa_criterio(f):
    if not f["existe"] or f["trade_mode"] != 4:
        return False
    if not f["d1_primera"]:
        return False
    if f["d1_primera"] > "2010-12-31":
        return False
    if not (f["bid"] and f["ask"] and f["bid"] > 0 and f["ask"] > 0):
        return False
    return True


def main():
    ok = mt5.initialize(path=r"C:\Program Files\MetaTrader 5\terminal64.exe")
    if not ok:
        print(f"FALLO conectar: {mt5.last_error()}")
        return

    acc = mt5.account_info()
    print(f"Cuenta: {acc.login if acc else '?'} | Server: {acc.server if acc else '?'}\n")

    filas = [fila(s) for s in SIMBOLOS]

    header = f"{'Simbolo':<8} {'Existe':<7} {'TradeMode':<11} {'D1 barras':<10} {'D1 primera':<12} {'SwapL':<9} {'SwapS':<9} {'Spread':<8} {'Bid':<10} {'Ask':<10}"
    print(header)
    print("-" * len(header))
    for f in filas:
        print(
            f"{f['simbolo']:<8} "
            f"{'SI' if f['existe'] else 'NO':<7} "
            f"{(str(f['trade_mode']) + ' ' + TRADE_MODE_NOMBRE.get(f['trade_mode'], '?')) if f['trade_mode'] is not None else 'N/A':<11} "
            f"{f['d1_barras'] if f['d1_barras'] is not None else 'N/A':<10} "
            f"{f['d1_primera'] or 'N/A':<12} "
            f"{f['swap_long'] if f['swap_long'] is not None else 'N/A':<9} "
            f"{f['swap_short'] if f['swap_short'] is not None else 'N/A':<9} "
            f"{f['spread'] if f['spread'] is not None else 'N/A':<8} "
            f"{f['bid'] if f['bid'] is not None else 'N/A':<10} "
            f"{f['ask'] if f['ask'] is not None else 'N/A':<10}"
        )

    print("\nPasan los 3 criterios (D1<=2010, trade_mode=4, bid/ask>0):")
    aprobados = [f["simbolo"] for f in filas if pasa_criterio(f)]
    rechazados = [f["simbolo"] for f in filas if not pasa_criterio(f)]
    print("  APRUEBAN:", ", ".join(aprobados) if aprobados else "(ninguno)")
    print("  RECHAZAN:", ", ".join(rechazados) if rechazados else "(ninguno)")

    mt5.shutdown()


if __name__ == "__main__":
    main()
