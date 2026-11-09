"""Piloto sintético H4. Solo lectura. El protocolo del operador está en --help."""

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory


EVENTS = {"alta.json", "alta.tsr", "inicio.json", "inicio.sig", "cierre.json"}
MANIFEST = {"inventario.json", "inventario.sig"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=120,
                          env={**os.environ, "LC_ALL": "C"}).stdout


def utc(value):
    require(isinstance(value, str), "Fecha inválida")
    date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(date.utcoffset() == timedelta(0), "La fecha debe estar en UTC")
    return date


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Clave JSON duplicada: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def verify(args, directory):
    prefix = f"atlas-h4-sintetico/{args.piloto}/"

    def aws(operation, *flags):
        return json.loads(run(
            args.aws, "s3api", operation, "--bucket", args.bucket,
            "--expected-bucket-owner", args.cuenta, "--profile", args.perfil,
            "--output", "json", "--no-cli-pager", *flags,
        ))

    def list_versions():
        listing = aws("list-object-versions", "--prefix", prefix)
        require(not listing.get("IsTruncated"), "Listado incompleto")
        require(not listing.get("DeleteMarkers"), "El prefijo contiene marcas de borrado")
        versions = {}
        for entry in listing.get("Versions", []):
            name = entry["Key"].removeprefix(prefix)
            require(name not in versions, f"Objeto con más de una versión: {name}")
            require(entry["VersionId"] not in ("", "null"), f"Objeto sin versión: {name}")
            versions[name] = entry
        require(versions.keys() == EVENTS | MANIFEST, "Inventario incompleto o con objetos inesperados")
        return versions

    versions = list_versions()
    now = datetime.now(timezone.utc)
    for name, entry in versions.items():
        flags = ("--key", entry["Key"], "--version-id", entry["VersionId"])
        retention = aws("get-object-retention", *flags)["Retention"]
        require(retention["Mode"] == "COMPLIANCE", f"Retención incorrecta: {name}")
        require(utc(retention["RetainUntilDate"]) > now, f"Retención vencida: {name}")
        response = aws("get-object", *flags, str(directory / name))
        require(response["VersionId"] == entry["VersionId"], f"Versión incorrecta: {name}")

    def verify_signature(stem):
        run(args.openssl, "pkeyutl", "-verify", "-rawin", "-pubin",
            "-inkey", args.clave, "-in", str(directory / f"{stem}.json"),
            "-sigfile", str(directory / f"{stem}.sig"))

    verify_signature("inventario")
    inventory = read_json(directory / "inventario.json")
    expected = {
        "piloto": args.piloto,
        "objetos": {
            name: {"version": versions[name]["VersionId"], "sha256": digest(directory / name)}
            for name in EVENTS
        },
    }
    require(inventory == expected, "El inventario firmado difiere del listado o de los bytes")

    verify_signature("inicio")
    registration = read_json(directory / "alta.json")
    start = read_json(directory / "inicio.json")
    end = read_json(directory / "cierre.json")
    identity = {"piloto": args.piloto, "intento": 1}
    for event in (registration, start, end):
        require(event["piloto"] == args.piloto and type(event["intento"]) is int
                and event["intento"] == 1, "Identidad de intento incorrecta")
    for key in ("definicion_sha256", "codigo_sha256", "datos_sha256"):
        require(re.fullmatch(r"[0-9a-f]{64}", registration[key]), f"Huella inválida: {key}")
    require(start == {**identity, "utc": start["utc"], "alta_sha256": digest(directory / "alta.json")},
            "El inicio firmado no vincula el alta")
    require(end == {**identity, "utc": end["utc"], "inicio_sha256": digest(directory / "inicio.json"),
                    "resultado": "sintetico"}, "El cierre no vincula el inicio")

    trust = ["-CAfile", args.ca]
    if args.tsa:
        trust += ["-untrusted", args.tsa]
    receipt = str(directory / "alta.tsr")
    run(args.openssl, "ts", "-verify", "-data", str(directory / "alta.json"),
        "-in", receipt, *trust)
    reply = run(args.openssl, "ts", "-reply", "-in", receipt, "-text")
    stamp = re.search(r"^Time stamp: (.+) GMT$", reply, re.MULTILINE)
    require(stamp, "El recibo no contiene una hora GMT")
    parsed = re.fullmatch(r"(.+:\d{2})(?:\.(\d{1,6}))? (\d{4})", stamp[1])
    require(parsed, "Formato de hora del recibo inválido")
    whole, fraction, year = parsed.groups()
    stamped = datetime.strptime(f"{whole} {year}", "%b %d %H:%M:%S %Y").replace(
        tzinfo=timezone.utc, microsecond=int((fraction or "").ljust(6, "0")),
    )
    started, ended = utc(start["utc"]), utc(end["utc"])
    stored_start = max(utc(versions[name]["LastModified"]) for name in ("inicio.json", "inicio.sig"))
    stored_receipt = utc(versions["alta.tsr"]["LastModified"])
    stored_end = utc(versions["cierre.json"]["LastModified"])
    require(stamped < started <= stored_start <= ended <= stored_end <= now
            and stored_receipt <= started,
            "El sello, el inicio registrado y el cierre no respetan el orden temporal")
    require(list_versions() == versions, "El listado cambió durante la verificación")
    return {"piloto": args.piloto, "intentos_sinteticos": 1, "estado": "PILOTO_VERIFICADO"}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Operador externo, con OpenSSL y una clave propia Ed25519:
1. Reserve un prefijo nuevo atlas-h4-sintetico/<piloto>/ en su bucket S3
   versionado con retención Compliance por defecto. Use un solo PUT por nombre.
2. Publique alta.json con piloto, intento=1, definicion_sha256, codigo_sha256
   y datos_sha256 de material sintético. Obtenga alta.tsr RFC 3161 sobre esos
   bytes exactos y publíquelo antes de emitir el inicio.
3. Publique inicio.json con piloto, intento=1, utc y alta_sha256. Firme sus
   bytes con: openssl pkeyutl -sign -rawin -inkey privada.pem -in inicio.json -out inicio.sig
   Publique inicio.sig y habilite la simulación solo tras confirmar ambos PUT.
4. Publique cierre.json con piloto, intento=1, utc, inicio_sha256 y
   resultado="sintetico". Las fechas usan ISO 8601 UTC con precisión de segundos.
5. Publique inventario.json con piloto y objetos. objetos mapea los cinco
   nombres anteriores a {"version": "VersionId de S3", "sha256": "huella"}.
   Fírmelo igual que el inicio y publique inventario.sig.
6. Entregue directamente al revisor el ID de piloto, bucket, cuenta, clave
   pública por canal autenticado y acceso de solo lectura a ese prefijo.
   Permisos AWS: s3:ListBucketVersions, s3:GetObjectVersion y
   s3:GetObjectRetention. El revisor fija su CA y cadena TSA por separado.
   El piloto es de un intento y su resultado no se incorpora a N_total.""")
    for flag in ("piloto", "bucket", "cuenta", "perfil", "clave", "ca"):
        parser.add_argument(f"--{flag}", required=True)
    parser.add_argument("--tsa")
    parser.add_argument("--aws", default="aws")
    parser.add_argument("--openssl", default="openssl")
    args = parser.parse_args()
    try:
        require(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", args.piloto), "ID de piloto inválido")
        require(re.fullmatch(r"[0-9]{12}", args.cuenta), "ID de cuenta inválido")
        with TemporaryDirectory() as temp:
            result = verify(args, Path(temp))
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f"INCONCLUSO: {error}\n")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
