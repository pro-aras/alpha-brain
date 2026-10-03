# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 18:18 +0400 — PREREG-RESIT-READER v4 §1.6 / R15 / R16: the origin's SOURCE COPY of a live life's tape (complete lines only, cut after the last sitting's end, the payloads the grader
# reads, truth whole, journal, genomes, a manifest with its sha256) and ITEMS-MATCH on that copy (ask digest, canvas digest, world scene line, the canvases' own bytes, refused BY NAME before any child).
# Written BEFORE the code. Every plant is a COPY, asserts it changed the bytes (#247 (5)) and is CAUGHT.
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 20:24 +0400 — TestDaxIndex: `dax_index_of` (the pinned grader's DAX_SCENE, the one input the origin's source copy needs from the grader checkout) had NO test; the origin tests'
# stub grader held no brain/scene/world.py, so 24 of 26 origin tests crashed there (FileNotFoundError → an ERROR row, not a named refusal). Written BEFORE the fix.
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 20:46 +0400 — the survivors of the first mutation sweep of origin mode (named in the sweep log): no test said a payload is COPIED and never symlinked into the life (R16), that the GENOME.v<n> files
# the epoch rows name are copied, that a MANIFEST rewritten to match an altered file is caught by the row's sha256, or that a sitting canvas swapped for another valid picture (its row sha updated) is seen by the canvas digest (plant f).
"""tests/tools/test_resit_origin_copy.py — build_source_copy, verify_source_copy, items_match."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.tools.test_resit import Tmp, sha, write_journal, write_tape
from tests.tools.test_resit_children import GENOME, png, sitting_spec
from tools.brain import resit as R

GENOME_ORIGIN = GENOME + "WORLD scene seed 20261101; train 3; sitting fresh s1b1; feed max backlog 8; utterance true\n"


def make_life(base: Path, name: str = "life", *, genome: str = GENOME_ORIGIN, extra_rows_after=(), truth: bool = True, seq0: int = 1000) -> Path:
    root = base / name
    root.mkdir()
    (root / "GENOME.genome").write_text(genome)
    spec = list(sitting_spec()) + list(extra_rows_after)
    write_tape(root, spec, seq0=seq0)
    write_journal(root, [{"kind": "brain", "act": "learn", "seq": seq0 + 2, "moment": "m", "at": "t"}, {"kind": "answer", "item": "M1:fresh:0", "seq": seq0 + 4}])
    if truth:
        (root / "truth" / "scene").mkdir(parents=True)
        for i in (1, 2, 3):
            (root / "truth" / "scene" / f"{i:09d}.json").write_text(json.dumps({"row": i}))
    return root


def tree_state(root: Path) -> dict:
    return {str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns) for p in sorted(root.rglob("*")) if p.is_file()}


def pin_of(root: Path) -> dict:
    text = (root / "GENOME.genome").read_text()
    scan = R.scan_items(root, R.tape_decl_of(text), verify_canvas_bytes=True)
    return {"root": str(root), "n_asks": scan["n_asks"], "n_canvases": scan["n_canvases"], "ask_digest": scan["ask_digest"], "canvas_digest": scan["canvas_digest"],
            "world_scene_line_sha": R.world_scene_line_sha(text), "scored": {"path": None, "sha256": None}}


class TestSourceCopy(Tmp):
    def test_the_copy_holds_the_tape_cut_after_the_last_end_the_payloads_the_grader_reads_truth_journal_and_genomes(self) -> None:
        base = self.mk("resit-src-")
        extra = [("ear", "m-late", "zzz"), ("eye", "m-late", None, png(1, 1, 1))]                  # rows AFTER the last sitting's end: nothing reads them
        root = make_life(base, extra_rows_after=extra)
        dest = base / "copy"
        res = R.build_source_copy(root, dest, dax_index=2699)
        tape_rows = [json.loads(l) for f in sorted((dest / "tape").glob("*.jsonl")) for l in f.read_text().splitlines()]
        self.assertEqual(res["cut_seq"], max(r["seq"] for r in tape_rows))
        last = tape_rows[-1]
        self.assertEqual((last["sense"], last["meta"]["form"]), ("ask", "end"), "cut right after the last sitting's end ask")
        self.assertEqual(len(tape_rows), 14, "an ear and an eye row, then two sittings of begin, two points, a canvas, a why and an end — and nothing after the last end")
        self.assertNotIn("m-late", {r["meta"]["moment"] for r in tape_rows})
        for r in tape_rows:
            if r["sense"] == "ask" or (r["sense"] == "eye" and (r.get("meta") or {}).get("kind") == "sitting"):
                self.assertTrue((dest / "tape" / r["payload"]).is_file(), r["payload"])
        self.assertEqual(sorted(p.name for p in (dest / "truth" / "scene").iterdir()), ["000000001.json", "000000002.json", "000000003.json"])
        self.assertTrue((dest / "journal" / "2026-10-03.jsonl").is_file())
        self.assertTrue((dest / "GENOME.genome").is_file())
        self.assertFalse((dest / "tape" / "payload").is_symlink(), "a COPY, never a symlink into the life")
        self.assertEqual(res["rows"], 14)

    def test_the_non_sitting_eye_payloads_are_not_copied_only_the_asks_the_sitting_canvases_and_the_dax_canvas(self) -> None:
        base = self.mk("resit-src-")
        root = make_life(base)
        dest = base / "copy"
        R.build_source_copy(root, dest, dax_index=2699)
        copied = {p.name for p in (dest / "tape" / "payload").iterdir()}
        src_pngs = {p.name for p in (root / "tape" / "payload").glob("*.png")}
        self.assertEqual(len(src_pngs), 3, "the stub tape holds one maker canvas and two sitting canvases")
        self.assertEqual(len([n for n in copied if n.endswith(".png")]), 2, "the maker canvas (not a sitting) is left behind")

    def test_the_dax_training_canvas_is_copied_by_its_scene_index(self) -> None:
        base = self.mk("resit-src-")
        root = base / "life"
        root.mkdir()
        (root / "GENOME.genome").write_text(GENOME_ORIGIN)
        spec = [("eye", "t-dax", "train", png(5, 5, 5)), ("eye", "t-other", "train", png(6, 6, 6))] + list(sitting_spec())
        write_tape(root, spec, seq0=1000)
        # write_tape gives a train row meta {kind, set, split, row}; add the scene index the way the real tape's train rows carry it
        for f in (root / "tape").glob("*.jsonl"):
            rows = [json.loads(l) for l in f.read_text().splitlines()]
            for r in rows:
                if r["sense"] == "eye" and r["meta"].get("kind") == "train":
                    r["meta"]["scene"] = 2699 if r["meta"]["moment"] == "t-dax" else 7
            f.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        write_journal(root, [{"kind": "brain", "act": "learn", "seq": 1, "moment": "m", "at": "t"}])
        dest = base / "copy"
        R.build_source_copy(root, dest, dax_index=2699)
        rows = [json.loads(l) for f in sorted((dest / "tape").glob("*.jsonl")) for l in f.read_text().splitlines()]
        dax = next(r for r in rows if r["sense"] == "eye" and r["meta"]["moment"] == "t-dax")
        other = next(r for r in rows if r["sense"] == "eye" and r["meta"]["moment"] == "t-other")
        self.assertTrue((dest / "tape" / dax["payload"]).is_file())
        self.assertFalse((dest / "tape" / other["payload"]).exists(), "any other training canvas's picture is not needed (M4a reads only truth)")

    def test_a_torn_last_line_of_the_journal_is_dropped_and_counted_never_copied(self) -> None:
        base = self.mk("resit-src-")
        root = make_life(base)
        with (root / "journal" / "2026-10-03.jsonl").open("a") as f:
            f.write('{"kind": "brain", "act": "learn", "seq": 5000, "mom')
        dest = base / "copy"
        res = R.build_source_copy(root, dest, dax_index=2699)
        self.assertEqual(res["torn_lines_journal"], 1)
        for f in (dest / "journal").glob("*.jsonl"):
            for line in f.read_text().splitlines():
                json.loads(line)

    def test_a_torn_tape_tail_beyond_later_rows_is_never_reached_and_one_right_after_the_cut_is_counted_not_copied(self) -> None:
        base = self.mk("resit-src-")
        root = make_life(base, "a", extra_rows_after=[("ear", "m-late", "zzz"), ("eye", "m-late", None, png(1, 1, 1))])
        with (root / "tape" / "2026-10-03.jsonl").open("a") as f:
            f.write('{"seq": 99999, "at": "t", "sense": "eye", "sha": "abc')
        res = R.build_source_copy(root, base / "copy-a", dax_index=2699)
        self.assertEqual(res["torn_lines_tape"], 0, "later complete rows stop the copy first: the torn line is beyond the cut and never reached")
        root2 = make_life(base, "b")
        with (root2 / "tape" / "2026-10-03.jsonl").open("a") as f:
            f.write('{"seq": 99999, "at": "t", "sense": "eye", "sha": "abc')
        res2 = R.build_source_copy(root2, base / "copy-b", dax_index=2699)
        self.assertEqual(res2["torn_lines_tape"], 1, "a torn line that directly follows the last kept row is seen, counted, and not copied")
        for f in (base / "copy-b" / "tape").glob("*.jsonl"):
            for line in f.read_text().splitlines():
                json.loads(line)

    def test_the_life_is_only_read_sizes_and_mtimes_are_unchanged_R16(self) -> None:
        base = self.mk("resit-src-")
        root = make_life(base)
        before = tree_state(root)
        R.build_source_copy(root, base / "copy", dax_index=2699)
        self.assertEqual(before, tree_state(root))

    def test_a_tape_whose_sittings_are_not_complete_is_skipped_by_name_R4c(self) -> None:
        base = self.mk("resit-src-")
        root = base / "life"
        root.mkdir()
        (root / "GENOME.genome").write_text(GENOME_ORIGIN)
        short = [it for it in sitting_spec()][:8]                                                  # the first set's end is there, the second set never ends
        write_tape(root, short, seq0=1000)
        write_journal(root, [{"kind": "brain", "act": "learn", "seq": 1, "moment": "m", "at": "t"}])
        with self.assertRaises(R.Skipped) as cm:
            R.build_source_copy(root, base / "copy", dax_index=2699)
        self.assertIn("sittings", str(cm.exception))
        self.assertFalse((base / "copy").exists() and any((base / "copy").iterdir()), "nothing is left behind")

    def test_the_manifest_hash_equals_an_independent_recomputation_and_names_every_file_R16(self) -> None:
        base = self.mk("resit-src-")
        root = make_life(base)
        dest = base / "copy"
        res = R.build_source_copy(root, dest, dax_index=2699)
        lines = []
        for p in sorted(dest.rglob("*"), key=lambda q: str(q.relative_to(dest))):
            if p.is_file() and p.name != "MANIFEST":
                lines.append(f"{p.relative_to(dest)} {p.stat().st_size} {hashlib.sha256(p.read_bytes()).hexdigest()}")
        manifest = "\n".join(lines) + "\n"
        self.assertEqual((dest / "MANIFEST").read_text(), manifest)
        self.assertEqual(res["source_copy_sha256"], hashlib.sha256(manifest.encode()).hexdigest())
        self.assertEqual(res["n_manifest_entries"], len(lines))
        self.assertGreater(res["bytes"], 0)

    def test_one_byte_flipped_in_the_copy_after_it_was_built_is_caught_by_the_reverification_R16(self) -> None:
        base = self.mk("resit-src-")
        root = make_life(base)
        dest = base / "copy"
        res = R.build_source_copy(root, dest, dax_index=2699)
        self.assertEqual(R.verify_source_copy(dest, res["source_copy_sha256"]), [])
        victim = sorted((dest / "tape" / "payload").glob("*.json"))[0]
        before = victim.read_bytes()
        victim.write_bytes(before[:-2] + bytes([before[-2] ^ 1]) + before[-1:])
        self.assertNotEqual(before, victim.read_bytes(), "the plant must change the bytes")
        bad = R.verify_source_copy(dest, res["source_copy_sha256"])
        self.assertTrue(any(str(victim.relative_to(dest)) in b for b in bad), bad)

    def test_an_added_or_removed_file_in_the_copy_is_caught_too(self) -> None:
        base = self.mk("resit-src-")
        root = make_life(base)
        dest = base / "copy"
        res = R.build_source_copy(root, dest, dax_index=2699)
        (dest / "journal" / "stray.jsonl").write_text("{}\n")
        self.assertTrue(R.verify_source_copy(dest, res["source_copy_sha256"]))
        (dest / "journal" / "stray.jsonl").unlink()
        self.assertEqual(R.verify_source_copy(dest, res["source_copy_sha256"]), [])
        next((dest / "truth" / "scene").glob("*.json")).unlink()
        self.assertTrue(R.verify_source_copy(dest, res["source_copy_sha256"]))

    def test_a_destination_that_is_not_empty_is_refused(self) -> None:
        base = self.mk("resit-src-")
        root = make_life(base)
        dest = base / "copy"
        dest.mkdir()
        (dest / "x").write_text("x")
        with self.assertRaises(R.Refused):
            R.build_source_copy(root, dest, dax_index=2699)

    def test_no_kept_file_is_a_symlink_a_copy_never_points_into_the_life_R16(self) -> None:
        base = self.mk("resit-src-")
        root = make_life(base)
        dest = base / "copy"
        res = R.build_source_copy(root, dest, dax_index=2699)
        self.assertEqual([str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_symlink()], [], "every kept file is a regular file with its own bytes")
        self.assertGreater(res["payloads_kept"], 0)
        # the plant: a payload replaced by a symlink to the life's own file — the manifest hashes through a link, so only the symlink check can see it
        victim = sorted((dest / "tape" / "payload").glob("*.json"))[0]
        target = root / "tape" / victim.relative_to(dest / "tape")
        self.assertEqual(victim.read_bytes(), target.read_bytes())
        victim.unlink()
        os.symlink(target, victim)
        self.assertTrue(victim.is_symlink(), "the plant must change the tree")
        bad = R.verify_source_copy(dest, res["source_copy_sha256"])
        self.assertTrue(any("symlink" in b and str(victim.relative_to(dest)) in b for b in bad), bad)

    def test_the_epoch_genomes_the_epoch_rows_name_are_copied_beside_the_launch_genome_and_listed_in_the_manifest(self) -> None:
        base = self.mk("resit-src-")
        root = make_life(base)
        (root / "GENOME.v1.genome").write_text(GENOME_ORIGIN + "# epoch 1\n")
        (root / "GENOME.v2.genome").write_text(GENOME_ORIGIN + "# epoch 2\n")
        dest = base / "copy"
        res = R.build_source_copy(root, dest, dax_index=2699)
        self.assertEqual(res["genomes"], ["GENOME.genome", "GENOME.v1.genome", "GENOME.v2.genome"])
        listed = [line.split(" ")[0] for line in (dest / "MANIFEST").read_text().splitlines()]
        for n in res["genomes"]:
            self.assertEqual((dest / n).read_bytes(), (root / n).read_bytes())
            self.assertIn(n, listed)

    def test_a_rewritten_manifest_matching_an_altered_file_is_caught_by_the_rows_sha256_R16(self) -> None:
        base = self.mk("resit-src-")
        root = make_life(base)
        dest = base / "copy"
        res = R.build_source_copy(root, dest, dax_index=2699)
        victim = sorted((dest / "tape" / "payload").glob("*.json"))[0]
        before = victim.read_bytes()
        victim.write_bytes(before[:-2] + bytes([before[-2] ^ 1]) + before[-1:])
        self.assertNotEqual(before, victim.read_bytes(), "the plant must change the bytes")
        (dest / "MANIFEST").write_text(R._manifest_text(dest)[0], encoding="utf-8")                 # the manifest now AGREES with every file: only the hash recorded in the row can disagree
        bad = R.verify_source_copy(dest, res["source_copy_sha256"])
        self.assertTrue(any("does not hash to the sha256 recorded in the row" in b for b in bad), bad)
        self.assertEqual([b for b in bad if "differ" in b or "missing" in b or "does not list" in b], [], "the per-file checks alone read it clean — that is the plant's point")


class TestItemsMatch(Tmp):
    """R15: the life's own sittings, ON THE COPY, equal the pinned items — FIRST, by name, before any child."""

    def copies(self):
        base = self.mk("resit-im-")
        items_life = make_life(base, "items")
        life = make_life(base, "life", seq0=5000)                                                   # another tape position: the digests carry content, never a seq
        dest = base / "copy"
        R.build_source_copy(life, dest, dax_index=2699)
        return base, items_life, life, dest

    def match(self, dest: Path, pin: dict) -> None:
        text = (dest / "GENOME.genome").read_text()
        scan = R.scan_items(dest, R.tape_decl_of(text), verify_canvas_bytes=True)
        R.items_match(scan, pin, R.world_scene_line_sha(text))

    def test_the_same_sittings_on_two_lives_match_the_digests_carry_content_never_a_seq(self) -> None:
        base, items_life, life, dest = self.copies()
        self.match(dest, pin_of(items_life))

    def test_plant_a_a_sitting_asks_payload_byte_changed_with_its_row_sha_updated_is_seen_by_the_digest_only(self) -> None:
        base, items_life, life, dest = self.copies()
        pin = pin_of(items_life)
        payload = sorted((dest / "tape" / "payload").glob("*.json"))[1]
        before = payload.read_bytes()
        payload.write_text(payload.read_text().replace('"test_seed": 7', '"test_seed": 8'))
        self.assertNotEqual(before, payload.read_bytes(), "the plant must change the bytes")
        for f in (dest / "tape").glob("*.jsonl"):                                                  # update the tape row's sha so the row/payload check passes
            rows = [json.loads(l) for l in f.read_text().splitlines()]
            for r in rows:
                if r.get("payload") == f"payload/{payload.name}":
                    r["sha"] = hashlib.sha256(payload.read_bytes()).hexdigest()
            f.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        with self.assertRaises(R.Refused) as cm:
            self.match(dest, pin)
        self.assertIn("ITEMS-MATCH", str(cm.exception))
        self.assertIn("ask_digest", str(cm.exception))

    def test_plant_b_one_ask_rows_moment_changed_is_seen_the_moment_is_inside_the_digest(self) -> None:
        base, items_life, life, dest = self.copies()
        pin = pin_of(items_life)
        changed = False
        for f in (dest / "tape").glob("*.jsonl"):
            rows = [json.loads(l) for l in f.read_text().splitlines()]
            for r in rows:
                if r["sense"] == "ask" and not changed:
                    r["meta"]["moment"] = r["meta"]["moment"] + "-x"
                    changed = True
            f.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        self.assertTrue(changed, "the plant must change a moment")
        with self.assertRaises(R.Refused) as cm:
            self.match(dest, pin)
        self.assertIn("ask_digest", str(cm.exception))

    def test_plant_c_one_sitting_canvases_png_byte_changed_with_its_row_sha_untouched_is_seen_by_the_bytes_check(self) -> None:
        base, items_life, life, dest = self.copies()
        pin = pin_of(items_life)
        png_file = sorted((dest / "tape" / "payload").glob("*.png"))[0]
        before = png_file.read_bytes()
        png_file.write_bytes(before[:-1] + bytes([before[-1] ^ 1]))
        self.assertNotEqual(before, png_file.read_bytes(), "the plant must change the bytes")
        with self.assertRaises(R.Refused) as cm:
            self.match(dest, pin)
        self.assertIn("sha", str(cm.exception))
        self.assertIn(png_file.name, str(cm.exception))

    def test_plant_d_the_world_scene_line_of_the_genome_copy_edited_is_seen(self) -> None:
        base, items_life, life, dest = self.copies()
        pin = pin_of(items_life)
        g = dest / "GENOME.genome"
        before = g.read_bytes()
        g.write_text(g.read_text().replace("seed 20261101", "seed 20261102"))
        self.assertNotEqual(before, g.read_bytes(), "the plant must change the bytes")
        with self.assertRaises(R.Refused) as cm:
            self.match(dest, pin)
        self.assertIn("world_scene_line_sha", str(cm.exception))

    def test_plant_e_one_ask_row_removed_is_seen_by_the_count_and_the_digest(self) -> None:
        base, items_life, life, dest = self.copies()
        pin = pin_of(items_life)
        f = next(iter(sorted((dest / "tape").glob("*.jsonl"))))
        rows = [json.loads(l) for l in f.read_text().splitlines()]
        victim = next(r for r in rows if r["sense"] == "ask" and r["meta"]["form"] == "point")
        rows.remove(victim)
        f.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        with self.assertRaises(R.Refused) as cm:
            self.match(dest, pin)
        self.assertIn("n_asks", str(cm.exception))

    def test_plant_f_one_sitting_canvas_replaced_by_another_valid_picture_with_its_row_sha_updated_is_seen_by_the_canvas_digest_only(self) -> None:
        base, items_life, life, dest = self.copies()
        pin = pin_of(items_life)
        png_file = sorted((dest / "tape" / "payload").glob("*.png"))[0]
        before = png_file.read_bytes()
        png_file.write_bytes(png(201, 101, 51))                                                    # another valid picture, hashing to its OWN sha
        self.assertNotEqual(before, png_file.read_bytes(), "the plant must change the bytes")
        new_sha = hashlib.sha256(png_file.read_bytes()).hexdigest()
        changed = 0
        for f in (dest / "tape").glob("*.jsonl"):                                                  # the tape row's sha follows: the row/payload check passes, the ask digest is untouched
            rows = [json.loads(l) for l in f.read_text().splitlines()]
            for r in rows:
                if r.get("payload") == f"payload/{png_file.name}":
                    r["sha"] = new_sha
                    changed += 1
            f.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        self.assertEqual(changed, 1)
        text = (dest / "GENOME.genome").read_text()
        scan = R.scan_items(dest, R.tape_decl_of(text), verify_canvas_bytes=True)                  # the bytes check alone reads it clean
        self.assertEqual(scan["ask_digest"], pin["ask_digest"])
        with self.assertRaises(R.Refused) as cm:
            self.match(dest, pin)
        self.assertIn("canvas_digest", str(cm.exception))

    def test_the_canvas_bytes_check_is_off_by_default_so_the_gate_and_daily_scans_are_unchanged(self) -> None:
        base, items_life, life, dest = self.copies()
        png_file = sorted((dest / "tape" / "payload").glob("*.png"))[0]
        png_file.write_bytes(png_file.read_bytes() + b"x")
        text = (dest / "GENOME.genome").read_text()
        R.scan_items(dest, R.tape_decl_of(text))                                                    # no verify_canvas_bytes: nothing raised
        with self.assertRaises(R.Refused):
            R.scan_items(dest, R.tape_decl_of(text), verify_canvas_bytes=True)


