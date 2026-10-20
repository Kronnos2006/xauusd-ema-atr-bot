"""KT-001: inferencia sintetica conjunta, sin backtest ni conexion de trading."""
import os
from pathlib import Path
import sys
import time
import json
import hashlib
import subprocess

ROOT = Path(__file__).resolve().parent
os.environ['HF_HOME'] = str(ROOT / 'kronos-cache')
sys.path.insert(0, str(ROOT / 'kronos-upstream'))

import numpy as np
import pandas as pd
import torch
import timesfm
from huggingface_hub import snapshot_download
from model import Kronos, KronosTokenizer, KronosPredictor


def combine(kronos_close, timesfm_close, last_close):
    """Retornos simples desde el mismo precio base y timestamps identicos."""
    if not kronos_close.index.equals(timesfm_close.index):
        raise ValueError('Forecast timestamps differ')
    if not np.isfinite(last_close) or last_close <= 0:
        raise ValueError('Invalid reference close')
    values = np.column_stack([kronos_close, timesfm_close])
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError('Invalid forecast close')
    result = pd.DataFrame({'kronos_close': kronos_close, 'timesfm_close': timesfm_close})
    result['kronos_return'] = kronos_close / last_close - 1
    result['timesfm_return'] = timesfm_close / last_close - 1
    result['ensemble_return'] = (result.kronos_return + result.timesfm_return) / 2
    result['ensemble_close'] = last_close * (1 + result.ensemble_return)
    return result


def main():
    started = time.perf_counter()
    torch.manual_seed(42)
    torch.set_num_threads(4)
    n, horizon = 400, 4
    t = np.arange(n)
    close = 100 + .02*t + np.sin(t/5)
    opening = np.r_[close[0], close[:-1]]
    frame = pd.DataFrame(dict(open=opening, high=np.maximum(opening, close)+.2,
                             low=np.minimum(opening, close)-.2, close=close,
                             volume=1000+10*np.cos(t)))
    frame['amount'] = frame.volume * frame.close
    stamps = pd.Series(pd.date_range('2026-01-01', periods=n+horizon, freq='h'))
    index = pd.DatetimeIndex(stamps.iloc[n:])
    revisions = {
        'NeoQuasar/Kronos-small': '901c26c1332695a2a8f243eb2f37243a37bea320',
        'NeoQuasar/Kronos-Tokenizer-base': '0e0117387f39004a9016484a186a908917e22426',
        'google/timesfm-2.5-200m-pytorch': '1d952420fba87f3c6dee4f240de0f1a0fbc790e3',
    }
    out = ROOT / 'ensemble-output'
    out.mkdir(exist_ok=True)
    lock = out / 'model_revisions.json'
    if lock.exists():
        if json.loads(lock.read_text(encoding='utf-8')) != revisions:
            raise ValueError('Model revision lock differs from KT-001')
    else:
        lock.write_text(json.dumps(revisions, indent=2), encoding='utf-8')
    tokenizer = KronosTokenizer.from_pretrained('NeoQuasar/Kronos-Tokenizer-base',
        revision=revisions['NeoQuasar/Kronos-Tokenizer-base'])
    model = Kronos.from_pretrained('NeoQuasar/Kronos-small',
        revision=revisions['NeoQuasar/Kronos-small'])
    predictor = KronosPredictor(model, tokenizer, device='cpu', max_context=512)
    with torch.inference_mode():
        kp = predictor.predict(frame, stamps.iloc[:n], stamps.iloc[n:], pred_len=horizon,
                               T=1., top_p=.9, sample_count=20, verbose=False)
    assert kp.shape == (horizon, 6) and np.isfinite(kp.to_numpy()).all()
    assert kp.index.equals(index)
    tfm = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
        'google/timesfm-2.5-200m-pytorch',
        revision=revisions['google/timesfm-2.5-200m-pytorch'], torch_compile=False)
    tfm.compile(timesfm.ForecastConfig(max_context=512, max_horizon=128,
        per_core_batch_size=1, normalize_inputs=True, use_continuous_quantile_head=True,
        force_flip_invariance=True, infer_is_positive=True, fix_quantile_crossing=True))
    with torch.inference_mode():
        point, quantiles = tfm.forecast(horizon=horizon, inputs=[close.astype(np.float32)])
    assert point.shape == (1, horizon), point.shape
    assert quantiles.shape == (1, horizon, 10), quantiles.shape
    assert np.isfinite(point).all() and np.isfinite(quantiles).all()
    combined = combine(kp.close, pd.Series(point[0], index=index), close[-1])
    np.testing.assert_allclose(combined.ensemble_close,
                               (combined.kronos_close + combined.timesfm_close)/2)
    # Comprobacion de rechazo: no promediar horizontes desalineados silenciosamente.
    try:
        combine(kp.close, pd.Series(point[0], index=index+pd.Timedelta(hours=1)), close[-1])
    except ValueError:
        pass
    else:
        raise AssertionError('Misaligned forecasts accepted')
    combined.to_csv(out / 'synthetic_ensemble.csv', index_label='timestamp')
    frame.assign(timestamp=stamps.iloc[:n].to_numpy()).to_csv(out / 'synthetic_input.csv', index=False)
    hashes = {}
    for repo, revision in revisions.items():
        path = Path(snapshot_download(repo, revision=revision, local_files_only=True))
        for weight in path.glob('*.safetensors'):
            with weight.open('rb') as stream:
                hashes[f'{repo}@{revision}/{weight.name}'] = hashlib.file_digest(stream, 'sha256').hexdigest()
    report = dict(status='PASS_TECHNICAL_ONLY', variant='KT-001', data='synthetic',
        input_rows=n, horizon=horizon, interval='1h', weights=[.5, .5], seed=42,
        kronos_samples=20, timesfm_estimator='median', revisions=revisions, sha256=hashes,
        elapsed_seconds=round(time.perf_counter()-started, 2), profitability_evaluated=False)
    (out/'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    frozen = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True)
    (out/'requirements-resolved.txt').write_text(frozen, encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('sha256',)}, indent=2))


if __name__ == '__main__':
    main()
