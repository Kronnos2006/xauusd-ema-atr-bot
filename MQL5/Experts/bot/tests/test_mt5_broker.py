import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from broker.mt5 import Mt5Broker  # noqa: E402
from contracts import Direction  # noqa: E402


class Mt5DemoOnlyTest(unittest.TestCase):
    def setUp(self):
        self.mt5 = Mock(spec=[
            "initialize", "ORDER_FILLING_IOC", "ACCOUNT_TRADE_MODE_DEMO",
            "ACCOUNT_TRADE_MODE_CONTEST", "ACCOUNT_TRADE_MODE_REAL",
            "account_info", "order_send", "TRADE_RETCODE_DONE", "TRADE_ACTION_DEAL",
            "ORDER_TYPE_BUY", "ORDER_TYPE_SELL", "ORDER_TIME_GTC", "symbol_info_tick",
            "terminal_info", "positions_get", "POSITION_TYPE_BUY",
        ])
        self.mt5.initialize.return_value = True
        self.mt5.ACCOUNT_TRADE_MODE_DEMO = 0
        self.mt5.ACCOUNT_TRADE_MODE_CONTEST = 1
        self.mt5.ACCOUNT_TRADE_MODE_REAL = 2
        self.mt5.account_info.return_value = SimpleNamespace(trade_mode=0)
        self.mt5.TRADE_RETCODE_DONE = 10009
        self.mt5.order_send.return_value = SimpleNamespace(retcode=10009)
        self.mt5.symbol_info_tick.return_value = SimpleNamespace(bid=2400, ask=2401)
        self.mt5.positions_get.return_value = [SimpleNamespace(
            ticket=42, symbol="XAUUSD", type=self.mt5.POSITION_TYPE_BUY,
            volume=0.01, price_open=2401, time=1700000000, magic=123,
        )]
        with patch.dict(sys.modules, {"MetaTrader5": self.mt5}):
            self.broker = Mt5Broker()

    def abrir(self):
        return self.broker.open("XAUUSD", Direction.LONG, 0.01, 123)

    def test_demo_permite_abrir_y_cerrar_con_una_comprobacion_por_envio(self):
        posicion = self.abrir()
        self.assertTrue(self.broker.close(posicion))

        self.assertEqual(self.mt5.account_info.call_count, 2)
        self.assertEqual(self.mt5.order_send.call_count, 2)
        llamadas = self.mt5.mock_calls
        for anterior, actual in zip(llamadas, llamadas[1:]):
            if actual[0] == "order_send":
                self.assertEqual(anterior, call.account_info())
        cierre = self.mt5.order_send.call_args
        self.assertEqual(cierre.args[0]["position"], 42)

    def test_bloquea_apertura_y_cierre_si_no_hay_demo_explicita(self):
        posicion = self.broker.positions("XAUUSD", 123)[0]
        casos = [
            ("real", SimpleNamespace(trade_mode=self.mt5.ACCOUNT_TRADE_MODE_REAL), "trade_mode=2"),
            ("concurso", SimpleNamespace(trade_mode=self.mt5.ACCOUNT_TRADE_MODE_CONTEST), "trade_mode=1"),
            ("sin cuenta", None, "no devolvió una cuenta"),
            ("sin campo", SimpleNamespace(), "no informó trade_mode"),
            ("desconocido", SimpleNamespace(trade_mode=99), "trade_mode=99"),
            ("booleano", SimpleNamespace(trade_mode=False), "trade_mode=False"),
        ]
        for nombre, info, motivo in casos:
            self.mt5.account_info.return_value = info
            for operacion in (self.abrir, lambda: self.broker.close(posicion)):
                with self.subTest(caso=nombre, operacion=operacion.__name__):
                    with self.assertRaisesRegex(PermissionError, motivo):
                        operacion()
                    self.mt5.order_send.assert_not_called()

    def test_bloquea_si_falta_la_constante_demo(self):
        del self.mt5.ACCOUNT_TRADE_MODE_DEMO
        with self.assertRaisesRegex(PermissionError, "falta un ACCOUNT_TRADE_MODE_DEMO"):
            self.abrir()
        self.mt5.order_send.assert_not_called()

    def test_bloquea_si_falla_la_consulta_de_cuenta(self):
        self.mt5.account_info.side_effect = RuntimeError("terminal desconectado")
        with self.assertRaisesRegex(PermissionError, r"account_info\(\) falló"):
            self.abrir()
        self.mt5.order_send.assert_not_called()

    def test_revalida_la_cuenta_al_cerrar_despues_de_abrir_en_demo(self):
        posicion = self.abrir()
        self.mt5.order_send.reset_mock()
        self.mt5.account_info.return_value = SimpleNamespace(trade_mode=self.mt5.ACCOUNT_TRADE_MODE_REAL)

        with self.assertRaisesRegex(PermissionError, "trade_mode=2"):
            self.broker.close(posicion)
        self.mt5.order_send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
