#!/usr/bin/env python3
"""
Estudio de costos de ejecucion reales — XAUUSD, broker propio.

QUE ES Y QUE NO ES
------------------
Esto NO es una estrategia y NO evalua edge. Es una MEDICION de lo que
cuesta operar en este activo con este broker, a partir de observaciones
reales capturadas en vivo.

Por eso no consume presupuesto de multiple testing: no hay hipotesis que
aceptar o rechazar. Se mide y se reporta.

QUE PRODUCE
-----------
  informe_costos.md   el informe con todos los numeros
  costos_*.png        graficos (si matplotlib esta disponible)

Uso:
    python analisis_costos.py senales_demo_live.csv

Sin dependencias obligatorias. matplotlib es opcional.
"""
import csv
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median, pstdev


# ---------------------------------------------------------------- utilidades

def pctl(datos, p):
    if not datos:
        return float("nan")
    s = sorted(datos)
    k = (len(s) - 1) * p / 100.0
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def resumen(datos, nombre, unidad=""):
    if not datos:
        return f"  {nombre}: sin datos"
    return (
        f"  {nombre}  (n={len(datos)})\n"
        f"    min {min(datos):.4f}{unidad}   p25 {pctl(datos,25):.4f}{unidad}   "
        f"mediana {median(datos):.4f}{unidad}\n"
        f"    p75 {pctl(datos,75):.4f}{unidad}   p90 {pctl(datos,90):.4f}{unidad}   "
        f"p99 {pctl(datos,99):.4f}{unidad}   max {max(datos):.4f}{unidad}\n"
        f"    media {mean(datos):.4f}{unidad}   sd {pstdev(datos):.4f}{unidad}"
    )


