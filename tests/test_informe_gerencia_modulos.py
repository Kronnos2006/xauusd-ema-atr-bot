import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import csv,json
from datetime import datetime,timezone
from informe_gerencia_sin_ia import generate,inspect_modules,inspect_kt002
class Tests(unittest.TestCase):
    def test_missing_evidence_never_promotes(self):
        with tempfile.TemporaryDirectory() as folder:
            r=inspect_modules(Path(folder))
            self.assertEqual(r["kronnos"]["kt002_operativo"],"NO_VERIFICADO")
            self.assertFalse(r["atlas"]["promocion_permitida"])
            self.assertEqual(r["orion"]["servicio_operativo"],"NO_VERIFICADO")
    def test_output_includes_three_modules(self):
        r=generate(Path(__file__).resolve().parents[1])
        self.assertEqual(set(r["modulos"]),{"kronnos","orion","atlas"})
        self.assertFalse(r["modulos"]["atlas"]["promocion_permitida"])
    def _kt002(self,folder,aciertos_resumen):
        d=Path(folder)/"data/kt002";d.mkdir(parents=True)
        cols=["run_utc","base_open_utc","actual_ret","kronos_hit","timesfm_hit","kt001_hit"]
        rows=[["2026-10-30T12:07:00+00:00","2026-10-30T08:00:00+00:00","0.01","1","0","1"],
              ["2026-10-30T13:07:00+00:00","2026-10-30T09:00:00+00:00","-0.01","1","1","1"],
              ["2026-10-30T14:07:00+00:00","2026-10-30T13:00:00+00:00","","","",""]]
        with open(d/"predicciones.csv","w",newline="") as f:
            w=csv.writer(f);w.writerow(cols);w.writerows(rows)
        s={"pronosticos":3,"vencidos":2,"sin_solape":{"kronos":{"aciertos":aciertos_resumen},"timesfm":{"aciertos":0},"kt001":{"aciertos":1},"siempre_sube":{"aciertos":1}}}
        (d/"resumen.json").write_text(json.dumps(s))
    def test_kt002_verificado_recalcula(self):
        with tempfile.TemporaryDirectory() as folder:
            self._kt002(folder,1)
            r=inspect_kt002(Path(folder),now=datetime(2026,10,30,15,0,tzinfo=timezone.utc))
            self.assertEqual(r["estado"],"VERIFICADO")
            self.assertEqual(r["sin_solape"]["kronos"],{"aciertos":1,"n":1})
    def test_kt002_inconsistente_y_atrasado(self):
        with tempfile.TemporaryDirectory() as folder:
            self._kt002(folder,5)
            self.assertEqual(inspect_kt002(Path(folder),now=datetime(2026,10,30,15,0,tzinfo=timezone.utc))["estado"],"INCONSISTENTE")
        with tempfile.TemporaryDirectory() as folder:
            self._kt002(folder,1)
            self.assertEqual(inspect_kt002(Path(folder),now=datetime(2026,10,31,15,0,tzinfo=timezone.utc))["estado"],"ATRASADO")
if __name__=="__main__":unittest.main()
