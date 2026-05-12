"""
Unit tests for WordleSolver.

Wordle scoring: 1=gray (not in word), 2=yellow (in word, wrong position), 3=green (correct position).
"""
import unittest
from WordleSolverDefs import check_word, eliminateCandidates, valid_result, valid_word


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fresh_state():
    """Return a clean (letters_in, letters_out, letters_correct, letters_incorrect) tuple."""
    return list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), [], {}, {}


# ---------------------------------------------------------------------------
# check_word — basic (no duplicates)
# ---------------------------------------------------------------------------

class TestCheckWordBasic(unittest.TestCase):

    def test_all_gray_adds_to_letters_out(self):
        """Every gray letter must appear in lettersOut."""
        li, lo, lc, li2 = fresh_state()
        check_word('ZZZZZ', '11111', li, lo, lc, li2)
        self.assertIn('Z', lo)
        self.assertEqual(lc, {})
        self.assertEqual(li2, {})

    def test_all_green_populates_letters_correct(self):
        """Every green letter/position must be stored in lettersCorrect."""
        li, lo, lc, li2 = fresh_state()
        check_word('ABCDE', '33333', li, lo, lc, li2)
        self.assertEqual(lc.get('A'), [0])
        self.assertEqual(lc.get('B'), [1])
        self.assertEqual(lc.get('C'), [2])
        self.assertEqual(lc.get('D'), [3])
        self.assertEqual(lc.get('E'), [4])
        self.assertEqual(lo, [])
        self.assertEqual(li2, {})

    def test_all_yellow_populates_letters_incorrect(self):
        """Every yellow letter/position must be stored in lettersIncorrect."""
        li, lo, lc, li2 = fresh_state()
        check_word('ABCDE', '22222', li, lo, lc, li2)
        self.assertEqual(li2.get('A'), [0])
        self.assertEqual(li2.get('B'), [1])
        self.assertEqual(li2.get('C'), [2])
        self.assertEqual(li2.get('D'), [3])
        self.assertEqual(li2.get('E'), [4])
        self.assertEqual(lo, [])
        self.assertEqual(lc, {})

    def test_mixed_result(self):
        """Mixed result: correct splits across all three buckets."""
        li, lo, lc, li2 = fresh_state()
        # CRANE vs target that gives: C gray, R yellow, A green, N gray, E yellow
        check_word('CRANE', '12312', li, lo, lc, li2)
        self.assertIn('C', lo)
        self.assertIn('N', lo)
        self.assertIn('R', li2)
        self.assertEqual(li2['R'], [1])
        self.assertIn('E', li2)
        self.assertEqual(li2['E'], [4])
        self.assertIn('A', lc)
        self.assertEqual(lc['A'], [2])

    def test_gray_letter_removed_from_letters_in(self):
        """A gray letter must be removed from lettersIn."""
        li, lo, lc, li2 = fresh_state()
        check_word('CRANE', '11111', li, lo, lc, li2)
        for ch in 'CRANE':
            self.assertNotIn(ch, li, f"{ch} should be removed from lettersIn")


# ---------------------------------------------------------------------------
# check_word — duplicate letters  (Bug 1 & Bug 2 regression tests)
# ---------------------------------------------------------------------------

