"""Utilidades Fase 3 — H3 Cross-Sectional Momentum FX. Ver README.md para las
reglas completas del experimento (timing, costos, criterios de supervivencia).

No corre ni carga el período de Test (2020-2026) — load_dev_data() corta en
2019-12-31, igual que en Fase 2.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FASE3_DIR = Path(__file__).resolve().parent
DATA_DIR = FASE3_DIR / "data"
RESULTADOS_DIR = FASE3_DIR / "resultados"

DOWNLOAD_START = "2003-01-01"
DOWNLOAD_END = "2026-08-08"

# (ticker yfinance, "direct"|"inverse")
TICKERS = {
    "EUR": ("EURUSD=X", "direct"),
    "GBP": ("GBPUSD=X", "direct"),
    "AUD": ("AUDUSD=X", "direct"),
    "NZD": ("NZDUSD=X", "direct"),
    "CHF": ("USDCHF=X", "inverse"),
    "JPY": ("USDJPY=X", "inverse"),
    "CAD": ("USDCAD=X", "inverse"),
    "NOK": ("USDNOK=X", "inverse"),
    "SEK": ("USDSEK=X", "inverse"),
}

PIP_SIZE = {"EUR": 0.0001, "GBP": 0.0001, "AUD": 0.0001, "NZD": 0.0001,
            "CHF": 0.0001, "JPY": 0.01, "CAD": 0.0001, "NOK": 0.0001, "SEK": 0.0001}

PIPS_PER_SIDE = {"EUR": 2, "GBP": 2, "JPY": 2, "CHF": 2, "AUD": 2, "CAD": 2,
                  "NZD": 4, "NOK": 4, "SEK": 4}

TRAIN = ("2005-01-01", "2014-12-31")
VALIDATION = ("2015-01-01", "2019-12-31")
TEST = ("2020-01-01", "2026-08-08")
DEV_CUTOFF = VALIDATION[1]

N_VARIANTS = [20, 60, 120]
N_WINNERS = 3
N_LOSERS = 3
WEIGHT = 1 / 6

QUALITY_PERIOD = ("2005-01-01", "2019-12-31")
MAX_MISSING_PCT = 0.10


def download_all(force=False):
    """Descarga (o carga de caché) cada ticker y guarda en data/{MONEDA}_d1.csv."""
    import yfinance as yf

    frames = {}
    for moneda, (ticker, _) in TICKERS.items():
        path = DATA_DIR / f"{moneda}_d1.csv"
        if path.exists() and not force:
            df = pd.read_csv(path, parse_dates=["Date"]).set_index("Date")
        else:
            print(f"[INFO] Descargando {moneda} ({ticker}) {DOWNLOAD_START}..{DOWNLOAD_END}")
            raw = yf.download(ticker, start=DOWNLOAD_START, end=DOWNLOAD_END,
                               auto_adjust=False, progress=False)
            if raw.empty:
                raise RuntimeError(f"yfinance no devolvió datos para {ticker} ({moneda})")
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            df = raw[["Open", "High", "Low", "Close"]].copy()
            df.index.name = "Date"
            df = df[~df.index.duplicated(keep="first")].sort_index()
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(path)
        frames[moneda] = df
    return frames


def check_data_quality(frames, period=QUALITY_PERIOD, max_missing_pct=MAX_MISSING_PCT):
    """Compara días hábiles esperados (calendario Mon-Fri) vs filas presentes por
    moneda en el período dado. NO imputa nada — solo reporta y señala qué pares
    superan el umbral de faltantes.
    """
    start, end = period
    expected = pd.bdate_range(start, end)
    n_expected = len(expected)

    rows = []
    flagged = []
    for moneda, df in frames.items():
        present = df.loc[(df.index >= start) & (df.index <= end)]
        n_present = len(present)
        missing_pct = 1 - n_present / n_expected
        rows.append(dict(moneda=moneda, dias_habiles_esperados=n_expected,
                          dias_presentes=n_present, pct_faltante=missing_pct * 100))
        if missing_pct > max_missing_pct:
            flagged.append(moneda)

    report = pd.DataFrame(rows).sort_values("pct_faltante", ascending=False)
    return report, flagged


def load_dev_data(force_download=False):
    """Descarga/carga las 9 series, corre el chequeo de calidad, y devuelve
    (frames recortados a <=2019-12-31, reporte de calidad). No lanza excepción
    por datos faltantes — quien llama decide qué hacer con `flagged`.
    """
    frames = download_all(force=force_download)
    report, flagged = check_data_quality(frames)
    dev_frames = {m: df.loc[:DEV_CUTOFF].copy() for m, df in frames.items()}
    return dev_frames, report, flagged


# ─────────────────────────────────────────────────────────────────────────
# Motor de backtest — H3 Cross-Sectional Momentum
#
# Decisión de datos (2026-08-08, confirmada por el usuario): AUD no tiene
# datos en yfinance antes de 2006-05-16 (hueco contiguo de 16 meses al
# arranque de Train, no detectado por el umbral agregado de 10% porque no
# está disperso). Se mantiene el universo de 9 monedas, pero AUD queda
# excluida del ranking en cualquier mes en que no tenga N días reales de
# historia para esa variante — nunca se fabrica ni se imputa un retorno.
# Ver README.md.
# ─────────────────────────────────────────────────────────────────────────

ALIGN_TOLERANCE_DAYS = 5  # tolerancia para alinear cada moneda a la fecha exacta de rebalanceo


def compute_daily_returns(frames):
    """r_i,t: retorno de la moneda i vs USD, en el calendario NATIVO de cada
    moneda (sin reindexar ni fabricar filas). Pares inversos con signo
    invertido, tal como pide la especificación.
    """
    returns = {}
    for moneda, (_, kind) in TICKERS.items():
        close = frames[moneda]["Close"]
        r = close.pct_change()
        if kind == "inverse":
            r = -r
        returns[moneda] = r.dropna()
    return returns


def compute_lookback_returns(returns, n):
    """Return_acum_i = Product(1+r_t) - 1 sobre las últimas N observaciones
    REALES de esa moneda (calendario nativo). NaN si no hay N observaciones
    reales todavía (min_periods=n) — así se excluye, nunca se imputa.
    """
    out = {}
    for moneda, r in returns.items():
        out[moneda] = r.rolling(n, min_periods=n).apply(
            lambda x: np.prod(1.0 + x) - 1.0, raw=True)
    return out


def get_rebalance_dates(start, end):
    """Último día hábil de cada mes calendario, calendario Mon-Fri estándar."""
    idx = pd.bdate_range(start, end)
    s = pd.Series(idx, index=idx)
    return pd.DatetimeIndex(s.resample("ME").last().dropna().values)


def align_to_rebalance(series_dict, rebal_dates, tolerance_days=ALIGN_TOLERANCE_DAYS):
    """Alinea cada serie (indexada en su calendario nativo) a las fechas de
    rebalanceo, usando el último valor real disponible dentro de una
    tolerancia de `tolerance_days`. NaN si no hay ningún valor real cerca
    (p. ej. AUD antes de 2006-05-16) — nunca se fabrica un valor.
    """
    aligned = {}
    for moneda, series in series_dict.items():
        s = series.sort_index()
        s = s[~s.index.duplicated(keep="last")]
        aligned[moneda] = s.reindex(rebal_dates, method="ffill",
                                     tolerance=pd.Timedelta(days=tolerance_days))
    return pd.DataFrame(aligned)


def rank_and_signal_frame(ret_acum_df, n_winners=N_WINNERS, n_losers=N_LOSERS):
    """Para cada fecha de rebalanceo: rankea las monedas con dato válido ese
    mes, LONG top n_winners, SHORT bottom n_losers, resto (incluida
    cualquier moneda sin dato disponible) en 0.
    """
    signal = pd.DataFrame(0.0, index=ret_acum_df.index, columns=ret_acum_df.columns)
    ranking = pd.DataFrame(np.nan, index=ret_acum_df.index, columns=ret_acum_df.columns)

    for fecha, row in ret_acum_df.iterrows():
        valid = row.dropna().sort_values(ascending=False)
        ranking.loc[fecha, valid.index] = range(1, len(valid) + 1)
        if len(valid) < n_winners + n_losers:
            print(f"[WARN] {fecha.date()}: solo {len(valid)} monedas con dato válido "
                  f"(< {n_winners + n_losers} necesarias) — rebalanceo con menos de "
                  f"{n_winners}/{n_losers}")
            continue
        signal.loc[fecha, valid.index[:n_winners]] = 1.0
        signal.loc[fecha, valid.index[-n_losers:]] = -1.0

    eligible = ret_acum_df.notna()
    return signal, ranking, eligible


def build_position_held(signal_df, master_daily_index):
    """Posición sostenida día a día. La señal decidida en la fecha de
    rebalanceo t_m recién es efectiva desde el próximo día hábil (t_m+1) —
    mismo patrón shift(1)+ffill que Fase 2, aplicado a las 9 columnas.
    """
    daily = signal_df.reindex(master_daily_index)
    return daily.shift(1).ffill().fillna(0.0)


def compute_rebalance_costs(signal_df, position_held, close_at_rebal):
    """Costo por transición en cada fecha de rebalanceo, por moneda.
    Devuelve (costo_por_moneda_df, lados_pagados_df, costo_total_portfolio).
    """
    old_signal = position_held.reindex(signal_df.index)
    new_signal = signal_df

    diff = new_signal - old_signal
    lados = pd.DataFrame(0.0, index=signal_df.index, columns=signal_df.columns)
    lados[(old_signal == 0) & (new_signal != 0)] = 1.0
    lados[(old_signal != 0) & (new_signal == 0)] = 1.0
    lados[(old_signal == 1) & (new_signal == -1)] = 2.0
    lados[(old_signal == -1) & (new_signal == 1)] = 2.0
    # sin cambio (incluye 0->0 y misma señal repetida) queda en 0.0

    cost_per_side_pct = pd.DataFrame(index=signal_df.index, columns=signal_df.columns, dtype=float)
    for moneda in signal_df.columns:
        cost_per_side_pct[moneda] = (PIPS_PER_SIDE[moneda] * PIP_SIZE[moneda]
                                      / close_at_rebal[moneda])

    costo_por_moneda = (lados * cost_per_side_pct).fillna(0.0)
    costo_total = (costo_por_moneda * WEIGHT).sum(axis=1)
    return costo_por_moneda, lados, costo_total


def run_h3_variant(frames, n, warmup_start="2004-01-01"):
    """Corre H3 completo (Train+Validation) para una variante N. Devuelve un
    dict con todas las series diarias/de rebalanceo necesarias para reportar
    cualquier sub-período después (mismo patrón que utils.run_backtest en
    Fase 2).
    """
    returns = compute_daily_returns(frames)
    ret_acum = compute_lookback_returns(returns, n)

    rebal_dates = get_rebalance_dates(warmup_start, DEV_CUTOFF)
    ret_acum_at_rebal = align_to_rebalance(ret_acum, rebal_dates)
    close_at_rebal = align_to_rebalance({m: frames[m]["Close"] for m in frames}, rebal_dates)

    signal_df, ranking_df, eligible_df = rank_and_signal_frame(ret_acum_at_rebal)

    master_daily = pd.bdate_range(warmup_start, DEV_CUTOFF)
    position_held = build_position_held(signal_df, master_daily)

    costo_por_moneda, lados, costo_total_rebal = compute_rebalance_costs(
        signal_df, position_held, close_at_rebal)

    returns_daily = pd.DataFrame({m: returns[m] for m in frames}).reindex(master_daily)
    contrib = position_held.mul(returns_daily)
    ret_gross_daily = WEIGHT * contrib.sum(axis=1, skipna=True)

    ret_net_daily = ret_gross_daily.copy()
    common_dates = ret_net_daily.index.intersection(costo_total_rebal.index)
    ret_net_daily.loc[common_dates] = ret_net_daily.loc[common_dates] - costo_total_rebal.loc[common_dates]

    return dict(
        label=f"H3_N{n}", n=n, frames=frames, master_daily=master_daily,
        signal_df=signal_df, ranking_df=ranking_df, eligible_df=eligible_df,
        ret_acum_at_rebal=ret_acum_at_rebal, close_at_rebal=close_at_rebal,
        position_held=position_held, costo_por_moneda=costo_por_moneda, lados=lados,
        costo_total_rebal=costo_total_rebal, ret_gross_daily=ret_gross_daily,
        ret_net_daily=ret_net_daily,
    )


def _annual_table(ret_gross, ret_net, costo_total_rebal):
    years = sorted(set(ret_net.index.year))
    rows = []
    for y in years:
        g = ret_gross[ret_gross.index.year == y]
        n = ret_net[ret_net.index.year == y]
        c = costo_total_rebal[costo_total_rebal.index.year == y]
        rows.append(dict(
            year=y,
            retorno_bruto_pct=((1 + g).prod() - 1) * 100,
            costos_pct=c.sum() * 100,
            retorno_neto_pct=((1 + n).prod() - 1) * 100,
        ))
    tabla = pd.DataFrame(rows)
    total_abs = tabla["retorno_neto_pct"].abs().sum()
    tabla["pct_del_total_absoluto"] = (tabla["retorno_neto_pct"].abs() / total_abs * 100
                                        if total_abs > 0 else np.nan)
    return tabla


def _turnover_series(lados, rebal_dates_in_period):
    if len(rebal_dates_in_period) == 0:
        return pd.Series(dtype=float)
    sub = lados.loc[lados.index.isin(rebal_dates_in_period)]
    return (sub * WEIGHT).sum(axis=1) * 100


def _bucket_composition(signal_row):
    winners = sorted(signal_row[signal_row == 1.0].index.tolist())
    losers = sorted(signal_row[signal_row == -1.0].index.tolist())
    middle = sorted(signal_row[signal_row == 0.0].index.tolist())
    return dict(winners=winners, losers=losers, middle=middle)


def report_h3_period(result, period, out_dir, apply_survival_criteria):
    start, end = period
    label = result["label"]
    out_dir.mkdir(parents=True, exist_ok=True)

    mask_daily = (result["ret_net_daily"].index >= start) & (result["ret_net_daily"].index <= end)
    ret_gross = result["ret_gross_daily"].loc[mask_daily]
    ret_net = result["ret_net_daily"].loc[mask_daily]

    equity = 100.0 * (1 + ret_net).cumprod()
    equity_gross = 100.0 * (1 + ret_gross).cumprod()

    rebal_mask = (result["costo_total_rebal"].index >= start) & (result["costo_total_rebal"].index <= end)
    rebal_dates_period = result["costo_total_rebal"].index[rebal_mask]
    n_rebalanceos = len(rebal_dates_period)

    total_return_bruto = (equity_gross.iloc[-1] / equity_gross.iloc[0] - 1) * 100 if len(equity_gross) else np.nan
    total_return_neto = (equity.iloc[-1] / equity.iloc[0] - 1) * 100 if len(equity) else np.nan
    n_days = len(ret_net)
    cagr_neto = (((equity.iloc[-1] / equity.iloc[0]) ** (252 / n_days) - 1) * 100
                 if len(equity) > 1 and equity.iloc[0] > 0 else np.nan)
    vol_anual = ret_net.std(ddof=1) * np.sqrt(252) * 100 if len(ret_net) > 1 else np.nan
    sharpe = (ret_net.mean() / ret_net.std(ddof=1) * np.sqrt(252)
              if len(ret_net) > 1 and ret_net.std(ddof=1) > 0 else np.nan)
    dd = equity / equity.cummax() - 1
    max_dd = -dd.min() * 100 if len(dd) else np.nan
    costos_totales = result["costo_total_rebal"].loc[rebal_mask].sum() * 100

    monthly_net = (1 + ret_net).resample("ME").prod() - 1
    pct_meses_pos = (monthly_net > 0).mean() * 100 if len(monthly_net) else np.nan

    turnover = _turnover_series(result["lados"], rebal_dates_period)
    turnover_prom = turnover.mean() if len(turnover) else np.nan

    tabla_anual = _annual_table(ret_gross, ret_net, result["costo_total_rebal"].loc[rebal_mask])
    tabla_anual.to_csv(out_dir / f"{label}_retorno_anual.csv", index=False)

    first_rebal_in_period = rebal_dates_period[0] if len(rebal_dates_period) else None
    composicion_inicial = (_bucket_composition(result["signal_df"].loc[first_rebal_in_period])
                            if first_rebal_in_period is not None else None)

    metrics = dict(
        label=label, periodo=f"{start}..{end}",
        retorno_bruto_pct=total_return_bruto, retorno_neto_pct=total_return_neto,
        cagr_neto_pct=cagr_neto, sharpe_anualizado=sharpe, volatilidad_anual_pct=vol_anual,
        max_drawdown_pct=max_dd, pct_meses_positivos=pct_meses_pos,
        n_rebalanceos=n_rebalanceos, turnover_promedio_mensual_pct=turnover_prom,
        costos_acumulados_pct=costos_totales,
        composicion_inicial=str(composicion_inicial),
    )

    if apply_survival_criteria:
        crit_a = sharpe > 0.50 if pd.notna(sharpe) else False
        crit_b = total_return_neto > 0 if pd.notna(total_return_neto) else False
        n_years_pos = (tabla_anual["retorno_neto_pct"] > 0).sum()
        crit_c = n_years_pos >= 3
        max_abs_year = tabla_anual["retorno_neto_pct"].abs().max()
        sum_abs_year = tabla_anual["retorno_neto_pct"].abs().sum()
        concentracion_d = max_abs_year / sum_abs_year if sum_abs_year > 0 else np.nan
        crit_d = concentracion_d <= 0.50 if pd.notna(concentracion_d) else False
        sobrevive = crit_a and crit_b and crit_c and crit_d
        metrics.update(dict(
            criterio_A_sharpe_gt_050=crit_a, criterio_B_retorno_neto_gt_0=crit_b,
            criterio_C_annos_pos=f"{n_years_pos}/5", criterio_C_ok=crit_c,
            criterio_D_concentracion=concentracion_d, criterio_D_ok=crit_d,
            veredicto="SOBREVIVE" if sobrevive else "ELIMINADA",
        ))

    lines = [f"{k}: {v}" for k, v in metrics.items()]
    (out_dir / f"{label}_metrics.txt").write_text("\n".join(lines), encoding="utf-8")

    summary_path = out_dir / "resumen.csv"
    row = pd.DataFrame([metrics])
    if summary_path.exists():
        existing = pd.read_csv(summary_path)
        existing = existing[existing["label"] != label]
        row = pd.concat([existing, row], ignore_index=True)
    row.to_csv(summary_path, index=False)

    print(f"[{label}] {metrics['periodo']}: Sharpe={sharpe:.2f} RetNeto={total_return_neto:.2f}% "
          f"MaxDD={max_dd:.2f}% rebalanceos={n_rebalanceos}"
          + (f" -> {metrics.get('veredicto')}" if apply_survival_criteria else ""))

    return metrics, equity, tabla_anual


def write_audit_table(result, period, out_path, n_dates=6):
    start, end = period
    signal_df, ranking_df = result["signal_df"], result["ranking_df"]
    position_held = result["position_held"]
    ret_acum = result["ret_acum_at_rebal"]
    lados, costo_por_moneda = result["lados"], result["costo_por_moneda"]

    rebal_in_period = signal_df.index[(signal_df.index >= start) & (signal_df.index <= end)][:n_dates]

    rows = []
    for fecha in rebal_in_period:
        old_signal = position_held.reindex([fecha]).iloc[0]
        for moneda in signal_df.columns:
            rows.append(dict(
                fecha=fecha.date(), moneda=moneda,
                ret_lookback_usd=ret_acum.loc[fecha, moneda],
                ranking=ranking_df.loc[fecha, moneda],
                senal_anterior=old_signal[moneda],
                senal_nueva=signal_df.loc[fecha, moneda],
                cambio=lados.loc[fecha, moneda],
                costo_pct=costo_por_moneda.loc[fecha, moneda],
            ))
    tabla = pd.DataFrame(rows)
    tabla.to_csv(out_path, index=False)
    return tabla
