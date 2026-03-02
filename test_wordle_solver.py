"""
Unit tests for WordleSolver - specifically targeting duplicate letter handling.

Wordle scoring: 1=gray (not in word), 2=yellow (in word, wrong position), 3=green (correct position).
When the target has duplicate letters (e.g., ABBEY), the solver must correctly track
multiple positions for the same letter.
"""
import unittest
from WordleSolverDefs import check_word, eliminateCandidates, valid_result, valid_word


class TestDuplicateLetterHandling(unittest.TestCase):
    """Tests for bug: target word with multiple copies of same letter."""

    def _fresh_state(self):
        """Create fresh state for each test."""
        letters_in = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        letters_out = []
        letters_correct = {}
        letters_incorrect = {}
        return letters_in, letters_out, letters_correct, letters_incorrect

    def test_duplicate_letter_correct_and_incorrect_positions(self):
        """
        Target: ABBEY (two B's at positions 1 and 2).
        Guess: BBAAA - B at 0 yellow, B at 1 green, A's gray.
        Result: 2, 3, 1, 1, 1 (pos 0: yellow, pos 1: green, pos 2-4: gray)
        The solver must know: B is correct at pos 1, B is wrong at pos 0.
        So valid candidates must have B at pos 1 and B somewhere else (not pos 0).
        """
        letters_in, letters_out, letters_correct, letters_incorrect = self._fresh_state()
        check_word('BBAAA', '23111', letters_in, letters_out, letters_correct, letters_incorrect)

        # B is in the word (we got yellow and green)
        self.assertNotIn('B', letters_out, "B should not be in letters_out (we got yellow+green)")
        self.assertIn('B', letters_correct, "B should be in letters_correct at pos 1")
        self.assertIn('B', letters_incorrect, "B should be in letters_incorrect at pos 0")

        # Must store both positions: B correct at [1], B wrong at [0]
        self.assertEqual(letters_correct['B'], [1], "B should be correct at position 1")
        self.assertEqual(letters_incorrect['B'], [0], "B should be incorrect at position 0")

        # Test eliminateCandidates: ABBEY should pass (B at 1 and 2, not at 0)
        candidates = ['ABBEY', 'BBAAA', 'CABBE', 'ABCEY']
        filtered = eliminateCandidates(candidates, letters_out, letters_correct, letters_incorrect)
        self.assertIn('ABBEY', filtered, "ABBEY has B at 1 and 2, should pass")
        self.assertNotIn('BBAAA', filtered, "BBAAA has B at 0 (wrong), should be rejected")
        self.assertNotIn('CABBE', filtered, "CABBE has B at 3 and 4, but not at 1 - should be rejected")
        self.assertNotIn('ABCEY', filtered, "ABCEY has only one B, need at least 2")

    def test_duplicate_letter_multiple_incorrect_positions(self):
        """
        Target: ABBEY (two B's at positions 1 and 2).
        Guess: BBAAA - B at 0 yellow, B at 1 green, A's gray. Result: 23111.
        We need to store: B correct at [1], B wrong at [0].
        BABEY has B at 0 (wrong position) - should be rejected.
        ABBEY has B at 1 and 2 - should pass.
        """
        letters_in, letters_out, letters_correct, letters_incorrect = self._fresh_state()
        check_word('BBAAA', '23111', letters_in, letters_out, letters_correct, letters_incorrect)

        candidates = ['ABBEY', 'BABEY', 'BBEAY']
        filtered = eliminateCandidates(candidates, letters_out, letters_correct, letters_incorrect)
        self.assertIn('ABBEY', filtered, "ABBEY has B at 1 and 2 - should pass")
        self.assertNotIn('BABEY', filtered, "BABEY has B at 0 (wrong position) - should be rejected")
        self.assertNotIn('BBEAY', filtered, "BBEAY has B at 0 (wrong position) - should be rejected")

    def test_duplicate_letter_minimum_count(self):
        """
        Target: ABBEY (two B's).
        Guess: ABBEY gives 33333.
        After: we know word has 2 B's. Candidates with only 1 B (e.g., ABLE) should be rejected.
        """
        letters_in, letters_out, letters_correct, letters_incorrect = self._fresh_state()
        check_word('ABBEY', '33333', letters_in, letters_out, letters_correct, letters_incorrect)

        # letters_correct has A=0, B=1, B=2 (overwrite!), E=3, Y=4
        # With dict we only get B=2 (last one). So we'd require cand[2]==B but not cand[1]==B!
        candidates = ['ABBEY', 'ABCEY', 'ABLEY', 'ABBEY']
        filtered = eliminateCandidates(candidates, letters_out, letters_correct, letters_incorrect)
        self.assertIn('ABBEY', filtered)
        self.assertNotIn('ABCEY', filtered, "Only one B, need two")
        self.assertNotIn('ABLEY', filtered, "Only one B, need two")


class TestValidFunctions(unittest.TestCase):
    """Tests for valid_word and valid_result."""

    def test_valid_result(self):
        self.assertTrue(valid_result('33333'))
        self.assertTrue(valid_result('12321'))
        self.assertFalse(valid_result('3333'))
        self.assertFalse(valid_result('33334'))
        self.assertFalse(valid_result('abcde'))

    def test_valid_word(self):
        self.assertTrue(valid_word('HELLO'))
        self.assertTrue(valid_word('hello'))
        self.assertFalse(valid_word('HELL'))
        self.assertFalse(valid_word('HELLO!'))


if __name__ == '__main__':
    unittest.main()
