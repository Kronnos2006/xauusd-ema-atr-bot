"""Prueba de inferencia sintetica; no evalua senales ni rentabilidad."""
import os
from pathlib import Path
import sys
import json
import time

ROOT = Path(__file__).resolve().parent
os.environ['HF_HOME'] = str(ROOT / 'kronos-cache')
sys.path.insert(0, str(ROOT / 'kronos-upstream'))

import numpy as np
import pandas as pd
import torch
from model import Kronos, KronosTokenizer, KronosPredictor

torch.manual_seed(42)
torch.set_num_threads(4)
n, horizon = 64, 4
t = np.arange(n)
close = 100 + 0.02 * t + np.sin(t / 5)
opening = np.r_[close[0], close[:-1]]
df = pd.DataFrame(dict(open=opening, high=np.maximum(opening, close)+0.2,
                       low=np.minimum(opening, close)-0.2, close=close,
                       volume=1000+10*np.cos(t)))
df['amount'] = df['volume'] * df['close']
timestamps = pd.Series(pd.date_range('2026-01-01', periods=n+horizon, freq='5min'))
started = time.perf_counter()
tokenizer = KronosTokenizer.from_pretrained('NeoQuasar/Kronos-Tokenizer-base')
model = Kronos.from_pretrained('NeoQuasar/Kronos-small')
predictor = KronosPredictor(model, tokenizer, device='cpu', max_context=512)
prediction = predictor.predict(df, timestamps.iloc[:n], timestamps.iloc[n:],
                               pred_len=horizon, sample_count=1, verbose=False)
assert prediction.shape == (horizon, 6), prediction.shape
assert np.isfinite(prediction.to_numpy()).all(), 'Non-finite output'
output = ROOT / 'kronos-output'
output.mkdir(exist_ok=True)
prediction.to_csv(output / 'synthetic_prediction.csv')
report = dict(status='PASS_TECHNICAL_ONLY', data='synthetic', input_rows=n,
              forecast_rows=horizon, device='cpu', seed=42,
              elapsed_seconds=round(time.perf_counter()-started, 2),
              torch=torch.__version__, pandas=pd.__version__, numpy=np.__version__,
              profitability_evaluated=False)
(output / 'smoke_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
