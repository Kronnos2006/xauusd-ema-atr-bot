"""KT-003: diagnostico historico de acierto direccional, BTCUSDT 1h, horizonte 4h.

Registro previo: docs/KT-003_registro_historico.md. Diagnostico, no backtest de
estrategia: sin ordenes, costos ni rentabilidad.

Subcomandos:
  datos  OUT_DIR            descarga y verifica velas 1h (Binance oficial), escribe CSV y manifiesto
  shard  DATA_CSV I N OUT   pronostica las bases i::N
  unir   DATA_CSV SHARDS... resume y escribe data/kt003/
"""
import gzip
import hashlib
import io
import json
import math
import os
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kt002_prospectivo as kt2  # misma configuracion de modelos y puntuacion

SYMBOL, CONTEXT, HORIZON = 'BTCUSDT', 400, 4
HOUR = pd.Timedelta(hours=1)
VISION = 'https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1h/'
API = 'https://data-api.binance.vision/api/v3/klines'
FIRST_MONTH = pd.Timestamp('2017-08-01')
CUTOFF = pd.Timestamp('2024-07-01', tz='UTC')  # Kronos declara preentrenamiento hasta junio 2024
BASE_HOUR_UTC = 0
BATCH = 8
OUT = REPO / 'data' / 'kt003'


def get(url, **kw):
    for attempt in range(5):
        try:
            r = requests.get(url, timeout=60, **kw)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))


def to_ts(v):
    v = int(v)
    unit = 'us' if v > 10**14 else 'ms'  # desde 2025 los spot usan microsegundos
    return pd.to_datetime(v, unit=unit, utc=True)


