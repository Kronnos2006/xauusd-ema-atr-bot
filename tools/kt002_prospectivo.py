"""KT-002: muestra prospectiva de acierto direccional, BTCUSDT 1h, horizonte 4h.

Cada corrida: (1) completa pronosticos vencidos con el cierre real, (2) pronostica
una vez desde la ultima vela cerrada, (3) reescribe el resumen. Sin ordenes, sin
costos, sin rentabilidad. Registro previo en docs/KT-002_registro_prospectivo.md.
"""
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get('KT002_OUT', REPO / 'data' / 'kt002'))
PRED = OUT / 'predicciones.csv'
KRONOS_SRC = Path(os.environ.get('KRONOS_SRC', REPO / 'tools' / 'kronos-upstream'))

SYMBOL, INTERVAL, CONTEXT, HORIZON = 'BTCUSDT', '1h', 400, 4
HOUR = pd.Timedelta(hours=1)
API = 'https://data-api.binance.vision/api/v3/klines'
REVISIONS = {
    'NeoQuasar/Kronos-small': '901c26c1332695a2a8f243eb2f37243a37bea320',
    'NeoQuasar/Kronos-Tokenizer-base': '0e0117387f39004a9016484a186a908917e22426',
    'google/timesfm-2.5-200m-pytorch': '1d952420fba87f3c6dee4f240de0f1a0fbc790e3',
}
KRONOS_CODE = '67b630e67f6a18c9e9be918d9b4337c960db1e9a'
MODELS = ('kronos', 'timesfm', 'kt001')
COLUMNS = (['run_utc', 'base_open_utc', 'base_close', 'target_open_utc']
           + [f'{m}_close4' for m in MODELS] + [f'{m}_ret' for m in MODELS]
           + ['actual_close4', 'actual_ret'] + [f'{m}_hit' for m in MODELS]
           + ['scored_utc', 'elapsed_s'])


def num(x):
    """Texto exacto de un float de Python (no np.float64(...))."""
    return repr(float(x))


def fetch_klines(start=None, limit=1000):
    params = dict(symbol=SYMBOL, interval=INTERVAL, limit=limit)
    if start is not None:
        params['startTime'] = int(start.timestamp() * 1000)
    for attempt in range(4):
        try:
            r = requests.get(API, params=params, timeout=30)
            r.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))
    rows = r.json()
    df = pd.DataFrame(rows, columns=['open_time', 'open', 'high', 'low', 'close', 'volume',
                                     'close_time', 'amount', 'trades', 'tb', 'tq', 'ig'])
    df = df[['open_time', 'open', 'high', 'low', 'close', 'volume', 'amount', 'close_time']]
    for c in ['open', 'high', 'low', 'close', 'volume', 'amount']:
        df[c] = df[c].astype(float)
    df['open_time'] = pd.to_datetime(df.open_time, unit='ms', utc=True)
    df['close_time'] = pd.to_datetime(df.close_time, unit='ms', utc=True)
    return df


def closed_only(df, now):
    """Solo velas cuyo cierre ya ocurrio."""
    return df[df.close_time < now].reset_index(drop=True)


def check_context(df):
    if len(df) < CONTEXT:
        raise ValueError(f'Solo {len(df)} velas cerradas, se necesitan {CONTEXT}')
    ctx = df.iloc[-CONTEXT:].reset_index(drop=True)
    gaps = ctx.open_time.diff().dropna()
    if not (gaps == HOUR).all():
        raise ValueError('Contexto con huecos o duplicados; no se pronostica')
    vals = ctx[['open', 'high', 'low', 'close', 'volume', 'amount']].to_numpy()
    if not np.isfinite(vals).all() or (ctx[['open', 'high', 'low', 'close']] <= 0).any().any():
        raise ValueError('Contexto con valores no finitos o no positivos')
    return ctx


def load_predictions():
    if PRED.exists():
        return pd.read_csv(PRED, dtype=str)
    return pd.DataFrame(columns=COLUMNS, dtype=str)


def sign_hit(pred_ret, actual_ret):
    if pred_ret == 0 or actual_ret == 0 or not (math.isfinite(pred_ret) and math.isfinite(actual_ret)):
        return ''
    return '1' if (pred_ret > 0) == (actual_ret > 0) else '0'


