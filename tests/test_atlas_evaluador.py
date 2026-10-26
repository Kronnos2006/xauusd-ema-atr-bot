import unittest
from atlas.evaluador import evaluar

class TestEvaluacionProspectiva(unittest.TestCase):
    def test_abstencion_evito_error_y_descarto_acierto(self):
        base = dict(publicada_utc="2026-10-24T05:30:00Z", vence_utc="2026-10-24T09:23:00Z",
                    puntuada_utc="2026-10-24T09:25:00Z", direccion_modelo=1,
                    sello_externo_verificado=True, decision_atlas="ABSTENERSE")
        r = evaluar([dict(base, id="a", retorno_real=-.00203), dict(base, id="b", retorno_real=.01)])
        self.assertEqual(r["errores_modelo_evitados"], 1)
        self.assertEqual(r["aciertos_modelo_descartados"], 1)
    def test_prohibe_resultado_previo_y_sello_no_validado(self):
        f = dict(id="a", publicada_utc="2026-10-24T09:30:00Z", vence_utc="2026-10-24T09:23:00Z",
                 puntuada_utc="2026-10-24T09:15:00Z", direccion_modelo=1, retorno_real=.1,
                 sello_externo_verificado=False, decision_atlas="ABSTENERSE")
        r = evaluar([f])
        self.assertEqual(r["validas"], 0)
        self.assertEqual(len(r["rechazadas_por_integridad"]), 1)

if __name__ == "__main__":
    unittest.main()
