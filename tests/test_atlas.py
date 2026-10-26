"""Pruebas de ORION–ATLAS: contratos, procedencia, ausencia de look-ahead, abstención, contradicciones,
casos adversos del piloto, registro inalterable, máquina de estados y aislamiento respecto de KT-002."""
import datetime as dt
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from atlas import analitica as an
from atlas.contradicciones import revisar
from atlas.datos import PrediccionesKT002, VelasArchivo
from atlas.piloto import (PROSP, RETRO, analizar, cargar_instantanea, evaluar, exigir_prediccion_reciente, guardar,
                          guardar_instantanea, main as piloto_main, obtener, sellar_prospectiva, validar_prospectiva)
from atlas.procedencia import Registro, cobertura_faltante, discrepancia
from atlas.tesis import Registro as RegistroTesis, TransicionInvalida, transicion

RAIZ = Path(__file__).resolve().parent.parent
CONTRATOS = RAIZ / "docs" / "arquitectura" / "contratos"
CORTE = dt.datetime(2026, 3, 1, 0, 0, tzinfo=dt.timezone.utc)
CAB = ("run_utc,base_open_utc,base_close,target_open_utc,kronos_close4,timesfm_close4,kt001_close4,kronos_ret,"
       "timesfm_ret,kt001_ret,actual_close4,actual_ret,kronos_hit,timesfm_hit,kt001_hit,scored_utc,elapsed_s\n")


def esquemas():
    s = {p.stem.replace(".schema", ""): json.loads(p.read_text()) for p in CONTRATOS.glob("*.schema.json")}
    reg = Registry().with_resources([(v["$id"], Resource.from_contents(v)) for v in s.values()])
    return s, reg


def escenario(d: Path, tendencia=+1, ret_pred=(0.01, 0.01, 0.01), dias_viejos=0, spread=0.00001, eventos=None,
              fila_futura=False):
    """Datos sintéticos en d/data/... con la misma forma que los del repo."""
    (d / "data/mercado").mkdir(parents=True)
    (d / "data/kt002").mkdir(parents=True)
    fin = CORTE - dt.timedelta(days=1 + dias_viejos)
    velas, p = [], 100.0
    for i in range(260, 0, -1):
        abre = fin - dt.timedelta(days=i - 1)
        p *= 1 + 0.002 * tendencia
        velas.append([int(abre.timestamp() * 1000), p, p, p, p, 1000.0 + i])
    if fila_futura:  # vela que cierra después del corte: debe excluirse
        velas.append([int(CORTE.timestamp() * 1000), 1e9, 1e9, 1e9, 1e9, 1.0])
    (d / "data/mercado/btc_1d.json").write_text(json.dumps(velas))
    (d / "data/mercado/spread_btcusdt.csv").write_text(
        "utc,bid,ask,spread_pct,desliz_compra_1k_pct,desliz_compra_10k_pct,desliz_compra_100k_pct\n"
        f"{(CORTE - dt.timedelta(hours=1)).isoformat()},1,1,{spread},0,0,0\n")
    run = CORTE - dt.timedelta(hours=1)
    base = CORTE - dt.timedelta(hours=2)
    k, tf, kt = ret_pred
    filas = [f"{run.isoformat()},{base.isoformat()},100,{(base + dt.timedelta(hours=4)).isoformat()},0,0,0,{k},{tf},{kt},,,,,,,1\n"]
    # fila con resultado puntuado DESPUÉS del corte: la puntuación debe ocultarse
    b0 = CORTE - dt.timedelta(hours=4)
    filas.insert(0, f"{(b0 + dt.timedelta(minutes=30)).isoformat()},{b0.isoformat()},100,{(b0 + dt.timedelta(hours=4)).isoformat()},"
                    f"0,0,0,0.01,0.01,0.01,101,0.01,1,1,1,{(CORTE + dt.timedelta(hours=1)).isoformat()},1\n")
    (d / "data/kt002/predicciones.csv").write_text(CAB + "".join(filas))
    if eventos is not None:
        (d / "eventos.json").write_text(json.dumps(eventos))
    return d


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def piloto(self, **kw):
        ev = kw.get("eventos")
        escenario(self.tmp, **kw)
        return evaluar(CORTE, self.tmp, "eventos.json" if ev is not None else None)


