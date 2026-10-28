#!/usr/bin/env python3
"""KRONNOS: provenance manifest inspired by Two Sigma Memento; stdlib only.
Does not run vendor code, call a model, trade, or silently modify inputs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

def hash_file(path):
    digest = hashlib.sha256()
    size = 0
    with Path(path).open("rb") as source:
        while True:
            block = source.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            size += len(block)
    return {"sha256": digest.hexdigest(), "bytes": size}

def build_manifest(root, paths, model_version, git_sha):
    root = Path(root).resolve()
    if not paths or not isinstance(model_version, str) or not model_version.strip():
        raise ValueError("Inputs y versión de modelo obligatorios")
    items = []
    for name in sorted(set(paths)):
        p = (root / name).resolve()
        if not p.is_relative_to(root) or not p.is_file() or p.is_symlink():
            raise ValueError("Input ausente, enlace o fuera de repositorio")
        info = hash_file(p)
        items.append({"path": p.relative_to(root).as_posix(), **info})
    payload = {"schema_version": 1, "model_version": model_version, "git_sha": git_sha, "inputs": items}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return {"payload": payload, "payload_sha256": hashlib.sha256(raw).hexdigest()}

def write_new(output, manifest):
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as dest:
        json.dump(manifest, dest, sort_keys=True, ensure_ascii=False, indent=2)
        dest.write("\n")

def verify(root, manifest):
    payload = manifest["payload"]
    current = build_manifest(root, [x["path"] for x in payload["inputs"]],
                             payload["model_version"], payload["git_sha"])
    return current == manifest

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--input", action="append", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--commit-sha", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    manifest = build_manifest(args.root, args.input, args.version, args.commit_sha)
    write_new(args.output, manifest)
    print(json.dumps({"manifest_sha256": manifest["payload_sha256"], "verified": verify(args.root, manifest)}))