def cmd_datos(out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    now = pd.Timestamp(datetime.now(timezone.utc))
    frames, manifest = [], []
    month = FIRST_MONTH
    current = now.tz_localize(None).normalize().replace(day=1)
    while month < current:
        name = f'{SYMBOL}-1h-{month:%Y-%m}.zip'
        z = get(VISION + name)
        c = get(VISION + name + '.CHECKSUM')
        if z is None or c is None:
            if month >= current - pd.offsets.MonthBegin(1):
                break  # el ultimo mes cerrado puede no estar publicado aun: se completa por API
            raise RuntimeError(f'Falta archivo oficial {name}')
        sha = hashlib.sha256(z.content).hexdigest()
        expected = c.text.split()[0]
        if sha != expected:
            raise RuntimeError(f'CHECKSUM no coincide en {name}')
        with zipfile.ZipFile(io.BytesIO(z.content)) as zf:
            raw = zf.read(zf.namelist()[0]).decode()
        rows = [l.split(',') for l in raw.strip().splitlines() if l and l[0].isdigit()]
        df = pd.DataFrame([r[:8] for r in rows], columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'amount'])
        frames.append(df)
        manifest.append(dict(archivo=name, sha256=sha, filas=len(df)))
        month += pd.offsets.MonthBegin(1)
    # Mes en curso: API publica (no hay ZIP mensual aun). Se registra aparte.
    start = pd.Timestamp(month, tz='UTC')
    api_rows = []
    while True:
        r = get(API, params=dict(symbol=SYMBOL, interval='1h', limit=1000, startTime=int(start.timestamp() * 1000)))
        batch = r.json()
        if not batch:
            break
        api_rows += [b[:8] for b in batch]
        start = to_ts(batch[-1][0]) + HOUR
        if len(batch) < 1000:
            break
    if api_rows:
        frames.append(pd.DataFrame(api_rows, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'amount']))
        manifest.append(dict(archivo=f'API klines desde {month:%Y-%m}', sha256=None, filas=len(api_rows)))
    df = pd.concat(frames, ignore_index=True)
    df['open_time'] = df.open_time.map(to_ts)
    df['close_time'] = df.close_time.map(to_ts)
    for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
        df[col] = df[col].astype(float)
    df = df[df.close_time < now]  # solo velas cerradas
    dup = int(df.open_time.duplicated().sum())
    df = df.drop_duplicates('open_time').sort_values('open_time').reset_index(drop=True)
    gaps = df.open_time.diff().dropna()
    bad_ohlc = int(((df.high < df[['open', 'close']].max(axis=1)) | (df.low > df[['open', 'close']].min(axis=1)) | (df[['open', 'high', 'low', 'close']] <= 0).any(axis=1)).sum())
    report = dict(fuente='data.binance.vision (ZIP mensuales con CHECKSUM) + API publica para el mes en curso',
                  descargado_utc=now.isoformat(), filas=len(df), primera=df.open_time.iloc[0].isoformat(),
                  ultima=df.open_time.iloc[-1].isoformat(), duplicados_eliminados=dup,
                  huecos=int((gaps != HOUR).sum()), horas_faltantes=int(((gaps - HOUR) / HOUR).clip(lower=0).sum()),
                  velas_ohlc_invalidas=bad_ohlc, archivos=manifest)
    if api_rows:
        manifest[-1]['sha256'] = hashlib.sha256(json.dumps(api_rows).encode()).hexdigest()
    csv_path = out_dir / 'btcusdt_1h.csv.gz'
    df.to_csv(csv_path, index=False, compression='gzip')
    report['sha256_csv_gz'] = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    report['sha256_csv_contenido'] = hashlib.sha256(gzip.decompress(csv_path.read_bytes())).hexdigest()
    report['velas_volumen_cero'] = int((df.volume == 0).sum())
    (out_dir / 'manifiesto_datos.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'archivos'}, indent=2))


def load(path):
    df = pd.read_csv(path, parse_dates=['open_time', 'close_time'])
    return df


def bases(df):
    """Bases diarias: vela que abre a las 00:00 UTC, con 400 velas contiguas y objetivo cerrado."""
    pos = pd.Series(np.arange(len(df)), index=df.open_time)
    out, skipped = [], 0
    ok = ((df.high >= df[['open', 'close']].max(axis=1)) & (df.low <= df[['open', 'close']].min(axis=1))
          & (df[['open', 'high', 'low', 'close']] > 0).all(axis=1)).to_numpy()
    for i in np.flatnonzero(df.open_time.dt.hour.to_numpy() == BASE_HOUR_UTC):
        if i < CONTEXT - 1:
            continue
        b = df.open_time.iloc[i]
        tgt = b + HOUR * HORIZON
        span = df.open_time.iloc[i - CONTEXT + 1:i + 1]
        if span.iloc[0] != b - HOUR * (CONTEXT - 1) or tgt not in pos.index or not ok[i - CONTEXT + 1:i + 1].all():
            skipped += 1
            continue
        out.append(i)
    return out, skipped


def cmd_shard(data_csv, i, n, out_csv):
    import torch
    import timesfm
    sys.path.insert(0, str(kt2.KRONOS_SRC))
    from model import Kronos, KronosTokenizer, KronosPredictor
    df = load(data_csv)
    idx, _ = bases(df)
    mine = idx[int(i)::int(n)]
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    R = kt2.REVISIONS
    tok = KronosTokenizer.from_pretrained('NeoQuasar/Kronos-Tokenizer-base', revision=R['NeoQuasar/Kronos-Tokenizer-base'])
    mdl = Kronos.from_pretrained('NeoQuasar/Kronos-small', revision=R['NeoQuasar/Kronos-small'])
    pred = KronosPredictor(mdl, tok, device='cpu', max_context=512)
    tfm = timesfm.TimesFM_2p5_200M_torch.from_pretrained('google/timesfm-2.5-200m-pytorch', revision=R['google/timesfm-2.5-200m-pytorch'], torch_compile=False)
    tfm.compile(timesfm.ForecastConfig(max_context=512, max_horizon=128, per_core_batch_size=1, normalize_inputs=True,
        use_continuous_quantile_head=True, force_flip_invariance=True, infer_is_positive=True, fix_quantile_crossing=True))
    cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
    rows, t0 = [], time.perf_counter()
    for start in range(0, len(mine), BATCH):
        chunk = mine[start:start + BATCH]
        ctxs = [df.iloc[j - CONTEXT + 1:j + 1].reset_index(drop=True) for j in chunk]
        xs = [c.open_time.dt.tz_localize(None).reset_index(drop=True) for c in ctxs]
        ys = [pd.Series([x.iloc[-1] + HOUR * (k + 1) for k in range(HORIZON)]) for x in xs]
        torch.manual_seed(42)
        with torch.inference_mode():
            kps = pred.predict_batch([c[cols] for c in ctxs], xs, ys, pred_len=HORIZON, T=1., top_p=.9, sample_count=20, verbose=False)
            point, _ = tfm.forecast(horizon=HORIZON, inputs=[c.close.to_numpy(np.float32) for c in ctxs])
        for c, kp, tp in zip(ctxs, kps, point):
            if kp.shape != (HORIZON, 6) or not np.isfinite(kp.to_numpy()).all() or not np.isfinite(tp).all():
                raise ValueError('Salida de modelo invalida')
            row = kt2.build_row(c, float(kp.close.iloc[-1]), float(tp[-1]), pd.Timestamp(datetime.now(timezone.utc)), 0.0)
            rows.append(row)
        if start == 0 and str(i) == '0':
            torch.manual_seed(42)
            with torch.inference_mode():
                kps2 = pred.predict_batch([c[cols] for c in ctxs], xs, ys, pred_len=HORIZON, T=1., top_p=.9, sample_count=20, verbose=False)
                point2, _ = tfm.forecast(horizon=HORIZON, inputs=[c.close.to_numpy(np.float32) for c in ctxs])
            same = all(a.equals(b) for a, b in zip(kps, kps2)) and bool(np.array_equal(point, point2))
            Path('reproducibilidad.json').write_text(json.dumps(dict(lote=[c.open_time.iloc[-1].isoformat() for c in ctxs], identico=same), indent=2))
        print(f'shard {i}/{n}: {len(rows)}/{len(mine)} en {time.perf_counter() - t0:.0f} s', flush=True)
    pd.DataFrame(rows, columns=kt2.COLUMNS).to_csv(out_csv, index=False)


def cmd_prueba(data_csv, out_json):
    import torch
    import timesfm
    sys.path.insert(0, str(kt2.KRONOS_SRC))
    from model import Kronos, KronosTokenizer, KronosPredictor
    df = load(data_csv)
    idx, skipped = bases(df)
    b = df.open_time.iloc[idx]
    cut = pd.Timestamp(CUTOFF)
    shards_ok = sorted(sum([idx[j::16] for j in range(16)], [])) == idx
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    R = kt2.REVISIONS
    tok = KronosTokenizer.from_pretrained('NeoQuasar/Kronos-Tokenizer-base', revision=R['NeoQuasar/Kronos-Tokenizer-base'])
    mdl = Kronos.from_pretrained('NeoQuasar/Kronos-small', revision=R['NeoQuasar/Kronos-small'])
    pred = KronosPredictor(mdl, tok, device='cpu', max_context=512)
    cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
    j = idx[0]
    c = df.iloc[j - CONTEXT + 1:j + 1].reset_index(drop=True)
    x = c.open_time.dt.tz_localize(None).reset_index(drop=True)
    y = pd.Series([x.iloc[-1] + HOUR * (k + 1) for k in range(HORIZON)])
    torch.manual_seed(42)
    with torch.inference_mode():
        single = pred.predict(c[cols], x, y, pred_len=HORIZON, T=1., top_p=.9, sample_count=20, verbose=False)
    torch.manual_seed(42)
    with torch.inference_mode():
        batch = pred.predict_batch([c[cols]], [x], [y], pred_len=HORIZON, T=1., top_p=.9, sample_count=20, verbose=False)[0]
    diff = float(np.abs(single.to_numpy() - batch.to_numpy()).max())
    # tiempo por lote de 8 (dos lotes)
    tiempos = []
    for start in (0, BATCH):
        chunk = idx[start:start + BATCH]
        ctxs = [df.iloc[k - CONTEXT + 1:k + 1].reset_index(drop=True) for k in chunk]
        xs = [cc.open_time.dt.tz_localize(None).reset_index(drop=True) for cc in ctxs]
        ys = [pd.Series([xx.iloc[-1] + HOUR * (k + 1) for k in range(HORIZON)]) for xx in xs]
        t0 = time.perf_counter()
        torch.manual_seed(42)
        with torch.inference_mode():
            pred.predict_batch([cc[cols] for cc in ctxs], xs, ys, pred_len=HORIZON, T=1., top_p=.9, sample_count=20, verbose=False)
        tiempos.append(round(time.perf_counter() - t0, 1))
    lotes_por_shard = math.ceil(len(idx) / 16 / BATCH)
    rep = dict(bases=len(idx), bases_saltadas=skipped, post_corte=int((b >= cut).sum()),
               primera=b.min().isoformat(), ultima=b.max().isoformat(), shards_cubren_todo=shards_ok,
               predict_vs_batch_max_dif=diff, predict_vs_batch_identico=bool(single.equals(batch)),
               segundos_por_lote=tiempos, lotes_por_shard=lotes_por_shard,
               minutos_estimados_por_shard=round(max(tiempos) * lotes_por_shard / 60, 1))
    Path(out_json).write_text(json.dumps(rep, indent=2), encoding='utf-8')
    print(json.dumps(rep, indent=2))


def cmd_unir(data_csv, *shards):
    OUT.mkdir(parents=True, exist_ok=True)
    df = load(data_csv)
    idx, skipped = bases(df)
    preds = pd.concat([pd.read_csv(s, dtype=str) for s in shards], ignore_index=True)
    if preds.base_open_utc.duplicated().any():
        raise ValueError('Bases duplicadas entre shards')
    esperadas = set(df.open_time.iloc[idx].map(lambda t: t.isoformat()))
    if set(preds.base_open_utc) != esperadas:
        raise ValueError(f'Bases distintas de las esperadas: {len(set(preds.base_open_utc) ^ esperadas)} diferencias')
    close = df.set_index('open_time').close
    now = pd.Timestamp(datetime.now(timezone.utc))
    for i in preds.index:
        tgt = pd.Timestamp(preds.at[i, 'target_open_utc'])
        actual = float(close[tgt])
        ar = actual / float(preds.at[i, 'base_close']) - 1
        preds.at[i, 'actual_close4'] = kt2.num(actual)
        preds.at[i, 'actual_ret'] = kt2.num(ar)
        for m in kt2.MODELS:
            preds.at[i, f'{m}_hit'] = kt2.sign_hit(float(preds.at[i, f'{m}_ret']), ar)
        preds.at[i, 'scored_utc'] = now.isoformat()
    preds['persist_ret'] = ''
    for i in preds.index:
        bt = pd.Timestamp(preds.at[i, 'base_open_utc'])
        preds.at[i, 'persist_ret'] = kt2.num(float(close[bt]) / float(close[bt - HOUR * HORIZON]) - 1)
    preds = preds.sort_values('base_open_utc').reset_index(drop=True)
    base = pd.to_datetime(preds.base_open_utc, utc=True)
    preds['periodo'] = np.where(base < CUTOFF, 'dentro_entrenamiento', 'post_corte')
    preds.to_csv(OUT / 'predicciones.csv', index=False)

    def block(sub):
        ar = sub.actual_ret.astype(float)
        nz = ar[ar != 0]
        b = dict(n=int(len(sub)), siempre_sube=stat(int((nz > 0).sum()), int(len(nz))))
        pr = sub.persist_ret.astype(float)
        ph = ((pr > 0) == (ar > 0))[(pr != 0) & (ar != 0)].astype(int)
        b['persistencia'] = stat(int(ph.sum()), int(len(ph)))
        up = (sub.actual_ret.astype(float) > 0).astype(int).where(sub.actual_ret.astype(float) != 0)
        for m in kt2.MODELS:
            h = sub[f'{m}_hit']
            h = h[h.isin(['0', '1'])].astype(int)
            both = h.index.intersection(up.dropna().index)
            b[m] = stat(int(h.sum()), int(len(h)))
            b[m]['mcnemar_vs_sube'] = kt2.mcnemar(h[both], up[both].astype(int))
        ps = sorted((b[m]['mcnemar_vs_sube']['p'], m) for m in kt2.MODELS if b[m]['mcnemar_vs_sube']['p'] is not None)
        run = 0.0
        for r, (pv, m) in enumerate(ps):  # Holm sobre los 3 modelos
            run = max(run, min(1.0, (len(ps) - r) * pv))
            b[m]['mcnemar_vs_sube']['p_holm'] = round(run, 4)
        return b

    def stat(k, n):
        lo, hi = kt2.wilson(k, n)
        return dict(aciertos=k, n=n, tasa=round(k / n, 4) if n else None, ic95=[lo, hi])

    summary = dict(variant='KT-003', generado_utc=now.isoformat(), bases_saltadas_por_huecos=skipped,
                   profitability_evaluated=False, total=block(preds),
                   por_periodo={p: block(g) for p, g in preds.groupby('periodo')},
                   por_anio={str(y): block(g) for y, g in preds.groupby(base.dt.year)})
    (OUT / 'resumen.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    f = lambda s: f"{s['aciertos']}/{s['n']} = {s['tasa'] * 100:.1f} % (IC95 {s['ic95'][0] * 100:.1f}–{s['ic95'][1] * 100:.1f})" if s['n'] else 'sin datos'
    lines = ['# KT-003 — diagnóstico histórico de acierto (BTCUSDT 1h, 4h, una base diaria)', '',
             'Diagnóstico, no backtest de estrategia: sin costos ni rentabilidad.',
             '"Dentro del entrenamiento" no mide predicción: Kronos ya vio esos datos.', '']
    for title, b in [('Después del corte (desde 2024-07-01)', summary['por_periodo'].get('post_corte')),
                     ('Dentro del entrenamiento (hasta 2024-06-30)', summary['por_periodo'].get('dentro_entrenamiento')),
                     ('Total', summary['total'])]:
        if not b:
            continue
        lines += [f'## {title} — n={b["n"]}', '', f'- Kronos: {f(b["kronos"])}', f'- TimesFM: {f(b["timesfm"])}',
                  f'- KT-001 50/50: {f(b["kt001"])}', f'- Referencia «siempre sube»: {f(b["siempre_sube"])}',
                  f'- Referencia «persistencia» (repite las 4 h previas): {f(b["persistencia"])}',
                  '- McNemar vs «siempre sube» (p / p Holm): ' + ', '.join(f'{m} {b[m]["mcnemar_vs_sube"]["p"]} / {b[m]["mcnemar_vs_sube"].get("p_holm")}' for m in kt2.MODELS), '']
    lines += ['## Por año (KT-001 / siempre sube)', '']
    for y, b in summary['por_anio'].items():
        lines.append(f'- {y}: {f(b["kt001"])} / {f(b["siempre_sube"])}')
    (OUT / 'resumen.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))


if __name__ == '__main__':
    cmd, *args = sys.argv[1:]
    {'datos': cmd_datos, 'prueba': cmd_prueba, 'shard': cmd_shard, 'unir': cmd_unir}[cmd](*args)
