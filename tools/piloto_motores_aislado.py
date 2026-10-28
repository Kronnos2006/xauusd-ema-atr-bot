#!/usr/bin/env python3
"""Piloto determinista de contrato: NO ejecuta LEAN ni NautilusTrader."""
import argparse
import hashlib
import json
from pathlib import Path
from comparador_motores import compare

def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(",",":")).encode()

def sha(data):
    return hashlib.sha256(canonical(data)).hexdigest()

def run():
    # Datos ficticios deliberados, separados de precios reales y de backtests.
    prices=[100.0,101.0,99.0,102.0]
    config={"strategy":"buy_hold_fixture_only","fee_rate_per_side":0.001,"position":1}
    sample={"prices":prices,"source":"SYNTHETIC_NOT_MARKET_DATA"}
    # Una compra al inicio y una venta al final, con costo explícito de ambos lados.
    buy=prices[0]*(1+config["fee_rate_per_side"])
    sell=prices[-1]*(1-config["fee_rate_per_side"])
    net_return=sell/buy-1
    equity=[(p*(1-config["fee_rate_per_side"]))/buy for p in prices]
    peak=equity[0]
    max_dd=0.0
    for x in equity:
        peak=max(peak,x)
        max_dd=min(max_dd,x/peak-1)
    shared={"dataset_sha256":sha(sample),"config_sha256":sha(config),"sample_id":"synthetic-contract-1","fees_model":"two-sided-0.1pct"}
    left={**shared,"net_return":net_return,"max_drawdown":max_dd,"trades":1}
    right={**shared,"net_return":net_return,"max_drawdown":max_dd,"trades":1}
    return {"status":"CONTRACT_ONLY","data":"SYNTHETIC","engine_a":"LOCAL_REFERENCE",
            "engine_b":"LOCAL_REFERENCE_CLONE_NOT_EXTERNAL",
            "comparison":compare(left,right),"operacion_real":"NO_AUTORIZADA"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="artifacts/piloto-contrato-motores.json")
    a=p.parse_args()
    result=run()
    out=Path(a.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result))
