"""Pruebas sin acceso a Google: portal deniega datos anónimos."""
import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

SOURCE = Path(__file__).resolve().parents[1] / "gateway" / "orion_google.py"
FAKE_ENV = {
    "GOOGLE_CLIENT_ID": "client.apps.googleusercontent.com",
    "GOOGLE_CLIENT_SECRET": "synthetic-not-real",
    "ORION_SESSION_SECRET": "x" * 64,
    "ORION_ALLOWED_GOOGLE_EMAILS": "owner@example.invalid",
    "ORION_BASE_URL": "https://orion.example.invalid",
}


def module():
    spec = importlib.util.spec_from_file_location("orion_google_test", SOURCE)
    obj = importlib.util.module_from_spec(spec)
    with patch.dict(os.environ, FAKE_ENV):
        spec.loader.exec_module(obj)
    return obj


class GatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gateway = module()

    def test_reject_unverified_google_email(self):
        verify = self.gateway.allowed_google_profile
        allowed = {"owner@example.invalid"}
        self.assertFalse(verify({"sub": "abc", "email": "owner@example.invalid",
                                 "email_verified": False}, allowed))
        self.assertTrue(verify({"sub": "abc", "email": "OWNER@example.invalid",
                                "email_verified": True}, allowed))
        self.assertFalse(verify({"sub": "abc", "email": "other@example.invalid",
                                 "email_verified": True}, allowed))
        self.assertFalse(verify({"email": "owner@example.invalid",
                                 "email_verified": True}, allowed))

    def test_anonymous_cannot_read_data(self):
        with TestClient(self.gateway.app, follow_redirects=False) as c:
            self.assertEqual(c.get("/data.json").status_code, 401)
            self.assertEqual(c.get("/orion/data.json").status_code, 401)
            self.assertEqual(c.get("/api/session").status_code, 401)
            self.assertEqual(c.get("/").status_code, 303)
            self.assertEqual(c.get("/visor/").status_code, 303)
            self.assertEqual(c.get("/cuentas").status_code, 303)

    def test_require_strong_secret_and_https(self):
        with patch.dict(os.environ, {**FAKE_ENV, "ORION_SESSION_SECRET": "short"}):
            with self.assertRaises(RuntimeError):
                self.gateway.env_config()
        with patch.dict(os.environ, {**FAKE_ENV,
                                     "ORION_BASE_URL": "http://insecure.example.invalid"}):
            with self.assertRaises(RuntimeError):
                self.gateway.env_config()


if __name__ == "__main__":
    unittest.main()
