# edit: Claude (Fable 5.1), 2026-09-23 04:11 +0400 — the hands' road from a LIFE checkout (the pre-flight's dead organ): the jail path
# resolves to /data/dev/alpha3/hands/jail_run whether the tree sits at /data/dev/genome or under genome-lives/<life>/code.
import os, tempfile, unittest
from pathlib import Path
from unittest import mock


class HandsRoadFromALifeCheckout(unittest.TestCase):
    JAIL = Path("/data/dev/alpha3/hands/jail_run")

    def test_resolves_from_the_dev_tree_and_from_a_nested_life_checkout(self):
        if not self.JAIL.exists():
            self.skipTest("the jail is not on this box")
        from creature import mind as mind_module
        self.assertEqual(mind_module.resolve_sibling("alpha3/hands/jail_run"), self.JAIL)
        nested = Path(tempfile.mkdtemp()) / "genome-lives" / "x" / "code"; nested.mkdir(parents=True)
        with mock.patch.object(mind_module, "_mind_repo_root", return_value=nested):
            self.assertEqual(mind_module.resolve_sibling("alpha3/hands/jail_run"), self.JAIL)
            jail, shelf = mind_module._hands_paths({"HANDS": {"jail": "alpha3/hands/jail_run", "shelf": "world/programs"}})
            self.assertEqual(jail, self.JAIL); self.assertEqual(shelf, nested / "world" / "programs")

    def test_the_body_uses_the_same_resolver(self):
        if not self.JAIL.exists():
            self.skipTest("the jail is not on this box")
        from creature import body as body_module
        self.assertEqual(body_module._resolve_sibling_for_body("alpha3/hands/jail_run"), self.JAIL)


if __name__ == "__main__":
    unittest.main()