class TestCheckWordDuplicates(unittest.TestCase):

    def test_duplicate_both_gray_adds_to_letters_out(self):
        """
        BUG 2 regression: when the SAME letter appears multiple times and ALL
        occurrences are gray it must still be added to lettersOut.

        Guess AABBB, result 11333 → A appears twice, both gray; B green.
        The counter fix (Bug 1) ensures only instances of A are counted (0),
        and the structural fix (Bug 2) ensures A is still appended to lettersOut.
        """
        li, lo, lc, li2 = fresh_state()
        check_word('AABBB', '11333', li, lo, lc, li2)
        self.assertIn('A', lo, "A (all-gray duplicate) must be in lettersOut")
        self.assertNotIn('B', lo, "B (green) must not be in lettersOut")
        self.assertEqual(lc.get('B'), [2, 3, 4])

    def test_duplicate_gray_not_suppressed_by_other_letter_results(self):
        """
        BUG 1 regression: the counter must only count occurrences of the SAME
        letter, not every letter in the guess that happens to have result > 1.

        Guess XXYAB, result 11321:
          X@0 gray, X@1 gray (X appears twice, both gray) → X must go to lettersOut
          Y@2 green, A@3 yellow, B@4 gray
        With the original bug, Y's green result (res[2]=3 > 1) inflates the
        counter for X, preventing X from being added to lettersOut.
        """
        li, lo, lc, li2 = fresh_state()
        check_word('XXYAB', '11321', li, lo, lc, li2)
        self.assertIn('X', lo, "X (all-gray duplicate) must be in lettersOut even though other letters are green/yellow")
        self.assertIn('B', lo, "B (single gray) must be in lettersOut")
        self.assertIn('Y', lc)
        self.assertEqual(lc['Y'], [2])
        self.assertIn('A', li2)
        self.assertEqual(li2['A'], [3])

    def test_duplicate_one_gray_one_yellow(self):
        """
        When a letter appears twice and one is gray (1) and one is yellow (2),
        the letter must NOT go to lettersOut (it IS in the target), and the
        yellow position must be in lettersIncorrect.
        """
        li, lo, lc, li2 = fresh_state()
        # Target DELTA, guess ADDED (A at 0 yellow, D at 1 gray, D at 2 green...)
        # Simpler: guess AAXXX result 12111 — A@0 gray, A@1 yellow, rest gray
        check_word('AAXXX', '12111', li, lo, lc, li2)
        self.assertNotIn('A', lo, "A should NOT be in lettersOut — one instance is yellow")
        self.assertIn('A', li2)
        self.assertEqual(li2['A'], [1])

    def test_duplicate_one_gray_one_green(self):
        """
        When a letter appears twice and one is gray (1) and one is green (3),
        the letter must NOT go to lettersOut, and the green position must be
        in lettersCorrect.
        """
        li, lo, lc, li2 = fresh_state()
        # guess AAXXX result 13111 — A@0 gray, A@1 green
        check_word('AAXXX', '13111', li, lo, lc, li2)
        self.assertNotIn('A', lo, "A should NOT be in lettersOut — one instance is green")
        self.assertIn('A', lc)
        self.assertEqual(lc['A'], [1])

    def test_duplicate_correct_and_incorrect_positions(self):
        """
        Target: ABBEY (B at positions 1 and 2).
        Guess: BBAAA result 23111 → B@0 yellow, B@1 green.
        B must be in lettersCorrect at [1] and lettersIncorrect at [0].
        """
        li, lo, lc, li2 = fresh_state()
        check_word('BBAAA', '23111', li, lo, lc, li2)
        self.assertNotIn('B', lo)
        self.assertIn('B', lc)
        self.assertEqual(lc['B'], [1])
        self.assertIn('B', li2)
        self.assertEqual(li2['B'], [0])

    def test_all_green_duplicate_letter(self):
        """
        Guess ABBEY result 33333 → B appears twice, both green.
        lettersCorrect must record both positions.
        """
        li, lo, lc, li2 = fresh_state()
        check_word('ABBEY', '33333', li, lo, lc, li2)
        self.assertEqual(lc.get('B'), [1, 2])
        self.assertEqual(lc.get('A'), [0])
        self.assertEqual(lc.get('E'), [3])
        self.assertEqual(lc.get('Y'), [4])


# ---------------------------------------------------------------------------
# eliminateCandidates
# ---------------------------------------------------------------------------

