# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 17:0x +0400 — tests for brain/world/families.py against
# B1-PREREG.md §5.2's own construction-exact counts table.
from __future__ import annotations

import unittest

from brain.world import families

SEED = 20261001


class TestBaseRelationCounts(unittest.TestCase):
    def test_after_pairs_25(self) -> None:
        self.assertEqual(len(families.AFTER_PAIRS), 25)
        self.assertEqual(families.AFTER_PAIRS[0], ("a", "b"))
        self.assertEqual(families.AFTER_PAIRS[-1], ("y", "z"))

    def test_between_triples_24(self) -> None:
        self.assertEqual(len(families.BETWEEN_TRIPLES), 24)
        self.assertEqual(families.BETWEEN_TRIPLES[0], ("a", "b", "c"))

    def test_two_after_pairs_24(self) -> None:
        self.assertEqual(len(families.TWO_AFTER_PAIRS), 24)
        self.assertEqual(families.TWO_AFTER_PAIRS[0], ("a", "c"))

    def test_digit_after_pairs_9(self) -> None:
        self.assertEqual(len(families.DIGIT_AFTER_PAIRS), 9)
        self.assertEqual(families.DIGIT_AFTER_PAIRS[0], ("zero", "one"))
        self.assertEqual(families.DIGIT_AFTER_PAIRS[-1], ("eight", "nine"))


class TestAfterBefore(unittest.TestCase):
    def test_12_held_13_taught(self) -> None:
        r = families.after_before(SEED)
        self.assertEqual(len(r["held_out"]), 12)
        self.assertEqual(len(r["taught"]), 13)
        self.assertEqual(set(r["held_out"]) | set(r["taught"]), set(families.AFTER_PAIRS))

    def test_before_is_after_reversed(self) -> None:
        r = families.after_before(SEED)
        self.assertEqual(r["before_held_out"], [(b, a) for a, b in r["held_out"]])
        self.assertEqual(r["before_taught"], [(b, a) for a, b in r["taught"]])

    def test_deterministic(self) -> None:
        r1 = families.after_before(SEED)
        r2 = families.after_before(SEED)
        self.assertEqual(r1, r2)

    def test_different_seeds_can_differ(self) -> None:
        r1 = families.after_before(20261001)
        r2 = families.after_before(20261002)
        # not a hard requirement that they differ, but they should be independently valid splits
        self.assertEqual(len(r1["held_out"]), len(r2["held_out"]))


class TestBetween(unittest.TestCase):
    def test_12_and_12(self) -> None:
        r = families.between(SEED)
        self.assertEqual(len(r["held_out"]), 12)
        self.assertEqual(len(r["taught"]), 12)


class TestTwoAfter(unittest.TestCase):
    def test_3_taught_21_held(self) -> None:
        r = families.two_after(SEED)
        self.assertEqual(len(r["taught"]), 3)
        self.assertEqual(len(r["held_out"]), 21)


class TestOtherCase(unittest.TestCase):
    def test_13_and_13(self) -> None:
        r = families.other_case(SEED)
        self.assertEqual(len(r["taught"]), 13)
        self.assertEqual(len(r["held_out"]), 13)
        self.assertEqual(set(r["held_out"]) | set(r["taught"]), set(families.LETTER_NAMES))


class TestChain(unittest.TestCase):
    def test_25_items_with_breakdown(self) -> None:
        ab = families.after_before(SEED)
        r = families.chain(after_before_result=ab)
        self.assertEqual(len(r["items"]), 25)
        self.assertEqual(len(r["breakdown"]), 25)
        held_pairs = set(ab["held_out"])
        for row in r["breakdown"]:
            expect = "held_out" if row["pair"] in held_pairs else "taught"
            self.assertEqual(row["after_was"], expect)

    def test_derives_its_own_split_from_seed(self) -> None:
        r = families.chain(seed=SEED)
        self.assertEqual(len(r["items"]), 25)

    def test_raises_without_seed_or_result(self) -> None:
        with self.assertRaises(families.FamiliesError):
            families.chain()


class TestTransfer(unittest.TestCase):
    def test_9_and_9_18_total(self) -> None:
        r = families.transfer()
        self.assertEqual(len(r["after"]), 9)
        self.assertEqual(len(r["before"]), 9)
        self.assertEqual(len(r["items"]), 18)


class TestPerceptual(unittest.TestCase):
    def test_mirror_17_positive_16_held(self) -> None:
        self.assertEqual(len(families.MIRROR_POSITIVE_FORMS), 17)
        r = families.mirror_symmetric(SEED)
        self.assertEqual(len(r["held_out"]["positive"]), 8)
        self.assertEqual(len(r["held_out"]["negative"]), 8)

    def test_loop_15_positive_14_held(self) -> None:
        self.assertEqual(len(families.LOOP_POSITIVE_FORMS), 15)
        r = families.has_loop(SEED)
        self.assertEqual(len(r["held_out"]["positive"]), 7)
        self.assertEqual(len(r["held_out"]["negative"]), 7)

    def test_vowel_10_forms_10_consonants(self) -> None:
        self.assertEqual(len(families.VOWEL_FORMS), 10)
        r = families.vowel(SEED)
        self.assertEqual(len(r["consonant_forms"]), 10)
        self.assertFalse(set(r["consonant_forms"]) & set(families.VOWEL_FORMS))

    def test_perceptual_splits_deterministic(self) -> None:
        self.assertEqual(families.mirror_symmetric(SEED), families.mirror_symmetric(SEED))
        self.assertEqual(families.has_loop(SEED), families.has_loop(SEED))
        self.assertEqual(families.vowel(SEED), families.vowel(SEED))


class TestMisuseItems(unittest.TestCase):
    def test_39_items_gradable_without_a_pool(self) -> None:
        ab = families.after_before(SEED)
        ta = families.two_after(SEED)
        bt = families.between(SEED)
        r = families.misuse_items(ab, ta, bt, never_taught_pool=None)
        self.assertIsNone(r["after_never_taught"])
        self.assertEqual(r["total_gradable"], 1 + 1 + 2 + 25 + 10)   # 39 of the full 49

    def test_49_items_gradable_with_a_pool(self) -> None:
        ab = families.after_before(SEED)
        ta = families.two_after(SEED)
        bt = families.between(SEED)
        pool = [f"sign-{i}" for i in range(20)]
        r = families.misuse_items(ab, ta, bt, never_taught_pool=pool)
        self.assertEqual(len(r["after_never_taught"]), 10)
        self.assertEqual(r["total_gradable"], 49)

    def test_raises_on_too_small_a_pool(self) -> None:
        ab = families.after_before(SEED)
        ta = families.two_after(SEED)
        bt = families.between(SEED)
        with self.assertRaises(families.FamiliesError):
            families.misuse_items(ab, ta, bt, never_taught_pool=["only", "three", "signs"])


if __name__ == "__main__":
    unittest.main()
