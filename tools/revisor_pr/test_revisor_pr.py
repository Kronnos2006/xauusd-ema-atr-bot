"""Pruebas del revisor con un repo git sintetico. Sin red ni IA."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import revisor_pr  # noqa: E402


def sh(cwd, *args):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


class RevisorTest(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.tmp = Path(temporal.name)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        sh(self.repo, "git", "init", "-q", "-b", "master")
        sh(self.repo, "git", "config", "user.email", "t@t")
        sh(self.repo, "git", "config", "user.name", "t")
        (self.repo / "bot").mkdir()
        (self.repo / "bot" / "mt5.py").write_text("ACCOUNT_TRADE_MODE_DEMO\norder_send(x)\n")
        sh(self.repo, "git", "add", ".")
        sh(self.repo, "git", "commit", "-qm", "base")
        sh(self.repo, "git", "checkout", "-qb", "pr")
        self.reglas = self.tmp / "reglas.json"

    def commit(self, ruta, texto):
        f = self.repo / ruta
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(texto)
        sh(self.repo, "git", "add", ".")
        sh(self.repo, "git", "commit", "-qm", "cambio")

    def correr(self, reglas):
        self.reglas.write_text(json.dumps(reglas))
        return revisor_pr.main(["--repo", str(self.repo), "--base", "master",
                                "--head", "pr", "--reglas", str(self.reglas)])

    def test_cambio_limpio_pasa(self):
        self.commit("bot/mt5.py", "ACCOUNT_TRADE_MODE_DEMO\norder_send(y)\n")
        self.assertEqual(self.correr({
            "rutas_prohibidas": ["data/*"], "rutas_permitidas": ["bot/*"],
            "invariantes": [{"nombre": "demo", "archivo": "bot/mt5.py",
                             "debe_contener": ["ACCOUNT_TRADE_MODE_DEMO"],
                             "max_apariciones": ["order_send\\(", 1]}],
            "pruebas": [{"nombre": "ok", "comando": "true"}]}), 0)

    def test_ruta_prohibida_falla(self):
        self.commit("data/kt002.csv", "x")
        self.assertEqual(self.correr({"rutas_prohibidas": ["data/*"]}), 1)

    def test_fuera_de_alcance_falla(self):
        self.commit("docs/nota.md", "x")
        self.assertEqual(self.correr({"rutas_permitidas": ["bot/*"]}), 1)

    def test_quitar_el_bloqueo_demo_falla(self):
        self.commit("bot/mt5.py", "order_send(x)\n")
        self.assertEqual(self.correr({"invariantes": [{
            "nombre": "demo", "archivo": "bot/mt5.py",
            "debe_contener": ["ACCOUNT_TRADE_MODE_DEMO"]}]}), 1)

    def test_anulacion_prohibida_falla(self):
        self.commit("bot/mt5.py", "ACCOUNT_TRADE_MODE_DEMO\nforzar_real=True\n")
        self.assertEqual(self.correr({"invariantes": [{
            "nombre": "demo", "archivo": "bot/mt5.py",
            "no_debe_contener": ["(?i)forzar_?real"]}]}), 1)

    def test_segundo_order_send_falla(self):
        self.commit("bot/mt5.py", "ACCOUNT_TRADE_MODE_DEMO\norder_send(a)\norder_send(b)\n")
        self.assertEqual(self.correr({"invariantes": [{
            "nombre": "demo", "archivo": "bot/mt5.py",
            "max_apariciones": ["order_send\\(", 1]}]}), 1)

    def test_detecta_otro_envio_fuera_del_bot(self):
        self.commit("otra carpeta/mt5.py", "mt5.order_send(\n    req,\n)\n")
        self.assertEqual(self.correr({"archivo_envio_mt5": "bot/mt5.py"}), 1)

    def test_no_cuenta_comentarios_ni_textos_como_envios(self):
        self.commit("otra carpeta/mt5.py", '# mt5.order_send(req)\ntexto = "order_send(req)"\n')
        self.assertEqual(self.correr({"archivo_envio_mt5": "bot/mt5.py"}), 0)

    def test_exige_la_llamada_en_el_adaptador(self):
        self.commit("bot/mt5.py", "# order_send(req)\n")
        self.assertEqual(self.correr({"archivo_envio_mt5": "bot/mt5.py"}), 1)

    def test_rechaza_mover_una_ruta_prohibida_hacia_el_bot(self):
        sh(self.repo, "git", "checkout", "-q", "master")
        self.commit("data/registro.txt", "x")
        sh(self.repo, "git", "checkout", "-q", "pr")
        sh(self.repo, "git", "merge", "--ff-only", "master")
        sh(self.repo, "git", "mv", "data/registro.txt", "bot/registro.txt")
        sh(self.repo, "git", "commit", "-qm", "mover")
        self.assertEqual(self.correr({"rutas_prohibidas": ["data/*"]}), 1)

    def test_prueba_roja_falla(self):
        self.commit("bot/mt5.py", "ACCOUNT_TRADE_MODE_DEMO\norder_send(z)\n")
        self.assertEqual(self.correr({"pruebas": [{"nombre": "roja", "comando": "false"}]}), 1)

    def test_aislamiento_usa_docker_sin_red_y_sin_salida_del_pr(self):
        self.commit("bot/prueba.py", "pass\n")
        ejecutar = subprocess.run
        invocaciones = []

        def docker_simulado(args, **kwargs):
            if args[0] != "docker":
                return ejecutar(args, **kwargs)
            invocaciones.append((args, kwargs))
            return subprocess.CompletedProcess(args, 0)

        informe = revisor_pr.Informe("master", "pr")
        reglas = {"pruebas": [{"nombre": "bot", "directorio": "bot", "comando": "python3 prueba.py"}]}
        with patch.object(revisor_pr.subprocess, "run", side_effect=docker_simulado):
            revisor_pr.revisar_pruebas(self.repo, "pr", reglas, informe, aislar=True)
        self.assertTrue(informe.pasa)
        [(args, kwargs)] = invocaciones
        self.assertIn("--network=none", args)
        self.assertIn("--read-only", args)
        self.assertIn("--user=65534:65534", args)
        montajes = [arg for arg in args if arg.startswith("--mount=")]
        self.assertEqual(len(montajes), 1)
        self.assertTrue(montajes[0].endswith("/bot,dst=/bot,readonly"))
        self.assertEqual(kwargs["stdout"], subprocess.DEVNULL)
        self.assertEqual(kwargs["stderr"], subprocess.DEVNULL)

    def test_aviso_no_bloquea(self):
        self.commit("bot/a.py", "x")
        self.commit("bot/b.py", "x")
        self.assertEqual(self.correr({"max_archivos": 1}), 0)

    def test_no_toca_el_checkout_del_repo(self):
        self.commit("bot/mt5.py", "ACCOUNT_TRADE_MODE_DEMO\norder_send(z)\n")
        sh(self.repo, "git", "checkout", "-q", "master")
        self.correr({"pruebas": [{"nombre": "ok", "comando": "true"}]})
        rama = subprocess.run(["git", "branch", "--show-current"], cwd=self.repo,
                              capture_output=True, text=True).stdout.strip()
        self.assertEqual(rama, "master")
        arboles = subprocess.run(["git", "worktree", "list"], cwd=self.repo,
                                 capture_output=True, text=True).stdout.strip().splitlines()
        self.assertEqual(len(arboles), 1)


if __name__ == "__main__":
    unittest.main()
