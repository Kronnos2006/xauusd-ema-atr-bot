import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "tools" / "orion_arbitro.py"
spec = importlib.util.spec_from_file_location("orion_arbitro", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def comment(num, event, actor="owner", operator="Claude", bot=True):
    import json
    return {
        "id": num,
        "user": {"login": "github-actions[bot]" if bot else "outsider"},
        "body": mod.MARKER + json.dumps({"event": event, "actor": actor,
                                        "operator": operator}) + mod.END,
    }


class ArbitroTests(unittest.TestCase):
    def test_empty_and_reserve(self):
        data, event = mod.decision("reservar", "Claude", "owner", [])
        self.assertEqual(data["status"], "reservado")
        self.assertEqual(event["actor"], "owner")

    def test_reject_second_reservation(self):
        with self.assertRaisesRegex(ValueError, "reservada"):
            mod.decision("reservar", "ChatGPT", "other", [comment(2, "reserved")])

    def test_release_only_actor(self):
        with self.assertRaisesRegex(ValueError, "Solo"):
            mod.decision("liberar", "Claude", "other", [comment(1, "reserved")])
        data, event = mod.decision("liberar", "Claude", "owner", [comment(1, "reserved")])
        self.assertEqual(data["status"], "libre")
        self.assertEqual(event["event"], "released")

    def test_release_allows_new_claim(self):
        comments = [comment(1, "reserved"), comment(2, "released")]
        self.assertIsNone(mod.current_claim(comments))
        data, _ = mod.decision("reservar", "ChatGPT", "other", comments)
        self.assertEqual(data["status"], "reservado")

    def test_ignore_fake_operator_comment(self):
        data, _ = mod.decision("reservar", "Claude", "owner",
                               [comment(1, "reserved", bot=False)])
        self.assertEqual(data["status"], "reservado")

    def test_unrecognized_action_and_actor(self):
        for action in ("shell", "merge", "deploy"):
            with self.assertRaises(ValueError):
                mod.validate(12, action, "Claude", "owner")
        with self.assertRaises(ValueError):
            mod.validate(0, "reservar", "Claude", "owner")
        with self.assertRaises(ValueError):
            mod.validate(1, "reservar", "Claude", "")

    def test_multiple_events_and_claim_owner(self):
        comments = [comment(1, "reserved", "owner"), comment(2, "released", "other")]
        self.assertEqual(mod.current_claim(comments)["actor"], "owner")


if __name__ == "__main__":
    unittest.main()