class Contratos(Base):
    def test_esquemas_validos_y_salida_del_piloto_cumple(self):
        s, reg = esquemas()
        for v in s.values():
            Draft202012Validator.check_schema(v)
        tesis = self.piloto()
        Draft202012Validator(s["tesis"], registry=reg, format_checker=FormatChecker()).validate(tesis)
        for e in tesis["evidencia"]:
            Draft202012Validator(s["evidencia"]).validate(e)

    def test_estrategia_no_puede_depender_de_llm(self):
        s, _ = esquemas()
        doc = {"id": "ES-900", "tesis_id": "TS-0", "preregistro": {"ruta": "x", "hash_sha256": "0" * 64, "fecha_utc": "2026-10-24T00:00:00Z"},
               "reglas": {"entrada": "a", "salida": "b", "tamano": "c", "usa_salida_llm": True},
               "costos": {"comision_pct": 0.1, "spread_pct": 0.01, "deslizamiento_pct": 0.05}, "limites_riesgo": {},
               "validacion": {"walk_forward": "x", "dsr": 0.96, "neto_de_costos": True}, "estado": "borrador"}
        self.assertFalse(Draft202012Validator(s["strategy_spec"]).is_valid(doc))


class SinLookAhead(Base):
    def test_vela_que_cierra_despues_del_corte_se_excluye(self):
        escenario(self.tmp, fila_futura=True)
        v = VelasArchivo(self.tmp / "data/mercado/btc_1d.json", "1d").obtener(CORTE)
        self.assertTrue(all(dt.datetime.fromisoformat(r.utilizable_utc) <= CORTE for r in v))
        self.assertNotIn(1e9, [r.valor["c"] for r in v])

    def test_resultado_puntuado_despues_del_corte_se_oculta(self):
        escenario(self.tmp)
        p = PrediccionesKT002(self.tmp / "data/kt002/predicciones.csv").obtener(CORTE)
        self.assertEqual(p[0].valor["actual_ret"], "")
        self.assertEqual(an.historial_modelo(p, "kronos")["n_sin_solape"], 0)

    def test_registro_futuro_inyectado_vuelve_insuficiente(self):
        escenario(self.tmp)
        futuro = Registro("x", "y", "BTCUSDT", "vela_1d", {"c": 1}, None, None, None,
                          (CORTE + dt.timedelta(hours=1)).isoformat(), "validado")
        ev = [an.tendencia(VelasArchivo(self.tmp / "data/mercado/btc_1d.json", "1d").obtener(CORTE))]
        r = revisar(1, ev, [futuro], CORTE)
        self.assertEqual(r["conclusion"], "INSUFICIENTE")


