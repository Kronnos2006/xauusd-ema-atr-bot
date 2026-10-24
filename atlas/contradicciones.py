"""ATLAS · motor de contradicciones. Desafía la tesis con 10 preguntas y llega a una de 4 conclusiones.
Nunca produce órdenes: la decisión es de investigación (CONTINUAR_INVESTIGANDO o ABSTENERSE).

Adapta la idea del debate alcista contra bajista de TauricResearch/TradingAgents@e8f5503
(agents/researchers/bull_researcher.py, bear_researcher.py), pero con reglas deterministas en vez de un LLM.
"""
from __future__ import annotations

import datetime as dt

from .analitica import COSTO_IDA_VUELTA, Evidencia
from .procedencia import Registro, frescura, t

CONCLUSIONES = ("FAVORABLE_CONTINUAR", "CONTRADICTORIA", "INCONCLUSA", "INSUFICIENTE")
LIMITE_FRESCURA = {"vela_1d": dt.timedelta(days=2), "prediccion": dt.timedelta(hours=3),
                   "spread": dt.timedelta(hours=6)}


def fugas(registros: list[Registro], corte: dt.datetime) -> list[str]:
    """Revalida TODO registro (también los que vienen de una instantánea): hora de uso, hora del evento y
    puntuaciones de predicciones conocidas después del corte."""
    out = []
    for r in registros:
        if r.utilizable_utc and frescura(r, corte, dt.timedelta(0)) == "futuro":
            out.append(f"{r.identificador}: utilizable después del corte")
        if r.tipo == "evento" and r.evento_utc and t(r.evento_utc) > corte:
            out.append(f"{r.identificador}: evento posterior al corte")
        if r.tipo == "prediccion" and isinstance(r.valor, dict) and r.valor.get("actual_ret") not in ("", None):
            s = t(r.valor.get("scored_utc"))
            if s is None or s > corte:
                out.append(f"{r.identificador}: resultado conocido después del corte")
    return out


