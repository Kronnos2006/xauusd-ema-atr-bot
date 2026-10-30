"""KT-004: acierto direccional a 4 h en ETH, SOL, BNB y XRP, periodo posterior a los modelos.

Registro previo: docs/KT-004_registro_multiactivo.md (con Enmienda A). Diagnostico, no backtest de
estrategia: sin ordenes, costos aplicados ni capital.

Subcomandos:
  datos  OUT_DIR             descarga y verifica velas 1h, escribe un CSV por activo y manifiesto
  prueba DATA_DIR OUT_JSON   cuenta bases y saltos (sin pronosticos)
  shard  DATA_DIR I N OUT    pronostica las bases i::N (todas los activos)
  unir   DATA_DIR SHARDS...  puntua, analiza y escribe data/kt004/
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kt002_prospectivo as kt2  # misma configuracion de modelos y puntuacion

SYMBOLS = ('ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT')
CONTEXT, HORIZON, BATCH = 400, 4, 8
HOUR = pd.Timedelta(hours=1)
FIRST_MONTH = pd.Timestamp('2024-07-01')            # contexto de 400 h antes de la primera base
LAST_MONTH = pd.Timestamp('2026-07-01')             # el holdout (desde 2026-08-01) no se descarga
FIRST_BASE = pd.Timestamp('2024-08-01 00:00', tz='UTC')
LAST_BASE = pd.Timestamp('2026-07-31 20:00', tz='UTC')
LAST_CANDLE = LAST_BASE + HOUR * HORIZON             # 2026-08-01 00:00: vela objetivo de la ultima base
CORTE_CONTAMINACION = pd.Timestamp('2025-10-01', tz='UTC')  # chequeo descriptivo antes/despues
PRIMARIO = ('kronos', 'ETHUSDT')
SECUNDARIOS = [('kronos', 'SOLUSDT'), ('kronos', 'BNBUSDT'), ('kronos', 'XRPUSDT'), ('timesfm', 'ETHUSDT'), ('kt001', 'ETHUSDT')]
OUT = REPO / 'data' / 'kt004'
BOOT_B, BOOT_SEED = 10_000, 20261030
COSTO_IDA_VUELTA = 0.002
KCOLS = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'amount']


# ---------------------------------------------------------------- datos
def get(url, **kw):
    import requests
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
    return pd.to_datetime(v, unit='us' if v > 10**14 else 'ms', utc=True)


def descargar(symbol, now):
    vision = f'https://data.binance.vision/data/spot/monthly/klines/{symbol}/1h/'
    frames, manifest = [], []
    month = FIRST_MONTH
    while month <= LAST_MONTH:
        name = f'{symbol}-1h-{month:%Y-%m}.zip'
        z, c = get(vision + name), get(vision + name + '.CHECKSUM')
        if z is None or c is None:
            raise RuntimeError(f'Falta archivo oficial {name}')
        sha = hashlib.sha256(z.content).hexdigest()
        if sha != c.text.split()[0]:
            raise RuntimeError(f'CHECKSUM no coincide en {name}')
        with zipfile.ZipFile(io.BytesIO(z.content)) as zf:
            raw = zf.read(zf.namelist()[0]).decode()
        rows = [l.split(',')[:8] for l in raw.strip().splitlines() if l and l[0].isdigit()]
        frames.append(pd.DataFrame(rows, columns=KCOLS))
        manifest.append(dict(archivo=name, sha256=sha, filas=len(rows)))
        month += pd.offsets.MonthBegin(1)
    # La vela 2026-08-01 00:00 (objetivo de la ultima base) esta en el ZIP de agosto: se pide sola por API.
    r = get('https://data-api.binance.vision/api/v3/klines', params=dict(symbol=symbol, interval='1h', limit=1,
            startTime=int(LAST_CANDLE.timestamp() * 1000)))
    extra = [b[:8] for b in r.json()][:1]
    frames.append(pd.DataFrame(extra, columns=KCOLS))
    manifest.append(dict(archivo='API: solo la vela 2026-08-01 00:00', filas=len(extra),
                         sha256=hashlib.sha256(json.dumps(extra).encode()).hexdigest()))
    df = pd.concat(frames, ignore_index=True)
    df['open_time'] = df.open_time.map(to_ts)
    df['close_time'] = df.close_time.map(to_ts)
    for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
        df[col] = df[col].astype(float)
    df = df[(df.close_time < now) & (df.open_time <= LAST_CANDLE)]  # solo velas cerradas y nada posterior
    dup = int(df.open_time.duplicated().sum())
    df = df.drop_duplicates('open_time').sort_values('open_time').reset_index(drop=True)
    return df, manifest, dup


def cmd_datos(out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    now = pd.Timestamp(datetime.now(timezone.utc))
    report = dict(fuente='data.binance.vision (ZIP mensuales con CHECKSUM) + API publica para el mes en curso',
                  descargado_utc=now.isoformat(), activos={})
    for sym in SYMBOLS:
        df, manifest, dup = descargar(sym, now)
        desal = df.open_time != df.open_time.dt.floor('h')
        gaps = df.open_time[~desal].diff().dropna()
        path = out_dir / f'{sym.lower()}_1h.csv.gz'
        df.to_csv(path, index=False, compression='gzip')
        report['activos'][sym] = dict(
            filas=len(df), primera=df.open_time.iloc[0].isoformat(), ultima=df.open_time.iloc[-1].isoformat(),
            duplicados_eliminados=dup, huecos=int((gaps != HOUR).sum()),
            horas_faltantes=int(((gaps - HOUR) / HOUR).clip(lower=0).sum()),
            velas_ohlc_invalidas=int((~ohlc_ok(df)).sum()), velas_desalineadas=int(desal.sum()),
            velas_volumen_cero=int((df.volume == 0).sum()),
            sha256_csv_gz=hashlib.sha256(path.read_bytes()).hexdigest(),
            sha256_csv_contenido=hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest(),
            archivos=manifest)
    (out_dir / 'manifiesto_datos.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({s: {k: v for k, v in a.items() if k != 'archivos'} for s, a in report['activos'].items()}, indent=2))


def verificar(data_dir):
    """Aborta si algun CSV no coincide con el hash sellado en el manifiesto."""
    man = json.loads((Path(data_dir) / 'manifiesto_datos.json').read_text(encoding='utf-8'))
    for sym in SYMBOLS:
        p = Path(data_dir) / f'{sym.lower()}_1h.csv.gz'
        if hashlib.sha256(p.read_bytes()).hexdigest() != man['activos'][sym]['sha256_csv_gz']:
            raise SystemExit(f'Hash de {p.name} distinto del sellado')


def ohlc_ok(df):
    return ((df.high >= df[['open', 'close']].max(axis=1)) & (df.low <= df[['open', 'close']].min(axis=1))
            & (df[['open', 'high', 'low', 'close']] > 0).all(axis=1))


def load(data_dir, sym):
    df = pd.read_csv(Path(data_dir) / f'{sym.lower()}_1h.csv.gz')
    for col in ('open_time', 'close_time'):
        df[col] = pd.to_datetime(df[col], utc=True, format='ISO8601')
    aligned = df.open_time == df.open_time.dt.floor('h')
    df = df[aligned].reset_index(drop=True)
    df.attrs['velas_desalineadas'] = int((~aligned).sum())
    return df


def bases(df):
    """Bases cada 4 h (hora UTC multiplo de 4) en [FIRST_BASE, LAST_BASE], contexto contiguo y objetivo presente."""
    times = set(df.open_time)
    ok = ohlc_ok(df).to_numpy()
    hours = df.open_time.dt.hour.to_numpy()
    out, skipped = [], 0
    sel = (hours % 4 == 0) & (df.open_time >= FIRST_BASE).to_numpy() & (df.open_time <= LAST_BASE).to_numpy()
    for i in np.flatnonzero(sel):
        b = df.open_time.iloc[i]
        if (i < CONTEXT - 1 or df.open_time.iloc[i - CONTEXT + 1] != b - HOUR * (CONTEXT - 1)
                or (b + HOUR * HORIZON) not in times or not ok[i - CONTEXT + 1:i + 1].all()):
            skipped += 1
            continue
        out.append(i)
    return out, skipped


def todas_las_bases(data_dir):
    lista, info = [], {}
    for sym in SYMBOLS:
        df = load(data_dir, sym)
        idx, skipped = bases(df)
        lista += [(sym, i) for i in idx]
        info[sym] = dict(bases=len(idx), saltadas=skipped, velas_desalineadas=df.attrs['velas_desalineadas'],
                         primera=df.open_time.iloc[idx[0]].isoformat() if idx else None,
                         ultima=df.open_time.iloc[idx[-1]].isoformat() if idx else None)
    return lista, info


def cmd_prueba(data_dir, out_json, n_shards='40'):
    verificar(data_dir)
    lista, info = todas_las_bases(data_dir)
    n = int(n_shards)
    cubre = sorted(sum([lista[j::n] for j in range(n)], [])) == sorted(lista)
    lotes = -(-len(lista) // n // BATCH) + 1
    rep = dict(bases_total=len(lista), por_activo=info, shards=n, shards_cubren_todo=cubre,
               lotes_por_shard_max=lotes, minutos_estimados_por_shard=round(lotes * 171 / 60, 1),
               nota='Sin pronosticos. Tiempo estimado con 171 s/lote medido en KT-003.')
    Path(out_json).write_text(json.dumps(rep, indent=2), encoding='utf-8')
    print(json.dumps(rep, indent=2))


# ---------------------------------------------------------------- pronosticos
def cmd_shard(data_dir, i, n, out_csv):
    import torch
    import timesfm
    sys.path.insert(0, str(kt2.KRONOS_SRC))
    from model import Kronos, KronosTokenizer, KronosPredictor
    verificar(data_dir)
    lista, _ = todas_las_bases(data_dir)
    mine = lista[int(i)::int(n)]
    frames = {s: load(data_dir, s) for s in SYMBOLS}
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
        ctxs = [frames[s].iloc[j - CONTEXT + 1:j + 1].reset_index(drop=True) for s, j in chunk]
        xs = [c.open_time.dt.tz_localize(None).reset_index(drop=True) for c in ctxs]
        ys = [pd.Series([x.iloc[-1] + HOUR * (k + 1) for k in range(HORIZON)]) for x in xs]
        torch.manual_seed(42)
        with torch.inference_mode():
            kps = pred.predict_batch([c[cols] for c in ctxs], xs, ys, pred_len=HORIZON, T=1., top_p=.9, sample_count=20, verbose=False)
            point, _ = tfm.forecast(horizon=HORIZON, inputs=[c.close.to_numpy(np.float32) for c in ctxs])
        for (s, _), c, kp, tp in zip(chunk, ctxs, kps, point):
            if kp.shape != (HORIZON, 6) or not np.isfinite(kp.to_numpy()).all() or not np.isfinite(tp).all():
                raise ValueError('Salida de modelo invalida')
            row = kt2.build_row(c, float(kp.close.iloc[-1]), float(tp[-1]), pd.Timestamp(datetime.now(timezone.utc)), 0.0)
            row['symbol'] = s
            rows.append(row)
        if start == 0 and str(i) == '0':
            torch.manual_seed(42)
            with torch.inference_mode():
                kps2 = pred.predict_batch([c[cols] for c in ctxs], xs, ys, pred_len=HORIZON, T=1., top_p=.9, sample_count=20, verbose=False)
                point2, _ = tfm.forecast(horizon=HORIZON, inputs=[c.close.to_numpy(np.float32) for c in ctxs])
            same = all(a.equals(b) for a, b in zip(kps, kps2)) and bool(np.array_equal(point, point2))
            Path('reproducibilidad.json').write_text(json.dumps(dict(lote=[f'{s} {c.open_time.iloc[-1].isoformat()}' for (s, _), c in zip(chunk, ctxs)], identico=same), indent=2))
        print(f'shard {i}/{n}: {len(rows)}/{len(mine)} en {time.perf_counter() - t0:.0f} s', flush=True)
    pd.DataFrame(rows, columns=['symbol'] + kt2.COLUMNS).to_csv(out_csv, index=False)


# ---------------------------------------------------------------- analisis
def boot_diff(d, day, rng):
    """Diferencia media pareada y p unilateral por bootstrap de bloques diarios (centrado en H0)."""
    obs = float(d.mean())
    days = np.unique(day)
    pos = {k: np.flatnonzero(day == k) for k in days}
    sums = np.array([d[pos[k]].sum() for k in days])
    cnts = np.array([len(pos[k]) for k in days])
    pick = rng.integers(0, len(days), size=(BOOT_B, len(days)))
    boot = sums[pick].sum(1) / cnts[pick].sum(1)
    p = (int(((boot - obs) >= obs).sum()) + 1) / (BOOT_B + 1)
    return dict(dif_puntos=round(obs * 100, 2), p_unilateral=round(p, 4), n=int(len(d)),
                ic95_puntos=[round(float(np.percentile(boot, 2.5)) * 100, 2), round(float(np.percentile(boot, 97.5)) * 100, 2)])


def pareado(sub, m):
    ar = sub.actual_ret.astype(float)
    h = sub[f'{m}_hit']
    keep = h.isin(['0', '1']) & (ar != 0)
    d = h[keep].astype(int).to_numpy() - (ar[keep] > 0).astype(int).to_numpy()
    return d, sub.loc[keep, 'dia'].to_numpy(), sub.loc[keep, 'symbol'].to_numpy()


def stat(k, n):
    lo, hi = kt2.wilson(k, n)
    return dict(aciertos=k, n=n, tasa=round(k / n, 4) if n else None, ic95=[lo, hi])


def bloque(sub):
    ar = sub.actual_ret.astype(float)
    nz = ar[ar != 0]
    b = dict(n=int(len(sub)), siempre_sube=stat(int((nz > 0).sum()), int(len(nz))))
    pr = sub.persist_ret.astype(float)
    ph = ((pr > 0) == (ar > 0))[(pr != 0) & (ar != 0)].astype(int)
    b['persistencia'] = stat(int(ph.sum()), int(len(ph)))
    for m in kt2.MODELS:
        h = sub[f'{m}_hit']
        h = h[h.isin(['0', '1'])].astype(int)
        b[m] = stat(int(h.sum()), int(len(h)))
    return b


def cmd_unir(data_dir, *shards):
    verificar(data_dir)
    OUT.mkdir(parents=True, exist_ok=True)
    lista, info = todas_las_bases(data_dir)
    frames = {s: load(data_dir, s) for s in SYMBOLS}
    preds = pd.concat([pd.read_csv(s, dtype=str) for s in shards], ignore_index=True)
    key = preds.symbol + ' ' + preds.base_open_utc
    if key.duplicated().any():
        raise ValueError('Bases duplicadas entre shards')
    esperadas = {f'{s} {frames[s].open_time.iloc[i].isoformat()}' for s, i in lista}
    if set(key) != esperadas:
        raise ValueError(f'Bases distintas de las esperadas: {len(set(key) ^ esperadas)} diferencias')
    now = pd.Timestamp(datetime.now(timezone.utc))
    closes = {s: frames[s].set_index('open_time').close for s in SYMBOLS}
    for i in preds.index:
        close = closes[preds.at[i, 'symbol']]
        bt, tg = pd.Timestamp(preds.at[i, 'base_open_utc']), pd.Timestamp(preds.at[i, 'target_open_utc'])
        ar = float(close[tg]) / float(preds.at[i, 'base_close']) - 1
        preds.at[i, 'actual_close4'] = kt2.num(float(close[tg]))
        preds.at[i, 'actual_ret'] = kt2.num(ar)
        for m in kt2.MODELS:
            preds.at[i, f'{m}_hit'] = kt2.sign_hit(float(preds.at[i, f'{m}_ret']), ar)
        prev = bt - HOUR * HORIZON
        preds.at[i, 'persist_ret'] = kt2.num(float(close[bt]) / float(close[prev]) - 1) if prev in close.index else ''
        preds.at[i, 'scored_utc'] = now.isoformat()
    preds = preds.sort_values(['base_open_utc', 'symbol']).reset_index(drop=True)
    base = pd.to_datetime(preds.base_open_utc, utc=True)
    preds['dia'] = base.dt.strftime('%Y-%m-%d')
    preds.to_csv(OUT / 'predicciones.csv', index=False)

    def mcnemar1(m, s, sub=None):
        """McNemar exacto a una cola (H1: el modelo acierta mas que «siempre sube»)."""
        g = preds[preds.symbol == s] if sub is None else sub
        ar = g.actual_ret.astype(float)
        h = g[f'{m}_hit']
        keep = h.isin(['0', '1']) & (ar != 0)
        mh, up = h[keep].astype(int), (ar[keep] > 0).astype(int)
        b, c = int(((mh == 1) & (up == 0)).sum()), int(((mh == 0) & (up == 1)).sum())
        p = sum(math.comb(b + c, k) for k in range(b, b + c + 1)) / 2 ** (b + c) if b + c else 1.0  # sin discordantes: sin evidencia
        n = int(keep.sum())
        dif = round((int(mh.sum()) - int(up.sum())) / n * 100, 2) if n else None
        return dict(modelo=m, activo=s, n=n, solo_modelo=b, solo_sube=c, dif_puntos=dif,
                    acierto=round(mh.mean(), 4) if n else None, p_unilateral=round(p, 6))

    k = mcnemar1(*PRIMARIO)
    pasa = k['p_unilateral'] < 0.05 and k['dif_puntos'] >= 2.0
    g = preds[(preds.symbol == PRIMARIO[1])]
    hk = g.kronos_hit[g.kronos_hit.isin(['0', '1'])].astype(int)
    k['moneda_p_unilateral'] = round(sum(math.comb(len(hk), j) for j in range(int(hk.sum()), len(hk) + 1)) / 2 ** len(hk), 6)
    sec = [mcnemar1(m, s) for m, s in SECUNDARIOS]
    run = 0.0
    for r, i in enumerate(sorted(range(len(sec)), key=lambda i: sec[i]['p_unilateral'])):
        run = max(run, min(1.0, (len(sec) - r) * sec[i]['p_unilateral']))
        sec[i]['p_holm'] = round(run, 6)
    antes = mcnemar1('kronos', PRIMARIO[1], g[pd.to_datetime(g.base_open_utc, utc=True) < CORTE_CONTAMINACION])
    despues = mcnemar1('kronos', PRIMARIO[1], g[pd.to_datetime(g.base_open_utc, utc=True) >= CORTE_CONTAMINACION])
    contaminacion = dict(antes_2025_10=antes['acierto'], desde_2025_10=despues['acierto'],
                         alerta_memoria=bool(antes['acierto'] is not None and despues['acierto'] is not None
                                             and antes['acierto'] - despues['acierto'] > 0.03))
    d, day, _ = pareado(preds, 'kronos')
    robustez = dict(descripcion='4 activos agrupados, bootstrap por bloques de 1 dia (descriptivo)',
                    **boot_diff(d, day, np.random.default_rng(BOOT_SEED)))

    costos = {}
    for s in SYMBOLS:
        ar = preds.loc[preds.symbol == s, 'actual_ret'].astype(float).abs()
        mabs = float(ar.mean())
        costos[s] = dict(media_abs_ret_4h=round(mabs, 5), acierto_minimo_para_cubrir_0_20=round(0.5 + COSTO_IDA_VUELTA / (2 * mabs), 4))

    trimestre = base.dt.year.astype(str) + 'T' + base.dt.quarter.astype(str)
    summary = dict(variant='KT-004', generado_utc=now.isoformat(), profitability_evaluated=False,
                   bases=info, primario=dict(**k, regla='McNemar exacto 1 cola p<0,05 y dif>=2 puntos', pasa=pasa),
                   secundarios_holm=sec, chequeo_contaminacion=contaminacion, robustez_agrupada=robustez,
                   costos_descriptivo=costos, total=bloque(preds),
                   por_activo={s: bloque(g) for s, g in preds.groupby('symbol')},
                   por_trimestre={t: bloque(g) for t, g in preds.groupby(trimestre)},
                   bootstrap=dict(B=BOOT_B, semilla=BOOT_SEED, bloque='dia UTC (los 4 activos juntos)'))
    (OUT / 'resumen.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    f = lambda s: f"{s['aciertos']}/{s['n']} = {s['tasa'] * 100:.1f} %" if s['n'] else 'sin datos'
    pe = summary['por_activo'][PRIMARIO[1]]
    lines = ['# KT-004 — acierto direccional a 4 h (2024-08-01 → 2026-07-31; holdout 2026-08 → 2026-10 sin tocar)', '',
             'Responde «¿predice la dirección?», no «¿es rentable?». Sin costos, deslizamiento ni tamaño de posición.', '',
             f"## Primario: Kronos en ETHUSDT — **{'PASA' if pasa else 'NO PASA'}**", '',
             f"- Kronos {k['acierto'] * 100:.2f} % vs «siempre sube»: {k['dif_puntos']} puntos; McNemar 1 cola p = {k['p_unilateral']} (solo Kronos {k['solo_modelo']}, solo sube {k['solo_sube']}), n = {k['n']}",
             f"- Contra moneda al aire (50 %): p 1 cola = {k['moneda_p_unilateral']}",
             f"- Persistencia: {f(pe['persistencia'])} · siempre sube: {f(pe['siempre_sube'])}",
             '- Regla: p < 0,05 y diferencia ≥ 2 puntos. Pasar no es ventaja ni autoriza operar.', '',
             '## Secundarios (Holm, 5 pruebas)', '']
    lines += [f"- {x['modelo']} {x['activo']}: {x['dif_puntos']} puntos, p {x['p_unilateral']} / Holm {x['p_holm']}" for x in sec]
    lines += ['', '## Chequeo de contaminación (Kronos ETH, descriptivo)', '',
              f"- Antes de 2025-10: {contaminacion['antes_2025_10']} · desde 2025-10: {contaminacion['desde_2025_10']} · alerta: {contaminacion['alerta_memoria']}", '',
              f"## Agrupado 4 activos (descriptivo): {robustez['dif_puntos']} puntos, p bootstrap {robustez['p_unilateral']}", '',
              '## Por activo (Kronos / siempre sube; descriptivo)', '']
    lines += [f"- {s}: {f(b['kronos'])} / {f(b['siempre_sube'])} · acierto mínimo para cubrir 0,20 % ≈ {costos[s]['acierto_minimo_para_cubrir_0_20'] * 100:.1f} %"
              for s, b in summary['por_activo'].items()]
    (OUT / 'resumen.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))


if __name__ == '__main__':
    cmd, *args = sys.argv[1:]
    {'datos': cmd_datos, 'prueba': cmd_prueba, 'shard': cmd_shard, 'unir': cmd_unir}[cmd](*args)
