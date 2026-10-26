"""ATLAS · registro de tesis (solo anexar, encadenado por hash) y máquina de estados."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ESTADOS = ("BORRADOR", "INVESTIGACION", "CONTRADICCION", "PREREGISTRADA", "VALIDACION",
           "ACEPTADA_PARA_SIMULACION", "RECHAZADA", "INCONCLUSA")
TRANSICIONES = {
    "BORRADOR": {"INVESTIGACION", "RECHAZADA"},
    "INVESTIGACION": {"CONTRADICCION", "INCONCLUSA", "RECHAZADA"},
    "CONTRADICCION": {"PREREGISTRADA", "INCONCLUSA", "RECHAZADA", "INVESTIGACION"},
    "PREREGISTRADA": {"VALIDACION"},
    "VALIDACION": {"ACEPTADA_PARA_SIMULACION", "RECHAZADA", "INCONCLUSA"},
    "INCONCLUSA": {"INVESTIGACION"},
    "RECHAZADA": {"INVESTIGACION"},           # solo con evidencia nueva y revisión registrada
    "ACEPTADA_PARA_SIMULACION": {"RECHAZADA"},
}


INICIALES = {"BORRADOR", "INVESTIGACION", "CONTRADICCION", "INCONCLUSA"}
# Revisores con identidad registrada en ORION. Un nombre libre (o un modelo de lenguaje) no aprueba nada.
REVISORES_REGISTRADOS = {"propietario", "desconfiado", "jefe-riesgo", "chatgpt-revision"}


class TransicionInvalida(ValueError):
    pass


def _evidencia_valida(ev) -> bool:
    return isinstance(ev, list) and len(ev) > 0 and all(
        isinstance(e, dict) and e.get("fuente") and e.get("utilizable_utc") and e.get("descripcion") for e in ev)


def transicion(tesis: dict, nuevo: str, revisor: str, motivo: str, evidencia_nueva: list | None = None) -> dict:
    viejo = tesis["estado"]
    if nuevo not in TRANSICIONES.get(viejo, set()):
        raise TransicionInvalida(f"{viejo} → {nuevo} no permitida")
    if viejo == "RECHAZADA" and not _evidencia_valida(evidencia_nueva):
        raise TransicionInvalida("reabrir una tesis rechazada exige evidencia nueva con fuente, hora de uso y descripción")
    if revisor not in REVISORES_REGISTRADOS:
        raise TransicionInvalida(f"revisor no registrado: {revisor!r} (válidos: {sorted(REVISORES_REGISTRADOS)})")
    if nuevo == "ACEPTADA_PARA_SIMULACION":
        raise TransicionInvalida("la aceptación para simulación requiere aprobación externa autenticada; una identidad declarada no basta")
    t2 = dict(tesis, estado=nuevo)
    t2["revisiones"] = tesis.get("revisiones", []) + [{"de": viejo, "a": nuevo, "revisor": revisor, "motivo": motivo,
                                                       "evidencia_nueva": evidencia_nueva or []}]
    return t2


def _canon(x) -> bytes:
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def huella(x) -> str:
    return hashlib.sha256(_canon(x)).hexdigest()


class Registro:
    """JSONL solo anexar: cada línea guarda el hash de la anterior. Alterar el pasado rompe la cadena."""

    def __init__(self, ruta: str):
        self.ruta = Path(ruta)

    def _lineas(self):
        return [json.loads(l) for l in self.ruta.read_text(encoding="utf-8").splitlines() if l.strip()] if self.ruta.exists() else []

    def ancla(self) -> dict:
        """Para guardar FUERA del archivo (documento, PR): detecta truncado o reescritura completa."""
        ls = self._lineas()
        return {"lineas": len(ls), "ultimo_hash": ls[-1]["hash"] if ls else "0" * 64}

    def anexar(self, tesis: dict) -> str:
        """Valida el estado contra la última versión de la misma tesis antes de anexar."""
        prev = self._lineas()
        previas = [l["tesis"] for l in prev if l["tesis"].get("id") == tesis.get("id")]
        nuevo = tesis.get("estado")
        if previas:
            viejo = previas[-1].get("estado")
            if nuevo != viejo and nuevo not in TRANSICIONES.get(viejo, set()):
                raise TransicionInvalida(f"registro: {viejo} → {nuevo} no permitida para {tesis.get('id')}")
            if nuevo != viejo and not (tesis.get("revisiones") or [{}])[-1].get("revisor") in REVISORES_REGISTRADOS:
                raise TransicionInvalida("registro: un cambio de estado exige una revisión registrada")
        elif nuevo not in INICIALES:
            raise TransicionInvalida(f"registro: una tesis nueva no puede empezar en {nuevo}")
        ant = prev[-1]["hash"] if prev else "0" * 64
        cuerpo = {"anterior": ant, "tesis": tesis}
        h = huella(cuerpo)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta.open("a", encoding="utf-8") as f:
            f.write(json.dumps({**cuerpo, "hash": h}, ensure_ascii=False, sort_keys=True) + "\n")
        return h

    def verificar(self, ancla: dict | None = None) -> list[str]:
        err, ant, n = [], "0" * 64, 0
        if not self.ruta.exists():
            return ["registro inexistente"]
        for i, txt in enumerate(x for x in self.ruta.read_text(encoding="utf-8").splitlines() if x.strip()):
            n += 1
            try:
                l = json.loads(txt)
                if l["anterior"] != ant:
                    err.append(f"línea {i}: cadena rota")
                if huella({"anterior": l["anterior"], "tesis": l["tesis"]}) != l["hash"]:
                    err.append(f"línea {i}: contenido alterado")
                ant = l["hash"]
            except (ValueError, KeyError, TypeError) as e:
                err.append(f"línea {i}: malformada ({type(e).__name__})")
                ant = None
        if ancla is not None and not any("malformada" in e for e in err):
            if n < ancla["lineas"]:
                err.append(f"truncado: {n} líneas, el ancla dice {ancla['lineas']}")
            else:
                ls = self._lineas()
                if ls[ancla["lineas"] - 1]["hash"] != ancla["ultimo_hash"] if ancla["lineas"] else False:
                    err.append("reescrito: el hash en la posición del ancla no coincide")
        return err
