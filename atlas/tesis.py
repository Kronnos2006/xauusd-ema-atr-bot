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


class TransicionInvalida(ValueError):
    pass


def transicion(tesis: dict, nuevo: str, revisor: str, motivo: str, evidencia_nueva: list | None = None) -> dict:
    viejo = tesis["estado"]
    if nuevo not in TRANSICIONES.get(viejo, set()):
        raise TransicionInvalida(f"{viejo} → {nuevo} no permitida")
    if viejo == "RECHAZADA" and not evidencia_nueva:
        raise TransicionInvalida("reabrir una tesis rechazada exige evidencia nueva")
    if not revisor or revisor.lower().startswith("llm"):
        raise TransicionInvalida("la transición exige un revisor registrado (no un LLM sin revisión)")
    if nuevo == "ACEPTADA_PARA_SIMULACION" and not tesis.get("preregistro_hash"):
        raise TransicionInvalida("sin preregistro no se acepta para simulación")
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

    def anexar(self, tesis: dict) -> str:
        prev = self._lineas()
        ant = prev[-1]["hash"] if prev else "0" * 64
        cuerpo = {"anterior": ant, "tesis": tesis}
        h = huella(cuerpo)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta.open("a", encoding="utf-8") as f:
            f.write(json.dumps({**cuerpo, "hash": h}, ensure_ascii=False, sort_keys=True) + "\n")
        return h

    def verificar(self) -> list[str]:
        err, ant = [], "0" * 64
        for i, l in enumerate(self._lineas()):
            if l["anterior"] != ant:
                err.append(f"línea {i}: cadena rota")
            if huella({"anterior": l["anterior"], "tesis": l["tesis"]}) != l["hash"]:
                err.append(f"línea {i}: contenido alterado")
            ant = l["hash"]
        return err
