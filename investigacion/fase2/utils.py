"""Motor de backtest compartido para H1 (momentum) y H2 (Donchian) — Fase 2 Invenio.

Reglas de ejecución (ver README.md para el detalle completo):
- La señal de cada hipótesis se decide con información disponible al cierre de la
  barra t (Close[t], o High/Low hasta t-1 en H2) y se ejecuta al Open de t+1 —
  sin look-ahead.
- Sizing: no hay stop-loss definido por H1/H2 (la única salida es señal opuesta),
  así que "riesgo fijo 1% de equity por trade" se interpreta como notional
  expuesto = 1% de equity (no como distancia a un stop). Esto solo afecta la
  magnitud de Max Drawdown % y Retorno total % — el Profit Factor, Win Rate,
  expectancy y Sharpe son invariantes a este factor de escala (ver informe final).
- El archivo fuente (historial/eurusd_d1.csv, datos reales MT5) se congela una
  copia en data/eurusd_d1.csv la primera vez que corre el script, para que la
  Fase 2 no dependa de que ese archivo siga existiendo o sin cambios más adelante.
"""
import shutil
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FASE2_DIR = Path(__file__).resolve().parent
REPO_ROOT = FASE2_DIR.parent.parent
DATA_DIR = FASE2_DIR / "data"
RESULTADOS_DIR = FASE2_DIR / "resultados"
SOURCE_CSV = REPO_ROOT / "historial" / "eurusd_d1.csv"
LOCAL_CSV = DATA_DIR / "eurusd_d1.csv"

SPREAD = 0.0001
SLIPPAGE = 0.00005
COST_PER_SIDE = SPREAD + SLIPPAGE       # 0.00015
COST_ROUND_TRIP = COST_PER_SIDE * 2     # 0.0003

RISK_FRACTION = 0.01  # 1% de equity expuesto por trade (ver docstring del módulo)

TRAIN = ("2005-01-01", "2014-12-31")
VALIDATION = ("2015-01-01", "2019-12-31")
TEST = ("2020-01-01", "2026-08-08")

DEV_CUTOFF = VALIDATION[1]  # nunca cargar/computar más allá de esta fecha en Fase 2


def load_dev_data():
    """Carga EURUSD D1 hasta el cierre de Validation (2019-12-31) inclusive.

    No devuelve ninguna fila de 2020 en adelante — el período de Test queda
    fuera del alcance de este módulo por diseño, no solo por disciplina de uso.
    """
    if not LOCAL_CSV.exists():
        if not SOURCE_CSV.exists():
            df = _load_yfinance()
        else:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy(SOURCE_CSV, LOCAL_CSV)
            df = _read_local_csv()
    else:
        df = _read_local_csv()

    df = df[~df.index.duplicated(keep="first")].sort_index()
    _check_gaps(df)
    return df.loc[:DEV_CUTOFF].copy()


def _read_local_csv():
    df = pd.read_csv(LOCAL_CSV, parse_dates=["time"])
    df = df.rename(columns={"time": "Date", "open": "Open", "high": "High",
                             "low": "Low", "close": "Close"})
    return df[["Date", "Open", "High", "Low", "Close"]].set_index("Date")


def _load_yfinance():
    import yfinance as yf
    print("[INFO] historial/eurusd_d1.csv no encontrado — descargando de yfinance.")
    df = yf.download("EURUSD=X", start="2000-01-01", end="2020-01-01",
                      auto_adjust=False, progress=False)
    df = df[["Open", "High", "Low", "Close"]]
    df.index.name = "Date"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(LOCAL_CSV)
    return df


def _check_gaps(df, max_gap_days=5):
    gaps = df.index.to_series().diff().dt.days
    big_gaps = gaps[gaps > max_gap_days]
    if len(big_gaps):
        print(f"[WARN] {len(big_gaps)} huecos > {max_gap_days} días en los datos D1:")
        for date, gap in big_gaps.items():
            print(f"  {date.date()}: hueco de {int(gap)} días")