def score(preds, closed, now):
    """Completa filas vencidas con el cierre real de la vela objetivo."""
    if preds.empty:
        return preds
    by_open = closed.set_index('open_time').close
    pending = preds.actual_close4.isna() | (preds.actual_close4 == '')
    for i in preds.index[pending]:
        target = pd.Timestamp(preds.at[i, 'target_open_utc'])
        if target + HOUR > now:
            continue  # aun no cierra
        if target not in by_open.index:
            extra = fetch_klines(start=target, limit=5)
            extra = closed_only(extra, now).set_index('open_time').close
            if target not in extra.index:
                continue
            actual = float(extra[target])
        else:
            actual = float(by_open[target])
        base = float(preds.at[i, 'base_close'])
        actual_ret = actual / base - 1
        preds.at[i, 'actual_close4'] = num(actual)
        preds.at[i, 'actual_ret'] = num(actual_ret)
        for m in MODELS:
            preds.at[i, f'{m}_hit'] = sign_hit(float(preds.at[i, f'{m}_ret']), actual_ret)
        preds.at[i, 'scored_utc'] = now.isoformat()
    return preds


def forecast(ctx):
    """Kronos y TimesFM con la configuracion fija de KT-001, sobre velas reales."""
    sys.path.insert(0, str(KRONOS_SRC))
    import torch
    import timesfm
    from model import Kronos, KronosTokenizer, KronosPredictor

    torch.manual_seed(42)
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    frame = ctx[['open', 'high', 'low', 'close', 'volume', 'amount']].copy()
    x_ts = ctx.open_time.dt.tz_localize(None).reset_index(drop=True)
    last = x_ts.iloc[-1]
    y_ts = pd.Series([last + HOUR * (k + 1) for k in range(HORIZON)])
    tokenizer = KronosTokenizer.from_pretrained(
        'NeoQuasar/Kronos-Tokenizer-base', revision=REVISIONS['NeoQuasar/Kronos-Tokenizer-base'])
    model = Kronos.from_pretrained('NeoQuasar/Kronos-small',
                                   revision=REVISIONS['NeoQuasar/Kronos-small'])
    predictor = KronosPredictor(model, tokenizer, device='cpu', max_context=512)
    with torch.inference_mode():
        kp = predictor.predict(frame, x_ts, y_ts, pred_len=HORIZON, T=1., top_p=.9,
                               sample_count=20, verbose=False)
    if kp.shape != (HORIZON, 6) or not np.isfinite(kp.to_numpy()).all():
        raise ValueError('Salida Kronos invalida')
    tfm = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
        'google/timesfm-2.5-200m-pytorch',
        revision=REVISIONS['google/timesfm-2.5-200m-pytorch'], torch_compile=False)
    tfm.compile(timesfm.ForecastConfig(max_context=512, max_horizon=128,
        per_core_batch_size=1, normalize_inputs=True, use_continuous_quantile_head=True,
        force_flip_invariance=True, infer_is_positive=True, fix_quantile_crossing=True))
    with torch.inference_mode():
        point, _ = tfm.forecast(horizon=HORIZON, inputs=[frame.close.to_numpy(np.float32)])
    if point.shape != (1, HORIZON) or not np.isfinite(point).all():
        raise ValueError('Salida TimesFM invalida')
    return float(kp.close.iloc[-1]), float(point[0, -1])


def build_row(ctx, k_close, t_close, now, elapsed):
    base = ctx.iloc[-1]
    c0 = float(base.close)
    if not all(math.isfinite(v) and v > 0 for v in (c0, k_close, t_close)):
        raise ValueError('Precio no finito o no positivo')
    k_ret, t_ret = k_close / c0 - 1, t_close / c0 - 1
    e_ret = 0.5 * k_ret + 0.5 * t_ret
    row = dict.fromkeys(COLUMNS, '')
    row.update(run_utc=now.isoformat(), base_open_utc=base.open_time.isoformat(),
               base_close=num(c0),
               target_open_utc=(base.open_time + HOUR * HORIZON).isoformat(),
               kronos_close4=num(k_close), timesfm_close4=num(t_close),
               kt001_close4=num(c0 * (1 + e_ret)),
               kronos_ret=num(k_ret), timesfm_ret=num(t_ret), kt001_ret=num(e_ret),
               elapsed_s=f'{elapsed:.1f}')
    return row


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(c - h, 4), round(c + h, 4)