class TestEliminateCandidates(unittest.TestCase):

    def _run(self, candidates, lo=None, lc=None, li=None):
        return eliminateCandidates(candidates, lo or [], lc or {}, li or {})

    # -- lettersOut filtering --

    def test_reject_word_containing_out_letter(self):
        filtered = self._run(['CRANE', 'BRAIN', 'DELTA'], lo=['C'])
        self.assertNotIn('CRANE', filtered)
        self.assertIn('BRAIN', filtered)
        self.assertIn('DELTA', filtered)

    def test_reject_multiple_out_letters(self):
        filtered = self._run(['CRANE', 'BRAIN', 'DELTA'], lo=['C', 'R'])
        self.assertNotIn('CRANE', filtered)
        self.assertNotIn('BRAIN', filtered)
        self.assertIn('DELTA', filtered)

    # -- lettersCorrect filtering --

    def test_require_correct_position(self):
        """Word must have the letter at the specified green position."""
        filtered = self._run(['CRANE', 'CRAVE', 'DELTA'], lc={'C': [0]})
        self.assertIn('CRANE', filtered)
        self.assertIn('CRAVE', filtered)
        self.assertNotIn('DELTA', filtered)

    def test_reject_correct_letter_at_wrong_position(self):
        """A candidate with the letter but at wrong position must be rejected."""
        # CRAZE = C(0) R(1) A(2) Z(3) E(4) → Z at position 3
        filtered = self._run(['CRAZE', 'ZAPPY', 'AZURE'], lc={'Z': [3]})
        self.assertIn('CRAZE', filtered)     # Z at position 3 ✓
        self.assertNotIn('ZAPPY', filtered)  # Z at position 0
        self.assertNotIn('AZURE', filtered)  # Z at position 1

    def test_require_minimum_count_for_correct(self):
        """
        If lettersCorrect has B at two positions, min_count = 2.
        Candidate with only 1 B must be rejected.
        """
        filtered = self._run(['ABBEY', 'ABCEY', 'ABLEY'], lc={'A': [0], 'B': [1, 2], 'E': [3], 'Y': [4]})
        self.assertIn('ABBEY', filtered)
        self.assertNotIn('ABCEY', filtered)
        self.assertNotIn('ABLEY', filtered)

    # -- lettersIncorrect filtering --

    def test_require_yellow_letter_present(self):
        """Yellow letter must exist somewhere in the candidate."""
        filtered = self._run(['CRANE', 'BRAIN', 'DELTA'], li={'C': [3]})
        self.assertIn('CRANE', filtered)  # C at 0, not at 3 ✓
        self.assertNotIn('BRAIN', filtered)  # no C at all
        self.assertNotIn('DELTA', filtered)  # no C at all

    def test_reject_yellow_letter_at_wrong_position(self):
        """Candidate must not have the yellow letter at the known-wrong position."""
        filtered = self._run(['CRANE', 'ACUTE'], li={'C': [0]})
        self.assertNotIn('CRANE', filtered)  # C at position 0 (wrong position)
        self.assertIn('ACUTE', filtered)      # C at position 1 (different position)

    # -- combined lettersCorrect + lettersIncorrect --

    def test_correct_and_incorrect_same_letter(self):
        """
        B correct at pos 1, incorrect at pos 0.
        Candidate needs at least 2 B's; one at pos 1, none at pos 0.
        """
        lc = {'B': [1]}
        li = {'B': [0]}
        candidates = ['ABBEY', 'BBAAA', 'CABBE', 'ABCEY']
        filtered = eliminateCandidates(candidates, [], lc, li)
        self.assertIn('ABBEY', filtered)
        self.assertNotIn('BBAAA', filtered)  # B at pos 0 (wrong position)
        self.assertNotIn('CABBE', filtered)  # no B at pos 1
        self.assertNotIn('ABCEY', filtered)  # only 1 B, need 2

    def test_no_candidates_survive_impossible_constraints(self):
        """If no word satisfies constraints, return empty list."""
        filtered = self._run(['CRANE', 'BRAIN'], lo=['C', 'R', 'B'])
        self.assertEqual(filtered, [])

    def test_all_candidates_survive_no_constraints(self):
        """With empty constraints every candidate passes."""
        words = ['CRANE', 'BRAIN', 'DELTA']
        filtered = self._run(words)
        self.assertEqual(filtered, words)

    # -- integration: check_word then eliminateCandidates --

    def test_integration_gray_duplicate_eliminates_correctly(self):
        """
        After fixing both bugs, a word that shares only gray-duplicate letters
        with the guess must be eliminated.

        Guess AABBB result 11333:
          A is entirely gray → words with A must be filtered out.
          B is green at 2,3,4 → candidates must have B at those positions.
        """
        li, lo, lc, li2 = fresh_state()
        check_word('AABBB', '11333', li, lo, lc, li2)
        candidates = ['BBBBB', 'AABBB', 'ZZBBB', 'BABBB']
        filtered = eliminateCandidates(candidates, lo, lc, li2)
        self.assertIn('BBBBB', filtered)   # no A, B at 2,3,4 ✓
        self.assertNotIn('AABBB', filtered)  # contains A
        self.assertIn('ZZBBB', filtered)   # no A, B at 2,3,4 ✓
        self.assertNotIn('BABBB', filtered)  # contains A

    def test_integration_other_letter_green_doesnt_suppress_gray_duplicate(self):
        """
        Bug 1 regression at the integration level.

        Guess XXYAB result 11321: X (duplicate, all gray) must go to lettersOut,
        so any candidate with X must be filtered out.
        """
        li, lo, lc, li2 = fresh_state()
        check_word('XXYAB', '11321', li, lo, lc, li2)
        candidates = ['XZYZB', 'ZZYZB', 'YZZAB']
        filtered = eliminateCandidates(candidates, lo, lc, li2)
        self.assertNotIn('XZYZB', filtered, "Contains X which should be in lettersOut")
        # ZZYZB: no X or B, Y at pos 0 (lettersCorrect Y=[2]→not at 0→reject), skip
        # Focus on X filtering
        for word in filtered:
            self.assertNotIn('X', word, f"{word} contains X which should be filtered out")


# ---------------------------------------------------------------------------
# valid_result
# ---------------------------------------------------------------------------

class TestValidResult(unittest.TestCase):

    def test_valid_all_greens(self):
        self.assertTrue(valid_result('33333'))

    def test_valid_mixed(self):
        self.assertTrue(valid_result('12321'))
        self.assertTrue(valid_result('13213'))

    def test_invalid_too_short(self):
        self.assertFalse(valid_result('3333'))

    def test_invalid_too_long(self):
        self.assertFalse(valid_result('333333'))

    def test_invalid_digit_out_of_range(self):
        self.assertFalse(valid_result('33334'))
        self.assertFalse(valid_result('03333'))

    def test_invalid_non_digit(self):
        self.assertFalse(valid_result('abcde'))
        self.assertFalse(valid_result('3333a'))


# ---------------------------------------------------------------------------
# valid_word
# ---------------------------------------------------------------------------

class TestValidWord(unittest.TestCase):

    def test_valid_uppercase(self):
        self.assertTrue(valid_word('HELLO'))

    def test_valid_lowercase(self):
        self.assertTrue(valid_word('hello'))

    def test_invalid_too_short(self):
        self.assertFalse(valid_word('HELL'))

    def test_invalid_too_long(self):
        self.assertFalse(valid_word('HELLOS'))

    def test_invalid_non_alpha(self):
        self.assertFalse(valid_word('HELLO!'))
        self.assertFalse(valid_word('HE110'))


if __name__ == '__main__':
    unittest.main()
