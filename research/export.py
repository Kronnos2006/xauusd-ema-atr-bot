"""Arma la carpeta `experiments/experiment_<fecha>_<NNN>/` de un experimento
con los 7 artefactos pedidos: config.yaml, metrics.json, trades.csv,
equity.csv, log.txt, summary.md, metadata.json.

`trades_df` se recibe SIN neto de spread (salida cruda de `backtest`/
`correr_fold`) -- este módulo llama a `metrics.descontar_spread` una vez y
esa es la fuente de verdad tanto para trades.csv (que incluye la columna
resultado_R_neto) como para equity.csv, coherente con que todas las
métricas del proyecto se evalúan netas de spread.
"""

import json
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

from research import metrics

DEFAULT_EXPERIMENTS_DIR = Path(__file__).resolve().parent.parent / "experiments"


def _git_commit_hash():
    try:
        repo_root = Path(__file__).resolve().parent.parent
        resultado = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root,
            capture_output=True, text=True, check=True,
        )
        return resultado.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _siguiente_numero(base_dir, fecha_str):
    if not base_dir.exists():
        return 1
    existentes = list(base_dir.glob(f"experiment_{fecha_str}_*"))
    return len(existentes) + 1


def _construir_equity(trades_neto_df):
    ordenado = trades_neto_df.sort_values("time_salida").reset_index(drop=True)
    equity = ordenado[["time_salida", "resultado_R_neto"]].copy()
    equity["equity"] = 1.0 + equity["resultado_R_neto"].cumsum()
    return equity


def _render_summary(cfg, metricas, resultados_folds):
    lineas = [
        f"# Experimento — {cfg['symbol']} {cfg['timeframe']} — estrategia `{cfg['strategy']}`",
        "",
        f"Rango de datos: {cfg['date_from']} -> {cfg['date_to']} | N_FOLDS: {cfg['n_folds']}",
        f"EMA {cfg['ema_fast']}/{cfg['ema_slow']}/{cfg['ema_trend']} | ATR({cfg['atr_period']}) x {cfg['sl_atr_mult']} | "
        f"R:R 1:{cfg['rr_ratio']} | spread: {cfg['spread_puntos']}pts | filtro sesión: {cfg['use_session_filter']}",
        "",
        "## Métricas (TEST agregado, neto de spread)",
        "",
        "| Métrica | Valor |",
        "|---|---|",
    ]
    for clave, valor in metricas.items():
        valor_fmt = f"{valor:.4f}" if isinstance(valor, float) else str(valor)
        lineas.append(f"| {clave} | {valor_fmt} |")

    if resultados_folds:
        lineas += ["", "## Detalle por fold", "", "| Fold | R:R | Filtro sesión | Trades | R neto |", "|---|---|---|---|---|"]
        for r in resultados_folds:
            lineas.append(
                f"| {r['fold']} | 1:{r['rr']} | {'CON' if r['filtro_sesion'] else 'SIN'} | "
                f"{r['n_trades_test']} | {r['r_neto_test']} |"
            )

    return "\n".join(lineas) + "\n"


def escribir_experimento(cfg, trades_df, metricas, data_hashes, log_text="", resultados_folds=None, base_dir=None):
    """Crea `experiment_<fecha>_<NNN>/` con los 7 artefactos y devuelve su Path.

    `data_hashes` es un dict {label: sha256} (p.ej. {"M15": "...", "H1": "..."}).
    """
    base_dir = Path(base_dir) if base_dir is not None else DEFAULT_EXPERIMENTS_DIR
    fecha_str = date.today().isoformat()
    numero = _siguiente_numero(base_dir, fecha_str)
    carpeta = base_dir / f"experiment_{fecha_str}_{numero:03d}"
    carpeta.mkdir(parents=True)

    trades_neto = metrics.descontar_spread(trades_df) if not trades_df.empty else trades_df.assign(resultado_R_neto=[])

    with open(carpeta / "config.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)

    trades_neto.to_csv(carpeta / "trades.csv", index=False)

    if not trades_df.empty:
        _construir_equity(trades_neto).to_csv(carpeta / "equity.csv", index=False)
    else:
        (carpeta / "equity.csv").write_text("time_salida,resultado_R_neto,equity\n", encoding="utf-8")

    with open(carpeta / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metricas, f, indent=2, default=str)

    metadata = {
        "git_commit": _git_commit_hash(),
        "data_hashes": data_hashes,
        "params": cfg,
        "seed": None,  # sin uso de RNG en el pipeline hoy; reservado para una estrategia futura que sí lo necesite
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(carpeta / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, default=str)

    (carpeta / "log.txt").write_text(log_text, encoding="utf-8")
    (carpeta / "summary.md").write_text(_render_summary(cfg, metricas, resultados_folds), encoding="utf-8")

    return carpeta
