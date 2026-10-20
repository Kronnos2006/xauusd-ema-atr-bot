"""KT-002: pronostico prospectivo fijo; evaluacion separada en panel/market.py."""
from pathlib import Path
import argparse
import json
import os
import sys
import time

ROOT=Path(__file__).resolve().parent
os.environ['HF_HOME']=str(ROOT/'kronos-cache')
sys.path.insert(0,str(ROOT/'kronos-upstream'))
import numpy as np
import pandas as pd
import torch
import timesfm
from model import Kronos,KronosTokenizer,KronosPredictor


def main(directory):
    def event(stage,message):print('@PANEL '+json.dumps(dict(stage=stage,message=message)),flush=True)
    context=json.loads((directory/'context.json').read_text(encoding='utf-8'))
    started=time.perf_counter();torch.manual_seed(42);torch.set_num_threads(4)
    revisions={'NeoQuasar/Kronos-small':'901c26c1332695a2a8f243eb2f37243a37bea320',
        'NeoQuasar/Kronos-Tokenizer-base':'0e0117387f39004a9016484a186a908917e22426',
        'google/timesfm-2.5-200m-pytorch':'1d952420fba87f3c6dee4f240de0f1a0fbc790e3'}
    frame=pd.DataFrame([[float(row[i]) for i in [1,2,3,4,5,7]] for row in context['rows']],
                       columns=['open','high','low','close','volume','amount'])
    # Los modelos reciben timestamps de apertura UTC; se puntua al cierre de cada vela futura.
    stamps=pd.Series(pd.to_datetime([row[0] for row in context['rows']],unit='ms',utc=True))
    future=pd.Series(pd.to_datetime([context['cutoff_ms']+i*3600000 for i in range(4)],unit='ms',utc=True))
    event('kronos','Kronos: 20 trayectorias sobre 400 velas BTCUSDT cerradas')
    tokenizer=KronosTokenizer.from_pretrained('NeoQuasar/Kronos-Tokenizer-base',revision=revisions['NeoQuasar/Kronos-Tokenizer-base'])
    model=Kronos.from_pretrained('NeoQuasar/Kronos-small',revision=revisions['NeoQuasar/Kronos-small'])
    predictor=KronosPredictor(model,tokenizer,device='cpu',max_context=512)
    with torch.inference_mode():
        paths=predictor.predict_batch([frame]*20,[stamps]*20,[future]*20,pred_len=4,
            T=1,top_p=.9,sample_count=1,verbose=False)
    values=np.stack([p.close.to_numpy() for p in paths])
    assert values.shape==(20,4) and np.isfinite(values).all() and (values>0).all()
    kronos=values.mean(axis=0)
    event('timesfm','TimesFM 2.5: cierres y cuantiles nominales')
    tfm=timesfm.TimesFM_2p5_200M_torch.from_pretrained('google/timesfm-2.5-200m-pytorch',
        revision=revisions['google/timesfm-2.5-200m-pytorch'],torch_compile=False)
    tfm.compile(timesfm.ForecastConfig(max_context=512,max_horizon=128,per_core_batch_size=1,
        normalize_inputs=True,use_continuous_quantile_head=True,force_flip_invariance=True,
        infer_is_positive=True,fix_quantile_crossing=True))
    with torch.inference_mode():point,quantiles=tfm.forecast(horizon=4,inputs=[frame.close.to_numpy(dtype=np.float32)])
    assert point.shape==(1,4) and quantiles.shape==(1,4,10)
    assert np.isfinite(point).all() and np.isfinite(quantiles).all() and (point>0).all()
    event('combine','Combinando 50/50 sin ajustar pesos; probabilidades sin calibrar')
    output=[]
    for i in range(4):
        k=float(kronos[i]);t=float(point[0,i]);e=(k+t)/2
        output.append(dict(horizon=i+1,target_close_ms=context['cutoff_ms']+(i+1)*3600000,
            kronos_close=k,timesfm_close=t,ensemble_close=e,
            kronos_up_fraction=float((values[:,i]>context['base']).mean()),
            timesfm_q10=float(quantiles[0,i,1]),timesfm_q90=float(quantiles[0,i,9])))
    event('verify','Guardando salida previa a los cierres objetivo')
    result=dict(forecast=output,revisions=revisions,weights=[.5,.5],seed=42,kronos_samples=20,
        kronos_paths=values.tolist(),elapsed_seconds=round(time.perf_counter()-started,2),
        probability_status='NO_CALIBRADA',profitability_evaluated=False)
    (directory/'generated.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    event('done','Pronosticos generados; pendientes de registro prospectivo')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--directory',type=Path,required=True)
    main(parser.parse_args().directory)