def summarize(preds, now):
    scored = preds[(preds.actual_ret.notna()) & (preds.actual_ret != '')].copy()
    hours = pd.to_datetime(scored.base_open_utc, utc=True).dt.hour
    out = dict(variant='KT-002', updated_utc=now.isoformat(), pronosticos=int(len(preds)),
               vencidos=int(len(scored)), profitability_evaluated=False)
    for name, sub in (('todos_solapados', scored), ('sin_solape', scored[hours % 4 == 0])):
        ar = sub.actual_ret.astype(float)
        nz = ar[ar != 0]
        block = dict(n_vencidos=int(len(sub)),
                     siempre_sube=dict(n=int(len(nz)), aciertos=int((nz > 0).sum()),
                                       tasa=round(float((nz > 0).mean()), 4) if len(nz) else None,
                                       ic95=wilson(int((nz > 0).sum()), int(len(nz)))))
        for m in MODELS:
            h = sub[f'{m}_hit']
            h = h[h.isin(['0', '1'])].astype(int)
            block[m] = dict(n=int(len(h)), aciertos=int(h.sum()),
                            tasa=round(float(h.mean()), 4) if len(h) else None,
                            ic95=wilson(int(h.sum()), int(len(h))))
        out[name] = block
    (OUT / 'resumen.json').write_text(json.dumps(out, indent=2), encoding='utf-8')

    def fmt(b):
        if not b['n']:
            return 'sin datos'
        lo, hi = b['ic95']
        return f"{b['aciertos']}/{b['n']} = {b['tasa']*100:.1f} % (IC95 {lo*100:.1f}–{hi*100:.1f})"
    lines = ['# KT-002 — acierto direccional prospectivo (BTCUSDT 1h, 4h)', '',
             f"Actualizado {now.strftime('%Y-%m-%d %H:%M')} UTC. Pronósticos: {out['pronosticos']}, "
             f"vencidos: {out['vencidos']}.", '',
             'Descriptivo. No mide rentabilidad ni costos. Interpretar solo **sin solape**.', '']
    for name, title in (('sin_solape', 'Sin solape (base cada 4 h)'),
                        ('todos_solapados', 'Todos (ventanas solapadas, no independientes)')):
        b = out[name]
        lines += [f'## {title}', '', f"- Kronos: {fmt(b['kronos'])}",
                  f"- TimesFM: {fmt(b['timesfm'])}", f"- KT-001 50/50: {fmt(b['kt001'])}",
                  f"- Referencia «siempre sube»: {fmt(b['siempre_sube'])}", '']
    (OUT / 'resumen.md').write_text('\n'.join(lines), encoding='utf-8')
    return out


def main():
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    lock = OUT / 'model_revisions.json'
    pinned = dict(REVISIONS, kronos_code=KRONOS_CODE)
    if lock.exists() and json.loads(lock.read_text(encoding='utf-8')) != pinned:
        raise ValueError('Revisiones distintas de las registradas en KT-002')
    lock.write_text(json.dumps(pinned, indent=2), encoding='utf-8')

    now = pd.Timestamp(datetime.now(timezone.utc))
    closed = closed_only(fetch_klines(), now)
    preds = score(load_predictions(), closed, now)
    preds[COLUMNS].to_csv(PRED, index=False)  # guardar puntuacion aunque falle el pronostico
    summarize(preds, now)

    ctx = check_context(closed)
    base_iso = ctx.iloc[-1].open_time.isoformat()
    if base_iso in set(preds.base_open_utc):
        print(f'Ya existe pronostico para base {base_iso}; solo se puntua.')
    else:
        k_close, t_close = forecast(ctx)
        row = build_row(ctx, k_close, t_close, now, time.perf_counter() - started)
        preds = pd.concat([preds, pd.DataFrame([row], columns=COLUMNS)], ignore_index=True)
        print(f"Pronostico base {base_iso}: kronos {row['kronos_ret']}, "
              f"timesfm {row['timesfm_ret']}, kt001 {row['kt001_ret']}")
    preds[COLUMNS].to_csv(PRED, index=False)
    print(json.dumps(summarize(preds, now)['sin_solape'], indent=1))


if __name__ == '__main__':
    main()