class TestDaxIndex(Tmp):
    """`dax_index_of`: the scene index of the one «dax» meeting, read from the PINNED grader checkout's brain/scene/world.py (the grader's own look at the dax training canvas, `meeting_seen`). The source copy keeps the
    payload of the training eye row of that scene, so a wrong index would silently drop the one canvas the grader reads from the training stream."""

    def grader(self, world_text, name="grader") -> Path:
        d = self.mk("resit-dax-") / name
        (d / "brain" / "scene").mkdir(parents=True)
        if world_text is not None:
            (d / "brain" / "scene" / "world.py").write_text(world_text)
        return d

    def test_the_index_is_the_pinned_graders_DAX_SCENE_minus_one_it_is_one_based_in_the_file(self) -> None:
        g = self.grader("DAX_SCENE = 2700                                  # «the 2,700th scene» (1-based) → index 2699\nDAX_INDEX = DAX_SCENE - 1\n")
        self.assertEqual(R.dax_index_of(g), 2699)

    def test_plant_a_different_constant_gives_a_different_index_the_read_is_not_a_default(self) -> None:
        g = self.grader("DAX_SCENE = 2701\n")
        self.assertEqual(R.dax_index_of(g), 2700)
        self.assertNotEqual(R.dax_index_of(g), 2699, "the plant must change the answer: a reader that returned a constant would pass the first test")

    def test_a_commented_line_or_the_derived_DAX_INDEX_line_is_not_the_constant(self) -> None:
        g = self.grader("# DAX_SCENE = 5\nDAX_INDEX = DAX_SCENE - 1\nDAX_SCENE = 2700\n")
        self.assertEqual(R.dax_index_of(g), 2699)

    def test_a_grader_checkout_without_world_py_is_refused_by_name_never_a_raw_file_error(self) -> None:
        g = self.grader(None)
        self.assertFalse((g / "brain" / "scene" / "world.py").exists(), "the plant must leave the file absent")
        with self.assertRaises(R.Refused) as cm:
            R.dax_index_of(g)
        self.assertIn("world.py", str(cm.exception))
        self.assertIn(str(g), str(cm.exception))

    def test_a_world_py_without_the_constant_is_refused_by_name(self) -> None:
        g = self.grader("DAX_INDEX = 2699\n")
        with self.assertRaises(R.Refused) as cm:
            R.dax_index_of(g)
        self.assertIn("DAX_SCENE", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
