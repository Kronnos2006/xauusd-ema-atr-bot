"""Smoke test local del piloto: inputs sintéticos, sin descarga ni IA."""
import importlib.util
import unittest
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "pilot/orion_upstream_check.py"
spec = importlib.util.spec_from_file_location("pilot_upstream", FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

MANIFEST = {
    "OpenHands/OpenHands": {
        "commit": "1" * 40, "license": "MIT",
    },
    "TauricResearch/TradingAgents": {
        "commit": "2" * 40, "license": "Apache-2.0",
    },
}
TEXTS = {
    "OpenHands/OpenHands": "Agent Canvas supports Claude Code and Codex." * 6,
    "TauricResearch/TradingAgents": "TradingAgents offers a risk analyst." * 6,
}


class SafePilot(unittest.TestCase):
    def test_safe_synthetic_inspection(self):
        result = mod.evaluate(MANIFEST, lambda name, sha: TEXTS[name])
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(len(result["upstreams"]), 2)
        for item in result["upstreams"]:
            self.assertFalse(item["external_code_executed"])
            self.assertFalse(item["orders_sent"])
            self.assertFalse(item["experiments_modified"])
            self.assertRegex(item["readme_sha256"], r"^[a-f0-9]{64}$")

    def test_failure_on_missing_claim(self):
        result = mod.evaluate(MANIFEST, lambda name, sha: ("A" * 160))
        self.assertEqual(result["status"], "NEEDS_REVIEW")

    def test_reject_unknown_repos(self):
        with self.assertRaises(ValueError):
            mod.evaluate({"unknown/repo": {"commit": "1"*40, "license": "MIT"}},
                         lambda name, sha: "A" * 150)

    def test_reject_bad_commit_and_license(self):
        bad = {k: dict(v) for k, v in MANIFEST.items()}
        bad["OpenHands/OpenHands"]["commit"] = "main"
        with self.assertRaises(ValueError):
            mod.evaluate(bad, lambda name, sha: TEXTS[name])
        bad = {k: dict(v) for k, v in MANIFEST.items()}
        bad["OpenHands/OpenHands"]["license"] = "UNKNOWN"
        with self.assertRaises(ValueError):
            mod.evaluate(bad, lambda name, sha: TEXTS[name])


if __name__ == "__main__":
    unittest.main()
