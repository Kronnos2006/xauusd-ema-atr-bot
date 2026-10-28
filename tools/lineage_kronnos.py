#!/usr/bin/env python3
"""KRONNOS: manifiestos deterministas de archivos. No custodia externa."""
import argparse
import hashlib
import json
from pathlib import Path

def hash_file(path):
    h = hashlib.sha256()
    total = 0
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            h.update(block)
            total += len(block)
    return {"sha256": h.hexdigest(), "bytes": total}

def build_manifest(root, paths, model_version, git_sha):
    root = Path(root).resolve()
    if not paths or not isinstance(model_version,str) or not model_version.strip():
        raise ValueError("Inputs y versión obligatorios")
    if not isinstance(git_sha,str) or len(git_sha)!=40 or any(ch not in "0123456789abcdef" for ch in git_sha.lower()):
        raise ValueError("SHA de commit inválido")
    items=[]
    for name in sorted(set(paths)):
        original=root/name
        if original.is_symlink():
            raise ValueError("Enlaces simbólicos prohibidos")
        p=original.resolve()
        if not p.is_relative_to(root) or not p.is_file():
            raise ValueError("Ruta no válida")
        items.append({"path":p.relative_to(root).as_posix(), **hash_file(p)})
    payload={"schema_version":1,"model_version":model_version,"git_sha":git_sha,"inputs":items}
    canonical=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return {"payload":payload,"payload_sha256":hashlib.sha256(canonical).hexdigest()}

def write_new(output, manifest):
    target=Path(output)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("x",encoding="utf-8") as f:
        json.dump(manifest,f,sort_keys=True,ensure_ascii=False,indent=2)
        f.write("\n")

def verify(root, manifest):
    payload=manifest["payload"]
    current=build_manifest(root,[x["path"] for x in payload["inputs"]],payload["model_version"],payload["git_sha"])
    return current==manifest

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=".")
    p.add_argument("--input",action="append",required=True)
    p.add_argument("--version",required=True)
    p.add_argument("--commit-sha",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    manifest=build_manifest(a.root,a.input,a.version,a.commit_sha)
    write_new(a.output,manifest)
    print(json.dumps({"verified":verify(a.root,manifest),"manifest_sha256":manifest["payload_sha256"]}))