class CasosAdversos(Base):
    def test_sano_sin_respaldo_independiente_se_abstiene(self):
        t = self.piloto()  # tendencia y predicción alineadas, pero sin ventaja demostrada
        self.assertNotEqual(t["contradicciones"]["conclusion"], "FAVORABLE_CONTINUAR")
        self.assertEqual(t["contradicciones"]["decision_investigacion"], "ABSTENERSE")

    def test_noticias_contradictorias(self):
        ev = [{"fuente": "A", "url": "u1", "publicado_utc": "2026-02-28T10:00:00Z", "hecho": "x", "direccion": 1},
              {"fuente": "B", "url": "u2", "publicado_utc": "2026-02-28T11:00:00Z", "hecho": "y", "direccion": -1}]
        t = self.piloto(eventos=ev)
        self.assertEqual(t["contradicciones"]["conclusion"], "CONTRADICTORIA")

    def test_fuente_sin_disponibilidad_temporal(self):
        ev = [{"fuente": "C", "url": "u3", "publicado_utc": None, "hecho": "z", "direccion": 1}]
        t = self.piloto(eventos=ev)
        self.assertTrue(any("sin disponibilidad temporal" in h["pregunta"] for h in t["contradicciones"]["hallazgos"]))
        e = next(x for x in t["evidencia"] if x["modulo"] == "noticias.eventos")
        self.assertEqual(e["medicion"], {})  # excluida de verdad, no solo etiquetada

    def test_datos_desactualizados(self):
        t = self.piloto(dias_viejos=5)
        self.assertEqual(t["contradicciones"]["conclusion"], "INSUFICIENTE")

    def test_fallo_de_proveedor(self):
        escenario(self.tmp)
        (self.tmp / "data/mercado/btc_1d.json").unlink()
        t = evaluar(CORTE, self.tmp)
        self.assertEqual(t["contradicciones"]["conclusion"], "INSUFICIENTE")
        self.assertTrue(any("tendencia" in x for x in t["datos_faltantes"]))

    def test_modelos_en_desacuerdo(self):
        t = self.piloto(ret_pred=(0.01, -0.01, 0.0001))
        self.assertTrue(any(h["pregunta"].startswith("¿Los modelos coinciden") for h in t["contradicciones"]["hallazgos"]))
        self.assertEqual(t["contradicciones"]["decision_investigacion"], "ABSTENERSE")

    def test_sin_liquidez(self):
        t = self.piloto(spread=1.0)
        self.assertEqual(t["contradicciones"]["conclusion"], "INSUFICIENTE")

    def test_tendencia_contraria_a_la_prediccion(self):
        t = self.piloto(tendencia=-1)
        self.assertIn("Régimen diario BAJISTA", " ".join(t["evidencia_contraria"]))
        self.assertEqual(t["contradicciones"]["decision_investigacion"], "ABSTENERSE")

    def test_favorable_exige_ventaja_demostrada(self):
        escenario(self.tmp)
        ev = [an.Evidencia("tecnico.a", "a", "hecho", 1, {}, []), an.Evidencia("tecnico.b", "b", "hecho", 1, {}, []),
              an.Evidencia("predictivo.kt001", "p", "inferencia", 1, {"ret_predicho": 0.02, "aciertos": 70,
                           "n_sin_solape": 120, "siempre_sube_aciertos": 50, "ventaja_demostrada": True}, [])]
        regs = obtener(CORTE, self.tmp)
        r = revisar(1, ev, regs, CORTE)
        self.assertEqual(r["conclusion"], "FAVORABLE_CONTINUAR")
        self.assertEqual(r["decision_investigacion"], "CONTINUAR_INVESTIGANDO")  # nunca una orden
        ev[2].medicion["ventaja_demostrada"] = False
        self.assertNotEqual(revisar(1, ev, regs, CORTE)["conclusion"], "FAVORABLE_CONTINUAR")