def run_backtest(df_dev, signal, label):
    """Corre el backtest sobre la serie completa (Train+Validation) y devuelve
    un dict con todo lo necesario para reportar cualquier sub-período después.
    """
    sig = signal.reindex(df_dev.index).ffill().fillna(0)

    pos = sig.shift(1).fillna(0)              # posición sostenida durante la barra t
    prev_pos = pos.shift(1).fillna(0)
    is_flip = pos != prev_pos

    ret_intraday = df_dev["Close"] / df_dev["Open"] - 1
    ret_close = df_dev["Close"] / df_dev["Close"].shift(1) - 1
    ret_gross = np.where(is_flip, pos * ret_intraday, pos * ret_close)

    first_entry = is_flip.to_numpy() & (prev_pos.to_numpy() == 0) & (pos.to_numpy() != 0)
    reentry = is_flip.to_numpy() & (prev_pos.to_numpy() != 0) & (pos.to_numpy() != 0)
    cost = np.where(first_entry, COST_PER_SIDE, np.where(reentry, COST_ROUND_TRIP, 0.0))
    ret_net = pd.Series(ret_gross - cost, index=df_dev.index)

    trades = _extract_trades(df_dev, pos)

    return {"label": label, "df_dev": df_dev, "pos": pos, "ret_net": ret_net, "trades": trades}


def _extract_trades(df, pos):
    dates = df.index
    pos_vals = pos.to_numpy()
    n = len(pos_vals)
    rows = []
    i = 0
    while i < n:
        if pos_vals[i] == 0:
            i += 1
            continue
        direction = pos_vals[i]
        entry_idx = i
        j = i
        while j + 1 < n and pos_vals[j + 1] == direction:
            j += 1
        exit_idx = j + 1 if (j + 1 < n) else None

        entry_raw = df["Open"].iloc[entry_idx]
        entry_eff = entry_raw + direction * COST_PER_SIDE * entry_raw

        if exit_idx is not None:
            exit_raw = df["Open"].iloc[exit_idx]
            exit_eff = exit_raw - direction * COST_PER_SIDE * exit_raw
            closed = True
            exit_date = dates[exit_idx]
        else:
            exit_eff = df["Close"].iloc[-1]
            closed = False
            exit_date = dates[-1]

        ret_pct = direction * (exit_eff / entry_eff - 1)
        pips = direction * (exit_eff - entry_eff) * 10000

        rows.append(dict(entry_date=dates[entry_idx], exit_date=exit_date,
                          direction=int(direction), return_pct=ret_pct, pips=pips,
                          closed=closed))
        i = exit_idx if exit_idx is not None else n

    return pd.DataFrame(rows, columns=["entry_date", "exit_date", "direction",
                                        "return_pct", "pips", "closed"])


