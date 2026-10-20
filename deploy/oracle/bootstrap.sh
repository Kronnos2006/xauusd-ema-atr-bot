#!/usr/bin/env bash
# Ejecutar en el checkout de Ubuntu 24.04 ARM, como usuario sin privilegios.
set -euo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
TASK_DATA_DIR="${KRONOS_DATA_DIR:-$PROJECT_DIR/panel}"
export HF_HOME="${HF_HOME:-$TASK_DATA_DIR/huggingface}"
export KRONOS_TORCH_THREADS=2
python3 - <<'PY'
import os, platform, shutil, sys
if sys.version_info[:2] != (3,12):
    raise SystemExit('Se requiere Python 3.12 (Ubuntu 24.04)')
if platform.system() != 'Linux' or platform.machine() != 'aarch64':
    raise SystemExit('Este instalador esta destinado a Linux ARM64/aarch64')
if shutil.disk_usage('.').free < 10*1024**3:
    raise SystemExit('Se requieren al menos 10 GiB de disco libre')
with open('/proc/meminfo') as f:
    available=next(int(line.split()[1])*1024 for line in f if line.startswith('MemAvailable:'))
if available < 4*1024**3:
    raise SystemExit('Se requieren al menos 4 GiB de memoria disponible')
print('Preflight Linux ARM: correcto; faltan instalacion e inferencia real')
PY
cd -- "$PROJECT_DIR"
python3 -m venv tools/kronos-env
PYTHON_BIN="$PROJECT_DIR/tools/kronos-env/bin/python"
"$PYTHON_BIN" -m pip install -r deploy/oracle/requirements.txt
checkout_pinned() {
  local url="$1" destination="$2" revision="$3"
  if [[ ! -d "$destination" ]]; then
    git clone --filter=blob:none --no-checkout "$url" "$destination"
    if [[ "$destination" == 'tools/timesfm-upstream' ]]; then
      # Solo paquete y ficheros raiz; evita imagenes LFS de ejemplos no utilizados.
      git -C "$destination" sparse-checkout init --cone
      git -C "$destination" sparse-checkout set src
    fi
    git -C "$destination" checkout --detach "$revision"
  fi
  [[ "$(git -C "$destination" rev-parse HEAD)" == "$revision" ]] || {
    echo "Revision inesperada en $destination. No se cambia automaticamente." >&2; exit 1;
  }
  [[ -z "$(git -C "$destination" status --porcelain --untracked-files=no)" ]] || {
    echo "Upstream modificado: $destination" >&2; exit 1;
  }
}
checkout_pinned https://github.com/shiyu-coder/Kronos.git tools/kronos-upstream 67b630e67f6a18c9e9be918d9b4337c960db1e9a
checkout_pinned https://github.com/google-research/timesfm.git tools/timesfm-upstream e51928e27119cb17bebc005be2696b75e0a9e688
"$PYTHON_BIN" -m pip install --no-build-isolation ./tools/timesfm-upstream
"$PYTHON_BIN" -m pip check
mkdir -p -- "$TASK_DATA_DIR"
"$PYTHON_BIN" tools/kronos_timesfm_smoke.py --progress --output-dir "$TASK_DATA_DIR/arm-smoke"
echo 'Inferencia sintetica ARM completada. Aun no se activa la generacion de mercado.'