class Auditoria20261024(Base):
    """Casos pedidos por el desconfiado (auditoría del PR #34)."""

    def test_modelo_contrario_con_ventaja_no_da_favorable(self):
        escenario(self.tmp)
        ev = [an.Evidencia("tecnico.a", "a", "hecho", 1, {}, []), an.Evidencia("tecnico.b", "b", "hecho", 1, {}, []),
              an.Evidencia("predictivo.kronos", "k", "inferencia", -1, {"ret_predicho": -0.02, "aciertos": 70,
                           "n_sin_solape": 120, "siempre_sube_aciertos": 50, "ventaja_demostrada": True}, [])]
        r = revisar(1, ev, obtener(CORTE, self.tmp), CORTE)
        self.assertNotEqual(r["conclusion"], "FAVORABLE_CONTINUAR")
        self.assertIn("k", r["contra"])

    def test_ventaja_nunca_sale_de_datos_descriptivos(self):
        escenario(self.tmp)
        p = PrediccionesKT002(self.tmp / "data/kt002/predicciones.csv").obtener(CORTE)
        self.assertFalse(an.historial_modelo(p, "kronos")["ventaja_demostrada"])
        self.assertTrue(an.historial_modelo(p, "kronos", {"kronos": "EC-001"})["ventaja_demostrada"])

    def test_sin_predicciones_insuficiente_y_sin_hipotesis_inventada(self):
        escenario(self.tmp)
        (self.tmp / "data/kt002/predicciones.csv").write_text(CAB)
        t = evaluar(CORTE, self.tmp)
        self.assertEqual(t["contradicciones"]["conclusion"], "INSUFICIENTE")
        self.assertTrue(t["hipotesis"].startswith("sin hipótesis direccional"))

    def test_prediccion_nula_insuficiente(self):
        t = self.piloto(ret_pred=(0.0, 0.0, 0.0))
        self.assertEqual(t["contradicciones"]["conclusion"], "INSUFICIENTE")
        self.assertNotIn("sube", t["hipotesis"])

    def test_prediccion_vieja_insuficiente(self):
        escenario(self.tmp)
        t = evaluar(CORTE + dt.timedelta(hours=4), self.tmp)  # última predicción de hace 5 h
        self.assertEqual(t["contradicciones"]["conclusion"], "INSUFICIENTE")

    def test_spread_viejo_no_se_usa_como_liquidez_actual(self):
        escenario(self.tmp)
        (self.tmp / "data/mercado/spread_btcusdt.csv").write_text(
            "utc,bid,ask,spread_pct,desliz_compra_1k_pct,desliz_compra_10k_pct,desliz_compra_100k_pct\n"
            f"{(CORTE - dt.timedelta(days=30)).isoformat()},1,1,0.00001,0,0,0\n")
        t = evaluar(CORTE, self.tmp)
        liq = next(e for e in t["evidencia"] if e["modulo"] == "mercado.liquidez")
        self.assertEqual(liq["tipo"], "ausente")
        self.assertEqual(t["contradicciones"]["conclusion"], "INSUFICIENTE")

    def test_instantanea_con_resultado_futuro_es_insuficiente(self):
        escenario(self.tmp)
        regs = obtener(CORTE, self.tmp)
        i = next(i for i, r in enumerate(regs) if r.tipo == "prediccion")
        v = dict(regs[i].valor, actual_ret="0.01", kronos_hit="1", scored_utc=(CORTE + dt.timedelta(hours=1)).isoformat())
        regs[i] = Registro(**{**regs[i].como_dict(), "valor": v})
        t = analizar(CORTE, regs)
        self.assertEqual(t["contradicciones"]["conclusion"], "INSUFICIENTE")
        f = guardar_instantanea(regs, "TS-X", self.tmp / "out")
        from atlas.piloto import main
        self.assertEqual(main(["--corte", CORTE.isoformat(), "--validar-instantanea", str(f)]), 1)

    def test_evento_sin_hora_queda_fuera(self):
        ev = [{"fuente": "C", "url": "u3", "publicado_utc": None, "hecho": "z", "direccion": 1},
              {"fuente": "D", "url": "u4", "publicado_utc": "2026-02-28T10:00:00Z", "evento_utc": "2026-03-02T00:00:00Z",
               "hecho": "futuro", "direccion": -1}]
        t = self.piloto(eventos=ev)
        e = next(x for x in t["evidencia"] if x["modulo"] == "noticias.eventos")
        self.assertEqual(e["tipo"], "ausente")
        self.assertNotIn("z", json.dumps(t["efectos_noticias"]))
        self.assertNotIn("futuro", json.dumps(t["efectos_noticias"]))