def report_period(result, period, out_dir):
    """Filtra el resultado completo (Train+Validation) a un sub-período y
    escribe métricas + gráficos a out_dir. Devuelve el dict de métricas.
    """
    start, end = period
    label = result["label"]
    df_dev, pos, ret_net_full, trades_full = (
        result["df_dev"], result["pos"], result["ret_net"], result["trades"])

    mask = (df_dev.index >= start) & (df_dev.index <= end)
    ret_period = ret_net_full.loc[mask]
    eq_ret = RISK_FRACTION * ret_period
    equity = 100.0 * (1 + eq_ret).cumprod()

    trades_period = trades_full[
        (trades_full["entry_date"] >= pd.Timestamp(start))
        & (trades_full["entry_date"] <= pd.Timestamp(end))
    ]
    closed = trades_period[trades_period["closed"]]
    n_open_excluded = (~trades_period["closed"]).sum()

    n_trades = len(closed)
    if n_trades == 0:
        pf = wr = exp_pct = exp_pips = np.nan
    else:
        wins = closed[closed["return_pct"] > 0]
        losses = closed[closed["return_pct"] <= 0]
        gross_win = wins["return_pct"].sum()
        gross_loss = -losses["return_pct"].sum()
        pf = gross_win / gross_loss if gross_loss > 0 else np.inf
        wr = len(wins) / n_trades
        exp_pct = closed["return_pct"].mean()
        exp_pips = closed["pips"].mean()

    dd = equity / equity.cummax() - 1
    max_dd = -dd.min() * 100 if len(dd) else np.nan
    sharpe = (eq_ret.mean() / eq_ret.std(ddof=1) * np.sqrt(252)
              if eq_ret.std(ddof=1) not in (0, np.nan) and len(eq_ret) > 1 else np.nan)
    total_return = (equity.iloc[-1] / equity.iloc[0] - 1) * 100 if len(equity) else np.nan

    if pf < 0.90:
        veredicto = "fuerte candidato a eliminar (PF < 0.90)"
    elif pf <= 1.10:
        veredicto = "inconcluso (PF 0.90-1.10)"
    elif pf <= 1.20:
        veredicto = "candidato a investigación (PF > 1.10)"
    else:
        veredicto = "candidato fuerte (PF > 1.20)" if exp_pct > 0 else "candidato a investigación (PF > 1.20 pero expectancy <= 0)"

    metrics = dict(
        label=label, periodo=f"{start}..{end}", trades=n_trades,
        trades_abiertos_excluidos=int(n_open_excluded),
        win_rate=wr, profit_factor=pf, expectancy_pct=exp_pct, expectancy_pips=exp_pips,
        max_drawdown_pct=max_dd, sharpe_anualizado=sharpe, retorno_total_pct=total_return,
        veredicto=veredicto,
    )

    _write_report(metrics, equity, closed, out_dir, label)
    return metrics


def _write_report(metrics, equity, closed_trades, out_dir, label):
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = [f"{k}: {v}" for k, v in metrics.items()]
    (out_dir / f"{label}_metrics.txt").write_text("\n".join(lines), encoding="utf-8")

    summary_path = out_dir / "resumen.csv"
    row = pd.DataFrame([metrics])
    if summary_path.exists():
        existing = pd.read_csv(summary_path)
        existing = existing[existing["label"] != label]
        row = pd.concat([existing, row], ignore_index=True)
    row.to_csv(summary_path, index=False)

    if len(equity):
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(equity.index, equity.values)
        ax.set_title(f"{label} — Equity curve")
        ax.set_ylabel("Equity (base 100)")
        fig.tight_layout()
        fig.savefig(out_dir / f"{label}_equity.png", dpi=100)
        plt.close(fig)

        by_year_first = equity.groupby(equity.index.year).first()
        by_year_last = equity.groupby(equity.index.year).last()
        ann_table = (by_year_last / by_year_first - 1) * 100
        ann_table.name = "retorno_anual_pct"
        ann_table.to_csv(out_dir / f"{label}_retorno_anual.csv")

    if len(closed_trades):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(closed_trades["return_pct"] * 100, bins=40)
        ax.set_title(f"{label} — Distribución de retornos por trade (%)")
        ax.set_xlabel("Retorno por trade (%)")
        fig.tight_layout()
        fig.savefig(out_dir / f"{label}_dist_trades.png", dpi=100)
        plt.close(fig)

    print(f"[{label}] {metrics['periodo']}: trades={metrics['trades']} "
          f"(+{metrics['trades_abiertos_excluidos']} abierto sin cerrar) "
          f"PF={metrics['profit_factor']:.3f} WR={_fmt_pct(metrics['win_rate'])} "
          f"exp={metrics['expectancy_pips']:.2f}pips MaxDD={metrics['max_drawdown_pct']:.2f}% "
          f"Sharpe={metrics['sharpe_anualizado']:.2f} Ret={metrics['retorno_total_pct']:.2f}% "
          f"-> {metrics['veredicto']}")


def _fmt_pct(x):
    return f"{x*100:.1f}%" if pd.notna(x) else "n/a"
