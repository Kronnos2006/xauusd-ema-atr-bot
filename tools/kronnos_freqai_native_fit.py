#!/usr/bin/env python3
"""Kronnos: invoca fit() del modelo nativo de FreqAI con datos SINTÉTICOS.
No equivale a pipeline completo, ni backtest, ni predicción prospectiva.
"""
import argparse,csv,json,math
from types import SimpleNamespace
import numpy as np
import pandas as pd
from freqtrade.freqai.prediction_models.LightGBMRegressor import LightGBMRegressor

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--historical-csv")
    a=parser.parse_args()
    x=[];y=[]
    if a.historical_csv:
        with open(a.historical_csv,newline="") as f:
            rows=list(csv.DictReader(f))
        if len(rows)<500:raise ValueError("Datos insuficientes")
        closes=[float(r["close"]) for r in rows]
        volumes=[float(r["volume"]) for r in rows]
        times=[int(r["time_open_ms"]) for r in rows]
        if any(not math.isfinite(v) or v<=0 for v in closes) or times!=sorted(set(times)):
            raise ValueError("Serie invalida")
        for i in range(5,len(rows)-1):
            x.append([closes[i]/closes[i-1]-1,closes[i-1]/closes[i-2]-1,math.log1p(volumes[i])])
            y.append(closes[i+1]/closes[i]-1)
    else:
        for i in range(180):
            ret=math.sin(i*.17)*.01
            x.append([math.sin(i*.13),math.cos(i*.07),ret])
            y.append(math.sin((i+1)*.17)*.01)
    X=pd.DataFrame(x,columns=["%-sin","%-cos","%-return"])
    Y=pd.DataFrame({"&-next_ret":y})
    split=int(len(x)*0.7)
    dd={"train_features":X.iloc[:split],"train_labels":Y.iloc[:split],
        "train_weights":np.ones(split),
        "test_features":X.iloc[split:],"test_labels":Y.iloc[split:],
        "test_weights":np.ones(len(X)-split)}
    obj=object.__new__(LightGBMRegressor)
    obj.freqai_info={"data_split_parameters":{"test_size":0},"activate_tensorboard":False}
    obj.model_training_parameters={"n_estimators":15,"n_jobs":1,"verbosity":-1}
    obj.get_init_model=lambda pair:None
    dk=SimpleNamespace(pair="BTC/USDT",data_path="/tmp")
    model=obj.fit(dd,dk)
    predictions=model.predict(X.iloc[split:])
    if len(predictions)!=len(X)-split or not np.isfinite(predictions).all():
        raise RuntimeError("Inferencia FreqAI inválida")
    hits=sum((p>0)==(actual>0) for p,actual in zip(predictions,y[split:]))
    print(json.dumps({"project":"Kronnos","engine":"FreqAI.LightGBMRegressor.fit",
        "freqai_model_fit_executed":True,"freqai_model_predict_executed":True,
        "freqai_full_pipeline_executed":False,"dataset":"BINANCE_SPOT_HISTORICAL" if a.historical_csv else "SYNTHETIC",
        "n_train":split,"n_test":len(predictions),"directional_hits_exploratory":int(hits),"always_up_hits":int(sum(t>0 for t in y[split:])),
        "edge_demonstrated":False,"promotion_permitted":False,"trading_real":False}))
if __name__=="__main__":main()
