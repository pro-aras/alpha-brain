# edit: Claude (Fable 5.1), 2026-09-23 04:13 +0400 — the pre-flight's crash: a numpy int in a counter or a merge-log tuple must neither
# abort state_hash nor change the digest a Python int gives.
import unittest
import numpy as np
from genome.machinery import _json_num
import json


class NumpyNumbersInTheHash(unittest.TestCase):
    def test_numpy_ints_render_as_python_ints(self):
        c = {"a": np.int64(3), "b": 4}
        self.assertEqual(json.dumps(c, sort_keys=True, default=_json_num), json.dumps({"a": 3, "b": 4}, sort_keys=True))
        log = [(1, "sight", np.int64(7), np.int32(9))]
        self.assertEqual(json.dumps(log, default=_json_num), json.dumps([(1, "sight", 7, 9)]))
        self.assertEqual(json.dumps([np.float64(0.5)], default=_json_num), json.dumps([0.5]))

    def test_anything_else_still_refuses(self):
        with self.assertRaises(TypeError):
            json.dumps({"x": object()}, default=_json_num)


class PlantedNumpyIdsInTheMergeLog(unittest.TestCase):
    def test_state_hash_survives_and_equals_the_python_int_hash(self):
        from pathlib import Path
        from genome.machinery import parse_genome, Organism
        g = parse_genome((Path(__file__).resolve().parents[2] / "genome" / "G4.genome").read_text())
        org = Organism(g)
        org.merges.append((0, "sight", 1, 2))
        h_py = org.state_hash()
        org.merges[-1] = (0, "sight", np.int64(1), np.int64(2))     # the pre-flight's shape (alpha4-pre-1, seq 2604)
        org.c["edges_pruned"] = np.int64(org.c["edges_pruned"])
        self.assertEqual(org.state_hash(), h_py)                      # no crash, the SAME digest


if __name__ == "__main__":
    unittest.main()
