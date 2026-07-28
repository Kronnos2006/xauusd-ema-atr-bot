"""
Verificacion de integridad de datos -- implementa los 3 chequeos de la
skill `data-integrity`.

1. Checksum SHA256, registrado en registro_checksums.json (versionado en
   git a proposito, a diferencia de los datos crudos que ignora
   historial/ -- el registro tiene que sobrevivir aunque el dato no).
2. Continuidad temporal: huecos > N dias, duplicados, rango plausible.
3. Revision retroactiva vs fuente publica (ALFRED/FRED) -- generaliza el
   chequeo ya hecho a mano para DFII10 (ver metricas_dfii10.py /
   Macro DFII10 - fase 1.md#Auditoria de robustez).
"""
import hashlib
import json
import os
import sys
from datetime import datetime

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RUTA_REGISTRO = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\registro_checksums.json"


# ============================================================
# 1. Checksum
# ============================================================

def calcular_checksum(ruta_archivo):
    h = hashlib.sha256()
    with open(ruta_archivo, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def registrar_checksum(ruta_archivo, ruta_registro=RUTA_REGISTRO):
    checksum = calcular_checksum(ruta_archivo)
    nombre = os.path.basename(ruta_archivo)

    registro = {}
    if os.path.exists(ruta_registro):
        with open(ruta_registro, "r", encoding="utf-8") as f:
            registro = json.load(f)

    anterior = registro.get(nombre, {}).get("sha256")
    cambio = anterior is not None and anterior != checksum

    registro[nombre] = {
        "sha256": checksum,
        "ultima_verificacion": datetime.now().isoformat(),
        "tamano_bytes": os.path.getsize(ruta_archivo),
    }
    with open(ruta_registro, "w", encoding="utf-8") as f:
        json.dump(registro, f, indent=2, ensure_ascii=False, sort_keys=True)

    if cambio:
        print(f"⚠️  {nombre}: checksum CAMBIÓ desde la última verificación "
              f"({anterior[:12]}... -> {checksum[:12]}...) -- revisar si el cambio fue intencional.")
    else:
        estado = "nuevo registro" if anterior is None else "sin cambios"
        print(f"✅ {nombre}: {checksum[:12]}... ({estado})")
    return checksum, cambio


# ============================================================
# 2. Continuidad temporal
# ============================================================

def verificar_continuidad(df, columna_fecha, max_hueco_dias=7, rango_valido=None, columna_valor=None):
    """rango_valido: (min, max) opcional, aplicado sobre columna_valor.
    Devuelve un dict con los hallazgos -- no lanza excepcion, deja que
    quien llama decida que hacer con cada uno."""
    fechas = pd.to_datetime(df[columna_fecha]).sort_values().reset_index(drop=True)
    hallazgos = {"duplicados": 0, "huecos": [], "fuera_de_rango": 0}

    duplicados = fechas[fechas.duplicated()]
    hallazgos["duplicados"] = len(duplicados)

    diffs = fechas.diff().dt.days.dropna()
    huecos = diffs[diffs > max_hueco_dias]
    for idx in huecos.index:
        hallazgos["huecos"].append({
            "desde": str(fechas.iloc[idx - 1].date()),
            "hasta": str(fechas.iloc[idx].date()),
            "dias": int(huecos.loc[idx]),
        })

    if rango_valido and columna_valor:
        vals = pd.to_numeric(df[columna_valor], errors="coerce")
        fuera = vals[(vals < rango_valido[0]) | (vals > rango_valido[1])]
        hallazgos["fuera_de_rango"] = len(fuera)

    print(f"Filas: {len(df)} | Duplicados: {hallazgos['duplicados']} | "
          f"Huecos > {max_hueco_dias}d: {len(hallazgos['huecos'])} | "
          f"Fuera de rango: {hallazgos['fuera_de_rango']}")
    for h in hallazgos["huecos"][:10]:
        print(f"  hueco: {h['desde']} -> {h['hasta']} ({h['dias']}d)")
    if len(hallazgos["huecos"]) > 10:
        print(f"  ... y {len(hallazgos['huecos']) - 10} más")

    return hallazgos


# ============================================================
# 3. Revision retroactiva vs fuente publica (FRED/ALFRED)
# ============================================================

def verificar_revision_fred(series_id, fechas_muestra, dias_vintage=10):
    """Generaliza el chequeo hecho a mano para DFII10: para cada fecha en
    fechas_muestra, compara el valor 'tal como se publico entonces'
    (ALFRED, vintage_date = fecha + dias_vintage) contra el valor actual
    de FRED. Requiere conexion a internet; usa curl via subprocess para
    no agregar una dependencia nueva (requests) al proyecto."""
    import subprocess

    diferencias = []
    for fecha in fechas_muestra:
        fecha_str = pd.Timestamp(fecha).strftime("%Y-%m-%d")
        vintage = (pd.Timestamp(fecha) + pd.Timedelta(days=dias_vintage)).strftime("%Y-%m-%d")

        url_vintage = (f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
                       f"&vintage_date={vintage}&cosd={fecha_str}&coed={fecha_str}")
        url_actual = (f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
                      f"&cosd={fecha_str}&coed={fecha_str}")

        out_vintage = subprocess.run(["curl", "-s", url_vintage], capture_output=True, text=True, timeout=30).stdout
        out_actual = subprocess.run(["curl", "-s", url_actual], capture_output=True, text=True, timeout=30).stdout

        def _extraer_valor(csv_text):
            lineas = [l for l in csv_text.strip().split("\n") if l and "," in l]
            if len(lineas) < 2:
                return None
            return lineas[1].split(",")[1]

        v_vintage = _extraer_valor(out_vintage)
        v_actual = _extraer_valor(out_actual)
        coincide = v_vintage == v_actual
        diferencias.append({"fecha": fecha_str, "real_time": v_vintage, "actual": v_actual, "coincide": coincide})
        estado = "✅" if coincide else "⚠️  DIFIERE"
        print(f"  {fecha_str} | real-time={v_vintage} | actual={v_actual}  {estado}")

    n_diff = sum(1 for d in diferencias if not d["coincide"])
    if n_diff:
        print(f"\n⚠️  {n_diff}/{len(diferencias)} fechas con diferencia -- revisar si son revisiones "
              f"esperables o contaminación de look-ahead en un backtest ya corrido.")
    else:
        print(f"\n✅ {len(diferencias)}/{len(diferencias)} fechas coinciden -- sin revisión detectada.")
    return diferencias


if __name__ == "__main__":
    print("=== Registrando checksums de los archivos macro en uso ===\n")
    archivos = [
        r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\dfii10.csv",
        r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\t10y2y.csv",
        r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\dxy_sintetico.csv",
    ]
    for archivo in archivos:
        if os.path.exists(archivo):
            registrar_checksum(archivo)
        else:
            print(f"(no encontrado, omitido: {archivo})")

    print("\n=== Continuidad temporal: DFII10 ===")
    df_dfii10 = pd.read_csv(archivos[0])
    df_dfii10.columns = ["fecha", "dfii10"]
    df_dfii10["dfii10"] = pd.to_numeric(df_dfii10["dfii10"], errors="coerce")
    df_dfii10 = df_dfii10.dropna(subset=["dfii10"])
    verificar_continuidad(df_dfii10, "fecha", max_hueco_dias=7, rango_valido=(-5, 15), columna_valor="dfii10")
