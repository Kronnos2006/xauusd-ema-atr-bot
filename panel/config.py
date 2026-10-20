"""Configuracion portable. Los defaults mantienen el panel local existente."""
import os
from pathlib import Path

PROJECT=Path(__file__).resolve().parent.parent


def model_python():
    override=os.environ.get('KRONOS_PYTHON')
    if override:
        return Path(override).expanduser().resolve()
    candidates=[PROJECT/'tools/kronos-env/Scripts/python.exe',
                PROJECT/'tools/kronos-env/bin/python',PROJECT/'.venv/bin/python']
    return next((p for p in candidates if p.is_file()),candidates[0])


def data_directory():
    return Path(os.environ.get('KRONOS_DATA_DIR',str(PROJECT/'panel'))).expanduser().resolve()
