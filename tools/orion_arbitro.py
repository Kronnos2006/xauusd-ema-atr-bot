#!/usr/bin/env python3
"""ORION bridge v1: arbiter de reservas en GitHub Issues (sin invocar IA).

Solo corre bajo workflow_dispatch autenticado con GITHUB_TOKEN y permiso issues:write.
El 'operador' es una etiqueta solicitada, nunca identidad probada de Claude/ChatGPT.
El ejecutor real queda registrado por GitHub actor. No abre PR ni cambia archivos.
"""
import argparse
import json
import os
import sys
from urllib import request, error
from urllib.parse import quote

PREFIX = "[ORION]"
MARKER = "<!-- ORION_CLAIM_V1 "
END = " -->"
ALLOWED = ("Claude", "ChatGPT", "Gerencia", "Operaciones")
BOT = "github-actions[bot]"


def validate(issue_number, operation, operator, actor):
    if not isinstance(issue_number, int) or issue_number < 1:
        raise ValueError("Número de issue inválido")
    if operation not in ("reservar", "liberar", "estado"):
        raise ValueError("Operación no permitida")
    if operator not in ALLOWED:
        raise ValueError("Operador inválido")
    if not actor or len(actor) > 80:
        raise ValueError("Usuario GitHub no verificado")


def decode_events(comments):
    """Solo los comentarios del bot son señal de reserva, no declaraciones humanas."""
    events = []
    for item in comments:
        if item.get("user", {}).get("login", "").lower() != BOT:
            continue
        body = item.get("body") or ""
        pos = body.find(MARKER)
        if pos < 0:
            continue
        end = body.find(END, pos + len(MARKER))
        if end < 0:
            continue
        try:
            record = json.loads(body[pos + len(MARKER):end])
        except (ValueError, TypeError):
            continue
        if (isinstance(record, dict) and record.get("event") in ("reserved", "released")
                and isinstance(record.get("actor"), str)
                and record.get("operator") in ALLOWED):
            events.append((item.get("id", 0), record))
    events.sort(key=lambda pair: pair[0])
    return [record for _, record in events]


def current_claim(comments):
    """Último estado confirmado; una liberación del mismo actor anula su reserva."""
    current = None
    for event in decode_events(comments):
        if event["event"] == "reserved" and current is None:
            current = event
        elif event["event"] == "released" and current and event["actor"] == current["actor"]:
            current = None
    return current


def decision(operation, operator, actor, comments):
    claim = current_claim(comments)
    if operation == "estado":
        return {"status": "reservado" if claim else "libre", "claim": claim}, None
    if operation == "reservar":
        if claim:
            raise ValueError("La tarea ya está reservada por " + claim["actor"] + " para " + claim["operator"])
        return {"status": "reservado", "actor": actor, "operator": operator}, {
            "event": "reserved", "actor": actor, "operator": operator}
    if not claim:
        raise ValueError("No hay reserva activa")
    if claim["actor"] != actor:
        raise ValueError("Solo el usuario GitHub que reservó puede liberar")
    return {"status": "libre", "actor": actor, "operator": operator}, {
        "event": "released", "actor": actor, "operator": claim["operator"]}


def api(method, url, token, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Accept": "application/vnd.github+json",
               "Authorization": "Bearer " + token,
               "X-GitHub-Api-Version": "2022-11-28"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=data, method=method, headers=headers)
    with request.urlopen(req, timeout=20) as res:
        return json.load(res)


def run(issue, operation, operator, repo, actor, token):
    validate(issue, operation, operator, actor)
    if not token or "/" not in repo:
        raise ValueError("Falta token de Actions o repositorio")
    base = "https://api.github.com/repos/" + quote(repo, safe="/") + "/issues/" + str(issue)
    record = api("GET", base, token)
    if not str(record.get("title", "")).upper().startswith(PREFIX) or "pull_request" in record:
        raise ValueError("Solo issues de solicitud [ORION] (nunca PRs)")
    if record.get("state") != "open":
        raise ValueError("Solicitud cerrada: no se permite reservar")
    comments = []
    page = 1
    while True:
        chunk = api("GET", base + "/comments?per_page=100&page=" + str(page), token)
        comments.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
        if page > 30:
            raise ValueError("Demasiados comentarios; revisar manualmente")
    result, event = decision(operation, operator, actor, comments)
    if event:
        message = MARKER + json.dumps(event, separators=(",", ":"), ensure_ascii=True) + END
        line = ("RESERVA" if operation == "reservar" else "LIBERACIÓN") + " ORION | solicitado por @" + actor
        api("POST", base + "/comments", token, {"body": line + "\n\n" + message +
            "\n\nNota: esto NO demuestra que un agente IA haya iniciado o finalizado una sesión."})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("issue", type=int)
    parser.add_argument("operation", choices=("reservar", "liberar", "estado"))
    parser.add_argument("operator", choices=ALLOWED)
    args = parser.parse_args()
    try:
        result = run(args.issue, args.operation, args.operator,
                     os.environ.get("GITHUB_REPOSITORY", ""),
                     os.environ.get("GITHUB_ACTOR", ""),
                     os.environ.get("GH_TOKEN", ""))
        print(json.dumps({"ok": True, "issue": args.issue, **result},
                         ensure_ascii=False))
    except (ValueError, OSError, error.URLError, error.HTTPError) as exc:
        # Nunca imprimir credenciales.
        print(json.dumps({"ok": False, "issue": args.issue, "error": str(exc)}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
