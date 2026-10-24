"""KT-002: verificación de integridad, SOLO LECTURA (orden ORION, 2026-10-23).

No escribe en data/kt002 ni cambia nada de la medición. Comprueba:
  1. registros únicos (una fila por vela base) y objetivo exactamente a 4 h;
  2. continuidad horaria (lista de horas omitidas);
  3. aciertos recalculados desde los cierres (misma regla sign_hit del script);
  4. resumen.json reproducible: se recalcula con la función summarize() original en un directorio
     temporal (KT002_OUT) y se compara campo por campo con el publicado;
  5. historial solo anexado (git): ninguna fila desaparece, los campos de pronóstico nunca cambian y
     los de puntuación solo pasan de vacío a lleno.
Uso: python3 tools/kt002_integridad.py [--sin-historial]   → JSON; código 1 si hay violaciones.
"""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "kt002"
CSV_REL = "data/kt002/predicciones.csv"
PRONOSTICO = ["run_utc", "base_open_utc", "base_close", "target_open_utc", "kronos_close4", "timesfm_close4",
              "kt001_close4", "kronos_ret", "timesfm_ret", "kt001_ret", "elapsed_s"]
PUNTUACION = ["actual_close4", "actual_ret", "kronos_hit", "timesfm_hit", "kt001_hit", "scored_utc"]
MODELOS = ("kronos", "timesfm", "kt001")


def _vacio(x) -> bool:
    return x is None or (isinstance(x, float) and pd.isna(x)) or str(x) == ""


def actuales(df: pd.DataFrame, kt) -> list[str]:
    v = []
    b = pd.to_datetime(df.base_open_utc, utc=True)
    if b.duplicated().any():
        v.append(f"bases duplicadas: {sorted(df.base_open_utc[b.duplicated()].tolist())}")
    t = pd.to_datetime(df.target_open_utc, utc=True)
    malos = df.base_open_utc[(t - b) != pd.Timedelta(hours=4)]
    if len(malos):
        v.append(f"objetivo distinto de 4 h en bases {malos.tolist()}")
    for i, r in df[~df.actual_ret.map(_vacio)].iterrows():
        ar = float(r.actual_close4) / float(r.base_close) - 1
        if abs(ar - float(r.actual_ret)) > 1e-9:
            v.append(f"actual_ret no coincide en {r.base_open_utc}")
        for m in MODELOS:
            esperado = kt.sign_hit(float(r[f"{m}_ret"]), ar)
            got = "" if _vacio(r[f"{m}_hit"]) else str(int(float(r[f"{m}_hit"])))
            if esperado != got:
                v.append(f"{m}_hit no coincide en {r.base_open_utc}: {got!r} vs {esperado!r}")
    return v


def huecos(df: pd.DataFrame) -> list[str]:
    b = pd.to_datetime(df.base_open_utc, utc=True).sort_values()
    todas = pd.date_range(b.iloc[0], b.iloc[-1], freq="h")
    return [x.isoformat() for x in todas.difference(pd.DatetimeIndex(b))]


def resumen_reproducible(kt_mod_path: Path) -> tuple[list[str], dict]:
    pub = json.loads((DATA / "resumen.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(DATA / "predicciones.csv", Path(d) / "predicciones.csv")
        os.environ["KT002_OUT"] = d
        sys.path.insert(0, str(kt_mod_path.parent))
        import kt002_prospectivo as kt  # noqa: E402
        # Si el módulo ya estaba importado, OUT apunta a data/kt002: se fuerza el directorio temporal
        # para que summarize() NUNCA escriba sobre los datos reales.
        out_orig, pred_orig = kt.OUT, kt.PRED
        kt.OUT, kt.PRED = Path(d), Path(d) / "predicciones.csv"
        try:
            preds = kt.load_predictions()
            nuevo = kt.summarize(preds, pd.Timestamp(pub["updated_utc"]))
        finally:
            kt.OUT, kt.PRED = out_orig, pred_orig
    nuevo = json.loads(json.dumps(nuevo))
    dif = [k for k in sorted(set(pub) | set(nuevo)) if pub.get(k) != nuevo.get(k)]
    return ([f"resumen.json difiere del recalculado en: {dif}"] if dif else []), kt


def historial() -> tuple[list[str], int]:
    shas = subprocess.run(["git", "-C", str(REPO), "log", "--format=%H", "--reverse", "--", CSV_REL],
                          capture_output=True, text=True, check=True).stdout.split()
    v, prev = [], None
    for sha in shas:
        txt = subprocess.run(["git", "-C", str(REPO), "show", f"{sha}:{CSV_REL}"], capture_output=True, text=True).stdout
        if not txt.strip():
            continue
        cur = pd.read_csv(io.StringIO(txt), dtype=str).set_index("base_open_utc", drop=False)
        if prev is not None:
            for base, r in prev.iterrows():
                if base not in cur.index:
                    v.append(f"{sha[:7]}: desapareció la fila {base}")
                    continue
                n = cur.loc[base]
                for c in PRONOSTICO:
                    if c in prev.columns and str(r[c]) != str(n[c]):
                        v.append(f"{sha[:7]}: cambió {c} en {base}")
                for c in PUNTUACION:
                    if c in prev.columns and not _vacio(r[c]) and str(r[c]) != str(n[c]):
                        v.append(f"{sha[:7]}: se reescribió {c} ya puntuado en {base}")
        prev = cur
    return v, len(shas)


def main(argv: list[str]) -> int:
    df = pd.read_csv(DATA / "predicciones.csv", dtype=str)
    viol, kt = resumen_reproducible(REPO / "tools" / "kt002_prospectivo.py")
    viol += actuales(df, kt)
    rep = dict(filas=len(df), puntuadas=int((~df.actual_ret.map(_vacio)).sum()),
               primera_base=df.base_open_utc.iloc[0], ultima_base=df.base_open_utc.iloc[-1],
               horas_omitidas=huecos(df))
    rep["reproducibilidad_modelos"] = json.loads((DATA / "reproducibilidad.json").read_text()).get("identico")
    if "--sin-historial" not in argv:
        hv, n = historial()
        viol += hv
        rep["versiones_revisadas_en_git"] = n
    rep["violaciones"] = viol
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 1 if viol else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
