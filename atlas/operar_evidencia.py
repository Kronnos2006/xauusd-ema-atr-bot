"""CLI operativa del censo ATLAS. Solo lectura, sin promoción ni órdenes.

Uso: python -m atlas.operar_evidencia verificar-censo --registro R --ancla A
La ancla debe provenir de custodia independiente. La CLI NO la genera.
"""
import argparse
import json
from .censo_variantes import verificar_censo


def main(argv=None):
    p = argparse.ArgumentParser(description="Verificación local ATLAS (sin trading)")
    sub = p.add_subparsers(dest="accion", required=True)
    c = sub.add_parser("verificar-censo")
    c.add_argument("--registro", required=True)
    c.add_argument("--ancla", required=True)
    args = p.parse_args(argv)
    try:
        with open(args.ancla, encoding="utf-8") as fh:
            ancla = json.load(fh)
        resultado = verificar_censo(args.registro, ancla)
        resultado["promocion_permitida"] = False
        print(json.dumps(resultado, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        print(json.dumps({"estado": "INVALIDO", "error": str(exc),
                          "promocion_permitida": False}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