def parse_ts(s):
    s = (s or "").strip().replace("Z", "+00:00")
    for fmt in (None, "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.fromisoformat(s) if fmt is None \
                else datetime.strptime(s, fmt)
        except (ValueError, TypeError):
            continue
    return None


def num(v):
    try:
        x = float(str(v).replace(",", "."))
        return x
    except (TypeError, ValueError):
        return None


def booleano(v):
    return str(v).strip().lower() in ("1", "true", "si", "sí", "yes", "y", "t")


# ---------------------------------------------------------------- carga

def cargar(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        filas = list(csv.DictReader(fh))
    if not filas:
        sys.exit("el CSV no tiene filas de datos")

    obs = []
    descartes = defaultdict(int)
    for f in filas:
        o = {
            "t_vela": parse_ts(f.get("timestamp_vela")),
            "t_det": parse_ts(f.get("timestamp_deteccion_utc")),
            "tipo": (f.get("tipo") or "").strip().lower(),
            "close": num(f.get("close_vela")),
            "atr": num(f.get("atr")),
            "riesgo": num(f.get("riesgo_teorico")),
            "sl": num(f.get("sl_teorico")),
            "liquida": booleano(f.get("en_sesion_liquida")),
            "bid": num(f.get("bid_real")),
            "ask": num(f.get("ask_real")),
            "spread_pts": num(f.get("spread_real_puntos")),
            "ref": num(f.get("precio_ref_real")),
            "gap_R": num(f.get("gap_vs_close_R")),
        }
        if o["t_vela"] is None:
            descartes["sin timestamp valido"] += 1
            continue
        # latencia entre el cierre de la vela y el momento en que el logger
        # capturo el precio. Es lo que separa deslizamiento real de
        # artefacto por reinicio del proceso.
        o["latencia_min"] = None
        if o["t_det"] is not None:
            a, b = o["t_vela"], o["t_det"]
            if a.tzinfo is None and b.tzinfo is not None:
                a = a.replace(tzinfo=b.tzinfo)
            elif b.tzinfo is None and a.tzinfo is not None:
                b = b.replace(tzinfo=a.tzinfo)
            o["latencia_min"] = (b - a).total_seconds() / 60.0
        obs.append(o)
    return obs, descartes


# ---------------------------------------------------------------- unidades

def inferir_spread_en_precio(obs):
    """
    spread_real_puntos viene en 'puntos' del broker, que no sabemos cuanto
    valen. Pero tenemos bid y ask: la diferencia esta en unidades de PRECIO.
    Con eso deducimos el tamano del punto en vez de asumirlo.
    """
    pares = [(o["ask"] - o["bid"], o["spread_pts"])
             for o in obs
             if None not in (o["bid"], o["ask"], o["spread_pts"])
             and o["spread_pts"] > 0 and o["ask"] > o["bid"]]
    if not pares:
        return None, "no se pudo deducir (faltan bid/ask o spread)"
    ratios = [d / p for d, p in pares]
    m = median(ratios)
    disp = pstdev(ratios) / m if m else float("inf")
    nota = (f"1 punto = {m:.6g} en precio "
            f"(deducido de bid/ask sobre {len(pares)} obs, "
            f"dispersion relativa {disp:.1%})")
    if disp > 0.05:
        nota += "  <-- ATENCION: dispersion alta, la conversion no es estable"
    return m, nota


# ---------------------------------------------------------------- analisis

def por_hora(obs, campo):
    g = defaultdict(list)
    for o in obs:
        if o[campo] is not None and o["t_vela"]:
            g[o["t_vela"].hour].append(o[campo])
    return g


def por_sesion(obs, campo):
    g = {True: [], False: []}
    for o in obs:
        if o[campo] is not None:
            g[o["liquida"]].append(o[campo])
    return g


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ruta = Path(sys.argv[1])
    obs, descartes = cargar(ruta)

    L = []
    def p(s=""):
        print(s)
        L.append(s)

    p("# Estudio de costos de ejecucion — XAUUSD")
    p()
    p(f"Fuente: `{ruta.name}`  ·  generado {datetime.now():%Y-%m-%d %H:%M}")
    p()
    p("Esto es una **medicion**, no una hipotesis de trading. No evalua edge")
    p("ni consume presupuesto de multiple testing.")
    p()

    # --- cobertura -------------------------------------------------
    tv = [o["t_vela"] for o in obs]
    dias = (max(tv) - min(tv)).total_seconds() / 86400
    p("## 1. Cobertura")
    p()
    p(f"- observaciones: **{len(obs)}**")
    if descartes:
        for k, v in descartes.items():
            p(f"- descartadas: {v} ({k})")
    p(f"- desde {min(tv):%Y-%m-%d %H:%M} hasta {max(tv):%Y-%m-%d %H:%M}")
    p(f"- span: {dias:.1f} dias ({dias/7:.1f} semanas)")
    p(f"- tasa: {len(obs)/dias:.2f} obs/dia")
    liq = sum(1 for o in obs if o["liquida"])
    p(f"- en sesion liquida: {liq} ({100*liq/len(obs):.1f}%)  ·  "
      f"fuera: {len(obs)-liq} ({100*(len(obs)-liq)/len(obs):.1f}%)")
    tipos = defaultdict(int)
    for o in obs:
        tipos[o["tipo"] or "(vacio)"] += 1
    p(f"- por tipo: " + ", ".join(f"{k}={v}" for k, v in sorted(tipos.items())))
    p()

    # --- unidades --------------------------------------------------
    punto, nota_punto = inferir_spread_en_precio(obs)
    p("## 2. Unidades")
    p()
    p(f"- {nota_punto}")
    p()

    # --- spread ----------------------------------------------------
    spreads = [o["spread_pts"] for o in obs if o["spread_pts"] is not None]
    p("## 3. Spread")
    p()
    p("```")
    p(resumen(spreads, "spread (puntos del broker)"))
    p("```")
    p()

    if punto:
        sp_precio = [s * punto for s in spreads]
        p("```")
        p(resumen(sp_precio, "spread (unidades de precio)"))
        p("```")
        p()

    # spread en unidades de R: cuanto del riesgo se va en cruzar el spread
    sp_R = []
    for o in obs:
        if None in (o["spread_pts"], o["riesgo"]) or not o["riesgo"] or not punto:
            continue
        sp_R.append((o["spread_pts"] * punto) / abs(o["riesgo"]))
    if sp_R:
        p("### Spread expresado en unidades de riesgo (R)")
        p()
        p("Cuanto del riesgo de la operacion se consume solo por cruzar el")
        p("spread de entrada. Es la magnitud que se compara directo contra")
        p("el resultado esperado de cualquier estrategia.")
        p()
        p("```")
        p(resumen(sp_R, "spread / riesgo_teorico", " R"))
        p("```")
        p()

    # --- spread por hora -------------------------------------------
    g = por_hora(obs, "spread_pts")
    if g:
        p("### Spread por hora (UTC)")
        p()
        p("| hora | n | mediana | p90 | max |")
        p("|---:|---:|---:|---:|---:|")
        for h in sorted(g):
            d = g[h]
            p(f"| {h:02d} | {len(d)} | {median(d):.2f} | "
              f"{pctl(d,90):.2f} | {max(d):.2f} |")
        p()
        peor = max(g, key=lambda h: median(g[h]))
        mejor = min(g, key=lambda h: median(g[h]))
        p(f"- hora mas cara: **{peor:02d}:00 UTC** "
          f"(mediana {median(g[peor]):.2f} pts, n={len(g[peor])})")
        p(f"- hora mas barata: **{mejor:02d}:00 UTC** "
          f"(mediana {median(g[mejor]):.2f} pts, n={len(g[mejor])})")
        if median(g[mejor]):
            p(f"- razon peor/mejor: **{median(g[peor])/median(g[mejor]):.2f}x**")
        p()
        p("> Ojo con las horas de pocas observaciones: una mediana sobre 2 o 3")
        p("> datos no dice nada. Mirar la columna n antes de concluir.")
        p()

    # --- sesion ----------------------------------------------------
    gs = por_sesion(obs, "spread_pts")
    if gs[True] and gs[False]:
        p("### Spread dentro vs fuera de sesion liquida")
        p()
        p(f"- dentro (n={len(gs[True])}): mediana {median(gs[True]):.2f} pts, "
          f"p90 {pctl(gs[True],90):.2f}")
        p(f"- fuera  (n={len(gs[False])}): mediana {median(gs[False]):.2f} pts, "
          f"p90 {pctl(gs[False],90):.2f}")
        if median(gs[True]):
            p(f"- penalizacion por operar fuera: "
              f"**{median(gs[False])/median(gs[True]):.2f}x**")
        p()

    # --- gap vs close ----------------------------------------------
    gaps = [o["gap_R"] for o in obs if o["gap_R"] is not None]
    if gaps:
        p("## 4. Deslizamiento: precio real vs cierre de la vela")
        p()
        p("`gap_vs_close_R` mide cuanto se despega el precio ejecutable del")
        p("cierre de la vela que genero la senal, en unidades de riesgo.")
        p("Un backtest que asume entrada al cierre ignora exactamente esto.")
        p()
        p("```")
        p(resumen(gaps, "gap_vs_close_R", " R"))
        p("```")
        p()
        adversos = [g for g in gaps if g > 0]
        p(f"- observaciones con gap adverso (>0): {len(adversos)} "
          f"({100*len(adversos)/len(gaps):.1f}%)")
        if adversos:
            p(f"- gap adverso medio: {mean(adversos):.4f} R  ·  "
              f"p90 {pctl(adversos,90):.4f} R")
        p(f"- |gap| mediano: {median([abs(g) for g in gaps]):.4f} R")
        p()

        gh = por_hora(obs, "gap_R")
        p("### Gap por hora (UTC)")
        p()
        p("| hora | n | mediana R | p90 R |")
        p("|---:|---:|---:|---:|")
        for h in sorted(gh):
            d = gh[h]
            p(f"| {h:02d} | {len(d)} | {median(d):+.4f} | {pctl(d,90):+.4f} |")
        p()

    # --- latencia: separar deslizamiento real de artefacto ----------
    LIMITE_MIN = 20.0
    lat = [o["latencia_min"] for o in obs if o["latencia_min"] is not None]
    gaps_limpios = [o["gap_R"] for o in obs
                    if o["gap_R"] is not None
                    and o["latencia_min"] is not None
                    and 0 <= o["latencia_min"] <= LIMITE_MIN]
    gaps_sucios = [o["gap_R"] for o in obs
                   if o["gap_R"] is not None
                   and (o["latencia_min"] is None or o["latencia_min"] > LIMITE_MIN
                        or o["latencia_min"] < 0)]

    p("## 4b. Latencia de captura — separar deslizamiento de artefacto")
    p()
    p("`gap_vs_close_R` compara el precio capturado contra el cierre de la")
    p("vela. Si el logger capturo el precio minutos despues del cierre, ese")
    p("gap es deslizamiento real. Si lo capturo horas o dias despues —porque")
    p("el proceso se cayo y revivio leyendo una vela vieja— el gap mide el")
    p("movimiento del mercado durante la caida, no un costo de ejecucion.")
    p()
    p(f"Corte usado: latencia <= {LIMITE_MIN:.0f} minutos.")
    p()
    if lat:
        p("```")
        p(resumen(lat, "latencia deteccion - cierre de vela", " min"))
        p("```")
        p()
    p(f"- observaciones limpias (latencia <= {LIMITE_MIN:.0f} min): "
      f"**{len(gaps_limpios)}**")
    p(f"- observaciones descartadas (latencia alta o desconocida): "
      f"**{len(gaps_sucios)}**")
    p()
    if gaps_limpios:
        p("### Gap SOLO con observaciones limpias")
        p()
        p("```")
        p(resumen(gaps_limpios, "gap_vs_close_R (limpio)", " R"))
        p("```")
        p()
    if gaps_sucios:
        p("### Gap de las descartadas (para contraste, NO usar como costo)")
        p()
        p("```")
        p(resumen(gaps_sucios, "gap_vs_close_R (contaminado)", " R"))
        p("```")
        p()
        p("Si estas magnitudes son mucho mayores que las limpias, confirma")
        p("que el problema era el logger y no el broker.")
        p()

    # --- el numero que importa -------------------------------------
    p("## 5. Costo total de implementacion")
    p()
    base = gaps_limpios if gaps_limpios else gaps
    etiqueta = ("gaps limpios" if gaps_limpios
                else "TODOS los gaps — sin filtro de latencia, poco confiable")
    if sp_R and base:
        p(f"_Calculado sobre {len(base)} observaciones ({etiqueta})._")
        p()
        c_med = median(sp_R) + median([abs(g) for g in base])
        c_p90 = pctl(sp_R, 90) + pctl([abs(g) for g in base], 90)
        p(f"Sumando spread de entrada y deslizamiento, en unidades de riesgo:")
        p()
        p(f"- caso tipico (medianas):  **{c_med:.4f} R por operacion**")
        p(f"- caso malo (p90):         **{c_p90:.4f} R por operacion**")
        p()
        p("### Edge minimo requerido")
        p()
        p("Para que una estrategia con ratio riesgo:beneficio 1:RR no pierda")
        p("plata, su win rate tiene que superar el de breakeven por encima de")
        p("lo que cuesta implementarla:")
        p()
        p("| RR | WR breakeven | WR minimo (tipico) | WR minimo (p90) |")
        p("|---:|---:|---:|---:|")
        for rr in (1.0, 1.5, 2.0, 2.5, 3.0):
            be = 1.0 / (1.0 + rr)
            wr_med = (c_med + 1.0) / (1.0 + rr)
            wr_p90 = (c_p90 + 1.0) / (1.0 + rr)
            f90 = f"{wr_p90:.2%}" if wr_p90 <= 1.0 else f"{wr_p90:.0%} IMPOSIBLE"
            p(f"| 1:{rr} | {be:.2%} | {wr_med:.2%} | {f90} |")
        p()
        if c_p90 >= 1.0:
            p("> **Un win rate requerido mayor al 100% no es un resultado: es")
            p("> un aviso.** Significa que el p90 del costo esta dominado por")
            p("> valores extremos que no representan operar normalmente.")
            p("> Revisar la seccion 4b antes de creerle a esa columna.")
            p()
        p("Cualquier hipotesis cuyo win rate esperado no supere la tercera")
        p("columna puede descartarse **antes** de escribir el backtest.")
        p()
    else:
        p("No hay datos suficientes (faltan spread en R o gap) para este calculo.")
        p()

    # --- graficos --------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        if spreads:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.hist(spreads, bins=25, edgecolor="white")
            ax.axvline(median(spreads), color="crimson", ls="--",
                       label=f"mediana {median(spreads):.1f}")
            ax.set_xlabel("spread (puntos)"); ax.set_ylabel("frecuencia")
            ax.set_title("Distribucion del spread real"); ax.legend()
            fig.tight_layout(); fig.savefig("costos_spread_hist.png", dpi=130)
            plt.close(fig)

        if g:
            horas = sorted(g)
            fig, ax = plt.subplots(figsize=(9, 4))
            ax.bar(horas, [median(g[h]) for h in horas], edgecolor="white")
            ax.set_xlabel("hora UTC"); ax.set_ylabel("spread mediano (puntos)")
            ax.set_title("Spread por hora del dia"); ax.set_xticks(horas)
            fig.tight_layout(); fig.savefig("costos_spread_hora.png", dpi=130)
            plt.close(fig)

        if gaps:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.hist(gaps, bins=25, edgecolor="white")
            ax.axvline(0, color="black", lw=1)
            ax.axvline(median(gaps), color="crimson", ls="--",
                       label=f"mediana {median(gaps):+.4f} R")
            ax.set_xlabel("gap_vs_close_R"); ax.set_ylabel("frecuencia")
            ax.set_title("Deslizamiento vs cierre de vela"); ax.legend()
            fig.tight_layout(); fig.savefig("costos_gap_hist.png", dpi=130)
            plt.close(fig)

        p("Graficos: `costos_spread_hist.png`, `costos_spread_hora.png`, "
          "`costos_gap_hist.png`")
    except ImportError:
        p("_(matplotlib no instalado — sin graficos. "
          "`pip install matplotlib` si los queres.)_")
    p()

    p("## Limitaciones")
    p()
    p("- Muestra de un solo broker, un solo activo, un solo periodo.")
    p("- El spread se observa en el momento de la SENAL, no en el de una")
    p("  ejecucion real: no incluye el deslizamiento de la orden en si.")
    p("- Las senales no son independientes entre si.")
    p("- No hay datos de ordenes rechazadas ni de requotes.")

    Path("informe_costos.md").write_text("\n".join(L), encoding="utf-8")
    print("\n>>> informe escrito en informe_costos.md")


if __name__ == "__main__":
    main()