def revisar(direccion_tesis: int, evid: list[Evidencia], registros: list[Registro], corte: dt.datetime, modelo_tesis: str = "kt001") -> dict:
    """direccion_tesis: +1 o -1 (la tesis que se pone a prueba); 0 = no hay tesis direccional que evaluar."""
    h = []  # hallazgos: {pregunta, resultado, critico}
    add = lambda p, r, c=False: h.append({"pregunta": p, "resultado": r, "critico": c})

    # 7. ¿Se usa información posterior al corte? (y fuentes sin hora verificable)
    futuros = fugas(registros, corte)
    sin_hora = [r for r in registros if r.calidad != "faltante" and not r.utilizable_utc]
    add("¿Se usa información posterior al corte?", f"{len(futuros)} fugas" + (f": {futuros[:3]}" if futuros else ""), bool(futuros))
    if sin_hora:
        add("¿Hay fuentes sin disponibilidad temporal verificable?",
            f"{len(sin_hora)} excluidas del análisis (sin hora de publicación)", False)

    # 5. ¿Los datos son actuales? ¿Fallaron proveedores?
    viejos, faltan = [], []
    for tipo, lim in LIMITE_FRESCURA.items():
        rs = [r for r in registros if r.tipo == tipo]
        if not rs or all(r.calidad == "faltante" for r in rs):
            faltan.append(tipo)
            continue
        ult = max((r for r in rs if r.utilizable_utc), key=lambda r: r.utilizable_utc, default=None)
        if ult is None or frescura(ult, corte, lim) == "viejo":
            viejos.append(tipo)
    # Sin velas, predicción o liquidez actuales no se puede justificar ninguna tesis: INSUFICIENTE.
    add("¿Los datos son suficientemente actuales?", f"viejos: {viejos or 'ninguno'}; faltantes: {faltan or 'ninguno'}",
        bool(viejos or faltan))
    if direccion_tesis == 0:
        add("¿Hay una tesis direccional que evaluar?", "no: sin predicción o predicción nula", True)

    por = {e.modulo: e for e in evid}
    pred = [e for e in evid if e.modulo.startswith("predictivo.") and e.tipo != "ausente"]
    indep = [e for e in evid if not e.modulo.startswith("predictivo.") and e.tipo == "hecho" and e.direccion != 0]

    # 1. ¿La predicción tiene respaldo independiente? Solo cuenta la ventaja (estudio confirmatorio aprobado)
    # de un modelo que predice EN LA DIRECCIÓN de la tesis; uno con ventaja en contra es evidencia contraria.
    con_ventaja = [e for e in pred if e.medicion.get("ventaja_demostrada") and e.direccion == direccion_tesis]
    ventaja_contra = [e for e in pred if e.medicion.get("ventaja_demostrada") and e.direccion == -direccion_tesis]
    add("¿La predicción tiene respaldo independiente?",
        (f"a favor: {[e.modulo for e in con_ventaja]}" if con_ventaja else "ningún modelo a favor con estudio confirmatorio aprobado")
        + (f"; en contra con ventaja: {[e.modulo for e in ventaja_contra]}" if ventaja_contra else ""))
    # 9. ¿La señal supera una referencia sencilla?
    add("¿La señal supera una referencia sencilla («siempre sube»)?",
        "; ".join(f"{e.modulo}: {e.medicion['aciertos']}/{e.medicion['n_sin_solape']} contra {e.medicion['siempre_sube_aciertos']}"
                  for e in pred) or "sin predicciones")
    # 8. ¿Fuera de régimen? (sin historial en este régimen no se puede saber)
    add("¿El modelo está fuera de su régimen de evaluación?",
        "historial insuficiente para evaluarlo por régimen" if all(e.medicion.get("n_sin_solape", 0) < 100 for e in pred)
        else "evaluar por régimen")
    # Modelos en desacuerdo
    dirs = {e.modulo: e.direccion for e in pred if e.modulo != "predictivo.kt001"}
    if len(set(dirs.values()) - {0}) > 1:
        add("¿Los modelos coinciden entre sí?", f"desacuerdo: {dirs}")

    # 2. ¿Qué contradice el escenario?
    contra = [e for e in indep if e.direccion == -direccion_tesis] + ventaja_contra
    favor = [e for e in indep if e.direccion == direccion_tesis]
    add("¿Qué información contradice el escenario?", [e.afirmacion for e in contra] or "nada independiente en contra")

    # 3. ¿Las noticias son relevantes para el horizonte? 6. ¿Correlación contra causalidad?
    ev = por.get("noticias.eventos")
    if ev is None or ev.tipo == "ausente":
        add("¿Las noticias son relevantes para el horizonte?", "sin cobertura de noticias verificables: no se puede evaluar")
    else:
        mixto = ev.medicion["a_favor"] and ev.medicion["en_contra"]
        add("¿Las noticias son relevantes para el horizonte?", f"{ev.medicion['n']} eventos; contradictorios: {bool(mixto)}")
        if mixto:
            contra.append(ev)
    add("¿Se confunde correlación con causalidad?", "ningún evento se usa como causa: solo como hipótesis no demostrada")

    # 4. ¿Hay explicaciones alternativas? — costo y liquidez
    vol = por.get("tecnico.volatilidad")
    mov = vol.medicion.get("mov_tipico_4h") if vol and vol.tipo != "ausente" else None
    if pred:
        modelo_objetivo = next((e for e in pred if e.modulo == f"predictivo.{modelo_tesis}"), None)
        r = abs(modelo_objetivo.medicion["ret_predicho"]) if modelo_objetivo else 0
        add("¿El movimiento predicho supera el costo de ida y vuelta?",
            f"|predicho| {r:.3%} contra costo {COSTO_IDA_VUELTA:.2%}; ruido típico 4 h {mov:.2%}" if mov else
            f"|predicho| {r:.3%} contra costo {COSTO_IDA_VUELTA:.2%}", False)
        costo_supera = modelo_objetivo is None or r < COSTO_IDA_VUELTA
    else:
        costo_supera = True
    liq = por.get("mercado.liquidez")
    iliquido = bool(liq and liq.medicion.get("insuficiente"))
    if iliquido:
        add("¿Hay liquidez suficiente?", liq.afirmacion, True)

    # Calidad de evidencias: material sin validar, corregido o contradictorio no justifica continuar.
    no_validados = [r.identificador for r in registros if r.calidad in ("sin_validar", "corregido", "contradictorio") and r.tipo != "evento"]
    if no_validados:
        add("¿Los datos utilizados están validados?", f"{len(no_validados)} registros sin validación decisoria", True)

    # Conclusión
    criticos = [x for x in h if x["critico"]]
    if criticos:
        concl = "INSUFICIENTE"
    elif favor and contra:
        concl = "CONTRADICTORIA"
    elif len(favor) >= 2 and con_ventaja and not costo_supera:
        concl = "FAVORABLE_CONTINUAR"
    else:
        concl = "INCONCLUSA"
    # 10. ¿La incertidumbre justifica abstenerse?
    abstener = concl != "FAVORABLE_CONTINUAR"
    add("¿La incertidumbre justifica abstenerse?", "sí" if abstener else "no: continuar la investigación (no es una orden)")
    return {"conclusion": concl, "decision_investigacion": "ABSTENERSE" if abstener else "CONTINUAR_INVESTIGANDO",
            "hallazgos": h, "favor": [e.afirmacion for e in favor], "contra": [e.afirmacion for e in contra]}