class Reproducibilidad(Base):
    def test_misma_entrada_misma_huella(self):
        escenario(self.tmp)
        self.assertEqual(evaluar(CORTE, self.tmp)["huella_contenido"], evaluar(CORTE, self.tmp)["huella_contenido"])

    def test_instantanea_reproduce_la_tesis_aunque_cambien_los_datos(self):
        escenario(self.tmp)
        regs = obtener(CORTE, self.tmp)
        t1 = analizar(CORTE, regs)
        f = guardar_instantanea(regs, t1["id"], self.tmp / "out")
        (self.tmp / "data/mercado/btc_1d.json").write_text("[]")  # los datos vivos cambian
        self.assertEqual(analizar(CORTE, cargar_instantanea(f))["huella_contenido"], t1["huella_contenido"])

    def test_salidas_publicadas_se_reproducen(self):
        """Las de la versión vigente se reproducen; las anteriores (p. ej. una prospectiva ya registrada,
        que no se reescribe) deben constar en el registro encadenado con su huella original."""
        from atlas.piloto import VERSION
        registradas = {json.loads(l)["tesis"].get("huella_contenido")
                       for l in (RAIZ / "research/atlas/registro/tesis.jsonl").read_text().splitlines() if l.strip()}
        for f in sorted((RAIZ / "research/atlas/salidas").glob("TS-*Z.json")):
            t = json.loads(f.read_text())
            self.assertIn(t["huella_contenido"], registradas, f.name)
            if t["version_software"] != VERSION:
                continue
            regs = cargar_instantanea(f.with_name(f.stem + ".entradas.json"))
            corte = dt.datetime.fromisoformat(t["corte_utc"])
            self.assertEqual(analizar(corte, regs)["huella_contenido"], t["huella_contenido"], f.name)


class Procedencia(unittest.TestCase):
    def test_discrepancia_conserva_ambas_fuentes(self):
        a = Registro("A", "1", "BTC", "spread", 100.0, None, None, None, "2026-01-01T00:00:00+00:00", "validado")
        b = Registro("B", "2", "BTC", "spread", 110.0, None, None, None, "2026-01-01T00:00:00+00:00", "validado")
        d = discrepancia(a, b, 0.01)
        self.assertEqual(d["valores"], [100.0, 110.0])
        self.assertIsNone(discrepancia(a, a, 0.01))

    def test_cobertura_faltante_no_es_ausencia(self):
        self.assertIn("no es ausencia", cobertura_faltante("x", "BTC", "evento", "m").nota)


