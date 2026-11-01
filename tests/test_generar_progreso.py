import unittest
from tools.generar_progreso import parse_progress, render


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.body = "\\n".join(
            f"### Fase {i} — prueba\\n" + "\\n".join(
                "- [x] hecho" if j == 0 else "- [ ] pendiente" for j in range(4)
            ) for i in range(1, 9)
        )

    def test_counts_and_percent(self):
        phases = parse_progress(self.body)
        self.assertEqual(sum(x[1] for x in phases), 8)
        self.assertIn("25.0%", render(phases, "https://github.com/example"))

    def test_fails_when_phase_missing(self):
        with self.assertRaises(ValueError):
            parse_progress(self.body.replace("### Fase 8", "### Otro 8"))

    def test_fails_when_checkbox_missing(self):
        with self.assertRaises(ValueError):
            parse_progress(self.body.replace("- [ ] pendiente", "no checkbox", 1))

    def test_empty_progress(self):
        phases = parse_progress(self.body.replace("[x]", "[ ]"))
        self.assertIn("0.0%", render(phases, "https://github.com/example"))


if __name__ == "__main__":
    unittest.main()
