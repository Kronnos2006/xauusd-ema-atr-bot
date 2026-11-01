#!/usr/bin/env python3
"""EWMA causal para volatilidad (solo investigación, sin órdenes ni holdouts).
El pronóstico de t+1 usa exclusivamente rendimientos observados hasta t.
"""
import argparse
import csv
import math
from pathlib import Path

def forecasts(returns, decay=0.94, warmup=30):
    if not 0 < decay < 1:
        raise ValueError("decay fuera de (0,1)")
    if warmup < 2 or len(returns) <= warmup:
        raise ValueError("muestra insuficiente")
    if any(not math.isfinite(x) for x in returns):
        raise ValueError("retornos no finitos")
    variance = sum(x*x for x in returns[:warmup]) / warmup
    results = []
    for t in range(warmup, len(returns)):
        # Pronóstico evaluado contra r[t], no incluye r[t] en el cálculo.
        results.append((t, variance, returns[t] ** 2))
        variance = decay*variance + (1-decay)*returns[t]**2
    return results

def compare(returns, decay=0.94, warmup=30, window=30):
    if window < 2 or warmup < window:
        raise ValueError("ventana inválida")
    estimates = forecasts(returns, decay, warmup)
    ewma_loss = sum((pred-actual)**2 for _, pred, actual in estimates)/len(estimates)
    historical_loss = sum((sum(x*x for x in returns[t-window:t])/window-actual)**2
                          for t, _, actual in estimates)/len(estimates)
    return {"observaciones":len(estimates), "mse_ewma":ewma_loss,
            "mse_historica":historical_loss, "mejora_mse": historical_loss-ewma_loss}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",required=True,help="CSV autorizado con columna retorno decimal, orden cronológico")
    p.add_argument("--lambda",dest="decay",type=float,default=0.94)
    p.add_argument("--warmup",type=int,default=30)
    p.add_argument("--window",type=int,default=30)
    args=p.parse_args()
    with Path(args.csv).open(newline="",encoding="utf-8") as f:
        values=[float(row["retorno"]) for row in csv.DictReader(f)]
    print(compare(values,args.decay,args.warmup,args.window))

if __name__=="__main__":
    main()
