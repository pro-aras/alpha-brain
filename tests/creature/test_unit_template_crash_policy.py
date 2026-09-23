# edit: Claude (Fable 5.1), 2026-09-23 04:14 +0400 — the ONE-life unit template must never restart a mind that exited 3 (PREREG §2.6: a
# crash pages, never loops — alpha4-pre-1 looped 10 times in 2 min before this line existed).
import unittest
from pathlib import Path


class UnitTemplateCrashPolicy(unittest.TestCase):
    def test_exit_3_is_never_restarted(self):
        p = Path(__file__).resolve().parents[2] / "deploy" / "creature-g5@.service"
        text = p.read_text()
        self.assertIn("Restart=on-failure", text)
        self.assertIn("RestartPreventExitStatus=3", text)


if __name__ == "__main__":
    unittest.main()
