#!/usr/bin/env python3
"""Kronnos: entrenamiento de regresión Ridge en Python aislado; NO es FreqAI nativo.
Solo datos CSV aportados; sin órdenes. No equivale a pipeline FreqAI nativo.
"""
import argparse,csv,hashlib,json,math
from pathlib import Path
def train(input_path):
    from sklearn.linear_model import Ridge
    import sklearn
    rows=list(csv.DictReader(input_path.open(newline="")))
    if len(rows)<80: raise ValueError("Se requieren >=80 velas cerradas")
    series=[];last=-1
    for r in rows:
        t=int(r["time_open_ms"]);end=int(r["time_close_ms"])
        op,hi,lo,cl,vol=(float(r[k]) for k in ("open","high","low","close","volume"))
        if not all(math.isfinite(x) for x in (op,hi,lo,cl,vol)):raise ValueError("No finito")
        if not(last<t<end and 0<lo<=min(op,cl)<=max(op,cl)<=hi and vol>=0):
            raise ValueError("Barras inválidas")
        last=t;series.append((cl,vol))
    x=[];y=[]
    for i in range(5,len(series)-1):
        # Solo información disponible al cierre de i; objetivo es retorno de i a i+1
        features=[(series[i-j][0]/series[i-j-1][0]-1) for j in range(4)]
        features.append(math.log1p(series[i][1]))
        x.append(features)
        y.append(series[i+1][0]/series[i][0]-1)
    split=int(len(x)*0.7)
    if split<40 or len(x)-split<15:raise ValueError("Fold insuficiente")
    model=Ridge(alpha=1.0)
    model.fit(x[:split],y[:split])
    predicted=model.predict(x[split:]).tolist()
    truths=y[split:]
    hits=sum((p>0)==(t>0) for p,t in zip(predicted,truths))
    baseline=sum(t>0 for t in truths)
    return {"project":"Kronnos","engine":"sklearn_Ridge_isolated_python",
        "sklearn_version":sklearn.__version__,"n_train":split,
        "n_test":len(truths),"directional_hits":hits,"always_up_hits":baseline,
        "directional_accuracy":hits/len(truths),"always_up_accuracy":baseline/len(truths),
        "source_sha256":hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "data_source_provenance":"INPUT_NOT_AUTHENTICATED",
        "freqai_native_pipeline_executed":False,"real_model_fit_executed":True,
        "training_data_synthetic":True,"external_holdout_verified":False,
        "statistical_edge_demonstrated":False,"promotion_permitted":False,"trading_real":False}
def main():
    a=argparse.ArgumentParser();a.add_argument("--input",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True);x=a.parse_args()
    result=train(x.input)
    x.out.parent.mkdir(exist_ok=True,parents=True)
    x.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