class EstadosYRegistro(unittest.TestCase):
    EV = [{"fuente": "Binance", "utilizable_utc": "2026-10-24T00:00:00Z", "descripcion": "dato nuevo"}]

    def test_rechazada_no_pasa_a_aceptada_sin_evidencia_y_revision(self):
        t = {"estado": "RECHAZADA"}
        with self.assertRaises(TransicionInvalida):
            transicion(t, "ACEPTADA_PARA_SIMULACION", "desconfiado", "x")
        with self.assertRaises(TransicionInvalida):
            transicion(t, "INVESTIGACION", "desconfiado", "x")  # sin evidencia nueva
        with self.assertRaises(TransicionInvalida):
            transicion(t, "INVESTIGACION", "desconfiado", "x", ["cualquier cosa"])  # evidencia sin estructura
        for falso in ("Claude", "gpt-4", "a", "rosiver-MLL", "llm"):
            with self.assertRaises(TransicionInvalida):
                transicion(t, "INVESTIGACION", falso, "x", self.EV)
        self.assertEqual(transicion(t, "INVESTIGACION", "desconfiado", "x", self.EV)["estado"], "INVESTIGACION")

    def test_registro_rechaza_saltos_de_estado(self):
        with tempfile.TemporaryDirectory() as d:
            r = RegistroTesis(Path(d) / "t.jsonl")
            with self.assertRaises(TransicionInvalida):
                r.anexar({"id": "TS-1", "estado": "ACEPTADA_PARA_SIMULACION"})  # no puede empezar aceptada
            r.anexar({"id": "TS-1", "estado": "INVESTIGACION"})
            r.anexar({"id": "TS-1", "estado": "INVESTIGACION"})  # reevaluación en el mismo estado
            with self.assertRaises(TransicionInvalida):
                r.anexar({"id": "TS-1", "estado": "ACEPTADA_PARA_SIMULACION"})
            with self.assertRaises(TransicionInvalida):  # transición válida pero sin revisión registrada
                r.anexar({"id": "TS-1", "estado": "RECHAZADA", "revisiones": [{"revisor": "Claude"}]})
            r.anexar({"id": "TS-1", "estado": "RECHAZADA", "revisiones": [{"revisor": "desconfiado"}]})

    def test_ancla_detecta_truncado_reescritura_y_lineas_malformadas(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "t.jsonl"
            r = RegistroTesis(ruta)
            for i in range(3):
                r.anexar({"id": f"TS-{i}", "estado": "INCONCLUSA"})
            ancla = r.ancla()
            self.assertEqual(r.verificar(ancla), [])
            lineas = ruta.read_text().splitlines()
            ruta.write_text("\n".join(lineas[:2]) + "\n")
            self.assertTrue(any("truncado" in e for e in r.verificar(ancla)))
            ruta.unlink()
            for i in range(3):
                r.anexar({"id": f"TS-{i}", "estado": "INVESTIGACION"})  # cadena rehecha entera
            self.assertEqual(r.verificar(), [])                        # sin ancla no se nota…
            self.assertTrue(any("reescrito" in e for e in r.verificar(ancla)))  # …con ancla sí
            ruta.write_text(ruta.read_text() + "{no es json\n")
            self.assertTrue(any("malformada" in e for e in r.verificar()))

    def test_sin_preregistro_no_se_acepta(self):
        with self.assertRaises(TransicionInvalida):
            transicion({"estado": "VALIDACION"}, "ACEPTADA_PARA_SIMULACION", "desconfiado", "x")

    def test_registro_detecta_alteracion(self):
        with tempfile.TemporaryDirectory() as d:
            r = RegistroTesis(Path(d) / "tesis.jsonl")
            r.anexar({"id": "TS-1", "estado": "INCONCLUSA"}); r.anexar({"id": "TS-2", "estado": "INCONCLUSA"})
            self.assertEqual(r.verificar(), [])
            lineas = r.ruta.read_text().splitlines()
            lineas[0] = lineas[0].replace("TS-1", "TS-9")
            r.ruta.write_text("\n".join(lineas) + "\n")
            self.assertTrue(r.verificar())


class Aislamiento(unittest.TestCase):
    def test_no_escribe_en_kt002_y_no_lo_modifica(self):
        csv = RAIZ / "data/kt002/predicciones.csv"
        antes = hashlib.sha256(csv.read_bytes()).hexdigest()
        t = evaluar(dt.datetime(2026, 10, 21, tzinfo=dt.timezone.utc), RAIZ)
        with self.assertRaises(PermissionError):
            guardar(t, RAIZ / "data/kt002")
        self.assertEqual(hashlib.sha256(csv.read_bytes()).hexdigest(), antes)

    def test_atlas_no_importa_nada_de_ejecucion(self):
        fuente = " ".join(p.read_text() for p in (RAIZ / "atlas").glob("*.py"))
        for prohibido in ("ccxt", "MetaTrader5", "create_order", "api_key", "urllib.request", "requests."):
            self.assertNotIn(prohibido, fuente)


class Prospectiva(Base):
    def test_candados_de_tiempo(self):
        h = dt.timedelta
        validar_prospectiva(CORTE, CORTE + h(minutes=30))
        for ahora in (CORTE - h(minutes=1), CORTE + h(minutes=61), CORTE + h(hours=4)):
            with self.assertRaises(ValueError):
                validar_prospectiva(CORTE, ahora)

    def test_hora_de_registro_fuera_de_la_huella(self):
        escenario(self.tmp)
        regs = obtener(CORTE, self.tmp)
        a = analizar(CORTE, regs, PROSP)
        huella = a["huella_contenido"]
        sellar_prospectiva(a, CORTE, CORTE + dt.timedelta(minutes=5))
        b = analizar(CORTE, cargar_instantanea(guardar_instantanea(regs, a["id"], self.tmp / "s")), PROSP)
        self.assertEqual(b["huella_contenido"], huella)
        self.assertEqual(a["vence_utc"], (CORTE + dt.timedelta(hours=4)).isoformat())
        self.assertEqual(a["explicacion_prediccion"]["naturaleza"], PROSP)
        self.assertNotEqual(analizar(CORTE, regs, RETRO)["huella_contenido"], huella)

    def test_exige_prediccion_vigente(self):
        falta = [cobertura_faltante("KT-002", "BTCUSDT", "prediccion", "x")]
        with self.assertRaises(ValueError):
            exigir_prediccion_reciente(falta, CORTE)

    def test_cli_prospectiva_registra_en_cadena(self):
        escenario(self.tmp)
        bases = [r.evento_utc for r in obtener(CORTE, self.tmp) if r.tipo == "prediccion" and r.calidad != "faltante"]
        corte = max(dt.datetime.fromisoformat(b.replace("Z", "+00:00")) for b in bases) + dt.timedelta(hours=1)
        cadena = self.tmp / "tesis.jsonl"
        piloto_main(["--corte", corte.isoformat(), "--raiz", str(self.tmp), "--salida", str(self.tmp / "s"),
                     "--prospectiva", "--registro", str(cadena)], ahora=corte + dt.timedelta(minutes=10))
        linea = json.loads(cadena.read_text().splitlines()[-1])
        self.assertEqual(linea["tesis"]["naturaleza"], "prospectiva")
        self.assertEqual(RegistroTesis(str(cadena)).verificar(), [])



class TestControlesRevisionChatGPT(unittest.TestCase):
    def test_identidad_declarada_no_autoriza_simulacion(self):
        for rol in ("propietario", "desconfiado", "chatgpt-revision", "jefe-riesgo"):
            with self.assertRaises(TransicionInvalida):
                transicion({"estado": "VALIDACION", "preregistro_hash": "no_autenticado"},
                           "ACEPTADA_PARA_SIMULACION", rol, "aprobado verbalmente")

    def test_calidad_de_mercado_no_validada_obliga_abstencion(self):
        from atlas.contradicciones import revisar
        from atlas.procedencia import Registro
        corte = dt.datetime(2026, 3, 1, tzinfo=dt.timezone.utc)
        r = Registro(fuente="prueba", identificador="mercado-no-verificado", activo="BTCUSDT",
                     tipo="spread", valor={"spread_pct": 0.001}, evento_utc=corte.isoformat(),
                     publicado_utc=corte.isoformat(), recibido_utc=None,
                     utilizable_utc=corte.isoformat(), calidad="sin_validar")
        out = revisar(1, [], [r], corte)
        self.assertEqual(out["conclusion"], "INSUFICIENTE")
        self.assertEqual(out["decision_investigacion"], "ABSTENERSE")
        self.assertTrue(any("validados" in h["pregunta"] for h in out["hallazgos"]))

    def test_costo_corresponde_al_modelo_de_la_tesis(self):
        from atlas.contradicciones import revisar
        from atlas.analitica import Evidencia
        corte = dt.datetime(2026, 3, 1, tzinfo=dt.timezone.utc)
        evid = [Evidencia(f"predictivo.{modelo}", "", "inferencia", 1,
                          {"ret_predicho": retorno, "aciertos": 0,
                           "n_sin_solape": 0, "siempre_sube_aciertos": 0}, [])
                for modelo, retorno in (("kronos", 0.01), ("kt001", 0.0001))]
        a = revisar(1, evid, [], corte, modelo_tesis="kronos")
        b = revisar(1, evid, [], corte, modelo_tesis="kt001")
        a_costo = next(h["resultado"] for h in a["hallazgos"] if "supera el costo" in h["pregunta"])
        b_costo = next(h["resultado"] for h in b["hallazgos"] if "supera el costo" in h["pregunta"])
        self.assertIn("1.000%", a_costo)
        self.assertIn("0.010%", b_costo)

if __name__ == "__main__":
    unittest.main()
